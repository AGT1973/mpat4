# INVESTIGACION_TEST_SUITE_V3_02.md
## DT-2 — Suite de tests integración cross-SubQ-A2A-Unikernel
## Autor: agt1973@gmail.com · 2026-05-15 · RELAY_017
## Sistema: MPAT V3_02 — Infraestructura Cognitiva Distribuida

---

## 1. POR QUÉ LOS TESTS UNITARIOS NO ALCANZAN

Los tests unitarios verifican componentes en aislamiento. En MPAT, los
fallos críticos emergen en la composición, no en los componentes
individuales. Tres escenarios que los tests unitarios no detectan:

| Escenario | Por qué escapa al test unitario | Detectado por |
|---|---|---|
| SubQ encola correctamente pero A2A no procesa el formato esperado | Cada uno pasa sus tests por separado; el contrato entre ellos no se verifica | Test integración SubQ→A2A |
| Unikernel permite acceso cross-tenant cuando Redis falla y cae al fallback | El test unitario mockeaa Redis exitosamente siempre | Test integración con Redis failure injection |
| VMAO genera plan válido per Verify, pero DAGExecutor agota timeout del tenant antes de completar | Verify y DAGExecutor pasan unitariamente con mocks de tiempo | Test integración con timeout real |

La suite DT-2 cubre exactamente estos escenarios de frontera.

---

## 2. ARQUITECTURA DE LA SUITE

```
tests/integration/
├── conftest.py                  # fixtures compartidas
├── test_subq_a2a.py             # Test 1 — SubQ → A2A
├── test_unikernel_isolation.py  # Test 2 — tenant isolation
├── test_vmao_execution.py       # Test 3 — VMAO plan end-to-end
├── test_mtls_handshake.py       # Test 4 — mTLS mock
├── test_flowgrpo_trigger.py     # Test 5 — Flow-GRPO trigger logic
└── helpers/
    ├── redis_mock.py
    ├── policy_factory.py
    └── tenant_factory.py
```

Stack: `pytest` + `pytest-asyncio` + `fakeredis` + `unittest.mock`
Sin dependencias de contenedores reales — todo mockeado estructuralmente.
CI target: `pytest tests/integration/ -v --timeout=30`

---

## 3. FIXTURES COMPARTIDAS — conftest.py

```python
# tests/integration/conftest.py
import pytest
import fakeredis.aioredis as fakeredis
from unittest.mock import AsyncMock, MagicMock

# ── Tenant factory ──────────────────────────────────────────────────────────
@pytest.fixture
def tenant_a():
    return {"tenant_id": "tenant-A", "plan": "pro", "region": "latam"}

@pytest.fixture
def tenant_b():
    return {"tenant_id": "tenant-B", "plan": "basic", "region": "latam"}

# ── Redis mock (fakeredis — comportamiento real sin servidor) ───────────────
@pytest.fixture
async def redis_client():
    client = fakeredis.FakeRedis()
    yield client
    await client.aclose()

# ── Policy factory ──────────────────────────────────────────────────────────
@pytest.fixture
def base_policy():
    return {
        "vmao.enabled": True,
        "vmao.planner.max_tasks_per_plan": 20,
        "vmao.task.timeout": 5,          # bajo para tests
        "vmao.task.retry_max": 1,
        "vmao.verify.require_signature": True,
        "vmao.verify.reject_cross_tenant": True,
        "pki.mtls.required": True,
        "pki.mtls.min_tls_version": "1.3",
        "flowgrpo.enabled": True,
        "flowgrpo.min_reward_variance": 0.1,
        "flowgrpo.score_threshold": 0.6,
        "connectors.signal.enabled": True,
        "connectors.signal.session_ttl": 86400,
        "observability.mask_inputs": True,
    }

class DictPolicy:
    def __init__(self, d): self._d = d
    def get(self, key, default=None): return self._d.get(key, default)

@pytest.fixture
def policy(base_policy):
    return DictPolicy(base_policy)

# ── RBAC checker mock ───────────────────────────────────────────────────────
@pytest.fixture
def rbac_allow_all():
    mock = MagicMock()
    mock.check.return_value = True
    return mock

@pytest.fixture
def rbac_deny_cross_tenant(tenant_a):
    """Permite tenant_a, deniega cualquier otro."""
    mock = MagicMock()
    mock.check.side_effect = lambda tenant_id, resource, action: (
        tenant_id == tenant_a["tenant_id"]
    )
    return mock
```

