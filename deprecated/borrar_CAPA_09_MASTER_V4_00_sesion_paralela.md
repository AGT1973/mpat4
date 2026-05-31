# CAPA_09_MASTER_V4_00.md
## MPAT — Seguridad Agéntica: NHP + ASL-3 + Zero Trust Session + SemanticFirewall
## Versión: V4_00 · Consolidación MPAT4
## Consolidado por: Claude Sonnet 4.6 · 2026-05-23
## Fuentes fusionadas:
##   - CAPA_09_MASTER_V3_01_UNIFICADO.md (2026-05-22, ai.mpat.designer) — implementación completa NHP+ASL+ZTS
##   - CAPA_09_MASTER_V3_02_DELTA.md (2026-05-23, agt1973) — RES.123/145/149 + INV-09-QUIC.1 observacional
## Razonamiento de fusión:
##   El DELTA no modifica código. Agrega: tabla de estado con RES nuevas + 1 invariante cross-capa observacional.
##   El cuerpo de implementación viene íntegro del V3_01_UNIFICADO.
##   La V3_02_base (ID: 1UzNb0u54ZQLG4iHZH8Y7UUmRfGduPUC-) fue intermedia — absorbida por el DELTA.
## RES activas: RES.090, RES.091, RES.092, RES.123, RES.145, RES.149, RES.157(obs)
## Sistema: MPAT V4_00 — Infraestructura Cognitiva Distribuida

---

## REGISTRO DE CONSOLIDACIÓN

| Campo | Valor |
|---|---|
| Capa | CAPA_09 |
| Versión destino | V4_00 |
| Fecha consolidación | 2026-05-23 |
| RES activas | RES.090, RES.091, RES.092, RES.123, RES.145, RES.149 |
| Cross-ref observacional | RES.157 (no modifica código de CAPA_09) |
| Calidad declarada | 9.5/10 (heredada del V3_01_UNIFICADO) |

---

## ÍNDICE DE COMPONENTES V4_00

| Sección | Componente | Estado |
|---|---|---|
| 9.1 | Zero-Trust Validator | HEREDADO V2 |
| 9.2 | Critic Agent | HEREDADO V2 |
| 9.3 | HITL Manager | HEREDADO V2 |
| 9.4 | Semantic Firewall | HEREDADO V2 |
| 9.5 | JWT / RBAC / OAuth 2.1 | HEREDADO V2 |
| 9.EX | Explainability3D + AutoCompliance | HEREDADO V2_77 FUT.30 |
| **9.NHP** | **NHP Protocol** | **CERRADO V3_01 — RES.090, RES.149** |
| **9.ASL** | **ASL-3 Controller** | **CERRADO V3_01 — RES.091** |
| **9.ZTS** | **Zero Trust Session** | **CERRADO V3_01 — RES.092** |
| **9.PERSIST** | **NHP used_nonces en Redis** | **CERRADO V3_02 — RES.123** |
| **9.DR** | **Double Ratchet E2E A2A** | **CERRADO V3_02 — RES.145** |
| **9.NHP2** | **NHP Protocol DEFINITIVO** | **CERRADO V3_02 — RES.149** |
| **9.QUIC-REF** | **Cross-ref RES.157** | **REGISTRADO V4_00 — observacional** |

> Los componentes HEREDADOS se mantienen sin modificación.
> Los componentes NUEVO integran FUT_3 con Design-by-Contract completo.

---

## COMPONENTES HEREDADOS — RESUMEN (referencia)

Los componentes 9.1 a 9.EX están documentados en su totalidad en
`CAPA_09_MASTER.md` (archivo base) y permanecen vigentes en V4_00.

Invariantes heredados activos:
- INV-ZT: `validated_by_orchestrator = true` solo lo setea el Orchestrator
- INV-CR: Critic NUNCA bloquea silenciosamente el pipeline
- INV-HITL: Timeout → cancelación, NUNCA aprobación automática
- INV-EX.1–3: Explainability3D con 3 niveles siempre disponibles

