# CAPA_06_MASTER_V3_02_FINAL.md
## MPAT — Estado Cognitivo (ECS) · RLHF + Multi-Expert + Dream Cycle + GRPOState
## Version: V3_02 · FINAL · Merge A+B+INFORME · 2026-05-23
## Fuente A: CAPA_06_MASTER_V3_02_UNIFICADO.md (andrea.bio · RELAY_033 · 9.5/10 · ID: 1R_2v3_5g7c6x3Qr4tq9jjtnng4tSd8uM)
## Fuente B: CAPA_06_MASTER_V3_02.md (ariel.garcia.traba@gmail.com · 2026-05-23 · ID: 1gGJeIngFjv-rbsFq4nPcUII-rHYwGckMuUiF6qkfA-U)
## Fuente C schema: INFORME_CAPA_06_V3_02.md (GRPOState + QUICConnectionState + INV-ECS · ID: 13mYxK4yGbOpzOiG8It195HtkYU7E7SPW)
## RES activas: RES.076, RES.077, RES.096, RES.115, RES.119, RES.123, RES.127, RES.156, RES.157, RES.158
## Autor merge: cursos.agt@gmail.com · 2026-05-23
## Paradigma: Co-evolution Human-AI + Post-Automation Paradigm
*que has usado el formato de razonamiento adaptado por AGT*

---

## NOTA PEDAGOGICA DE APERTURA

CAPA_06 es el nucleo de estado cognitivo de MPAT. Gestiona tres dimensiones inseparables
del estado del agente durante la ejecucion:

- Adaptacion: ajusta comportamiento en tiempo real segun seniales de la sesion activa (RLHF on-the-fly)
- Consenso experto: integra multiples perfiles de docente para generar respuestas ponderadas (Multi-Expert)
- Consolidacion: comprime la experiencia acumulada en un UserModel de largo plazo (Dream Cycle)

Principio rector: P8 — Co-evolution Human-AI. El agente no es estatico; evoluciona con cada
interaccion. La CAPA_06 es el mecanismo de esa evolucion a nivel de estado cognitivo.

Analogia: CAPA_06 es el sistema nervioso adaptativo del agente. CAPA_08 es su memoria de largo
plazo. No son lo mismo. CAPA_06 trabaja con preferencias del usuario en tiempo real.
CAPA_08 trabaja con fragmentos de memoria del agente entre sesiones.

CAPA_06 tambien es la fuente de verdad del estado de ejecucion de cada sesion activa
(ECS — Execution Context State). Aloja GRPOState (CAPA_05), QUICConnectionState (CAPA_01),
y perfiles de preferencia del usuario (RLHF). Garantiza inmutabilidad de tenant_id
y session_id post-asignacion.

---

## 1. RESPONSABILIDAD Y LIMITES

Lo que NO hace CAPA_06:
- NO gestiona memoria vectorial persistente (ChromaDB, FAISS) -> CAPA_08
- NO decide que modelo usar -> CAPA_03 + CAPA_05
- NO valida resultado semantico -> CAPA_09
- NO gestiona aislamiento unikernel -> CAPA_11
- NO implementa A2A ni SubQ directamente — propaga tenant_id como clave de aislamiento
- NO toma decisiones de negocio (es un store, no un motor)
- NO gestiona autenticacion -> CAPA_09
- NO gestiona presupuesto -> CAPA_12
- NO genera observabilidad (CAPA_10 lee de ECS, no escribe)
- NO persiste historia a largo plazo -> CAPA_08 (MemoriaEpisodica)
- NO ejecuta el Dream Cycle -> CAPA_08

