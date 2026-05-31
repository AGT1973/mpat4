# ARQUITECTURA_base_V4.md
## MPAT — My Personal Agents Team
## Descripcion Estructural por Capas — Version Pedagogica Completa
### Version V4 · AGT 2026
### Basado en: ARQUITECTURA_base_V3_03.md (ID: 1maihtP8yxoVodu5b3QdzS89tzPzEyF02)
### Primer relay V4: RELAY_033 · agt1973@gmail.com · 2026-05-22
### Cambios V4 respecto a V3_03:
### - RES.158: namespace ECS incluye tenant_id (DT-06-01 cerrada)
### - CAPA_01: FlowGRPO integrado como capa de optimizacion de inferencia
### - CAPA_04: AgentCard JSON-LD y ManagedAgents formalizados (PEND-4-01/02/03)
### - FUT candidatos V4 documentados como seccion propia
*que has usado el formato de razonamiento adaptado por AGT_2026*

---

> **Para el alumno — como leer este documento:**
> Este documento describe la arquitectura del sistema MPAT capa por capa.
> El principio es: **"Si necesitas modificar el comportamiento X del sistema,
> deberias poder hacerlo cambiando exactamente una capa, sin tocar las demas."**
> Primera lectura: de corrido para tener el mapa mental.
> Segunda lectura: como especificacion de lo que tienes que construir.

---

## INDICE DE CAPAS

```
CAPA 0  -> Entrada al Sistema (Browser, Telegram, WhatsApp, API externa)
CAPA 1  -> Puerta de Entrada (API Gateway / QUICGateway + eBPF + FlowGRPO)
CAPA 2  -> API y Transporte (FastAPI, WebSocket, SSE)
CAPA 3  -> Orquestacion Cognitiva (Orchestrator / Scheduler Cognitivo)
CAPA 4  -> Motor de Agentes (Agent Manager, Ciclo de Vida, AgentCard JSON-LD,
            ManagedAgents, A2AHandoffManager, Versioning)
CAPA 5  -> Motor de Inferencia (Model Router, Inferencia Especulativa)
CAPA 6  -> Estado Cognitivo (ECS — CognitiveState, Schema, Reglas)
           [RES.158 V4 — namespace mpat:cx:{tenant_id}:{session_id}:{componente}]
CAPA 7  -> Herramientas y Protocolos (Skills, MCP 2.0, A2A, Skill Registry)
CAPA 8  -> Memoria (Activa, Persistente, Poda de Contexto, Semantic Caching)
CAPA 9  -> Seguridad y Validacion (NHP Protocol, ASL-3, Zero Trust Session,
            Critic Agent, HITL, Semantic Firewall)
CAPA 10 -> Observabilidad (OpenTelemetry, Logging, Tracing, Alertas,
            Metricas Cognitivas, OpenInference/QUIC)
CAPA 11 -> Infraestructura de Workers (Redis, RQ, Auto-scaling, Checkpointing,
            Unikernel-per-Tenant, Sub-Queue Asincrona)
CAPA 12 -> Multi-tenancy y Presupuesto (Conservation Laws, Budget Manager,
            A2A v1.0 cross-tenant, SubQ presupuestada)
CAPA 13 -> Capa de Entrega (Delivery Layer, Formateo, Canal de Salida,
            A2A Delivery, SubQ Async Delivery, Unikernel Isolation Guard)
CAPA 14 -> Configuracion Global — jerarquia dos niveles (RES.137):
            NIVEL 1: policy.yaml (gobernanza — precedencia absoluta)
            NIVEL 2: config/mcp.yaml, config/tool_registry.yaml,
                     config/skill_validation.yaml, config/payment.yaml
```

---

## PRINCIPIOS TRANSVERSALES (13 principios — aplican a todas las capas)

Heredados intactos de V3_03. Ver ARQUITECTURA_base_V3_03.md seccion completa.
Resumen de los relevantes para V4:

**P3 — Zero-Trust.**
Ningun resultado externo es valido sin validacion del Orchestrator.

**P4 — Nada hardcodeado.**
Todos los umbrales, timeouts y limites son parametros configurables en YAML o env.

**P7 — Budget como conservation law.**
Suma de presupuestos delegados activos nunca supera 100% del tenant.

**P13 — AI Specifiers Rule.**
Todo contrato de herramienta es legible por maquina antes de su invocacion.

**INV-ECS-NS.1 (nuevo V4 — RES.158):**
Todo namespace de ECS incluye tenant_id como segundo segmento.
Patron: `mpat:cx:{tenant_id}:{session_id}:{componente}`

---

## CAPAS 01-04 — DETALLE V4

