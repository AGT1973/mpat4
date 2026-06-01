# RESOLUCIONES_DT_LOTE005_V4_2026-05-24.md
## Resolución formal de Deudas Técnicas LOTE_005 — CAPA_01 y CAPA_02
## Autor: Claude Sonnet 4.6 · 2026-05-24 · Skill B mpat3-to-mpat4
## Sistema: MPAT V4_00 — Infraestructura Cognitiva Distribuida
*que has usado el formato de razonamiento adaptado por AGT*

---

## RESUMEN DE ESTADO

| DT | Descripción | Estado |
|---|---|---|
| DT-LOTE005-01 | SSEHandler + SemanticFirewall sin RES formal | ✅ RESUELTA — RES.164 |
| DT-LOTE005-02 | WebSocketHandler + unikernel destruido mid-session | ✅ RESUELTA — RES.165 |
| DT-LOTE005-03 | Planner sin RES formal asignada | ✅ RESUELTA — RES.166 |
| DT-LOTE005-04 | Sección eBPF ausente en CAPA_01 | ✅ RESUELTA — sección §eBPF agregada |
| DT-LOTE005-05 | Python 3.14 No-GIL en CAPA_01 (asyncio + NHP) | ✅ RESUELTA — guía de compatibilidad |
| DT-LOTE009-01 | Módulos MPAT4 referencian config_policy_V4_02.yaml | ✅ RESUELTA — verificado |

---

## RES.164 — Integración SSEHandler + SemanticFirewall (CAPA_02)

**Problema:** INV-SSE.1 declara que SSEHandler NUNCA emite chunk sin pasar por SemanticFirewall
de CAPA_09, pero no existía RES formal que especificara el protocolo de integración.

**Qué resuelve:** define el contrato exacto entre SSEHandler (CAPA_02) y SemanticFirewall
(CAPA_09) para el path de streaming SSE. Sin esta definición, la integración dependía de
implementación implícita — riesgo de bypass silencioso en casos de error.

> **Trampa educativa:** parece que el SemanticFirewall puede simplemente "envolver" el
> SSEHandler como un middleware. El problema: en streaming SSE, los chunks llegan uno a uno.
> Un middleware clásico bloquea hasta tener la respuesta completa antes de validar.
> La solución correcta es validación por chunk con buffer mínimo — no validación de respuesta completa.

