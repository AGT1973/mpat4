"""
RES164__mesh_router.py
DESTINO FINAL: event_bus/mesh_router.py
RES.164 — MPAT4 | Relay: RELAY_010 | 2026-05-23
Autor: cursos.agt.ia@gmail.com (docente_AGT_2026)


Router de complejidad semántica para el CognitiveEventMesh.
Decide si un evento va a SLM local o a API externa.
Implementa circuit breaker por nodo caído.


INVARIANTES:
  INV-ROUTER.1: la decisión SLM/API se basa en COMPLEJIDAD del payload,
                nunca en preferencia arbitraria.
  INV-ROUTER.2: el circuit breaker protege al mesh de cascadas de fallos.
  INV-ROUTER.3: el estado del circuit breaker es por (tenant_id, node_id).


que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations


import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


logger = logging.getLogger("mpat.mesh_router")




# ---------------------------------------------------------------------------
# Complejidad de evento
# ---------------------------------------------------------------------------


class EventComplexity(str, Enum):
    LOW    = "low"     # SLM local suficiente (Phi-3, Qwen-1.5B)
    MEDIUM = "medium"  # SLM grande o API económica (Claude Haiku, GPT-4o mini)
    HIGH   = "high"    # API premium necesaria (Claude Sonnet, GPT-4o)




@dataclass(frozen=True)
class RoutingDecision:
    complexity: EventComplexity
    target_backend: str          # "slm_local" | "api_haiku" | "api_sonnet"
    target_node_id: Optional[str]
    target_agent_id: Optional[str]
    estimated_tokens: int
    reason: str




# ---------------------------------------------------------------------------
# ComplexityClassifier — heurístico sin modelo externo
# ---------------------------------------------------------------------------


class ComplexityClassifier:
    """
    Clasifica la complejidad de un evento para decidir el backend de inferencia.


    Criterios (sin modelo externo — heurístico local rápido):
      LOW:    payload < 500 chars, event_type en tipos simples, no contiene
              palabras clave de razonamiento complejo.
      MEDIUM: payload 500-2000 chars, o contiene keywords de análisis.
      HIGH:   payload > 2000 chars, o contiene keywords de código/matemáticas/
              razonamiento multi-paso, o es un relay writer task.


    INV-ROUTER.1: clasificación basada en señales del payload, nunca aleatoria.
    """


    # Keywords que elevan la complejidad
    HIGH_KEYWORDS = frozenset([
        "relay", "implementar", "arquitectura", "código", "refactor",
        "matemática", "razonamiento", "analizar profundamente", "investigar",
        "contrato", "schema", "invariante", "sistema distribuido",
    ])
    MEDIUM_KEYWORDS = frozenset([
        "resumir", "comparar", "explicar", "listar", "buscar",
        "planificar", "revisar",
    ])


    def classify(self, event_type: str, payload_str: str) -> EventComplexity:
        payload_lower = payload_str.lower()
        payload_len = len(payload_str)


        # Señales de alta complejidad
        has_high_keyword = any(kw in payload_lower for kw in self.HIGH_KEYWORDS)
        if has_high_keyword or payload_len > 2000:
            return EventComplexity.HIGH


        # Señales de complejidad media
        has_medium_keyword = any(kw in payload_lower for kw in self.MEDIUM_KEYWORDS)
        if has_medium_keyword or payload_len > 500:
            return EventComplexity.MEDIUM


        return EventComplexity.LOW


    def backend_for(self, complexity: EventComplexity) -> str:
        return {
            EventComplexity.LOW:    "slm_local",
            EventComplexity.MEDIUM: "api_haiku",
            EventComplexity.HIGH:   "api_sonnet",
        }[complexity]


    def token_estimate(self, payload_str: str) -> int:
        """Estimación rápida: ~4 chars por token (BPE aproximado)."""
        return max(100, len(payload_str) // 4)




# ---------------------------------------------------------------------------
# CircuitBreaker — por (tenant_id, node_id)
# ---------------------------------------------------------------------------


class CircuitState(str, Enum):
    CLOSED   = "closed"    # Normal — deja pasar
    OPEN     = "open"      # Fallo detectado — bloquea
    HALF_OPEN = "half_open" # Probando recuperación




@dataclass
class CircuitBreaker:
    """
    Circuit breaker por nodo del mesh.


    CLOSED → OPEN: cuando failure_count >= threshold en window_seconds.
    OPEN → HALF_OPEN: después de recovery_seconds.
    HALF_OPEN → CLOSED: si el próximo request tiene éxito.
    HALF_OPEN → OPEN: si el próximo request falla.


    INV-ROUTER.2: protege al mesh de cascadas de fallos.
    INV-ROUTER.3: estado por (tenant_id, node_id).
    """
    tenant_id: str
    node_id: str
    threshold: int = 3
    window_seconds: float = 60.0
    recovery_seconds: float = 30.0


    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _last_failure_time: float = field(default=0.0, init=False)
    _opened_at: float = field(default=0.0, init=False)


    def allow(self) -> bool:
        """Retorna True si se permite el request."""
        now = time.monotonic()


        if self._state == CircuitState.CLOSED:
            # Resetear contador si ya pasó la ventana de tiempo
            if now - self._last_failure_time > self.window_seconds:
                self._failure_count = 0
            return True


        if self._state == CircuitState.OPEN:
            if now - self._opened_at > self.recovery_seconds:
                self._state = CircuitState.HALF_OPEN
                logger.info("CircuitBreaker HALF_OPEN: node=%s", self.node_id)
                return True
            return False


        # HALF_OPEN: dejar pasar un request de prueba
        return True


    def record_success(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            logger.info("CircuitBreaker CLOSED (recuperado): node=%s", self.node_id)


    def record_failure(self) -> None:
        now = time.monotonic()
        self._failure_count += 1
        self._last_failure_time = now


        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            self._opened_at = now
            logger.warning("CircuitBreaker OPEN (reincidencia): node=%s", self.node_id)
            return


        if self._failure_count >= self.threshold:
            self._state = CircuitState.OPEN
            self._opened_at = now
            logger.warning(
                "CircuitBreaker OPEN (threshold=%d): node=%s tenant=%s",
                self.threshold, self.node_id, self.tenant_id,
            )


    @property
    def state(self) -> CircuitState:
        return self._state




# ---------------------------------------------------------------------------
# MeshRouter — orquestador de routing y circuit breakers
# ---------------------------------------------------------------------------


class MeshRouter:
    """
    Router del CognitiveEventMesh.


    Responsabilidades:
      1. Clasificar la complejidad de cada evento (ComplexityClassifier).
      2. Seleccionar el backend de inferencia (SLM local / API externa).
      3. Obtener el nodo del mesh para el routing (desde MeshTopology).
      4. Gestionar circuit breakers por nodo (INV-ROUTER.2/3).
      5. Proveer failover automático cuando un nodo cae.


    Uso típico:
      decision = await router.route(
          tenant_id="escuela_IA",
          event_type="agent.task",
          payload_bytes=b"...",
          mesh_topology=topology,
      )
    """


    def __init__(self):
        self._classifier = ComplexityClassifier()
        self._breakers: dict[tuple[str, str], CircuitBreaker] = {}


    def _get_breaker(self, tenant_id: str, node_id: str) -> CircuitBreaker:
        key = (tenant_id, node_id)
        if key not in self._breakers:
            self._breakers[key] = CircuitBreaker(
                tenant_id=tenant_id, node_id=node_id
            )
        return self._breakers[key]


    async def route(
        self,
        tenant_id: str,
        event_type: str,
        payload_bytes: bytes,
        mesh_topology,  # MeshTopology — import circular evitado con duck typing
        required_specialization: str = "general",
    ) -> RoutingDecision:
        """
        Decide el routing completo para un evento.


        Flujo:
          1. Clasificar complejidad del payload.
          2. Determinar backend (SLM / API).
          3. Obtener nodo por especialización.
          4. Verificar circuit breaker del nodo.
          5. Si breaker OPEN → failover al siguiente nodo disponible.
          6. Si ningún nodo pasa el breaker → RoutingDecision con target_node_id=None.
        """
        payload_str = payload_bytes.decode("utf-8", errors="replace")
        complexity   = self._classifier.classify(event_type, payload_str)
        backend      = self._classifier.backend_for(complexity)
        token_est    = self._classifier.token_estimate(payload_str)


        # Intentar con el nodo de especialización requerida
        node = await mesh_topology.node_for_specialization(
            tenant_id, required_specialization
        )


        if node is None:
            return RoutingDecision(
                complexity=complexity,
                target_backend=backend,
                target_node_id=None,
                target_agent_id=None,
                estimated_tokens=token_est,
                reason="no_nodes_available",
            )


        breaker = self._get_breaker(tenant_id, node.node_id)
        if not breaker.allow():
            logger.warning(
                "CircuitBreaker OPEN para node=%s — buscando failover", node.node_id
            )
            # Failover: buscar nodo general alternativo
            all_alive = await mesh_topology.alive_nodes(tenant_id)
            alternatives = [
                n for n in all_alive
                if n.node_id != node.node_id
                and self._get_breaker(tenant_id, n.node_id).allow()
            ]
            if not alternatives:
                return RoutingDecision(
                    complexity=complexity,
                    target_backend=backend,
                    target_node_id=None,
                    target_agent_id=None,
                    estimated_tokens=token_est,
                    reason="all_circuit_breakers_open",
                )
            node = max(alternatives, key=lambda n: n.capacity_tokens)


        logger.debug(
            "MeshRouter: tenant=%s event=%s complexity=%s backend=%s node=%s",
            tenant_id, event_type, complexity.value, backend, node.node_id,
        )
        return RoutingDecision(
            complexity=complexity,
            target_backend=backend,
            target_node_id=node.node_id,
            target_agent_id=node.agent_id,
            estimated_tokens=token_est,
            reason=f"routed_to_{node.specialization}_node",
        )


    def record_outcome(
        self,
        tenant_id: str,
        node_id: str,
        success: bool,
    ) -> None:
        """Registra el resultado de un request para actualizar el circuit breaker."""
        breaker = self._get_breaker(tenant_id, node_id)
        if success:
            breaker.record_success()
        else:
            breaker.record_failure()


    def breaker_states(self, tenant_id: str) -> dict[str, str]:
        """Retorna el estado de todos los circuit breakers del tenant."""
        return {
            node_id: cb.state.value
            for (tid, node_id), cb in self._breakers.items()
            if tid == tenant_id
        }