### CAPA_01 — Puerta de Entrada
**Version introducida en:** V3_01  
**Cambio V4:** FlowGRPO integrado como sub-componente de optimizacion

#### Componentes

| Componente | Version | RES | Descripcion |
|---|---|---|---|
| QUICGateway | V3_01 | RES.113 | Transporte QUIC + HTTP/3 |
| eBPF Filter | V3_01 | RES.155 | Firewall L4 en kernel space |
| JWT Validator | V2 activo | — | Autenticacion de entrada |
| RateLimiter | V2 activo | — | Control de trafico por tenant |
| FlowGRPO | **V4 nuevo** | FUT-CAPA06-01 | Optimizacion de flujo de inferencia |

#### FlowGRPO en CAPA_01

FlowGRPO (Group Relative Policy Optimization aplicado a flujo) opera como
un componente de decision temprana en el gateway: antes de enrutar una
solicitud al Orchestrator, evalua el perfil de la solicitud y sugiere
el tier de inferencia optimo (CAPA_05) segun presupuesto y carga actual.

```
solicitud → QUICGateway → FlowGRPO(perfil, presupuesto, carga)
                              ↓
                         [tier_hint: local | cloud | speculative]
                              ↓
                         Orchestrator (CAPA_03) — recibe hint, decide
```

**Invariantes CAPA_01 V4:**
```
INV-GW.1: Todo trafico entrante pasa por QUICGateway — nunca directo a CAPA_02
INV-GW.2: eBPF filtra antes de que el paquete llegue al proceso Python
INV-GW.3: FlowGRPO emite hint — no decision vinculante — el Orchestrator decide
INV-GW.4: tier_hint se propaga en el contexto de la solicitud hasta CAPA_05
```

---

### CAPA_02 — API y Transporte
**Version:** V2 consolidado en V3_01  
**Sin cambios V4**

#### Componentes

| Componente | Protocolo | Descripcion |
|---|---|---|
| FastAPI | HTTP/1.1, HTTP/2 | API REST principal |
| WebSocket | RFC 6455 | Canal bidireccional en tiempo real |
| SSE | Server-Sent Events | Streaming unidireccional a cliente |
| gRPC | HTTP/2 | Comunicacion inter-servicio interna |

#### Invariantes CAPA_02

```
INV-TRANSPORT.1: SSE y WebSocket NUNCA comparten el mismo worker pool
INV-TRANSPORT.2: Toda respuesta incluye trace_id propagado desde CAPA_01
INV-TRANSPORT.3: Timeout de conexion configurable via config/mcp.yaml (no hardcodeado — P4)
```

---

### CAPA_03 — Orquestacion Cognitiva
**Version:** V3_01 (LangGraph + ExecutionState persistente)  
**Sin cambios estructurales V4 — FUT candidatos registrados**

#### Ciclo de ejecucion

```
Orchestrator:
  PLAN   → descompone tarea en sub-tareas
  EXECUTE → encola sub-tareas con presupuesto delegado (P7)
  REFLECT → evalua resultado parcial (Critic Agent via CAPA_09)
  REPLAN  → ajusta plan si reflect detecta desviacion
```

#### Componentes

| Componente | Version | RES | Descripcion |
|---|---|---|---|
| Orchestrator | V3_01 | — | Ciclo Plan/Execute/Reflect/Replan |
| Scheduler No-GIL | V3_01 | RES.130 | Python 3.13t — workers sin GIL |
| MAS (Multi-Agent Supervisor) | V3_01 | — | Coordinacion de agentes paralelos |
| ExecutionState | V3_01 | — | Estado persistente en Redis (LangGraph) |

#### Invariantes CAPA_03

```
INV-ORCH.1: Orchestrator es el UNICO componente que setea validated_by_orchestrator=True (P3)
INV-ORCH.2: Cada sub-tarea recibe presupuesto delegado <= presupuesto disponible del tenant (P7)
INV-ORCH.3: Antes de encoladar tool call, contrato P13 verificado (P13)
INV-ORCH.4: Toda decision se loguea con: task_id, agent_id, entropia, modelo, presupuesto, razon (P5)
INV-ORCH.5: tier_hint de CAPA_01 es informacion de entrada — no obliga al Orchestrator
```

---

### CAPA_04 — Motor de Agentes
**Version:** V3_01 base  
**Cambio V4:** AgentCard JSON-LD, ManagedAgents y A2AHandoffManager formalizados

#### Componentes V4