> DISTINCION ARQUITECTURAL CAPA_01 vs CAPA_11 (resuelta en merge 2026-05-23):
> CAPA_01 (TenantRouter): asigna unikernel_id al request entrante. INV-TENANT.1.
> CAPA_11 (UniKernelManager): gestiona ciclo de vida y GARANTIA DE AISLAMIENTO.
>   INV-UK.1: unikernel NUNCA arranca con tenant_id = None.
>   INV-UK.2: cada unikernel tiene exactamente un tenant_id. Sin excepcion.
>   INV-UK.3: destroy_on_session_end = true (INMUTABLE). Nunca reutilizado.
> "Aislamiento unikernel" = CAPA_11 (isolation invariants).
> "Asignacion de unikernel" = CAPA_01 (routing).
> Fuente A (CAPA_11) era CORRECTA. Fuente B + INFORME simplificaron incorrectamente.

Distincion critica CAPA_06 vs CAPA_08 (RES.119):

| Componente | CAPA_06 | CAPA_08 |
|---|---|---|
| DreamCycleProcessor | NO — consume output | SI — lo ejecuta |
| HebbianManager | NO | SI — fortaleza y decay de fragmentos de memoria |
| HebbianReinforcer | SI — correlaciones de preferencia del usuario | NO |
| Objeto que refuerza | Dimensiones de preferencia del usuario | Fragmentos de memoria del agente |
| UserModel | SI — persiste 30 dias | NO |
| RLHF con feedback hebbiano | SI — RLHFSignalCollector | NO |

Regla de distincion: si el objeto es "una dimension de como aprende el usuario" -> CAPA_06.
Si el objeto es "un fragmento de lo que recuerda el agente" -> CAPA_08.

---

## 2. COMPONENTES

### 2.1 RLHFSignalCollector [RES.076]

Observa seniales implicitas y explicitas del usuario durante la sesion para ajustar en tiempo
real temperatura, tokens, nivel de detalle y formalidad.

**Design-by-Contract: RLHFSignalCollector**

```
Precondicion: sesion activa con tenant_id verificado (INV-TENANT.1 de CAPA_01).
             policy.yaml cargado con seccion rlhf.* (INV-14-PL.1).
             Redis disponible — si no: degradacion graciosa (INV-6-RLHF.2).

Postcondicion: confidence_delta en [0.0, 1.0] (INV-6-RLHF.1).
               ECS actualizado con los ajustes de la sesion.
               Si Redis falla: LOG + continuar sin ajuste. NUNCA abortar.

INV-6-RLHF.1: confidence_delta siempre en [0.0, 1.0].
               Fuera de rango: clampear, nunca lanzar excepcion.
INV-6-RLHF.2: degradacion graciosa si Redis falla.
               El agente continua sin ajuste RLHF — no interrumpe la sesion.
INV-6-RLHF.3: RLHFSignalCollector NUNCA modifica el modelo LLM.
               Solo ajusta parametros de inferencia del request.
```

DbC coleccion de senal:
Precondicion: signal_type en conjunto valido. confidence_delta en [0.0, 1.0]. session_id activo en Redis.
Postcondicion: senal registrada en mpat:cx:{tenant_id}:{session_id} con TTL=3600s. OTel span emitido.

**Namespaces Redis:**

| Namespace | TTL | Tipo | RES origen |
|---|---|---|---|
| `mpat:cx:{tenant_id}:{session_id}` | 3600s | Hash | RES.076 |

**OTel spans:**
- `rlhf.signal_collected`: signal_type, confidence_delta, dimension_affected, tenant_id
- `rlhf.adjustment_applied`: dimension, delta, new_value, tenant_id

---

### 2.2 MultiExpertAligner [RES.077]

Mantiene N perfiles de docente experto activos y calcula el vector de consenso ponderado
segun relevancia al contexto actual del alumno.

**Invariantes:**
- INV-6-MEA.1: suma de weights == 1.0 (tolerancia +-0.001)
- INV-6-MEA.2: divergencia > CONFLICT_THRESHOLD -> registrar en conflict_log
- INV-6-MEA.3: consensus siempre en [0.0, 1.0] por dimension
- INV-6-MEA.4: minimo 1 perfil activo; maximo definido en CAPA_14 (mea.max_profiles)

**Namespaces Redis — corregidos por RES.158:**