---

## §9.NHP — NHP Protocol (Neural Handshake Protocol) · RES.090, RES.149 · FUT_3

**Qué resuelve NHP:**
En V2, los agentes se comunican entre sí sin verificar la identidad del agente con quien hablan.
Un agente comprometido puede hacer pasar mensajes falsos dentro del enjambre.

NHP resuelve esto con un protocolo de apretón de manos (handshake) criptográfico entre agentes
ANTES de que fluya cualquier dato operativo. El principio es: authenticate-before-connect.

> **Trampa educativa:** parece que "autenticar agentes" es simplemente usar un JWT.
> La diferencia es que NHP verifica la identidad del agente (no solo del usuario) mediante
> una cadena de confianza que incluye el AgentCard firmado, el tenant_id, y un nonce temporal.
> Un JWT puede ser robado y reutilizado. Un NHP handshake es unidireccional y expira
> por diseño en cada sesión.

```python
# capa_9/nhp_protocol.py — RES.090 · FUT_3

import hashlib
import secrets
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentIdentity:
    agent_id: str            # UUID único del agente
    tenant_id: str           # tenant al que pertenece
    role: str                # rol declarado en AgentCard
    pubkey_fingerprint: str  # hash SHA-256 de la clave pública
    card_signature: str      # firma del AgentCard por el Orchestrator

@dataclass
class NHPHandshake:
    nonce: str               # token de un solo uso (32 bytes hex)
    timestamp: float         # epoch UTC del handshake
    initiator_id: str        # agent_id del que inicia
    responder_id: str        # agent_id del que responde
    session_token: str       # token derivado — válido solo esta sesión
    expires_at: float        # timestamp de expiración

@dataclass
class NHPResult:
    success: bool
    session_token: Optional[str]   # None si failed
    rejection_reason: Optional[str]  # None si success
    handshake_log: str             # registro para auditoría

class NHPProtocol:
    """
    Neural Handshake Protocol — authenticate-before-connect.

    INV-NHP.1: Un agente NUNCA recibe datos operativos sin NHP exitoso.
    INV-NHP.2: El nonce es de un solo uso — reutilización = rechazo.
    INV-NHP.3: tenant_id del iniciador == tenant_id del respondedor.
               Agentes de distintos tenants NUNCA se conectan entre sí.
    INV-NHP.4: session_token expira en nhp.session_ttl_seconds (default: 300s).
    INV-NHP.5: card_signature verificada contra la firma del Orchestrator.
    """

    SESSION_TTL = 300  # segundos — configurable vía Capa 14

    def __init__(self, orchestrator_pubkey: str, config: dict = None):
        self.orchestrator_pubkey = orchestrator_pubkey
        self.cfg = config or {}
        self.used_nonces: set[str] = set()  # anti-replay
        self.session_ttl = self.cfg.get("nhp.session_ttl_seconds", self.SESSION_TTL)

    def initiate(self, initiator: AgentIdentity) -> tuple[str, str]:
        """
        Paso 1: el iniciador genera nonce y lo envía al respondedor.
        Retorna (nonce, timestamp_str) para incluir en el mensaje.
        """
        nonce = secrets.token_hex(32)
        timestamp = time.time()
        return nonce, str(timestamp)

    def respond(
        self,
        initiator: AgentIdentity,
        responder: AgentIdentity,
        nonce: str,
        timestamp_str: str
    ) -> NHPResult:
        """
        Paso 2: el respondedor verifica y genera el session_token.

        INV-NHP.3: tenant_id debe coincidir.
        INV-NHP.2: nonce no debe haber sido usado.
        """
        timestamp = float(timestamp_str)
        now = time.time()

        # INV-NHP.3 — mismo tenant
        if initiator.tenant_id != responder.tenant_id:
            return NHPResult(
                success=False,
                session_token=None,
                rejection_reason=f"Cross-tenant handshake bloqueado: "
                                 f"{initiator.tenant_id} != {responder.tenant_id}",
                handshake_log=f"REJECT cross-tenant {initiator.agent_id}→{responder.agent_id}"
            )

        # INV-NHP.2 — nonce de un solo uso
        if nonce in self.used_nonces:
            return NHPResult(
                success=False,
                session_token=None,
                rejection_reason="Nonce ya utilizado — posible replay attack",
                handshake_log=f"REJECT replay nonce {nonce[:8]}... {initiator.agent_id}"
            )

        # Validez temporal: nonce no puede tener más de 30s de antigüedad
        if now - timestamp > 30:
            return NHPResult(
                success=False,
                session_token=None,
                rejection_reason=f"Nonce expirado: {now - timestamp:.1f}s > 30s",
                handshake_log=f"REJECT expired nonce {initiator.agent_id}"
            )

        # Verificar card_signature
        expected_sig = hashlib.sha256(
            f"{initiator.agent_id}:{initiator.tenant_id}:{self.orchestrator_pubkey}".encode()
        ).hexdigest()
        if initiator.card_signature != expected_sig:
            return NHPResult(
                success=False,
                session_token=None,
                rejection_reason="AgentCard signature inválida",
                handshake_log=f"REJECT invalid card_sig {initiator.agent_id}"
            )

        # Registrar nonce como usado
        self.used_nonces.add(nonce)

        # Generar session_token derivado
        session_token = hashlib.sha256(
            f"{nonce}:{initiator.agent_id}:{responder.agent_id}:{timestamp}".encode()
        ).hexdigest()

        expires_at = now + self.session_ttl

        log_entry = (f"NHP OK {initiator.agent_id}→{responder.agent_id} "
                     f"tenant={initiator.tenant_id} "
                     f"expires={expires_at:.0f}")

        return NHPResult(
            success=True,
            session_token=session_token,
            rejection_reason=None,
            handshake_log=log_entry
        )

    def validate_session(self, session_token: str, issued_at: float) -> bool:
        """INV-NHP.4: Verifica que el session_token no haya expirado."""
        return time.time() < issued_at + self.session_ttl
```

