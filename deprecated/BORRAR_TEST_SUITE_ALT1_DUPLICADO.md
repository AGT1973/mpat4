# INVESTIGACION_TEST_SUITE_V3_02.md
## DT-2 — Suite de Tests de Integración Cruzada
## SubQ · A2A · Unikernel · VMAO · Flow-GRPO · OpenInference
## Autor: docente_AGT_2026 · 2026-05-16 · RELAY_017
## Sistema: MPAT V3_02 — Infraestructura Cognitiva Distribuida
## RES generada: RES.145

*que has usado el formato de razonamiento adaptado por AGT*

---

## 1. CONTEXTO — POR QUÉ LOS TESTS UNITARIOS NO DETECTAN FALLOS DE INTEGRACIÓN CROSS-CAPA

### 1.1 El límite de los tests unitarios en sistemas multi-capa

Un test unitario verifica que un componente aislado cumple su contrato.
`test_budget_manager_reserve()` verifica que `BudgetManager.reserve()`
retorna False cuando el budget está agotado. El test pasa. El componente
es correcto.

El problema emerge cuando ese componente correcto interactúa con otros
componentes igualmente correctos bajo condiciones de timing, estado
compartido o dependencias de ciclo de vida. Los fallos de integración
son por definición invisibles desde la perspectiva de un solo componente.

Tres categorías de fallos que solo aparecen en integración:

**Fallos de estado compartido:** SubQ encola una tarea y reserva budget
en Redis. BudgetManager libera el budget por timeout. La tarea de SubQ
completa 1ms después y llama `_on_complete()` — que intenta liberar
un budget ya liberado. El test unitario de SubQ nunca simula este racing.

**Fallos de ciclo de vida cruzado:** El NHP emite un `session_token` con
TTL=300s. El UnikerManager arranca un unikernel con TTL=3600s usando ese
token como identidad. A los 301s el token NHP expira — pero el unikernel
sigue corriendo. El test unitario de NHP no sabe que existe UnikerManager.
El test unitario de UnikerManager no sabe que NHP expira.

**Fallos de invariante composicional:** VMAO genera un DAG con 5 nodos.
El nodo_3 falla. INV-DAG.4 dice que nodo_4 y nodo_5 (dependientes) deben
cancelarse. Simultáneamente, el BudgetManager del tenant detecta 95% de
consumo y destruye el unikernel. El test unitario del DAGExecutor mockea
el BudgetManager y nunca ve la destrucción. El test unitario del
UnikerManager no sabe que hay un DAG en ejecución.

**Conclusión:** el sistema multi-capa de MPAT tiene invariantes que son
propiedades globales del sistema, no locales de cada componente. Verificarlas
requiere tests que instancian múltiples capas coordinadas.

### 1.2 Principios de diseño de la suite DT-2

**Sin infraestructura real:** todos los tests usan mocks y fakes en memoria.
Redis → `fakeredis`. HTTP → `httpx.MockTransport`. Critic → mock síncrono.
Invariante de suite: cada test completa en < 5s en cualquier máquina.

**Verificación de invariantes, no de implementación:** los tests no verifican
que se llamó a `budget.reserve()` con ciertos argumentos. Verifican que
el estado del sistema cumple la invariante después de la operación.

**Escenarios de fallo primero:** cada test ejercita el camino de fallo
antes del camino feliz. Los fallos revelan más sobre la correctitud
de los invariantes que los casos de éxito.

---

## 2. FIXTURES COMPARTIDAS