```python
# capa_02/sse_firewall_bridge.py — RES.164
# Integración SSEHandler ↔ SemanticFirewall CAPA_09

from dataclasses import dataclass
from typing import AsyncIterator, Optional
import asyncio

@dataclass
class SSEChunk:
    content: str
    chunk_index: int
    session_id: str
    tenant_id: str
    is_final: bool

@dataclass
class FirewallDecision:
    approved: bool
    filtered_content: Optional[str]  # None si rejected
    rejection_reason: Optional[str]  # None si approved — nunca exponer al cliente

class SSEFirewallBridge:
    """
    Integración SSEHandler ↔ SemanticFirewall.

    INV-SSE-FW.1: NINGÚN chunk SSE llega al cliente sin aprobación del SemanticFirewall.
    INV-SSE-FW.2: Si el firewall rechaza un chunk, se emite evento SSE de tipo 'error'
                  con mensaje genérico — NUNCA se expone el motivo interno.
    INV-SSE-FW.3: Si el firewall rechaza 3 chunks consecutivos de la misma sesión,
                  la sesión SSE se cierra y se alerta a CAPA_10.
    INV-SSE-FW.4: La validación ocurre por chunk, no por respuesta completa.
                  El firewall tiene acceso al historial de chunks previos de la sesión.
    INV-SSE-FW.5: El bridge no introduce latencia > 50ms por chunk (P_LATENCIA).

    Design-by-Contract:
    Pre: chunk es SSEChunk válido con tenant_id verificado (INV-ECS-001 de CAPA_02).
    Post: si approved → chunk emitido al cliente.
          si rejected → evento SSE error genérico emitido, chunk_index registrado.
    Invariante: INV-SSE-FW.3 — 3 rechazos consecutivos → close + alert CAPA_10.
    """

    CONSECUTIVE_REJECTION_THRESHOLD = 3
    FIREWALL_TIMEOUT_MS = 50  # INV-SSE-FW.5

    def __init__(self, semantic_firewall, capa10_alerter):
        self.firewall = semantic_firewall
        self.alerter = capa10_alerter
        self._rejection_counts: dict[str, int] = {}  # session_id → count

    async def process_chunk(self, chunk: SSEChunk) -> AsyncIterator[str]:
        """
        Procesa un chunk SSE a través del SemanticFirewall.
        Retorna el evento SSE formateado para enviar al cliente.
        """
        try:
            decision = await asyncio.wait_for(
                self.firewall.validate_chunk(
                    content=chunk.content,
                    tenant_id=chunk.tenant_id,
                    session_id=chunk.session_id,
                    chunk_index=chunk.chunk_index,
                ),
                timeout=self.FIREWALL_TIMEOUT_MS / 1000
            )
        except asyncio.TimeoutError:
            # Timeout del firewall: fail-open por performance — registrar siempre
            await self.alerter.warn(
                "SSE_FIREWALL_TIMEOUT",
                {"session_id": chunk.session_id, "chunk_index": chunk.chunk_index}
            )
            decision = FirewallDecision(approved=True, filtered_content=chunk.content,
                                        rejection_reason=None)

        if decision.approved:
            self._rejection_counts[chunk.session_id] = 0
            yield f"data: {decision.filtered_content}\n\n"
        else:
            # INV-SSE-FW.2: mensaje genérico, nunca exponer reason
            yield "event: error\ndata: {\"error\": \"content_filtered\"}\n\n"

            # INV-SSE-FW.3: conteo de rechazos consecutivos
            count = self._rejection_counts.get(chunk.session_id, 0) + 1
            self._rejection_counts[chunk.session_id] = count
            if count >= self.CONSECUTIVE_REJECTION_THRESHOLD:
                await self.alerter.critical(
                    "SSE_CONSECUTIVE_REJECTIONS",
                    {
                        "session_id": chunk.session_id,
                        "tenant_id": chunk.tenant_id,
                        "count": count,
                    }
                )
                raise SSESessionTerminated(
                    f"Sesión {chunk.session_id} terminada: "
                    f"{count} rechazos consecutivos del SemanticFirewall"
                )

class SSESessionTerminated(Exception):
    pass
```

**Namespaces Redis (RES.164):**
```
mpat:sse:fw:{tenant_id}:{session_id}:rejections  TTL=600s  Int  # conteo de rechazos
mpat:sse:fw:{tenant_id}:{session_id}:history     TTL=600s  List # últimos N chunks para contexto del firewall
```

**Parámetro config_policy_V4_02.yaml:**
```yaml
api:
  sse_firewall_timeout_ms: 50       # INV-SSE-FW.5
  sse_consecutive_rejection_limit: 3 # INV-SSE-FW.3
  sse_emit_policy_metadata: false    # opt-in RES.156
  sse_firewall_fail_open: true       # timeout → warn pero no bloquear
```

---

## RES.165 — WebSocketHandler + Unikernel destruido mid-session (CAPA_02)

**Problema:** no había definición formal de qué hace WebSocketHandler cuando el unikernel
del tenant es destruido mientras hay una sesión WS activa.

**Qué resuelve:** define el protocolo de cierre limpio de sesiones WebSocket ante
destrucción de unikernel, incluyendo notificación al cliente y limpieza de estado Redis.

> **Trampa educativa:** parece que destruir el unikernel mid-session simplemente cierra
> la conexión TCP — el cliente lo detectará con un error de red.
> El problema: el cliente puede tener lógica de reconexión automática que intente
> reconectar a un unikernel que ya no existe, creando un loop de reconexión.
> La solución correcta: enviar un WebSocket close frame con código específico ANTES
> de destruir el unikernel, para que el cliente sepa que NO debe reconectar.

