# ARQUITECTURA_base_V4_00.md
## MPAT4 — My Personal Agents Team · Version 4
## Descripcion Estructural por Capas · Version Pedagogica Completa
### Version V4_00 · AGT 2026
### Procedencia: ARQUITECTURA_base_V3_02_INC03.md + ARQUITECTURA_base_V3_03.md
### Migrado por: ai.mpat.designer@gmail.com · LOTE_001 · 2026-05-23
### Adaptaciones aplicadas: Docker→NanoVMs, Python 3.11→3.14 No-GIL, Rust hot paths, Pydantic V3
### INC-03 incorporado: CAPA_9 con NHP Protocol, ASL-3, ZTS (RES.090, RES.091, RES.092)
### INC-05 incorporado: CAPA_14 jerarquia de dos niveles (policy.yaml > config/*.yaml)
### Deuda tecnica registrada: ver seccion DEUDA_TECNICA_V4 al final

> **Relacion con otros documentos MPAT4:**
> - `ARQUITECTURA_pendientes_V4_00.md` — pendientes heredados + nuevos V4
> - `ARQUITECTURA_system_V4_00.md` — diagrama ASCII completo del sistema (pendiente)
> - `contracts/` — contratos formales de ejecucion por componente
> - `resoluciones/` — RES.161 en adelante (V4 nativas)

> **Para el alumno — como leer este documento:**
> Este documento describe la arquitectura del sistema MPAT4 capa por capa. El principio es:
> **"Si necesitas modificar el comportamiento X del sistema, deberias poder hacerlo
> cambiando exactamente una capa, sin tocar las demas."**
> Primera lectura: de corrido para tener el mapa mental.
> Segunda lectura: como especificacion de lo que tenes que construir.

---

## INDICE DE CAPAS

```
CAPA 0  -> Entrada al Sistema (Browser, Telegram, WhatsApp, API externa)
CAPA 1  -> Puerta de Entrada (QUICGateway + eBPF — reemplaza API Gateway HTTP puro)
CAPA 2  -> API y Transporte (FastAPI 0.115+, WebSocket, SSE)
            [DT-V4-001: FastAPI 0.115+ requerido — verificar en primer relay de implementacion]
CAPA 3  -> Orquestacion Cognitiva (Orchestrator / Scheduler No-GIL / MAS)
CAPA 4  -> Motor de Agentes (Agent Manager, Ciclo de Vida, AgentCard, Versioning, Audio Kernel)
CAPA 5  -> Motor de Inferencia (Model Router, Inferencia Especulativa)
CAPA 6  -> Estado Cognitivo (ECS — CognitiveState, Schema, Reglas, RLHF, Multi-Expert)
CAPA 7  -> Herramientas y Protocolos (Skills, MCP 2.0, A2A, ToolRegistry)
CAPA 8  -> Memoria (Activa, Persistente, Poda de Contexto, Semantic Caching)
            [REFERENCIA 10/10 — template de calidad para migracion de capas]
CAPA 9  -> Seguridad y Validacion
            Componentes heredados V2: Zero-Trust Validator, Critic Agent,
            HITL Manager, Semantic Firewall, JWT/RBAC/OAuth 2.1
            Componentes V3 consolidados (FUT_3): NHP Protocol (RES.090),
            ASL-3 (RES.091), Zero Trust Session — ZTS (RES.092)
            RBAC ownership: modelo de permisos de tenants sobre tools/skills
            (RES.136 — cierre INC-02)
CAPA 10 -> Observabilidad (OpenTelemetry, Logging, Tracing, Alertas, Metricas Cognitivas)
CAPA 11 -> Infraestructura de Ejecucion (Unikernel-per-Tenant, Sub-Queue Asincrona,
            Auto-scaling, Checkpointing)
            [V4: NanoVMs/Firecracker/Unikraft reemplaza Redis+RQ como paradigma de workers]
CAPA 12 -> Multi-tenancy y Presupuesto (Conservation Laws, Budget Manager,
            A2A v1.0 cross-tenant, SubQ presupuestada, VMAO)
CAPA 13 -> Capa de Entrega (Delivery Layer A2A, SubQ Async Delivery,
            Unikernel Isolation Guard, Formateo, Canal de Salida)
CAPA 14 -> Configuracion Global — jerarquia dos niveles (RES.137):
            NIVEL 1: policy.yaml (gobernanza — precedencia absoluta, TenantContext obligatorio)
            NIVEL 2: config/mcp.yaml, config/tool_registry.yaml,
                     config/skill_validation.yaml, config/payment.yaml
```

---