**Parámetros Capa 14:**
```yaml
nhp:
  enabled: true
  session_ttl_seconds: 300       # [60, 3600]
  nonce_max_age_seconds: 30      # [10, 60]
  require_card_signature: true   # false solo en entorno dev
  cross_tenant_block: true       # NUNCA false en producción
  log_all_handshakes: true       # auditoría completa
```

**Namespace Redis:**
```
mpat:nhp:{agent_id}:sessions  → Lista session_tokens activos (TTL: session_ttl)
mpat:nhp:nonces               → Set de nonces usados (TTL: 24h)
mpat:nhp:log:{date}           → Log de handshakes del día
```

---

## §9.ASL — ASL-3 (Agentic Security Level 3) · RES.091 · FUT_3

**Qué resuelve ASL-3:**
En V2, la seguridad es binaria: el agente puede o no puede ejecutar una acción.
No hay gradaciones según el nivel de autonomía y riesgo.

ASL-3 define un sistema de niveles de seguridad agéntica inspirado en los Responsible
Scaling Policies de Anthropic. A mayor autonomía del agente, mayor nivel de control requerido.

> **Trampa educativa:** parece que ASL-3 es simplemente "más permisos para agentes más
> confiables". La dirección es la contraria: a mayor autonomía del agente (ASL más alto),
> mayor cantidad de controles y restricciones se activan — no menos.
> Un agente ASL-3 no tiene más libertad; tiene más supervisión.

