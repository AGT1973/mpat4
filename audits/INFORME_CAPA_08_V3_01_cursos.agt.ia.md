\# INFORME CAPA 08 — MEMORIA · Dream Cycle · Ori-Mnemos RMH · Aprendizaje Hebbiano  
\*\*Version fuente:\*\* V3\_01  
\*\*Alumno:\*\* cursos.agt.ia@gmail.com  
\*\*Fecha:\*\* 2026-05-14  
\*\*RES que afectan esta capa:\*\* RES.004, RES.081, RES.096, RES.119  
\*\*Paradigma predominante:\*\* Inteligencia Artificial Generativa y Agéntica \+ Co-evolution Human-AI

\> \*\*Nota de ejecución:\*\* Este informe fue generado en sesión RELAY\_008 con autorización  
\> docente explícita, bajo deuda técnica de RELAY\_004. Scope original RELAY\_008 ya completado.

\---

\#\# 1\. Descripción de la capa

La Capa 8 es el sistema de \*\*memoria persistente e inteligente\*\* de MPAT V3\_01.  
Su responsabilidad es garantizar que el conocimiento generado durante la ejecución  
de un agente no se pierda al finalizar esa ejecución — transformando un sistema  
de agentes efímeros en una plataforma que aprende y acumula conocimiento entre sesiones.

En V2\_x, la Capa 8 era un almacén pasivo: guardaba fragmentos vectoriales y los  
recuperaba por similitud semántica. En \*\*V3\_01\*\*, la capa pasa a ser un sistema  
cognitivo activo: no solo retiene — también consolida, prioriza y fortalece  
conexiones entre fragmentos durante los períodos de inactividad del tenant.

Esta transformación se implementa mediante tres mecanismos nuevos en FUT\_3:  
\- \*\*Dream Cycle\*\* (§8.6): consolidación asíncrona de memoria durante idle del tenant  
\- \*\*Ori-Mnemos RMH\*\* (§8.7): reranking de fragmentos por Q-Value histórico de utilidad  
\- \*\*Aprendizaje Hebbiano\*\* (§8.8): fortalecimiento de conexiones entre fragmentos co-activados