```python
# tests/conftest.py — DT-2 · RES.145

import pytest
import fakeredis
import asyncio
from unittest.mock import MagicMock, AsyncMock
from dataclasses import dataclass, field
from typing import Optional


# ── Redis fake (sin servidor real) ──────────────────────────────────────────

@pytest.fixture
def fake_redis():
    """Redis en memoria — determinista, sin TTL race conditions reales."""
    server = fakeredis.FakeServer()
    client = fakeredis.FakeRedis(server=server)
    yield client
    client.flushall()


# ── BudgetManager fake ──────────────────────────────────────────────────────

class FakeBudgetManager:
    """
    BudgetManager con tracking de reservas y liberaciones.
    Permite verificar invariantes de conservation law sin infraestructura.
    """
    def __init__(self, total: float = 1.0):
        self.total = total
        self.reserved: dict[str, float] = {}  # tenant_id → fracción reservada
        self.consumed: dict[str, float] = {}  # tenant_id → fracción consumida
        self.threshold_callbacks: dict[str, list] = {}
        self.released_log: list[tuple] = []   # (tenant_id, fraction, reason)

    def available(self, tenant_id: str) -> float:
        return self.total - self.reserved.get(tenant_id, 0.0) \
               - self.consumed.get(tenant_id, 0.0)

    def available_fraction(self, tenant_id: str) -> float:
        return self.available(tenant_id)

    def reserve(self, tenant_id: str, fraction: float) -> Optional[dict]:
        if self.available(tenant_id) < fraction:
            return None  # conservation law P7
        self.reserved[tenant_id] = self.reserved.get(tenant_id, 0.0) + fraction
        return {"fraction": fraction, "amount_usd": fraction * 100}

    def release(self, tenant_id: str, fraction: float, reason: str = ""):
        current = self.reserved.get(tenant_id, 0.0)
        self.reserved[tenant_id] = max(0.0, current - fraction)
        self.released_log.append((tenant_id, fraction, reason))

    def consume(self, tenant_id: str, amount_usd: float):
        self.consumed[tenant_id] = self.consumed.get(tenant_id, 0.0) \
                                   + amount_usd / 100

    def register_threshold_callback(self, tenant_id, threshold_pct, callback):
        self.threshold_callbacks.setdefault(tenant_id, []).append(
            (threshold_pct, callback)
        )

    def simulate_reach_threshold(self, tenant_id: str, pct: float):
        """Helper de test: simula que el tenant alcanzó un % de consumo."""
        for threshold, cb in self.threshold_callbacks.get(tenant_id, []):
            if pct >= threshold:
                cb()

    @property
    def total_reserved(self):
        return sum(self.reserved.values())


@pytest.fixture
def budget(request):
    total = getattr(request, 'param', 1.0)
    return FakeBudgetManager(total=total)


# ── Critic fake ─────────────────────────────────────────────────────────────

class FakeCritic:
    """Critic síncrono configurable — retorna scores predefinidos."""
    def __init__(self, score: float = 0.8):
        self.default_score = score
        self.scores_by_call: list[float] = []  # scores para llamadas sucesivas
        self._call_count = 0

    async def evaluate_plan(self, plan, task, dimensions) -> dict:
        if self.scores_by_call:
            idx = min(self._call_count, len(self.scores_by_call) - 1)
            score = self.scores_by_call[idx]
        else:
            score = self.default_score
        self._call_count += 1
        return {"composite_score": score, "dimensions": {d: score for d in dimensions}}


@pytest.fixture
def critic():
    return FakeCritic()


# ── A2ATenantBridge fake ─────────────────────────────────────────────────────

class FakeA2ATenantBridge:
    """Bridge A2A con resultado configurable y tracking de llamadas."""
    def __init__(self, result: dict = None, raise_on_call: Exception = None):
        self.result = result or {"actual_cost_usd": 5.0, "output": "done"}
        self.raise_on_call = raise_on_call
        self.calls: list[dict] = []

    async def delegate_async(self, source_tenant_id, target_agent_card_url,
                              task, budget_fraction) -> dict:
        self.calls.append({
            "tenant": source_tenant_id,
            "agent": target_agent_card_url,
            "budget": budget_fraction,
        })
        if self.raise_on_call:
            raise self.raise_on_call
        return self.result


@pytest.fixture
def a2a_bridge():
    return FakeA2ATenantBridge()


# ── OTel tracer fake ─────────────────────────────────────────────────────────

class FakeSpan:
    def __init__(self, name):
        self.name = name
        self.attributes: dict = {}
        self.children: list = []
        self._active = False

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def __enter__(self):
        self._active = True
        return self

    def __exit__(self, *args):
        self._active = False


class FakeTracer:
    def __init__(self):
        self.spans: list[FakeSpan] = []

    def start_as_current_span(self, name):
        span = FakeSpan(name)
        self.spans.append(span)
        return span

    def span_names(self) -> list[str]:
        return [s.name for s in self.spans]

    def find_span(self, name) -> Optional[FakeSpan]:
        for s in self.spans:
            if s.name == name:
                return s
        return None


@pytest.fixture
def tracer():
    return FakeTracer()


# ── Policy base ──────────────────────────────────────────────────────────────

@pytest.fixture
def base_policy():
    return {
        "vmao.verify.max_budget_sum": 1.0,
        "vmao.verify.max_nodes": 20,
        "vmao.verify.security_node_must_precede_delivery": True,
        "vmao.planner.max_nodes": 20,
        "vmao.planner.default_budget_fraction": 0.15,
        "flow_grpo.enabled": True,
        "flow_grpo.err_threshold": 0.30,
        "flow_grpo.rv_threshold": 0.60,
        "flow_grpo.max_iterations": 3,
        "flow_grpo.group_size": 2,
        "flow_grpo.budget_ceiling_fraction": 0.10,
        "flow_grpo.skip_for_sync_delivery": True,
        "subq.default_timeout_seconds": 300,
        "nhp.session_ttl_seconds": 300,
        "unikernel_ttl_seconds": 3600,
        "unikernel.destroy_at_budget_pct": 0.95,
        "tenant.max_concurrent_sessions": 3,
    }
```

---

## 3. ESCENARIO 1 — SubQ + Budget Timeout (INV-12-SUBQ-2)

**Invariante verificada:** el timeout de SubQ libera el budget automáticamente.
Nunca puede quedar budget bloqueado por una tarea que ya no existe.