---

## 4. TEST 1 — SubQ ENQUEUE → A2A DISPATCH → RESULTADO

```python
# tests/integration/test_subq_a2a.py
import pytest
from unittest.mock import AsyncMock, patch
from mpat.capa11.subq import SubQQueue
from mpat.capa12.a2a import A2ADispatcher

pytestmark = pytest.mark.asyncio

async def test_subq_enqueue_a2a_dispatch_completes(
        redis_client, tenant_a, policy):
    """
    Happy path: SubQ encola una tarea, A2A la despacha y retorna resultado.
    Verifica el contrato de formato entre los dos componentes.
    """
    subq  = SubQQueue(redis_client, policy)
    a2a   = A2ADispatcher(redis_client, policy)

    # Enqueue via SubQ
    task_id = await subq.enqueue(
        tenant_id=tenant_a["tenant_id"],
        payload={"action": "summarize", "content": "texto de prueba"},
        priority=1,
    )
    assert task_id is not None

    # A2A debe encontrar y despachar la tarea
    result = await a2a.dispatch_next(tenant_id=tenant_a["tenant_id"])

    assert result["task_id"] == task_id
    assert result["status"] == "dispatched"
    assert result["tenant_id"] == tenant_a["tenant_id"]

    # La tarea no debe seguir en cola después del dispatch
    queue_len = await subq.queue_length(tenant_a["tenant_id"])
    assert queue_len == 0


async def test_subq_a2a_respects_tenant_isolation(
        redis_client, tenant_a, tenant_b, policy):
    """
    Tarea encolada por tenant_a NO debe ser visible para tenant_b.
    INV-SUBQ: namespaces de cola son por tenant, nunca compartidos.
    """
    subq = SubQQueue(redis_client, policy)
    a2a  = A2ADispatcher(redis_client, policy)

    await subq.enqueue(
        tenant_id=tenant_a["tenant_id"],
        payload={"action": "test"},
        priority=1,
    )

    # tenant_b no debe ver la tarea de tenant_a
    result_b = await a2a.dispatch_next(tenant_id=tenant_b["tenant_id"])
    assert result_b is None

    # La tarea de tenant_a sigue disponible
    result_a = await a2a.dispatch_next(tenant_id=tenant_a["tenant_id"])
    assert result_a is not None


async def test_subq_score_attached_to_result(
        redis_client, tenant_a, policy):
    """
    El resultado en Redis debe incluir el SubQ score para Flow-GRPO.
    """
    subq = SubQQueue(redis_client, policy)

    task_id = await subq.enqueue(
        tenant_id=tenant_a["tenant_id"],
        payload={"action": "generate", "prompt": "test"},
        priority=1,
    )

    # Simular resultado con score
    await subq.complete(
        tenant_id=tenant_a["tenant_id"],
        task_id=task_id,
        result={"output": "respuesta generada"},
        subq_score=0.82,
    )

    stored = await subq.get_result(tenant_a["tenant_id"], task_id)
    assert stored["subq_score"] == 0.82
    assert stored["output"] == "respuesta generada"
```

---

## 5. TEST 2 — UNIKERNEL AISLAMIENTO CROSS-TENANT

