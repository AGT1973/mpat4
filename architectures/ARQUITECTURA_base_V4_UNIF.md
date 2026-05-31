# ARQUITECTURA_base_V4_UNIF.md
## MPAT — My Personal Agents Team
## Descripcion Estructural por Capas · Version Pedagogica Completa
### Version V4 · UNIFICADO · AGT 2026
### Fuentes unificadas:
###   A) ID: 1cyg9BLUeSi4VUJWVVpvVxG_j2JOMeuX9 (cursos.python.agt · RELAY_033 · agt1973)
###   B) ID: 1dpYcf1OjLwyFOr9oc6SLvFPzgClgd1dZ (ai.mpat.andrea · ariel.garcia.traba)
### Unificacion: agt1973@gmail.com · 2026-05-23 · LOTE_001
### Cambios V4 respecto a V3_03:
###   - RES.155: Transport Layer QUIC + eBPF (QUICGateway nativo)
###   - RES.156: Payment Dispatcher x402/Stripe MPP
###   - RES.157: OpenInference + QUICSpanExporter (observabilidad LLM)
###   - RES.158: Namespace ECS incluye tenant_id — patron canonico V4 (DT-06-01 cerrada)
###   - CAPA_01: FlowGRPO integrado como hint de tier de inferencia
###   - CAPA_03: Planner V4 formalizado (task.parallelizable)
###   - CAPA_04: AgentCard JSON-LD, ManagedAgents, A2AHandoffManager, Audio Kernel 2.0
###   - FUT candidatos V4: FUT.40-FUT.52 documentados
*que has usado el formato de razonamiento adaptado por AGT_2026*

---

> **Para el alumno — como leer este documento:**
> Este documento describe la arquitectura del sistema MPAT capa por capa.
> El principio es: **"Si necesitas modificar el comportamiento X del sistema,
> deberias poder hacerlo cambiando exactamente una capa, sin tocar las demas."**
> Primera lectura: de corrido para tener el mapa mental.
> Segunda lectura: como especificacion de lo que tenes que construir.

---

## SISTEMA DE RELAY COGNITIVO

El Relay Cognitivo permite transferir entre agentes/workers/sesiones:
contexto, presupuesto, memoria, estado parcial, reasoning trace, ownership de ejecucion.

Sin Relay: agentes reinician contexto, se pierde reasoning, aumenta costo, inconsistencias.
Con Relay: preserva estado operacional, reduce recomputacion, mejora resiliencia, habilita ejecucion distribuida real.

Opera sobre: ECS snapshots, semantic cache, checkpoints, memory deltas, execution lineage, contracts de delegacion.

---

## INDICE DE CAPAS

```
CAPA 0  -> Entrada al Sistema (Browser, Telegram, WhatsApp, API externa)
CAPA 1  -> Puerta de Entrada (QUICGateway + eBPF + FlowGRPO) [V4: RES.155 + FlowGRPO]
CAPA 2  -> API y Transporte (FastAPI, WebSocket, SSE + GRPO metadata) [V4: RES.156 integrada]
CAPA 3  -> Orquestacion Cognitiva (Orchestrator / Planner V4 / Scheduler No-GIL / MAS)
CAPA 4  -> Motor de Agentes (AgentManager, AgentCard JSON-LD, ManagedAgents,
            A2AHandoffManager, Audio Kernel 2.0, Versioning)
CAPA 5  -> Motor de Inferencia (Model Router, Inferencia Especulativa)
CAPA 6  -> Estado Cognitivo (ECS, Schema, Reglas) [V4: RES.158 — namespace fix tenant_id]
CAPA 7  -> Herramientas y Protocolos (Skills, MCP 2.0, A2A, Skill Registry)
CAPA 8  -> Memoria (Activa, Persistente, Poda de Contexto, Semantic Caching)
CAPA 9  -> Seguridad y Validacion (NHP Protocol, ASL-3, Zero Trust Session,
            Critic Agent, HITL, Semantic Firewall)
CAPA 10 -> Observabilidad (OpenTelemetry, QUICSpanExporter, Tracing, Alertas,
            Metricas Cognitivas, OpenInference) [V4: RES.157 integrada]
CAPA 11 -> Infraestructura de Workers (Redis, RQ, Auto-scaling, Checkpointing,
            Unikernel-per-Tenant, Sub-Queue Asincrona)
CAPA 12 -> Multi-tenancy y Presupuesto (Conservation Laws, Budget Manager,
            A2A v1.0 cross-tenant, SubQ presupuestada, VMAO — RES.144)
CAPA 13 -> Capa de Entrega (Delivery Layer, Formateo, Canal de Salida,
            A2A Delivery, SubQ Async Delivery, Unikernel Isolation Guard)
CAPA 14 -> Configuracion Global — jerarquia dos niveles (RES.137):
            NIVEL 1: policy.yaml (gobernanza — precedencia absoluta)
            NIVEL 2: config/mcp.yaml, config/tool_registry.yaml,
                     config/skill_validation.yaml, config/payment.yaml
```

