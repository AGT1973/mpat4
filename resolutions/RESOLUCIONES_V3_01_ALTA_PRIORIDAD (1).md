\# RESOLUCIONES\_V3\_01\_ALTA\_PRIORIDAD.md · MPAT  
\<\!-- Fuente única de verdad para decisiones técnicas de V3\_01 — Alta Prioridad \--\>  
\<\!-- Generado: 2026-05-12 · cursos.ai.agt@gmail.com \--\>  
\<\!-- Rango: RES.119 a RES.120 · Version: V3\_01 · RELAY\_002 sub-sesion \--\>  
\<\!-- Cubre: FUT\_3 de CAPA\_08 (Dream Cycle) y CAPA\_09 (NHP Protocol) sin RES formal previo \--\>  
\<\!-- Complementa: RESOLUCIONES\_V3\_01.md (RES.113-RES.118) \--\>

\---

\#\# GUIA DE LECTURA

Estas RES completan la cobertura de RELAY\_001 Alta Prioridad.  
RES.119 y RES.120 cubren los FUT\_3 de las capas 08 y 09 que quedaron  
sin resolución formal en la sesión anterior de RELAY\_002.

Regla: estas RES son específicas de capa. RES.119 afecta solo Capa 8\.  
RES.120 afecta Capa 9 y se integra con RES.113 (A2A) y RES.115 (Unikernel).

\---

\#\# Tabla resumen — RES V3\_01 Alta Prioridad

| RES | FUT\_3 | Componente | Capas afectadas | Estado |  
|---|---|---|---|---|  
| RES.119 | §8.01/§8.02/§8.03 | Dream Cycle \+ Ori-Mnemos RMH \+ Aprendizaje Hebbiano | 8 | CERRADO |  
| RES.120 | §9.NHP/§9.ASL/§9.ZTS | NHP Protocol \+ ASL-3 \+ Zero Trust Session | 9 | CERRADO |

\---

\#\# RES.119 · FUT\_3 §8.01 \+ §8.02 \+ §8.03 · Dream Cycle \+ Ori-Mnemos RMH \+ Aprendizaje Hebbiano  
Fecha: 2026-05-12 · Version: V3\_01  
Capa: 8 (Memoria Persistente)  
Config: config/dream\_cycle.yaml \+ config/memory.yaml  
Paradigma: Co-evolution Human-AI — el sistema no solo retiene, consolida y prioriza

\*\*Que se decidio:\*\*  
Extender la Capa 8 de almacén pasivo a sistema cognitivo activo mediante tres  
mecanismos interconectados:

1\. Dream Cycle: proceso de consolidación asíncrona post-sesión que procesa  
   la Memoria Activa, detecta patrones, refuerza conexiones de alta frecuencia,  
   y descarta registros de baja relevancia. Se ejecuta en estado DESTROY del ECS.