La Capa 8 \*\*no es punto de entrada ni salida para A2A (RES.113), SubQ (RES.114)  
ni Unikernel (RES.115)\*\*. Su integración con el sistema de aislamiento multi-tenant  
se expresa a través del invariante de colección vectorial por tenant (INV-8-VM.1)  
y del aislamiento estricto de buffers y pesos hebbianos por \`tenant\_id\`.

\---

\#\# 2\. Componentes de la capa

\#\#\# 2.1 — Memoria Activa (Cache en Memoria)

\- \*\*Qué hace:\*\* Mantiene el contexto inmediato de la ejecución en curso. Es la  
  ventana de trabajo del agente activo: limitada en tokens, privada por ejecución,  
  liberada al estado DESTROY. En V3\_01 agrega una función nueva: antes de DESTROY,  
  su contenido se serializa como \`dream\_buffer\` en Redis para alimentar el Dream Cycle.  
\- \*\*Capa de origen:\*\* Capa 8  
\- \*\*RES que lo definen:\*\* sin RES propia — es infraestructura base  
\- \*\*Dependencias:\*\* Capa 3 (Orquestación — dispara DESTROY), Capa 14 (policy.yaml configura TTLs)  
\- \*\*Namespaces Redis propios:\*\* ninguno directo — el \`dream\_buffer\` es responsabilidad del DreamCycleProcessor  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agéntica  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\`

\#\#\# 2.2 — Memoria Vectorial Persistente

\- \*\*Qué hace:\*\* Base de datos vectorial con aislamiento por tenant. Almacena  
  fragmentos de conocimiento con embeddings. Default: ChromaDB. Alternativa optimizada:  
  FAISS. Clave de aislamiento: \`colección \= f"{tenant\_id}\_{source\_group}"\`. En V3\_01  
  cada fragmento agrega el campo \`hebbian\_weight\` (float, default 1.0) que el  
  Ori-Mnemos RMH actualiza durante el Dream Cycle.  
\- \*\*Capa de origen:\*\* Capa 8  
\- \*\*RES que lo definen:\*\* RES.004 (clave con tenant\_id — corrección de seguridad V2\_02)  
\- \*\*Dependencias:\*\* Capa 4 (Agentes — escriben fragmentos), Capa 6 (ECS — lee fragmentos para contexto)  
\- \*\*Namespaces Redis propios:\*\* no usa Redis directamente — usa ChromaDB/FAISS  
\- \*\*Paradigma:\*\* Co-evolution Human-AI  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\`

\*\*Design-by-Contract:\*\*  
\`\`\`  
Precondición: tenant\_id válido y activo  
Postcondición: búsqueda retorna solo documentos de la colección del tenant activo  
Invariante: INV-8-VM.1 — ninguna búsqueda cruza colecciones de tenants distintos  
\`\`\`

\#\#\# 2.3 — Context Pruning

\- \*\*Qué hace:\*\* Cuando la ventana de contexto del modelo se aproxima al límite,  
  elimina automáticamente los fragmentos de menor relevancia del contexto activo.  
  Los fragmentos eliminados no se pierden — siguen en la Memoria Vectorial.  
  En V3\_01 el criterio de relevancia combina score semántico con \`hebbian\_weight\`:  
  \`score \* hebbian\_weight \> retention\_threshold\`. Un fragmento con alta memoria  
  hebbiana puede sobrevivir al pruning aunque su similitud semántica puntual sea baja.  
\- \*\*Capa de origen:\*\* Capa 8  
\- \*\*RES que lo definen:\*\* sin RES propia — parámetro: \`context\_pruning\_threshold\` (default 0.35)  
\- \*\*Dependencias:\*\* Capa 14 (configura el umbral), Capa 8.7 (provee hebbian\_weight)  
\- \*\*Namespaces Redis propios:\*\* ninguno  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agéntica  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\`

\#\#\# 2.4 — Semantic Caching

\- \*\*Qué hace:\*\* Cachea respuestas del modelo para queries semánticamente similares.  
  La clave incluye \`tenant\_id\` como corrección de seguridad desde V2\_02 (RES.004):  
  \`hash(tenant\_id \+ prompt \+ model\_id)\`. Sin \`tenant\_id\` en la clave, un tenant  
  podría recuperar respuestas cacheadas de otro tenant con queries similares  
  (Key Collision Attack — evidencia: arxiv.org/pdf/2601.23088, HKUST \+ Fudan, 2026).  
  Ahorro estimado: 40–70% de tokens en consultas recurrentes.  
\- \*\*Capa de origen:\*\* Capa 8  
\- \*\*RES que lo definen:\*\* RES.004  
\- \*\*Dependencias:\*\* Capa 1 (API Gateway — consulta cache antes de invocar el modelo)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:sc:{tenant\_id}:{prompt\_hash}:{model\_id}\` TTL=86400s  
\- \*\*Paradigma:\*\* Post-Automation Paradigm (optimización autónoma de costos)  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\` — \`semantic\_cache\_ttl\`

\#\#\# 2.5 — P2P Learning · RES.081

\- \*\*Qué hace:\*\* Permite sincronizar contexto de aprendizaje entre alumnos del mismo  
  tenant con consentimiento explícito (\`consent=True\`). Conceptos con alta confianza  
  individual enriquecen el semantic cache compartido del tenant. La contribución  
  siempre se anonimiza (session\_id hasheado). El aislamiento de tenant es estricto.  
\- \*\*Capa de origen:\*\* Capa 8  
\- \*\*RES que lo definen:\*\* RES.081 (FUT.29)  
\- \*\*Dependencias:\*\* Capa 6 (ECS — provee el \`consent\` del alumno), Capa 14 (configura TTLs y confianza mínima)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:pv:{tenant\_id}:shared:{concept\_hash}\` TTL=2592000s (30 días)  
\- \*\*Paradigma:\*\* Co-evolution Human-AI  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\` — \`p2p\_min\_confidence\`, \`p2p\_shared\_ttl\_seconds\`

\#\#\# 2.6 — Dream Cycle · FUT\_3 \[V3\_01 NUEVO\]

\- \*\*Qué hace:\*\* Proceso asíncrono de consolidación de memoria que se activa durante  
  el idle del tenant (default: 300s sin tareas activas). Reproduce los fragmentos  
  del \`dream\_buffer\` del ciclo anterior, detecta co-activaciones, consolida los  
  fragmentos de mayor valor aumentando su \`hebbian\_weight\`, y poda los de menor  
  valor marcándolos \`stale\`. Implementa \`DreamCycleProcessor\` en \`capa\_8/dream\_cycle.py\`.  
\- \*\*Capa de origen:\*\* Capa 8  
\- \*\*RES que lo definen:\*\* RES.096  
\- \*\*Dependencias:\*\* Capa 3 (Orquestador — señal de idle), Capa 8.2 (Memoria Vectorial — destino de actualizaciones), Capa 8.7 (Ori-Mnemos RMH — reranking durante el ciclo)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:dream:{tenant\_id}:buffer\` TTL=3600s (List de JSON)  
\- \*\*Paradigma:\*\* Co-evolution Human-AI  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\` — \`dream\_cycle\_interval\_s\`, \`dream\_buffer\_ttl\_s\`

\#\#\# 2.7 — Ori-Mnemos RMH · FUT\_3 \[V3\_01 NUEVO\]

\- \*\*Qué hace:\*\* Subsistema de reranking de memoria que combina similitud semántica  
  con Q-Value histórico de utilidad del fragmento. Implementa Q-learning sobre  
  la Memoria Vectorial: cada vez que un fragmento contribuye a resolver una tarea  
  exitosamente, su Q-Value aumenta. El reranking final pondera:  
  \`score \= 0.6 \* cos\_sim \+ 0.4 \* q\_normalized\`. Implementa \`OriMnemosRMH\`  
  en \`capa\_8/ori\_mnemos\_rmh.py\`. Q-Values clampeados en \[-1.0, 2.0\].  
\- \*\*Capa de origen:\*\* Capa 8  
\- \*\*RES que lo definen:\*\* RES.119  
\- \*\*Dependencias:\*\* Capa 8.6 (Dream Cycle — lo invoca durante la consolidación), Capa 4 (Agentes — reportan reward tras cada tarea)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:rmh:{tenant\_id}:qval:{fragment\_id}\` TTL=7776000s (90 días)  
\- \*\*Paradigma:\*\* Post-Automation Paradigm  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\` — \`qvalue\_alpha\`, \`qvalue\_gamma\`, \`rerank\_alpha\_semantic\`, \`rerank\_alpha\_qvalue\`

\#\#\# 2.8 — HebbianManager · FUT\_3 \[V3\_01 NUEVO\]

\- \*\*Qué hace:\*\* Gestiona los pesos de conexión entre fragmentos de memoria.  
  Implementa la regla de Hebb: fragmentos que aparecen juntos en la ventana de  
  contexto durante tareas exitosas fortalecen su conexión. Peso clampeado en \[0.1, 3.0\].  
  Baseline \= 1.0. Incluye decaimiento pasivo hacia baseline para evitar saturación.  
  El decay es responsabilidad del DreamCycleProcessor, no del pipeline activo.  
  Implementa \`HebbianManager\` en \`capa\_8/hebbian\_manager.py\`.  
\- \*\*Capa de origen:\*\* Capa 8  
\- \*\*RES que lo definen:\*\* RES.119 (mismo FUT que Ori-Mnemos — componentes acoplados)  
\- \*\*Dependencias:\*\* Capa 8.6 (Dream Cycle — dispara decay y bulk\_strengthen), Capa 4 (Agentes — reportan reward)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:hebbian:{tenant\_id}:{fragment\_id}\` TTL=7776000s (90 días)  
\- \*\*Paradigma:\*\* Co-evolution Human-AI  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\` — \`hebbian\_eta\`, \`hebbian\_decay\`, \`hebbian\_min\`, \`hebbian\_max\`

\---

\#\# 3\. Resoluciones que afectan esta capa

\#\#\# RES.004 — Semantic Cache Key con tenant\_id  
\*\*FUT asociado:\*\* — \*\*Fecha:\*\* V2\_02 \*\*Version:\*\* V3\_01 (preservada)

\#\#\#\# 3.1 Problema que resolvía  
Sin \`tenant\_id\` en la clave del semantic cache, un tenant podía recuperar respuestas  
cacheadas de otro tenant con queries semánticamente similares. Este es el Key Collision  
Attack documentado en arxiv.org/pdf/2601.23088 (HKUST \+ Fudan, 2026).

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*Opción A:\*\* Clave \`hash(prompt \+ model\_id)\` — descartada: permite colisión entre tenants  
\- \*\*Opción B:\*\* Clave \`hash(tenant\_id \+ prompt \+ model\_id)\` — elegida: aislamiento garantizado  
\- \*\*Opción C:\*\* Cache por tenant en namespaces Redis separados — posible pero más costoso en infraestructura

\#\#\#\# 3.3 Decisión elegida y justificación  
Opción B. La inclusión de \`tenant\_id\` en la clave garantiza que dos tenants con  
queries semánticamente idénticas nunca compartan caché. El costo computacional  
es mínimo (un hash adicional). La corrección es normativa: \*\*esta clave no puede  
modificarse sin actualizar RESOLUCIONES\*\*.

\#\#\#\# 3.4 Parámetros resultantes  
| Parámetro | Valor default | Rango | Descripción |  
|---|---|---|---|  
| \`semantic\_cache\_ttl\` | 86400 | 300–604800 | TTL en segundos del cache semántico |  
| Clave | \`hash(tenant\_id \+ prompt \+ model\_id)\` | — | Fija — no modificar |

\#\#\#\# 3.5 Namespaces Redis  
\- \`mpat:sc:{tenant\_id}:{hash}\` TTL=86400s \[String\] \[RES.004\]

\#\#\#\# 3.6 Integraciones con otras capas  
Capa 1 (API Gateway) consulta el cache antes de invocar el modelo LLM.  
Capa 14 configura el TTL vía \`policy.yaml\`.

\#\#\#\# 3.7 OTel spans definidos  
\- Span \`memory.semantic\_cache.hit\`: atributos: \`tenant\_id\`, \`prompt\_hash\`, \`model\_id\`, \`saved\_tokens\`  
\- Span \`memory.semantic\_cache.miss\`: atributos: \`tenant\_id\`, \`prompt\_hash\`

\#\#\#\# 3.8 Trampa educativa  
La trampa es asumir que el semantic cache guarda solo respuestas a prompts idénticos.  
La respuesta simple sería "es como un diccionario prompt → respuesta".  
La respuesta correcta: el cache actúa por similitud semántica, no por igualdad exacta  
de texto. Dos prompts con palabras distintas pero misma intención pueden compartir  
caché dentro del mismo tenant. Esto es lo que genera el 40–70% de ahorro real.

\---

\#\#\# RES.081 — P2P Learning con consentimiento  
\*\*FUT asociado:\*\* FUT.29 \*\*Fecha:\*\* V2\_75 \*\*Version:\*\* V3\_01 (preservada)

\#\#\#\# 3.1 Problema que resolvía  
La memoria de cada alumno era completamente aislada. Conceptos bien consolidados  
por un alumno no podían beneficiar a otros alumnos del mismo tenant, desperdiciando  
conocimiento colectivo ya validado.

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*Opción A:\*\* Memoria completamente compartida entre alumnos — descartada: viola privacidad  
\- \*\*Opción B:\*\* Sincronización con consentimiento explícito y anonimización — elegida  
\- \*\*Opción C:\*\* Memoria compartida sin consentimiento — descartada: inaceptable éticamente

\#\#\#\# 3.3 Decisión elegida y justificación  
Opción B. El consentimiento (\`consent=True\` en ECS del alumno) es condición  
obligatoria. La contribución se anonimiza (session\_id hasheado). El pool compartido  
solo existe dentro del mismo \`tenant\_id\` — nunca cruza tenants.

\#\#\#\# 3.4 Parámetros resultantes  
| Parámetro | Valor default | Rango | Descripción |  
|---|---|---|---|  
| \`p2p\_min\_confidence\` | 0.75 | 0.5–1.0 | Confianza mínima para contribuir |  
| \`p2p\_shared\_ttl\_seconds\` | 2592000 | 86400–7776000 | TTL del pool compartido (30 días) |

\#\#\#\# 3.5 Namespaces Redis  
\- \`mpat:pv:{tenant\_id}:shared:{concept\_hash}\` TTL=2592000s \[String/JSON\] \[RES.081\]

\#\#\#\# 3.6 Integraciones con otras capas  
Capa 6 (ECS) provee el flag \`consent\` del alumno. Capa 14 configura umbrales.

\#\#\#\# 3.7 OTel spans definidos  
\- Span \`memory.p2p.contribute\`: atributos: \`tenant\_id\`, \`concept\_hash\`, \`confidence\`, \`anon\_session\_id\`

\#\#\#\# 3.8 Trampa educativa  
La trampa es asumir que P2P Learning implica que todos los alumnos comparten  
toda su memoria. La respuesta simple: "es memoria compartida". La respuesta  
correcta: solo se comparten conceptos con confianza ≥ 0.75, con consentimiento  
activo, de forma anónima, y dentro del mismo tenant. El aislamiento entre tenants  
es absoluto incluso con P2P activo.

\---

\#\#\# RES.096 — Dream Cycle: consolidación asíncrona de memoria  
\*\*FUT asociado:\*\* FUT\_3 (Capa 8\) \*\*Fecha:\*\* 2026-05-12 \*\*Version:\*\* V3\_01

\#\#\#\# 3.1 Problema que resolvía  
La memoria activa de cada ejecución se perdía completamente al hacer DESTROY  
del agente. Los fragmentos de conocimiento generados en cada sesión no  
contribuían a mejorar la calidad de futuras ejecuciones del mismo tenant.  
La Memoria Vectorial era un almacén pasivo: no había mecanismo para consolidar  
ni priorizar lo más valioso.

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*Opción A:\*\* Guardar toda la memoria activa en la vectorial al final de cada sesión — descartada: ruido, no discrimina calidad  
\- \*\*Opción B:\*\* Dream Cycle asíncrono durante idle: replay \+ consolidación selectiva — elegida  
\- \*\*Opción C:\*\* Fine-tuning continuo del modelo en base a las sesiones — descartada: complejidad y costo prohibitivos para V3\_01

\#\#\#\# 3.3 Decisión elegida y justificación  
Opción B. El Dream Cycle opera en idle (no bloquea ejecuciones activas — INV-8-DC.1),  
procesa el \`dream\_buffer\` acumulado del ciclo anterior, detecta co-activaciones en  
ventana de 5 fragmentos, consolida los valiosos (aumenta \`hebbian\_weight\`) y  
marca los irrelevantes como \`stale\`. La analogía biológica es el sueño REM:  
el sistema fortalece lo que importa y descarta el ruido mientras no está en uso activo.

\#\#\#\# 3.4 Parámetros resultantes  
| Parámetro | Valor default | Rango | Descripción |  
|---|---|---|---|  
| \`dream\_cycle\_interval\_s\` | 300 | 60–3600 | Segundos de idle antes de activar Dream Cycle |  
| \`dream\_buffer\_ttl\_s\` | 3600 | 600–86400 | TTL máximo del buffer antes del ciclo |  
| \`HEBBIAN\_INCREMENT\` | 0.15 | — | Incremento de peso por co-activación confirmada |  
| \`STALE\_THRESHOLD\` | 0.3 | — | Peso debajo del cual el fragmento se marca stale |

\#\#\#\# 3.5 Namespaces Redis  
\- \`mpat:dream:{tenant\_id}:buffer\` TTL=3600s \[List/JSON de DreamFragment\] \[RES.096\]

\#\#\#\# 3.6 Integraciones con otras capas  
El Orquestador (Capa 3\) detecta el idle del tenant y dispara el Dream Cycle.  
El DreamCycleProcessor actualiza \`hebbian\_weight\` en la Memoria Vectorial (Capa 8.2).  
El Ori-Mnemos RMH (Capa 8.7) es invocado internamente durante la consolidación.  
PolicyEnforcer (Capa 14\) valida que el Dream Cycle respete los límites de tenant.

\#\#\#\# 3.7 OTel spans definidos  
\- Span \`memory.dream\_cycle.run\`: atributos: \`tenant\_id\`, \`processed\`, \`consolidated\`, \`stale\`, \`duration\_ms\`  
\- Span \`memory.dream\_cycle.buffer\_load\`: atributos: \`tenant\_id\`, \`fragment\_count\`

\#\#\#\# 3.8 Trampa educativa  
La trampa es asumir que el Dream Cycle se ejecuta en tiempo real junto con  
las tareas del agente. La respuesta simple: "el Dream Cycle procesa la memoria  
constantemente". La respuesta correcta: el Dream Cycle ÚNICAMENTE opera durante  
el idle del tenant (INV-8-DC.1). Si hay una tarea activa, el Dream Cycle no  
puede ejecutarse. Esta separación es un invariante de diseño — no una opción  
de configuración.

\---

\#\#\# RES.119 — Ori-Mnemos RMH \+ Aprendizaje Hebbiano  
\*\*FUT asociado:\*\* FUT\_3 (Capa 8\) \*\*Fecha:\*\* 2026-05-12 \*\*Version:\*\* V3\_01

\#\#\#\# 3.1 Problema que resolvía  
La recuperación de fragmentos de memoria usaba únicamente similitud semántica puntual.  
Dos problemas: (1) fragmentos muy usados y valiosos en el pasado no tenían ventaja  
sobre fragmentos nuevos e igualmente similares; (2) no había mecanismo para que  
el sistema aprendiera qué fragmentos son más útiles para cada tipo de tarea.

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*Opción A:\*\* Solo similitud semántica (estado anterior V2\_x) — descartada: no aprende  
\- \*\*Opción B:\*\* Q-learning sobre fragmentos (Ori-Mnemos) \+ pesos hebbianos (HebbianManager) — elegida  
\- \*\*Opción C:\*\* Fine-tuning de embeddings — descartada: costo prohibitivo en tiempo real

\#\#\#\# 3.3 Decisión elegida y justificación  
Opción B. Ori-Mnemos combina similitud semántica (peso 0.6) con Q-Value normalizado  
(peso 0.4): \`score \= 0.6 \* cos\_sim \+ 0.4 \* q\_normalized\`. El HebbianManager  
fortalece los pesos de fragmentos co-activados en tareas exitosas. Ambos  
componentes son por \`tenant\_id\` — nunca se comparten entre tenants (INV-8-RMH.3,  
INV-8-HB.4). Los Q-Values se clampean en \[-1.0, 2.0\] para evitar divergencia  
(INV-8-RMH.1). Los pesos hebbianos se clampean en \[0.1, 3.0\] con decaimiento  
pasivo hacia baseline=1.0 (INV-8-HB.1, INV-8-HB.3).

\#\#\#\# 3.4 Parámetros resultantes  
| Parámetro | Valor default | Rango | Descripción |  
|---|---|---|---|  
| \`qvalue\_alpha\` | 0.10 | 0.01–0.5 | Tasa de aprendizaje Q |  
| \`qvalue\_gamma\` | 0.90 | 0.5–0.99 | Factor de descuento Q |  
| \`rerank\_alpha\_semantic\` | 0.60 | 0.3–0.9 | Peso semántico en reranking |  
| \`rerank\_alpha\_qvalue\` | 0.40 | 0.1–0.7 | Peso Q-Value en reranking |  
| \`hebbian\_eta\` | 0.10 | 0.01–0.5 | Tasa hebbiana de fortalecimiento |  
| \`hebbian\_decay\` | 0.005 | 0.001–0.05 | Decaimiento hacia baseline |  
| \`hebbian\_min\` | 0.10 | 0.01–0.5 | Peso mínimo |  
| \`hebbian\_max\` | 3.0 | 1.5–5.0 | Peso máximo |

\*\*Invariante de ponderación:\*\* \`rerank\_alpha\_semantic \+ rerank\_alpha\_qvalue \= 1.0\` (INV-8-RMH.4)

\#\#\#\# 3.5 Namespaces Redis  
\- \`mpat:rmh:{tenant\_id}:qval:{fragment\_id}\` TTL=7776000s (90 días) \[String/float\] \[RES.119\]  
\- \`mpat:hebbian:{tenant\_id}:{fragment\_id}\` TTL=7776000s (90 días) \[String/float\] \[RES.119\]

\#\#\#\# 3.6 Integraciones con otras capas  
Capa 4 (Agentes) reporta el \`reward\` al finalizar cada tarea. Capa 8.6 (Dream  
Cycle) invoca \`rerank\_and\_consolidate\` durante el ciclo. Capa 14 configura todos  
los parámetros vía \`policy.yaml\` (Regla P4 — nada hardcodeado).

\#\#\#\# 3.7 OTel spans definidos  
\- Span \`memory.rmh.rerank\`: atributos: \`tenant\_id\`, \`fragment\_count\`, \`top\_fragment\_id\`, \`top\_score\`  
\- Span \`memory.hebbian.strengthen\`: atributos: \`tenant\_id\`, \`fragment\_id\_a\`, \`fragment\_id\_b\`, \`reward\`, \`new\_weight\`  
\- Span \`memory.hebbian.decay\`: atributos: \`tenant\_id\`, \`fragment\_id\`, \`old\_weight\`, \`new\_weight\`

\#\#\#\# 3.8 Trampa educativa  
La trampa doble de esta RES:

\*\*Trampa 1 (Ori-Mnemos):\*\* Asumir que el reranking por Q-Value reemplaza la  
similitud semántica. La respuesta simple: "ahora se usa Q-learning en lugar de  
similitud". La respuesta correcta: la similitud semántica sigue siendo el componente  
dominante (peso 0.6). El Q-Value es complementario (peso 0.4). La suma siempre  
es 1.0 (INV-8-RMH.4). Nunca es "en lugar de".

\*\*Trampa 2 (Hebbiano):\*\* Asumir que el \`hebbian\_weight\` crece indefinidamente  
con el uso. La respuesta simple: "más se usa, más peso tiene". La respuesta  
correcta: el peso está clampeado en \[0.1, 3.0\] (INV-8-HB.1) y sufre decaimiento  
pasivo hacia baseline=1.0 durante el Dream Cycle (INV-8-HB.3). Un fragmento  
no usado durante suficiente tiempo vuelve a peso 1.0, independientemente de cuán  
valioso haya sido en el pasado.

\---

\#\# 4\. Integración V3\_01 — Cadena crítica A2A \+ SubQ \+ Unikernel

\[NO APLICA\] — La Capa 8 no es punto de entrada ni salida para A2A (RES.113),  
SubQ (RES.114) ni Unikernel (RES.115). Su aislamiento multi-tenant se implementa  
a nivel de colección vectorial (INV-8-VM.1) y namespace Redis por \`tenant\_id\`.

\---

\#\# 5\. Estado final de la capa en V3\_01

La Capa 8 en V3\_01 es un sistema de memoria \*\*activamente cognitivo\*\*, compuesto  
por 8 componentes (2.1 a 2.8). Los tres componentes nuevos de FUT\_3 —  
Dream Cycle, Ori-Mnemos RMH y HebbianManager — transforman la capa de almacén  
pasivo a sistema que consolida, prioriza y fortalece conocimiento entre sesiones.

\*\*Cambios respecto a V2\_102:\*\*

| Componente | Estado V2\_102 | Estado V3\_01 |  
|---|---|---|  
| Memoria Activa | Solo contexto de ejecución | \+ Alimenta dream\_buffer antes de DESTROY |  
| Memoria Vectorial | Fragmentos con embedding | \+ Campo \`hebbian\_weight\` por fragmento |  
| Context Pruning | Solo score semántico | \+ Considera \`hebbian\_weight\` combinado |  
| Semantic Caching | Sin cambios (RES.004 desde V2\_02) | Sin cambios |  
| P2P Learning | Sin cambios (RES.081 desde V2\_75) | Sin cambios |  
| Dream Cycle | No existía | \*\*NUEVO\*\* — DreamCycleProcessor |  
| Ori-Mnemos RMH | No existía | \*\*NUEVO\*\* — Q-Value Reranking |  
| HebbianManager | No existía | \*\*NUEVO\*\* — Aprendizaje Hebbiano |

Invariantes vigentes: 11 (4 heredados de V2\_x \+ 7 nuevos V3\_01)  
Tests de integración: 9 (preservados V2) \+ 9 (nuevos V3\_01) \= 18 tests activos

\---

\#\# 6\. Flujo de datos completo

\`\`\`  
\[Tarea activa del tenant\]  
  AgentRuntime (Capa 4\) → escribe fragmentos → MemoriaVectorial (ChromaDB/FAISS)  
  MemoriaActiva → acumula contexto durante ejecución  
  SemanticCache (Capa 1\) → consulta antes de invocar LLM → ahorro 40-70% tokens  
  OTel span: memory.semantic\_cache.hit / miss

\[Final de ejecución — estado DESTROY\]  
  MemoriaActiva → serializa contenido → mpat:dream:{tenant\_id}:buffer  
  OTel span: memory.dream\_cycle.buffer\_load

\[Idle del tenant — 300s sin tareas\]  
  Orquestador (Capa 3\) → detecta idle → dispara DreamCycleProcessor  
  DreamCycleProcessor.run\_cycle():  
    → carga dream\_buffer desde Redis  
    → \_detect\_co\_activations(fragments) → ventana de 5 fragmentos  
    → OriMnemosRMH.rerank\_and\_consolidate(fragments)  
      → Q-Value por fragmento desde mpat:rmh:{tenant\_id}:qval:{id}  
      → combined \= (q+1.0)/3.0 \* hebbian\_weight  
      → si combined \>= 0.3 → consolidated (hebbian\_weight \+= 0.05)  
      → si combined \< 0.3 → stale  
    → VectorStore.update\_hebbian\_weight(tenant\_id, fragment\_id, new\_weight)  
    → VectorStore.mark\_stale(tenant\_id, fragment\_id)  
    → r.delete(dream\_buffer) — INV-8-DC.2  
  OTel span: memory.dream\_cycle.run

\[Tarea activa — recuperación de fragmentos\]  
  OriMnemosRMH.rerank(fragments, query\_embedding):  
    → cos\_sim por fragmento  
    → q\_val desde Redis → q\_normalized \= (q+1.0)/3.0  
    → score \= 0.6 \* cos\_sim \+ 0.4 \* q\_normalized  
    → sorted descending  
  OTel span: memory.rmh.rerank

\[Tarea completada con éxito — reward \= 1.0\]  
  AgentRuntime (Capa 4\) → reporta reward  
  OriMnemosRMH.update\_q\_value(fragment\_id, reward=1.0)  
  HebbianManager.bulk\_strengthen(co\_activations, reward=1.0)  
  OTel span: memory.hebbian.strengthen

PolicyEnforcer (Capa 14\) → auditoría en cada operación con tenant\_id  
\`\`\`

\---

\#\# 7\. Config files V3\_01

| Config file | Parámetros clave | RES origen |  
|---|---|---|  
| \`config/memory.yaml\` | \`context\_pruning\_threshold\`, \`semantic\_cache\_ttl\` | RES.004 |  
| \`config/memory.yaml\` | \`p2p\_min\_confidence\`, \`p2p\_shared\_ttl\_seconds\` | RES.081 |  
| \`config/memory.yaml\` | \`dream\_cycle\_interval\_s\`, \`dream\_buffer\_ttl\_s\`, \`HEBBIAN\_INCREMENT\`, \`STALE\_THRESHOLD\` | RES.096 |  
| \`config/memory.yaml\` | \`qvalue\_alpha\`, \`qvalue\_gamma\`, \`rerank\_alpha\_semantic\`, \`rerank\_alpha\_qvalue\`, \`hebbian\_eta\`, \`hebbian\_decay\`, \`hebbian\_min\`, \`hebbian\_max\` | RES.119 |

\> \*\*Regla P4 (Arquitectura base V3\_01):\*\* TODOS los parámetros son configurables  
\> vía \`policy.yaml\` (Capa 14). Ninguno está hardcodeado.

\---

\#\# 8\. Puntos de atención para implementación

\*\*Críticos — no negociables:\*\*

1\. \*\*INV-8-DC.1:\*\* El Dream Cycle NUNCA puede ejecutarse mientras hay una tarea activa en el tenant. La señal de idle debe ser confiable y proveniente del Orquestador (Capa 3).

2\. \*\*INV-8-VM.1:\*\* La colección vectorial siempre usa \`f"{tenant\_id}\_{source\_group}"\` como clave de aislamiento. Una búsqueda que cruce colecciones de tenants distintos es una violación de seguridad, no un bug menor.

3\. \*\*INV-8-RMH.4:\*\* \`rerank\_alpha\_semantic \+ rerank\_alpha\_qvalue\` DEBE ser exactamente 1.0. Si se ajustan ambos parámetros por separado en \`policy.yaml\`, el sistema debe validar esta suma antes de aplicar.

4\. \*\*INV-8-HB.1 \+ INV-8-RMH.1:\*\* Los clamps de Q-Value \[-1.0, 2.0\] y hebbian\_weight \[0.1, 3.0\] son obligatorios. Sin ellos, los valores pueden diverger hasta hacer inútil el reranking.

5\. \*\*INV-8-DC.2:\*\* El \`dream\_buffer\` se elimina al finalizar cada ciclo. No es reutilizable. Cada ciclo trabaja solo con los fragmentos del período de ejecución anterior.

\*\*Mandatorios para seguridad:\*\*

6\. \*\*RES.004:\*\* La clave del semantic cache incluye \`tenant\_id\`. Este diseño no puede modificarse sin actualizar formalmente las RESOLUCIONES y notificar al docente.

7\. \*\*INV-8-P2P.1 \+ INV-8-P2P.2:\*\* P2P Learning requiere \`consent=True\` en ECS. La contribución siempre se anonimiza. Nunca exponer \`session\_id\` real en el pool compartido.

\---

\#\# 9\. Datos faltantes o inconsistencias detectadas

1\. \*\*RES.096 y RES.119 no están en el MAPA\_RES\_CANONICO\_V3\_01.md\*\* — estas RES fueron asignadas a FUT\_3 de Capa 8 durante RELAY\_001 pero no están formalmente registradas en el mapa canónico. Se recomienda agregarlas en una sesión futura de RELAY\_002 o en un patch de resoluciones.

2\. \*\*IDs de CAPA\_08\_MASTER\_V3\_01.md\*\* no estaban en el snapshot de RELAY\_007 — registrado aquí: ID \`1qAN2il5qEU5NvZAHksWBzniKI233jGJj\`.

3\. \*\*Tests de integración\*\* están nombrados pero no implementados en el MASTER (stubs). La implementación real queda pendiente para sesión de desarrollo.

4\. \*\*Archivo \`capa\_8/dream\_cycle.py\`\*\* referenciado en el MASTER — sin confirmación de que exista en el repositorio del proyecto. Pendiente verificación.

\---

\*INFORME\_CAPA\_08\_V3\_01\_cursos.agt.ia.md · AGT 2026-05-14\*  
\*cursos.agt.ia@gmail.com · 2026-05-14\*  
\*Generado con autorización docente en RELAY\_008 (deuda RELAY\_004)\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
