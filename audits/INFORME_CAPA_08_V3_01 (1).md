\# INFORME CAPA 08 — MEMORIA  
\*\*Version fuente:\*\* V3\_01  
\*\*Alumno:\*\* cursos.agt@gmail.com  
\*\*Fecha:\*\* 2026-05-14  
\*\*RES que afectan esta capa:\*\* RES.004, RES.081, RES.119, RES.120  
\*\*Paradigma predominante:\*\* Inteligencia Artificial Generativa y Agentica

\---

\#\# 1\. Descripcion de la capa

La Capa 8 gestiona la persistencia, consolidación y priorización del conocimiento generado por los agentes en MPAT. Su responsabilidad central es hacer que el sistema no sea solo un almacén pasivo de información, sino un sistema cognitivo activo que aprende entre ejecuciones.

Los agentes de MPAT son efímeros (Capa 4): nacen, ejecutan y se destruyen. Sin embargo, el conocimiento acumulado durante una sesión no debería perderse. La Capa 8 garantiza que los hechos, patrones y relaciones semánticas identificados por un agente estén disponibles para el próximo agente que trabaje en el mismo tenant.

En V3\_01, la capa evoluciona de almacén reactivo a sistema cognitivo activo. Las tres adiciones de FUT\_3 (Dream Cycle, Ori-Mnemos RMH, Aprendizaje Hebbiano) transforman la memoria desde un repositorio estático hacia un sistema que consolida, prioriza y fortalece conexiones entre fragmentos de conocimiento de forma autónoma durante los períodos de inactividad.

Esta capa NO es punto de entrada ni salida para A2A (RES.113), SubQ (RES.114) o Unikernel (RES.115). Su integración con esos protocolos es indirecta: el aislamiento de tenants garantiza que ningún fragmento de memoria cruce colecciones de distintos tenants, y los pesos hebbianos son específicos por tenant\_id.

\---

\#\# 2\. Componentes de la capa