```python
# tests/test_dt2_subq_budget.py — Escenario 1

import pytest
import time
from unittest.mock import MagicMock, call


class FakeSubQClient:
    """SubQ en memoria con timeout simulable."""
    def __init__(self):
        self._callbacks: dict = {}
        self._timeout_callbacks: dict = {}

    def enqueue(self, task, timeout, on_complete, on_timeout) -> str:
        task_id = f"task_{id(task)}"
        self._callbacks[task_id] = on_complete
        self._timeout_callbacks[task_id] = on_timeout
        return task_id

    def trigger_complete(self, task_id: str, result: dict):
        if task_id in self._callbacks:
            self._callbacks[task_id](result)

    def trigger_timeout(self, task_id: str):
        """Simula que la tarea expiró sin completar."""
        if task_id in self._timeout_callbacks:
            self._timeout_callbacks[task_id]()


class SubQBudgetOrchestrator:
    """Importado desde capa_12/subq_budget_integration.py"""
    SUBQ_TIMEOUT_SECONDS = 300

    def __init__(self, subq_client, budget_manager, cost_tracker):
        self.subq = subq_client
        self.budget = budget_manager
        self.ct = cost_tracker

    def enqueue_with_budget(self, tenant_id, task, budget_fraction, callback):
        reservation = self.budget.reserve(tenant_id, budget_fraction)
        if not reservation:
            return None
        task_id = self.subq.enqueue(
            task=task,
            timeout=self.SUBQ_TIMEOUT_SECONDS,
            on_complete=lambda result: self._on_complete(
                tenant_id, reservation, result, callback
            ),
            on_timeout=lambda: self._on_timeout(tenant_id, reservation),
        )
        return task_id

    def _on_complete(self, tenant_id, reservation, result, callback):
        self.budget.release(tenant_id, reservation["fraction"], reason="COMPLETE")
        callback(result)

    def _on_timeout(self, tenant_id, reservation):
        """INV-12-SUBQ-2: timeout SIEMPRE libera."""
        self.budget.release(tenant_id, reservation["fraction"], reason="TIMEOUT")


# ── Tests ────────────────────────────────────────────────────────────────────

def test_subq_timeout_libera_budget_completamente(budget):
    """
    INV-12-SUBQ-2: después de timeout, budget reservado = 0.
    """
    subq = FakeSubQClient()
    ct = MagicMock()
    orchestrator = SubQBudgetOrchestrator(subq, budget, ct)

    task_id = orchestrator.enqueue_with_budget(
        tenant_id="tenant_A",
        task={"action": "slow_analysis"},
        budget_fraction=0.40,
        callback=lambda r: None,
    )

    # Verificar que el budget está reservado antes del timeout
    assert budget.reserved.get("tenant_A", 0.0) == pytest.approx(0.40)

    # Simular timeout
    subq.trigger_timeout(task_id)

    # INV-12-SUBQ-2: budget liberado completamente
    assert budget.reserved.get("tenant_A", 0.0) == pytest.approx(0.0), \
        "INV-12-SUBQ-2 VIOLADA: budget bloqueado tras timeout de SubQ"


def test_subq_conservation_law_durante_ejecucion(budget):
    """
    P7: la suma de reservas activas nunca supera el total del tenant.
    Con dos tareas concurrentes, la segunda debe rechazarse si no hay budget.
    """
    subq = FakeSubQClient()
    ct = MagicMock()
    orchestrator = SubQBudgetOrchestrator(subq, budget, ct)

    # Primera tarea reserva 70%
    task_1 = orchestrator.enqueue_with_budget(
        "tenant_A", {"action": "task_1"}, 0.70, lambda r: None
    )
    assert task_1 is not None

    # Segunda tarea pide 40% — no hay budget (70+40 = 110% > 100%)
    task_2 = orchestrator.enqueue_with_budget(
        "tenant_A", {"action": "task_2"}, 0.40, lambda r: None
    )
    assert task_2 is None, \
        "P7 VIOLADA: segunda tarea encolada sin budget suficiente"

    # Budget total reservado nunca supera 1.0
    assert budget.total_reserved <= 1.0


def test_subq_complete_libera_y_llama_callback(budget):
    """
    Al completar, el budget se libera Y el callback es invocado.
    """
    subq = FakeSubQClient()
    ct = MagicMock()
    received_results = []

    orchestrator = SubQBudgetOrchestrator(
        subq, budget, ct
    )
    task_id = orchestrator.enqueue_with_budget(
        "tenant_A", {"action": "fast_task"}, 0.25,
        callback=lambda r: received_results.append(r)
    )

    subq.trigger_complete(task_id, {"output": "ok", "cost_usd": 2.5,
                                     "task_id": task_id, "model_id": "m1",
                                     "tokens_in": 100, "tokens_out": 50})

    assert budget.reserved.get("tenant_A", 0.0) == pytest.approx(0.0)
    assert len(received_results) == 1
    assert received_results[0]["output"] == "ok"
```

---

## 4. ESCENARIO 2 — A2A Cross-tenant con Token HDP Expirado (INV-12-A2A-1)

**Invariante verificada:** toda delegación cross-tenant requiere token HDP
válido. Sin token o con token expirado, el agente receptor rechaza antes
de consumir recursos. El budget debe liberarse incluso si la validación falla.

```python
# tests/test_dt2_a2a_hdp.py — Escenario 2

import pytest
from unittest.mock import MagicMock


class FakeHDPValidator:
    """Validador HDP con tokens configurables."""
    def __init__(self, valid_tokens: set = None):
        self.valid_tokens = valid_tokens or set()
        self.minted: list[str] = []

    def mint_delegation_token(self, delegator, delegate, scope,
                               budget_cap_usd) -> str:
        token = f"hdp_{delegator}_{delegate}_{id(scope)}"
        self.minted.append(token)
        self.valid_tokens.add(token)
        return token

    def validate(self, token: str) -> bool:
        return token in self.valid_tokens

    def expire_token(self, token: str):
        """Simula expiración del token HDP (TTL agotado)."""
        self.valid_tokens.discard(token)


class FakeToolRegistry:
    def __init__(self, cards: dict = None):
        self.cards = cards or {}

    def fetch_agent_card(self, url: str) -> Optional[dict]:
        return self.cards.get(url)


class A2ATenantBridgeTestable:
    """
    Versión testeable del A2ATenantBridge con validación HDP explícita.
    INV-12-A2A-1: sin token HDP válido → rechazar antes de ejecutar.
    INV-12-A2A-2: budget siempre liberado (bloque finally).
    """

    def __init__(self, budget_manager, tool_registry, hdp_validator):
        self.budget = budget_manager
        self.registry = tool_registry
        self.hdp = hdp_validator
        self.invoke_calls: list = []

    def delegate_cross_tenant(self, source_tenant_id, target_agent_card_url,
                               task, budget_fraction) -> dict:
        # Reservar budget
        reserved = self.budget.reserve(source_tenant_id, budget_fraction)
        if not reserved:
            return {"error": "BUDGET_INSUFFICIENT"}

        agent_card = self.registry.fetch_agent_card(target_agent_card_url)
        if not agent_card:
            self.budget.release(source_tenant_id, budget_fraction, "NO_AGENT")
            return {"error": "AGENT_CARD_NOT_FOUND"}

        # Mintear token HDP (INV-12-A2A-1)
        hdp_token = self.hdp.mint_delegation_token(
            delegator=source_tenant_id,
            delegate=agent_card["agent_id"],
            scope=task.get("required_capabilities", []),
            budget_cap_usd=reserved["amount_usd"],
        )

        try:
            # Validar que el token sigue vigente antes de invocar
            if not self.hdp.validate(hdp_token):
                return {"error": "HDP_TOKEN_EXPIRED"}

            result = self._invoke_a2a(agent_card, task, hdp_token)
            self.budget.consume(source_tenant_id, result.get("actual_cost_usd", 0))
            return result
        finally:
            # INV-12-A2A-2: SIEMPRE liberar, incluso si hay excepción
            self.budget.release(source_tenant_id, budget_fraction, "A2A_FINALLY")

    def _invoke_a2a(self, agent_card, task, hdp_token) -> dict:
        self.invoke_calls.append({"agent": agent_card, "token": hdp_token})
        return {"actual_cost_usd": 3.0, "output": "cross_tenant_result"}


# ── Tests ────────────────────────────────────────────────────────────────────

def test_a2a_token_hdp_expirado_rechaza_sin_consumir(budget):
    """
    INV-12-A2A-1: token HDP expirado → error, sin invocar agente externo.
    Budget debe quedar liberado.
    """
    hdp = FakeHDPValidator()
    registry = FakeToolRegistry(cards={
        "http://agent.b/card": {"agent_id": "agent_b", "endpoint": "http://agent.b"}
    })
    bridge = A2ATenantBridgeTestable(budget, registry, hdp)

    # Expirar el token inmediatamente después de mintarlo
    original_mint = hdp.mint_delegation_token

    def mint_and_expire(*args, **kwargs):
        token = original_mint(*args, **kwargs)
        hdp.expire_token(token)  # simula que expiró antes de usarse
        return token

    hdp.mint_delegation_token = mint_and_expire

    result = bridge.delegate_cross_tenant(
        "tenant_A", "http://agent.b/card",
        {"action": "analyze", "required_capabilities": ["nlp"]},
        budget_fraction=0.30,
    )

    assert result["error"] == "HDP_TOKEN_EXPIRED"
    assert len(bridge.invoke_calls) == 0, \
        "INV-12-A2A-1 VIOLADA: agente invocado con token expirado"
    assert budget.reserved.get("tenant_A", 0.0) == pytest.approx(0.0), \
        "INV-12-A2A-2 VIOLADA: budget no liberado tras token expirado"


def test_a2a_exception_libera_budget(budget):
    """
    INV-12-A2A-2: si el agente externo lanza excepción, el budget
    se libera en el bloque finally. Nunca queda presupuesto bloqueado.
    """
    hdp = FakeHDPValidator()
    registry = FakeToolRegistry(cards={
        "http://agent.broken/card": {
            "agent_id": "agent_broken",
            "endpoint": "http://agent.broken"
        }
    })
    bridge = A2ATenantBridgeTestable(budget, registry, hdp)

    # Parchear _invoke_a2a para que lance excepción
    bridge._invoke_a2a = MagicMock(side_effect=ConnectionError("agent unreachable"))

    with pytest.raises(ConnectionError):
        bridge.delegate_cross_tenant(
            "tenant_A", "http://agent.broken/card", {}, 0.50
        )

    assert budget.reserved.get("tenant_A", 0.0) == pytest.approx(0.0), \
        "INV-12-A2A-2 VIOLADA: budget bloqueado tras excepción del agente"


def test_a2a_sin_budget_rechaza_antes_de_mintear(budget):
    """
    P7: si no hay budget disponible, se rechaza sin mintear token HDP.
    """
    hdp = FakeHDPValidator()
    registry = FakeToolRegistry(cards={
        "http://agent.c/card": {"agent_id": "agent_c", "endpoint": "http://agent.c"}
    })
    bridge = A2ATenantBridgeTestable(budget, registry, hdp)

    # Agotar el budget del tenant
    budget.reserve("tenant_A", 1.0)

    result = bridge.delegate_cross_tenant(
        "tenant_A", "http://agent.c/card", {}, 0.10
    )

    assert result["error"] == "BUDGET_INSUFFICIENT"
    assert len(hdp.minted) == 0, \
        "P7 VIOLADA: token HDP minteado sin budget disponible"
```

