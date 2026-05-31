\# INFORME CAPA 05 — MOTOR DE INFERENCIA  
\*\*Version fuente:\*\* V3\_01  
\*\*Alumno:\*\* cursos.au.agt@gmail.com  
\*\*Fecha:\*\* 2026-05-13  
\*\*RES que afectan esta capa:\*\* RES.014, RES.016, RES.017, RES.020, RES.021, RES.022, RES.023, RES.024, RES.027, RES.029, RES.031, RES.034, RES.036, RES.039, RES.047, RES.048, RES.051, RES.052, RES.053, RES.054  
\*\*Paradigma predominante:\*\* Inteligencia Artificial Generativa y Agentica

\---

\#\# 1\. Descripcion de la capa

La Capa 5 es el Motor de Inferencia de MPAT. Su responsabilidad es recibir la solicitud de inferencia del Orchestrator (Capa 3\) y ejecutarla contra el modelo correcto, aplicando optimizaciones de velocidad y calidad segun el perfil declarado por el agente (Capa 4).

\*\*Principio P2 (ARQUITECTURA\_base):\*\* ningun agente llama directamente a un modelo. Todo agente declara un perfil de inferencia. La Capa 5 decide que modelo cumple ese perfil.

Esta capa NO es punto de entrada A2A (RES.113) ni SubQ (RES.114) ni Unikernel (RES.115). Es una capa interna de computo puro: recibe, ejecuta, retorna metricas. Sus salidas alimentan a Capa 4 (resultado de inferencia) y Capa 10 (trazas OTel con spans de TTFT/TPOT).

La complejidad de esta capa en V3\_01 es acumulativa: 19 optimizaciones activas simultaneamente, 3 nuevas de FUT\_3 (ShadowRadix+CSA/HCA, NVFP4, XGrammar-2), mas la cadena de fallback de modelos y los SLAs por perfil de tarea.

\---

\#\# 2\. Componentes de la capa