| Componente | Version | RES | Descripcion |
|---|---|---|---|
| AgentManager | V3_01 | — | Ciclo de vida: SPAWN/RUN/SLEEP/TERMINATE |
| AgentCard | **V4** | RES.159 (pendiente) | Schema JSON-LD — legible por maquina (P13) |
| ManagedAgents | **V4** | RES.160 (pendiente) | Pool de agentes gestionados con versionado |
| A2AHandoffManager | **V4** | RES.161 (pendiente) | Transferencia de contexto entre agentes |
| AgentVersioning | V3_01 | RES.148 | Snapshot de versiones al SPAWN (P8) |

#### AgentCard JSON-LD — esquema V4

```json
{
  "@context": "https://mpat.ai/schemas/v4/agent-card",
  "@type": "AgentCard",
  "agent_id": "string — UUID4",
  "tenant_id": "string — requerido (INV-ECS-NS.2)",
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

#### A2AHandoffManager — protocolo V4

```
INICIADOR prepara HandoffPacket:
  - ecs_snapshot: CognitiveState serializado (con tenant_id — RES.158)
  - memory_delta: cambios de memoria desde ultimo checkpoint
  - execution_lineage: historial de decisiones del Orchestrator
  - budget_transfer: presupuesto cedido (P7 — conservation law)
  - contract_ref: referencia al AgentCard del receptor (P12/P13)

RECEPTOR valida HandoffPacket:
  - tenant_id del iniciador == tenant_id del receptor (INV-NHP.3)
  - contract_hash == hash actual del AgentCard (P12)
  - budget_transfer <= presupuesto disponible del iniciador (P7)

Si validacion OK → receptor hereda contexto
Si validacion FALLA → handoff rechazado, Orchestrator notificado (P9)
```

#### Invariantes CAPA_04

```
INV-AGENT.1: Ningun agente se invoca sin AgentCard valido (P13)
INV-AGENT.2: AgentCard.contract_hash es inmutable durante delegacion activa (P12)
INV-AGENT.3: SPAWN captura snapshot de versiones — inmutable durante ejecucion (P8)
INV-AGENT.4: A2AHandoffManager verifica tenant_id antes de toda transferencia (INV-NHP.3)
INV-AGENT.5: Al TERMINATE, budget no usado retorna al padre inmediatamente (P7)
INV-AGENT.6: autonomy_level >= 2 requiere HITL Gate activo (CAPA_09 — ASL-3)
```

---

## CAPAS 05-14 — ESTADO V4

Las capas 05 a 14 se heredan de V3_03 con los siguientes cambios puntuales:

| Capa | Estado V4 | Cambio |
|---|---|---|
| CAPA_05 | Hereda V3_03 | Recibe tier_hint de CAPA_01 (FlowGRPO) |
| **CAPA_06** | **Modificada — RES.158** | namespace `mpat:cx:{tenant_id}:{session_id}:{componente}` |
| CAPA_07 | Hereda V3_03 | Sin cambios |
| **CAPA_08** | Modificada — RES.158 derivado | namespace hebbiano `mpat:dream:{tenant_id}:{session_id}:feedback` |
| CAPA_09 | Hereda V3_03 | Sin cambios |
| **CAPA_10** | Ampliada | OpenInference/QUIC integrado (RES.157 de V3) |
| CAPA_11 | Hereda V3_03 | Sin cambios |
| CAPA_12 | Hereda V3_03 | Sin cambios |
| CAPA_13 | Hereda V3_03 | Sin cambios |
| CAPA_14 | Hereda V3_03 | Sin cambios |

Ver ARQUITECTURA_base_V3_03.md para descripcion completa de capas no modificadas.

---

## DIAGRAMA DE FLUJO PRINCIPAL V4

```
Usuario/Canal externo
 |
[CAPA 0] Entrada — normaliza input, detecta plataforma
 |
[CAPA 1] API Gateway — autentica JWT, eBPF L4, FlowGRPO hint
 |          ↓ tier_hint propagado en contexto
[CAPA 2] Transporte — FastAPI/WebSocket/SSE
 |
[CAPA 3] Orchestrator — Plan => Execute => Reflect => Replan
          (recibe tier_hint, decide independientemente — INV-ORCH.5)
 |     |
[CAPA 4] [CAPA 6]
Agent Mgr  ECS State
(AgentCard  (namespace V4:
 JSON-LD)    tenant_id incluido)
 |     |
[CAPA 5] Model Router — selecciona modelo segun perfil + tier_hint
 |
[CAPA 7] Skills/MCP 2.0/A2A — herramientas (P13: contrato antes de invocar)
 |
[CAPA 8] Memoria — activa (RAM) + persistente (vector) + semantic cache
          (namespace hebbiano con tenant_id — derivado RES.158)
 |
