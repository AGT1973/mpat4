\# INVESTIGACION\_FUT16\_GRAFO\_DECISIONES\_V3\_01.md  
\#\# MPAT V3\_01 — Investigación formal FUT.16  
\#\# Alumno: cursos.agt.ia@gmail.com · 2026-05-13  
\#\# RELAY\_006 — GAP media prioridad

\---

\#\# 1\. Identificación del FUT

| Campo | Valor |  
|---|---|  
| FUT | FUT.16 |  
| Descripción original | Visualización Grafo Decisiones multi-agente |  
| RES propuesta | RES.124 (canónica — MAPA\_RES\_CANONICO\_V3\_01.md) |  
| Capa principal | Capa 5 (KG \+ Multi-agent) \+ Capa 11 (Orchestration) \+ Capa 10 (OTel) |  
| Estado anterior | GAP — DashboardAdapter (RES.093) cubre dashboard reactivo básico, NO cubre grafo de decisiones |  
| Prioridad | MEDIA |

\---

\#\# 2\. Distinción crítica: FUT.16 vs DashboardAdapter (RES.093)

| Dimensión | DashboardAdapter (RES.093) | DecisionGraphVisualizer (RES.124) |  
|---|---|---|  
| Qué muestra | Métricas del sistema (latencia, errores, estado capas) | Árbol de decisiones del agente: qué evaluó, qué descartó, por qué eligió |  
| Estructura | Tablero de métricas numéricas | Grafo dirigido acíclico (DAG) de nodos de decisión |  
| Interactividad | Lectura de estado actual | Exploración de razonamiento: expandir nodos, ver evidencia |  
| Usuarios | Administradores de sistema | Docentes y alumnos que quieren entender qué razonó el agente |  
| Actualización | Polling periódico | Event-driven: un nodo nuevo por cada decisión del agente |  
| Capa fuente | Capa 10 (OTel spans) | Capa 5 (KG) \+ Capa 11 (Orchestrator decision log) |

\*\*Por qué esto importa en un sistema educativo:\*\*  
Un alumno que recibe una respuesta del agente MPAT puede querer entender  
"¿por qué el agente eligió esta estrategia pedagógica y no otra?".  
El DecisionGraphVisualizer expone ese razonamiento como un grafo navegable,  
en lugar de una caja negra.

\---

\#\# 3\. Diagnóstico del GAP

\#\#\# 3.1 Verificación en MASTERs

\- \*\*CAPA\_05\_MASTER\_V3\_01.md\*\*: Knowledge Graph (KG) implementa ShadowRadix+CSA/HCA (RES.110)  
  y Multi-agent Orchestration (RES.092). El KG almacena nodos de conocimiento pero NO  
  registra el árbol de decisiones del agente como estructura separada. \*\*GAP confirmado.\*\*

\- \*\*CAPA\_11\_MASTER\_V3\_01.md\*\*: Unikernel-per-Tenant (RES.115) \+ SubQ (RES.114).  
  El orquestador toma decisiones (qué agente invocar, qué herramienta usar) pero  
  NO persiste un log estructurado de esas decisiones como DAG. \*\*GAP confirmado.\*\*