---

## PRINCIPIOS TRANSVERSALES (13 principios — aplican a todas las capas)

**P1 — Todo efecto externo pasa por MCP.**
Ningun componente llama a servicio externo directamente. Interfaz unica: MCP 2.0.

**P2 — Ninguna decision de modelo es directa.**
Todo agente declara perfil de inferencia. El sistema decide que modelo cumple ese perfil.

**P3 — Zero-Trust.**
Ningun resultado externo es valido sin validacion del Orchestrator.
`validated_by_orchestrator = true` solo puede ser seteado por el Orchestrator.

**P4 — Nada hardcodeado.**
Todos los umbrales, timeouts y limites son parametros configurables en YAML o env.

**P5 — Toda decision es auditable.**
Cada decision del Orchestrator se loguea: task_id, agent_id, entropia, modelo, presupuesto, razon.

**P6 — El sistema se degrada, no falla.**
Ante recurso insuficiente: remoto => local, alta calidad => aproximacion, completo => parcial.
Siempre entrega algo util. Nunca un error vacio.

**P7 — Budget como conservation law.**
Suma de presupuestos delegados activos nunca supera 100% del tenant.
Al destruir un agente, presupuesto no usado retorna al padre inmediatamente.
Referencia: incidente COINE 2026 — $47.000 USD en 11 dias por ausencia de este principio.

**P8 — Version semantica obligatoria para Skills.**
Toda skill tiene version `major.minor.patch`. Al inicio de ejecucion (SPAWN), se captura
snapshot de versiones. Ese snapshot es inmutable durante la ejecucion.

**P9 — El Critic nunca bloquea el pipeline silenciosamente.**
Si el modelo de evaluacion falla: fail-open progresivo con alerta. Nunca silencio.

**P10 — El logic_trace nunca se loguea en texto plano por defecto.**
Puede contener PII. Solo en modo debug explicito. Con privacidad HIGH: nunca se loguea.

**P11 — Las metricas cognitivas son tan importantes como las de ejecucion.**
Metricas ERR, RV, CI, MCS y PSC miden calidad del razonamiento, no solo ejecucion mecanica.

**P12 — El contrato de capacidades de un agente es inmutable durante una delegacion activa.**
Si el AgentCard cambia durante ejecucion, el sistema lo detecta y actua segun politica configurada.

**P13 — AI Specifiers Rule: todo contrato de herramienta es legible por maquina antes de su invocacion.**
Ningun componente del sistema puede invocar una herramienta, skill o agente externo
sin que exista un contrato formal (schema de input/output, trust_tier, version) legible
por maquina en el momento de la invocacion.
Capas que deben cumplir P13: CAPA_3, CAPA_4, CAPA_7, CAPA_12.

**INV-ECS-NS.1 (nuevo V4 — RES.158):**
Todo namespace de ECS incluye tenant_id como segundo segmento.
Patron: `mpat:cx:{tenant_id}:{session_id}:{componente}`

---

## CAPAS 01-04 — DOCUMENTACION COMPLETA V4

### CAPA_01 — QUICGateway + eBPF + FlowGRPO (V4 — RES.155 nativa)

