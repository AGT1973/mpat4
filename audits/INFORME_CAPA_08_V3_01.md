\# INFORME CAPA 08 — MEMORIA: Dream Cycle · Ori-Mnemos RMH · Aprendizaje Hebbiano  
\*\*Version fuente:\*\* V3\_01  
\*\*Alumno:\*\* cursos.agt.ia@gmail.com  
\*\*Fecha:\*\* 2026-05-14  
\*\*RES que afectan esta capa:\*\* RES.004, RES.081, RES.096, RES.119  
\*\*Paradigma predominante:\*\* Co-evolution Human-AI / Post-Automation Paradigm

\---

\#\# 1\. Descripción de la capa

La Capa 8 es el sistema de memoria persistente de MPAT. Su responsabilidad es garantizar  
que el conocimiento generado por agentes efímeros (Capa 4\) no se pierda entre ejecuciones,  
y que el sistema mejore progresivamente su capacidad de recuperación de información a  
medida que acumula experiencia por tenant.

En V2\_x, la capa era un almacén pasivo: guardaba fragmentos y los recuperaba por similitud  
semántica. En V3\_01, pasa a ser un sistema cognitivo activo con tres mecanismos nuevos:

\- \*\*Dream Cycle (8.6):\*\* consolida memoria entre ejecuciones (asíncrono, solo en idle).  
\- \*\*Ori-Mnemos RMH (8.7):\*\* reranking de fragmentos por valor instrumental histórico (Q-Value).  
\- \*\*Aprendizaje Hebbiano (8.8):\*\* fortalece conexiones entre fragmentos que co-aparecen en tareas exitosas.

Esta capa NO es punto de entrada o salida para A2A (RES.113), SubQ (RES.114) ni Unikernel (RES.115).  
Su aislamiento multi-tenant es estricto por colección vectorial, namespace Redis y pesos hebbianos.

\---

\#\# 2\. Componentes de la capa