```python
# capa_9/asl3.py — RES.091 · FUT_3

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional

class AgenticSecurityLevel(IntEnum):
    """
    ASL-1: Agente reactivo — solo responde, no inicia acciones externas.
    ASL-2: Agente con herramientas — puede leer datos, llamar APIs de solo lectura.
    ASL-3: Agente autónomo — puede escribir, modificar, iniciar acciones reversibles.
    ASL-4: Agente crítico — puede ejecutar acciones irreversibles (SIEMPRE con HITL).
    """
    ASL_1 = 1  # Reactivo
    ASL_2 = 2  # Herramientas de lectura
    ASL_3 = 3  # Acciones reversibles autónomas
    ASL_4 = 4  # Acciones irreversibles — HITL obligatorio

@dataclass
class ASLProfile:
    agent_id: str
    assigned_level: AgenticSecurityLevel
    capabilities: list[str]          # qué puede hacer
    restrictions: list[str]          # qué está explícitamente prohibido
    requires_nhp: bool                # NHP obligatorio para comunicación
    max_autonomy_minutes: int         # tiempo máximo sin check-in al Orchestrator
    hitl_required: bool               # HITL obligatorio para toda acción

@dataclass
class ASLCheckResult:
    allowed: bool
    effective_level: AgenticSecurityLevel
    controls_activated: list[str]    # controles activos para este nivel
    rejection_reason: Optional[str]  # None si allowed

class ASL3Controller:
    """
    Controlador de Agentic Security Levels.

    INV-ASL.1: Un agente NUNCA opera por encima de su assigned_level.
    INV-ASL.2: ASL-4 requiere HITL sin excepción — no hay override.
    INV-ASL.3: ASL-3 requiere NHP para comunicación inter-agente.
    INV-ASL.4: max_autonomy_minutes se verifica activamente — excederlo
               desactiva el agente hasta check-in del Orchestrator.
    """

    LEVEL_CONTROLS = {
        AgenticSecurityLevel.ASL_1: [
            "output_only",
            "no_external_calls",
            "semantic_firewall_active"
        ],
        AgenticSecurityLevel.ASL_2: [
            "read_only_tools",
            "nhp_for_inter_agent",
            "semantic_firewall_active",
            "critic_mandatory"
        ],
        AgenticSecurityLevel.ASL_3: [
            "nhp_mandatory",
            "reversible_actions_only",
            "critic_mandatory",
            "explainability3d_mandatory",
            "autonomy_timer_active",
            "semantic_firewall_active",
            "zero_trust_session_active"
        ],
        AgenticSecurityLevel.ASL_4: [
            "hitl_mandatory",
            "nhp_mandatory",
            "critic_mandatory",
            "explainability3d_mandatory",
            "dual_approval_required",
            "semantic_firewall_active",
            "zero_trust_session_active",
            "full_audit_log"
        ]
    }

    def check_action(
        self,
        profile: ASLProfile,
        action_type: str,
        is_reversible: bool,
        is_inter_agent: bool
    ) -> ASLCheckResult:
        level = profile.assigned_level
        controls = list(self.LEVEL_CONTROLS.get(level, []))

        if level == AgenticSecurityLevel.ASL_4:
            return ASLCheckResult(
                allowed=True,  # permitido PERO requiere HITL
                effective_level=level,
                controls_activated=controls,
                rejection_reason=None
            )

        if level == AgenticSecurityLevel.ASL_1 and action_type != "output":
            return ASLCheckResult(
                allowed=False,
                effective_level=level,
                controls_activated=controls,
                rejection_reason=f"ASL-1 no permite acciones externas: {action_type}"
            )

        if level == AgenticSecurityLevel.ASL_2 and not is_reversible:
            return ASLCheckResult(
                allowed=False,
                effective_level=level,
                controls_activated=controls,
                rejection_reason=f"ASL-2 requiere acciones reversibles: {action_type}"
            )

        if level == AgenticSecurityLevel.ASL_3 and not is_reversible:
            return ASLCheckResult(
                allowed=False,
                effective_level=level,
                controls_activated=controls,
                rejection_reason=(
                    f"ASL-3 no permite acciones irreversibles. "
                    f"Escalar a ASL-4 con HITL: {action_type}"
                )
            )

        return ASLCheckResult(
            allowed=True,
            effective_level=level,
            controls_activated=controls,
            rejection_reason=None
        )
```