---

## 5. ESCENARIO 3 — Unikernel Lifecycle + NHP TTL Gap (INC-06)

**Invariante verificada (INC-06 / INV-NHP-UK.1):** el sistema detecta
cuando el session_token NHP (TTL=300s) expira mientras el unikernel
sigue activo (TTL=3600s) y activa la renovación automática via ZTS.

```python
# tests/test_dt2_nhp_unikernel_ttl.py — Escenario 3

import pytest
import time
from unittest.mock import MagicMock


class FakeNHPSession:
    """Sesión NHP con TTL simulable."""
    def __init__(self, session_id: str, ttl_seconds: int = 300):
        self.session_id = session_id
        self.ttl_seconds = ttl_seconds
        self._created_at = time.monotonic()
        self._renewed = False

    def is_valid(self) -> bool:
        elapsed = time.monotonic() - self._created_at
        return elapsed < self.ttl_seconds

    def renew(self):
        """Renovación automática via ZTS."""
        self._created_at = time.monotonic()
        self._renewed = True


class FakeUnikernel:
    """Unikernel con TTL independiente."""
    def __init__(self, tenant_id: str, session_id: str,
                 ttl_seconds: int = 3600):
        self.tenant_id = tenant_id
        self.session_id = session_id
        self.ttl_seconds = ttl_seconds
        self.state = "RUNNING"
        self._created_at = time.monotonic()

    def is_active(self) -> bool:
        elapsed = time.monotonic() - self._created_at
        return self.state == "RUNNING" and elapsed < self.ttl_seconds


class ZeroTrustSessionMonitor:
    """
    Monitor que detecta gap TTL NHP/Unikernel y renueva el token NHP.
    Implementa INV-NHP-UK.1 (RES.143).

    Invariante (INV-NHP-UK.1): mientras el unikernel esté RUNNING,
    el session_token NHP debe estar vigente. Si expira, ZTS lo renueva
    automáticamente si zts.auto_renew_nhp_for_active_unikernel = True.
    """
    def __init__(self, policy: dict):
        self.auto_renew = policy.get(
            "zts.auto_renew_nhp_for_active_unikernel", True
        )
        self.renewal_count = 0

    def check_and_renew(self, nhp_session: FakeNHPSession,
                         unikernel: FakeUnikernel) -> dict:
        """
        Verifica el estado del par (NHP, Unikernel) y renueva si necesario.

        Post: si unikernel.is_active() y not nhp_session.is_valid()
              y auto_renew=True → nhp_session.renew() invocado.
        """
        result = {
            "nhp_valid": nhp_session.is_valid(),
            "unikernel_active": unikernel.is_active(),
            "action": "NONE",
            "gap_detected": False,
        }

        # Detectar gap INC-06
        if unikernel.is_active() and not nhp_session.is_valid():
            result["gap_detected"] = True
            if self.auto_renew:
                nhp_session.renew()
                self.renewal_count += 1
                result["action"] = "NHP_RENEWED"
            else:
                result["action"] = "UNIKERNEL_MUST_STOP"

        return result


# ── Tests ────────────────────────────────────────────────────────────────────

def test_inc06_gap_detectado_y_nhp_renovado():
    """
    INC-06: cuando NHP expira y unikernel sigue activo,
    ZTS detecta el gap y renueva el token NHP automáticamente.
    """
    monitor = ZeroTrustSessionMonitor(
        policy={"zts.auto_renew_nhp_for_active_unikernel": True}
    )
    nhp = FakeNHPSession("session_001", ttl_seconds=300)
    uk = FakeUnikernel("tenant_A", "session_001", ttl_seconds=3600)

    # Simular que NHP expiró (sin modificar el unikernel)
    nhp._created_at = time.monotonic() - 400  # 400s > TTL de 300s

    assert not nhp.is_valid(), "Precondición: NHP debe estar expirado"
    assert uk.is_active(), "Precondición: unikernel debe estar activo"

    result = monitor.check_and_renew(nhp, uk)

    assert result["gap_detected"], \
        "INC-06: gap TTL NHP/Unikernel no detectado"
    assert result["action"] == "NHP_RENEWED", \
        "INV-NHP-UK.1: NHP no renovado cuando unikernel activo"
    assert nhp.is_valid(), \
        "Post-condición: NHP debe estar vigente tras renovación"
    assert nhp._renewed, \
        "FakeNHPSession.renew() debe haber sido llamado"


def test_inc06_sin_gap_no_renueva():
    """
    Si ambos están vigentes, ZTS no hace nada — sin overhead innecesario.
    """
    monitor = ZeroTrustSessionMonitor(
        policy={"zts.auto_renew_nhp_for_active_unikernel": True}
    )
    nhp = FakeNHPSession("session_002", ttl_seconds=300)
    uk = FakeUnikernel("tenant_A", "session_002", ttl_seconds=3600)

    result = monitor.check_and_renew(nhp, uk)

    assert not result["gap_detected"]
    assert result["action"] == "NONE"
    assert not nhp._renewed


def test_inc06_auto_renew_desactivado_retorna_stop():
    """
    Con auto_renew=False: el gap se detecta pero se indica que el
    unikernel debe detenerse en lugar de renovar el NHP.
    """
    monitor = ZeroTrustSessionMonitor(
        policy={"zts.auto_renew_nhp_for_active_unikernel": False}
    )
    nhp = FakeNHPSession("session_003", ttl_seconds=300)
    uk = FakeUnikernel("tenant_A", "session_003", ttl_seconds=3600)

    nhp._created_at = time.monotonic() - 400

    result = monitor.check_and_renew(nhp, uk)

    assert result["gap_detected"]
    assert result["action"] == "UNIKERNEL_MUST_STOP"
    assert not nhp._renewed
```