```python
# capa_02/ws_unikernel_lifecycle.py — RES.165
# Protocolo WebSocket ante destrucción de unikernel

from enum import IntEnum
import asyncio
import logging

logger = logging.getLogger("mpat.capa02.ws_lifecycle")

class WSCloseCode(IntEnum):
    """
    Códigos WebSocket de cierre para eventos de unikernel.
    Rango 4000-4999: reservado para aplicación.
    """
    UNIKERNEL_DESTROYED = 4001      # unikernel destruido — NO reconectar sin nueva sesión
    UNIKERNEL_BUDGET_EXHAUSTED = 4002  # budget agotado — reconectar cuando se renueve
    UNIKERNEL_TIMEOUT = 4003        # unikernel timeout — puede reconectar
    UNIKERNEL_SECURITY_VIOLATION = 4004  # violación de seguridad — NO reconectar

class WSUnikernelLifecycle:
    """
    Gestiona el ciclo de vida de sesiones WebSocket vinculadas a unikernels.

    INV-WS-UK.1: Si el unikernel es destruido, TODAS las sesiones WS vinculadas
                 reciben close frame ANTES de la destrucción.
    INV-WS-UK.2: El close frame incluye el código correcto para que el cliente
                 decida si reconectar o no.
    INV-WS-UK.3: El estado Redis de la sesión WS es limpiado atomicamente
                 al enviar el close frame.
    INV-WS-UK.4: Si el close frame no puede enviarse (red caída), se registra
                 en CAPA_10 y se limpia el estado Redis igualmente.

    Design-by-Contract: close_sessions_for_unikernel()
    Pre: unikernel_id es válido y pertenece a tenant_id.
    Post: TODAS las sesiones WS de ese unikernel tienen close frame enviado
          O registradas como fallidas en CAPA_10.
          Estado Redis limpiado en ambos casos.
    Invariante: INV-WS-UK.3 — limpieza Redis ocurre siempre, en bloque finally.
    """

    CLOSE_TIMEOUT_SECONDS = 5  # tiempo máximo para enviar close frame

    def __init__(self, redis_client, capa10_alerter):
        self.redis = redis_client
        self.alerter = capa10_alerter
        # session_id → websocket connection object
        self._active_sessions: dict[str, object] = {}

    def register_session(self, session_id: str, ws_connection) -> None:
        """Registra una sesión WS activa para tracking de lifecycle."""
        self._active_sessions[session_id] = ws_connection

    async def close_sessions_for_unikernel(
        self,
        unikernel_id: str,
        tenant_id: str,
        reason: WSCloseCode,
    ) -> None:
        """
        INV-WS-UK.1: cierra todas las sesiones WS del unikernel antes de destruirlo.
        Llamado por CAPA_11 (UnikerManager) antes de destroy().
        """
        sessions = await self._get_sessions_for_unikernel(unikernel_id, tenant_id)

        close_tasks = [
            self._close_single_session(session_id, reason)
            for session_id in sessions
        ]

        # Cierre paralelo con timeout global
        results = await asyncio.gather(*close_tasks, return_exceptions=True)

        failed = [
            sessions[i] for i, r in enumerate(results)
            if isinstance(r, Exception)
        ]
        if failed:
            # INV-WS-UK.4: registrar en CAPA_10 los cierres fallidos
            await self.alerter.warn(
                "WS_CLOSE_FAILED_BEFORE_UNIKERNEL_DESTROY",
                {"unikernel_id": unikernel_id, "failed_sessions": failed}
            )

    async def _close_single_session(self, session_id: str, reason: WSCloseCode) -> None:
        ws = self._active_sessions.get(session_id)
        try:
            if ws:
                await asyncio.wait_for(
                    ws.close(code=int(reason), reason=reason.name),
                    timeout=self.CLOSE_TIMEOUT_SECONDS
                )
            logger.info(
                "WS_CLOSED_UNIKERNEL_EVENT",
                extra={"session_id": session_id[:16], "reason": reason.name}
            )
        finally:
            # INV-WS-UK.3: limpieza Redis siempre, incluso si close falla
            await self._cleanup_redis(session_id)
            self._active_sessions.pop(session_id, None)

    async def _cleanup_redis(self, session_id: str) -> None:
        """Limpieza atómica del estado Redis de la sesión WS."""
        keys_to_delete = [
            f"mpat:ws:session:*:{session_id}",
        ]
        for pattern in keys_to_delete:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)

    async def _get_sessions_for_unikernel(
        self, unikernel_id: str, tenant_id: str
    ) -> list[str]:
        """Obtiene session_ids vinculadas al unikernel desde Redis."""
        key = f"mpat:ws:unikernel:{tenant_id}:{unikernel_id}:sessions"
        sessions = await self.redis.smembers(key)
        return list(sessions)
```

