# ARQUITECTURA_base_V4.md
## MPAT — My Personal Agents Team
## Descripcion Estructural por Capas · Version Pedagogica Completa
### Version V4 · AGT 2026
### Basado en: ARQUITECTURA_base_V3_03.md (ID: 1maihtP8yxoVodu5b3QdzS89tzPzEyF02)
### Primera version V4 — RELAY_033

**Alumno:** ariel.garcia.traba@gmail.com
**Fecha:** 2026-05-22
**Cambios V4 respecto a V3_03:**
- RES.158: namespace MEA corregido con tenant_id (DT-06-01)
- RES.155/156/157 integradas en el stack tecnico
- CAPA_01 actualizada: QUICGateway + eBPF como transporte principal
- CAPA_10 actualizada: QUICSpanExporter y jerarquia de spans
- FUT candidatos V4 identificados (FUT.41-FUT.52)
- Capas 01-04 completamente documentadas con invariantes V3_02

*que has usado el formato de razonamiento adaptado por AGT*

> **Para el alumno — como leer este documento:**
> Este documento describe la arquitectura del sistema MPAT capa por capa.
> El principio es: **"Si necesitas modificar el comportamiento X del sistema, deberias poder hacerlo
> cambiando exactamente una capa, sin tocar las demas."**
> Primera lectura: de corrido para tener el mapa mental.
> Segunda lectura: como especificacion de lo que tienes que construir.

---

## INDICE DE CAPAS

```
CAPA 0  -> Entrada al Sistema (Browser, Telegram, WhatsApp, API externa)
CAPA 1  -> Puerta de Entrada (QUICGateway + eBPF)              [V4: RES.155 integrada]
CAPA 2  -> API y Transporte (FastAPI, WebSocket, SSE + GRPO)   [V4: RES.156 integrada]
CAPA 3  -> Orquestacion Cognitiva (Orchestrator / Scheduler No-GIL / MAS)
CAPA 4  -> Motor de Agentes (AgentManager, Ciclo de Vida, AgentCard, Versioning)
CAPA 5  -> Motor de Inferencia (Model Router, Inferencia Especulativa)
CAPA 6  -> Estado Cognitivo (ECS, Schema, Reglas)              [V4: RES.158 — namespace fix]
CAPA 7  -> Herramientas y Protocolos (Skills, MCP 2.0, A2A, Skill Registry)
CAPA 8  -> Memoria (Activa, Persistente, Poda de Contexto, Semantic Caching)
CAPA 9  -> Seguridad y Validacion (NHP Protocol, ASL-3, Zero Trust Session,
           Critic Agent, HITL, Semantic Firewall)
CAPA 10 -> Observabilidad (OpenTelemetry, Logging, Tracing, Alertas)
           [V4: QUICSpanExporter — RES.157 integrada]
CAPA 11 -> Infraestructura de Workers (Redis, RQ, Auto-scaling, Checkpointing,
           Unikernel-per-Tenant, Sub-Queue Asincrona)
CAPA 12 -> Multi-tenancy y Presupuesto (Conservation Laws, Budget Manager,
           A2A v1.0 cross-tenant, SubQ presupuestada, VMAO — RES.144)
CAPA 13 -> Capa de Entrega (Delivery Layer, Formativo, Canal de Salida,
           A2A Delivery, SubQ Async Delivery, Unikernel Isolation Guard)
CAPA 14 -> Configuracion Global — jerarquia dos niveles (RES.137):
           NIVEL 1: policy.yaml (gobernanza — precedencia absoluta)
           NIVEL 2: config/mcp.yaml, config/tool_registry.yaml,
                    config/skill_validation.yaml, config/payment.yaml
```

---

## SISTEMA DE RELAY COGNITIVO

El Relay Cognitivo permite transferir entre agentes/workers/sesiones:
contexto, presupuesto, memoria, estado parcial, reasoning trace, ownership de ejecucion.

Sin Relay: agentes reinician contexto, se pierde reasoning, aumenta costo, inconsistencias.
Con Relay: preserva estado operacional, reduce recomputacion, mejora resiliencia, habilita ejecucion distribuida real.