| Namespace | TTL | Tipo | RES origen |
|---|---|---|---|
| `mpat:cx:{tenant_id}:{session_id}:experts` | session | Hash | RES.077 -> RES.158 |
| `mpat:cx:{tenant_id}:{session_id}:conflict_log` | session | List | RES.077 -> RES.158 |

> RES.158 (2026-05-22): namespace migrado de mpat:cx:{session_id}:experts a
> mpat:cx:{tenant_id}:{session_id}:experts para garantizar aislamiento multi-tenant.
> INV-158.1 aplica: ningun dato de tenant A puede aparecer en namespace de tenant B.

---

### 2.3 DreamConsolidator + UserModel [RES.096]

Proceso asincrono que consolida seniales RLHF y vectores de consenso experto en un UserModel
comprimido de largo plazo.

**Invariantes:**
- INV-6-DC.1: minimo 3 seniales para activar consolidacion
- INV-6-DC.2: `UserModel.confidence in [0.0, 0.95]`
- INV-6-DC.3: `DreamConsolidator.run()` es idempotente por session_id
- INV-6-DC.4: `UserModel.version` es monotonicamente creciente por tenant_id
- INV-6-DC.5: consolidacion asincrona — NUNCA ejecuta durante sesion activa

**Namespaces Redis:**

| Namespace | TTL | Tipo | RES origen |
|---|---|---|---|
| `mpat:usermodel:{tenant_id}` | 30 dias | String | RES.096 |

---

### 2.4 QValueReranker + HebbianReinforcer [RES.119]

Extiende el Dream Cycle con Q-Value Reranking (alpha=0.1, gamma=0.9) y aprendizaje hebbiano
(umbral=0.6, decay=0.95).

**Namespaces Redis:**

| Namespace | TTL | Tipo | RES origen |
|---|---|---|---|
| `mpat:cx:{tenant_id}:qvalue_history` | 90 dias | List | RES.119 |

---

### 2.5 GRPOState — Sub-objeto del ECS [RES.156]

Sub-objeto del ECS que almacena el estado actual de la politica GRPO activa para la sesion.
Write-by-CAPA_05-only (INV-GRPO.3).

**Campos:**

| Campo | Tipo | Descripcion |
|---|---|---|
| `current_policy_version` | str | Version de la politica GRPO activa |
| `policy_adjusted_in_previous_chunk` | bool | Flag: si el chunk anterior aplico un PolicyDelta |
| `temperature` | float | Temperatura activa del motor de inferencia |
| `top_p` | float | Top-p activo |
| `repetition_penalty` | float | Penalizacion de repeticion activa |
| `last_reward_score` | float | Ultimo reward_score calculado por el Critic Agent |

**Invariante:**
INV-GRPO.3: GRPOState es write-by-CAPA_05-only. Cualquier otra capa que intente escribir
recibe ECSWriteViolationError.

---

### 2.6 QUICConnectionState — Sub-objeto del ECS [RES.157]

Sub-objeto del ECS que almacena el estado de la conexion QUIC activa.
Write-by-CAPA_01-only. Leido por QUICSpanExporter (CAPA_10) via ECS.

**Campos:**

| Campo | Tipo | Descripcion |
|---|---|---|
| `connection_id` | str | ID unico de la conexion QUIC |
| `handshake_ms` | int | Duracion del handshake QUIC en ms |
| `stream_open_ms` | int | Duracion de apertura del stream en ms |
| `zero_rtt_used` | bool | Si se uso 0-RTT en esta conexion |
| `zero_rtt_result` | str | Resultado del intento 0-RTT (accepted/rejected/na) |
| `ebpf_quota_remaining` | int | Quota eBPF restante al momento del registro |
| `ebpf_packets_dropped` | int | Paquetes dropeados por eBPF en esta sesion |

---

### 2.7 ECSContextGuard + ECSExpiryManager [RES.127]

