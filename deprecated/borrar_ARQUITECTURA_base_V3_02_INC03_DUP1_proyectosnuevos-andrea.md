# ARQUITECTURA_base_V3_02_INC03.md
## MPAT — My Personal Agents Team
## Descripcion Estructural por Capas · Version Pedagogica Completa
### Version V3_02 + INC-03 aplicado · AGT 2026
### Basado en: MPAT_V32_1 + PROMPT_V30 + Contrato Formal de Ejecucion
### Incorpora recopilacion historica completa + consolidacion multicapa + resoluciones V01_1 a V01_9 + RES.001 a RES.007 + sistema de Relay Cognitivo
### Cambios V3_02 respecto a V3_01: incorporacion de P13 — AI Specifiers Rule (cierre INC-01)
### INC-03 aplicado (RELAY_028, autorizado por docente_AGT_2026, 2026-05-19):
###   CAPA_9 actualizada con NHP Protocol (RES.090), ASL-3 (RES.091), ZTS (RES.092)
###   Indice, diagrama de flujo y stack actualizados.
###   Autores del patch diferencial: cursos.agt@gmail.com (RELAY_014),
###   ai.mpat.info@gmail.com (RELAY_014), docente_AGT_2026 (RELAY_018).
###   Aplicacion fisica autorizada: docente_AGT_2026 · RELAY_028 · 2026-05-19.

> **Relacion con otros documentos:**
> - `ARQUITECTURA_pendientes_V3_03.md` — pendientes abiertos
> - `ARQUITECTURA_systema_V3_03.md` — diagrama ASCII completo del sistema
> - `contrato_formal_ejecucion.md` — contrato de componentes con ejemplos reales
> - `RESOLUCIONES_MPAT_V3_03.md` — decisiones de diseno V2_03

> **Para el alumno — como leer este documento:**
> Este documento describe la arquitectura del sistema MPAT capa por capa. El principio es:
> **"Si necesitas modificar el comportamiento X del sistema, deberias poder hacerlo
> cambiando exactamente una capa, sin tocar las demas."**
> Primera lectura: de corrido para tener el mapa mental.
> Segunda lectura: como especificacion de lo que tenes que construir.

---

## INDICE DE CAPAS

```
CAPA 0 -> Entrada al Sistema (Browser, Telegram, WhatsApp, API externa)
CAPA 1 -> Puerta de Entrada (API Gateway)
CAPA 2 -> API y Transporte (FastAPI, WebSocket, SSE)
CAPA 3 -> Orquestacion Cognitiva (Orchestrator / Scheduler Cognitivo)
CAPA 4 -> Motor de Agentes (Agent Manager, Ciclo de Vida, AgentCard, Versioning)
CAPA 5 -> Motor de Inferencia (Model Router, Inferencia Especulativa)
CAPA 6 -> Estado Cognitivo (ECS — CognitiveState, Schema, Reglas)
CAPA 7 -> Herramientas y Protocolos (Skills, MCP 2.0, A2A, Skill Registry)
CAPA 8 -> Memoria (Activa, Persistente, Poda de Contexto, Semantic Caching)
CAPA 9 -> Seguridad y Validacion
         Componentes heredados V2: Zero-Trust Validator, Critic Agent,
         HITL Manager, Semantic Firewall, JWT/RBAC/OAuth 2.1
         Componentes nuevos V3_01 (FUT_3): NHP Protocol (RES.090),
         ASL-3 (RES.091), Zero Trust Session — ZTS (RES.092)
         RBAC ownership: modelo de permisos de tenants sobre tools/skills
         (RES.136 — cierre INC-02)
CAPA 10 -> Observabilidad (OpenTelemetry, Logging, Tracing, Alertas, Metricas Cognitivas)
CAPA 11 -> Infraestructura de Workers (Redis, RQ, Auto-scaling, Checkpointing)
CAPA 12 -> Multi-tenancy y Presupuesto (Conservation Laws, Budget Manager)
CAPA 13 -> Capa de Entrega (Delivery Layer, Formateo, Canal de Salida)
CAPA 14 -> Configuracion Global (Config, Politicas, Parametros)
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
via cierre de INC-01 (Alumno 7 — Rol Pedagogo — 2026-05-15).

---

## DIAGRAMA DE FLUJO PRINCIPAL

```
Usuario/Canal externo
 |
 [CAPA 0] Entrada — normaliza input, detecta plataforma
 |
 [CAPA 1] API Gateway — autentica JWT, valida, encola, rate limiting
 |
 [CAPA 2] Transporte — FastAPI/WebSocket/SSE
 |
 [CAPA 3] Orchestrator — Plan => Execute => Reflect => Replan
 | |
 [CAPA 4] [CAPA 6]
 Agent Mgr ECS State
 | |
 [CAPA 5] Model Router — selecciona modelo segun perfil
 |
 [CAPA 7] Skills/MCP 2.0/A2A — herramientas
 |
 [CAPA 8] Memoria — activa (RAM) + persistente (vector) + semantic cache
 |
 [CAPA 9] Critic/Security
          Heredados: Zero-Trust Validator, Critic Agent, HITL, Semantic Firewall
          V3_01 nuevos: NHP Protocol, ASL-3, Zero Trust Session (ZTS)
          RBAC (RES.136)
 |
 [CAPA 13] Delivery — formatea y envia por canal correcto
 |
 Usuario/Canal