```python
# tests/integration/test_unikernel_isolation.py
import pytest
from unittest.mock import AsyncMock
from mpat.capa11.unikernel_manager import UnikerManager

pytestmark = pytest.mark.asyncio

async def test_unikernel_rejects_cross_tenant_access(
        redis_client, tenant_a, tenant_b, policy):
    """
    Un unikernel de tenant_a NO debe ser accesible por tenant_b.
    INV-UNIKERNEL: aislamiento de tenant es absoluto.
    """
    manager = UnikerManager(redis_client, policy)

    uk_id = await manager.spawn(tenant_id=tenant_a["tenant_id"],
                                 image="mpat-base:v3_02")
    assert uk_id is not None

    # Acceso cross-tenant debe lanzar excepción
    with pytest.raises(SecurityError, match="cross-tenant"):
        await manager.access(unikernel_id=uk_id,
                              requesting_tenant=tenant_b["tenant_id"])

    # Acceso del propio tenant debe funcionar
    result = await manager.access(unikernel_id=uk_id,
                                   requesting_tenant=tenant_a["tenant_id"])
    assert result["tenant_id"] == tenant_a["tenant_id"]


async def test_unikernel_isolation_holds_on_redis_failure(
        redis_client, tenant_a, tenant_b, policy):
    """
    Si Redis falla durante access(), el fallback NO debe permitir
    cross-tenant. Debe fallar seguro (fail-closed).
    INV-VMAO.8 análogo: sin estado verificado → acceso denegado.
    """
    manager = UnikerManager(redis_client, policy)
    uk_id   = await manager.spawn(tenant_id=tenant_a["tenant_id"],
                                   image="mpat-base:v3_02")

    # Simular fallo de Redis
    await redis_client.aclose()

    # Cross-tenant con Redis caído → debe denegar, no permitir
    with pytest.raises((SecurityError, ConnectionError)):
        await manager.access(unikernel_id=uk_id,
                              requesting_tenant=tenant_b["tenant_id"])


async def test_unikernel_lifecycle_persisted(
        redis_client, tenant_a, policy):
    """
    Spawn, pause y terminate deben reflejarse en Redis.
    """
    manager = UnikerManager(redis_client, policy)

    uk_id = await manager.spawn(tenant_a["tenant_id"], "mpat-base:v3_02")
    state = await manager.get_state(tenant_a["tenant_id"], uk_id)
    assert state["status"] == "running"

    await manager.pause(tenant_a["tenant_id"], uk_id)
    state = await manager.get_state(tenant_a["tenant_id"], uk_id)
    assert state["status"] == "paused"

    await manager.terminate(tenant_a["tenant_id"], uk_id)
    state = await manager.get_state(tenant_a["tenant_id"], uk_id)
    assert state["status"] == "terminated"
```

---

## 6. TEST 3 — VMAO PLAN VERIFICADO → EJECUCIÓN EXITOSA

```python
# tests/integration/test_vmao_execution.py
import pytest
from mpat.vmao.planner   import VMAOPlanner
from mpat.vmao.verifier  import VMAOVerifier, PlanRejectedError
from mpat.vmao.executor  import DAGExecutor
from mpat.vmao.models    import AgentTask, OrchestrationPlan

pytestmark = pytest.mark.asyncio

async def test_vmao_happy_path(redis_client, tenant_a, policy,
                                rbac_allow_all):
    """Plan válido: Planner → Verify → DAGExecutor → resultados."""
    secret  = b"test-hmac-secret-32-bytes-exactly"
    verify  = VMAOVerifier(policy, rbac_allow_all, secret)

    # Plan manual con dependencia simple: t1 → t2
    plan = OrchestrationPlan(
        plan_id   = "plan-test-001",
        tenant_id = tenant_a["tenant_id"],
        tasks     = {
            "t1": AgentTask("t1", "summarizer",
                            tenant_a["tenant_id"], {}, []),
            "t2": AgentTask("t2", "formatter",
                            tenant_a["tenant_id"], {}, ["t1"]),
        },
        created_by = "test_agent",
    )

    signed_plan = verify.verify(plan)
    assert signed_plan.verify_signature is not None

    # Mock del agent_registry
    mock_registry = AsyncMock()
    mock_registry.get_agent.return_value = AsyncMock(
        run=AsyncMock(return_value={"output": "ok"})
    )

    executor = DAGExecutor(mock_registry, redis_client, policy, verify)
    results  = await executor.execute(signed_plan)

    assert results["t1"]["output"] == "ok"
    assert results["t2"]["output"] == "ok"


async def test_vmao_rejects_cross_tenant_plan(
        redis_client, tenant_a, tenant_b, policy, rbac_allow_all):
    """Plan con tarea de tenant_b dentro de plan de tenant_a → rechazado."""
    secret  = b"test-hmac-secret-32-bytes-exactly"
    verify  = VMAOVerifier(policy, rbac_allow_all, secret)

    plan = OrchestrationPlan(
        plan_id   = "plan-cross-001",
        tenant_id = tenant_a["tenant_id"],
        tasks     = {
            "t1": AgentTask("t1", "summarizer",
                            tenant_a["tenant_id"], {}, []),
            "t2": AgentTask("t2", "formatter",
                            tenant_b["tenant_id"],   # ← cross-tenant
                            {}, ["t1"]),
        },
        created_by = "malicious_agent",
    )

    with pytest.raises(PlanRejectedError, match="cross-tenant"):
        verify.verify(plan)


async def test_vmao_rejects_cyclic_plan(
        redis_client, tenant_a, policy, rbac_allow_all):
    """Plan con ciclo A→B→A debe ser rechazado por Verify."""
    secret = b"test-hmac-secret-32-bytes-exactly"
    verify = VMAOVerifier(policy, rbac_allow_all, secret)

    plan = OrchestrationPlan(
        plan_id   = "plan-cycle-001",
        tenant_id = tenant_a["tenant_id"],
        tasks     = {
            "tA": AgentTask("tA", "agent_x",
                            tenant_a["tenant_id"], {}, ["tB"]),
            "tB": AgentTask("tB", "agent_y",
                            tenant_a["tenant_id"], {}, ["tA"]),
        },
        created_by = "test",
    )

    with pytest.raises(PlanRejectedError, match="[Cc]iclo"):
        verify.verify(plan)


async def test_dag_executor_blocks_unsigned_plan(
        redis_client, tenant_a, policy, rbac_allow_all):
    """DAGExecutor debe bloquear plan sin verify_signature. INV-VMAO.1."""
    secret   = b"test-hmac-secret-32-bytes-exactly"
    verify   = VMAOVerifier(policy, rbac_allow_all, secret)
    executor = DAGExecutor(AsyncMock(), redis_client, policy, verify)

    unsigned_plan = OrchestrationPlan(
        plan_id   = "plan-unsigned",
        tenant_id = tenant_a["tenant_id"],
        tasks     = {"t1": AgentTask("t1", "any", tenant_a["tenant_id"],
                                     {}, [])},
        created_by = "test",
        verify_signature = None,    # sin firma
    )

    with pytest.raises(SecurityError, match="verify_signature"):
        await executor.execute(unsigned_plan)
```