**ECSContextGuard:** Valida que tenant_id y session_id no sean modificados post-asignacion.
Lanza SessionContextViolationError si se intenta (INV-P15.1, RES.127).

**ECSExpiryManager:** Gestiona TTLs y limpieza activa de sesiones expiradas.
Emite evento session.expired a CAPA_10 antes de eliminar.

---

## 3. INVARIANTES CRITICOS VIGENTES

| ID | Invariante | Nivel |
|---|---|---|
| INV-ECS-001 | ECS NUNCA sale de CAPA_06 sin tenant_id valido. Si ausente o vacio: ECSValidationError antes de persistir. | CRITICO |
| INV-ECS-002 | tenant_id y session_id son inmutables post-asignacion. ECSContextGuard rechaza modificaciones con SessionContextViolationError. | ALTO |
| INV-ECS-003 | Todas las escrituras al ECS son atomicas (pipeline Redis). Sin escritura parcial. | ALTO |
| INV-ECS-TTL.1 | Todo ECS tiene TTL. NUNCA se crea ECS sin TTL. Default 3600s. | ALTO |
| INV-GRPO.3 | GRPOState write-by-CAPA_05-only. Otras capas reciben ECSWriteViolationError. | ALTO |
| INV-6-RLHF.1 | confidence_delta SIEMPRE en [0.0, 1.0]. Fuera de rango: clampear, nunca excepcion. | ALTO |
| INV-6-RLHF.2 | Si Redis falla durante RLHF: degradacion graciosa (LOG). NUNCA abortar sesion activa. | MEDIO |
| INV-6-RLHF.3 | RLHFSignalCollector NUNCA modifica el modelo LLM. Solo ajusta parametros del request. | ALTO |
| INV-6-MEA.1 | suma de weights == 1.0 (tolerancia +-0.001) | ALTO |
| INV-6-MEA.2 | divergencia > CONFLICT_THRESHOLD -> registrar en conflict_log | MEDIO |
| INV-6-MEA.3 | consensus siempre en [0.0, 1.0] por dimension | ALTO |
| INV-6-MEA.4 | minimo 1 perfil activo; maximo definido en CAPA_14 | ALTO |
| INV-6-DC.1 | minimo 3 seniales para activar consolidacion | ALTO |
| INV-6-DC.2 | UserModel.confidence in [0.0, 0.95] | ALTO |
| INV-6-DC.3 | DreamConsolidator.run() es idempotente por session_id | ALTO |
| INV-6-DC.4 | UserModel.version es monotonicamente creciente por tenant_id | ALTO |
| INV-6-DC.5 | consolidacion asincrona — NUNCA ejecuta durante sesion activa | CRITICO |
| INV-158.1 | ningun dato de tenant A puede aparecer en namespace de tenant B | CRITICO |

---

## 4. FLUJO DE DATOS COMPLETO

```
[Sesion activa]
  RLHFSignalCollector -> mpat:cx:{tenant_id}:{session_id} (TTL 3600s)
  MultiExpertAligner  -> mpat:cx:{tenant_id}:{session_id}:experts
  CAPA_03 aplica consensus en cada PLAN
  CAPA_05 escribe GRPOState en ECS (write-by-CAPA_05-only, INV-GRPO.3)
  CAPA_01 escribe QUICConnectionState en ECS (write-by-CAPA_01-only)

[Near-TTL o cierre de sesion]
  DreamConsolidator.run(tenant_id, session_id)
    -> QValueReranker.rerank(qvalue_history)
    -> HebbianReinforcer.reinforce(model_prefs, session_prefs)
    -> Escribe mpat:usermodel:{tenant_id} (TTL 30d)

[Nueva sesion]
  ECS.load() -> DreamConsolidator.load_for_session(tenant_id)
    -> Si UserModel presente Y confidence >= 0.3: aplicar prior RLHF
    -> Si no: iniciar sin prior
```

---

## 5. TRAMPAS EDUCATIVAS