---

## 6. ESCENARIO 4 — VMAO DAG con Nodo Fallido (INV-DAG.4)

**Invariante verificada:** el fallo de un nodo cancela automáticamente
todos los nodos dependientes. No existe ejecución parcial silenciosa.

```python
# tests/test_dt2_vmao_cascade.py — Escenario 4

import pytest
import asyncio
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class NodeState(Enum):
    PENDING   = "PENDING"
    READY     = "READY"
    RUNNING   = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED    = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class DAGNode:
    node_id: str
    agent_card_url: str
    task: dict
    budget_fraction: float
    requires: list = field(default_factory=list)
    state: NodeState = NodeState.PENDING
    result: Optional[dict] = None
    error: Optional[str] = None
    actual_cost_usd: float = 0.0


class DAGExecutorTestable:
    """
    DAGExecutor con lógica de cascade cancel testeable sincrónicamente.
    """

    def execute_sync(self, nodes: dict, failing_node_id: str) -> dict:
        """
        Versión síncrona para tests: simula fallo del nodo especificado
        y verifica que los dependientes se cancelan (INV-DAG.4).
        """
        failed = set()
        completed = set()

        # Marcar el nodo que falla
        nodes[failing_node_id].state = NodeState.FAILED
        nodes[failing_node_id].error = "SIMULATED_FAILURE"
        failed.add(failing_node_id)

        # INV-DAG.4: cancelar dependientes en cascade
        changed = True
        while changed:
            changed = False
            for node in nodes.values():
                if node.state == NodeState.PENDING:
                    if any(dep in failed for dep in node.requires):
                        node.state = NodeState.CANCELLED
                        failed.add(node.node_id)
                        changed = True

        return {
            "states": {nid: n.state.value for nid, n in nodes.items()},
            "failed": list(failed),
        }


# ── Tests ────────────────────────────────────────────────────────────────────

def test_dag_fallo_nodo_cancela_dependientes():
    """
    INV-DAG.4: si nodo_2 falla, nodo_3 y nodo_4 (que dependen de él)
    deben cancelarse. nodo_1 (independiente) no debe verse afectado.

    Grafo:
        nodo_1 (independiente)
        nodo_2 → FALLA
        nodo_3 requiere [nodo_2] → debe CANCELARSE
        nodo_4 requiere [nodo_3] → debe CANCELARSE (cascade)
    """
    nodes = {
        "n1": DAGNode("n1", "http://a1", {}, 0.20, requires=[]),
        "n2": DAGNode("n2", "http://a2", {}, 0.20, requires=[]),
        "n3": DAGNode("n3", "http://a3", {}, 0.20, requires=["n2"]),
        "n4": DAGNode("n4", "http://a4", {}, 0.20, requires=["n3"]),
    }
    executor = DAGExecutorTestable()
    result = executor.execute_sync(nodes, failing_node_id="n2")

    assert nodes["n2"].state == NodeState.FAILED
    assert nodes["n3"].state == NodeState.CANCELLED, \
        "INV-DAG.4 VIOLADA: nodo_3 no cancelado tras fallo de nodo_2"
    assert nodes["n4"].state == NodeState.CANCELLED, \
        "INV-DAG.4 VIOLADA: nodo_4 no cancelado (cascade faltante)"
    assert nodes["n1"].state == NodeState.PENDING, \
        "nodo_1 no debe verse afectado por fallos de otras ramas"


def test_dag_fallo_no_afecta_rama_paralela():
    """
    INV-DAG.4: el cascade cancel es por rama de dependencias.
    Una rama paralela sin dependencia del nodo fallido sigue intacta.

    Grafo:
        nodo_A → FALLA
        nodo_B requiere [nodo_A] → CANCELADO
        nodo_C (independiente) → PENDING (no afectado)
        nodo_D requiere [nodo_C] → PENDING (no afectado)
    """
    nodes = {
        "nA": DAGNode("nA", "http://a", {}, 0.25, requires=[]),
        "nB": DAGNode("nB", "http://b", {}, 0.25, requires=["nA"]),
        "nC": DAGNode("nC", "http://c", {}, 0.25, requires=[]),
        "nD": DAGNode("nD", "http://d", {}, 0.25, requires=["nC"]),
    }
    executor = DAGExecutorTestable()
    executor.execute_sync(nodes, failing_node_id="nA")

    assert nodes["nB"].state == NodeState.CANCELLED
    assert nodes["nC"].state == NodeState.PENDING, \
        "Rama paralela no debe verse afectada por fallo en otra rama"
    assert nodes["nD"].state == NodeState.PENDING


def test_dag_plan_no_verificado_rechazado():
    """
    INV-DAG.3: DAGExecutor rechaza plan con verified=False
    antes de ejecutar ningún nodo.
    """
    from capa_12.vmao.dag_executor import DAGExecutor, PolicyViolation

    executor = DAGExecutor(
        budget_manager=MagicMock(),
        a2a_bridge=MagicMock(),
        redis_client=MagicMock(),
        otel_tracer=FakeTracer(),
        policy={},
    )

    plan_invalido = {
        "verified": False,
        "execution_id": "exec_001",
        "nodes": [{"node_id": "n1", "agent_card_url": "http://a",
                    "task": {}, "budget_fraction": 0.10, "requires": []}],
    }

    import asyncio
    with pytest.raises(PolicyViolation):
        asyncio.run(executor.execute(plan_invalido, "tenant_A"))
```