\#\#\# 2.1 — Memoria Activa  
\- \*\*Qué hace:\*\* almacena el contexto inmediato de la ejecución en curso (window del modelo). Se libera en estado \`DESTROY\`. En V3\_01, antes del DESTROY guarda su contenido como \`dream\_buffer\` en Redis para el próximo Dream Cycle.  
\- \*\*Capa de origen:\*\* 8  
\- \*\*RES que lo definen:\*\* RES.096 (feed al Dream Cycle)  
\- \*\*Dependencias:\*\* Capa 4 (agentes efímeros producen el contexto), Capa 14 (policy.yaml)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:dream:{tenant\_id}:buffer\` TTL=3600s List\[JSON\]  
\- \*\*Paradigma:\*\* Co-evolution Human-AI — el contexto activo es la base del aprendizaje futuro.  
\- \*\*Config file V3\_01:\*\* \`config/dream\_cycle.yaml\`

\#\#\# 2.2 — Memoria Vectorial Persistente  
\- \*\*Qué hace:\*\* base de datos vectorial (ChromaDB default, FAISS alternativa). Colecciones aisladas por tenant: \`f"{tenant\_id}\_{source\_group}"\`. Búsquedas solo dentro de la colección del tenant activo. En V3\_01 cada vector incluye el campo \`hebbian\_weight\` (float, default 1.0).  
\- \*\*Capa de origen:\*\* 8  
\- \*\*RES que lo definen:\*\* RES.004 (clave con tenant\_id), RES.081 (P2P)  
\- \*\*Dependencias:\*\* Capa 3 (sesión activa), Capa 14 (policy.yaml)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:pv:{tenant\_id}:shared:{concept\_hash}\` TTL=2592000s Hash (P2P)  
\- \*\*Paradigma:\*\* Co-evolution Human-AI  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\`

\#\#\# 2.3 — Context Pruning  
\- \*\*Qué hace:\*\* cuando la ventana de contexto se acerca al límite, elimina fragmentos con \`score \* hebbian\_weight \< retention\_threshold\`. En V3\_01 un fragmento de baja similitud puntual puede ser retenido si su peso hebbiano histórico es alto.  
\- \*\*Capa de origen:\*\* 8  
\- \*\*RES que lo definen:\*\* RES.119 (vía hebbian\_weight), RES.096  
\- \*\*Dependencias:\*\* Capa 8.2 (vectores), Capa 8.8 (pesos)  
\- \*\*Namespaces Redis propios:\*\* ninguno propio — opera sobre Memoria Vectorial  
\- \*\*Paradigma:\*\* Post-Automation Paradigm — decisión autónoma sobre qué olvidar.  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\` (\`context\_pruning\_threshold\`)

\#\#\# 2.4 — Semantic Caching  
\- \*\*Qué hace:\*\* caché de respuestas del modelo con clave \`hash(tenant\_id \+ prompt \+ model\_id)\`. Ahorro estimado 40–70% de tokens en consultas similares recurrentes.  
\- \*\*Capa de origen:\*\* 8  
\- \*\*RES que lo definen:\*\* RES.004 — corrección de seguridad que añadió \`tenant\_id\` a la clave desde V2\_02.  
\- \*\*Dependencias:\*\* Capa 1 (API Gateway), Capa 14  
\- \*\*Namespaces Redis propios:\*\* no especificado en MASTER — operar con clave compuesta indicada.  
\- \*\*Paradigma:\*\* Post-Automation Paradigm  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\` (\`semantic\_cache\_ttl\`)

\#\#\# 2.5 — P2P Learning  
\- \*\*Qué hace:\*\* sincroniza conceptos bien consolidados entre alumnos del mismo tenant (con \`consent=True\`). \`contributed\_by\` siempre anonimizado. Nunca cruza \`tenant\_id\`.  
\- \*\*Capa de origen:\*\* 8  
\- \*\*RES que lo definen:\*\* RES.081 (FUT.29 V2\_75)  
\- \*\*Dependencias:\*\* Capa 6 (ECS — consent flag)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:pv:{tenant\_id}:shared:{concept\_hash}\` TTL=2592000s JSON  
\- \*\*Paradigma:\*\* Co-evolution Human-AI — alumnos y sistema co-evolucionan compartiendo conocimiento.  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\` (\`p2p\_min\_confidence\`, \`p2p\_shared\_ttl\_seconds\`)

\#\#\# 2.6 — DreamCycleProcessor \[V3\_01 NUEVO\]  
\- \*\*Qué hace:\*\* proceso asíncrono que activa el Dream Cycle cuando el tenant está en idle ≥ \`dream\_cycle\_interval\_s\` (default 300s). Ejecuta 5 pasos: recolección del buffer → detección de co-activaciones → consolidación vía Ori-Mnemos → actualización de \`hebbian\_weight\` en Memoria Vectorial → poda de stale → limpieza del buffer.  
\- \*\*Capa de origen:\*\* 8  
\- \*\*RES que lo definen:\*\* RES.096  
\- \*\*Dependencias:\*\* 8.1 (buffer), 8.2 (vectores), 8.7 (Ori-Mnemos), 8.8 (HebbianManager)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:dream:{tenant\_id}:buffer\` TTL=3600s List  
\- \*\*Paradigma:\*\* Co-evolution Human-AI — consolida mientras el humano no interactúa.  
\- \*\*Config file V3\_01:\*\* \`config/dream\_cycle.yaml\`

\#\#\# 2.7 — OriMnemosRMH \[V3\_01 NUEVO\]  
\- \*\*Qué hace:\*\* reranking de fragmentos de memoria combinando similitud semántica (60%) y Q-Value histórico (40%). Fórmula: \`score \= alpha\_semantic \* cos\_sim \+ alpha\_qvalue \* q\_normalized\`. Q-Value actualizado por Bellman: \`Q(s,a) ← Q(s,a) \+ α\[r \+ γ max Q(s',a') − Q(s,a)\]\`. Q-Value clampeado en \[-1.0, 2.0\].  
\- \*\*Capa de origen:\*\* 8  
\- \*\*RES que lo definen:\*\* RES.119  
\- \*\*Dependencias:\*\* 8.6 (DreamCycle), 8.2 (vectores)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:rmh:{tenant\_id}:qval:{fragment\_id}\` TTL=7776000s (90d) float  
\- \*\*Paradigma:\*\* Post-Automation Paradigm — decisión autónoma sobre valor instrumental de la memoria.  
\- \*\*Config file V3\_01:\*\* \`config/dream\_cycle.yaml\` (\`qvalue\_alpha\`, \`qvalue\_gamma\`, \`rerank\_alpha\_semantic\`, \`rerank\_alpha\_qvalue\`)

\#\#\# 2.8 — HebbianManager \[V3\_01 NUEVO\]  
\- \*\*Qué hace:\*\* gestiona los pesos de conexión entre fragmentos de memoria. \`strengthen(a, b, reward)\` incrementa el peso de ambos fragmentos si \`reward \> 0\`. \`apply\_decay\` aplica decaimiento hacia baseline (1.0) durante el Dream Cycle. Pesos clampeados en \[0.1, 3.0\].  
\- \*\*Capa de origen:\*\* 8  
\- \*\*RES que lo definen:\*\* RES.096 (via Dream Cycle), RES.119 (via Ori-Mnemos)  
\- \*\*Dependencias:\*\* 8.6 (DreamCycleProcessor ejecuta el decay)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:hebbian:{tenant\_id}:{fragment\_id}\` TTL=7776000s (90d) float  
\- \*\*Paradigma:\*\* Co-evolution Human-AI — el sistema aprende qué recuerdos van juntos.  
\- \*\*Config file V3\_01:\*\* \`config/dream\_cycle.yaml\` (\`hebbian\_eta\`, \`hebbian\_decay\`, \`hebbian\_min\`, \`hebbian\_max\`)

\---

\#\# 3\. Resoluciones que afectan esta capa

\#\#\# RES.004 — Semantic Cache Key con tenant\_id  
\*\*FUT asociado:\*\* FUT corrección de seguridad V2\_02 \*\*Fecha:\*\* 2026 \*\*Versión:\*\* V2\_02 → vigente en V3\_01

\#\#\#\# 3.1 Problema que resolvía  
Sin \`tenant\_id\` en la clave del semantic cache, un tenant podía recuperar respuestas  
cacheadas de otro tenant si sus queries eran semánticamente similares (Key Collision Attack).  
Evidencia formal: arxiv.org/pdf/2601.23088 (HKUST \+ Fudan, 2026).

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*Opción A:\*\* Clave solo por \`hash(prompt \+ model\_id)\` — descartada por vulnerabilidad de colisión entre tenants.  
\- \*\*Opción B:\*\* Clave \`hash(tenant\_id \+ prompt \+ model\_id)\` — elegida: incluye el aislamiento requerido.  
\- \*\*Opción C:\*\* Desactivar semantic cache — descartada: elimina ahorro de 40–70% de tokens.

\#\#\#\# 3.3 Decisión elegida y justificación  
Clave \`hash(tenant\_id \+ prompt \+ model\_id)\` obligatoria. El \`tenant\_id\` actúa como salt  
semántico que garantiza que colecciones distintas no se contaminen en el cache, manteniendo  
el ahorro de tokens sin sacrificar el aislamiento multi-tenant.

\#\#\#\# 3.4 Parámetros resultantes  
| Parámetro | Valor default | Rango | Descripción |  
|---|---|---|---|  
| \`semantic\_cache\_ttl\` | 86400 s | 300–604800 | TTL del cache semántico por tenant |

\#\#\#\# 3.5 Namespaces Redis  
\- Clave: \`hash(tenant\_id \+ prompt \+ model\_id)\` — TTL configurable, tipo string (respuesta modelo)

\#\#\#\# 3.6 Integraciones con otras capas  
Capa 1 (API Gateway) es quien ejecuta la consulta al semantic cache antes de llamar al LLM.  
Capa 14 (policy.yaml) controla el TTL por dominio y nivel de sensibilidad.

\#\#\#\# 3.7 OTel spans definidos  
\- Span \`cache.semantic.hit\`: atributos: \`tenant\_id\`, \`model\_id\`, \`prompt\_hash\`, \`ttl\_remaining\`  
\- Span \`cache.semantic.miss\`: atributos: \`tenant\_id\`, \`model\_id\`, \`prompt\_hash\`

\#\#\#\# 3.8 Trampa educativa  
\*\*La trampa:\*\* "Si dos usuarios hacen la misma pregunta, el sistema les devuelve la misma respuesta cacheada, lo que es más eficiente."  
\*\*La respuesta correcta:\*\* la respuesta cacheada se devuelve solo si coincide el \`tenant\_id\`. Si los usuarios pertenecen a tenants distintos, sus caches son completamente independientes aunque la pregunta sea idéntica. La eficiencia (40–70% de ahorro) aplica \*\*dentro\*\* del mismo tenant, no entre tenants.

\---

\#\#\# RES.081 — P2P Learning con anonimización  
\*\*FUT asociado:\*\* FUT.29 \*\*Fecha:\*\* 2026-05-12 (V2\_75) \*\*Versión:\*\* V2\_75 → vigente en V3\_01

\#\#\#\# 3.1 Problema que resolvía  
Los alumnos del mismo tenant aprendían en silos completamente aislados. Un alumno que  
consolidó bien un concepto no podía enriquecer el aprendizaje de otros alumnos del mismo tenant.

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*Opción A:\*\* Compartir memorias completas entre alumnos — descartada: viola privacidad individual.  
\- \*\*Opción B:\*\* Pool de conceptos anonimizados con \`consent=True\` — elegida: equilibra colaboración y privacidad.  
\- \*\*Opción C:\*\* Compartir entre tenants — descartada: viola invariante de aislamiento multi-tenant absoluto.

\#\#\#\# 3.3 Decisión elegida y justificación  
Solo se comparten conceptos con \`confidence \>= 0.75\` y \`consent=True\` en el ECS del alumno.  
El \`contributed\_by\` es siempre el SHA256\[:16\] del \`session\_id\` (anonimizado). Nunca se cruza \`tenant\_id\`.

\#\#\#\# 3.4 Parámetros resultantes  
| Parámetro | Valor default | Rango | Descripción |  
|---|---|---|---|  
| \`p2p\_min\_confidence\` | 0.75 | 0.5–1.0 | Confianza mínima para contribuir |  
| \`p2p\_shared\_ttl\_seconds\` | 2592000 | 86400–7776000 | TTL pool compartido (30d default) |

\#\#\#\# 3.5 Namespaces Redis  
\- \`mpat:pv:{tenant\_id}:shared:{concept\_hash}\` TTL=2592000s JSON \[RES.081\]

\#\#\#\# 3.6 Integraciones con otras capas  
Capa 6 (ECS) proporciona el flag \`consent\` del alumno. Capa 4 (agentes) son los generadores  
del conocimiento que puede ser candidato a contribución P2P.

\#\#\#\# 3.7 OTel spans definidos  
\- Span \`p2p.contribute\`: atributos: \`tenant\_id\`, \`concept\_hash\`, \`confidence\`, \`consent\`  
\- Span \`p2p.fetch\_shared\`: atributos: \`tenant\_id\`, \`concept\_hash\`, \`hit\`

\#\#\#\# 3.8 Trampa educativa  
\*\*La trampa:\*\* "El P2P Learning permite que alumnos de distintas organizaciones se beneficien del conocimiento de otros, haciendo el sistema más inteligente globalmente."  
\*\*La respuesta correcta:\*\* el P2P Learning opera estrictamente dentro del mismo \`tenant\_id\`. Cruzar \`tenant\_id\` viola INV-8-P2P.3 y está prohibido. No existe aprendizaje global entre tenants.

\---

\#\#\# RES.096 — Dream Cycle V3\_01  
\*\*FUT asociado:\*\* FUT\_3 (Dream Cycle) \*\*Fecha:\*\* 2026-05-12 \*\*Versión:\*\* V3\_01

\#\#\#\# 3.1 Problema que resolvía  
En V2\_x la memoria era un almacén pasivo: lo que se guardaba permanecía con el mismo peso  
indefinidamente hasta expirar por TTL. No había mecanismo para consolidar, priorizar ni  
descubrir patrones entre memorias en momentos de baja actividad.

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*Opción A:\*\* Consolidación síncrona durante la ejecución — descartada: aumenta latencia del pipeline activo.  
\- \*\*Opción B:\*\* Job batch nocturno (cron) — descartada: desconectado del ritmo real de uso del tenant.  
\- \*\*Opción C:\*\* Dream Cycle asíncrono activado por idle del tenant — elegida: opera cuando no interfiere con el usuario, análogo al sueño REM biológico.

\#\#\#\# 3.3 Decisión elegida y justificación  
El DreamCycleProcessor se activa cuando el orquestador detecta idle ≥ 300s para el tenant.  
Opera sobre el \`dream\_buffer\` (fragmentos de la Memoria Activa del ciclo anterior). Consolida  
por co-activación, actualiza \`hebbian\_weight\` en Memoria Vectorial, marca stale los de baja  
relevancia histórica, y limpia el buffer. No puede ejecutarse durante ejecución activa (INV-8-DC.1).

\#\#\#\# 3.4 Parámetros resultantes  
| Parámetro | Valor default | Rango | Descripción |  
|---|---|---|---|  
| \`dream\_cycle\_interval\_s\` | 300 | 60–3600 | Segundos de idle antes de activar |  
| \`dream\_buffer\_ttl\_s\` | 3600 | 600–86400 | TTL máximo del buffer |  
| \`HEBBIAN\_INCREMENT\` | 0.15 | — | Incremento por co-activación confirmada |  
| \`STALE\_THRESHOLD\` | 0.3 | — | Peso combinado debajo del cual \= stale |

\#\#\#\# 3.5 Namespaces Redis  
\- \`mpat:dream:{tenant\_id}:buffer\` TTL=3600s List\[JSON(DreamFragment)\] \[RES.096\]  
\- \`mpat:hebbian:{tenant\_id}:{fragment\_id}\` TTL=7776000s float \[RES.096 \+ RES.119\]

\#\#\#\# 3.6 Integraciones con otras capas  
Capa 3 (orquestador) señaliza el idle del tenant al DreamCycleProcessor.  
Capa 8.7 (Ori-Mnemos) ejecuta el reranking y consolidación dentro del Dream Cycle.  
Capa 8.8 (HebbianManager) aplica el decay de pesos durante el Dream Cycle.  
Capa 14 (policy.yaml) controla todos los parámetros.

\#\#\#\# 3.7 OTel spans definidos  
\- Span \`dream\_cycle.run\`: atributos: \`tenant\_id\`, \`processed\`, \`consolidated\`, \`stale\`, \`duration\_ms\`  
\- Span \`dream\_cycle.buffer\_load\`: atributos: \`tenant\_id\`, \`fragment\_count\`

\#\#\#\# 3.8 Trampa educativa  
\*\*La trampa:\*\* "El Dream Cycle es un proceso en segundo plano que corre continuamente para mantener la memoria actualizada mientras el usuario trabaja."  
\*\*La respuesta correcta:\*\* el Dream Cycle está estrictamente prohibido durante ejecución activa del tenant (INV-8-DC.1). Si se ejecutara durante una sesión activa, podría alterar los \`hebbian\_weight\` de fragmentos que están siendo consultados simultáneamente, generando resultados de reranking inconsistentes. Solo opera en idle.

\---

\#\#\# RES.119 — Q-Value Reranking (Ori-Mnemos RMH)  
\*\*FUT asociado:\*\* FUT\_3 (Ori-Mnemos) \*\*Fecha:\*\* 2026-05-12 \*\*Versión:\*\* V3\_01

\#\#\#\# 3.1 Problema que resolvía  
La recuperación de memoria por similitud semántica pura ignora el historial de utilidad de  
cada fragmento. Un fragmento que siempre contribuyó a tareas exitosas competía en igualdad  
de condiciones con uno nuevo sin historial, dependiendo solo de la similitud del embedding puntual.

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*Opción A:\*\* Ordenar solo por frecuencia de uso — descartada: frecuencia no implica utilidad real.  
\- \*\*Opción B:\*\* Reranking puramente por feedback explícito (RLHF) — descartada: requiere señal humana continua.  
\- \*\*Opción C:\*\* Q-Value Reranking (Bellman) \+ similitud semántica ponderada — elegida: combina señal automática de recompensa de tarea con relevancia semántica.

\#\#\#\# 3.3 Decisión elegida y justificación  
OriMnemosRMH calcula \`score \= 0.6 \* cos\_sim \+ 0.4 \* q\_normalized\` donde \`q\_normalized \= (q\_val \+ 1.0) / 3.0\`.  
El Q-Value se actualiza por Bellman con \`α=0.1, γ=0.9\`, reward=1.0 si tarea OK, \-0.5 si falla.  
Clampeado en \[-1.0, 2.0\]. La invariante \`alpha\_semantic \+ alpha\_qvalue \= 1.0\` garantiza que  
el score total siga siendo comparable entre fragmentos.

\#\#\#\# 3.4 Parámetros resultantes  
| Parámetro | Valor default | Rango | Descripción |  
|---|---|---|---|  
| \`qvalue\_alpha\` | 0.10 | 0.01–0.5 | Tasa de aprendizaje Q |  
| \`qvalue\_gamma\` | 0.90 | 0.5–0.99 | Factor de descuento Q |  
| \`rerank\_alpha\_semantic\` | 0.60 | 0.3–0.9 | Peso similitud semántica |  
| \`rerank\_alpha\_qvalue\` | 0.40 | 0.1–0.7 | Peso Q-Value |

\#\#\#\# 3.5 Namespaces Redis  
\- \`mpat:rmh:{tenant\_id}:qval:{fragment\_id}\` TTL=7776000s (90d) float \[RES.119\]

\#\#\#\# 3.6 Integraciones con otras capas  
El orquestador (Capa 3\) señaliza el resultado de la tarea (OK / falla) como reward al OriMnemosRMH.  
El DreamCycleProcessor (8.6) llama a \`rerank\_and\_consolidate\` de OriMnemosRMH.  
Capa 14 (policy.yaml) gestiona todos los parámetros Q.

\#\#\#\# 3.7 OTel spans definidos  
\- Span \`rmh.rerank\`: atributos: \`tenant\_id\`, \`fragment\_count\`, \`top\_fragment\_id\`, \`top\_score\`  
\- Span \`rmh.qvalue\_update\`: atributos: \`tenant\_id\`, \`fragment\_id\`, \`reward\`, \`new\_q\`

\#\#\#\# 3.8 Trampa educativa  
\*\*La trampa:\*\* "El Q-Value Reranking reemplaza la similitud semántica — si un fragmento tiene Q-Value alto, siempre se recupera primero independientemente de cuán relevante sea semánticamente."  
\*\*La respuesta correcta:\*\* el reranking es una ponderación, no un reemplazo (INV-8-RMH.2). La fórmula \`0.6 \* cos\_sim \+ 0.4 \* q\_normalized\` garantiza que la similitud semántica siempre pesa 60% del score final. Un fragmento con Q-Value máximo (2.0 → normalizado ≈ 1.0) pero similitud semántica 0 obtiene un score de 0.4 — puede ser superado por un fragmento nuevo con similitud 0.7 (score \= 0.42).

\---

\#\# 4\. Integración V3\_01 — Cadena crítica A2A \+ SubQ \+ Unikernel

\[NO APLICA\] — Capa 8 no es punto de entrada ni salida para A2A (RES.113), SubQ (RES.114) ni Unikernel (RES.115). Su aislamiento multi-tenant se gestiona por colección vectorial y namespace Redis, no por la cadena A2A/SubQ/Unikernel.

\---

\#\# 5\. Estado final de la capa en V3\_01

\*\*Estado:\*\* ACTIVA — todos los componentes V3\_01 implementados.

Respecto a V2\_102, los cambios son:  
\- 8.1: Memoria Activa alimenta \`dream\_buffer\` antes de DESTROY (nuevo en V3\_01)  
\- 8.2: Campo \`hebbian\_weight\` (float, default 1.0) en cada fragmento vectorial (nuevo en V3\_01)  
\- 8.3: Context Pruning considera \`score \* hebbian\_weight \> retention\_threshold\` (extendido en V3\_01)  
\- 8.6: DreamCycleProcessor — consolidación asíncrona en idle (nuevo en V3\_01)  
\- 8.7: OriMnemosRMH — Q-Value Reranking (nuevo en V3\_01)  
\- 8.8: HebbianManager — pesos de co-activación (nuevo en V3\_01)  
\- \+11 invariantes V3\_01, \+9 tests de integración, \+10 parámetros en policy.yaml

Componentes de V2 preservados sin cambios de interfaz: Semantic Caching (RES.004), P2P Learning (RES.081), Memoria Vectorial Persistente (arquitectura base).

Todos los parámetros son configurables vía \`policy.yaml\` (Capa 14\) — ninguno hardcodeado (P4 arquitectura).

\---

\#\# 6\. Flujo de datos completo

\`\`\`  
\[Agente Capa 4 en ejecución\]  
  → Memoria Activa (contexto de sesión)  
  → Semantic Cache consulta: hash(tenant\_id \+ prompt \+ model\_id) → HIT/MISS  
  → Si MISS: LLM procesa → respuesta cacheada  
  → Context Pruning: score \* hebbian\_weight \> retention\_threshold  
  → Memoria Vectorial: búsqueda por embedding en colección tenant activo  
  → OriMnemosRMH.rerank: 0.6\*cos\_sim \+ 0.4\*q\_normalized → fragmentos ordenados

\[Al finalizar la tarea\]  
  → Capa 3 señaliza resultado (OK / falla) → reward a OriMnemosRMH  
  → OriMnemosRMH.update\_q\_value: Bellman update  
  → Memoria Activa → guardada como DreamFragment en mpat:dream:{tenant\_id}:buffer  
  → Estado DESTROY: Memoria Activa liberada

\[Idle del tenant ≥ 300s\]  
  → DreamCycleProcessor.run\_cycle()  
  → Paso 1: lrange mpat:dream:{tenant\_id}:buffer  
  → Paso 2: \_detect\_co\_activations (ventana de 5 fragmentos)  
  → Paso 3: OriMnemosRMH.rerank\_and\_consolidate → \[consolidated, stale\]  
  → Paso 4: vector\_store.update\_hebbian\_weight para consolidated  
  → Paso 5: vector\_store.mark\_stale para stale  
  → Paso 6: delete mpat:dream:{tenant\_id}:buffer  
  → HebbianManager.apply\_decay sobre fragmentos en Memoria Vectorial

OTel spans: dream\_cycle.run, rmh.rerank, rmh.qvalue\_update, cache.semantic.hit/miss  
PolicyEnforcer (Capa 14\) audita parámetros en cada ciclo  
\`\`\`

\---

\#\# 7\. Config files V3\_01

| Config file | Parámetros clave | RES origen |  
|---|---|---|  
| \`config/memory.yaml\` | \`context\_pruning\_threshold\`, \`semantic\_cache\_ttl\`, \`p2p\_min\_confidence\`, \`p2p\_shared\_ttl\_seconds\` | RES.004, RES.081 |  
| \`config/dream\_cycle.yaml\` | \`dream\_cycle\_interval\_s\`, \`dream\_buffer\_ttl\_s\`, \`hebbian\_eta\`, \`hebbian\_decay\`, \`hebbian\_min\`, \`hebbian\_max\`, \`qvalue\_alpha\`, \`qvalue\_gamma\`, \`rerank\_alpha\_semantic\`, \`rerank\_alpha\_qvalue\` | RES.096, RES.119 |

\---

\#\# 8\. Puntos de atención para implementación

\- INV-8-DC.1 \*\*CRÍTICO:\*\* el Dream Cycle NUNCA puede ejecutarse durante sesión activa del tenant. El orquestador debe verificar idle antes de disparar el ciclo.  
\- INV-8-VM.1 \*\*MANDATORIO:\*\* búsquedas vectoriales siempre dentro de la colección del tenant activo. Cualquier implementación alternativa de vector store debe respetar este invariante.  
\- INV-8-SC.1 \*\*SEGURIDAD:\*\* la clave de semantic cache DEBE incluir \`tenant\_id\`. Eliminar \`tenant\_id\` de la clave habilita Key Collision Attack documentado (arxiv.org/pdf/2601.23088).  
\- INV-8-RMH.4 \*\*INVARIANTE DE SUMA:\*\* \`alpha\_semantic \+ alpha\_qvalue \= 1.0\` siempre. Si se ajustan via policy.yaml, la suma debe verificarse.  
\- INV-8-HB.2 \*\*RESTRICCIÓN:\*\* HebbianManager.strengthen solo opera con \`reward \> 0\`. No llamar con reward=0 o negativo — tiene \`return\` explícito.  
\- INV-8-DC.2: el buffer de Dream Cycle se elimina al finalizar el ciclo — no es reutilizable entre ciclos.  
\- Todos los parámetros configurables deben gestionarse exclusivamente via \`policy.yaml\` (P4 de arquitectura). No hardcodear ningún umbral.

\---

\#\# 9\. Datos faltantes o inconsistencias detectadas

\- RES.119 referenciada como dependencia de CAPA\_08 en el snapshot de RELAY\_007 pero no aparece con número formal en el MASTER V3\_01 (el MASTER menciona "Q-Value Reranking" como FUT\_3 sin número RES explícito). Se asume RES.119 según la tabla de dependencias del RELAY\_NEXT\_POINTER. Si RES.119 tiene otro número en RESOLUCIONES\_CONSOLIDADAS, actualizar este informe.  
\- RES.096 idem — mencionada como "Dream Cycle RMH" en la tabla de dependencias. Verificar número exacto en \`RESOLUCIONES\_V3\_01.md\` (ID: \`1rXrQDwsvDU\_GvQtDZGpVegE6U-2G5Yc0\`).  
\- El MASTER no especifica namespace Redis para Semantic Caching (8.4) — solo describe la clave compuesta. Se recomienda formalizar en un RELAY futuro.  
\- \`STALE\_THRESHOLD \= 0.3\` definido en \`dream\_cycle.py\` pero no aparece en la tabla de parámetros configurables del MASTER 8.11. Verificar si debe ser configurable via policy.yaml.

\---

\*INFORME\_CAPA\_08\_V3\_01.md · AGT 2026 · cursos.agt.ia@gmail.com · 2026-05-14\*  
\*Generado en RELAY\_008 (extensión autorizada RELAY\_004) · cursos.agt.ia@gmail.com · 2026-05-14\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
