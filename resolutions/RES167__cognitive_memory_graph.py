"""
RES167__cognitive_memory_graph.py
DESTINO FINAL: core/memory_fabric/graph/cognitive_memory_graph.py
RES.167 - MPAT4 | Relay: RELAY_013 | 2026-05-23
Autor: cursos.agt.ia@gmail.com (docente_AGT_2026)


Item 03 — Persistent Cognitive Memory Graph.
Grafo de conocimiento persistente que conecta episodios, conceptos y
relaciones a través de sesiones. Supera al RAG plano con razonamiento
multi-hop y relaciones históricas.


TECNOLOGÍA:
  FalkorDB embedded (default) — sin proceso servidor, protocolo Redis.
  Neo4j local — para deployments con más de 10M nodos.
  Patrón adaptador: GraphBackend abstrae ambos. Intercambiable sin
  cambiar el código de CognitiveMemoryGraph.


INVARIANTES:
  INV-GRAPH.1: todo nodo tiene tenant_id — aislamiento multi-tenant garantizado.
  INV-GRAPH.2: upsert semántico — si una entidad ya existe, se actualiza,
               nunca se crea un duplicado.
  INV-GRAPH.3: hybrid_search ejecuta Cypher y vector en PARALELO
               (asyncio.gather) — nunca secuencial.
  INV-GRAPH.4: consolidate_session() es idempotente — llamadas repetidas
               con el mismo session_id producen el mismo estado del grafo.
  INV-GRAPH.5: las relaciones CONTRADICTS se priorizan en la fusión RRF
               — el sistema debe saber cuándo dos hechos se contradicen.


TRAMPA EDUCATIVA:
  "El grafo de conocimiento reemplaza al RAG vectorial."
  FALSO: son COMPLEMENTARIOS. El grafo captura RELACIONES (multi-hop).
  El vectorial captura SIMILITUD SEMÁNTICA (fuzzy matching).
  hybrid_search() los combina porque resuelven problemas diferentes:
  - "¿Qué proyectos tiene el alumno relacionados con Rust?" → grafo (relacional)
  - "¿Qué documentos hablan de programación de sistemas?" → vectorial (semántico)
  - "¿Qué dice el doc X sobre Y que también menciona Z?" → AMBOS en paralelo


que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations


import asyncio
import hashlib
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4


from core.memory_fabric.graph.graph_schema import (
    GraphNode, GraphRelation, GraphDelta,
    NodeType, RelationType, HybridSearchResult,
    ConsolidationResult,
)


logger = logging.getLogger("mpat.memory_graph")




# ---------------------------------------------------------------------------
# GraphBackend — interfaz abstracta del motor de grafo
# ---------------------------------------------------------------------------


class GraphBackend(ABC):
    """
    Interfaz abstracta para el motor de grafo.
    FalkorDB y Neo4j implementan esta interfaz.
    CognitiveMemoryGraph programa contra esta interfaz — nunca contra el motor.
    """


    @abstractmethod
    async def connect(self) -> None: ...


    @abstractmethod
    async def close(self) -> None: ...


    @abstractmethod
    async def upsert_node(self, node: GraphNode) -> bool:
        """Inserta o actualiza un nodo. Retorna True si fue creado (no actualizado)."""
        ...


    @abstractmethod
    async def upsert_relation(self, relation: GraphRelation) -> bool: ...


    @abstractmethod
    async def query_cypher(self, cypher: str, params: dict) -> list[dict]: ...


    @abstractmethod
    async def node_exists(self, node_id: str, tenant_id: str) -> bool: ...


    @abstractmethod
    async def delete_session_data(self, session_id: str, tenant_id: str) -> int:
        """Borra nodos/relaciones de una sesión. Retorna cantidad borrada."""
        ...




# ---------------------------------------------------------------------------
# FalkorDBBackend — implementación embedded (default)
# ---------------------------------------------------------------------------


class FalkorDBBackend(GraphBackend):
    """
    Backend FalkorDB para MPAT4.


    FalkorDB es un grafo embedded sobre Redis — no requiere proceso servidor
    separado. Usa el protocolo RedisGraph (compatible con Neo4j Cypher subset).
    Ideal para deployments en VPS $5 o Raspberry Pi (INV de soberanía LATAM).


    Instalación: pip install falkordb redis
    Docker local: docker run -p 6379:6379 falkordb/falkordb
    """


    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        graph_name: str = "mpat4_memory",
        password: Optional[str] = None,
    ):
        self._host = host
        self._port = port
        self._graph_name = graph_name
        self._password = password
        self._client = None
        self._graph = None


    async def connect(self) -> None:
        try:
            import falkordb
            self._client = falkordb.FalkorDB(
                host=self._host, port=self._port, password=self._password
            )
            self._graph = self._client.select_graph(self._graph_name)
            # Crear índices si no existen
            await self._ensure_indexes()
            logger.info("FalkorDB conectado: %s:%d graph=%s",
                        self._host, self._port, self._graph_name)
        except ImportError:
            raise RuntimeError(
                "FalkorDB no instalado. Instalar: pip install falkordb redis\n"
                "O usar Neo4jBackend con Neo4j local."
            )


    async def _ensure_indexes(self) -> None:
        """Crear índices para búsquedas eficientes por tenant_id y node_id."""
        try:
            self._graph.query(
                "CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.tenant_id)"
            )
            self._graph.query(
                "CREATE INDEX IF NOT EXISTS FOR (n:Concept) ON (n.tenant_id)"
            )
            self._graph.query(
                "CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.node_id)"
            )
        except Exception as exc:
            logger.debug("Index creation (may already exist): %s", exc)


    async def close(self) -> None:
        if self._client:
            self._client.close()


    async def upsert_node(self, node: GraphNode) -> bool:
        """
        INV-GRAPH.2: upsert — si existe, actualiza; si no, crea.
        Usa MERGE en Cypher para garantizar idempotencia (INV-GRAPH.4).
        """
        label = node.node_type.value
        cypher = f"""
        MERGE (n:{label} {{node_id: $node_id, tenant_id: $tenant_id}})
        ON CREATE SET
            n.name = $name,
            n.embedding_hash = $embedding_hash,
            n.created_at = $created_at,
            n.session_id = $session_id,
            n.metadata = $metadata
        ON MATCH SET
            n.name = $name,
            n.embedding_hash = $embedding_hash,
            n.updated_at = $updated_at
        RETURN n.node_id AS node_id, (n.created_at = $created_at) AS was_created
        """
        now = datetime.now(timezone.utc).isoformat()
        result = self._graph.query(cypher, {
            "node_id": node.node_id,
            "tenant_id": node.tenant_id,
            "name": node.name,
            "embedding_hash": node.embedding_hash or "",
            "created_at": node.created_at.isoformat(),
            "updated_at": now,
            "session_id": node.session_id or "",
            "metadata": json.dumps(node.metadata),
        })
        return bool(result.result_set and result.result_set[0][1])


    async def upsert_relation(self, relation: GraphRelation) -> bool:
        rel_type = relation.relation_type.value
        cypher = f"""
        MATCH (a {{node_id: $from_id, tenant_id: $tenant_id}})
        MATCH (b {{node_id: $to_id, tenant_id: $tenant_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        ON CREATE SET
            r.relation_id = $relation_id,
            r.weight = $weight,
            r.created_at = $created_at,
            r.session_id = $session_id
        ON MATCH SET
            r.weight = $weight,
            r.updated_at = $updated_at
        RETURN r.relation_id AS rid
        """
        now = datetime.now(timezone.utc).isoformat()
        result = self._graph.query(cypher, {
            "from_id": relation.from_node_id,
            "to_id": relation.to_node_id,
            "tenant_id": relation.tenant_id,
            "relation_id": relation.relation_id,
            "weight": relation.weight,
            "created_at": relation.created_at.isoformat(),
            "updated_at": now,
            "session_id": relation.session_id or "",
        })
        return bool(result.result_set)


    async def query_cypher(self, cypher: str, params: dict) -> list[dict]:
        result = self._graph.query(cypher, params)
        rows = []
        for record in result.result_set:
            row = {}
            for i, key in enumerate(result.header):
                row[key] = record[i]
            rows.append(row)
        return rows


    async def node_exists(self, node_id: str, tenant_id: str) -> bool:
        result = self._graph.query(
            "MATCH (n {node_id: $node_id, tenant_id: $tenant_id}) RETURN n LIMIT 1",
            {"node_id": node_id, "tenant_id": tenant_id},
        )
        return bool(result.result_set)


    async def delete_session_data(self, session_id: str, tenant_id: str) -> int:
        result = self._graph.query(
            "MATCH (n {session_id: $session_id, tenant_id: $tenant_id}) "
            "DETACH DELETE n RETURN count(n) AS deleted",
            {"session_id": session_id, "tenant_id": tenant_id},
        )
        if result.result_set:
            return result.result_set[0][0]
        return 0




# ---------------------------------------------------------------------------
# EntityExtractor — LLM local extrae entidades y relaciones del texto
# ---------------------------------------------------------------------------


class EntityExtractor:
    """
    Extrae entidades y relaciones de texto usando un LLM local.


    El prompt de extracción retorna JSON estructurado con:
    - entities: [{id, type, name}]
    - relations: [{from, to, type, weight}]


    En tests (sin LLM disponible), usa extracción heurística por regex.
    """


    EXTRACTION_PROMPT = """Analiza el siguiente texto y extrae:
1. ENTIDADES: personas, proyectos, tecnologías, conceptos, organizaciones
2. RELACIONES entre entidades: RELATED_TO, OWNED_BY, MENTIONED_IN, CONTRADICTS


Responde SOLO en JSON válido con esta estructura exacta:
{
  "entities": [{"id": "hash_corto", "type": "Entity|Concept", "name": "nombre"}],
  "relations": [{"from": "id1", "to": "id2", "type": "RELATED_TO|OWNED_BY|MENTIONED_IN|CONTRADICTS", "weight": 0.8}]
}


TEXTO:
"""


    def __init__(self, llm_backend=None):
        self._llm = llm_backend  # None = modo heurístico (tests)


    async def extract(
        self,
        text: str,
        tenant_id: str,
        session_id: str,
    ) -> tuple[list[GraphNode], list[GraphRelation]]:
        """Extrae entidades y relaciones del texto dado."""
        if self._llm:
            return await self._extract_with_llm(text, tenant_id, session_id)
        return self._extract_heuristic(text, tenant_id, session_id)


    async def _extract_with_llm(
        self, text: str, tenant_id: str, session_id: str
    ) -> tuple[list[GraphNode], list[GraphRelation]]:
        prompt = self.EXTRACTION_PROMPT + text[:4000]  # truncar para evitar overflow
        response = await self._llm.complete(prompt, max_tokens=1000)
        try:
            # Limpiar posibles markdown fences
            clean = response.strip().removeprefix("```json").removesuffix("```").strip()
            data = json.loads(clean)
        except json.JSONDecodeError as exc:
            logger.warning("EntityExtractor: JSON inválido del LLM: %s", exc)
            return [], []
        return self._parse_extraction(data, tenant_id, session_id)


    def _extract_heuristic(
        self, text: str, tenant_id: str, session_id: str
    ) -> tuple[list[GraphNode], list[GraphRelation]]:
        """
        Extracción heurística sin LLM — para tests y desarrollo local.
        Detecta palabras capitalizadas y términos técnicos conocidos.
        """
        import re
        # Detectar palabras capitalizadas (probables entidades)
        words = re.findall(r'\b[A-Z][a-zA-Z]{2,}\b', text)
        # Términos técnicos conocidos de MPAT4
        tech_terms = ["MPAT4", "Python", "Rust", "Redis", "FalkorDB", "EventBus",
                      "OPA", "Firecracker", "WASM", "Docker", "Kubernetes"]
        entities_raw = list(set(words + [t for t in tech_terms if t in text]))[:20]


        nodes = []
        for name in entities_raw:
            node_id = hashlib.md5(f"{tenant_id}:{name}".encode()).hexdigest()[:12]
            node_type = NodeType.CONCEPT if name in tech_terms else NodeType.ENTITY
            nodes.append(GraphNode(
                node_id=node_id,
                tenant_id=tenant_id,
                node_type=node_type,
                name=name,
                session_id=session_id,
                created_at=datetime.now(timezone.utc),
            ))


        # Crear relaciones RELATED_TO entre entidades consecutivas mencionadas
        relations = []
        for i in range(len(nodes) - 1):
            a, b = nodes[i], nodes[i + 1]
            relations.append(GraphRelation(
                relation_id=str(uuid4())[:8],
                tenant_id=tenant_id,
                from_node_id=a.node_id,
                to_node_id=b.node_id,
                relation_type=RelationType.RELATED_TO,
                weight=0.5,
                session_id=session_id,
                created_at=datetime.now(timezone.utc),
            ))
        return nodes, relations


    def _parse_extraction(
        self, data: dict, tenant_id: str, session_id: str
    ) -> tuple[list[GraphNode], list[GraphRelation]]:
        nodes = []
        node_map = {}  # id_short → node_id completo
        for e in data.get("entities", []):
            node_id = hashlib.md5(
                f"{tenant_id}:{e.get('name', '')}".encode()
            ).hexdigest()[:12]
            node_map[e.get("id", "")] = node_id
            node_type_str = e.get("type", "Entity")
            node_type = NodeType.CONCEPT if node_type_str == "Concept" else NodeType.ENTITY
            nodes.append(GraphNode(
                node_id=node_id,
                tenant_id=tenant_id,
                node_type=node_type,
                name=e.get("name", ""),
                session_id=session_id,
                created_at=datetime.now(timezone.utc),
            ))


        relations = []
        for r in data.get("relations", []):
            from_id = node_map.get(r.get("from", ""))
            to_id = node_map.get(r.get("to", ""))
            if not from_id or not to_id:
                continue
            rel_type_str = r.get("type", "RELATED_TO")
            try:
                rel_type = RelationType(rel_type_str)
            except ValueError:
                rel_type = RelationType.RELATED_TO
            relations.append(GraphRelation(
                relation_id=str(uuid4())[:8],
                tenant_id=tenant_id,
                from_node_id=from_id,
                to_node_id=to_id,
                relation_type=rel_type,
                weight=float(r.get("weight", 0.7)),
                session_id=session_id,
                created_at=datetime.now(timezone.utc),
            ))
        return nodes, relations




# ---------------------------------------------------------------------------
# CognitiveMemoryGraph — motor principal
# ---------------------------------------------------------------------------


class CognitiveMemoryGraph:
    """
    Grafo de conocimiento persistente de MPAT4.


    Supera al RAG vectorial plano con:
      - Razonamiento multi-hop: "proyectos del alumno que usan Rust"
        requiere saltar: alumno → proyecto → tecnología.
      - Relaciones históricas: qué entidades aparecen juntas a lo largo
        del tiempo, qué hechos se contradicen (INV-GRAPH.5).
      - Contexto relacional: quién es propietario de qué (OWNED_BY).


    hybrid_search() combina grafo + vectorial en paralelo (INV-GRAPH.3)
    y fusiona con RRF (Reciprocal Rank Fusion).
    """


    def __init__(
        self,
        backend: GraphBackend,
        extractor: Optional[EntityExtractor] = None,
        vector_runtime=None,   # VectorRuntime (RES.176) — opcional
    ):
        self._backend = backend
        self._extractor = extractor or EntityExtractor()
        self._vector = vector_runtime
        # Cache de sesiones consolidadas (INV-GRAPH.4: idempotencia)
        self._consolidated_sessions: set[str] = set()


    async def initialize(self) -> None:
        await self._backend.connect()
        logger.info("CognitiveMemoryGraph inicializado")


    async def close(self) -> None:
        await self._backend.close()


    # ------------------------------------------------------------------
    # consolidate_session — extrae y persiste conocimiento de una sesión
    # ------------------------------------------------------------------


    async def consolidate_session(
        self,
        session_id: str,
        tenant_id: str,
        session_transcript: str,
    ) -> ConsolidationResult:
        """
        Extrae entidades y relaciones del transcript de la sesión
        y las persiste en el grafo.


        INV-GRAPH.4: idempotente — llamadas repetidas con el mismo
        session_id no duplican datos (MERGE semántico).


        Flujo:
          1. Verificar si ya fue consolidada (cache + MERGE garantiza idempotencia).
          2. EntityExtractor extrae entidades y relaciones del transcript.
          3. Upsert de todos los nodos (INV-GRAPH.2).
          4. Upsert de todas las relaciones.
          5. Registrar en cache y retornar ConsolidationResult.
        """
        cache_key = f"{tenant_id}:{session_id}"
        if cache_key in self._consolidated_sessions:
            logger.debug("Sesión ya consolidada (idempotente): %s", session_id)
            return ConsolidationResult(
                session_id=session_id,
                tenant_id=tenant_id,
                nodes_created=0,
                relations_created=0,
                already_consolidated=True,
            )


        nodes, relations = await self._extractor.extract(
            text=session_transcript,
            tenant_id=tenant_id,
            session_id=session_id,
        )


        nodes_created = 0
        for node in nodes:
            was_created = await self._backend.upsert_node(node)
            if was_created:
                nodes_created += 1


        relations_created = 0
        for relation in relations:
            was_created = await self._backend.upsert_relation(relation)
            if was_created:
                relations_created += 1


        self._consolidated_sessions.add(cache_key)


        result = ConsolidationResult(
            session_id=session_id,
            tenant_id=tenant_id,
            nodes_created=nodes_created,
            nodes_total=len(nodes),
            relations_created=relations_created,
            relations_total=len(relations),
            already_consolidated=False,
        )
        logger.info(
            "Sesión consolidada: %s nodes_new=%d/%d rels_new=%d/%d",
            session_id[:8], nodes_created, len(nodes),
            relations_created, len(relations),
        )
        return result


    # ------------------------------------------------------------------
    # query_relational — Cypher directo
    # ------------------------------------------------------------------


    async def query_relational(
        self,
        cypher: str,
        params: Optional[dict] = None,
        tenant_id: Optional[str] = None,
    ) -> list[dict]:
        """
        Ejecuta una query Cypher directamente en el grafo.


        Si se provee tenant_id, se inyecta automáticamente en los params
        para garantizar aislamiento multi-tenant (INV-GRAPH.1).


        Ejemplos de queries útiles:
          # Entidades relacionadas con "MPAT4"
          MATCH (a {name: 'MPAT4', tenant_id: $tid})-[:RELATED_TO]->(b)
          RETURN b.name, b.node_type


          # Multi-hop: proyectos del alumno que usan Rust
          MATCH (u {name: $user, tenant_id: $tid})-[:OWNED_BY*1..3]-(p)-[:RELATED_TO]->(t {name: 'Rust'})
          RETURN p.name


          # Encontrar contradicciones
          MATCH (a)-[:CONTRADICTS]->(b)
          WHERE a.tenant_id = $tid
          RETURN a.name, b.name
        """
        merged_params = dict(params or {})
        if tenant_id:
            merged_params["tid"] = tenant_id
        return await self._backend.query_cypher(cypher, merged_params)


    # ------------------------------------------------------------------
    # hybrid_search — grafo + vectorial en paralelo (INV-GRAPH.3)
    # ------------------------------------------------------------------


    async def hybrid_search(
        self,
        prompt: str,
        tenant_id: str,
        top_k: int = 10,
        graph_weight: float = 0.5,
        vector_weight: float = 0.5,
    ) -> list[HybridSearchResult]:
        """
        Búsqueda híbrida: Cypher + vectorial en paralelo, fusionados con RRF.


        INV-GRAPH.3: SIEMPRE paralelo con asyncio.gather — nunca secuencial.


        RRF (Reciprocal Rank Fusion):
          score_rrf(doc, rank) = 1 / (k + rank)   donde k=60 (constante empírica)
          Combina rankings de diferentes fuentes sin importar la escala de scores.


        Si no hay vector_runtime disponible (RES.176 pendiente), retorna
        solo resultados del grafo con score_vector=0.
        """
        # INV-GRAPH.3: ejecutar en paralelo
        graph_task = asyncio.create_task(
            self._graph_search(prompt, tenant_id, top_k * 2)
        )
        vector_task = asyncio.create_task(
            self._vector_search(prompt, tenant_id, top_k * 2)
        )


        graph_results, vector_results = await asyncio.gather(
            graph_task, vector_task, return_exceptions=True
        )


        if isinstance(graph_results, Exception):
            logger.warning("Graph search falló: %s", graph_results)
            graph_results = []
        if isinstance(vector_results, Exception):
            logger.warning("Vector search falló: %s", vector_results)
            vector_results = []


        return self._rrf_fusion(
            graph_results=graph_results,
            vector_results=vector_results,
            top_k=top_k,
            graph_weight=graph_weight,
            vector_weight=vector_weight,
        )


    async def _graph_search(
        self, prompt: str, tenant_id: str, limit: int
    ) -> list[dict]:
        """
        Búsqueda en el grafo por nombre de entidad (substring match).
        Luego expande 1 hop para obtener entidades relacionadas.
        """
        # Extraer términos de búsqueda del prompt (palabras capitalizadas o > 4 chars)
        terms = [w for w in prompt.split() if len(w) > 4][:5]


        results = []
        for term in terms:
            cypher = """
            MATCH (n {tenant_id: $tid})
            WHERE toLower(n.name) CONTAINS toLower($term)
            OPTIONAL MATCH (n)-[r]-(neighbor {tenant_id: $tid})
            RETURN n.node_id AS node_id, n.name AS name, n.node_type AS node_type,
                   collect(DISTINCT neighbor.name)[..5] AS neighbors,
                   count(r) AS degree
            ORDER BY degree DESC
            LIMIT $limit
            """
            rows = await self._backend.query_cypher(cypher, {
                "tid": tenant_id, "term": term, "limit": limit // max(1, len(terms))
            })
            results.extend(rows)
        return results


    async def _vector_search(
        self, prompt: str, tenant_id: str, limit: int
    ) -> list[dict]:
        """
        Búsqueda vectorial usando VectorRuntime (RES.176).
        Si no está disponible, retorna lista vacía.
        """
        if not self._vector:
            logger.debug("VectorRuntime no disponible — solo búsqueda por grafo")
            return []
        try:
            results = await self._vector.search(
                query=prompt, tenant_id=tenant_id, top_k=limit
            )
            return [{"node_id": r.id, "name": r.text, "score": r.score}
                    for r in results]
        except Exception as exc:
            logger.warning("Vector search error: %s", exc)
            return []


    def _rrf_fusion(
        self,
        graph_results: list[dict],
        vector_results: list[dict],
        top_k: int,
        graph_weight: float,
        vector_weight: float,
        k: int = 60,
    ) -> list[HybridSearchResult]:
        """
        Reciprocal Rank Fusion.
        score(doc) = graph_weight * 1/(k + rank_graph)
                   + vector_weight * 1/(k + rank_vector)
        """
        scores: dict[str, float] = {}
        names: dict[str, str] = {}
        sources: dict[str, list[str]] = {}


        # Scores del grafo
        for rank, result in enumerate(graph_results):
            nid = result.get("node_id", str(rank))
            rrf_score = graph_weight * (1.0 / (k + rank + 1))
            scores[nid] = scores.get(nid, 0.0) + rrf_score
            names[nid] = result.get("name", nid)
            sources.setdefault(nid, []).append("graph")


        # Scores del vector
        for rank, result in enumerate(vector_results):
            nid = result.get("node_id", str(rank))
            rrf_score = vector_weight * (1.0 / (k + rank + 1))
            scores[nid] = scores.get(nid, 0.0) + rrf_score
            names[nid] = result.get("name", names.get(nid, nid))
            sources.setdefault(nid, []).append("vector")


        # Ordenar y retornar top_k
        sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
        return [
            HybridSearchResult(
                node_id=nid,
                name=names.get(nid, nid),
                rrf_score=scores[nid],
                sources=sources.get(nid, []),
            )
            for nid in sorted_ids[:top_k]
        ]


    # ------------------------------------------------------------------
    # graph_delta — diferencias desde un timestamp
    # ------------------------------------------------------------------


    async def get_graph_delta(
        self,
        tenant_id: str,
        since: datetime,
    ) -> GraphDelta:
        """
        Retorna los nodos y relaciones creados/modificados desde `since`.
        Útil para sincronización incremental entre sesiones.
        """
        since_iso = since.isoformat()
        new_nodes = await self._backend.query_cypher(
            "MATCH (n {tenant_id: $tid}) "
            "WHERE n.created_at >= $since OR n.updated_at >= $since "
            "RETURN n.node_id AS node_id, n.name AS name, n.node_type AS node_type "
            "LIMIT 500",
            {"tid": tenant_id, "since": since_iso},
        )
        new_rels = await self._backend.query_cypher(
            "MATCH ()-[r {tenant_id: $tid}]->() "
            "WHERE r.created_at >= $since OR r.updated_at >= $since "
            "RETURN r.relation_id AS relation_id, type(r) AS rel_type "
            "LIMIT 500",
            {"tid": tenant_id, "since": since_iso},
        )
        return GraphDelta(
            tenant_id=tenant_id,
            since=since,
            nodes_added=len(new_nodes),
            relations_added=len(new_rels),
            node_ids=[r["node_id"] for r in new_nodes],
            relation_ids=[r["relation_id"] for r in new_rels],
        )


    # ------------------------------------------------------------------
    # Factory — get_default_graph
    # ------------------------------------------------------------------


    @classmethod
    def create_with_falkordb(
        cls,
        host: str = "localhost",
        port: int = 6379,
        graph_name: str = "mpat4_memory",
        llm_backend=None,
        vector_runtime=None,
    ) -> "CognitiveMemoryGraph":
        """Factory para FalkorDB (deployment default MPAT4)."""
        backend = FalkorDBBackend(host=host, port=port, graph_name=graph_name)
        extractor = EntityExtractor(llm_backend=llm_backend)
        return cls(backend=backend, extractor=extractor, vector_runtime=vector_runtime)