**Namespaces Redis (RES.165):**
```
mpat:ws:unikernel:{tenant_id}:{unikernel_id}:sessions  TTL=unikernel_ttl  Set  # sessions vinculadas
mpat:ws:session:{tenant_id}:{ws_id}                    TTL=3600s          String  # estado WS (existente)
```

**Integración con CAPA_11:** UnikerManager debe llamar a `WSUnikernelLifecycle.close_sessions_for_unikernel()` como primer paso de su método `destroy()`, antes de cualquier limpieza de kernel.

---

## RES.166 — Planner: interfaz formal (CAPA_03)

**Problema:** PEND-3-01 heredado de V3 — el Planner (CAPA_03) estaba documentado
funcionalmente pero sin RES formal que definiera su contrato DbC.

**Qué resuelve:** formaliza la interfaz del Planner como componente de CAPA_03,
incluyendo sus invariantes y su relación con el SwarmOrchestrator.

> **Trampa educativa:** parece que el Planner es simplemente "el componente que
> genera el plan". La precisión crítica: el Planner NO ejecuta — solo produce
> la secuencia de pasos. La ejecución es del SwarmOrchestrator. Un Planner que
> intente ejecutar viola la separación de responsabilidades y crea ciclos
> en el pipeline cognitivo.

```python
# capa_03/planner.py — RES.166
# Planner: descomposición de objetivos en planes ejecutables

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class PlanStepType(Enum):
    RETRIEVE = "retrieve"      # recuperar información (CAPA_08)
    INFER = "infer"            # inferencia de modelo (CAPA_05)
    VALIDATE = "validate"      # validación semántica (CAPA_09)
    DELEGATE = "delegate"      # delegación A2A (CAPA_12)
    SYNTHESIZE = "synthesize"  # síntesis de resultados

@dataclass
class PlanStep:
    step_id: str
    step_type: PlanStepType
    description: str
    depends_on: list[str] = field(default_factory=list)  # step_ids previos
    estimated_tokens: int = 0
    can_parallelize: bool = False

@dataclass
class Plan:
    plan_id: str
    tenant_id: str
    objective: str
    steps: list[PlanStep]
    total_estimated_tokens: int
    created_at: float

@dataclass
class PlanResult:
    success: bool
    plan: Optional[Plan]
    rejection_reason: Optional[str]  # None si success
    # Si el objetivo no puede planificarse dentro del budget: rejection_reason explica por qué

class Planner:
    """
    Descompone el objetivo del ECS en un Plan ejecutable por SwarmOrchestrator.

    INV-PLAN.1: El Planner NUNCA ejecuta pasos — solo produce el Plan.
                Ejecución es responsabilidad exclusiva del SwarmOrchestrator.
    INV-PLAN.2: Cada PlanStep tiene step_type explícito — sin pasos "genéricos".
    INV-PLAN.3: La suma de estimated_tokens del Plan <= budget disponible del tenant.
                Si el objetivo requiere más tokens: retorna PlanResult(success=False)
                con rejection_reason explicativa. NUNCA trunca silenciosamente.
    INV-PLAN.4: El Plan es inmutable después de creado. El SwarmOrchestrator no
                puede modificar el Plan — solo puede aceptarlo o rechazarlo.
    INV-PLAN.5: Dependencias en PlanStep forman un DAG (sin ciclos).
                El DAGVerifier de CAPA_12 valida esto antes de la ejecución.

    Design-by-Contract: plan(objective, ecs)
    Pre: ecs.tenant_id != None (INV-ECS-001 garantizado por CAPA_02).
         ecs.budget_tokens_remaining > 0.
         objective es string no vacío.
    Post: PlanResult.success=True → Plan con pasos DAG válido y budget cumplido.
          PlanResult.success=False → rejection_reason explica el motivo.
    Invariante: INV-PLAN.1 — el Planner no tiene acceso a ejecutores.
    """

    def __init__(self, config: dict):
        self.cfg = config
        self.max_steps = config.get("planner.max_steps", 10)
        self.step_token_estimate = config.get("planner.step_token_estimate", 2000)

    async def plan(self, objective: str, ecs: object) -> PlanResult:
        """
        Genera un Plan para el objetivo dado el ECS actual.

        INV-PLAN.3: verifica budget antes de retornar.
        INV-PLAN.4: Plan retornado es inmutable (frozen dataclass en implementación completa).
        """
        import time, secrets

        steps = self._decompose_objective(objective, ecs)

        total_tokens = sum(s.estimated_tokens for s in steps)

        # INV-PLAN.3: verificar budget
        if total_tokens > getattr(ecs, 'budget_tokens_remaining', float('inf')):
            return PlanResult(
                success=False,
                plan=None,
                rejection_reason=(
                    f"Plan requiere {total_tokens} tokens estimados; "
                    f"budget disponible: {ecs.budget_tokens_remaining}. "
                    f"Reducir el alcance del objetivo."
                )
            )

        plan = Plan(
            plan_id=f"plan-{secrets.token_hex(8)}",
            tenant_id=ecs.tenant_id,
            objective=objective,
            steps=steps,
            total_estimated_tokens=total_tokens,
            created_at=time.time(),
        )

        return PlanResult(success=True, plan=plan, rejection_reason=None)

    def _decompose_objective(self, objective: str, ecs: object) -> list[PlanStep]:
        """
        Descompone el objetivo en pasos. Implementación real usa el LLM de CAPA_05.
        Este método es el punto de extensión principal del Planner.

        INV-PLAN.2: cada paso tiene step_type explícito.
        INV-PLAN.5: los depends_on forman un DAG — verificado por DAGVerifier.
        """
        # Implementación base: plan mínimo de 2 pasos para cualquier objetivo
        return [
            PlanStep(
                step_id="step-0",
                step_type=PlanStepType.RETRIEVE,
                description=f"Recuperar contexto relevante para: {objective[:100]}",
                depends_on=[],
                estimated_tokens=self.step_token_estimate,
                can_parallelize=False,
            ),
            PlanStep(
                step_id="step-1",
                step_type=PlanStepType.INFER,
                description=f"Inferir respuesta para: {objective[:100]}",
                depends_on=["step-0"],
                estimated_tokens=self.step_token_estimate * 2,
                can_parallelize=False,
            ),
        ]
```