**Responsabilidad:** puerta de entrada del sistema. Transporte principal QUIC con eBPF para
filtrado en kernel space. FlowGRPO emite hint de tier de inferencia antes de enrutar al
Orchestrator. HTTP/1.1 permanece como fallback (P6).

**Componentes:**

| Componente | Version | RES | Descripcion |
|---|---|---|---|
| QUICGateway | V4 | RES.155 | Transporte QUIC + HTTP/3 + TLS 1.3 integrado |
| eBPFPacketFilter | V4 | RES.155 | Firewall L4 en kernel space — filtra antes de userspace |
| JWTValidator | V2 activo | — | Verifica tenant_id antes de asignar Unikernel |
| RateLimiter | V2 activo | — | Control de trafico por tenant |
| TenantRouter | V4 | RES.155 | Asigna unikernel_id al tenant |
| FlowGRPO | **V4 nuevo** | FUT.40 | Hint de tier de inferencia optimo para CAPA_05 |

**StreamTypes (QUIC):**

| StreamType | Descripcion | Prioridad | 0-RTT |
|---|---|---|---|
| AGENT_TASK | Nueva tarea de agente | HIGH | NO (INV-QUIC.5) |
| AGENT_RESULT | Resultado de agente | HIGH | NO |
| SUBQ_NOTIFY | Notificacion SubQ | NORMAL | SI |
| HEARTBEAT | Keepalive | LOW | SI |
| OTEL_SPAN | Spans OTel (V4 — RES.157) | LOW | NO |

**FlowGRPO en CAPA_01 — diagrama:**

```
solicitud → QUICGateway → FlowGRPO(perfil, presupuesto, carga)
                                        ↓
                         [tier_hint: local | cloud | speculative]
                                        ↓
                         Orchestrator (CAPA_03) — recibe hint, decide
```

FlowGRPO (Group Relative Policy Optimization aplicado a flujo) evalua el perfil de la solicitud
y sugiere el tier de inferencia optimo segun presupuesto y carga actual. El hint es informativo:
el Orchestrator decide independientemente (INV-ORCH.5).

**Invariantes CAPA_01:**
```
INV-GW.1: Todo trafico entrante pasa por QUICGateway — nunca directo a CAPA_02
INV-GW.2: eBPF filtra antes de que el paquete llegue al proceso Python
INV-GW.3: FlowGRPO emite hint — no decision vinculante — el Orchestrator decide
INV-GW.4: tier_hint se propaga en el contexto de la solicitud hasta CAPA_05
INV-QUIC.1: NUNCA opera sin TLS 1.3 integrado.
INV-QUIC.2: perdida de un stream NUNCA bloquea otros streams de la misma conexion.
INV-QUIC.3: una conexion NUNCA supera max_streams_per_connection activos.
INV-QUIC.4: BPF map NUNCA excede budget del tenant (P7). Orden: Redis primero, luego BPF map.
INV-QUIC.5: AGENT_TASK siempre 1-RTT. Solo HEARTBEAT y SUBQ_NOTIFY admiten 0-RTT.
INV-QUIC.6: si Redis no disponible en sincronizacion BPF map, mantener ultimo valor. NUNCA resetear a 0.
INV-EBPF.1: programa eBPF NUNCA accede a memoria fuera del buffer del paquete actual.
INV-EBPF.2: recarga del programa eBPF es zero downtime.
INV-157.3: StreamType OTEL_SPAN es read-only — solo el sistema puede escribir en el.
```

**Namespaces Redis CAPA_01:**

| Namespace | TTL | Tipo |
|---|---|---|
| mpat:quic:session:{tenant_id}:{connection_id} | 3600s | Hash |
| mpat:quic:ticket:{tenant_id} | 86400s | String |
| mpat:ebpf:quota:{tenant_id} | 60s | String |
| mpat:jwt:blacklist:{jti} | jwt_expiry | String |

---

### CAPA_02 — API y Transporte (V4 — RES.156 integrada)