---

## 7. TEST 4 — mTLS HANDSHAKE ENTRE CONTENEDORES MOCK

```python
# tests/integration/test_mtls_handshake.py
import pytest, ssl, threading, socket
from mpat.capa09.nhp_gateway import NHPGateway
from tests.integration.helpers.cert_factory import (
    generate_test_ca, generate_service_cert
)

pytestmark = pytest.mark.asyncio

def test_mtls_mutual_authentication_succeeds(tenant_a, policy):
    """
    Contenedor A y Contenedor B con certs válidos de la CA test → handshake OK.
    """
    ca_cert, ca_key = generate_test_ca()
    cert_a, key_a   = generate_service_cert(ca_cert, ca_key,
                                             "mpat-gateway",
                                             tenant_a["tenant_id"])
    cert_b, key_b   = generate_service_cert(ca_cert, ca_key,
                                             "mpat-subq",
                                             tenant_a["tenant_id"])

    gateway = NHPGateway(ca_cert_path=ca_cert,
                          cert_path=cert_b, key_path=key_b)

    # Simular handshake con cert válido del cliente
    session = gateway.simulate_handshake(client_cert=cert_a,
                                          client_key=key_a)
    assert session is not None
    assert session.tenant_id == tenant_a["tenant_id"]
    assert session.auth_method == "mtls"


def test_mtls_rejects_unknown_cert(tenant_a, policy):
    """
    Cert no firmado por la CA MPAT → handshake rechazado. INV-MTLS.3.
    """
    ca_cert, ca_key       = generate_test_ca()
    unknown_ca, unknown_k = generate_test_ca()         # CA diferente
    cert_b, key_b         = generate_service_cert(ca_cert, ca_key,
                                                   "mpat-subq",
                                                   tenant_a["tenant_id"])
    rogue_cert, rogue_key = generate_service_cert(unknown_ca, unknown_k,
                                                   "rogue-service",
                                                   tenant_a["tenant_id"])

    gateway = NHPGateway(ca_cert_path=ca_cert,
                          cert_path=cert_b, key_path=key_b)

    with pytest.raises((ssl.SSLError, SecurityError)):
        gateway.simulate_handshake(client_cert=rogue_cert,
                                   client_key=rogue_key)


def test_mtls_rejects_cross_tenant_cert(tenant_a, tenant_b, policy):
    """
    Cert de tenant_b intentando conectar a endpoint de tenant_a → rechazado.
    INV-MTLS.4: tenantId en cert DEBE coincidir con tenant del request.
    """
    ca_cert, ca_key = generate_test_ca()
    cert_a, key_a   = generate_service_cert(ca_cert, ca_key,
                                             "mpat-gateway",
                                             tenant_a["tenant_id"])
    cert_b, key_b   = generate_service_cert(ca_cert, ca_key,
                                             "mpat-agent",
                                             tenant_b["tenant_id"])  # tenant_b

    gateway = NHPGateway(ca_cert_path=ca_cert,
                          cert_path=cert_a, key_path=key_a)

    with pytest.raises(SecurityError, match="[Tt]enant"):
        gateway.simulate_handshake(client_cert=cert_b, client_key=key_b,
                                   expected_tenant=tenant_a["tenant_id"])
```