Transversales (todas las capas los usan):
 [CAPA 10] Observabilidad — OpenTelemetry, tracing, metricas cognitivas
 [CAPA 11] Workers — Redis, RQ, auto-scaling
 [CAPA 12] Multi-tenancy — Budget Manager, Conservation Laws
 [CAPA 14] Config Global — YAML, env vars, politicas
```

---

## STACK TECNOLOGICO

```
Runtime: LangGraph + ExecutionState persistente
Estado: Redis State Manager
Memoria: ChromaDB + FAISS + Context Buffer + Episodic Memory
API: FastAPI + WebSocket + SSE
Canales: WhatsApp Business, Telegram, Email, SMS, WebRTC
Voz: Whisper STT + TTS local/cloud + VAD
Observ.: OpenTelemetry + structured logging
Workers: Redis + RQ + auto-scaling
Seguridad: Zero-Trust + Critic Agent + HITL + Sandbox RAM + KeyVault
           + NHP Protocol (authenticate-before-connect, RES.090)
           + ASL-3 (Agentic Security Level 3, RES.091)
           + Zero Trust Session — ZTS (renovacion automatica NHP, RES.092)
Embeddings: Pipeline como columna vertebral
Multi-tenant: Aislamiento total por tenant (namespace Redis por tenant)
Optimiz.: Nuitka, PyPy, Rust via PyO3
Acceso: Tailscale + FastAPI headless 24/7
```

---

## ESTADO DEL CICLO V2_x

- 34/34 FUT cerrados
- 109 Resoluciones documentadas
- Version final: V2_102 — fecha de cierre: 2026-05-10
- Proximo ciclo: V3 — FUT.31–FUT.40 identificados (rama paralela recomendada)
- Primer commit V3: FUT.31 — Transport Layer eBPF/QUIC

---

## REGISTRO DE CAMBIOS V3_02

| ID | Tipo | Descripcion | Autor | Fecha |
|---|---|---|---|---|
| INC-01 | Gap documental cerrado | P13 — AI Specifiers Rule elevado de invariante local CAPA_07 a principio transversal. Encabezado actualizado de 12 a 13 principios. Capas afectadas declaradas: CAPA_3, CAPA_4, CAPA_7, CAPA_12. | Alumno 7 — Rol Pedagogo | 2026-05-15 |
| INC-03 | Gap documental cerrado | CAPA_9 actualizada con componentes V3_01 nuevos: NHP Protocol (RES.090), ASL-3 (RES.091), ZTS (RES.092). Indice, diagrama de flujo y stack actualizados. Invariantes INV-NHP-UK.1 (RES.143) e INV-NHP-PERSIST (RES.144) referenciados. | docente_AGT_2026 · autorizacion RELAY_028 | 2026-05-19 |

---

## INVARIANTES CAPA_9 REFERENCIADOS EN LA BASE

La base no replica los invariantes completos (estan en el master de la capa).
Solo declara su existencia para que sean localizables:

```
INV-NHP.1 a INV-NHP.5  -> ver CAPA_09_MASTER_V3_01.md
INV-ASL.1 a INV-ASL.4  -> ver CAPA_09_MASTER_V3_01.md
INV-ZTS.1 a INV-ZTS.5  -> ver CAPA_09_MASTER_V3_01.md
INV-NHP-UK.1            -> ver RES143_INC06_TTL_NHP_UNIKERNEL_V3_02.md (RELAY_014)
INV-NHP-PERSIST         -> ver RES144_INC09_NHP_PERSIST_V3_02.md (RELAY_014)
```

---

*ARQUITECTURA_base_V3_02_INC03.md · AGT 2026 · Reconstituido desde recopilacion historica multicapa*
*INC-03 aplicado — autorizacion docente_AGT_2026 — RELAY_028 — 2026-05-19*
*que has usado el formato de razonamiento adaptado por AGT*