**Responsabilidad:** preprocesamiento, validacion semantica del payload, routing al Orchestrator.
Soporte SSE con metadatos de politica GRPO (RES.156). Version V2 consolidado en V3_01.

**Componentes:**

| Componente | Protocolo | Descripcion |
|---|---|---|
| FastAPIRouter | HTTP/1.1, HTTP/2 | Recibe ValidatedRequest de CAPA_01, valida schema ECS |
| WebSocketHandler | RFC 6455 | Sesiones bidireccionales en tiempo real |
| SSEHandler | Server-Sent Events | Streaming unidireccional — compatible MCP 2.0 chunks |
| gRPC | HTTP/2 | Comunicacion inter-servicio interna |
| TenantContextInjector | — | Inyecta tenant_id en todos los campos ECS |
| SchemaValidator | — | Valida payload contra ECS schema del tenant |

**Invariantes CAPA_02:**
```
INV-TRANSPORT.1: SSE y WebSocket NUNCA comparten el mismo worker pool
INV-TRANSPORT.2: Toda respuesta incluye trace_id propagado desde CAPA_01
INV-TRANSPORT.3: Timeout de conexion configurable via config/mcp.yaml (no hardcodeado — P4)
INV-SCHEMA.1: SchemaValidator NUNCA deja pasar payload invalido a CAPA_3.
INV-ECS-001: ningun ECS sale de CAPA_02 con tenant_id=None o tenant_id="unknown".
INV-SSE.1: SSEHandler NUNCA emite chunk sin que haya pasado por SemanticFirewall (CAPA_9).
```

**Config V4:**
```yaml
api:
  sse_emit_policy_metadata: false  # opt-in por tenant (RES.156)
  ws_timeout: 3600
  sse_max_buffer_size: 1048576
```

---

### CAPA_03 — Orquestacion Cognitiva (V4 — Planner formalizado)

**Responsabilidad:** nucleo de decision. No genera texto. Evalua entropia, aplica politica formal,
decide modelo, coordina agentes y swarms.

**Componentes:**

| Componente | Version | RES | Descripcion |
|---|---|---|---|
| Orchestrator | V3_01 | — | Ciclo Plan/Execute/Reflect/Replan |
| ExecutionPolicyEngine | V2_04 | — | Decision de modelo basada en Entropia E |
| EntropyCalculator | V2_04 | — | Metrica CDR compuesta |
| K_BROKEN Detector | V2_04 | — | Coherence Index continuo [0.0-1.0] |
| ZeroTrust Validator | V2_04 | — | Unico que puede setear validated_by_orchestrator=true |
| CognitiveScheduler | V3_01 | RES.094 | ThreadPoolExecutor No-GIL, 50-200 agentes/nodo |
| SwarmOrchestrator | V3_01 | RES.095 | Enjambre MAS para E > 0.8 |
| Planner | **V4** | FUT.44 | Setea task.parallelizable con INV-PLAN.1/2/3 |

**Tabla de decision por entropia:**

| E | Decision |
|---|---|
| < 0.3 | SLM local |
| 0.3-0.6 | modelo local + remoto especulativo |
| 0.6-0.8 | API remota |
| 0.8-1.0 | API top tier + alerta + MAS si parallelizable |

**Ciclo de ejecucion:**
```
Orchestrator:
  PLAN    → descompone tarea en sub-tareas (Planner V4 — task.parallelizable)
  EXECUTE → encola sub-tareas con presupuesto delegado (P7)
  REFLECT → evalua resultado parcial (Critic Agent via CAPA_09)
  REPLAN  → ajusta plan si reflect detecta desviacion
```