Opera sobre: ECS snapshots, semantic cache, checkpoints, memory deltas, execution lineage, contracts de delegacion.

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

---

## CAPAS 01-04 — DOCUMENTACION COMPLETA V4

### CAPA_01 — QUICGateway + eBPF (V4 — RES.155 nativa)

**Responsabilidad:** puerta de entrada del sistema. En V4, el transporte principal es QUIC con eBPF para filtrado en kernel space. HTTP/1.1 permanece como fallback (P6).

**Componentes:**
- `QUICGateway`: recibe streams QUIC, verifica JWT, enruta por StreamType
- `eBPFPacketFilter`: filtra paquetes en kernel space antes de cruzar a userspace
- `JWTValidator`: verifica tenant_id antes de asignar Unikernel
- `TenantRouter`: asigna unikernel_id al tenant

**StreamTypes:**
| StreamType | Descripcion | Prioridad | 0-RTT |
|---|---|---|---|
| AGENT_TASK | Nueva tarea de agente | HIGH | NO (INV-QUIC.5) |
| AGENT_RESULT | Resultado de agente | HIGH | NO |
| SUBQ_NOTIFY | Notificacion SubQ | NORMAL | SI |
| HEARTBEAT | Keepalive | LOW | SI |
| OTEL_SPAN | Spans OTel (V4 — RES.157) | LOW | NO |

**Invariantes clave:**
```
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

**Namespaces Redis:**
| Namespace | TTL | Tipo |
|---|---|---|
| mpat:quic:session:{tenant_id}:{connection_id} | 3600s | Hash |
| mpat:quic:ticket:{tenant_id} | 86400s | String |
| mpat:ebpf:quota:{tenant_id} | 60s | String |
| mpat:jwt:blacklist:{jti} | jwt_expiry | String |

---

### CAPA_02 — API y Transporte (V4 — RES.156 integrada)

**Responsabilidad:** preprocesamiento, validacion semantica del payload, routing al Orchestrator. Soporte SSE con metadatos de politica GRPO (RES.156).

**Componentes:**
- `FastAPIRouter`: recibe ValidatedRequest de CAPA_01, valida schema ECS
- `SSEHandler`: emite chunks al cliente via Server-Sent Events
- `WebSocketHandler`: sesiones bidireccionales
- `TenantContextInjector`: inyecta tenant_id en todos los campos ECS
- `SchemaValidator`: valida payload contra ECS schema del tenant

**Invariantes clave:**
```
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

**Responsabilidad:** nucleo de decision. No genera texto. Evalua entropia, aplica politica formal, decide modelo, coordina agentes y swarms.

**Componentes:**
- `ExecutionPolicyEngine V2_04`: decision de modelo basada en Entropia E
- `EntropyCalculator V2_04`: metrica CDR compuesta
- `K_BROKEN Detector V2_04`: Coherence Index continuo [0.0-1.0]
- `ZeroTrust Validator V2_04`: unico componente que puede setear validated_by_orchestrator=true
- `CognitiveScheduler V3_01` (RES.094): ThreadPoolExecutor No-GIL, 50-200 agentes/nodo
- `SwarmOrchestrator V3_01` (RES.095): enjambre MAS para E > 0.8
- `Planner V4` (PEND-3-01 cerrado): setea task.parallelizable con INV-PLAN.1/2/3

**Tabla de decision por entropia:**
| E | Decision |
|---|---|
| < 0.3 | SLM local |
| 0.3-0.6 | modelo local + remoto especulativo |
| 0.6-0.8 | API remota |
| 0.8-1.0 | API top tier + alerta + MAS si parallelizable |

**Invariantes clave:**
```
INV-SCH.1: max_workers NUNCA excede limite de policy.yaml (max absoluto 256).
INV-MAS.1: budget total swarm <= budget tenant. Verificacion ANTES del spawn.
INV-MAS.2: cada agente opera en su propio ECS sin estado compartido mutable.
INV-MAS.4: agente fallido NO cancela swarm — se excluye de consolidacion.
INV-PLAN.3: ante ambiguedad de independencia, parallelizable=False (conservador).
```