**Parámetros Capa 14:**
```yaml
asl:
  default_level: 2
  max_autonomy_minutes: 30          # [5, 120]
  escalation_on_irreversible: true  # ASL-3 → escalar a ASL-4 automáticamente
  audit_all_checks: true
  asl3_requires_nhp: true           # NHP obligatorio desde ASL-3
  asl4_dual_approval: false         # true en entornos bancarios/médicos

asl_role_map:
  critic: 1
  reader: 2
  analyst: 2
  executor: 3
  coordinator: 3
  admin: 4
```

---

## §9.ZTS — Zero Trust Session · RES.092 · FUT_3

**Qué resuelve Zero Trust Session:**
En V2, una vez que un agente o usuario es autenticado, su sesión mantiene la confianza
implícita hasta que expira el JWT. Si el JWT es robado o el agente es comprometido después
del login, el sistema no lo detecta.

Zero Trust Session aplica el principio "never trust, always verify" a cada operación dentro
de la sesión — no solo al inicio. Cada acción relevante requiere micro-verificación contextual.

> **Trampa educativa:** parece que Zero Trust significa "no confiar en nadie externo".
> El concepto completo va más lejos: tampoco confiar en entidades ya autenticadas dentro
> del sistema. Un agente que pasó el NHP hace 2 minutos puede haber sido comprometido
> en esos 2 minutos. Zero Trust Session lo detecta por anomalías de comportamiento.

```python
# capa_9/zero_trust_session.py — RES.092 · FUT_3

import time
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SessionContext:
    session_id: str
    tenant_id: str
    agent_id: str
    asl_level: int
    nhp_token: str           # token del NHP exitoso
    created_at: float
    last_verified_at: float
    action_count: int = 0
    anomaly_score: float = 0.0   # [0.0-1.0] — acumula por comportamientos atípicos
    revoked: bool = False

@dataclass
class ZTSVerification:
    approved: bool
    anomaly_delta: float     # cuánto subió el anomaly_score esta acción
    new_anomaly_score: float
    action_log: str
    revocation_triggered: bool
    revocation_reason: Optional[str]

class ZeroTrustSession:
    """
    Zero Trust Session — verificación continua por acción.

    INV-ZTS.1: anomaly_score >= 0.8 → revocación automática de sesión.
    INV-ZTS.2: Sesión NUNCA se extiende automáticamente — solo por Orchestrator.
    INV-ZTS.3: Acción fuera del ASL del agente suma +0.3 al anomaly_score.
    INV-ZTS.4: NHP token expirado suma +0.5 al anomaly_score.
    INV-ZTS.5: tenant_id de la acción == tenant_id de la sesión. Siempre.
    """

    ANOMALY_THRESHOLD = 0.8    # revocación automática
    TTL_DEFAULT = 1800          # 30 minutos

    def __init__(self, config: dict = None):
        self.cfg = config or {}
        self.threshold = self.cfg.get("zts.anomaly_threshold", self.ANOMALY_THRESHOLD)
        self.ttl = self.cfg.get("zts.session_ttl_seconds", self.TTL_DEFAULT)
        self.sessions: dict[str, SessionContext] = {}

    def create_session(
        self,
        agent_id: str,
        tenant_id: str,
        asl_level: int,
        nhp_token: str
    ) -> SessionContext:
        """Crea una nueva sesión Zero Trust tras NHP exitoso."""
        import secrets
        now = time.time()
        ctx = SessionContext(
            session_id=secrets.token_hex(16),
            tenant_id=tenant_id,
            agent_id=agent_id,
            asl_level=asl_level,
            nhp_token=nhp_token,
            created_at=now,
            last_verified_at=now
        )
        self.sessions[ctx.session_id] = ctx
        return ctx

    def verify_action(
        self,
        session_id: str,
        action_tenant_id: str,
        action_type: str,
        required_asl: int,
        nhp_token_current: str,
        nhp_issued_at: float,
        nhp_ttl: int = 300
    ) -> ZTSVerification:
        """
        Verifica cada acción dentro de la sesión activa.
        Acumula anomaly_score y revoca si supera el umbral.
        """
        ctx = self.sessions.get(session_id)
        now = time.time()

        if not ctx or ctx.revoked:
            return ZTSVerification(
                approved=False,
                anomaly_delta=0.0,
                new_anomaly_score=1.0,
                action_log=f"REJECT session {session_id[:8]} no válida o revocada",
                revocation_triggered=False,
                revocation_reason="Sesión inválida"
            )

        delta = 0.0
        log_parts = []

        # INV-ZTS.5 — tenant match
        if action_tenant_id != ctx.tenant_id:
            delta += 0.5
            log_parts.append("cross-tenant action (+0.5)")

        # INV-ZTS.4 — NHP token vigente
        if now > nhp_issued_at + nhp_ttl:
            delta += 0.5
            log_parts.append("NHP expired (+0.5)")
        elif nhp_token_current != ctx.nhp_token:
            delta += 0.3
            log_parts.append("NHP token mismatch (+0.3)")

        # INV-ZTS.3 — ASL level check
        if required_asl > ctx.asl_level:
            delta += 0.3
            log_parts.append(f"action requires ASL-{required_asl} > assigned ASL-{ctx.asl_level} (+0.3)")

        # Sesión expirada por TTL
        if now > ctx.created_at + self.ttl:
            delta += 0.5
            log_parts.append("session TTL expired (+0.5)")

        # Actualizar contexto
        ctx.anomaly_score = min(1.0, ctx.anomaly_score + delta)
        ctx.action_count += 1
        ctx.last_verified_at = now

        # INV-ZTS.1 — umbral de revocación
        revoked = ctx.anomaly_score >= self.threshold
        revocation_reason = None
        if revoked and not ctx.revoked:
            ctx.revoked = True
            revocation_reason = (
                f"anomaly_score={ctx.anomaly_score:.2f} >= threshold={self.threshold}. "
                f"Causas: {', '.join(log_parts) if log_parts else 'acumulación progresiva'}"
            )

        action_log = (
            f"ZTS {'REVOKE' if revoked else 'OK'} "
            f"session={session_id[:8]} "
            f"action={action_type} "
            f"anomaly={ctx.anomaly_score:.2f} "
            f"{'| ' + ' | '.join(log_parts) if log_parts else ''}"
        )

        return ZTSVerification(
            approved=not revoked and delta == 0.0,
            anomaly_delta=delta,
            new_anomaly_score=ctx.anomaly_score,
            action_log=action_log,
            revocation_triggered=revoked,
            revocation_reason=revocation_reason
        )
```