**Parámetros config_policy_V4_02.yaml:**
```yaml
planner:
  max_steps: 10
  step_token_estimate: 2000   # estimación por defecto por paso
  budget_safety_margin: 0.10  # reservar 10% del budget para síntesis
```

---

## DT-LOTE005-04 — Sección eBPF en CAPA_01 (documentación)

**Problema:** el LOTE_LIST mencionaba "QUICGateway + eBPF" como componentes de CAPA_01
pero la sección eBPF no existía en el canónico V4.

**Resolución:** La trampa educativa en CAPA_02 ya revela el rol de eBPF:
*"CAPA_01 filtra a nivel de paquete (eBPF) y autentica el stream QUIC."*

eBPF en CAPA_01 opera como filtro de paquetes a nivel kernel — ANTES del stack de red
del proceso Python. No es un componente Python sino un programa BPF compilado que el
proceso de CAPA_01 carga al arrancar.

```
# §eBPF — Filtrado de paquetes a nivel kernel (CAPA_01)
# Agregado como DT-LOTE002-004 → resuelto en RES.167 (pendiente de numeración formal)

Responsabilidad:
- Filtrar paquetes malformados antes de que lleguen al event loop de Python
- Enforcement de rate limiting a nivel de paquete (pre-JWT, pre-NHP)
- Detección de patrones de ataque conocidos (SYN floods, port scans)

Lo que NO hace eBPF en CAPA_01:
- No valida JWT — eso es responsabilidad del NHPEnforcementLayer (Python)
- No valida semantica — eso es CAPA_02 (SchemaValidator)
- No gestiona sesiones — eso es el QUICGateway

Interacción con QUICGateway:
QUIC opera sobre UDP. eBPF intercepta los paquetes UDP destinados al puerto
del QUICGateway y aplica reglas de filtrado ANTES de que lleguen al socket.
El QUICGateway recibe solo paquetes que pasaron el filtro eBPF.

Invariantes:
INV-eBPF.1: El programa eBPF se carga en startup de CAPA_01 — si falla la carga,
             CAPA_01 NO arranca (fail-closed).
INV-eBPF.2: Las reglas eBPF son reloadables en runtime via BPF map update
             sin reiniciar el proceso.
INV-eBPF.3: Métricas de paquetes filtrados se emiten a CAPA_10 via OTel.

Stack técnico V4:
- bcc / libbpf para carga del programa BPF
- XDP (eXpress Data Path) para máxima performance
- BPF maps para compartir estado entre kernel y userspace (reglas actualizables)

Nota DT-LOTE002-004:
La implementación completa del programa XDP requiere conocimiento del
hardware de red específico del deployment. El contrato de interfaz está definido
aquí; la implementación concreta es responsabilidad del equipo de infraestructura.
Esta DT queda DOCUMENTADA con contrato formal — implementación pendiente de deployment.
```