2\. Ori-Mnemos RMH (Relevance Memory Hierarchy): gestor de pesos de memoria  
   que mantiene un score de relevancia \`hebbian\_weight\` (float, default 1.0)  
   por vector en ChromaDB/FAISS. El peso sube con cada acceso exitoso y decae  
   con el tiempo según \`hebbian\_decay\_rate\`.

3\. Aprendizaje Hebbiano: regla de actualización de pesos inspirada en  
   neurociencia — "neuronas que se activan juntas, se conectan". Vectores  
   accedidos conjuntamente en la misma sesión incrementan su peso mutuamente.

Namespaces Redis:  
\- mpat:dream:{tenant\_id}:queue — Stream MAXLEN\~1000 (tareas de consolidacion pendientes)  
\- mpat:dream:{tenant\_id}:log — Stream MAXLEN\~500 (resultado de cada ciclo)  
\- mpat:hebbian:{tenant\_id}:{vector\_id} — HASH (hebbian\_weight \+ last\_accessed \+ access\_count)

Parametros:  
| Parametro | Default | Rango |  
|---|---|---|  
| dream\_cycle.enabled | true | bool |  
| dream\_cycle.trigger | "on\_destroy" | "on\_destroy" \\| "scheduled" \\| "both" |  
| dream\_cycle.min\_session\_events | 5 | \[1-100\] |  
| dream\_cycle.consolidation\_threshold | 0.65 | \[0.40-0.95\] |  
| dream\_cycle.discard\_threshold | 0.20 | \[0.05-0.50\] |  
| hebbian.decay\_rate | 0.01 | \[0.001-0.10\] |  
| hebbian.reinforce\_delta | 0.05 | \[0.01-0.20\] |  
| hebbian.max\_weight | 5.0 | \[1.0-10.0\] |  
| hebbian.min\_weight | 0.1 | \[0.01-1.0\] |  
| memory.retention\_threshold | 0.30 | \[0.10-0.80\] |

\*\*Por que se decidio:\*\*

| Posicion A (descartada) | Posicion B (descartada) | Posicion adoptada (C) |  
|---|---|---|  
| Memoria pasiva — todos los vectores con peso uniforme | Decay temporal simple sin refuerzo | Dream Cycle \+ Hebbian weights con refuerzo activo |

Razonamiento:  
Memoria pasiva con peso uniforme genera ruido acumulativo: cada sesion agrega  
vectores sin discriminar relevancia. A largo plazo, las busquedas por similaridad  
devuelven resultados de baja calidad porque fragmentos irrelevantes compiten  
con conocimiento valioso.  
Decay temporal simple descarta sin criterio de uso real — un vector accedido  
frecuentemente pero hace 30 dias seria descartado igual que uno nunca accedido.  
Dream Cycle \+ Hebbian: el sistema refuerza lo que usa y deja decaer lo que no.  
El resultado es una memoria que se auto-organiza segun el patron de uso del tenant,  
no segun una politica de retencion arbitraria.

Trampa educativa: "el aprendizaje hebbiano es solo para redes neuronales biologicas".  
Incorrecto: el principio — conexiones que se activan juntas se refuerzan — es  
aplicable a cualquier sistema de recuperacion de informacion ponderada.  
Aqui los "vectores" son los nodos y los "pesos" son hebbian\_weight en ChromaDB.  
No es IA biologica — es una heuristica de relevancia contextual implementada  
en infraestructura estandar de bases de datos vectoriales.

\*\*Como se implementa:\*\*  
\- Clase: DreamCycleProcessor — se activa en DESTROY del ECS, lee Memoria Activa,  
  consolida vectores con score \> consolidation\_threshold, descarta \< discard\_threshold  
\- Clase: OriMnemosRMH — gestiona hebbian\_weight por vector, expone  
  update\_weight(vector\_id, delta) y decay\_all(tenant\_id)  
\- Clase: HebbianLearner — detecta co-activacion de vectores en sesion,  
  llama update\_weight para cada par co-activado  
\- Context Pruning V3\_01 (8.3): ahora usa \`score \* hebbian\_weight \> retention\_threshold\`  
  en lugar de solo score semantico — vectores con alto peso hebbiano se retienen  
  aunque su similaridad puntual sea baja

Invariantes:  
\- INV-8-DC.1: Dream Cycle NUNCA interrumpe un ECS en ejecucion — solo se activa en DESTROY  
\- INV-8-DC.2: Dream Cycle es no-bloqueante — fallo silencioso, nunca propaga excepcion  
\- INV-8-HB.1: hebbian\_weight siempre dentro de \[min\_weight, max\_weight\]  
\- INV-8-HB.2: aislamiento de pesos por tenant\_id — hebbian de tenant\_A nunca afecta tenant\_B

\*\*Donde vive en el codigo:\*\*  
\- memory/dream\_cycle\_processor.py (Capa 8\)  
\- memory/ori\_mnemos\_rmh.py (Capa 8\)  
\- memory/hebbian\_learner.py (Capa 8\)  
\- config/dream\_cycle.yaml  
\- config/memory.yaml (parametro: retention\_threshold, hebbian.\*)

\*\*ID de archivo que implementa esta RES:\*\*  
\- CAPA\_08\_MASTER\_V3\_01.md: 1qAN2il5qEU5NvZAHksWBzniKI233jGJj

\*\*Nota sobre RES.096 (V2):\*\*  
RES.096 registrado en sesiones anteriores cubria Dream Cycle en version conceptual V2.  
RES.119 lo reemplaza y formaliza con Design-by-Contract completo, parametros de Capa 14,  
invariantes, y alineacion con Unikernel (RES.115) y ZeroTrustSession (RES.120).  
RES.096 queda deprecated en V3\_01. Referencia historica unicamente.

\---

\#\# RES.120 · FUT\_3 §9.NHP \+ §9.ASL \+ §9.ZTS · NHP Protocol \+ ASL-3 \+ Zero Trust Session  
Fecha: 2026-05-12 · Version: V3\_01  
Capa: 9 (Seguridad)  
Config: config/nhp.yaml \+ config/security.yaml  
Paradigma: Post-Automation Paradigm — seguridad diseñada para agentes, no solo para usuarios

\*\*Que se decidio:\*\*  
Adoptar tres mecanismos de seguridad nuevos en V3\_01 para cubrir el modelo  
de amenazas de un sistema multi-agente:

1\. NHP Protocol (Neural Handshake Protocol): authenticate-before-connect.  
   Cada par de agentes que se comunican deben completar un handshake criptografico  
   antes de que fluyan datos operativos. El handshake verifica AgentCard firmada,  
   tenant\_id coincidente, y nonce de un solo uso con TTL de 30s.

2\. ASL-3 (Agentic Security Level 3): clasificacion de nivel de riesgo por tarea.  
   ASL-2 para tareas de bajo impacto (lectura, analisis). ASL-3 para tareas  
   de alto impacto (escritura, delegacion con budget \> umbral, acceso a datos sensibles).  
   En ASL-3: NHP obligatorio \+ aprobacion HITL si hitl.required\_for\_asl3 \= true.

3\. Zero Trust Session (ZTS): sesion de confianza cero por ejecucion de tarea.  
   Cada task\_id genera una ZeroTrustSession con zts\_session\_id unico.  
   La sesion expira en zts\_max\_session\_age\_s (default: 3600s).  
   Sin ZTS activa, ningun agente puede recibir datos del Orchestrator.

Namespaces Redis:  
\- mpat:nhp:nonces:{tenant\_id} — SET TTL=30s (nonces usados, anti-replay)  
\- mpat:zts:{tenant\_id}:{task\_id} — HASH TTL=3600s (sesion activa)  
\- mpat:zts:registry:{tenant\_id} — ZSET (score=expiry\_timestamp, member=zts\_session\_id)  
\- mpat:asl:{tenant\_id}:{task\_id} — STRING ("ASL-2"|"ASL-3") TTL=task\_lifetime

Parametros:  
| Parametro | Default | Rango |  
|---|---|---|  
| nhp.enabled | true | bool |  
| nhp.session\_ttl\_seconds | 300 | \[60-3600\] |  
| nhp.nonce\_window\_seconds | 30 | \[10-120\] |  
| nhp.require\_for\_asl3 | true | bool |  
| asl.default\_level | "ASL-2" | "ASL-2"\\|"ASL-3" |  
| asl.budget\_threshold\_asl3 | 1000 | \[100-100000\] tokens |  
| asl.delegation\_threshold\_asl3 | true | bool — toda delegacion A2A \= ASL-3 |  
| security.zts\_max\_session\_age\_s | 3600 | \[300-86400\] |  
| security.nhp\_failure\_rate\_threshold | 0.05 | \[0.01-0.20\] |

\*\*Por que se decidio:\*\*

| Posicion A (descartada) | Posicion B (descartada) | Posicion adoptada (C) |  
|---|---|---|  
| JWT estatico entre agentes | mTLS por certificado de agente | NHP handshake \+ ZTS por task\_id |

Razonamiento:  
JWT estatico puede ser robado y reutilizado sin limite temporal — un agente  
comprometido puede impersonar a otro indefinidamente. mTLS requiere  
infraestructura PKI completa por agente: costoso, complejo de rotar certificados  
en sistemas dinamicos donde los agentes se crean y destruyen por sesion.  
NHP \+ ZTS: el handshake expira por diseno (30s nonce \+ 300s session).  
La ZTS vincula la autorizacion a un task\_id especifico — un token capturado  
de task\_A no puede usarse para task\_B porque la ZTS verifica task\_id.  
Compatible con Unikernel (RES.115): la ZTS incluye session\_id del unikernel,  
garantizando que la autorizacion esta vinculada tanto a la tarea como al  
contexto de ejecucion del tenant.

Trampa educativa: "autenticar al agente es lo mismo que autenticar al usuario".  
Incorrecto: en un sistema multi-agente, un usuario puede delegar a un agente  
que delega a otro. El usuario autentico al inicio de la cadena pero el agente  
del extremo puede ser malicioso o comprometido. NHP verifica la identidad  
de CADA agente en CADA salto — no solo en el entry point del sistema.  
Esto cubre el vector de ataque de "agent-in-the-middle" donde un agente  
intermedio manipula el payload antes de reenviarlo.

\*\*Como se implementa:\*\*  
\- Clase: NHPProtocol — initiate(agent) → nonce \+ timestamp;  
  respond(initiator, responder, nonce, ts) → NHPResult con session\_token  
\- Clase: ZeroTrustSessionManager — create\_session(task\_id, agent\_id, tenant\_id) → zts\_session\_id;  
  validate\_session(zts\_session\_id) → bool; revoke\_session(zts\_session\_id, reason)  
\- Clase: ASLClassifier — classify(task: TaskContext) → "ASL-2" | "ASL-3"  
  basado en budget, tipo de operacion, y presencia de delegacion A2A  
\- Integracion Capa 10 (Observabilidad): NHP verification failed → log evento  
  \`{ task\_id, agent\_id, nhp\_error\_code }\` \+ alerta si failure rate \> threshold  
\- Integracion Capa 14 (policy.yaml): parametros nhp.\* y asl.\* configurables  
  sin redeployar codigo — PolicyEnforcer lee config en cada request

Invariantes:  
\- INV-NHP.1: Agente NUNCA recibe datos operativos sin NHP exitoso en ASL-3  
\- INV-NHP.2: Nonce de un solo uso — reutilizacion \= rechazo inmediato  
\- INV-NHP.3: tenant\_id iniciador \== tenant\_id respondedor — cross-tenant bloqueado  
\- INV-NHP.4: session\_token expira en nhp.session\_ttl\_seconds  
\- INV-ZTS.1: Cada task\_id tiene exactamente una ZTS — no compartida entre tareas  
\- INV-ZTS.2: ZTS revocada \= acceso denegado inmediato para ese task\_id  
\- INV-ASL.1: Delegacion A2A con budget \> asl.budget\_threshold\_asl3 → siempre ASL-3

\*\*Donde vive en el codigo:\*\*  
\- security/nhp\_protocol.py (Capa 9\)  
\- security/zero\_trust\_session\_manager.py (Capa 9\)  
\- security/asl\_classifier.py (Capa 9\)  
\- config/nhp.yaml  
\- config/security.yaml

\*\*Integracion cross-RES critica:\*\*  
\- RES.113 (A2A): cada A2A envelope pasa por ASLClassifier antes de dispatch.  
  Si ASL-3: NHPProtocol.respond() debe retornar NHPResult.success=True.  
\- RES.115 (Unikernel): ZTS incluye session\_id del unikernel — autorizacion vinculada  
  al contexto de ejecucion, no solo a la identidad del agente.  
\- RES.030 (Observabilidad Capa 10 — V2): alertas de NHP failure rate ya documentadas  
  en CAPA\_10\_MASTER\_V3\_01.md §10.06 — ZTS y NHP tienen spans y alertas formales.

\*\*ID de archivo que implementa esta RES:\*\*  
\- CAPA\_09\_MASTER\_V3\_01.md: 1SmM9aJpSOY90jnzEHFk32qOXuVi-9MfB

\---

\#\# Notas de integracion cross-RES — extension V3\_01

\#\#\# Cadena de seguridad completa V3\_01

La cadena de ejecucion segura en V3\_01 combina todas las RES:

\`\`\`  
Usuario → \[ZTS creada (RES.120)\] → Orchestrator  
  → ASLClassifier (RES.120): ¿ASL-2 o ASL-3?  
    → Si ASL-3: NHP handshake (RES.120) entre agentes  
    → A2A dispatch (RES.113): envelope con session\_id  
    → SubQ si larga duracion (RES.114)  
    → UniKernelDeliveryGuard (RES.115): validar (tenant\_id, session\_id)  
    → Observabilidad (RES.030/CAPA\_10): spans \+ alertas en cada paso  
    → PolicyEnforcer (Capa 14): auditoria de envelope en cada salto  
\`\`\`

Cualquier brecha en esta cadena viola el modelo de seguridad V3\_01.

\#\#\# Estado de cobertura RELAY\_002

| Capa | FUT\_3 | RES formal | Estado |  
|---|---|---|---|  
| CAPA\_07 | MCP 2.0 \+ Tool Registry \+ Skill Validation | RES.116-118 | CERRADO |  
| CAPA\_08 | Dream Cycle \+ Ori-Mnemos \+ Hebbiano | RES.119 (este archivo) | CERRADO |  
| CAPA\_09 | NHP \+ ASL-3 \+ ZTS | RES.120 (este archivo) | CERRADO |  
| CAPA\_11 | Unikernel \+ SubQ | RES.114-115 | CERRADO |  
| CAPA\_12 | A2A \+ SubQ \+ Unikernel | RES.113-115 | CERRADO |  
| CAPA\_13 | A2A Delivery \+ SubQ \+ Unikernel | RES.113-115 | CERRADO |  
| CAPA\_05 | ShadowRadix \+ CSA/HCA \+ NVFP4 | RES.030 V2 — pendiente V3\_01 | RELAY\_005 |  
| CAPA\_01/02/04/14 | Foundations \+ A2A base \+ policy.yaml | Heredado V2 — sin cambios V3\_01 | OK |

\#\#\# Pendientes que CIERRAN con este archivo

\- PENDIENTE-001 de RESOLUCIONES\_V3\_01.md → CERRADO por RES.120  
\- PENDIENTE-002 de RESOLUCIONES\_V3\_01.md → CERRADO por RES.119

\#\#\# Pendiente que permanece

\- PENDIENTE-003 (ShadowRadix \+ CSA/HCA — CAPA\_05) → RELAY\_005 investigaciones  
\- PENDIENTE-004 (gdoc accidental en informes/) → accion manual en Drive

\---

\*MPAT · RESOLUCIONES\_V3\_01\_ALTA\_PRIORIDAD · V3\_01 · AGT 2026-05-12\*  
\*Generado por: cursos.ai.agt@gmail.com · 2026-05-12\*  
\*RELAY\_002 sub-sesion — RES.119 (Dream Cycle \+ Ori-Mnemos RMH \+ Hebbiano) \+ RES.120 (NHP \+ ASL-3 \+ ZTS)\*  
\*RELAY\_002 CERRADO: RES.113-RES.120 cubren todos los FUT\_3 de RELAY\_001 excepto ShadowRadix (→ RELAY\_005)\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