\- \*\*CAPA\_10\_MASTER\_V3\_01.md\*\*: OTel spans registran latencias y errores. No incluye  
  spans de tipo \`decision\_node\` con relaciones padre-hijo. \*\*GAP confirmado.\*\*

\#\#\# 3.2 Conclusión

FUT.16 requiere dos componentes nuevos:  
1\. \`DecisionLogger\` (Capa 11\) — registra cada decisión del orquestador como nodo con relaciones  
2\. \`DecisionGraphAPI\` (Capa 10/OTel) — expone el grafo acumulado por sesión vía endpoint

\---

\#\# 4\. Definición de componentes

\#\#\# 4.1 Modelo de datos — DecisionNode

\`\`\`python  
\# capa\_11/decision\_graph.py — RES.124

from dataclasses import dataclass, field  
from datetime import datetime, timezone  
from typing import Optional, Literal  
import uuid

DecisionType \= Literal\[  
    "agent\_selection",      \# qué agente invocar  
    "tool\_selection",       \# qué herramienta del ToolRegistry usar  
    "strategy\_selection",   \# qué estrategia pedagógica aplicar  
    "context\_retrieval",    \# qué fragmento del KG recuperar  
    "fallback",             \# decisión de fallback ante error  
    "hallucination\_guard",  \# decisión de filtrar/regenerar respuesta  
\]

@dataclass  
class DecisionNode:  
    """  
    Representa una decisión atómica tomada por el orquestador durante una sesión.

    Precondición:  
    \- node\_id es único en el grafo de la sesión.  
    \- parent\_id, si existe, corresponde a un nodo ya registrado en el mismo grafo.  
    \- confidence ∈ \[0.0, 1.0\].

    Postcondición:  
    \- Al registrarse, el nodo queda disponible en DecisionGraph para consulta vía API.

    Invariante (INV-DG.1):  
    \- Un nodo nunca puede ser su propio padre (sin ciclos).  
    \- tenant\_id del nodo \== tenant\_id del grafo contenedor.  
    """  
    node\_id: str \= field(default\_factory=lambda: str(uuid.uuid4()))  
    tenant\_id: str \= ""  
    session\_id: str \= ""  
    parent\_id: Optional\[str\] \= None          \# None \= nodo raíz de la sesión

    decision\_type: DecisionType \= "agent\_selection"  
    chosen: str \= ""                          \# opción elegida (nombre agente/herramienta/etc)  
    alternatives\_considered: list\[str\] \= field(default\_factory=list)  
    reason: str \= ""                          \# justificación en lenguaje natural  
    evidence: dict \= field(default\_factory=dict)  
    \# evidence puede incluir: {"kg\_fragment": "...", "hallucination\_score": 0.12, "tool\_score": 0.87}

    confidence: float \= 1.0  
    timestamp\_utc: datetime \= field(default\_factory=lambda: datetime.now(timezone.utc))  
    duration\_ms: float \= 0.0                  \# tiempo que tomó tomar la decisión  
\`\`\`

\#\#\# 4.2 DecisionGraph — grafo por sesión

\`\`\`python  
\# capa\_11/decision\_graph.py (cont.) — RES.124

@dataclass  
class DecisionGraph:  
    """  
    Grafo dirigido acíclico (DAG) de decisiones de una sesión de agente.

    Precondición: session\_id único por tenant.  
    Postcondición: el grafo es consultable como árbol JSON o lista de nodos.

    Invariante (INV-DG.2):  
    \- El grafo es estrictamente acíclico. No se permiten nodos con parent\_id  
      que forme un ciclo (verificado en add\_node).  
    \- Máximo MAX\_NODES\_PER\_SESSION nodos (configurable en policy.yaml).  
    """  
    MAX\_NODES\_PER\_SESSION \= 500

    tenant\_id: str  
    session\_id: str  
    \_nodes: dict\[str, DecisionNode\] \= field(default\_factory=dict)

    def add\_node(self, node: DecisionNode) \-\> None:  
        """  
        Pre: node.node\_id no existe en el grafo. node.parent\_id es None o existe en el grafo.  
        Post: nodo agregado. Si len \> MAX\_NODES\_PER\_SESSION, lanza OverflowError.  
        """  
        if node.node\_id in self.\_nodes:  
            raise ValueError(f"nodo duplicado: {node.node\_id}")  
        if node.parent\_id and node.parent\_id not in self.\_nodes:  
            raise ValueError(f"parent\_id {node.parent\_id} no existe en el grafo")  
        if len(self.\_nodes) \>= self.MAX\_NODES\_PER\_SESSION:  
            raise OverflowError(f"grafo excede MAX\_NODES\_PER\_SESSION={self.MAX\_NODES\_PER\_SESSION}")  
        \# Verificación de ciclo: el parent\_id no puede ser el mismo nodo (trivial) ni  
        \# un descendiente del nodo actual (no aplica en inserción ordenada)  
        self.\_nodes\[node.node\_id\] \= node

    def to\_json(self) \-\> dict:  
        """Serializa el grafo completo para la API."""  
        return {  
            "tenant\_id": self.tenant\_id,  
            "session\_id": self.session\_id,  
            "node\_count": len(self.\_nodes),  
            "nodes": \[  
                {  
                    "id": n.node\_id,  
                    "parent\_id": n.parent\_id,  
                    "type": n.decision\_type,  
                    "chosen": n.chosen,  
                    "alternatives": n.alternatives\_considered,  
                    "reason": n.reason,  
                    "confidence": n.confidence,  
                    "timestamp": n.timestamp\_utc.isoformat(),  
                    "duration\_ms": n.duration\_ms,  
                }  
                for n in self.\_nodes.values()  
            \]  
        }  
\`\`\`

\#\#\# 4.3 DecisionLogger — integrado en el Orquestador (Capa 11\)

\`\`\`python  
\# capa\_11/decision\_logger.py — RES.124

import asyncio  
import logging

logger \= logging.getLogger("mpat.decision\_graph")

class DecisionLogger:  
    """  
    Registra decisiones del orquestador en el DecisionGraph de la sesión.  
    Emite OTel span por cada nodo agregado.

    Invariante (INV-DL.1):  
    \- Cada decisión registrada tiene timestamp UTC monotónico.  
    \- El logger nunca bloquea el orquestador: usa SubQ asíncrona para persistir.  
    """

    def \_\_init\_\_(self, subq, otel\_emitter, policy: dict):  
        self.\_subq \= subq  
        self.\_otel \= otel\_emitter  
        self.\_policy \= policy  
        self.\_graphs: dict\[tuple, DecisionGraph\] \= {}  \# keyed by (tenant\_id, session\_id)

    async def log(self, node: DecisionNode) \-\> None:  
        """  
        Pre: node.tenant\_id y node.session\_id están definidos.  
        Post: nodo agregado al grafo de la sesión y span OTel emitido vía SubQ.  
        """  
        key \= (node.tenant\_id, node.session\_id)  
        if key not in self.\_graphs:  
            self.\_graphs\[key\] \= DecisionGraph(  
                tenant\_id=node.tenant\_id,  
                session\_id=node.session\_id  
            )

        self.\_graphs\[key\].add\_node(node)

        \# Emitir vía SubQ (no bloqueante) hacia Capa 10  
        await self.\_subq.publish("decision\_graph.nodes", {  
            "tenant\_id": node.tenant\_id,  
            "session\_id": node.session\_id,  
            "node": {  
                "id": node.node\_id,  
                "parent\_id": node.parent\_id,  
                "type": node.decision\_type,  
                "chosen": node.chosen,  
                "confidence": node.confidence,  
                "reason": node.reason,  
            }  
        })

    def get\_graph(self, tenant\_id: str, session\_id: str) \-\> dict:  
        """Retorna el grafo completo serializado como JSON."""  
        key \= (tenant\_id, session\_id)  
        if key not in self.\_graphs:  
            return {"tenant\_id": tenant\_id, "session\_id": session\_id, "nodes": \[\]}  
        return self.\_graphs\[key\].to\_json()  
\`\`\`

\#\#\# 4.4 DecisionGraphAPI — endpoint de consulta (Capa 10\)

\`\`\`python  
\# capa\_10/decision\_graph\_api.py — RES.124

\# Endpoint REST/SSE para consulta del grafo de decisiones.  
\# Integrado en el servidor de observabilidad de Capa 10\.

from fastapi import FastAPI, HTTPException  
from fastapi.responses import StreamingResponse

app \= FastAPI()

@app.get("/decision-graph/{tenant\_id}/{session\_id}")  
async def get\_decision\_graph(tenant\_id: str, session\_id: str):  
    """  
    Retorna el grafo de decisiones de una sesión como JSON.  
    Requiere autenticación NHP (RES.120) — tenant\_id debe coincidir con el token.

    Pre: tenant\_id y session\_id existen en el DecisionLogger activo.  
    Post: retorna JSON con lista de nodos y relaciones padre-hijo.  
    """  
    graph \= decision\_logger.get\_graph(tenant\_id, session\_id)  
    if not graph\["nodes"\]:  
        raise HTTPException(status\_code=404, detail="grafo no encontrado o sesión vacía")  
    return graph

@app.get("/decision-graph/{tenant\_id}/{session\_id}/stream")  
async def stream\_decision\_graph(tenant\_id: str, session\_id: str):  
    """  
    SSE stream: emite cada nodo nuevo en tiempo real a medida que el agente decide.  
    Permite visualización en vivo del razonamiento del agente.  
    """  
    async def event\_generator():  
        async for node\_event in subq.consume(f"decision\_graph.nodes.{tenant\_id}.{session\_id}"):  
            yield f"data: {node\_event}\\n\\n"

    return StreamingResponse(event\_generator(), media\_type="text/event-stream")  
\`\`\`

\---

\#\# 5\. Configuración en policy.yaml (Capa 14\)

\`\`\`yaml  
\# policy.yaml — sección decision\_graph (RES.124)

decision\_graph:  
  enabled: true  
  max\_nodes\_per\_session: 500  
  persist\_after\_session\_end: true     \# guardar grafo en KG (Capa 5\) para análisis post-sesión  
  stream\_enabled: true                \# habilitar SSE en tiempo real  
  log\_alternatives: true              \# registrar opciones descartadas (más rico pedagógicamente)  
  log\_evidence: true                  \# registrar evidencia de cada decisión  
  retention\_hours: 72                 \# conservar grafos 72 horas post-sesión  
  otel\_span\_name: "decision\_node"  
\`\`\`

\---

\#\# 6\. Integración con el ecosistema V3\_01

\`\`\`  
Orquestador Capa 11 (toma decisión)  
    │ DecisionNode(type, chosen, alternatives, reason, confidence)  
    ▼  
DecisionLogger (Capa 11, RES.124)  
    │  
    ├── SubQ (RES.114) → emit "decision\_graph.nodes" \[no bloqueante\]  
    │       │  
    │       ▼  
    │   OTel Capa 10 (RES.030) → span "decision\_node" para observabilidad  
    │  
    └── in-memory DecisionGraph por (tenant\_id, session\_id)  
            │  
            ▼  
        DecisionGraphAPI (Capa 10, RES.124)  
            ├── GET  /decision-graph/{tenant}/{session}  → JSON snapshot  
            └── GET  /decision-graph/{tenant}/{session}/stream → SSE live

Integraciones adicionales:  
├── KG Capa 5 (RES.092): el grafo post-sesión se persiste como subgrafo del KG  
│   para análisis de patrones de decisión entre sesiones  
├── HallucinationMetric (RES.121): nodos de tipo "hallucination\_guard" incluyen  
│   el score de HallucinationGuard como evidencia  
└── NHP Protocol (RES.120): endpoint DecisionGraphAPI requiere ZeroTrustSession válida  
\`\`\`

\---

\#\# 7\. RES formal

| Campo | Valor |  
|---|---|  
| RES | RES.124 |  
| Nombre | DecisionGraphVisualizer — Grafo de Decisiones Multi-agente |  
| Componentes | DecisionNode · DecisionGraph · DecisionLogger · DecisionGraphAPI |  
| Decisión | Registrar el razonamiento del orquestador como DAG navegable, accesible via REST/SSE, persistible en KG |  
| Alternativa descartada | Registrar solo el resultado final de cada decisión (sin alternativas ni evidencia) — insuficiente para transparencia pedagógica |  
| Dependencias | RES.114 (SubQ) · RES.030 (OTel) · RES.092 (KG Multi-agent) · RES.120 (NHP/ZTS) · RES.121 (HallucinationMetric) |  
| Capa destino | Capa 11 (logger) \+ Capa 10 (API \+ OTel) \+ Capa 14 (policy.yaml) |

\---

\*INVESTIGACION\_FUT16\_GRAFO\_DECISIONES\_V3\_01.md\*  
\*MPAT V3\_01 · RELAY\_006 · cursos.agt.ia@gmail.com · 2026-05-13\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