\#\#\# 2.1 — ModelRouter  
\- \*\*Que hace:\*\* recibe un objeto \`InferenceRequest\` de Capa 3 y decide que modelo ejecuta la tarea. Aplica la cadena de fallback si el primer candidato no esta disponible o no cumple el SLA declarado.  
\- \*\*Capa de origen:\*\* Capa 5  
\- \*\*RES que lo definen:\*\* RES.051 (ModelPolicy \+ model\_selector.py), RES.052 (ShadowRadix seleccion), RES.053 (NVFP4 seleccion)  
\- \*\*Dependencias:\*\* Capa 3 (recibe InferenceRequest), Capa 4 (InferenceProfile del AgentCard), Capa 14 (config\_policy.yaml con cadena de fallback y SLA profiles)  
\- \*\*Namespaces Redis propios:\*\* ninguno directo — la seleccion es stateless  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agentica  
\- \*\*Config file V3\_01:\*\* config\_policy.yaml (seccion inference.sla\_profiles y inference.fallback\_chain)

\#\#\# 2.2 — InferenceExecutor  
\- \*\*Que hace:\*\* ejecuta la inferencia contra el modelo seleccionado por ModelRouter. Mide TTFT y TPOT. Activa las optimizaciones correspondientes segun el perfil (especulativa, longcontext, cuantizacion, grammar).  
\- \*\*Capa de origen:\*\* Capa 5  
\- \*\*RES que lo definen:\*\* RES.016 (SuffixDecoding), RES.020 (EAGLE-3), RES.021 (SSD), RES.022 (TALON), RES.023 (CAST), RES.024 (TorchSpec), RES.027 (Prefix Caching), RES.029 (Chunked Prefill), RES.031 (Continuous Batching), RES.034 (Flash Attention 3), RES.036 (INT8 SmoothQuant), RES.039 (SGLang RadixAttention), RES.047 (vLLM MRV2), RES.048 (Token Alignment), RES.052 (ShadowRadix+CSA/HCA), RES.053 (NVFP4), RES.054 (XGrammar-2)  
\- \*\*Dependencias:\*\* ModelRouter (modelo seleccionado), Capa 10 (emite spans OTel), Capa 14 (parametros de cada optimizacion)  
\- \*\*Namespaces Redis propios:\*\* KV Cache via ShadowRadix (hot/warm tiers). Cold tier en NVMe local.  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agentica  
\- \*\*Config file V3\_01:\*\* config\_policy.yaml (secciones inference.long\_context, inference.quantization, inference.structured\_decoding, inference.speculative)

\#\#\# 2.3 — QuantizationSelector  
\- \*\*Que hace:\*\* selecciona el formato de cuantizacion optimo (BF16, INT8, NVFP4) segun hardware disponible y quality\_floor declarado por el agente.  
\- \*\*Capa de origen:\*\* Capa 5  
\- \*\*RES que lo definen:\*\* RES.036 (INT8 SmoothQuant), RES.053 (NVFP4)  
\- \*\*Dependencias:\*\* InferenceProfile (quality\_floor), config\_policy.yaml (hardware\_allowlist NVFP4), Capa 14  
\- \*\*Namespaces Redis propios:\*\* ninguno  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agentica  
\- \*\*Config file V3\_01:\*\* config\_policy.yaml (seccion inference.quantization)

\#\#\# 2.4 — LongContextManager  
\- \*\*Que hace:\*\* detecta si el contexto supera el umbral de 32768 tokens y activa ShadowRadix \+ CSA/HCA. Gestiona los tiers de KV Cache (hot GPU RAM / warm CPU RAM / cold NVMe).  
\- \*\*Capa de origen:\*\* Capa 5  
\- \*\*RES que lo definen:\*\* RES.039 (SGLang RadixAttention base), RES.052 (ShadowRadix+CSA/HCA)  
\- \*\*Dependencias:\*\* ECS de Capa 4 (tamanio del contexto), hardware local (NVMe para cold tier), Capa 10 (spans de kv\_hit\_rate)  
\- \*\*Namespaces Redis propios:\*\* KV Cache compartido en hot\_tier (TTL=5s), warm\_tier (TTL=60s)  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agentica  
\- \*\*Config file V3\_01:\*\* config\_policy.yaml (seccion inference.long\_context)

\#\#\# 2.5 — XGrammar2Sampler  
\- \*\*Que hace:\*\* guia el proceso de sampling para que solo sean posibles tokens gramaticalmente validos segun el schema del ECS. Compila la gramatica de forma incremental. En V3\_01 integra con EAGLE-3 y TALON via bridge.  
\- \*\*Capa de origen:\*\* Capa 5  
\- \*\*RES que lo definen:\*\* RES.054 (XGrammar-2)  
\- \*\*Dependencias:\*\* ECS schema (Capa 4), EAGLE-3/TALON/CAST (bridge para especulacion restringida), Capa 9 (Critic valida semanticamente lo que XGrammar garantiza sintacticamente)  
\- \*\*Namespaces Redis propios:\*\* ninguno  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agentica  
\- \*\*Config file V3\_01:\*\* config\_policy.yaml (seccion inference.structured\_decoding)

\---

\#\# 3\. Resoluciones que afectan esta capa

\#\#\# RES.051 — ModelPolicy \+ model\_selector.py: cadena de fallback canonicа  
\*\*FUT asociado:\*\* M.5 \*\*Fecha:\*\* 2026-05-07 \*\*Version:\*\* V2\_46

\#\#\#\# 3.1 Problema que resolvía  
Sin politica formal de seleccion de modelos, cada agente podia llamar al modelo que quisiera. Esto generaba: consumo innecesario de modelos remotos costosos para tareas simples, falta de fallback automatico ante indisponibilidad de modelo local, imposibilidad de garantizar SLA por tipo de tarea.

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*Opcion A:\*\* cada agente elige su propio modelo — descartada: no garantiza SLA, no permite fallback centralizado.  
\- \*\*Opcion B:\*\* un modelo unico para todo — descartada: costo operativo excesivo, latencia innecesaria para tareas simples.  
\- \*\*Opcion C:\*\* ModelPolicy con cadena de fallback por perfil de inferencia — elegida.

\#\#\#\# 3.3 Decision elegida y justificacion  
ModelRouter con cadena de fallback: phi4-mini → qwen3:8b → qwen3.5:9b → gemini-2.5-flash → claude-sonnet-4. El primer modelo no es el peor sino el mas economico para el patron de carga promedio. El modelo elegido siempre es el mas economico que cumple el SLA declarado.

\#\#\#\# 3.4 Parametros resultantes  
| Parametro | Valor default | Rango | Descripcion |  
|---|---|---|---|  
| fallback\_chain\[0\] | phi4-mini | — | primer intento, local, rapido |  
| fallback\_chain\[2\] | qwen3.5:9b | — | activado si entropy \> 0.65 o domain="critical" |  
| fallback\_chain\[4\] | claude-sonnet-4 | — | ultimo recurso remoto |

\#\#\#\# 3.5 Namespaces Redis  
\- Ninguno directo — seleccion stateless

\#\#\#\# 3.6 Integraciones con otras capas  
\- Capa 3: envia InferenceRequest con perfil declarado  
\- Capa 4: InferenceProfile del AgentCard define quality\_floor y budget\_tokens  
\- Capa 14: config\_policy.yaml contiene la cadena y SLA profiles

\#\#\#\# 3.7 OTel spans definidos  
\- Span \`model.selection\`: atributos: task\_id, agent\_id, model\_selected, fallback\_reason, profile\_used

\#\#\#\# 3.8 Trampa educativa  
La trampa: "el primer modelo de la cadena es el peor porque es el mas simple". La respuesta correcta: el primer modelo es el mas economico para el patron de carga promedio de MPAT. La jerarquia es de costo, no de calidad absoluta. El modelo elegido siempre es el mas economico que cumple el SLA declarado para esa tarea especifica.

\---

\#\#\# RES.052 — ShadowRadix \+ CSA/HCA: atencion optimizada para largo contexto  
\*\*FUT asociado:\*\* FUT\_3.1 \*\*Fecha:\*\* 2026-05-12 \*\*Version:\*\* V3\_01

\#\#\#\# 3.1 Problema que resolvía  
MPAT V3\_01 introduce Unikernel por usuario y SubQ asincrona, lo que implica que el contexto del agente puede crecer hasta 128K-256K tokens en sesiones largas (historial \+ ECS completo \+ memoria semantica activa). Con full attention O(n²), para 256K tokens son 65 mil millones de operaciones por cabeza de atencion — impracticable en tiempo real. Sin solucion, el TTFT se triplicaria y los SLAs de §5.3 se romperien sistematicamente.

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*Opcion A:\*\* limitar el contexto a 32K tokens — descartada: elimina la ventaja pedagogica de sesiones largas con memoria completa.  
\- \*\*Opcion B:\*\* ShadowRadix solo (KV Cache compartido) — parcial: no resuelve contextos unicos por usuario sin prefijos compartibles.  
\- \*\*Opcion C:\*\* CSA/HCA solo (atencion jerarquica) — parcial: no aprovecha prefijos comunes entre usuarios del mismo tenant.  
\- \*\*Opcion D:\*\* ShadowRadix \+ CSA/HCA combinados (complementarios) — elegida.

\#\#\#\# 3.3 Decision elegida y justificacion  
ShadowRadix extiende RadixAttention de SGLang con un indice shadow de tres tiers (hot GPU / warm CPU / cold NVMe). Reutiliza fragmentos de KV Cache entre usuarios cuando comparten prefijos (ej: system prompt identico para todos los usuarios de un tenant). CSA/HCA actua sobre el mecanismo de atencion para contextos unicos: CSA divide el contexto en ventanas de 4K tokens con atencion cruzada selectiva entre las top-K ventanas mas relevantes; HCA construye una representacion jerarquica en tres niveles (token / segmento 4K / global 64K). Ambos son complementarios: ShadowRadix actua en la capa de almacenamiento, CSA/HCA en la capa de computo. El sistema elige automaticamente segun hit\_rate medido en tiempo real.

\#\#\#\# 3.4 Parametros resultantes  
| Parametro | Valor default | Rango | Descripcion |  
|---|---|---|---|  
| long\_context.threshold\_tokens | 32768 | \[8192, 131072\] | activa optimizaciones si se supera |  
| shadowradix.hot\_tier\_ttl\_seconds | 5 | \[1, 60\] | TTL en GPU RAM |  
| shadowradix.warm\_tier\_ttl\_seconds | 60 | \[10, 600\] | TTL en CPU RAM |  
| shadowradix.cold\_offload | true | bool | requiere NVMe local \>500 GB/s |  
| csa.window\_size\_tokens | 4096 | \[1024, 8192\] | tamano de ventana local |  
| csa.cross\_attention\_top\_k | 8 | \[2, 32\] | ventanas no contiguas examinadas |  
| hca.level3\_granularity | 65536 | \[32768, 131072\] | tokens por vector global |  
| hca.level2\_granularity | 4096 | \[1024, 8192\] | tokens por vector de segmento |

\#\#\#\# 3.5 Namespaces Redis  
\- \`mpat:kv\_cache:{tenant}:hot:{prefix\_hash}\` TTL=5s GPU RAM (ShadowRadix hot tier)  
\- \`mpat:kv\_cache:{tenant}:warm:{prefix\_hash}\` TTL=60s CPU RAM (ShadowRadix warm tier)

\#\#\#\# 3.6 Integraciones con otras capas  
\- Capa 4: tamanio del contexto del ECS determina activacion  
\- Capa 10: span \`inference.longcontext\` con atributos strategy, kv\_hit\_rate, threshold\_tokens  
\- Capa 14: parametros en config\_policy.yaml seccion inference.long\_context

\#\#\#\# 3.7 OTel spans definidos  
\- Span \`inference.longcontext\`: atributos: strategy (ShadowRadix/CSA/HCA/combined), threshold\_tokens, kv\_hit\_rate, ttft\_ms\_before, ttft\_ms\_after

\#\#\#\# 3.8 Trampa educativa  
La trampa: "con mas contexto, el modelo sabe mas, por lo tanto es siempre mejor dar todo el contexto posible". La respuesta correcta: mas contexto tiene costo cuadratico en atencion, lo que puede triplicar el TTFT y romper los SLAs (§5.3). El objetivo de ShadowRadix \+ CSA/HCA es mantener el TTFT dentro del SLA aunque el contexto crezca. Mas contexto no es gratis, y en MPAT el presupuesto de latencia es tan real como el de dinero.

\---

\#\#\# RES.053 — NVFP4: cuantizacion FP4 en hardware NVIDIA Blackwell  
\*\*FUT asociado:\*\* FUT\_3.2 \*\*Fecha:\*\* 2026-05-12 \*\*Version:\*\* V3\_01

\#\#\#\# 3.1 Problema que resolvía  
MPAT ya usa INT8 (SmoothQuant, RES.036). En 2026, NVIDIA introduce soporte nativo para FP4 en arquitecturas Blackwell (B100, B200). FP4 comprime el modelo 4x vs BF16 y 2x vs INT8, pero mantiene mas rango dinamico que INT4 clasico porque usa punto flotante y no entero. Sin una politica formal de cuando usar NVFP4, el sistema no puede aprovechar el hardware Blackwell disponible sin riesgo de degradar la calidad ECS por debajo del quality\_floor del agente.

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*Opcion A:\*\* NVFP4 para todos los modelos en cualquier hardware — descartada: en Hopper (H100) la ganancia vs INT8 es marginal (\<12% throughput) y la degradacion de calidad no esta justificada.  
\- \*\*Opcion B:\*\* INT4 clasico — descartada: mayor perdida de calidad (-4.3% vs \-2.1% de NVFP4) sin ventaja de rango dinamico.  
\- \*\*Opcion C:\*\* QuantizationSelector con decision por hardware \+ quality\_floor — elegida.

\#\#\#\# 3.3 Decision elegida y justificacion  
NVFP4 es la opcion optima exclusivamente en hardware Blackwell (B100/B200). En Hopper/Ampere, INT8 sigue siendo optimal. El QuantizationSelector decide automaticamente segun hardware y quality\_floor del agente: si quality\_floor \< 0.95, acepta la degradacion del 2.1% de NVFP4 en Blackwell. Si quality\_floor \>= 0.95, usa INT8 aunque haya Blackwell disponible.

\#\#\#\# 3.4 Parametros resultantes  
| Parametro | Valor default | Rango | Descripcion |  
|---|---|---|---|  
| quantization.auto\_select | true | bool | usa QuantizationSelector automaticamente |  
| nvfp4.enabled | false | bool | requiere hardware Blackwell explicito |  
| nvfp4.hardware\_allowlist | \[B100, B200\] | lista | hardware donde NVFP4 es optimo |  
| nvfp4.max\_quality\_degradation | 0.021 | \[0.0, 0.05\] | si se supera, fallback a int8 |  
| int8.enabled | true | bool | default activo |  
| int8.smoothquant\_alpha | 0.85 | \[0.5, 1.0\] | factor de suavizado SmoothQuant |

\#\#\#\# 3.5 Namespaces Redis  
\- Ninguno directo

\#\#\#\# 3.6 Integraciones con otras capas  
\- Capa 4: quality\_floor del InferenceProfile determina si NVFP4 es aceptable  
\- Capa 10: span \`inference.quantization\` con atributos format, hardware, quality\_floor  
\- Capa 14: config\_policy.yaml seccion inference.quantization

\#\#\#\# 3.7 OTel spans definidos  
\- Span \`inference.quantization\`: atributos: format (nvfp4/int8/bf16), hardware, quality\_floor, throughput\_gain\_estimated

\#\#\#\# 3.8 Trampa educativa  
La trampa: "4 bits es mejor que 8 bits porque ocupa menos". La respuesta correcta: NVFP4 tiene mejor rango dinamico que INT4, pero aun pierde precision vs INT8. En MPAT, una degradacion del 2.1% en calidad ECS puede representar 2 campos criticos incorrectos en cada 100 tasks. El decision point no es cuanto ahorro, sino si puedo permitirme ese nivel de degradacion dado el quality\_floor del agente actual. La respuesta correcta siempre viene del contrato de calidad, no del hardware disponible.

\---

\#\#\# RES.054 — XGrammar-2: decoding gramatical restringido v2  
\*\*FUT asociado:\*\* FUT\_3.3 \*\*Fecha:\*\* 2026-05-12 \*\*Version:\*\* V3\_01

\#\#\#\# 3.1 Problema que resolvía  
Los agentes MPAT deben generar salidas siempre validas para el ECS: JSON con schema definido, codigo Python sintacticamente correcto, campos con tipo y rango fijos. Un token invalido en medio de un JSON rompe el pipeline completo. XGrammar v1 (2025) resolvia esto pero tenia dos problemas criticos para MPAT: overhead de 12ms por token (inaceptable para SLA emit \<20ms/tok) y overhead de compilacion inicial de 180-250ms antes del primer token. Ademas, no era compatible con EAGLE-3 ni TALON porque el draft model no conocia las restricciones gramaticales del target.

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*Opcion A:\*\* post-procesamiento: generar libremente y corregir el JSON despues — descartada: no garantiza validez si el modelo alucina estructuralmente.  
\- \*\*Opcion B:\*\* XGrammar v1 sin modificacion — descartada: 12ms/token y 200ms overhead inicial rompen SLAs.  
\- \*\*Opcion C:\*\* XGrammar-2 con compilacion incremental \+ pesos semanticos \+ bridge especulativo — elegida.

\#\#\#\# 3.3 Decision elegida y justificacion  
XGrammar-2 introduce tres mejoras criticas: (1) compilacion incremental — compila solo el delta de la gramatica por token, reduciendo overhead de 12ms a 0.8ms; (2) gramaticas probabilisticas adaptativas — tokens mas probables segun el schema del ECS reciben boost de probabilidad (semantic\_weight=0.15); (3) integracion nativa con EAGLE-3 y TALON via bridge — el draft model especula con la mascara de tokens validos, elevando el acceptance rate de 89% a 94%. INV\_5\_22\_1: XGrammar-2 garantiza validez SINTACTICA siempre, no semantica. La validacion semantica definitiva sigue siendo responsabilidad de Capa 9 (Critic Agent).

\#\#\#\# 3.4 Parametros resultantes  
| Parametro | Valor default | Rango | Descripcion |  
|---|---|---|---|  
| xgrammar\_version | 2 | \[1, 2\] | "1" para retrocompatibilidad |  
| semantic\_weight | 0.15 | \[0.0, 0.3\] | boost semantico (0.0 \= comportamiento v1) |  
| incremental\_compile | true | bool | compilacion incremental (default on en v2) |  
| eagle\_bridge.enabled | true | bool | integracion con EAGLE-3 |  
| talon\_bridge.enabled | true | bool | integracion con TALON/CAST |

\#\#\#\# 3.5 Namespaces Redis  
\- Ninguno directo

\#\#\#\# 3.6 Integraciones con otras capas  
\- Capa 4: schema del ECS define las restricciones gramaticales  
\- Capa 9: Critic valida semanticamente lo que XGrammar garantiza sintacticamente  
\- Capa 10: span \`inference.xgrammar\` con atributos version, overhead\_ms, acceptance\_rate\_with\_speculative

\#\#\#\# 3.7 OTel spans definidos  
\- Span \`inference.xgrammar\`: atributos: version, schema\_id, compilation\_ms (inicial), overhead\_per\_token\_ms, semantic\_weight, eagle\_bridge\_active, acceptance\_rate\_boost

\#\#\#\# 3.8 Trampa educativa  
La trampa: "XGrammar garantiza que el JSON sea correcto". La respuesta correcta: XGrammar garantiza que el JSON sea SINTACTICAMENTE valido. Un JSON puede ser sintacticamente perfecto y semanticamente absurdo: \`{"edad": \-999, "nombre": "", "prioridad": "INEXISTENTE"}\` pasa el schema pero es un ECS corrupto. Por eso Capa 9 (Critic Agent) existe y no puede ser eliminada aunque XGrammar-2 mejore la calidad semantica.

\---

\#\# 4\. Integracion V3\_01 — Cadena critica A2A \+ SubQ \+ Unikernel

\[NO APLICA — Capa 5 es interna de computo. No es punto de entrada ni salida de A2A, SubQ ni Unikernel. Recibe de Capa 3 y retorna a Capa 4.\]

\---

\#\# 5\. Estado final de la capa en V3\_01

\*\*Componentes activos:\*\*  
\- ModelRouter con cadena de fallback canonicа (5 modelos: phi4-mini → qwen3:8b → qwen3.5:9b → gemini-2.5-flash → claude-sonnet-4)  
\- 19 optimizaciones activas simultaneamente (todas aditivas — INV\_5\_2)  
\- ShadowRadix \+ CSA/HCA: ACTIVO (threshold 32K tokens, cold offload a NVMe)  
\- NVFP4: OPT-IN (solo hardware Blackwell B100/B200)  
\- XGrammar-2: ACTIVO (version 2, compilacion incremental, bridge EAGLE-3 y TALON)  
\- EAGLE-3 como especulacion default para synthesis; TALON para alta ambiguedad; CAST para domain-aware

\*\*Cambios respecto a V2\_102:\*\*  
\- §5.20 NUEVO: ShadowRadix \+ CSA/HCA (RES.052) — no existia en V2  
\- §5.21 NUEVO: NVFP4 (RES.053) — no existia en V2  
\- §5.22 NUEVO: XGrammar-2 (RES.054) — v1 existia; v2 con bridge especulativo es nueva  
\- qwen3.5:9b agregado como tercer eslabon local (RES.051 / V2\_46)

\*\*Metricas objetivo vigentes:\*\*  
\- TTFT \< 500ms (Tier Standard) / 340ms con ShadowRadix+CSA/HCA en contexto 256K  
\- TPOT \< 25ms/tok (standard) / \<20ms/tok para perfil emit  
\- Throughput \> 10.000 tok/s/GPU  
\- Acceptance Rate \> 90% (EAGLE-3 en MPAT workload: 89% → 94% con XGrammar-2 bridge)

\---

\#\# 6\. Flujo de datos completo

\`\`\`  
Capa 3 (Orchestrator) → InferenceRequest {task\_type, profile\_id, context, budget\_tokens}  
  ↓  
ModelRouter.select\_model(profile)  
  → verifica disponibilidad y SLA por modelo en cadena de fallback  
  → retorna model\_id \+ quantization\_format  
  ↓  
LongContextManager (si context \> 32768 tokens)  
  → ShadowRadix: busca KV Cache hit en hot/warm/cold tier  
  → si hit rate \< umbral: activa CSA/HCA para atencion jerarquica  
  → OTel span: inference.longcontext {strategy, kv\_hit\_rate, ttft\_before}  
  ↓  
QuantizationSelector  
  → segun hardware y quality\_floor: nvfp4 | int8 | bf16  
  → OTel span: inference.quantization {format, hardware, quality\_floor}  
  ↓  
InferenceExecutor  
  → activa modo especulativo: EAGLE-3 | TALON | CAST (segun perfil)  
  → si structured output: XGrammar2Sampler con schema del ECS  
    → bridge EAGLE-3/TALON para especulacion restringida  
  → ejecuta inferencia con optimizaciones activas (§5.11-§5.19)  
  → mide TTFT y TPOT por fase (prefill / decode)  
  → OTel span: inference.execute {ttft\_ms, tpot\_ms, model\_id, acceptance\_rate}  
  ↓  
Resultado → Capa 4 (InferenceResult con output \+ metricas)  
PolicyEnforcer (Capa 14\) → audita cada decision de seleccion de modelo  
\`\`\`

\---

\#\# 7\. Config files V3\_01

| Config file | Parametros clave | RES origen |  
|---|---|---|  
| config\_policy.yaml § inference.fallback\_chain | cadena de 5 modelos, criterio de activacion qwen3.5:9b | RES.051 |  
| config\_policy.yaml § inference.sla\_profiles | TTFT/TPOT max por tipo de tarea (emit/analysis/synthesis/critical) | RES.020-024 |  
| config\_policy.yaml § inference.long\_context | threshold\_tokens, shadowradix tiers TTL, csa window\_size, hca granularity | RES.052 |  
| config\_policy.yaml § inference.quantization | auto\_select, nvfp4 allowlist, max\_quality\_degradation, int8 smoothquant\_alpha | RES.053 |  
| config\_policy.yaml § inference.structured\_decoding | xgrammar\_version, semantic\_weight, incremental\_compile, eagle/talon bridge | RES.054 |  
| config\_policy.yaml § inference.speculative | enabled, draft\_model, draft\_tokens\_k, acceptance\_threshold, avoid\_speculative TTL | RES.017, RES.020 |

\---

\#\# 8\. Puntos de atencion para implementacion

1\. \*\*INV\_5\_1 (cadena de fallback):\*\* la cadena no es un ranking de calidad. NO modificar el orden asumiendo que "modelo mas avanzado \= mejor para esta tarea". El ModelRouter usa el mas economico que cumple el SLA.

2\. \*\*INV\_5\_2 (optimizaciones aditivas):\*\* las optimizaciones §5.11-§5.19 son TODAS activas simultaneamente. Ninguna desactiva a otra. La configuracion activa en produccion es la suma de todas las marcadas ACTIVO.

3\. \*\*INV\_5\_20\_1 (ShadowRadix vs CSA/HCA):\*\* son complementarios, no alternativos. ShadowRadix actua en almacenamiento (KV Cache), CSA/HCA actua en computo (mecanismo de atencion). Pueden estar activos simultaneamente sin conflicto.

4\. \*\*INV\_5\_21\_1 (NVFP4):\*\* NVFP4 NO reemplaza INT8 en hardware Hopper (H100/H200). La ganancia en H100 es marginal (\<12% throughput). NVFP4 es optimo exclusivamente en Blackwell (B100/B200).

5\. \*\*INV\_5\_22\_1 (XGrammar-2):\*\* garantiza validez SINTACTICA, no semantica. Capa 9 (Critic) no puede eliminarse aunque XGrammar-2 mejore la calidad semantica al 93.8%.

6\. \*\*INV\_EAGLE3\_1 (draft model):\*\* el draft model de EAGLE-3 requiere reentrenamiento cada vez que el target model se actualiza. Usar draft de version anterior degrada acceptance rate a \<60%.

7\. \*\*SSD vs EAGLE-3:\*\* EAGLE-3, TALON y CAST son mutuamente excluyentes por request. Solo uno puede estar activo. El sistema elige automaticamente segun el perfil de la tarea (§5.1).

8\. \*\*Cold tier NVMe:\*\* ShadowRadix cold\_offload requiere NVMe local con \>500 GB/s de throughput. Sin este hardware, deshabilitar cold\_offload para evitar degradacion de latencia.

9\. \*\*Compilacion inicial XGrammar-2:\*\* aunque la compilacion incremental elimina el overhead por token, la primera compilacion de un schema nuevo todavia tiene overhead. Precompilar schemas frecuentes del ECS en startup.

\---

\#\# 9\. Datos faltantes o inconsistencias detectadas

1\. \*\*Draft model EAGLE-3 para qwen3.5:9b (PENDIENTE activo):\*\* la integracion de qwen3.5:9b (RES.051) requiere un draft model especifico. El draft actual (entrenado para qwen3:8b) opera con acceptance rate degradado (\~71%) en qwen3.5:9b. No hay RES abierta para resolverlo — requiere nueva RES en RELAY\_006.

2\. \*\*Knowledge Graph RAG en Capa 5 (FUT\_4 candidato):\*\* conectar busqueda vectorial semantica con un grafo de conceptos para saltos logicos en contextos largos. Estado: investigacion activa, sin RES asignada.

3\. \*\*Long-term Episodic Memory en Capa 5:\*\* sistema de memoria que recuerde el patron de errores por agente para personalizar el draft model de EAGLE-3. Requiere coordinacion con Capa 8\. Sin RES asignada.

4\. \*\*SSD en produccion:\*\* la tabla de optimizaciones marca SSD (RES.021) como ACTIVO pero el MASTER indica que SSD tiene peor performance que EAGLE-3 estandar si la tasa de prediccion del micro-draft cae a \<80%. No hay criterio formal documentado para cuando SSD debe ceder a EAGLE-3. \[DATO FALTANTE — requiere parametro de umbral en config\_policy.yaml\]

\---

\*INFORME\_CAPA\_05\_V3\_01.md · AGT 2026-05-13 · cursos.au.agt@gmail.com\*  
\*Generado en RELAY\_004 · cursos.au.agt@gmail.com · 2026-05-13\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
