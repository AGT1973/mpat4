"""
T008__hydration_loader.py
DESTINO FINAL: session_scheduler/hydration_loader.py
RES.163 - MPAT4 | Relay: RELAY_009 | 2026-05-23
Autor: cursos.agt.ia@gmail.com (docente_AGT_2026)


V4-INV-MEMORY.4: hydration IDEMPOTENTE.
N llamadas con mismo relay_packet_id producen el mismo estado inicial.


que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional
from session_scheduler.session_scheduler_schema_v4 import HydrationResult


logger = logging.getLogger("mpat.hydration_loader")




class HydrationLoader:
    """
    Carga un RelayPacket en una sesion nueva.


    Flujo load():
      1. Descargar RelayPacket desde relay_store/
      2. Verificar firma HMAC via kernel.verify_signature()
      3. Cargar EpisodicSnapshot en memory_fabric/
      4. Registrar referencias SemanticSnapshot en vector_runtime/
      5. Activar GovernanceSnapshot.policies_active en OPAEngine
      6. Retornar True si OK


    V4-INV-MEMORY.4: si relay_packet_id ya fue cargado en esta sesion,
    retorna True inmediatamente sin re-procesar (idempotencia).
    """


    def __init__(self, kernel, opa_engine, relay_store_path: str = ".mpat/relay_store"):
        self._kernel = kernel
        self._opa = opa_engine
        self._relay_store = relay_store_path
        # Cache de sesiones ya hidratadas (idempotencia V4-INV-MEMORY.4)
        self._hydrated: set[str] = set()


    async def load(
        self,
        tenant_id: str,
        session_id: str,
        relay_packet_id: str,
    ) -> bool:
        """
        Carga el RelayPacket en la sesion indicada.
        Retorna True si la hydration fue exitosa.
        Idempotente: llamadas repetidas con mismo relay_packet_id retornan True.
        """
        # V4-INV-MEMORY.4: idempotencia
        cache_key = f"{session_id}:{relay_packet_id}"
        if cache_key in self._hydrated:
            logger.debug("Hydration ya aplicada (idempotente) session=%s packet=%s",
                         session_id, relay_packet_id)
            return True


        import time
        t0 = time.monotonic()


        try:
            # PASO 1: Obtener RelayPacket
            packet = await self._fetch_relay_packet(tenant_id, relay_packet_id)
            if not packet:
                logger.error("RelayPacket no encontrado: %s", relay_packet_id)
                return False


            # PASO 2: Verificar firma HMAC
            valid = await self._kernel.verify_signature(
                tenant_id=tenant_id,
                payload=packet.get("payload_bytes", b""),
                signature=packet.get("hmac_signature", ""),
            )
            if not valid:
                logger.error("HMAC invalido relay_packet=%s", relay_packet_id)
                return False


            # PASO 3: Cargar EpisodicSnapshot
            episodic = packet.get("episodic_snapshot", {})
            episodic_count = await self._load_episodic(session_id, tenant_id, episodic)


            # PASO 4: Cargar referencias SemanticSnapshot
            semantic = packet.get("semantic_snapshot", {})
            semantic_count = await self._load_semantic(session_id, tenant_id, semantic)


            # PASO 5: Activar GovernanceSnapshot
            governance = packet.get("governance_snapshot", {})
            policies_count = await self._activate_governance(tenant_id, governance)


            elapsed_ms = (time.monotonic() - t0) * 1000
            self._hydrated.add(cache_key)


            result = HydrationResult(
                success=True,
                session_id=session_id,
                tenant_id=tenant_id,
                episodic_fragments_loaded=episodic_count,
                semantic_refs_loaded=semantic_count,
                policies_activated=policies_count,
                hydration_ms=elapsed_ms,
            )
            logger.info("Hydration OK session=%s packet=%s ms=%.1f episodic=%d semantic=%d policies=%d",
                        session_id, relay_packet_id, elapsed_ms,
                        episodic_count, semantic_count, policies_count)
            return True


        except Exception as exc:
            logger.error("Hydration FAILED session=%s packet=%s: %s",
                         session_id, relay_packet_id, exc)
            return False


    async def _fetch_relay_packet(self, tenant_id: str, relay_packet_id: str) -> Optional[dict]:
        """Descarga RelayPacket desde relay_store/ local."""
        import json, os
        path = os.path.join(self._relay_store, tenant_id, f"{relay_packet_id}.json")
        if not os.path.exists(path):
            return None
        with open(path) as f:
            return json.load(f)


    async def _load_episodic(self, session_id: str, tenant_id: str, snapshot: dict) -> int:
        """Carga fragmentos episodicos en memory_fabric/."""
        fragments = snapshot.get("fragments", [])
        # TODO: integrar con memory_fabric cuando este disponible
        logger.debug("Episodic: %d fragmentos cargados session=%s", len(fragments), session_id)
        return len(fragments)


    async def _load_semantic(self, session_id: str, tenant_id: str, snapshot: dict) -> int:
        """Registra referencias semanticas en vector_runtime/."""
        refs = snapshot.get("vector_refs", [])
        # TODO: integrar con vector_runtime cuando este disponible
        logger.debug("Semantic: %d refs cargados session=%s", len(refs), session_id)
        return len(refs)


    async def _activate_governance(self, tenant_id: str, snapshot: dict) -> int:
        """Activa politicas del GovernanceSnapshot en OPAEngine."""
        policies = snapshot.get("policies_active", [])
        for policy in policies:
            await self._opa.activate_policy(tenant_id=tenant_id, policy=policy)
        logger.debug("Governance: %d politicas activadas tenant=%s", len(policies), tenant_id)
        return len(policies)