\#\#\# 2.1 — Memoria Activa (Cache en Memoria)  
\- \*\*Que hace:\*\* Mantiene el contexto inmediato de la ejecución en curso dentro de la ventana de tokens del modelo. Se libera en estado DESTROY.  
\- \*\*Capa de origen:\*\* Capa 8  
\- \*\*RES que lo definen:\*\* No tiene RES formal — es el mecanismo base heredado de V2.  
\- \*\*Dependencias:\*\* Capa 3 (Orchestrator inyecta contexto), Capa 6 (ECS provee estado)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:dream:{tenant\_id}:buffer\` (TTL: 3600s) — buffer que se alimenta al final de la sesión para el Dream Cycle  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agentica  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\`

\#\#\# 2.2 — Memoria Vectorial Persistente (ChromaDB \+ FAISS)  
\- \*\*Que hace:\*\* Persiste fragmentos de conocimiento como vectores semánticos, aislados por tenant. Permite recuperación por similitud semántica. Cada fragmento tiene un campo \`hebbian\_weight\` (float, default 1.0) que el Ori-Mnemos RMH actualiza.  
\- \*\*Capa de origen:\*\* Capa 8  
\- \*\*RES que lo definen:\*\* RES.004 (aislamiento por tenant\_id en clave), INV-8-VM.1  
\- \*\*Dependencias:\*\* Capa 8.7 (Ori-Mnemos actualiza weights), Capa 9 (NHP garantiza que el tenant\_id es auténtico)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:rmh:{tenant\_id}:qval:{fragment\_id}\` (TTL: 7776000s / 90 días)  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agentica  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\`

\#\#\# 2.3 — Context Pruning  
\- \*\*Que hace:\*\* Cuando la ventana de contexto está cerca del límite, elimina fragmentos de baja relevancia del contexto activo. En V3\_01, la decisión considera \`hebbian\_weight\` además del score semántico: un fragmento con alto peso hebbiano puede ser retenido aunque su score semántico puntual sea bajo.  
\- \*\*Capa de origen:\*\* Capa 8  
\- \*\*RES que lo definen:\*\* Criterio base heredado V2; criterio hebbiano introducido por FUT\_3 (RES.119/120)  
\- \*\*Dependencias:\*\* Capa 8.8 (HebbianManager provee weights)  
\- \*\*Namespaces Redis propios:\*\* Ninguno propio — lee \`mpat:hebbian:{tenant\_id}:{fragment\_id}\`  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agentica  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\` — parámetro \`context\_pruning\_threshold\` (default: 0.35)

\#\#\# 2.4 — Semantic Caching (RES.004)  
\- \*\*Que hace:\*\* Cachea respuestas del modelo para queries semánticamente similares. La clave incluye obligatoriamente \`tenant\_id\` para prevenir Key Collision Attacks (un tenant no puede recuperar respuestas de otro tenant con queries similares).  
\- \*\*Capa de origen:\*\* Capa 8 (V2\_02)  
\- \*\*RES que lo definen:\*\* RES.004  
\- \*\*Dependencias:\*\* Capa 5 (provee hash del prompt y model\_id), Capa 14 (TTL configurable)  
\- \*\*Namespaces Redis propios:\*\* clave: \`hash(tenant\_id \+ prompt \+ model\_id)\` → respuesta \+ pasos de razonamiento; TTL configurable por dominio  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agentica  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\` — \`semantic\_cache\_ttl\`

\#\#\# 2.5 — P2P Learning (RES.081 / FUT.29)  
\- \*\*Que hace:\*\* Sincroniza conceptos bien consolidados entre alumnos del mismo tenant, enriqueciendo el semantic cache compartido con consentimiento explícito. Nunca cruza tenant\_id.  
\- \*\*Capa de origen:\*\* Capa 8 (V2\_75)  
\- \*\*RES que lo definen:\*\* RES.081  
\- \*\*Dependencias:\*\* ECS (requiere consent=True), Capa 14 (min\_confidence configurable)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:pv:{tenant\_id}:shared:{concept\_hash}\` TTL=2592000s (30 días)  
\- \*\*Paradigma:\*\* Co-evolution Human-AI  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\` — \`p2p\_min\_confidence\`, \`p2p\_shared\_ttl\_seconds\`

\#\#\# 2.6 — Dream Cycle (FUT\_3 · V3\_01 NUEVO)  
\- \*\*Que hace:\*\* Proceso asíncrono de consolidación de memoria que se activa en período idle del tenant (análogo al sueño REM biológico). Recolecta el dream\_buffer de la Memoria Activa, re-procesa fragmentos por co-activación, consolida los de alta frecuencia elevando su \`hebbian\_weight\`, y marca como stale los de baja relevancia.  
\- \*\*Capa de origen:\*\* Capa 8 (V3\_01)  
\- \*\*RES que lo definen:\*\* RES.119 (Dream Cycle \+ Hebbiano)  
\- \*\*Dependencias:\*\* Capa 8.7 (Ori-Mnemos), Capa 8.8 (HebbianManager), Capa 8.2 (Memoria Vectorial)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:dream:{tenant\_id}:buffer\` → List\[JSON(DreamFragment)\] TTL=3600s  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agentica  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\` — \`dream\_cycle\_interval\_s\` (300), \`dream\_buffer\_ttl\_s\` (3600)

\#\#\# 2.7 — Ori-Mnemos RMH (FUT\_3 · V3\_01 NUEVO)  
\- \*\*Que hace:\*\* Subsistema de reranking de memoria que implementa Q-Value Reranking. Pondera la recuperación de fragmentos combinando similitud semántica (alpha=0.6) y valor instrumental histórico del fragmento en la resolución de tareas exitosas (alpha=0.4). El Q-Value se actualiza con la ecuación de Bellman adaptada.  
\- \*\*Capa de origen:\*\* Capa 8 (V3\_01)  
\- \*\*RES que lo definen:\*\* RES.119 (Dream Cycle \+ Hebbiano)  
\- \*\*Dependencias:\*\* Capa 8.6 (DreamCycle llama a rerank\_and\_consolidate), Redis (Q-Values por fragment\_id)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:rmh:{tenant\_id}:qval:{fragment\_id}\` TTL=7776000s (90 días)  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agentica  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\` — \`qvalue\_alpha\` (0.10), \`qvalue\_gamma\` (0.90), \`rerank\_alpha\_semantic\` (0.60), \`rerank\_alpha\_qvalue\` (0.40)

\#\#\# 2.8 — HebbianManager (FUT\_3 · V3\_01 NUEVO)  
\- \*\*Que hace:\*\* Implementa la regla de aprendizaje hebbiano ("neuronas que se activan juntas, se conectan"): los fragmentos que co-aparecen en ventana de contexto durante tareas exitosas fortalecen su peso mutuo. El peso decae hacia baseline (1.0) con el tiempo. Operar solo con reward \> 0\.  
\- \*\*Capa de origen:\*\* Capa 8 (V3\_01)  
\- \*\*RES que lo definen:\*\* RES.119 (Dream Cycle \+ Hebbiano)  
\- \*\*Dependencias:\*\* Capa 8.6 (DreamCycleProcessor llama a bulk\_strengthen), Capa 8.3 (Context Pruning lee weights)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:hebbian:{tenant\_id}:{fragment\_id}\` TTL=7776000s (90 días)  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agentica  
\- \*\*Config file V3\_01:\*\* \`config/memory.yaml\` — \`hebbian\_eta\` (0.10), \`hebbian\_decay\` (0.005), \`hebbian\_min\` (0.10), \`hebbian\_max\` (3.0)

\---

\#\# 3\. Resoluciones que afectan esta capa

\#\#\# RES.004 — Semantic Cache con tenant\_id obligatorio  
\*\*FUT asociado:\*\* FUT.02 \*\*Fecha:\*\* 2026-05-02 \*\*Version:\*\* V2\_02

\#\#\#\# 3.1 Problema que resolvia  
Sin tenant\_id en la clave del semantic cache, un tenant podía recuperar respuestas cacheadas de otro tenant con queries semánticamente similares (Key Collision Attack). Evidencia formal: arxiv.org/pdf/2601.23088 (HKUST \+ Fudan, 2026).

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*Opcion A:\*\* Clave solo por hash del prompt — descartada por la vulnerabilidad de Key Collision Attack documentada.  
\- \*\*Opcion B:\*\* Clave \`hash(tenant\_id \+ prompt \+ model\_id)\` — elegida por garantizar aislamiento completo.  
\- \*\*Opcion C:\*\* Cache sin persistencia (solo in-memory) — descartada por pérdida de ahorro entre sesiones.

\#\#\#\# 3.3 Decision elegida y justificacion  
Clave compuesta \`hash(tenant\_id \+ prompt \+ model\_id)\`. El tenant\_id hace la clave específica al tenant, eliminando la posibilidad de que dos tenants distintos colisionen aunque sus prompts sean semánticamente equivalentes.

\#\#\#\# 3.4 Parametros resultantes  
| Parametro | Valor default | Rango | Descripcion |  
|---|---|---|---|  
| \`semantic\_cache\_ttl\` | 86400 | 300–604800 | TTL del cache en segundos |  
| clave | \`hash(tenant\_id+prompt+model\_id)\` | fijo | Estructura obligatoria |

\#\#\#\# 3.5 Namespaces Redis  
\- \`mpat:sc:{hash(tenant\_id+prompt+model\_id)}\` TTL=86400s Hash \[RES.004\]

\#\#\#\# 3.6 Integraciones con otras capas  
Capa 5 genera el hash del prompt y model\_id. Capa 12 provee el tenant\_id verificado. Capa 14 define el TTL por dominio.

\#\#\#\# 3.7 OTel spans definidos  
\- Span \`cache.hit\`: atributos: \`tenant\_id\`, \`model\_id\`, \`cache\_key\_hash\`  
\- Span \`cache.miss\`: atributos: \`tenant\_id\`, \`model\_id\`

\#\#\#\# 3.8 Trampa educativa  
La trampa es pensar que con solo guardar la respuesta idéntica al mismo prompt es suficiente. La RES.004 resuelve un ataque donde prompts \*semánticamente distintos pero similares\* entre distintos tenants colisionaban en la misma clave, permitiendo a un tenant leer respuestas de otro.

\---

\#\#\# RES.081 — P2P Learning entre alumnos del mismo tenant  
\*\*FUT asociado:\*\* FUT.29 \*\*Fecha:\*\* 2026-05-08 \*\*Version:\*\* V2\_75

\#\#\#\# 3.1 Problema que resolvia  
Cada alumno tenía memoria completamente aislada, impidiendo que conceptos bien consolidados por un alumno enriquecieran a otros del mismo tenant.

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*Opcion A:\*\* Memoria completamente compartida entre todos los alumnos del tenant — descartada por privacidad.  
\- \*\*Opcion B:\*\* Sincronización de pool compartido con consentimiento \+ anonimización — elegida.  
\- \*\*Opcion C:\*\* Sincronización automática sin consentimiento — descartada por ética y privacidad.

\#\#\#\# 3.3 Decision elegida y justificacion  
Pool P2P opt-in: solo conceptos con confidence \>= 0.75 y consent=True se comparten. El contributed\_by se anonimiza (SHA256 del session\_id truncado a 16 chars). El tenant\_id jamás cruza.

\#\#\#\# 3.4 Parametros resultantes  
| Parametro | Valor default | Rango | Descripcion |  
|---|---|---|---|  
| \`p2p\_min\_confidence\` | 0.75 | 0.5–1.0 | Confianza mínima para contribuir |  
| \`p2p\_shared\_ttl\_seconds\` | 2592000 | 86400–7776000 | TTL del pool compartido |

\#\#\#\# 3.5 Namespaces Redis  
\- \`mpat:pv:{tenant\_id}:shared:{concept\_hash}\` TTL=2592000s (30 días) \[RES.081\]

\#\#\#\# 3.6 Integraciones con otras capas  
ECS (Capa 6\) contiene el campo consent. Capa 9 NHP garantiza que tenant\_id es auténtico antes de escribir en el pool.

\#\#\#\# 3.7 OTel spans definidos  
\- Span \`p2p.contribute\`: atributos: \`tenant\_id\`, \`confidence\`, \`concept\_hash\`  
\- Span \`p2p.fetch\`: atributos: \`tenant\_id\`, \`concept\_hash\`

\#\#\#\# 3.8 Trampa educativa  
La trampa es pensar que P2P Learning sin consentimiento es aceptable si el \`contributed\_by\` se anonimiza. El anonimato no elimina la necesidad de consentimiento: el alumno tiene derecho a decidir si comparte su conocimiento, independientemente de si puede ser identificado.

\---

\#\#\# RES.119 — Dream Cycle \+ Aprendizaje Hebbiano  
\*\*FUT asociado:\*\* FUT\_3 \*\*Fecha:\*\* 2026-05-12 \*\*Version:\*\* V3\_01

\#\#\#\# 3.1 Problema que resolvia  
El sistema de memoria V2 retenía fragmentos pero no aprendía de ellos. No había diferencia entre un fragmento que había resuelto 100 tareas y uno que no había sido usado nunca. El reranking era puramente semántico y no capturaba el valor instrumental histórico de cada fragmento.

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*Opcion A:\*\* Solo semántica (cosine similarity) — insuficiente: no captura valor instrumental.  
\- \*\*Opcion B:\*\* Q-Value Reranking (RL) solo — elegible, pero no fortalece conexiones entre fragmentos relacionados.  
\- \*\*Opcion C:\*\* Q-Value \+ Hebbiano \+ Dream Cycle — elegida: cubre tanto el valor instrumental de cada fragmento (Ori-Mnemos) como las conexiones entre fragmentos co-activados (Hebbiano) y la consolidación asíncrona (Dream Cycle).

\#\#\#\# 3.3 Decision elegida y justificacion  
Implementación en tres capas complementarias: Dream Cycle consolida en idle, Ori-Mnemos prioriza por valor instrumental, HebbianManager fortalece conexiones. Los tres se combinan en el DreamCycleProcessor que orquesta el pipeline completo.

\#\#\#\# 3.4 Parametros resultantes  
| Parametro | Valor default | Rango | Descripcion |  
|---|---|---|---|  
| \`dream\_cycle\_interval\_s\` | 300 | 60–3600 | Idle antes de activar Dream Cycle |  
| \`hebbian\_eta\` | 0.10 | 0.01–0.5 | Tasa de fortalecimiento hebbiano |  
| \`hebbian\_decay\` | 0.005 | 0.001–0.05 | Decaimiento hacia baseline |  
| \`qvalue\_alpha\` | 0.10 | 0.01–0.5 | Tasa de aprendizaje Q |  
| \`qvalue\_gamma\` | 0.90 | 0.5–0.99 | Factor de descuento Q |  
| \`rerank\_alpha\_semantic\` | 0.60 | 0.3–0.9 | Peso semántico en reranking |  
| \`rerank\_alpha\_qvalue\` | 0.40 | 0.1–0.7 | Peso Q-Value en reranking |

\#\#\#\# 3.5 Namespaces Redis  
\- \`mpat:dream:{tenant\_id}:buffer\` TTL=3600s List\[JSON\] \[Dream Cycle\]  
\- \`mpat:rmh:{tenant\_id}:qval:{fragment\_id}\` TTL=7776000s Float \[Ori-Mnemos\]  
\- \`mpat:hebbian:{tenant\_id}:{fragment\_id}\` TTL=7776000s Float \[Hebbiano\]

\#\#\#\# 3.6 Integraciones con otras capas  
Dream Cycle opera sobre fragmentos de la Memoria Vectorial (ChromaDB/FAISS). Ori-Mnemos es llamado por Dream Cycle. HebbianManager es llamado por Dream Cycle en bulk\_strengthen. Ninguna de las tres opera durante ejecución activa del tenant (INV-8-DC.1).

\#\#\#\# 3.7 OTel spans definidos  
\- Span \`dream\_cycle.run\`: atributos: \`tenant\_id\`, \`processed\`, \`consolidated\`, \`stale\`  
\- Span \`memory.rerank\`: atributos: \`tenant\_id\`, \`fragment\_id\`, \`q\_value\`, \`semantic\_score\`, \`final\_score\`

\#\#\#\# 3.8 Trampa educativa  
La trampa es pensar que el Dream Cycle es solo un proceso de limpieza de memoria (eliminar fragmentos viejos). En realidad, es un proceso de CONSOLIDACION: fortalece las conexiones entre fragmentos útiles y solo marca como stale los que no aportaron valor. La limpieza es secundaria; el fortalecimiento es el objetivo principal.

\---

\#\# 4\. Integración V3\_01 — Cadena A2A \+ SubQ \+ Unikernel

\[NO APLICA — Capa 8 no es 7, 11, 12 ni 13\]

Nota de integración indirecta: el aislamiento de tenant en Memoria Vectorial (INV-8-VM.1) y en todos los namespaces Redis de Capa 8 es requisito previo para que A2A cross-tenant sea seguro. Un fallo de aislamiento en Capa 8 comprometería la cadena A2A completa.

\---

\#\# 5\. Estado final de la capa en V3\_01

Post-aplicación de FUT\_3, la Capa 8 tiene los siguientes componentes activos:

| Componente | Estado | Cambio respecto a V2\_102 |  
|---|---|---|  
| Memoria Activa | ACTIVO | Alimenta dream\_buffer antes de DESTROY |  
| Memoria Vectorial \+ ChromaDB/FAISS | ACTIVO | Campo \`hebbian\_weight\` agregado a fragmentos |  
| Context Pruning | ACTIVO | Considera hebbian\_weight en decisión |  
| Semantic Caching (RES.004) | ACTIVO | Sin cambio en lógica; clave tenant\_id obligatoria |  
| P2P Learning (RES.081) | ACTIVO | Sin cambio en V3\_01 |  
| Dream Cycle | NUEVO V3\_01 | Consolidación asíncrona durante idle |  
| Ori-Mnemos RMH | NUEVO V3\_01 | Q-Value reranking de fragmentos |  
| HebbianManager | NUEVO V3\_01 | Fortalecimiento de conexiones entre fragmentos |

Invariantes vigentes: 11 invariantes (INV-8-VM.1, INV-8-SC.1, INV-8-P2P.1/2/3, INV-8-DC.1/2/3/4, INV-8-RMH.1/2/3/4, INV-8-HB.1/2/3/4/5).

\---

\#\# 6\. Flujo de datos completo

\`\`\`  
Agente activo → genera fragmentos → Memoria Activa  
Memoria Activa → serializa como DreamFragment → mpat:dream:{tenant\_id}:buffer (pre-DESTROY)  
\[idle tenant\] → DreamCycleProcessor.run\_cycle()  
  → lee dream\_buffer  
  → \_detect\_co\_activations (ventana de 5 fragmentos)  
  → OriMnemosRMH.rerank\_and\_consolidate()  
    → get\_q\_value por fragment\_id → mpat:rmh:{tenant\_id}:qval:{fragment\_id}  
    → combined \= (q+1)/3 \* hebbian\_weight  
    → consolidated si combined \>= 0.3 / stale si no  
  → HebbianManager.bulk\_strengthen(co\_activations, reward)  
    → mpat:hebbian:{tenant\_id}:{fragment\_id} \+= hebbian\_eta \* reward  
  → VectorStore.update\_hebbian\_weight(fragment\_id, new\_weight)  
  → VectorStore.mark\_stale(fragment\_id) para los stale  
  → elimina mpat:dream:{tenant\_id}:buffer  
PolicyEnforcer (Capa 14\) → auditoria en cada paso vía config/memory.yaml  
\`\`\`

\---

\#\# 7\. Config files V3\_01

| Config file | Parametros clave | RES origen |  
|---|---|---|  
| \`config/memory.yaml\` | \`context\_pruning\_threshold\`, \`semantic\_cache\_ttl\`, \`p2p\_min\_confidence\`, \`dream\_cycle\_interval\_s\`, \`hebbian\_eta\`, \`hebbian\_decay\`, \`qvalue\_alpha\`, \`qvalue\_gamma\`, \`rerank\_alpha\_semantic\`, \`rerank\_alpha\_qvalue\` | RES.004, RES.081, RES.119 |

\---

\#\# 8\. Puntos de atencion para implementacion

\- \*\*CRITICO:\*\* INV-8-DC.1 — el Dream Cycle NUNCA puede activarse durante ejecución activa del tenant. Verificar que el scheduler verifica el estado del orquestador antes de iniciar el ciclo.  
\- \*\*CRITICO:\*\* INV-8-VM.1 — ninguna búsqueda vectorial puede cruzar colecciones de tenants distintos. Esta regla es normativa, no depende de la configuración de ChromaDB.  
\- \*\*MANDATORIO:\*\* RES.004 — jamás eliminar tenant\_id de la clave del semantic cache sin actualizar las RESOLUCIONES. Está documentado como corrección de seguridad con evidencia formal.  
\- \*\*RESTRICCION:\*\* INV-8-HB.2 — HebbianManager.strengthen() solo opera con reward \> 0\. Si reward \<= 0, retorna sin modificar pesos.  
\- \*\*INVARIANTE:\*\* INV-8-RMH.4 — \`rerank\_alpha\_semantic \+ rerank\_alpha\_qvalue \= 1.0\`. Si se modifican ambos parámetros vía policy.yaml, validar que suman 1.0 antes de aplicar.  
\- \*\*INVARIANTE:\*\* Q-Value clampeado en \[-1.0, 2.0\], hebbian\_weight clampeado en \[0.1, 3.0\]. Respetar rangos en tests.

\---

\#\# 9\. Datos faltantes o inconsistencias detectadas

\- La documentación de V3\_01 no especifica el mecanismo exacto de activación del Dream Cycle en producción (cron job, proceso separado, hook del orquestador). Pendiente definir en ARQUITECTURA\_base.  
\- No hay especificación formal de cuántos fragmentos máximos puede contener el dream\_buffer antes de truncarse. Recomendado: definir \`dream\_buffer\_max\_size\` en config/memory.yaml.  
\- \`DreamFragment.co\_activations\` tiene window\_size=5 hardcodeado en \`\_detect\_co\_activations\`. Debería ser configurable vía policy.yaml (P4).

\---

\*INFORME\_CAPA\_08\_V3\_01.md · AGT 2026 · cursos.agt@gmail.com · 2026-05-14\*  
\*Generado en reparacion RELAY\_004 · autorizado por docente · 2026-05-14\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