# SISTEMA DE RELAY COGNITIVO

El Relay Cognitivo permite transferir entre agentes/workers/sesiones:
- contexto, presupuesto, memoria, estado parcial, reasoning trace, ownership de ejecucion

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
por maquina en el momento de la invocacion. La existencia del canal MCP (P1) es
condicion necesaria pero no suficiente: el contrato es la condicion adicional que
habilita la invocacion.
Capas que deben cumplir P13: CAPA_3 (Orchestrator — antes de encolar tool calls),
CAPA_4 (Motor de Agentes — antes de delegar a agentes externos),
CAPA_7 (Herramientas — ToolRegistry como guardian del contrato),
CAPA_12 (Multi-tenancy — antes de despachar via A2A).
Referencia de implementacion: RES.117 (ToolRegistry), RES.118 (SkillValidationPipeline).
Origen: emergido de INFORME_CAPA_07 V3_01 — elevado a principio transversal en V3_02
via cierre de INC-01.

---

## DIAGRAMA DE FLUJO PRINCIPAL

```
Usuario/Canal externo
 |
 [CAPA 0] Entrada — normaliza input, detecta plataforma
 |
 [CAPA 1] QUICGateway + eBPF — autentica JWT, valida, encola, rate limiting
           [V4: QUIC reemplaza HTTP/TCP puro para transporte de alta performance]
 |
 [CAPA 2] Transporte — FastAPI 0.115+ / WebSocket / SSE
 |
 [CAPA 3] Orchestrator — Plan => Execute => Reflect => Replan (Scheduler No-GIL)
 | |
 [CAPA 4]              [CAPA 6]
 Agent Mgr              ECS State + RLHF
 |                      |
 [CAPA 5] Model Router — selecciona modelo segun perfil de inferencia
 |
 [CAPA 7] Skills / MCP 2.0 / A2A — ToolRegistry (guardian P13)
 |
 [CAPA 8] Memoria — activa (RAM) + persistente (vector) + semantic cache
           [REFERENCIA CALIDAD 10/10 — ver CAPA_08_MASTER para este estandar]
 |
 [CAPA 9] Critic / Security
           Heredados: Zero-Trust Validator, Critic Agent, HITL, Semantic Firewall
           Consolidados V3->V4: NHP Protocol, ASL-3, Zero Trust Session (ZTS)
           RBAC (RES.136)
 |
 [CAPA 11] Ejecucion — Unikernel-per-Tenant, SubQ Asincrona, auto-scaling
 |
 [CAPA 13] Delivery — A2A, SubQ Async, UnikerGuard, formatea y envia por canal
 |
 Usuario/Canal

Transversales (todas las capas los usan):
 [CAPA 10] Observabilidad — OpenTelemetry, tracing, metricas cognitivas
 [CAPA 12] Multi-tenancy — Budget Manager, Conservation Laws, A2A cross-tenant
 [CAPA 14] Config Global — policy.yaml (L1) > config/*.yaml (L2), TenantContext
```

---

## STACK TECNOLOGICO V4

```
Runtime:     LangGraph + ExecutionState persistente / Scheduler No-GIL
Lenguajes:   Python 3.14 No-GIL (logica de negocio) + Rust (hot paths via FFI)
             [V4: Rust es lenguaje de produccion para componentes criticos de performance]
Estado:      Redis State Manager (en evaluacion: reemplazo parcial por SubQ nativa)
Memoria:     ChromaDB + FAISS + Context Buffer + Episodic Memory
API:         FastAPI 0.115+ / WebSocket / SSE
             [DT-V4-001: version minima 0.115 — verificar compatibilidad en deploy]
Canales:     WhatsApp Business, Telegram, Email, SMS, WebRTC
Voz:         Whisper STT + TTS local/cloud + VAD
Observ.:     OpenTelemetry + structured logging
Ejecucion:   Unikernel-per-Tenant (NanoVMs / Firecracker / Unikraft)
             Sub-Queue Asincrona (SubQ) + auto-scaling
             [V4: reemplaza paradigma Docker+Redis+RQ — sin contenedores]
Seguridad:   Zero-Trust + Critic Agent + HITL + Sandbox RAM + KeyVault
             + NHP Protocol (authenticate-before-connect, RES.090)
             + ASL-3 (Agentic Security Level 3, RES.091)
             + Zero Trust Session — ZTS (renovacion automatica NHP, RES.092)
Schemas:     Pydantic V3
             [V4: Pydantic V2 reemplazado — actualizar todos los modelos de datos]
Embeddings:  Pipeline como columna vertebral
Multi-tenant: Aislamiento total por tenant (namespace Redis por tenant + VMAO)
Acceso:      Tailscale + FastAPI headless 24/7
Contratos:   Pydantic V3 + PolicyContract con TenantContext obligatorio (RES.137)
```