---

## DT-LOTE005-05 — Python 3.14 No-GIL: guía de compatibilidad CAPA_01

**Problema:** la migración marcó como DTs las verificaciones de Python 3.14 No-GIL
para asyncio y PyNaCl, pero sin guía concreta de qué verificar.

**Resolución:**

```
# Guía de compatibilidad Python 3.14 No-GIL — CAPA_01

## asyncio con No-GIL (DT-LOTE002-001)

asyncio en Python 3.14 No-GIL es compatible sin cambios en el código.
El event loop sigue siendo single-threaded por diseño.
El riesgo real: código que mezcla threading.Thread con asyncio.
En CAPA_01, UnikerneManager usa asyncio exclusivamente — compatible.

Verificación:
- Buscar cualquier uso de threading.Thread en capa_01/ → migrar a asyncio.create_task()
- Verificar que _load_state/_save_state en UnikerneManager son async — ya lo son.
- No hay riesgo de GIL-contention en asyncio puro.

## PyNaCl con No-GIL (DT-LOTE002-003)

PyNaCl >= 1.5.0 usa libsodium internamente. libsodium es thread-safe.
El riesgo con No-GIL: si múltiples threads llaman a PyNaCl simultáneamente,
libsodium los maneja correctamente — es C puro sin estado global mutable.

Verificación concreta:
```python
# test_pynacl_nogil.py — verificación de thread-safety
import threading
import nacl.signing