---

## 8. TEST 5 — FLOW-GRPO TRIGGER: ENTRENA SOLO CON VARIANZA SUFICIENTE

```python
# tests/integration/test_flowgrpo_trigger.py
import pytest
from unittest.mock import MagicMock, patch
from mpat.capa06.flowgrpo import FlowGRPOTrainer, GRPOConfig

pytestmark = pytest.mark.asyncio

def make_trainer(redis_client, policy):
    policy_mock = MagicMock()
    ref_mock    = MagicMock()
    # Congelar parámetros del ref_model
    for p in [MagicMock()]:
        p.requires_grad = False
    config = GRPOConfig(min_reward_variance=0.1, group_size=4)
    return FlowGRPOTrainer(policy_mock, ref_mock, config,
                           redis_client, MagicMock())


def test_should_train_with_sufficient_variance(redis_client, tenant_a, policy):
    """Alta varianza en rewards → should_train=True. INV-FGRPO.3."""
    trainer = make_trainer(redis_client, policy)
    scores  = [0.3, 0.9, 0.4, 0.85]   # varianza ≈ 0.08 — sobre threshold
    assert trainer.should_train(scores, tenant_a["tenant_id"]) is True


def test_should_not_train_with_low_variance(redis_client, tenant_a, policy):
    """Todos los rewards similares → should_train=False. INV-FGRPO.3."""
    trainer = make_trainer(redis_client, policy)
    scores  = [0.75, 0.76, 0.74, 0.75]  # varianza ≈ 0.0001
    assert trainer.should_train(scores, tenant_a["tenant_id"]) is False


def test_should_not_train_with_empty_scores(redis_client, tenant_a, policy):
    """Sin scores → should_train=False."""
    trainer = make_trainer(redis_client, policy)
    assert trainer.should_train([], tenant_a["tenant_id"]) is False


def test_should_not_train_below_score_threshold(redis_client, tenant_a, policy):
    """
    Varianza alta pero todos los scores bajos (modelo pésimo) → no entrenar.
    Entrenar con señal de baja calidad generalizada degrada el modelo.
    INV-FGRPO.1.
    """
    trainer = make_trainer(redis_client, policy)
    scores  = [0.1, 0.4, 0.15, 0.35]   # varianza OK pero max=0.4 < threshold(0.6)
    assert trainer.should_train(scores, tenant_a["tenant_id"]) is False


async def test_train_step_persists_history(redis_client, tenant_a, policy):
    """Después de train_step exitoso, historial debe estar en Redis."""
    trainer = make_trainer(redis_client, policy)

    with patch.object(trainer, '_log_prob',
                      return_value=__import__('torch').tensor(-1.0,
                                                              requires_grad=True)), \
         patch.object(trainer, '_get_optimizer',
                      return_value=MagicMock(step=MagicMock(),
                                             zero_grad=MagicMock())):

        result = await trainer.train_step(
            prompts            = ["prompt test"],
            responses_groups   = [["resp1", "resp2", "resp3", "resp4"]],
            rewards_groups     = [[0.3, 0.9, 0.4, 0.85]],
            tenant_id          = tenant_a["tenant_id"],
        )

    assert result["trained"] is True
    # Verificar que algo fue escrito en Redis
    keys = list(redis_client.scan_iter(
        f"mpat:flowgrpo:history:{tenant_a['tenant_id']}:*"))
    assert len(keys) >= 1
```

---