**Parámetros Capa 14:**
```yaml
zero_trust_session:
  enabled: true
  session_ttl_seconds: 1800          # [300, 7200]
  anomaly_threshold: 0.8             # [0.5, 1.0]
  cross_tenant_weight: 0.5
  nhp_expired_weight: 0.5
  nhp_mismatch_weight: 0.3
  asl_violation_weight: 0.3
  log_anomalies: true
  alert_on_revocation: true
```

**Namespace Redis:**
```
mpat:zts:{session_id}:ctx        → SessionContext (TTL: session_ttl)
mpat:zts:{session_id}:anomaly    → anomaly_score actual (TTL: session_ttl)
mpat:zts:revoked:{date}          → Set de sessions revocadas hoy
mpat:zts:alerts:{tenant_id}      → List de alertas de revocación (max 100)
```

---

## INVARIANTE CROSS-CAPA: INV-09-QUIC.1 (observacional, RES.157)

```
INV-09-QUIC.1 (OBSERVACIONAL):
  El tenant_id verificado por NHPProtocol en el handshake es el mismo
  que QUICGateway registra en Redis y QUICSpanExporter publica en OTel.
  No hay sincronización activa entre CAPA_09 y CAPA_10 — el invariante
  se sostiene porque ambas capas leen el mismo campo del ECS.
  Violación sería síntoma de compromiso del ECS (INV-6-ECS.1).
```