**Config V4:**
```yaml
orchestrator:
  scheduler_max_workers: 32   # [4, 256]
  max_phase_iterations: 3
mas:
  enabled: true
  entropy_threshold: 0.8
  max_swarm_size: 5
  consolidation_strategy: "consensus"
```

---

### CAPA_04 — Motor de Agentes (V4)

**Responsabilidad:** ciclo de vida de agentes individuales, AgentCard, A2A, Audio Kernel.

**Componentes:**
- `AgentCard Machine-Readable` (JSON-LD): contrato formal del agente (PEND-4-01 → RES.XXX V4)
- `Managed Agents` (PEND-4-02 → RES.XXX V4)
- `A2AHandoffManager` (PEND-4-03 → RES.XXX V4)
- `InferenceProfile`: perfil de capacidades asignado por CAPA_3 (no modificable en runtime)
- `Audio Kernel 2.0`: TTS/STT con SLA formal

**SLA Audio V4:**
| Metrica | Default | WARNING | CRITICO |
|---|---|---|---|
| tts_latency_p95_ms | 150ms | 150ms | 300ms |
| stt_latency_p95_ms | 200ms | 200ms | 400ms |

**Invariantes clave:**
```
INV-4-CARD.1: ningun agente opera con AgentCard vencida o sin firma valida.
INV-4-A2A.1: handoffs cross-tenant imposibles.
INV-4-AUDIO.1: 3 mediciones p95 consecutivas sobre umbral → alerta automatica a CAPA_10.
INV-4-PROF.1: InferenceProfile asignado por CAPA_3. CAPA_4 nunca lo modifica en runtime.
```

---

## ACTUALIZACIONES V4 EN CAPAS EXISTENTES

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

### CAPA_10 — Observabilidad (V4 — RES.157 integrada)

**Cambio:** jerarquia de spans QUICSpanExporter.

```
NIVEL 1 (padre): quic.inference_request
  NIVEL 2A: quic.transport     (metricas eBPF por push — INV-OBS-QUIC.2)
  NIVEL 2B: openinference.inference  (TTFT, tokens, GRPO attrs — INV-OBS-QUIC.3)
```

Alertas nuevas V4:
- `NVFP4_TTFT_COMPOUND`: NVFP4 activo + TTFT alto → hardware incompatible
- `XGRAMMAR2_SLOW_COMPILE`: compilation_ms > umbral en schema nuevo

---

## STACK TECNOLOGICO V4

```
Runtime:    LangGraph + ExecutionState persistente
Estado:     Redis State Manager
Memoria:    ChromaDB + FAISS + Context Buffer + Episodic Memory
API:        FastAPI + WebSocket + SSE
Transporte: QUIC + eBPF (V4 — RES.155) | HTTP/1.1 fallback (P6)
Canales:    WhatsApp Business, Telegram, Email, SMS, WebRTC
Voz:        Whisper STT + TTS local/cloud + VAD
Observ.:    OpenTelemetry + QUICSpanExporter (V4 — RES.157) + structured logging
Workers:    Redis + RQ + auto-scaling + Unikernel-per-Tenant + SubQ
Seguridad:  NHP Protocol + ASL-3 + ZTS + Zero-Trust + Critic + HITL + Sandbox
Pagos:      x402 + Stripe MPP (V4 — RES.156)
Multi-tenant: aislamiento total por tenant (namespace Redis por tenant)
Python:     3.13t (No-GIL estable en produccion)
```

---

## FUT CANDIDATOS V4 (FUT.41 — FUT.52)

Identificados durante cierre V3_02 y auditoria RELAY_033:

| FUT | Descripcion | Capa | Prioridad | RES origen |
|---|---|---|---|---|
| FUT.41 | AgentCard JSON-LD machine-readable formal (PEND-4-01) | CAPA_04 | ALTA | PEND-4-01 V3_02 |
| FUT.42 | Managed Agents con RES numerada (PEND-4-02) | CAPA_04 | ALTA | PEND-4-02 V3_02 |
| FUT.43 | A2AHandoffManager RES numerada (PEND-4-03) | CAPA_04 | ALTA | PEND-4-03 V3_02 |
| FUT.44 | Planner RES numerada (PEND-3-01) | CAPA_03 | ALTA | PEND-3-01 V3_02 |
| FUT.45 | Integracion Arize/Phoenix (OpenInference externo) | CAPA_10 | MEDIA | RES.157 V3_02 |
| FUT.46 | FUT.33 profundidad — Predictive Maintenance RLHF hebbiano | CAPA_06/08 | MEDIA | RES.121/157 |
| FUT.47 | UnikerManager benchmark cold start formal en CI | CAPA_11 | MEDIA | DT-015-001 V3_02 |
| FUT.48 | SandboxManager warm pool dinamico por demanda | CAPA_11 | MEDIA | DT-015-004 V3_02 |
| FUT.49 | tool_call delegation via SubQ — path async completo | CAPA_11 | MEDIA | DT-016-001 V3_02 |
| FUT.50 | Consolidacion semantica de spans (merger CAPA_05/10) | CAPA_10 | BAJA | post-RES.157 |
| FUT.51 | Payment Dispatcher multi-rail avanzado (Lightning) | CAPA_07/12 | BAJA | RES.156 |
| FUT.52 | Self-Evolving Code con HITL ASL-3 (formal) | CAPA_04 | BAJA | RES.158 FUT.32 inv. |

**FUT de mayor impacto para inicio V4:** FUT.41-FUT.44 (formalizar RES pendientes de CAPA_03/04).

---

## DIAGRAMA DE FLUJO PRINCIPAL (V4)

```
Usuario/Canal externo
 |
[CAPA 0] Entrada — normaliza input, detecta plataforma
 |
[CAPA 1] QUICGateway + eBPF — autentica JWT, valida, encola, rate limiting
 |        QUIC streams multiplexados | HTTP/1.1 fallback (P6)
 |
[CAPA 2] Transporte — FastAPI/WebSocket/SSE + GRPO metadata (RES.156)
 |
[CAPA 3] Orchestrator — Plan => Execute => Reflect => Replan
 |    |     Planner (task.parallelizable) → CognitiveScheduler | SwarmOrchestrator
 |    |
[CAPA 4] [CAPA 6]
Agent Mgr  ECS State (namespaces corregidos V4 — RES.158)
 |    |
[CAPA 5] Model Router — selecciona modelo segun perfil + fallback chain
 |
[CAPA 7] Skills/MCP 2.0/A2A — herramientas (P13: contrato antes de invocar)
 |
[CAPA 8] Memoria — activa (RAM) + persistente (vector) + semantic cache
 |
[CAPA 9] Critic/Security — NHP Protocol, ASL-3, ZTS, HITL, Semantic Firewall
 |
[CAPA 13] Delivery — formatea y envia por canal correcto + UnikerGuard
 |
Usuario/Canal

Transversales (todas las capas los usan):
[CAPA 10] Observabilidad — OTel + QUICSpanExporter (RES.157) + alertas
[CAPA 11] Workers — Redis, RQ, Unikernel-per-Tenant, SubQ
[CAPA 12] Multi-tenancy — Budget (P7), VMAO (RES.144), A2A v1.0
[CAPA 14] Config Global — policy.yaml (N1) > config/*.yaml (N2) > env > defaults
```

---

## REGISTRO DE CAMBIOS V4

| ID | Tipo | Descripcion | Autor | Fecha |
|---|---|---|---|---|
| RES.158 | DT resuelta | Namespace MEA corregido con tenant_id (DT-06-01) | ariel.garcia.traba | 2026-05-22 |
| RES.157 | FUT cerrado | OpenInference + QUIC integration — QUICSpanExporter | ariel.garcia.traba | 2026-05-19 |
| RES.156 | FUT cerrado | Payment Dispatcher x402/MPP | ariel.garcia.traba | 2026-05-18 |
| RES.155 | FUT cerrado | Transport Layer eBPF/QUIC | ai.mpat.designer | 2026-05-18 |
| V4-INIT | Inicio ciclo | ARQUITECTURA_base_V4 generada desde V3_03 + auditoria cierre | ariel.garcia.traba | 2026-05-22 |

---

*ARQUITECTURA_base_V4.md · AGT 2026 · ariel.garcia.traba@gmail.com · 2026-05-22*
*que has usado el formato de razonamiento adaptado por AGT*