**Trampa 1 — RES.076:**
La afirmacion "RLHF on-the-fly modifica el modelo LLM subyacente en tiempo real — los pesos del
modelo cambian con cada sesion" es **FALSA**.
Respuesta correcta: RLHF on-the-fly en MPAT ajusta los **parametros de inferencia** (temperatura,
tokens, formalidad, nivel de detalle), NO los pesos del modelo. El modelo LLM es estatico durante
la sesion. La confusion es comun porque el termino RLHF en la literatura de investigacion si implica
actualizacion de pesos — pero el RLHF de CAPA_06 es una adaptacion del concepto al contexto de
inferencia en tiempo real sin reentrenamiento.
Invariante que la cierra: INV-6-RLHF.3 — RLHFSignalCollector NUNCA modifica el modelo LLM.

**Trampa 2 — RES.077:**
La afirmacion "Con mas perfiles de docente activos, el sistema siempre genera mejores respuestas
— cuantos mas perfiles, mejor el consenso" es **FALSA**.
Respuesta correcta: a partir de cierto punto, mas perfiles generan consensos mas difusos y con mayor
probabilidad de divergencia que supere CONFLICT_THRESHOLD. mea.max_profiles (default=5) es un balance
entre diversidad de perspectivas y coherencia del consenso resultante. Aumentarlo arbitrariamente puede
degradar la calidad de la respuesta al producir un vector de consenso demasiado disperso para ser actionable.
Invariante que la cierra: INV-6-MEA.1 — suma de weights == 1.0 (+-0.001).

**Trampa 3 — RES.096:**
La afirmacion "El Dream Cycle ejecuta durante la sesion activa para no perder seniales — es un proceso
de consolidacion continua" es **FALSA**.
Respuesta correcta: el Dream Cycle es ASINCRONO — nunca durante la sesion activa (INV-6-DC.5). La
analogia del sueno REM es precisa: ocurre cuando el sujeto no esta activo. Ejecutar durante la sesion
violaria el principio de no interferencia con el flujo cognitivo activo.
Invariante que la cierra: INV-6-DC.5.

**Trampa 4 — RES.119:**
La afirmacion "HebbianReinforcer de CAPA_06 y HebbianManager de CAPA_08 son el mismo componente
— duplicacion innecesaria" es **FALSA**.
Respuesta correcta: CAPA_06 refuerza correlaciones entre **dimensiones de preferencia del usuario**.
CAPA_08 refuerza conexiones entre **fragmentos de memoria del agente**. Mismo principio de Hebb,
implementaciones y propositos incompatibles.
Invariante que la cierra: INV-6-DC.3 — HebbianReinforcer de CAPA_06 opera sobre el UserModel,
no sobre los fragmentos de CAPA_08.

---

## 6. CONFIG FILES V3_02 (policy.yaml)

| Seccion | Parametro | Default | Rango | Descripcion | RES |
|---|---|---|---|---|---|
| rlhf | signal_window | 300s | [60,3600] | Ventana de observacion | RES.076 |
| rlhf | min_confidence | 0.3 | [0.0,1.0] | Minimo para aplicar ajuste | RES.076 |
| rlhf | max_delta_per_turn | 0.15 | [0.05,0.30] | Maximo ajuste por turno | RES.076 |
| mea | max_profiles | 5 | [1,10] | Maximo de perfiles activos | RES.077 |
| mea | conflict_threshold | 0.4 | [0.1,0.9] | Umbral de divergencia | RES.077 |
| mea | weight_tolerance | 0.001 | — | Tolerancia en suma de pesos | RES.077 |
| dream | min_signals | 3 | [1,10] | Minimo seniales para consolidar | RES.096 |
| dream | confidence_ceiling | 0.95 | [0.5,1.0] | Techo de confianza UserModel | RES.096 |
| dream | usermodel_ttl | 30d | [7d,365d] | TTL del UserModel en Redis | RES.096 |
| dream | trigger_at_ttl_pct | 0.85 | [0.5,0.99] | % TTL para disparar consolidacion | RES.096 |
| dream.hebbiano | learning_rate | 0.1 | [0.01,0.5] | Alpha Q-Learning | RES.119 |
| dream.hebbiano | discount | 0.9 | [0.5,1.0] | Gamma Q-Learning | RES.119 |
| dream.hebbiano | threshold | 0.6 | [0.1,1.0] | Umbral co-activacion hebbiana | RES.119 |
| dream.hebbiano | decay | 0.95 | [0.5,1.0] | Decaimiento pasivo por sesion | RES.119 |