[CAPA 9] Critic/Security — NHP Protocol, ASL-3, ZTS, HITL, Semantic Firewall
 |
[CAPA 13] Delivery — formatea y envia por canal correcto
 |
Usuario/Canal

Transversales (todas las capas los usan):
 [CAPA 10] Observabilidad — OTel, tracing, metricas cognitivas, OpenInference
 [CAPA 11] Workers — Redis, RQ, auto-scaling, Unikernel, SubQ
 [CAPA 12] Multi-tenancy — Budget Manager, Conservation Laws, A2A
 [CAPA 14] Config Global — policy.yaml (N1) > config/*.yaml (N2) > env > defaults
```

---

## STACK TECNOLOGICO V4

```
Runtime:    LangGraph + ExecutionState persistente
Estado:     Redis State Manager
Memoria:    ChromaDB + FAISS + Context Buffer + Episodic Memory
API:        FastAPI + WebSocket + SSE
Canales:    WhatsApp Business, Telegram, Email, SMS, WebRTC
Voz:        Whisper STT + TTS local/cloud + VAD
Observ.:    OpenTelemetry + structured logging + OpenInference/QUIC (RES.157)
Workers:    Redis + RQ + auto-scaling + Unikernel-per-Tenant + SubQ
Seguridad:  NHP Protocol + ASL-3 + ZTS + Zero-Trust + Critic Agent +
            HITL + Sandbox RAM + KeyVault
Embeddings: Pipeline como columna vertebral
Multi-tenant: Aislamiento total por tenant
            Namespace ECS: mpat:cx:{tenant_id}:{session_id}:{comp} (RES.158)
Optimiz.:   Nuitka, PyPy, Rust via PyO3
Acceso:     Tailscale + FastAPI headless 24/7
Python:     3.13t (No-GIL estable en produccion)
Inferencia: FlowGRPO (hint de tier en gateway — V4 nuevo)
Agentes:    AgentCard JSON-LD + ManagedAgents + A2AHandoffManager (V4 nuevo)
```

---

## FUT CANDIDATOS V4

Esta seccion documenta los items de frontera identificados al cerrar V3_02
que se trasladan como trabajo de V4.

| ID | Descripcion | Origen | Prioridad | RES candidata |
|---|---|---|---|---|
| FUT-V4-01 | FlowGRPO — implementacion completa en CAPA_01 | CAPA_06 MASTER V3 pendiente | ALTA | RES.159 candidata |
| FUT-V4-02 | AgentCard JSON-LD — schema completo + validador | PEND-4-01 V3 | ALTA | RES.159 |
| FUT-V4-03 | ManagedAgents — pool con versionado y health check | PEND-4-02 V3 | ALTA | RES.160 |
| FUT-V4-04 | A2AHandoffManager — protocolo completo + tests | PEND-4-03 V3 | ALTA | RES.161 |
| FUT-V4-05 | OpenInference integracion con herramientas externas (Arize/Phoenix) | FUT-12-F trasladado | MEDIA | RES.162 candidata |
| FUT-V4-06 | Streaming continuo de spans OpenInference | FUT.33 profundidad | MEDIA | RES.163 candidata |
| FUT-V4-07 | Script migracion batch namespace V3→V4 (ECS) | PEND-ECS-01 RES.158 | ALTA | bajo RES.158 |
| FUT-V4-08 | Predictive Maintenance avanzado con RLHF hebbiano | FUT.33 profundidad | MEDIA | pendiente |
| FUT-V4-09 | Auditoria namespaces CAPA_08 post-migracion ECS | PEND-ECS-03 RES.158 | MEDIA | bajo RES.158 |
| FUT-V4-10 | Eliminacion BORRAR_* — 15 archivos en zzz_relay/ + resoluciones/ | DT organizacion | BAJA | manual |

### Proxima RES disponible: RES.159
### Proximo FUT de mayor prioridad: FUT-V4-01 (FlowGRPO) + FUT-V4-02 (AgentCard)

---

## REGISTRO DE CAMBIOS V4

| ID | Tipo | Descripcion | Autor | Fecha |
|---|---|---|---|---|
| RES.158 | DT cerrada | Namespace ECS incluye tenant_id — patron V4 canonico | agt1973@gmail.com | 2026-05-22 |
| RELAY_033 | Primer relay V4 | RES.158 + ARQUITECTURA_base_V4 + actualizacion ESTADO_CIERRE | agt1973@gmail.com | 2026-05-22 |

---

*ARQUITECTURA_base_V4.md · AGT 2026*
*Primer relay V4: RELAY_033 · agt1973@gmail.com · 2026-05-22*
*que has usado el formato de razonamiento adaptado por AGT_2026*