**Invariantes CAPA_03:**
```
INV-ORCH.1: Orchestrator es el UNICO componente que setea validated_by_orchestrator=True (P3)
INV-ORCH.2: Cada sub-tarea recibe presupuesto delegado <= presupuesto disponible del tenant (P7)
INV-ORCH.3: Antes de encolar tool call, contrato P13 verificado (P13)
INV-ORCH.4: Toda decision se loguea con: task_id, agent_id, entropia, modelo, presupuesto, razon (P5)
INV-ORCH.5: tier_hint de CAPA_01 es informacion de entrada — no obliga al Orchestrator
INV-SCH.1: max_workers NUNCA excede limite de policy.yaml (max absoluto 256).
INV-MAS.1: budget total swarm <= budget tenant. Verificacion ANTES del spawn.
INV-MAS.2: cada agente opera en su propio ECS sin estado compartido mutable.
INV-MAS.4: agente fallido NO cancela swarm — se excluye de consolidacion.
INV-PLAN.3: ante ambiguedad de independencia, parallelizable=False (conservador).
```

**Config V4:**
```yaml
orchestrator:
  scheduler_max_workers: 32  # [4, 256]
  max_phase_iterations: 3
mas:
  enabled: true
  entropy_threshold: 0.8
  max_swarm_size: 5
  consolidation_strategy: "consensus"
```

---

### CAPA_04 — Motor de Agentes (V4)

**Responsabilidad:** ciclo de vida de agentes individuales, AgentCard JSON-LD, A2A, Audio Kernel 2.0.

**Componentes V4:**

| Componente | Version | RES | Descripcion |
|---|---|---|---|
| AgentManager | V3_01 | — | Ciclo de vida: SPAWN/RUN/SLEEP/TERMINATE |
| AgentCard JSON-LD | **V4** | FUT.41 | Schema legible por maquina (P13) |
| ManagedAgents | **V4** | FUT.42 | Pool de agentes gestionados con versionado y health check |
| A2AHandoffManager | **V4** | FUT.43 | Transferencia de contexto entre agentes |
| AgentVersioning | V3_01 | RES.148 | Snapshot de versiones al SPAWN (P8) |
| Audio Kernel 2.0 | **V4** | — | TTS/STT con SLA formal |
| InferenceProfile | V3_01 | — | Perfil asignado por CAPA_3 — no modificable en runtime |

**AgentCard JSON-LD — schema V4:**

```json
{
  "@context": "https://mpat.ai/schemas/v4/agent-card",
  "@type": "AgentCard",
  "agent_id": "string — UUID4",
  "tenant_id": "string — requerido (INV-ECS-NS.1)",
  "version": "semver — major.minor.patch (P8)",
  "capabilities": ["lista de habilidades declaradas"],
  "trust_tier": "internal | external | sandboxed",
  "input_schema": "JSON Schema del input esperado (P13)",
  "output_schema": "JSON Schema del output producido (P13)",
  "budget_ceiling": "float — maximo presupuesto delegable (P7)",
  "autonomy_level": "1 | 2 | 3 — segun ASL-3 (CAPA_09)",
  "contract_hash": "SHA256 del contrato — inmutable durante delegacion activa (P12)"
}
```

**A2AHandoffManager — protocolo V4:**

```
INICIADOR prepara HandoffPacket:
  - ecs_snapshot:        CognitiveState serializado (con tenant_id — RES.158)
  - memory_delta:        cambios de memoria desde ultimo checkpoint
  - execution_lineage:   historial de decisiones del Orchestrator
  - budget_transfer:     presupuesto cedido (P7 — conservation law)
  - contract_ref:        referencia al AgentCard del receptor (P12/P13)

RECEPTOR valida HandoffPacket:
  - tenant_id del iniciador == tenant_id del receptor (INV-NHP.3)
  - contract_hash == hash actual del AgentCard (P12)
  - budget_transfer <= presupuesto disponible del iniciador (P7)

Si validacion OK   → receptor hereda contexto
Si validacion FALLA → handoff rechazado, Orchestrator notificado (P9)
```

**Audio Kernel 2.0 — SLA V4:**

| Metrica | Default | WARNING | CRITICO |
|---|---|---|---|
| tts_latency_p95_ms | 150ms | 150ms | 300ms |
| stt_latency_p95_ms | 200ms | 200ms | 400ms |