---

## 7. NAMESPACES REDIS — TABLA COMPLETA

| Namespace | TTL | Tipo | RES origen | Nota |
|---|---|---|---|---|
| `mpat:ecs:{tenant_id}:{session_id}` | 3600s | Hash | RES.076 | Canonico V3_02 |
| `mpat:cx:{tenant_id}:{session_id}` | 3600s | Hash | RES.076 | Alias legacy |
| `mpat:cx:{session_id}:experts` | session | Hash | RES.077 | DT-06-01: sin tenant_id (legacy) |
| `mpat:cx:{session_id}:conflict_log` | session | List | RES.077 | DT-06-01: sin tenant_id (legacy) |
| `mpat:cx:{tenant_id}:{session_id}:experts` | session | Hash | RES.077 -> RES.158 | Correcto |
| `mpat:cx:{tenant_id}:{session_id}:conflict_log` | session | List | RES.077 -> RES.158 | Correcto |
| `mpat:usermodel:{tenant_id}` | 30 dias | String | RES.096 | |
| `mpat:cx:{tenant_id}:qvalue_history` | 90 dias | List | RES.119 | |
| `mpat:quic:session:{tenant_id}:{conn_id}` | 3600s | Hash | RES.155 | Write-by-CAPA_01 |

> DT-06-01 CERRADA por RES.158 (2026-05-22).

---

## 8. INTEGRACION CON OTRAS CAPAS

Escribe en ECS: CAPA_01 (QUICConnectionState), CAPA_05 (GRPOState)
Lee de ECS: CAPA_03 (orquestacion), CAPA_05 (politica activa), CAPA_10 (QUICSpanExporter, PolicyVersionTracker)
Notifica: CAPA_10 (evento session.expired en OTel)

---

## 9. ESTADO FINAL DE LA CAPA EN V3_02

| Componente | Estado V3_01 | Estado V3_02 | Cambio |
|---|---|---|---|
| RLHFSignalCollector | Activo (RES.076) | Sin cambios | Estable |
| MultiExpertAligner | Activo (RES.077) | Namespace corregido (RES.158) | Gap cerrado |
| DreamConsolidator | Activo (RES.096) | Sin cambios | Estable |
| QValueReranker | Activo (RES.119) | Sin cambios | Estable |
| HebbianReinforcer | Activo (RES.119) | Sin cambios | Estable |
| DbC RLHFSignalCollector | AUSENTE | NUEVO V3_02b | Brecha cerrada |
| Tabla CAPA_06 vs CAPA_08 | AUSENTE | NUEVO V3_02b | Brecha cerrada |
| GRPOState sub-objeto ECS | AUSENTE | NUEVO (RES.156) | Gap cerrado |
| QUICConnectionState sub-objeto | AUSENTE | NUEVO (RES.157) | Gap cerrado |
| ECSContextGuard | AUSENTE | NUEVO (RES.127) | Gap cerrado |
| ECSExpiryManager | AUSENTE | NUEVO (RES.127) | Gap cerrado |
| INV-ECS-001/002/003/TTL.1 | AUSENTES | NUEVOS V3_02 | Gaps cerrados |
| INV-GRPO.3 | AUSENTE | NUEVO (RES.156) | Gap cerrado |
| INV-6-RLHF.3 | AUSENTE | NUEVO V3_02 | Gap cerrado |
| Namespace experts/conflict_log | Sin tenant_id (gap) | Con tenant_id (RES.158) | DT-06-01 CERRADA |
| 4 trampas formato A | 1 informal | 4 completas V3_02 | Brecha cerrada |