---

## INVARIANTES CAPA_9 REFERENCIADOS EN LA BASE

La base no replica los invariantes completos (estan en el master de la capa).
Solo declara su existencia para que sean localizables:

```
INV-NHP.1 a INV-NHP.5  -> ver CAPA_09_MASTER_V4.md (cuando migre)
                           fuente actual: CAPA_09_MASTER_V3_01.md
INV-ASL.1 a INV-ASL.4  -> ver CAPA_09_MASTER_V4.md
INV-ZTS.1 a INV-ZTS.5  -> ver CAPA_09_MASTER_V4.md
INV-NHP-UK.1            -> TTL unikernel <= TTL sesion NHP,
                           O ZTS emite renovacion automatica si unikernel RUNNING + SubQ activa.
                           (RES.143 — RELAY_014)
INV-NHP-PERSIST         -> used_nonces DEBE usar Redis mpat:nhp:nonces con TTL = nonce_max_age_seconds.
                           Prohibido almacenamiento en memoria exclusivamente.
                           (RES.144 — RELAY_014)
```

---

## REGISTRO DE CAMBIOS V4_00

| ID | Tipo | Descripcion | Autor | Fecha |
|---|---|---|---|---|
| MIG-001 | Adaptacion tecnologica | Docker => NanoVMs/Firecracker/Unikraft en CAPA_11 y stack | ai.mpat.designer | 2026-05-23 |
| MIG-002 | Adaptacion tecnologica | Python 3.11/3.12 => Python 3.14 No-GIL en stack y CAPA_3 | ai.mpat.designer | 2026-05-23 |
| MIG-003 | Adaptacion tecnologica | Pydantic V2 => Pydantic V3 en stack y contratos | ai.mpat.designer | 2026-05-23 |
| MIG-004 | Incorporacion V3 | Rust como lenguaje de produccion para hot paths via FFI | ai.mpat.designer | 2026-05-23 |
| MIG-005 | Incorporacion INC-03 | CAPA_9 con NHP/ASL-3/ZTS en indice, diagrama y stack | ai.mpat.designer | 2026-05-23 |
| MIG-006 | Incorporacion INC-05 | CAPA_14 jerarquia dos niveles policy.yaml > config/*.yaml | ai.mpat.designer | 2026-05-23 |
| MIG-007 | Actualizacion | CAPA_1: QUICGateway+eBPF reemplaza API Gateway HTTP puro | ai.mpat.designer | 2026-05-23 |
| MIG-008 | Actualizacion | PolicyContract agrega TenantContext obligatorio (RES.137) | ai.mpat.designer | 2026-05-23 |

---

## DEUDA TECNICA V4 — REGISTRADA EN MIGRACION

| DT-ID | Descripcion | Prioridad | Referencia |
|---|---|---|---|
| DT-V4-001 | FastAPI version minima 0.115+ — verificar compatibilidad en primer deploy | MEDIA | CAPA_2, LOTE_002 |
| DT-V4-002 | LangGraph — evaluar si sigue siendo el runtime correcto o si hay alternativa No-GIL nativa | MEDIA | CAPA_3, pendiente investigacion |
| DT-V4-003 | Redis State Manager — evaluar reemplazo parcial por SubQ nativa de CAPA_11 | BAJA | CAPA_11 |
| DT-V4-004 | CAPA_09_MASTER debe migrarse a V4 antes de implementar componentes NHP/ASL-3/ZTS | ALTA | LOTE_003 |

---

## ESTADO DEL CICLO V3

- MPAT3 V3_02: CERRADO DEFINITIVAMENTE
- 34/34 FUT cerrados en V2_x, V3_02 finalizado con RELAY_035
- Resoluciones heredadas: RES.001 a RES.160 (inmutables, solo lectura en V4)
- Primera RES disponible en V4: RES.161

---

*ARQUITECTURA_base_V4_00.md · LOTE_001 · ai.mpat.designer@gmail.com · 2026-05-23*
*Migrado desde: ARQUITECTURA_base_V3_02_INC03.md (ID: 1peMlToJcdcrU3qFga3sSaCqQjQHMvnis)*
*                + ARQUITECTURA_base_V3_03.md (ID: 1maihtP8yxoVodu5b3QdzS89tzPzEyF02)*
*que has usado el formato de razonamiento adaptado por AGT*