**Invariantes CAPA_04:**
```
INV-AGENT.1: Ningun agente se invoca sin AgentCard valido (P13)
INV-AGENT.2: AgentCard.contract_hash es inmutable durante delegacion activa (P12)
INV-AGENT.3: SPAWN captura snapshot de versiones — inmutable durante ejecucion (P8)
INV-AGENT.4: A2AHandoffManager verifica tenant_id antes de toda transferencia (INV-NHP.3)
INV-AGENT.5: Al TERMINATE, budget no usado retorna al padre inmediatamente (P7)
INV-AGENT.6: autonomy_level >= 2 requiere HITL Gate activo (CAPA_09 — ASL-3)
INV-4-CARD.1: ningun agente opera con AgentCard vencida o sin firma valida.
INV-4-A2A.1: handoffs cross-tenant imposibles.
INV-4-AUDIO.1: 3 mediciones p95 consecutivas sobre umbral → alerta automatica a CAPA_10.
INV-4-PROF.1: InferenceProfile asignado por CAPA_3. CAPA_4 nunca lo modifica en runtime.
```

---

## ACTUALIZACIONES V4 EN CAPAS HEREDADAS

### CAPA_06 — ECS (V4 — RES.158 aplicada)

**Cambio:** namespaces MEA corregidos con tenant_id.

```
# V3_02 (INCORRECTO)
mpat:cx:{session_id}:experts
mpat:cx:{session_id}:conflict_log

# V4 (CORRECTO — RES.158)
mpat:cx:{tenant_id}:{session_id}:experts
mpat:cx:{tenant_id}:{session_id}:conflict_log
```

Namespace canonico V4: `mpat:cx:{tenant_id}:{session_id}:{componente}`

### CAPA_08 — Memoria (V4 — derivado RES.158)

Namespace hebbiano actualizado:

```
# V4
mpat:dream:{tenant_id}:{session_id}:feedback
```

> PENDIENTE: FUT-V4-09 — auditoria completa de namespaces CAPA_08 post-migracion. Ver LOTE_001.

### CAPA_10 — Observabilidad (V4 — RES.157 integrada)

**Cambio:** jerarquia de spans QUICSpanExporter.

```
NIVEL 1 (padre): quic.inference_request
  NIVEL 2A: quic.transport (metricas eBPF por push — INV-OBS-QUIC.2)
  NIVEL 2B: openinference.inference (TTFT, tokens, GRPO attrs — INV-OBS-QUIC.3)
```

Alertas nuevas V4:
- `NVFP4_TTFT_COMPOUND`: NVFP4 activo + TTFT alto → hardware incompatible
- `XGRAMMAR2_SLOW_COMPILE`: compilation_ms > umbral en schema nuevo

### CAPAS 05, 07, 09, 11, 12, 13, 14 — Sin cambios V4

Heredan de V3_03. Ver ARQUITECTURA_base_V3_03.md (ID: 1maihtP8yxoVodu5b3QdzS89tzPzEyF02) para descripcion completa.

| Capa | Estado V4 | Cambio |
|---|---|---|
| CAPA_05 | Hereda V3_03 | Recibe tier_hint de CAPA_01 (FlowGRPO) |
| CAPA_07 | Hereda V3_03 | Sin cambios |
| CAPA_09 | Hereda V3_03 | Sin cambios |
| CAPA_11 | Hereda V3_03 | Sin cambios |
| CAPA_12 | Hereda V3_03 | Sin cambios |
| CAPA_13 | Hereda V3_03 | Sin cambios |
| CAPA_14 | Hereda V3_03 | Sin cambios |

---

## DIAGRAMA DE FLUJO PRINCIPAL (V4)