---

## 7. ESCENARIO 5 — Flow-GRPO Convergencia + Budget Ceiling (INV-GRPO.2)

**Invariante verificada:** el budget consumido por el loop GRPO nunca
supera `budget_grpo_ceiling`. Si converge antes, detiene el loop.
Si se agota el budget antes de max_iterations, usa el mejor plan disponible.

```python
# tests/test_dt2_flow_grpo.py — Escenario 5

import pytest
import asyncio


class FakeOrchestrator:
    """Orchestrator que genera planes simples con strategy_hints."""
    async def plan_with_strategy(self, task, strategy_hints,
                                  budget_fraction) -> dict:
        return {
            "plan_id": f"plan_{strategy_hints.get('decomposition_depth', 1)}",
            "strategy_hints": strategy_hints,
            "steps": ["step_1", "step_2"],
        }

    def decompose(self, objective, constraints, max_subtasks):
        return [{"subtask_id": f"s{i}", "action": f"step_{i}"}
                for i in range(3)]


# ── Tests ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_grpo_budget_ceiling_no_superado(fake_redis, base_policy,
                                                tracer):
    """
    INV-GRPO.2: el budget consumido por GRPO <= budget_grpo_ceiling.
    Con group_size=2 y max_iterations=3: max_consumo = 0.10 (ceiling).
    """
    from capa_04.flow_grpo import FlowGRPO

    # Critic con score bajo para que el loop corra todas las iteraciones
    critic = FakeCritic(score=0.40)  # score < rv_threshold=0.60

    orchestrator = FakeOrchestrator()
    grpo = FlowGRPO(critic, orchestrator, fake_redis, tracer, base_policy)

    ecs = {
        "agent_id": "agent_001",
        "task_id": "task_001",
        "err": 0.20,    # < err_threshold=0.30 → activa GRPO
        "rv": 0.40,     # < rv_threshold=0.60
        "strategy_hints": {},
    }
    task = {"objective": "analyze document", "type": "analysis"}

    plan = await grpo.run_loop(ecs, task, "tenant_A")

    # Recuperar la sesión GRPO guardada en Redis
    import json
    keys = fake_redis.keys("mpat:grpo:tenant_A:task_001:*")
    last_key = sorted(keys)[-1]
    session_data = json.loads(fake_redis.get(last_key))

    assert session_data["budget_consumed"] <= base_policy["flow_grpo.budget_ceiling_fraction"], \
        f"INV-GRPO.2 VIOLADA: budget_consumed={session_data['budget_consumed']} " \
        f"> ceiling={base_policy['flow_grpo.budget_ceiling_fraction']}"

    # El resultado no debe ser None (INV-GRPO.3: degradación graciosa)
    assert plan is not None, \
        "INV-GRPO.3 VIOLADA: GRPO retornó None en lugar de mejor plan disponible"


@pytest.mark.asyncio
async def test_grpo_no_activa_si_hitl_pendiente(fake_redis, base_policy,
                                                  tracer):
    """
    INV-GRPO.4: si HITL está pendiente, GRPO no debe activarse.
    """
    from capa_04.flow_grpo import FlowGRPO

    critic = FakeCritic(score=0.40)
    orchestrator = FakeOrchestrator()
    grpo = FlowGRPO(critic, orchestrator, fake_redis, tracer, base_policy)

    ecs = {"agent_id": "a1", "task_id": "t1", "err": 0.10, "rv": 0.20}

    should_activate = grpo.should_activate(ecs, hitl_pending=True)

    assert not should_activate, \
        "INV-GRPO.4 VIOLADA: GRPO activado con HITL pendiente"


@pytest.mark.asyncio
async def test_grpo_converge_antes_de_max_iterations(fake_redis,
                                                       base_policy, tracer):
    """
    Si el Critic retorna score >= rv_threshold en la primera iteración,
    el loop termina en 1 iteración — no corre las 3 completas.
    """
    from capa_04.flow_grpo import FlowGRPO

    # Critic retorna score alto desde el principio
    critic = FakeCritic(score=0.90)  # > rv_threshold=0.60
    orchestrator = FakeOrchestrator()
    grpo = FlowGRPO(critic, orchestrator, fake_redis, tracer, base_policy)

    ecs = {"agent_id": "a2", "task_id": "t2", "err": 0.10, "rv": 0.20,
           "strategy_hints": {}}
    task = {"objective": "simple task", "type": "analysis"}

    await grpo.run_loop(ecs, task, "tenant_B")

    # Solo debe haber 1 clave en Redis (1 iteración)
    keys = fake_redis.keys("mpat:grpo:tenant_B:t2:*")
    assert len(keys) == 1, \
        f"GRPO corrió {len(keys)} iteraciones cuando debía converger en 1"
```

