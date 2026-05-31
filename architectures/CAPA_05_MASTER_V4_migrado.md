\---  
migrado\_desde: MPAT3/capas/CAPA\_05\_MASTER\_V3\_02.md  
id\_origen: 11uFdcD3UygJK-0AnxTorUV1U8FY5wjYg9uFQ9g7x65s  
autor\_migracion: mpat.andrea  
fecha\_migracion: 2026-05-23  
estado: MIGRADO\_ADAPTADO  
cambios: |  
  \- Encabezado de migracion agregado.  
  \- Error de numeracion RES corregido en todo el documento:  
    RES.052 → RES.110 (ShadowRadix+CSA/HCA)  
    RES.053 → RES.111 (NVFP4)  
    RES.054 → RES.112 (XGrammar-2)  
  \- La seccion 7 del original ("Nota sobre error de numeracion") se mantiene  
    como registro historico de la correccion.  
  \- Sin cambio al contenido tecnico — calidad original 9.0/10.  
deuda\_heredada: |  
  \- PEND-05-V4-01: el MASTER raw original (720KB) contiene sesiones relay acumuladas  
    sin depurar. V4 debe extraer solo el contenido arquitectural vigente en una sesion  
    de limpieza dedicada \[ABIERTO → sesion dedicada\].  
  \- NOTA: FlowGRPO (RES.156) esta activo y referenciado correctamente en CAPA\_05.  
    Verificar consistencia con CAPA\_14 (PolicyLoader) que provee el PolicyDelta.  
destino\_mpat4: core/cognition/reasoning/  
\---

\# CAPA\_05 — Motor de Inferencia: ModelRouter · ShadowRadix · XGrammar-2 · QuantizationSelector  
\#\# Version: MASTER\_V3\_02 — Consolidado MPAT4  
\#\# Fuentes: CAPA\_05\_MASTER.md \+ INFORME\_CAPA\_05\_V3\_02b (RELAY\_029 GAMMA)  
\#\# Autor consolidacion: ariel.garcia.traba@gmail.com · 2026-05-23  
\#\# RES que afectan esta capa: RES.051, RES.110 (ShadowRadix+CSA/HCA), RES.111 (NVFP4), RES.112 (XGrammar-2), RES.156 (FlowGRPO)  
\#\# NOTA: RES.052/053/054 que aparecen en el canonico original son error de numeracion — corregidos en este migrado a RES.110/111/112  
\#\# Paradigma: Post-Automation Paradigm — el sistema decide que modelo usar

\*que has usado el formato de razonamiento adaptado por AGT\*

\---

\#\# NOTA PEDAGOGICA DE APERTURA

CAPA\_05 es el cerebro de seleccion de modelos. No ejecuta el modelo — decide CUAL usar en  
funcion de la tarea, el hardware disponible, el presupuesto del tenant, y la latencia actual  
de cada modelo. Esta decision es completamente autonoma: el usuario no elige el modelo, el  
ModelRouter lo elige por el.

La analogia: CAPA\_05 es el jefe de triaje en una guardia medica. Cuando llega un paciente  
(tarea), no siempre lo atiende el cirujano mas especializado. Si es una consulta simple, va  
con el medico general (phi4-mini). Si es critica, va con el especialista (claude-sonnet-4).  
El medico de guardia que decide no es el paciente — es el sistema de triaje, basado en  
urgencia, carga actual, y capacidades del medico disponible.

\---

\#\# 1\. DESCRIPCION Y EVOLUCION

\#\#\# 1.1 Que hace CAPA\_05  
\- Selecciona el modelo mas adecuado para cada tarea segun: latencia P99, VRAM disponible,  
  quality\_floor del agente, y presupuesto del tenant  
\- Implementa la cadena de fallback (phi4-mini → ... → claude-sonnet-4)  
\- Gestiona contextos largos via ShadowRadix \+ CSA/HCA (RES.110)  
\- Selecciona cuantizacion optima segun hardware (RES.111 — NVFP4 solo en B100/B200)  
\- Aplica XGrammar-2 para generacion estructurada (RES.112)  
\- Aplica FlowGRPO para ajuste de politica en token boundary (RES.156)

