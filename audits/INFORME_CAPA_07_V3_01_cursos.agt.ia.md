\# INFORME CAPA 07 — TOOL INTEGRATION LAYER · MCP 2.0 \+ Tool Registry \+ Skill Validation Pipeline  
\*\*Version fuente:\*\* V3\_01  
\*\*Alumno:\*\* cursos.agt.ia@gmail.com  
\*\*Fecha:\*\* 2026-05-14  
\*\*RES que afectan esta capa:\*\* RES.116 (MCP 2.0 Streaming), RES.117 (Tool Registry), RES.118 (Skill Validation Pipeline)  
\*\*Paradigma predominante:\*\* Inteligencia Artificial Generativa y Agéntica

\---

\#\# 1\. Descripcion de la capa

La Capa 7 es el \*\*motor de ejecucion de herramientas\*\* de MPAT V3\_01. Su responsabilidad es mediar entre la intencion del agente orquestador (Capa 3\) y la ejecucion concreta de skills, APIs y servicios externos. En V3\_01 evoluciona de un sistema de "llamadas a funciones" a un sistema de "contratos de ejecucion verificados con streaming nativo".

\*\*Principio rector:\*\* P13 — AI Specifiers Rule. Toda herramienta que ingresa al ecosistema debe presentar un contrato legible por maquina antes de ser invocada. La Capa 7 es el guardian de ese contrato.

\*\*Evolucion V2 a V3\_01:\*\*  
En V2, las tools eran funciones hardcodeadas en los agentes. El catalogo era estatico, la ejecucion sincrona, y no habia validacion de seguridad formal. En V3\_01, las tres adiciones de FUT\_3 transforman la capa:  
\- \*\*§7.01 MCP 2.0 Streaming (RES.116):\*\* tool calls largas dejan de bloquear al orquestador.  
\- \*\*§7.02 Tool Registry (RES.117):\*\* catalogo dinamico y saludable de herramientas en Redis.  
\- \*\*§7.03 Skill Validation Pipeline (RES.118):\*\* validacion automatica de skills antes de activarlos.

\*\*Lo que NO hace la Capa 7:\*\*  
\- No decide si invocar una tool (eso es Capa 3 — Orchestrator).  
\- No gestiona identidad del agente que invoca (eso es Capa 1 \+ Capa 4).  
\- No valida el resultado semantico de la tool (eso es Capa 9 — Critic/ZeroTrust).  
\- No es punto de entrada ni salida para A2A (RES.113) ni SubQ (RES.114) ni Unikernel (RES.115) directamente. Si puede integrar tool calls largas via SubQ y recibir delegaciones A2A con task\_type="mcp\_tool\_call".

\---

\#\# 2\. Componentes de la capa