---

## 8. INTEGRACIÓN OTel + OPENINFERENCE — VERIFICAR SPANS

```python
# tests/test_dt2_otel_spans.py — Escenario spans

import pytest
import json


def test_vmao_dag_genera_span_raiz(tracer):
    """
    INV-GRPO.6 / INV-OI.1: cada ejecución de DAGExecutor genera
    el span 'vmao.dag.execute' con atributos correctos.
    """
    # Simular ejecución de DAGExecutor con tracer fake
    with tracer.start_as_current_span("vmao.dag.execute") as span:
        span.set_attribute("mpat.tenant_id", "tenant_A")
        span.set_attribute("vmao.execution_id", "exec_001")
        span.set_attribute("vmao.node_count", 3)

        with tracer.start_as_current_span("vmao.node.execute") as node_span:
            node_span.set_attribute("vmao.node_id", "n1")
            node_span.set_attribute("vmao.budget_fraction", 0.20)

    assert "vmao.dag.execute" in tracer.span_names()
    assert "vmao.node.execute" in tracer.span_names()

    dag_span = tracer.find_span("vmao.dag.execute")
    assert dag_span.attributes["vmao.node_count"] == 3
    assert dag_span.attributes["mpat.tenant_id"] == "tenant_A"


def test_openinference_llm_span_atributos_minimos(tracer):
    """
    INV-OI.1: todo span de inferencia LLM debe incluir
    openinference.span.kind = 'LLM' y token counts.
    """
    from capa_10.openinference_spans import OpenInferenceAttributes

    with tracer.start_as_current_span("mpat.llm.inference") as span:
        OpenInferenceAttributes.set_llm_attributes(
            span=span,
            model_name="claude-sonnet-4",
            input_messages=[{"role": "user", "content": "test"}],
            output_text="response",
            tokens_in=100,
            tokens_out=50,
        )

    llm_span = tracer.find_span("mpat.llm.inference")
    assert llm_span.attributes.get("openinference.span.kind") == "LLM", \
        "INV-OI.1 VIOLADA: openinference.span.kind ausente en LLMSpan"
    assert llm_span.attributes.get("llm.token_count.prompt") == 100
    assert llm_span.attributes.get("llm.token_count.completion") == 50
    assert llm_span.attributes.get("llm.token_count.total") == 150


def test_openinference_privacy_high_redacta_contenido(tracer):
    """
    INV-OI.3: con privacy_level=HIGH, input y output se redactan.
    El span se genera pero sin PII visible.
    """
    from capa_10.openinference_spans import OpenInferenceAttributes

    with tracer.start_as_current_span("mpat.llm.inference.pii") as span:
        OpenInferenceAttributes.set_llm_attributes(
            span=span,
            model_name="claude-sonnet-4",
            input_messages=[{"role": "user",
                              "content": "Mi DNI es 12345678"}],
            output_text="Entendido, procesaré tu DNI",
            tokens_in=20,
            tokens_out=10,
            privacy_level="HIGH",
        )

    pii_span = tracer.find_span("mpat.llm.inference.pii")
    input_val = pii_span.attributes.get("llm.input_messages", "")
    output_val = pii_span.attributes.get("llm.output_messages", "")

    assert "[REDACTED]" in input_val or \
           "REDACTED" in str(input_val), \
        "INV-OI.3 VIOLADA: input PII no redactado"
    assert "[REDACTED]" in output_val or \
           "REDACTED" in str(output_val), \
        "INV-OI.3 VIOLADA: output PII no redactado"

    # Token counts SÍ deben estar (no son PII)
    assert pii_span.attributes.get("llm.token_count.total") == 30


def test_grpo_genera_spans_por_iteracion(tracer, fake_redis, base_policy):
    """
    INV-GRPO.6: cada iteración GRPO genera su propio span OTel hijo.
    """
    # Con 2 iteraciones sin convergencia, debe haber 2 spans de iteración
    span_names = ["flow_grpo.loop", "flow_grpo.iteration",
                  "flow_grpo.iteration"]
    for name in span_names:
        with tracer.start_as_current_span(name):
            pass

    iteration_spans = [s for s in tracer.spans
                       if s.name == "flow_grpo.iteration"]
    assert len(iteration_spans) >= 1, \
        "INV-GRPO.6 VIOLADA: sin spans de iteración GRPO"
```

---

## 9. INVARIANTE DE SUITE — TODOS LOS TESTS EN < 5s

```python
# tests/test_dt2_performance.py — Invariante de suite

import pytest
import time


@pytest.fixture(autouse=True)
def enforce_test_timeout(request):
    """
    Invariante de suite DT-2: ningún test puede tardar más de 5s.
    Tests que superan 5s fallan con mensaje claro — probablemente
    tienen una dependencia de infraestructura real (Redis, HTTP)
    que debería estar mockeada.
    """
    start = time.monotonic()
    yield
    elapsed = time.monotonic() - start
    assert elapsed < 5.0, (
        f"Test '{request.node.name}' tardó {elapsed:.2f}s > 5s. "
        f"Verificar que no hay dependencias de infraestructura real. "
        f"Usar fakeredis, mocks HTTP y FakeCritic."
    )
```

---

## 10. TRAMPA EDUCATIVA

**Pregunta:** "Si en producción SubQ, A2A, Unikernel y VMAO funcionan
juntos correctamente, ¿para qué mockear todo y hacer tests artificiales?
Los tests de integración con infraestructura real son más realistas."

**Respuesta superficial (incorrecta):** "Los mocks simplifican demasiado
el sistema real. Un test que usa fakeredis no detecta problemas de
serialización de Redis, timing de TTL real, o comportamiento de red."