\#\#\# 1.2 Lo que CAPA\_05 NO hace  
\- NO executa el transporte de la respuesta al usuario (CAPA\_02 — SSEHandler)  
\- NO coordina agentes (CAPA\_03)  
\- NO valida semantica del output (CAPA\_09)  
\- NO gestiona budget (CAPA\_12)

\---

\#\# 2\. COMPONENTES

\#\#\# 2.1 ModelRouter  
Selecciona el modelo y ejecuta la cadena de fallback.

Cadena de fallback por defecto (NO es un ranking de calidad — ver Trampa 1):  
  phi4-mini \-\> \[modelos intermedios segun config\] \-\> claude-sonnet-4

Invariante INV-5-1: la cadena de fallback NO es un ranking de calidad. P6 mandatorio:  
  ModelRouter NUNCA lanza excepcion vacia — chain\[-1\] (claude-sonnet-4) es el ultimo  
  recurso siempre disponible.

\#\#\# 2.2 ShadowRadix \+ CSA/HCA (RES.110)  
Gestion de contextos largos. ShadowRadix mantiene un indice radix de los KV caches activos.  
CSA (Context-Sensitive Attention) y HCA (Hierarchical Context Attention) reducen la atencion  
en partes del contexto que tienen baja relevancia para el token actual.

Namespace Redis: mpat:inference:long\_ctx:{tenant\_id}:kv\_hit\_rate (TTL=300s, Float)

\#\#\# 2.3 QuantizationSelector (RES.111 — NVFP4)  
Selecciona el formato de cuantizacion optimo segun hardware.

NVFP4: solo en hardware Blackwell (B100/B200). En Hopper/Ampere: INT8 obligatorio.  
Perdida de calidad NVFP4: 2.1% ECS vs INT8 (\~2 campos criticos incorrectos por 100 tasks).

Invariante INV-5-21-1: NVFP4 exclusivamente en B100/B200. En Hopper/Ampere: INT8 obligatorio.  
  El QuantizationSelector lo verifica en startup. Activar NVFP4 en hardware incorrecto es  
  degradacion silenciosa sin beneficio real.

Namespace Redis: mpat:inference:quant\_format:{model\_id} (TTL=3600s, String enum)

\#\#\# 2.4 XGrammar-2 (RES.112)  
Generacion estructurada con compilacion de gramatica incremental. Garantiza que la salida  
del modelo cumpla el schema esperado sin postprocesamiento.

\#\#\# 2.5 FlowGRPO (RES.156)  
Ajuste de politica de generacion en token boundary. Cuando el ModelRouter detecta que la  
politica del tenant cambio durante la generacion, aplica el PolicyDelta sin interrumpir  
el stream y emite grpo.policy\_adjusted hacia CAPA\_10.

\---

\#\# 3\. NAMESPACES REDIS — CAPA\_05

| Namespace | TTL | Tipo | RES origen |  
|---|---|---|---|  
| mpat:model:availability:{model\_id} | 60s | String(bool) | RES.051 |  
| mpat:model:latency\_p99:{model\_id} | 300s | Float | RES.030 |  
| mpat:model:vram\_usage:{model\_id} | 60s | Float | RES.051 |  
| mpat:model:avoid\_speculative:{model\_id} | 3600s | String(TTL logico) | RES.017 |  
| mpat:inference:long\_ctx:{tenant\_id}:kv\_hit\_rate | 300s | Float | RES.110 |  
| mpat:inference:quant\_format:{model\_id} | 3600s | String(enum) | RES.111 |

\---

\#\# 4\. OTEL SPANS — CAPA\_05

| Span | Atributos | RES |  
|---|---|---|  
| inference.model\_route | tenant\_id, profile\_id, model\_selected, fallback\_used(bool), latency\_ms | RES.051 |  
| inference.speculative.cycle | task\_id, acceptance\_rate, tokens\_drafted, tokens\_accepted | RES.020-024 |  
| inference.long\_context.kv | tenant\_id, context\_tokens, kv\_hit\_rate, strategy | RES.110 |  
| inference.quantization.select | model\_id, hardware, format\_selected(INT8/NVFP4/BF16), quality\_delta | RES.111 |  
| inference.xgrammar2.compile | schema\_id, compilation\_ms, incremental(bool), semantic\_boost | RES.112 |  
| inference.ttft | tenant\_id, model\_id, ttft\_ms, context\_tokens | RES.030 |  
| inference.tpot | tenant\_id, model\_id, tpot\_ms, token\_count | RES.030 |