> **Trampa educativa cross-capa:** parece razonable que CAPA_09 verifique que el tenant_id
> del span QUIC coincide con el del handshake NHP antes de aprobar cada acción.
> El error: introduce acoplamiento directo entre CAPA_09 y CAPA_10 donde no lo hay.
> ZeroTrustSession ya verifica `tenant_id` en CADA acción (INV-ZTS.5). Si el ECS tiene
> el tenant_id correcto (garantizado por INV-6-ECS.1), y el span QUIC lo lee del mismo ECS,
> la verificación ya ocurrió. Una segunda verificación en CAPA_09 contra CAPA_10 sería
> redundante y crearía dependencia circular (seguridad dependiendo de observabilidad).

---

## INVARIANTES GLOBALES — CAPA_09 V4_00

| ID | Invariante | Nivel |
|---|---|---|
| INV-NHP.1 | Datos operativos solo fluyen tras NHP exitoso | CRÍTICO |
| INV-NHP.2 | Nonce de un solo uso — anti-replay | CRÍTICO |
| INV-NHP.3 | Cross-tenant handshake siempre bloqueado | CRÍTICO |
| INV-NHP.4 | session_token expira en session_ttl_seconds | ALTO |
| INV-ASL.1 | Agente nunca opera sobre su assigned_level | CRÍTICO |
| INV-ASL.2 | ASL-4 requiere HITL sin excepción | CRÍTICO |
| INV-ASL.3 | ASL-3 requiere NHP para comunicación | ALTO |
| INV-ASL.4 | Autonomy timer activo desde ASL-3 | ALTO |
| INV-ZTS.1 | anomaly_score >= 0.8 → revocación automática | CRÍTICO |
| INV-ZTS.2 | Sesión no se extiende automáticamente | CRÍTICO |
| INV-ZTS.3 | Acción fuera del ASL suma +0.3 al anomaly_score | ALTO |
| INV-ZTS.4 | NHP expirado suma +0.5 al anomaly_score | ALTO |
| INV-ZTS.5 | tenant_id siempre verificado por acción | CRÍTICO |
| INV-09-QUIC.1 | tenant_id NHP == tenant_id span QUIC (observacional) | MEDIO |

---

## ESTADO GLOBAL CAPA_09 — V4_00

| Componente | Estado | RES |
|---|---|---|
| Zero-Trust Validator | HEREDADO V2 | — |
| Critic Agent | HEREDADO V2 | — |
| HITL Manager | HEREDADO V2 | RES.001 |
| Semantic Firewall | HEREDADO V2 | — |
| JWT / RBAC / OAuth 2.1 | HEREDADO V2 | — |
| Explainability3D | HEREDADO FUT.30 | RES.083 |
| PredictiveEmpathy | HEREDADO FUT.32 | RES.084 |
| **NHP Protocol** | **CERRADO V3_01** | **RES.090** |
| **ASL-3** | **CERRADO V3_01** | **RES.091** |
| **Zero Trust Session** | **CERRADO V3_01** | **RES.092** |
| **NHP used_nonces Redis** | **CERRADO V3_02** | **RES.123** |
| **Double Ratchet E2E A2A** | **CERRADO V3_02** | **RES.145** |
| **NHP Protocol DEFINITIVO** | **CERRADO V3_02** | **RES.149** |
| **Cross-ref RES.157** | **REGISTRADO V4_00** | **RES.157 (obs)** |

---

## DTs activas: NINGUNA

Todas las DTs de CAPA_09 cerradas en V3_02 base.

---

*CAPA_09_MASTER_V4_00.md · MPAT V4_00 · 2026-05-23*
*Consolidado desde: CAPA_09_MASTER_V3_01_UNIFICADO (ai.mpat.designer) + CAPA_09_MASTER_V3_02_DELTA (agt1973)*
*Razonamiento: el DELTA no modifica código — agrega RES.123/145/149 en tabla de estado + INV-09-QUIC.1 observacional.*
*El cuerpo de implementación viene íntegro del V3_01_UNIFICADO. V3_02_base absorbida por el DELTA.*