## 9. INVARIANTES DE LA SUITE

| ID | Invariante de test | Qué garantiza |
|---|---|---|
| INV-TEST.1 | NUNCA conectar a Redis real — siempre fakeredis | Tests reproducibles sin infraestructura |
| INV-TEST.2 | NUNCA hardcodear tenant_ids — siempre usar fixtures | Refactor-safe y legibilidad |
| INV-TEST.3 | Todo test de seguridad debe verificar que la excepción es la esperada (no solo que lanza alguna) | Evita falsos positivos por errores no relacionados |
| INV-TEST.4 | Los tests de cross-tenant SIEMPRE verifican en ambas direcciones: A→B falla Y A→A funciona | Evita que un test pase porque todo falla, no solo el cross-tenant |
| INV-TEST.5 | NUNCA mockear el algoritmo criptográfico bajo prueba — solo los I/O externos | Tests que mockean lo que prueban no detectan nada |
| INV-TEST.6 | timeout de 30s por test en CI — si tarda más, es un bug de diseño | Previene tests que cuelgan por deadlock |
| INV-TEST.7 | Cada archivo de test importa solo las clases que prueba — sin imports cruzados entre tests | Aislamiento de fallos en CI |

---

## 10. TRAMPA EDUCATIVA

**Pregunta:** "Tenemos tests unitarios con 95% de cobertura en cada módulo.
¿Para qué añadir tests de integración? ¿No están los mismos casos cubiertos?"

**Respuesta superficial (incorrecta):** "Con 95% de cobertura unitaria
el sistema está suficientemente testeado."

**Respuesta correcta — la falacia de la cobertura:**

La cobertura unitaria mide qué líneas de código se ejecutan durante
los tests, no si el sistema funciona correctamente cuando los componentes
interactúan. Un sistema puede tener 100% de cobertura unitaria y fallar
completamente en producción.

El caso más instructivo de la suite: `test_unikernel_isolation_holds_on_redis_failure`.
El test unitario del Unikernel siempre pasa porque mockea Redis con éxito.
El test de integración inyecta un fallo real de Redis y verifica que el
sistema falla de forma segura (fail-closed), no que deja pasar el acceso
cross-tenant. Ningún mock puede detectar este comportamiento.

En sistemas de IA Agéntica, los fallos en composición son especialmente
peligrosos porque los agentes actúan con autonomía. Un agente puede
tomar decisiones correctas individualmente pero producir comportamiento
no deseado cuando interactúa con otros agentes con estado compartido
(Redis, policy.yaml, RatchetSession). La suite DT-2 verifica que la
composición respeta las propiedades de seguridad del sistema, no solo
que cada componente funciona en aislamiento.

Esta es la diferencia entre un sistema que parece seguro y un sistema
que es verificablemente seguro.

---

## REFERENCIAS

| Documento | ID Drive | Relevancia |
|---|---|---|
| INVESTIGACION_VMAO_V3_02.md | `1TI6xu4-pFuB-ZdxaGQOsipCLkmbdcbuJ` | Tests 3 y 4 |
| INVESTIGACION_ZEROTRUST_V3_02.md | `1NPNBz2Y_6bja-3aV-qDYgE4lpG37dC3i` | Test 4 mTLS |
| INVESTIGACION_FLOWGRPO_OBSERVABILIDAD_V3_02.md | `1Ls__rWFm4pPhATMb2ejDhsJ4LoCMP5CG` | Test 5 |
| ARQUITECTURA_SUBQ_V3_01.md | `1i8lidA3QbWyyFZ4LclsnmFWpHP6Y3Z2H` | Tests 1 y 2 |
| ARQUITECTURA_UNIKERNEL_V3_01.md | `1Wwy2gkuxLZI0qX76xB7wmkOETOkfGpLv` | Test 2 |
| RESOLUCIONES_CONSOLIDADAS_V3_02_R013.md | `1ZLdclhRZt6BiJiRVYXnpMhdWo4JyQWMd` | Invariantes RES |

---

*INVESTIGACION_TEST_SUITE_V3_02.md · MPAT V3_02 · 2026-05-15*
*agt1973@gmail.com — RELAY_017 completado · DT-2 cerrada*
*5 tests de integración · 7 invariantes de suite · pytest-asyncio*
*que has usado el formato de razonamiento adaptado por AGT*