```
Usuario/Canal externo
 |
[CAPA 0]  Entrada — normaliza input, detecta plataforma
 |
[CAPA 1]  QUICGateway + eBPF — autentica JWT, rate limit, FlowGRPO hint
           | QUIC streams multiplexados | HTTP/1.1 fallback (P6)
           | tier_hint propagado en contexto
 |
[CAPA 2]  Transporte — FastAPI/WebSocket/SSE + GRPO metadata (RES.156)
           TenantContextInjector + SchemaValidator
 |
[CAPA 3]  Orchestrator — Plan => Execute => Reflect => Replan
           Planner (task.parallelizable) → CognitiveScheduler | SwarmOrchestrator
           (recibe tier_hint, decide independientemente — INV-ORCH.5)
           |                          |
[CAPA 4]                          [CAPA 6]
Agent Mgr                         ECS State
(AgentCard JSON-LD                (namespaces V4 — RES.158:
 ManagedAgents                     mpat:cx:{tenant_id}:{session_id}:{comp})
 A2AHandoffManager)
           |
[CAPA 5]  Model Router — selecciona modelo segun perfil + tier_hint + fallback chain
 |
[CAPA 7]  Skills/MCP 2.0/A2A — herramientas (P13: contrato antes de invocar)
 |
[CAPA 8]  Memoria — activa (RAM) + persistente (vector) + semantic cache
           (namespace hebbiano: mpat:dream:{tenant_id}:{session_id}:feedback)
 |
[CAPA 9]  Critic/Security — NHP Protocol, ASL-3, ZTS, HITL, Semantic Firewall
 |
[CAPA 13] Delivery — formatea y envia por canal correcto + UnikerGuard
 |
Usuario/Canal

Transversales (todas las capas los usan):
  [CAPA 10] Observabilidad — OTel + QUICSpanExporter (RES.157) + OpenInference
  [CAPA 11] Workers — Redis, RQ, Unikernel-per-Tenant, SubQ
  [CAPA 12] Multi-tenancy — Budget (P7), VMAO (RES.144), A2A v1.0
  [CAPA 14] Config Global — policy.yaml (N1) > config/*.yaml (N2) > env > defaults
```

---

## STACK TECNOLOGICO V4

```
Runtime:      LangGraph + ExecutionState persistente
Estado:       Redis State Manager
Memoria:      ChromaDB + FAISS + Context Buffer + Episodic Memory
API:          FastAPI + WebSocket + SSE
Transporte:   QUIC + eBPF (V4 — RES.155) | HTTP/1.1 fallback (P6)
Canales:      WhatsApp Business, Telegram, Email, SMS, WebRTC
Voz:          Whisper STT + TTS local/cloud + VAD
Observ.:      OpenTelemetry + QUICSpanExporter (V4 — RES.157) +
              structured logging + OpenInference (semantico LLM)
Workers:      Redis + RQ + auto-scaling + Unikernel-per-Tenant + SubQ
Seguridad:    NHP Protocol + ASL-3 + ZTS + Zero-Trust + Critic Agent +
              HITL + Sandbox RAM + KeyVault
Pagos:        x402 + Stripe MPP (V4 — RES.156)
Multi-tenant: Aislamiento total por tenant
              Namespace ECS: mpat:cx:{tenant_id}:{session_id}:{comp} (RES.158)
Optimiz.:     Nuitka, PyPy, Rust via PyO3
Acceso:       Tailscale + FastAPI headless 24/7
Python:       3.13t (No-GIL estable en produccion)
Inferencia:   FlowGRPO (hint de tier en gateway — V4 nuevo)
Agentes:      AgentCard JSON-LD + ManagedAgents + A2AHandoffManager (V4 nuevo)
```

---

## FUT CANDIDATOS V4

Identificados durante cierre V3_02 y auditoria RELAY_033.
**Proxima RES disponible:** RES.159