Invariante INV-5-RES157: tenant\_id obligatorio en TODOS los spans de CAPA\_05.  
  El QUICSpanExporter (CAPA\_10) verifica su presencia antes de exportar (INV-157.4).

\---

\#\# 5\. INVARIANTES CRITICOS

| ID | Invariante | Nivel |  
|----|-----------|-------|  
| INV-5-1 | Cadena de fallback NO es ranking de calidad. chain\[-1\] siempre disponible. | CRITICO |  
| INV-5-21-1 | NVFP4 exclusivamente en B100/B200. Hopper/Ampere: INT8 obligatorio. | CRITICO |  
| INV-5-RES157 | tenant\_id obligatorio en TODOS los spans de CAPA\_05. | ALTO |

\---

\#\# 6\. TRAMPAS EDUCATIVAS

\*\*Trampa 1 — la cadena de fallback no es un ranking:\*\*  
La afirmacion "la cadena de fallback es un ranking de calidad — phi4-mini es el peor modelo y  
claude-sonnet-4 el mejor" es FALSA.

El primer eslabon (phi4-mini) es el MAS ECONOMICO que cumple el SLA para esa tarea, no el  
"peor". Un agente de respuesta rapida puede siempre usar phi4-mini con excelentes resultados.  
Claude-sonnet-4 es el ultimo recurso porque es el mas COSTOSO, no porque sea el "mejor" en  
absoluto — para algunas tareas phi4-mini genera mejor resultado por su menor latencia.  
El criterio correcto: "el modelo correcto para esta tarea en este momento con este presupuesto",  
no el mas caro.

\*\*Trampa 2 — NVFP4 siempre mejor:\*\*  
La afirmacion "4 bits es mejor que 8 bits porque ocupa menos VRAM — activar NVFP4 siempre que  
sea posible para maximizar throughput" es FALSA.

NVFP4 pierde 2.1% de calidad ECS vs INT8. En MPAT esto representa \~2 campos criticos  
incorrectos por cada 100 tasks. El decision point no es "cuanto ahorro de VRAM" sino "puedo  
permitirme esa degradacion dado el quality\_floor del agente actual". Ademas, NVFP4 SOLO es  
optimo en hardware Blackwell (B100/B200) — en Hopper/Ampere la ganancia es marginal (\<12%)  
con la misma perdida de calidad. Activar NVFP4 en hardware incorrecto es degradacion silenciosa  
sin beneficio real.

\---

\#\# 7\. REGISTRO DE CORRECCION — ERROR DE NUMERACION EN CANONICO ORIGINAL

El canonico CAPA\_05\_MASTER referenciaba las RES de inferencia V3\_01 con numeracion incorrecta.  
Este migrado los corrige:

| Referencia en canonico original | Referencia correcta | Descripcion |  
|---|---|---|  
| RES.052 | RES.110 | ShadowRadix \+ CSA/HCA |  
| RES.053 | RES.111 | NVFP4 |  
| RES.054 | RES.112 | XGrammar-2 |

Esta correccion fue aplicada en todos los headers y referencias del presente documento.

\---

\#\# 8\. DEUDA TECNICA AL CIERRE V3\_02 Y PENDIENTES V4

| DT | Descripcion | Estado |  
|----|-------------|--------|  
| RES.110 | ShadowRadix \+ CSA/HCA | CERRADO |  
| RES.111 | NVFP4 \+ QuantizationSelector | CERRADO |  
| RES.112 | XGrammar-2 | CERRADO |  
| RES.156 | FlowGRPO | CERRADO |  
| PEND-05-V4-01 | Limpieza del MASTER raw (720KB) — extraer solo contenido arquitectural vigente | ABIERTO → sesion dedicada |

\---

\*CAPA\_05\_MASTER\_V4\_migrado.md · MPAT4 · mpat.andrea · 2026-05-23\*  
\*Migrado desde: ariel.garcia.traba@gmail.com · CAPA\_05\_MASTER\_V3\_02.md\*  
\*Consolida: CAPA\_05\_MASTER.md \+ INFORME\_CAPA\_05\_V3\_02b (RELAY\_029 GAMMA)\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