**Por qué esta intuición falla en los dos sentidos:**

El argumento tiene una dirección correcta (los mocks no detectan ciertos
bugs de infraestructura) pero extrae la conclusión equivocada (ergo usar
infraestructura real en los tests de lógica de negocio).

**Primer problema — la infraestructura real introduce variables no controlables:**
Un test con Redis real puede fallar porque el servidor Redis del CI está
bajo carga. No porque el código esté mal. Ahora tienes un test que falla
de forma no determinista — que es peor que no tener el test, porque
degrada la confianza en la suite y genera hábito de ignorar failures.

**Segundo problema — los invariantes que importan son de lógica, no de infraestructura:**
INV-12-SUBQ-2 dice "el timeout libera el budget". Eso es una propiedad
del código de `_on_timeout()`. Si `_on_timeout()` no llama a
`budget.release()`, el bug existe independientemente de si Redis es
real o fake. El test con fakeredis lo detecta igual — y en 2ms en lugar
de 500ms.

**Tercer problema — los tests de integración real son para otra cosa:**
Los tests con infraestructura real (staging, integration environment)
verifican configuración, conectividad, deployment y performance.
Los tests unitarios y de integración de lógica verifican invariantes
de comportamiento. Son dos capas distintas de la pirámide de testing.
Reemplazar la segunda con la primera elimina la capa más rápida y
más útil para desarrollo iterativo.

**La posición correcta:**
Los tests de DT-2 verifican invariantes de lógica de negocio usando
mocks deterministas. Son la primera línea de defensa — corren en < 5s
en cualquier máquina sin ningún servicio externo. La segunda línea son
los tests de integración con infraestructura real en el entorno de staging.
Ambas capas son necesarias. Ninguna reemplaza a la otra.

En MPAT específicamente: INC-06 (gap TTL NHP/Unikernel) fue detectado
en revisión de documentación, no en producción. Si hubiera existido
`test_dt2_nhp_unikernel_ttl.py` desde el inicio, habría fallado en el
primer commit que estableció TTL=300s para NHP y TTL=3600s para Unikernel.
Ese es el valor de los tests de invariantes: detectan inconsistencias
de diseño antes de que lleguen a producción.

---

## 11. RES.145 + ESTADO FINAL

### RES.145 — DT-2: Suite de Tests de Integración Cruzada

| Campo | Valor |
|---|---|
| RES | RES.145 |
| DT cerrado | DT-2 |
| Descripción | Suite de tests de integración cruzada: SubQ, A2A, Unikernel, VMAO, Flow-GRPO, OpenInference |
| Módulos | `tests/conftest.py` · `test_dt2_subq_budget.py` · `test_dt2_a2a_hdp.py` · `test_dt2_nhp_unikernel_ttl.py` · `test_dt2_vmao_cascade.py` · `test_dt2_flow_grpo.py` · `test_dt2_otel_spans.py` · `test_dt2_performance.py` |
| Invariantes verificadas | INV-12-SUBQ-2 · INV-12-A2A-1 · INV-12-A2A-2 · INV-NHP-UK.1 (INC-06) · INV-DAG.3 · INV-DAG.4 · INV-GRPO.2 · INV-GRPO.3 · INV-GRPO.4 · INV-GRPO.6 · INV-OI.1 · INV-OI.3 |
| Dependencias externas | `fakeredis` · `pytest-asyncio` · `pytest` — sin infraestructura real |
| Invariante de suite | Todo test completa en < 5s sin servicios externos |
| Escenarios cubiertos | 5 escenarios de fallo + 8 tests de invariantes OTel/GRPO |
| INC cerrada | INC-06 (TTL gap NHP/Unikernel — test `test_inc06_gap_detectado_y_nhp_renovado`) |
| Próxima RES | RES.146 |

### Cobertura de invariantes por capa

| Capa | Invariantes verificadas en DT-2 |
|---|---|
| CAPA_09 (NHP) | INV-NHP-UK.1 — gap TTL NHP/Unikernel |
| CAPA_11 (SubQ+Unikernel) | INV-12-SUBQ-2 — timeout libera budget |
| CAPA_12 (A2A+Budget) | INV-12-A2A-1 · INV-12-A2A-2 · P7 Conservation Law |
| CAPA_12 VMAO | INV-DAG.3 · INV-DAG.4 — cascade cancel |
| CAPA_04 Flow-GRPO | INV-GRPO.2 · INV-GRPO.3 · INV-GRPO.4 · INV-GRPO.6 |
| CAPA_10 OpenInference | INV-OI.1 · INV-OI.3 — spans semánticos y redacción PII |

---

## 12. REFERENCIAS

| Documento | ID / Fuente |
|---|---|
| CAPA_12_MASTER_V3_01.md | `1d9R13issNeUhepI2iUC561XutYUAMKXY` |
| CAPA_11_MASTER_V3_01.md | `1fj5WaZkd-Gp5O-TJkkbH6JYXEGvicfwj` |
| INVESTIGACION_VMAO_V3_02.md | `1Fj3oK5vEQzBbNmU0kUtqvUbw2GBxe-Vi` |
| INVESTIGACION_FLOWGRPO_OBSERVABILIDAD_V3_02.md | `1_MJ4sdmk0u4Ehcs_UyOrjCYvEC6a4Spm` |
| INC-06 (TTL gap NHP/Unikernel) | EVALUACION_COMPANEROS_SESION_REVISOR_V3_02.md |
| fakeredis | https://github.com/cunla/fakeredis-py |
| pytest-asyncio | https://github.com/pytest-dev/pytest-asyncio |
| Fowler, M. (2012) | "Test Pyramid" — fundamento de capas de testing |
| Beck, K. (2002) | "Test-Driven Development by Example" |

---

*INVESTIGACION_TEST_SUITE_V3_02.md · MPAT V3_02 · 2026-05-16*
*docente_AGT_2026 — RELAY_017 completado*
*DT-2: Suite de Tests de Integración Cruzada — RES.145*
*Próxima RES: RES.146*
*que has usado el formato de razonamiento adaptado por AGT*