| FUT | Descripcion | Capa | Prioridad | RES candidata / origen |
|---|---|---|---|---|
| FUT.40 | FlowGRPO — implementacion completa (hint tier es paso 1) | CAPA_01 | ALTA | RES.159 candidata |
| FUT.41 | AgentCard JSON-LD machine-readable formal (PEND-4-01) | CAPA_04 | ALTA | RES.159 |
| FUT.42 | Managed Agents con RES numerada (PEND-4-02) | CAPA_04 | ALTA | RES.160 |
| FUT.43 | A2AHandoffManager protocolo completo + tests (PEND-4-03) | CAPA_04 | ALTA | RES.161 |
| FUT.44 | Planner V4 con RES numerada (PEND-3-01) | CAPA_03 | ALTA | RES.162 candidata |
| FUT.45 | Integracion Arize/Phoenix (OpenInference externo) | CAPA_10 | MEDIA | RES.157 extension |
| FUT.46 | Predictive Maintenance RLHF hebbiano (FUT.33 profundidad) | CAPA_06/08 | MEDIA | RES.121/157 |
| FUT.47 | UnikerManager benchmark cold start formal en CI | CAPA_11 | MEDIA | DT-015-001 V3_02 |
| FUT.48 | SandboxManager warm pool dinamico por demanda | CAPA_11 | MEDIA | DT-015-004 V3_02 |
| FUT.49 | tool_call delegation via SubQ — path async completo | CAPA_11 | MEDIA | DT-016-001 V3_02 |
| FUT.50 | Consolidacion semantica de spans (merger CAPA_05/10) | CAPA_10 | BAJA | post-RES.157 |
| FUT.51 | Payment Dispatcher multi-rail avanzado (Lightning) | CAPA_07/12 | BAJA | RES.156 extension |
| FUT.52 | Self-Evolving Code con HITL ASL-3 (formal) | CAPA_04 | BAJA | FUT.32 inversion |

**Pendientes de migracion (no FUT — tareas operativas):**
- FUT-V4-07: Script migracion batch namespace V3→V4 (ECS) — bajo RES.158
- FUT-V4-09: Auditoria namespaces CAPA_08 post-migracion — bajo RES.158
- FUT-V4-10: Eliminacion archivos BORRAR_* en zzz_relay/ + resoluciones/ (15 archivos) — tarea manual

**FUT de mayor impacto para inicio V4:** FUT.40-FUT.44 (FlowGRPO + CAPA_03/04 pendientes formalizacion RES).

---

## REGISTRO DE CAMBIOS V4

| ID | Tipo | Descripcion | Autor | Fecha |
|---|---|---|---|---|
| UNIF-001 | Unificacion | Dos versiones ARQUITECTURA_base_V4 unificadas en este archivo | agt1973@gmail.com | 2026-05-23 |
| RES.158 | DT resuelta | Namespace ECS incluye tenant_id — patron canonico V4 (DT-06-01) | agt1973 + ariel.garcia.traba | 2026-05-22 |
| RES.157 | FUT cerrado | OpenInference + QUIC integration — QUICSpanExporter | ariel.garcia.traba | 2026-05-19 |
| RES.156 | FUT cerrado | Payment Dispatcher x402/MPP | ariel.garcia.traba | 2026-05-18 |
| RES.155 | FUT cerrado | Transport Layer eBPF/QUIC — QUICGateway nativo | ai.mpat.designer | 2026-05-18 |
| RELAY_033 | Primer relay V4 | RES.158 + ARQUITECTURA_base_V4 + actualizacion ESTADO_CIERRE | agt1973@gmail.com | 2026-05-22 |
| V4-INIT | Inicio ciclo | ARQUITECTURA_base_V4 generada desde V3_03 + auditoria cierre | ariel.garcia.traba | 2026-05-22 |

---

## PENDIENTES DE INVESTIGACION (deuda tecnica documentada)

| ID | Descripcion | Impacto | Estado |
|---|---|---|---|
| DT-UNIF-001 | Verificar si FUT.40 (FlowGRPO completo) requiere su propia RES o va bajo RES.159 junto con AgentCard | ALTA — define numeracion RES | Pendiente decision docente |
| DT-UNIF-002 | Confirmar que FUT.41-44 se procesan en ese orden o si tienen dependencias entre si | ALTA — roadmap V4 | Pendiente |
| DT-UNIF-003 | FUT-V4-07 (script batch namespace) — validar si se hace en Python o Rust | MEDIA | Pendiente |

---

*ARQUITECTURA_base_V4_UNIF.md · V4 UNIFICADO · AGT 2026-05-23*
*Fuentes: 1cyg9BLUeSi4VUJWVVpvVxG_j2JOMeuX9 + 1dpYcf1OjLwyFOr9oc6SLvFPzgClgd1dZ*
*que has usado el formato de razonamiento adaptado por AGT_2026*