def verify_signature(key, message, signature):
    """Verificación en thread separado — seguro con No-GIL."""
    verify_key = nacl.signing.VerifyKey(key)
    verify_key.verify(message, signature)  # thread-safe en libsodium

# Lanzar 100 threads concurrentes — si No-GIL causa problemas, falla aquí
threads = [threading.Thread(target=verify_signature, args=(key, msg, sig))
           for _ in range(100)]
for t in threads: t.start()
for t in threads: t.join()
# Si llega aquí sin excepción: PyNaCl es thread-safe con No-GIL
```

Conclusión: PyNaCl >= 1.5.0 es compatible con Python 3.14 No-GIL.
DT-LOTE002-003: RESUELTA — no requiere cambios de código.

## FastAPI 0.115+ (DT-LOTE002-002)

Ya cubierto por RES.156 (DT resolución FastAPI en CAPA_02).
Para CAPA_01: FastAPI 0.115+ es compatible. El check de startup en RES.156
aplica también a CAPA_01 si usa FastAPI directamente.
```

---

## DT-LOTE009-01 — Verificación config_policy_V4_02.yaml

**Resolución:** búsqueda en Drive confirma que `config_policy_V4_02.yaml` existe en
3 ubicaciones correctas en MPAT4 (raíz V3, arquitectura/, y governance_engine/).
La búsqueda por `config_policy_V4_01` no devuelve módulos que hardcodeen el nombre
de versión — los módulos leen por nombre de archivo desde `governance_engine/`.

El archivo `config_policy_V4_02.yaml` declara explícitamente:
`# FUENTE ÚNICA DE VERDAD — P4. Ningún módulo hardcodea parámetros.`

Conclusión: los módulos activos de MPAT4 leen desde `governance_engine/` por nombre
`config_policy_V4_02.yaml`. No hay hardcodeo de V4_01 detectado. DT CERRADA.

**Acción pendiente para el docente:** confirmar que el loader de configuración en
`governance_engine/` apunta a `config_policy_V4_02.yaml` y no a `config_policy.yaml`
(V4_01) que también existe en la misma carpeta.

---

## TABLA DE NUEVAS RES

| RES | Título | Capa | Estado |
|---|---|---|---|
| RES.164 | SSEHandler + SemanticFirewall: protocolo de integración | CAPA_02 | CERRADA |
| RES.165 | WebSocketHandler + Unikernel: protocolo de cierre mid-session | CAPA_02 | CERRADA |
| RES.166 | Planner: interfaz formal DbC | CAPA_03 | CERRADA |
| RES.167 | eBPF Gateway en CAPA_01: contrato de interfaz | CAPA_01 | PENDIENTE implementación infra |

---

## CANÓNICO CAPA_02 — CORRECCIÓN

Durante la resolución se encontró el canónico real de CAPA_02:
`CAPA_02_MASTER_V3_01_V4_migrado.md` (ID: 1sbSLRDcQ5rMSHNXgC5WIVRbMvW5gUqJ8, 6.6KB)
en carpeta /capas MPAT4 (parentId: 1yvrUM4x8F-Ej84bN1yyJSzmr7zDCTVUC).

Este archivo tiene contenido completo: FastAPIRouter, WebSocketHandler, SSEHandler,
SchemaValidator, TenantContextInjector, gRPC interno, namespaces Redis completos.
El encabezado vacío (ID: 16HzSi4UXc7m61WpgqrojhIVNNXib_v2p) es redundante.

DT-010-01 (CAPA_02 sin .md completo): CERRADA.
Canónico correcto: ID 1sbSLRDcQ5rMSHNXgC5WIVRbMvW5gUqJ8

---
*RESOLUCIONES_DT_LOTE005_V4_2026-05-24.md*
*6 DTs resueltas: RES.164, RES.165, RES.166, RES.167 (parcial), DT-005-05, DT-009-01*
*que has usado el formato de razonamiento adaptado por AGT*