\#\#\# 2.1 — MPATSkillServer (base MCP 2.0)  
\- \*\*Que hace:\*\* Clase base para todos los servidores de skills de MPAT. Expone tools, resources y prompts via JSON-RPC 2.0. Soporta stdio (ejecucion local) y SSE (streaming remoto). Cada skill de MPAT es un servidor MCP 2.0 independiente.  
\- \*\*Capa de origen:\*\* 7  
\- \*\*RES que lo definen:\*\* RES.116  
\- \*\*Dependencias:\*\* Capa 3 (Orchestrator conecta servers por sesion), Capa 14 (policy.yaml define servers por tenant)  
\- \*\*Namespaces Redis propios:\*\* ninguno — servidor MCP es stateless entre llamadas  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agéntica  
\- \*\*Config file V3\_01:\*\* \`config/mcp.yaml\`

\*\*Design-by-Contract:\*\*  
\`\`\`  
Precondicion: skill\_id registrado en ToolRegistry con health=UP  
Postcondicion: retorna dict con campo "result" o "error", nunca silencio  
Invariante INV-7-SERVER.1: todo servidor MCP 2.0 debe implementar list\_tools() y call\_tool()  
\`\`\`

\---

\#\#\# 2.2 — MCPStreamingClient \[V3\_01 NUEVO — RES.116\]  
\- \*\*Que hace:\*\* Inicia tool calls de larga duracion via SSE. Publica chunks en \`mpat:mcp:stream:{tool\_call\_id}\`. El orquestador no espera — retorna inmediatamente. Compatible con SubQ: tool calls muy largas pueden delegarse a SubQDispatcher.  
\- \*\*Capa de origen:\*\* 7  
\- \*\*RES que lo definen:\*\* RES.116  
\- \*\*Dependencias:\*\* Capa 3, Capa 11/12 (SubQ), Capa 10 (OTel)  
\- \*\*Namespaces Redis propios:\*\*  
  \- \`mpat:mcp:stream:{tool\_call\_id}\` TTL=300s Stream MAXLEN\~500  
  \- \`mpat:mcp:active:{tenant\_id}\` TTL=sesion SET  
  \- \`mpat:mcp:result:{tool\_call\_id}\` TTL=300s HASH  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agéntica  
\- \*\*Config file V3\_01:\*\* \`config/mcp.yaml\`

\*\*Invariante INV-7-STREAM.1:\*\* todo chunk debe incluir \`tool\` y \`type\`. Chunks malformados se descartan silenciosamente.

\*\*Trampa educativa:\*\* "Streaming en MCP significa que el modelo recibe los tokens del LLM en tiempo real." INCORRECTO. El streaming de Capa 7 es de TOOL CALLS — respuestas de servicios externos. Los tokens del LLM se streaman via Capa 1\. Son mecanismos independientes.

\---

\#\#\# 2.3 — MCPStreamConsumer \[V3\_01 NUEVO — RES.116\]  
\- \*\*Que hace:\*\* Consume \`mpat:mcp:stream:{tool\_call\_id}\`, materializa en \`mpat:mcp:result:{tool\_call\_id}\` cuando llega chunk \`type=done\`. Notifica al orquestador via Redis Pub/Sub.  
\- \*\*Capa de origen:\*\* 7  
\- \*\*RES que lo definen:\*\* RES.116  
\- \*\*Dependencias:\*\* MCPStreamingClient (productor), Capa 3 (suscrito a notificaciones)  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agéntica  
\- \*\*Config file V3\_01:\*\* \`config/mcp.yaml\` (parametro \`stream\_chunk\_timeout\_ms\`)

\---

\#\#\# 2.4 — ToolRegistry \[V3\_01 NUEVO — RES.117\]  
\- \*\*Que hace:\*\* Registro centralizado de herramientas por tenant. Mantiene catalogo en Redis con schema (nombre, descripcion, input\_schema, output\_schema, mcp\_endpoint, health). Agentes consultan antes de invocar cualquier tool.  
\- \*\*Capa de origen:\*\* 7  
\- \*\*RES que lo definen:\*\* RES.117  
\- \*\*Dependencias:\*\* Capa 3, Capa 4 (A2A registra Agent Cards), Capa 9 (NHP firma para trust tier)  
\- \*\*Namespaces Redis propios:\*\*  
  \- \`mpat:tools:registry:{tenant\_id}\` HASH (tool\_name → JSON schema \+ health)  
  \- \`mpat:tools:health:{tool\_name}\` HASH TTL=60s (heartbeat)  
  \- \`mpat:tools:usage:{tenant\_id}:{tool\_name}\` ZSET MAXLEN\~1000  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agéntica  
\- \*\*Config file V3\_01:\*\* \`config/tool\_registry.yaml\`

\*\*Invariante INV-7-REG.1:\*\* el orquestador NUNCA carga mas de \`top\_k=10\` skills por sesion. Superar este limite requiere aprobacion HITL.

\*\*Trampa educativa:\*\* "El ToolRegistry es un diccionario de funciones disponibles." INCORRECTO. Tambien gestiona ESTADO DE SALUD en tiempo real (TTL=60s heartbeat). Un diccionario estatico no puede detectar tools caidas ni redirigir al fallback.

\---

\#\#\# 2.5 — ToolHealthMonitor \[V3\_01 NUEVO — RES.117\]  
\- \*\*Que hace:\*\* Publica heartbeat de cada tool cada 30s actualizando \`mpat:tools:health:{tool\_name}\` con TTL=60s. Si una tool cae, el TTL expira y el agente ve health=DOWN.  
\- \*\*Capa de origen:\*\* 7  
\- \*\*RES que lo definen:\*\* RES.117  
\- \*\*Dependencias:\*\* ToolRegistry (escribe health), Capa 10 (OTel alerta si tool DOWN)  
\- \*\*Namespaces Redis propios:\*\* \`mpat:tools:health:{tool\_name}\` HASH TTL=60s  
\- \*\*Config file V3\_01:\*\* \`config/tool\_registry.yaml\` (parametro \`health\_ttl\_seconds\`)

\---

\#\#\# 2.6 — SkillValidationPipeline \[V3\_01 NUEVO — RES.118\]  
\- \*\*Que hace:\*\* Valida un skill antes de activarlo. Pipeline de 4 etapas: schema check → dependency check (tools en registry) → permission check (RBAC Capa 2\) → dry-run con inputs sinteticos. Si dry-run falla, skill queda en PENDING con log detallado.  
\- \*\*Capa de origen:\*\* 7  
\- \*\*RES que lo definen:\*\* RES.118  
\- \*\*Dependencias:\*\* ToolRegistry, Capa 2 (RBAC), Capa 14 (limites de pasos y timeout)  
\- \*\*Namespaces Redis propios:\*\*  
  \- \`mpat:skills:pending:{tenant\_id}\` ZSET (score=timestamp)  
  \- \`mpat:skills:active:{tenant\_id}\` HASH (skill\_name → JSON validado)  
  \- \`mpat:skills:validation\_log:{skill\_id}\` Stream MAXLEN\~100  
\- \*\*Paradigma:\*\* Inteligencia Artificial Generativa y Agéntica  
\- \*\*Config file V3\_01:\*\* \`config/skill\_validation.yaml\`

\*\*Invariante INV-7-VAL.1:\*\* ningun skill Tier 2 o 3 se ejecuta sin \`sandbox\_ok \= True\`.  
\*\*Invariante INV-7-VAL.2:\*\* validacion sincrona PREVIA a ejecucion. No existe "ejecucion optimista".

\*\*Trampa educativa:\*\* "Un skill validado es un skill seguro." INCOMPLETO. RES.118 garantiza que el skill esta bien formado. No garantiza que no pueda comportarse maliciosamente con inputs reales en produccion — para eso existe el Tier System (Tier 2 \= sandbox obligatorio).

\---

\#\#\# 2.7 — SkillDryRunner \[V3\_01 NUEVO — RES.118\]  
\- \*\*Que hace:\*\* Ejecuta el skill con inputs sinteticos para detectar errores de dependencia o runtime antes de activarlo en produccion. Captura excepciones y las registra en validation\_log.  
\- \*\*Capa de origen:\*\* 7  
\- \*\*RES que lo definen:\*\* RES.118  
\- \*\*Dependencias:\*\* SkillValidationPipeline, ToolRegistry (tools deben estar UP para dry-run)  
\- \*\*Config file V3\_01:\*\* \`config/skill\_validation.yaml\` (parametro \`dry\_run\_timeout\_ms\`)

\---

\#\# 3\. Resoluciones que afectan esta capa

\#\#\# RES.116 — MCP 2.0 Streaming  
\*\*FUT:\*\* FUT\_3 §7.01 \*\*Fecha:\*\* 2026-05-12 \*\*Version:\*\* V3\_01

\#\#\#\# 3.1 Problema  
Tool calls largas bloqueaban el orquestador hasta recibir respuesta completa. El ciclo de inferencia quedaba congelado durante segundos o minutos, degradando la experiencia de todos los tenants activos.

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*A (descartada):\*\* MCP 1.x request/response sincrono — mantiene el bloqueo.  
\- \*\*B (descartada):\*\* Polling de resultado — latencia artificial y carga innecesaria en Redis.  
\- \*\*C (adoptada):\*\* MCP 2.0 Streaming via SSE \+ Redis Stream.

\#\#\#\# 3.3 Decision  
MCP 2.0 Streaming desacopla la duracion de la tool call del ciclo de inferencia. El orquestador inicia la call y continua procesando otros eventos. Compatible con SubQ (RES.114) para tool calls muy largas. Compatible con A2A (RES.113): agentes delegan tool calls via envelope con task\_type="mcp\_tool\_call".

\#\#\#\# 3.4 Parametros  
| Parametro | Valor default | Rango | Descripcion |  
|---|---|---|---|  
| mcp.stream\_maxlen | 500 | \[100-5000\] | MAXLEN del Stream de chunks |  
| mcp.result\_ttl\_seconds | 300 | \[60-3600\] | TTL del resultado materializado |  
| mcp.chunk\_timeout\_ms | 5000 | \[1000-30000\] | Timeout por chunk |  
| mcp.max\_concurrent\_tools | 5 | \[1-20\] | Tools concurrentes por tenant |  
| mcp.streaming\_enabled | true | bool | Habilitar/deshabilitar |

\#\#\#\# 3.5 Namespaces Redis  
\- \`mpat:mcp:stream:{tool\_call\_id}\` TTL=300s Stream MAXLEN\~500 \[RES.116\]  
\- \`mpat:mcp:active:{tenant\_id}\` TTL=sesion SET \[RES.116\]  
\- \`mpat:mcp:result:{tool\_call\_id}\` TTL=300s HASH \[RES.116\]

\#\#\#\# 3.6 Integraciones  
\- Capa 3: Orchestrator inicia via MCPStreamingClient, recibe notificacion de resultado.  
\- Capa 11/12: SubQDispatcher puede recibir tool call delegada en worker separado.  
\- Capa 10: OTel span \`mcp\_tool\_call\`: tool\_name, tenant\_id, duration\_ms, chunk\_count.

\#\#\#\# 3.7 OTel spans  
\- Span \`mcp\_tool\_call\_start\`: tool\_name, tenant\_id, streaming\_mode  
\- Span \`mcp\_chunk\_received\`: tool\_call\_id, chunk\_index, chunk\_size\_bytes  
\- Span \`mcp\_tool\_call\_complete\`: tool\_call\_id, total\_chunks, total\_duration\_ms

\#\#\#\# 3.8 Trampa educativa  
"MCP 2.0 Streaming hace que el LLM responda mas rapido." FALSO. El streaming de Capa 7 acelera la entrega de resultados de TOOLS EXTERNAS, no del modelo de lenguaje. La latencia del LLM la gestiona Capa 5\. Confundir ambos lleva a optimizar la capa equivocada.

\---

\#\#\# RES.117 — Tool Registry  
\*\*FUT:\*\* FUT\_3 §7.02 \*\*Fecha:\*\* 2026-05-12 \*\*Version:\*\* V3\_01

\#\#\#\# 3.1 Problema  
Con mas de 280,000 skills publicos disponibles en 2026, cargar el catalogo completo en contexto es inviable. Los agentes no tenian forma de verificar si una tool estaba disponible antes de invocarla — un agente podia comprometer tokens de razonamiento en un plan que dependia de una tool caida.

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*A (descartada):\*\* Tools hardcodeadas por agente — no escala, requiere redespliegue.  
\- \*\*B (descartada):\*\* Config YAML estatico — no refleja estado de salud en tiempo real.  
\- \*\*C (adoptada):\*\* Registry dinamico en Redis con heartbeat de salud (TTL=60s).

\#\#\#\# 3.3 Decision  
Self-registration al arrancar. Heartbeat cada 30s, TTL=60s. Agentes consultan antes de invocar. Si DOWN → fallback sin error al usuario. Descubrimiento A2A: agentes externos se registran via Agent Cards igual que skills internos.

\#\#\#\# 3.4 Parametros  
| Parametro | Valor default | Rango | Descripcion |  
|---|---|---|---|  
| tool\_registry.health\_ttl\_seconds | 60 | \[10-300\] | TTL del heartbeat |  
| tool\_registry.usage\_maxlen | 1000 | \[100-10000\] | MAXLEN historial de uso |  
| tool\_registry.schema\_version | "v1" | string | Version del schema |  
| tool\_registry.max\_tools\_per\_tenant | 50 | \[5-500\] | Limite por tenant |

\#\#\#\# 3.5 Namespaces Redis  
\- \`mpat:tools:registry:{tenant\_id}\` HASH \[RES.117\]  
\- \`mpat:tools:health:{tool\_name}\` HASH TTL=60s \[RES.117\]  
\- \`mpat:tools:usage:{tenant\_id}:{tool\_name}\` ZSET MAXLEN\~1000 \[RES.117\]

\#\#\#\# 3.6 Integraciones  
\- Capa 3: consulta \`ToolRegistry.search(capability, top\_k)\` antes de planificar.  
\- Capa 4: A2ARouter registra Agent Cards externas.  
\- Capa 9: NHP firma Agent Cards — base del trust tier en RES.118.  
\- Capa 14: define \`registry\_top\_k\` maximo y \`trust\_tier\_min\_external\`.

\#\#\#\# 3.7 OTel spans  
\- Span \`tool\_registry\_search\`: capability, top\_k, results\_count, tenant\_id  
\- Span \`tool\_health\_check\`: tool\_name, health\_status, ttl\_remaining\_ms

\#\#\#\# 3.8 Trampa educativa  
"El ToolRegistry solo sirve para saber que tools existen." FALSO. Tambien gestiona ESTADO DE SALUD en tiempo real. Sin esta consulta, un agente puede planificar pasos que dependen de una tool caida y descubrir el error despues de haber comprometido tokens de razonamiento.

\---

\#\#\# RES.118 — Skill Validation Pipeline  
\*\*FUT:\*\* FUT\_3 §7.03 \*\*Fecha:\*\* 2026-05-12 \*\*Version:\*\* V3\_01

\#\#\#\# 3.1 Problema  
Skills externos maliciosos o malformados podian comprometer la sesion (vector "ClawHavoc"). Sin validacion, el sistema confiaba en que el desarrollador del skill lo hiciera bien — no escalable en multi-tenant.

\#\#\#\# 3.2 Alternativas evaluadas  
\- \*\*A (descartada):\*\* Activar sin validacion — riesgo de seguridad directo.  
\- \*\*B (descartada):\*\* Validacion manual por admin — no escala con decenas de tenants.  
\- \*\*C (adoptada):\*\* Pipeline automatico de 4 etapas con dry-run.

\#\#\#\# 3.3 Decision  
Falla inmediata en schema check (O(1)) antes de llegar al dry-run costoso. APPROVED mueve a \`mpat:skills:active\`. REJECTED genera log detallado y notifica al desarrollador. Integracion con ToolRegistry: dependency check requiere todas las tools del skill en estado UP.

\#\#\#\# 3.4 Parametros  
| Parametro | Valor default | Rango | Descripcion |  
|---|---|---|---|  
| skill\_validation.dry\_run\_timeout\_ms | 10000 | \[1000-60000\] | Timeout del dry-run |  
| skill\_validation.max\_steps | 20 | \[2-100\] | Pasos maximos en un skill |  
| skill\_validation.max\_pending\_per\_tenant | 10 | \[1-50\] | Skills en validacion simultanea |

\#\#\#\# 3.5 Namespaces Redis  
\- \`mpat:skills:pending:{tenant\_id}\` ZSET \[RES.118\]  
\- \`mpat:skills:active:{tenant\_id}\` HASH \[RES.118\]  
\- \`mpat:skills:validation\_log:{skill\_id}\` Stream MAXLEN\~100 \[RES.118\]

\#\#\#\# 3.6 Integraciones  
\- ToolRegistry (RES.117): dependency check llama \`ToolRegistry.get\_tool()\` por cada tool del skill.  
\- Capa 2 (RBAC): permission check verifica permisos del tenant.  
\- Capa 14: limites de pasos y timeout.

\#\#\#\# 3.7 OTel spans  
\- Span \`skill\_validation\_start\`: skill\_id, tenant\_id, step\_count  
\- Span \`skill\_dry\_run\`: skill\_id, duration\_ms, result  
\- Span \`skill\_activated\`: skill\_id, tenant\_id, trust\_tier

\#\#\#\# 3.8 Trampa educativa  
"Un skill validado es un skill seguro." INCOMPLETO. RES.118 garantiza que el skill esta bien formado y sus dependencias existen. No garantiza ausencia de comportamiento malicioso con inputs reales — para eso existe el Tier System. La validacion es necesaria pero no suficiente.

\---

\#\# 4\. Integracion V3\_01 — Cadena MCP 2.0 \+ Tool Registry \+ Skill Validation

\#\#\# 4.4 Pipeline completo de ejecucion de tool en Capa 7

\`\`\`  
Agente (Capa 3\)  
  → ToolRegistry.search(capability, top\_k)     \# RES.117 — descubrir  
  → ToolRegistry.get\_tool(name, tenant\_id)     \# RES.117 — verificar health=UP  
  → SkillValidationPipeline.validate(skill)    \# RES.118 — si skill nuevo  
  → MCPStreamingClient.call\_tool\_streaming()   \# RES.116 — ejecutar  
  → MCPStreamConsumer materializa resultado    \# RES.116  
  → Orchestrator recibe via Redis Pub/Sub      \# retorno al ciclo  
\`\`\`

Integracion A2A (RES.113): delegacion via envelope con \`task\_type="mcp\_tool\_call"\`.  
Integracion SubQ (RES.114): tool calls largas delegadas a SubQDispatcher con prioridad "normal" o "low".  
Integracion Unikernel (RES.115): NO APLICA directamente. Aislamiento garantizado via \`tenant\_id\` en todos los namespaces.

\---

\#\# 5\. Estado final de la capa en V3\_01

Cambios respecto a V2:  
\- Tools hardcodeadas → servidores MCP 2.0 independientes (self-registration)  
\- Catalogo estatico → ToolRegistry dinamico con health en tiempo real  
\- Ejecucion sincrona bloqueante → MCPStreamingClient \+ MCPStreamConsumer  
\- Sin validacion de skills → SkillValidationPipeline con dry-run automatico

Componentes activos: MPATSkillServer, MCPStreamingClient, MCPStreamConsumer, ToolRegistry, ToolHealthMonitor, SkillValidationPipeline, SkillDryRunner.

\---

\#\# 6\. Flujo de datos completo

\`\`\`  
Agente (Capa 3\)  
  → ToolRegistry.search("sql\_query", top\_k=5)  
      → mpat:tools:registry:{tenant\_id} \[HASH lookup\]  
      → retorna lista con health status  
  → ToolRegistry.get\_tool("sql\_query", tenant\_id)  
      → verifica mpat:tools:health:sql\_query \[TTL check\]  
      → si expirado \= DOWN → fallback a tool alternativa  
      → si UP → continua  
  → MCPStreamingClient.call\_tool\_streaming("sql\_query", args)  
      → abre SSE connection al MCP server  
      → publica chunks en mpat:mcp:stream:{tool\_call\_id}  
      → Orchestrator retorna al ciclo (NO BLOQUEA)  
  → MCPStreamConsumer consume stream  
      → type=done → materializa en mpat:mcp:result:{tool\_call\_id}  
      → notifica via Redis Pub/Sub  
  → Orchestrator recibe resultado → continua plan  
  OTel span: mcp\_tool\_call\_complete  
  PolicyEnforcer (Capa 14\) → auditoria de cada tool call con tenant\_id  
\`\`\`

\---

\#\# 7\. Config files V3\_01

| Config file | Parametros clave | RES origen |  
|---|---|---|  
| config/mcp.yaml | stream\_maxlen, result\_ttl\_seconds, chunk\_timeout\_ms, max\_concurrent\_tools, streaming\_enabled | RES.116 |  
| config/tool\_registry.yaml | health\_ttl\_seconds, usage\_maxlen, schema\_version, max\_tools\_per\_tenant | RES.117 |  
| config/skill\_validation.yaml | dry\_run\_timeout\_ms, max\_steps, max\_pending\_per\_tenant | RES.118 |

\---

\#\# 8\. Puntos de atencion para implementacion

1\. INV-7-STREAM.1 es absoluto: chunks sin \`tool\` o \`type\` se descartan silenciosamente, nunca propagan error al usuario.  
2\. INV-7-REG.1 es gate de seguridad: top\_k \> 10 requiere aprobacion HITL. No omitir bajo presion de performance.  
3\. INV-7-VAL.1 \+ INV-7-VAL.2 son complementarios: no existe "ejecucion optimista". Un skill sin \`approved=True\` NO se ejecuta.  
4\. Aislamiento de tenant en TODOS los namespaces: cualquier operacion que no filtre por tenant\_id es un bug de seguridad.  
5\. ToolHealthMonitor debe tener watchdog propio — si el monitor cae, todos los tools aparecen DOWN en 60s.  
6\. Compatibilidad A2A \+ SubQ debe estar cubierta en tests de integracion.

\---

\#\# 9\. Datos faltantes o inconsistencias detectadas

1\. CAPA\_07\_MASTER no lista explicitamente RES.116/117/118 en su seccion de Resoluciones Aplicadas — se incorporaron desde RESOLUCIONES\_V3\_01.md como fuente autoritativa.  
2\. FUT-7-C (micropagos x402) y FUT-7-D (SEP-1865 MCP Apps) documentados como frontera sin RES formal.  
3\. Schema del Agent Card externo referenciado en ToolRegistry no completamente especificado — se asume compatible con JSON-LD de RES.113.  
4\. Configuracion de sandbox para Tier 2 (Docker/Wasm) sin parametros en config/skill\_validation.yaml. \[DATO FALTANTE\]

\---

\*INFORME\_CAPA\_07\_V3\_01\_cursos.agt.ia.md · AGT 2026 · cursos.agt.ia@gmail.com · 2026-05-14\*  
\*Generado en RELAY\_004b · autorizacion docente confirmada · cursos.agt.ia@gmail.com\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