**Invariantes vigentes:** INV-ECS-001/002/003/TTL.1, INV-GRPO.3,
INV-6-RLHF.1/2/3, INV-6-MEA.1/2/3/4, INV-6-DC.1/2/3/4/5, INV-158.1/2/3/4

---

## 10. DEUDA TECNICA HEREDADA A V4

| Item | Descripcion | Prioridad |
|---|---|---|
| FUT-6-A | Sin RES asignada en V3_02 | MEDIA |
| FUT-6-B | Sin RES asignada en V3_02 | MEDIA |
| DT-06-01 | CERRADA por RES.158 (2026-05-22) | RESUELTA |

---

## NOTA DE MERGE Y RESOLUCION DE CONFLICTO

**Conflicto CAPA_01 vs CAPA_11 — RESOLUCION DEFINITIVA:**

| Fuente | Referencia | Estado |
|---|---|---|
| Fuente A (UNIFICADO, andrea.bio) | CAPA_11 | CORRECTO |
| Fuente B (agt1973) | CAPA_01 | SIMPLIFICACION INCORRECTA |
| INFORME_CAPA_06 | CAPA_01 | SIMPLIFICACION INCORRECTA |
| CAPA_11_MASTER (canonico) | UniKernelManager, INV-UK.1/2/3 | CONFIRMA CAPA_11 para aislamiento |
| CAPA_01_MASTER (canonico) | TenantRouter, INV-TENANT.1 | CONFIRMA CAPA_01 para asignacion |

Distincion definitiva:
- CAPA_11 gestiona AISLAMIENTO: spawn, lifecycle, destroy_on_session_end, NHP token renewal.
  Es quien garantiza que ningun unikernel sirva a dos tenants (INV-UK.2).
- CAPA_01 gestiona ASIGNACION: verifica tenant activo y asigna unikernel_id al request entrante.
  Es el punto de entrada, no el garante del aislamiento.

La frase "NO gestiona aislamiento unikernel" en CAPA_06 apunta a quien garantiza el aislamiento = CAPA_11.
Fuente A era correcta. El INFORME y Fuente B simplificaron indebidamente.

**Aporte exclusivo de cada fuente en este merge:**
- Fuente A: componentes RLHF/MEA/Dream COMPLETOS con DbC, 4 trampas completas, config policy.yaml, flujo de datos, referencia CAPA_11 CORRECTA.
- Fuente B: NOTA PEDAGOGICA DE APERTURA, numeracion de secciones, tabla ESTADO AL CIERRE.
- Fuente C (INFORME): GRPOState schema, QUICConnectionState schema, INV-ECS-001/002/003/TTL.1, INV-GRPO.3, INV-6-RLHF.3, namespace canonico mpat:ecs:, tabla integracion capas.

**Archivo a deprecar en proxima sesion (docente):**
ID: 1xS1HTEepitM2SGes13ZGACR-MDE8-fuV (CAPA_06_MASTER_V3_02_FINAL.md previo, agt1973, 2026-05-23 16:02)
Razon: version anterior al merge completo A+B+INFORME. Tiene CAPA_11 correcto pero carece de GRPOState schema, INV-ECS y componentes 2.5-2.7.

---

*CAPA_06_MASTER_V3_02_FINAL.md · Merge A+B+INFORME · cursos.agt@gmail.com · 2026-05-23*
*Fuente A: CAPA_06_MASTER_V3_02_UNIFICADO.md (andrea.bio · RELAY_033 · 9.5/10)*
*Fuente B: CAPA_06_MASTER_V3_02.md (ariel.garcia.traba@gmail.com · 2026-05-23)*
*Fuente C schema: INFORME_CAPA_06_V3_02.md (GRPOState + QUICConnectionState + INV-ECS)*
*que has usado el formato de razonamiento adaptado por AGT*
