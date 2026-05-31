\---  
migrado\_desde: MPAT3/capas/CAPA\_04\_MASTER\_V3\_02.md  
id\_origen: 1GRkM9kr9NIOZ8zu1qSasNyYCGdgQ0cq3GJA7BS-hSJM  
autor\_migracion: mpat.andrea  
fecha\_migracion: 2026-05-23  
estado: MIGRADO\_ADAPTADO  
cambios: |  
  \- Encabezado de migracion agregado.  
  \- Terminologia V4 verificada: sin Docker, sin Pydantic V1/V2 obsoleto.  
  \- Modelos en InferenceProfile (qwen3:8b, phi4-mini) confirmados como vigentes V4.  
  \- Deuda tecnica heredada registrada (ver abajo).  
  \- Pendientes V4 de frontera\_capa4 conservados en seccion 8\.  
  \- Sin modificacion al contenido tecnico — calidad original 9.5/10.  
deuda\_heredada: |  
  \- PEND-04-V4-01: Feedback Loop RLHF Educativo — ajuste de prompts por calificacion de docentes \[ABIERTO → V4\]  
  \- PEND-04-V4-02: Audit Trail E2EE — logs de auditoria cifrados \[ABIERTO → V4\]  
  \- PEND-04-V4-03: Streaming de chunks de audio via WebSocket mientras LLM genera \[ABIERTO → V4\]  
  \- PEND-04-V4-04: RES.XXX-A/B/C (AgentCard Machine-Readable, Managed Agents, A2AHandoffManager) sin numerar formalmente \[ABIERTO → V4\]  
  \- NOTA: CognitiveScheduler en CAPA\_03 usa Python 3.13t No-GIL. AgentLifecycleManager en CAPA\_04 no tiene restriccion explicita — verificar si operaciones de spawn/destroy requieren No-GIL o son I/O bound (Redis). Si son CPU-bound: agregar INV-GIL equivalente.  
destino\_mpat4: core/cognition/agents/  
\---

\# CAPA\_04 — Agent Manager: Ciclo de Vida · AgentCard · InferenceProfile · HallucinationGuard  
\#\# Version: MASTER\_V3\_02 — Consolidado MPAT4  
\#\# Fuentes: CAPA\_04\_MASTER.md (V2\_04 \+ V2\_33 \+ V2\_46 \+ V2\_49) \+ Frontera Capa 4  
\#\# RES: RES.034 (InferenceProfile), RES.051 (ModelPolicy), RES.055 (HallucinationGuard)  
\#\# Autor consolidacion: ariel.garcia.traba@gmail.com · 2026-05-23  
\#\# Paradigma: IA Generativa y Agentica — Co-evolution Human-AI

\*que has usado el formato de razonamiento adaptado por AGT\*

\---

\#\# NOTA PEDAGOGICA DE APERTURA

Los agentes en MPAT son efimeros. Esta propiedad es contraintuitiva: en la mayoria de los  
sistemas, los componentes son persistentes — el servidor siempre esta corriendo. Los agentes  
en MPAT nacen, hacen su trabajo y mueren. Su memoria entre tareas no vive en el agente —  
vive en la memoria persistente (CAPA\_08).

Si un agente falla a mitad de una tarea, no hay estado corrupto que limpiar. Se destruye la  
instancia fallida y se crea una nueva desde el ultimo checkpoint. Como una hoja en blanco  
con memoria de lo que hizo antes.

Esto encarna el Co-evolution Human-AI: el sistema evoluciona su identidad (AgentCard) por  
versionado semantico, detecta sus propias alucinaciones (HallucinationGuard), y separa lo que  
sabe hacer (capabilities en AgentCard) de como infiere (InferenceProfile). Tres contratos  
ortogonales que nunca se mezclan.

\---

\#\# 1\. CICLO DE VIDA DEL AGENTE (V2\_04)

\`\`\`  
SPAWN  
  El Orchestrator (CAPA\_03) decide crear un agente para una tarea.  
  El Agent Manager instancia el agente con su configuracion.  
  |  
INIT  
  Condicion: identidad valida \+ budget \> 0\.  
  Captura snapshot de skill\_versions en ECS (P2.6).  
  Si es primera ejecucion: AgentCard publicado (estado PUBLISHED).  
  |  
PLAN  
  El agente calcula E(tarea) y define subtareas.  
  entropy\_initial registrado en ECS.  
  |  
EXECUTE  
  El agente ejecuta inferencia, llama MCP, delega via A2A si necesario.  
  Si hay TASK\_DELEGATE: Orchestrator captura snapshot del AgentCard receptor.  
  Orchestrator calcula ERR/RV/CI/MCS/PSC al finalizar cada fase.  
  |  
VERIFY  
  Orchestrator valida el resultado completo.  
  Verifica skill\_versions \+ agentcard\_snapshots activos.  
  \-\> NO valido: retry / fallback \-\> abort si excede limites  
  \-\> Valido: continua  
  |  
EMIT  
  Output transferido a CAPA\_13 con validated\_by\_orchestrator=True.  
  |  
SUSPEND  
  ECS completo persistido en Redis (checkpoint).  
  Incluye agentcard\_snapshots y campos de metricas cognitivas.  
  NOTA: SUSPEND no es solo "pausa" — es el momento donde el agente  
  se hace persistente. Si el worker falla despues de SUSPEND, el estado  
  esta en Redis y se puede recuperar. Si falla antes, se pierde desde el  
  ultimo checkpoint. Por eso los checkpoints son frecuentes.  
  |  
DESTROY  
  Budget no consumido retorna inmediatamente al agente padre.  
  Trace cerrado en OpenTelemetry (CAPA\_10).  
  Registro final en tabla cognitive\_metrics.  
  Si hubo AGENTCARD\_VERSION\_MISMATCH: entrada en historial del AgentCard.  
\`\`\`

\*\*Design-by-Contract: Agent Manager\*\*  
Precondicion SPAWN: Orchestrator decidio crear el agente. Budget asignado \> 0\.  
  AgentCard existe y esta en estado PUBLISHED.  
Postcondicion DESTROY: Budget no consumido retorno al padre. Trace OTel cerrado.  
  Registro en cognitive\_metrics completado. Mismatch de AgentCard registrado si ocurrio.  
Invariante: Un agente NUNCA tiene budget \> el que el Orchestrator le asigno.  
  AgentCard DRAFT NO es visible para discovery ni para delegaciones.

\---

\#\# 2\. AGENTCARD — SEMANTIC VERSIONING Y SNAPSHOT (V2\_04)

El AgentCard es el contrato de capacidades que un agente publica al sistema. Define exactamente  
que puede hacer, a que costo, con que nivel de confianza. Cuando el Orchestrator delega una  
tarea, lo hace basandose en este contrato.

\`\`\`typescript  
interface AgentCard {  
  // Identificacion  
  agent\_id: string;  
  agentcard\_version: string;  // formato: major.minor.patch  
  published\_at: string;       // ISO-8601

  // Capacidades declaradas  
  capabilities: string\[\];     // ej: \["pdf\_analysis", "legal\_reasoning"\]

  // Costo y confianza  
  cost\_per\_token\_usd: number;  
  trust\_level: "HIGH" | "MEDIUM" | "LOW";  
  max\_budget\_per\_task\_usd: number;

  // Protocolo A2A  
  a2a\_endpoint: string;  
  supported\_message\_types: string\[\];

  // Restricciones operativas  
  max\_concurrent\_delegations: number;  
  max\_delegation\_depth\_accepted: number;

  // InferenceProfile (RES.034)  
  inference\_profile\_id: string;  
  // Referencia al InferenceProfile en config\_policy.yaml.  
  // NUNCA debe contener el nombre del modelo directamente.  
}  
\`\`\`

\*\*Version semantica (major.minor.patch):\*\*

| Tipo | Ejemplo | Impacto en delegaciones activas |  
|---|---|---|  
| patch | 1.2.3 \-\> 1.2.4 | Ninguno — cambio interno |  
| minor | 1.2.x \-\> 1.3.0 | Verificacion — capabilities nuevas, viejas siguen |  
| major | 1.x.x \-\> 2.0.0 | CRITICO — capabilities modificadas o eliminadas |

Por que el major update es serio: si el Agente A delego al Agente B porque B declara  
"legal\_document\_analysis", y B se actualiza a major dividiendo esa capability en dos, sin  
deteccion de MAJOR el fallo es dificil de diagnosticar. Con la deteccion, el abort ocurre  
inmediatamente con mensaje explicito de que cambio y por que la delegacion ya no es valida.

\*\*Ciclo de vida del AgentCard:\*\*  
\- DRAFT: no visible para discovery ni delegaciones. En edicion por el Admin.  
\- PUBLISHED: version activa. El Orchestrator la usa para nuevas delegaciones.  
  Las delegaciones activas tienen su snapshot inmutable (no se ven afectadas).  
\- DEPRECATED: existe una version mas nueva. Solo para auditoria.

\*\*Regla de publicacion:\*\* el campo \`changes\` es OBLIGATORIO al publicar una nueva version.  
Un AgentCard sin descripcion del cambio no puede publicarse — igual que un commit sin mensaje.

\`\`\`typescript  
interface AgentCardHistoryEntry {  
  version: string;  
  published\_at: string;  
  published\_by: string;  
  changes: string;  // OBLIGATORIO  
  active\_delegations\_at\_publish: number;  
  capabilities\_added: string\[\];  
  capabilities\_removed: string\[\];  
  capabilities\_modified: string\[\];  
}  
\`\`\`

\---

\#\# 3\. INFERENCEPROFILE — SEPARACION DE CONTRATOS (RES.034 · BRECHA.10 CERRADO)

\#\#\# 3.1 Por que existe el InferenceProfile

El AgentCard define QUE puede hacer el agente (capabilities).  
El InferenceProfile define COMO infiere el agente (parametros de ejecucion).  
Son contratos ortogonales: cambiar el modelo no cambia las capabilities, y agregar una  
capability no cambia los parametros de inferencia.

La trampa educativa: creer que alcanza con poner el nombre del modelo en el AgentCard.  
La respuesta correcta: el modelo es solo uno de los parametros. El InferenceProfile tambien  
define temperatura, max\_tokens, timeout, fallback\_model, y si el agente puede usar  
disaggregation. Sin el perfil, dos agentes con el mismo modelo base producen resultados  
completamente distintos — y el sistema no puede auditar por que.

Analogia: el AgentCard es el CV de una persona (habilidades declaradas). El InferenceProfile  
es su contrato laboral (herramientas, tiempo por tarea, que hacer si la herramienta falla).  
El CV no cambia si le asignan un ecografo distinto al medico, pero el procedimiento si.

\#\#\# 3.2 Schema YAML del InferenceProfile (config\_policy.yaml)

\`\`\`yaml  
inference\_profiles:  
  default:  
    model\_id: "phi4-mini"  
    temperature: 0.7        \# \[0.0, 2.0\] — para razonamiento: 0.2-0.4  
    max\_tokens: 2048        \# \[1, 32768\] — limitado por el modelo  
    timeout\_ms: 30000       \# \[1000, 120000\] — si supera: fallback  
    fallback\_model\_id: ""   \# vacio \= sin fallback  
    disaggregation\_eligible: false  
    top\_p: 1.0              \# \[0.0, 1.0\]  
    frequency\_penalty: 0.0  \# \[-2.0, 2.0\]

  reasoning:  
    model\_id: "qwen3:8b"  
    temperature: 0.2  
    max\_tokens: 8192  
    timeout\_ms: 60000  
    fallback\_model\_id: "phi4-mini"  
    disaggregation\_eligible: true  
    top\_p: 0.9  
    frequency\_penalty: 0.1

  fast\_response:  
    model\_id: "phi4-mini"  
    temperature: 0.5  
    max\_tokens: 512  
    timeout\_ms: 5000  
    fallback\_model\_id: ""  
    disaggregation\_eligible: false  
    top\_p: 1.0  
    frequency\_penalty: 0.0  
\`\`\`

Por que hay 3 perfiles: \`default\` es el base para la mayoria de tareas. \`reasoning\` activa  
disaggregation y usa el modelo mas capaz — para analisis profundo donde el tiempo importa  
menos que la calidad. \`fast\_response\` minimiza latencia: modelo liviano, pocos tokens, sin  
fallback — si tarda mas de 5s, algo esta mal. La trampa es crear un perfil "universal".

\*\*Tabla de compatibilidad: InferenceProfile x disaggregation\*\*  
| disaggregation\_eligible | disaggregation.enabled (global) | Comportamiento |  
|---|---|---|  
| false | false | Pool unico. Sin disaggregation. |  
| false | true | Pool unico. El perfil sobreescribe la config global. |  
| true | false | Pool unico. La config global sobreescribe el perfil. |  
| true | true | Disaggregation activa. Routing segun routing\_strategy (RES.029). |

Un agente fast\_response con timeout\_ms=5000 no puede tolerar el overhead de disaggregation.  
Si el admin activa disaggregation globalmente, ese agente debe quedar excluido.  
disaggregation\_eligible=false en el perfil es ese mecanismo.

\#\#\# 3.3 InferenceProfileResolver — Design-by-Contract

\`\`\`python  
class InferenceProfileResolver:  
    """  
    Precondicion: agent\_card.inference\_profile\_id es string no vacio.  
      config contiene inference\_profiles con al menos "default".  
    Postcondicion: retorna InferenceProfile completo.  
      Si ID no existe: retorna "default" \+ WARNING. Nunca None.  
    Invariante: El Agent Manager NUNCA pasa model\_id directamente al Model Router.  
      Siempre pasa el InferenceProfile completo resuelto.  
    """  
    def resolve(self, profile\_id: str, config: dict) \-\> dict:  
        profiles \= config.get("inference\_profiles", {})  
        if profile\_id in profiles:  
            return profiles\[profile\_id\]  
        logging.warning(f"InferenceProfile '{profile\_id}' no encontrado. Usando 'default'.")  
        default \= profiles.get("default")  
        if default is None:  
            raise MPATFailure(code="CONFIG\_ERROR",  
                detail="inference\_profiles.default no existe en config\_policy.yaml")  
        return default  
\`\`\`

\*\*Invariante RES.034:\*\* Un agente NUNCA llama al Model Router con parametros directos de  
modelo. Siempre pasa inference\_profile\_id \-\> el Router resuelve el perfil \-\> ejecuta.  
Cambiar el modelo de todos los agentes de un tenant se hace en un solo lugar (config\_policy.yaml).

\---

\#\# 4\. MODELPOLICY — FALLBACK POR VRAM Y LATENCIA (RES.051)

\`\`\`python  
@dataclass  
class ModelPolicy:  
    primary: str \= "qwen3:8b"  
    fallback\_l1: str \= "phi-4-mini"  
    fallback\_l2: str \= "mistral:7b-v0.3"  
    fallback\_trigger\_vram\_gb: float \= 8.0  
    fallback\_trigger\_latency\_ms: int \= 2000

def select\_model(policy: ModelPolicy, available\_vram\_gb: float) \-\> str:  
    """VRAM decidido ANTES de llamar al modelo."""  
    if available\_vram\_gb \< policy.fallback\_trigger\_vram\_gb:  
        return policy.fallback\_l1  
    return policy.primary

def on\_latency\_exceeded(policy: ModelPolicy, elapsed\_ms: int) \-\> str:  
    """Latencia detectada DURANTE la llamada."""  
    if elapsed\_ms \> policy.fallback\_trigger\_latency\_ms:  
        return policy.fallback\_l1  
    return policy.primary  
\`\`\`

Trampa educativa: "si el modelo falla, usar el siguiente de la lista". Respuesta correcta:  
hay dos criterios de fallback ORTOGONALES — VRAM (decidido antes de llamar al modelo) y  
latencia (detectado durante la llamada). Mezclarlos en un solo if produce bugs silenciosos  
donde el fallback L1 activa el L2 por latencia aunque VRAM sea suficiente. Las dos funciones  
separadas hacen explicito que criterio acciono el fallback.

\*\*Parametros en config\_policy.yaml:\*\*  
\`\`\`yaml  
models:  
  primary: "qwen3:8b"          \# MMLU: 83.1% · VRAM: 8.5GB · Tokens/s: 118  
  fallback\_l1: "phi-4-mini"    \# MMLU: 78.3% · VRAM: 6.2GB · Tokens/s: 145  
  fallback\_l2: "mistral:7b-v0.3"  \# VRAM: 7.2GB · legacy  
  fallback\_trigger\_vram\_gb: 8.0   \# \[4.0, 16.0\]  
  fallback\_trigger\_latency\_ms: 2000  \# \[500, 10000\]  
benchmark\_reference: "lm-sys/chatbot-arena-2026-Q1"  
\# qwen3.5:9b descartado: \+1.3GB VRAM sin ganancia operativa suficiente  
\`\`\`

\---

\#\# 5\. HALLUCINATIONGUARD — AUTOCORRECCION TRANSPARENTE (RES.055 · FUT.19 CERRADO)

\#\#\# 5.1 Por que existe separado del Critic

El Critic (CAPA\_09) evalua RAZONAMIENTO: coherencia interna del razonamiento del agente.  
El HallucinationGuard evalua FACTUALIDAD: consistencia externa con la fuente de verdad.  
Un agente puede razonar perfectamente bien sobre un dato inventado.  
Son dos controles ortogonales — ninguno reemplaza al otro.

La trampa educativa: "no es lo mismo que el Critic?". La respuesta incorrecta: "si, el Critic  
ya evalua la calidad". La respuesta correcta: son controles distintos sobre dimensiones  
distintas. El Critic mide coherencia del plan; el HallucinationGuard mide veracidad del dato.

\#\#\# 5.2 Tipos de senal

\`\`\`python  
class HallucinationType(str, Enum):  
    DATE\_INCONSISTENCY \= "DATE\_INCONSISTENCY"    \# fecha fuera de rango razonable  
    NUMERIC\_OUTLIER \= "NUMERIC\_OUTLIER"          \# numero estadisticamente imposible  
    ENTITY\_NOT\_IN\_CONTEXT \= "ENTITY\_NOT\_IN\_CONTEXT"  \# entidad no mencionada antes  
    SELF\_CONTRADICTION \= "SELF\_CONTRADICTION"    \# agente contradice trace anterior  
    CONFIDENCE\_COLLAPSE \= "CONFIDENCE\_COLLAPSE"  \# confidence cayo \>0.4 en un paso  
\`\`\`

Severidad \[0.0-1.0\]: \<0.4 loggear sin interrumpir. 0.4-0.7 re-prompt suave. \>0.7 re-prompt  
directo \+ registrar en ECS.

\#\#\# 5.3 Re-prompt loop — transparente para el usuario

\`\`\`python  
async def run\_with\_hallucination\_guard(agent, initial\_prompt, ecs, guard, model\_router, config):  
    """  
    Precondicion: agent inicializado, ecs con logic\_trace disponible.  
    Postcondicion: resultado paso el guard O se agotaron los intentos.  
      Si se agotaron: retorna con warning en ECS (nunca cancela la tarea).  
    Invariante INV\_HALLGUARD\_2: el usuario NUNCA ve los re-prompts intermedios.  
    """  
    max\_attempts \= config.get("agent.hallucination\_max\_reprompt\_attempts", 2\)  
    result\_text \= await agent.generate(initial\_prompt, model\_router)

    for attempt in range(max\_attempts):  
        is\_clean, signals \= guard.analyze(result\_text, ecs)  
        if is\_clean:  
            break  
        reprompt \= build\_reprompt(signals, result\_text)  
        ecs.logic\_trace.append({  
            "step": f"HALLUCINATION\_REPROMPT\_attempt\_{attempt+1}",  
            "action": "hallucination\_correction",  
            "reasoning": str(\[s.hallucination\_type for s in signals\]),  
        })  
        result\_text \= await agent.generate(reprompt, model\_router)  
    else:  
        \# Agotados los intentos — dejar pasar con warning (INV\_HALLGUARD\_1)  
        ecs.hallucination\_warning \= True

    return result\_text  
\`\`\`

Invariante INV\_HALLGUARD\_1: el HallucinationGuard NO cancela la tarea — solo solicita  
  revision. Despues de max\_reprompt\_attempts, deja pasar con warning en ECS.  
Invariante INV\_HALLGUARD\_2: el usuario NUNCA ve el re-prompt ni la senal. Transparente.

\#\#\# 5.4 Campo ECS nuevo y parametros config\_policy.yaml

\`\`\`python  
hallucination\_warning: bool \= False  
\# True si el Guard agoto los intentos sin limpiar las senales.  
\# CAPA\_13 puede usar este campo para agregar nota de advertencia.  
\`\`\`

\`\`\`yaml  
agent:  
  hallucination\_guard\_enabled: true  
  hallucination\_severity\_threshold: 0.4   \# \[0.1, 0.9\]  
  hallucination\_max\_reprompt\_attempts: 2  \# \[1, 5\] — 2 es el equilibrio recomendado  
\`\`\`

\---

\#\# 6\. NAMESPACES REDIS — CAPA\_04

| Namespace | TTL | Tipo | Descripcion |  
|---|---|---|---|  
| mpat:agent:{tenant\_id}:{agent\_id}:state | session | String(enum) | Estado del ciclo de vida |  
| mpat:agent:{tenant\_id}:{agent\_id}:ecs | session | Hash | ECS del agente |  
| mpat:agent:{tenant\_id}:{agent\_id}:agentcard | permanente | Hash | AgentCard PUBLISHED |  
| mpat:agent:{tenant\_id}:{agent\_id}:agentcard:history | permanente | List\[JSON\] | Historial de versiones |  
| mpat:agent:{tenant\_id}:{agent\_id}:checkpoint | session | Hash | Ultimo checkpoint SUSPEND |  
| mpat:cognitive\_metrics:{tenant\_id}:{agent\_id} | 86400s | Hash | Metricas de sesion |

\---

\#\# 7\. INVARIANTES CRITICOS

| ID | Invariante | Nivel |  
|----|-----------|-------|  
| INV-04-BUDGET | Un agente NUNCA tiene budget \> el asignado por el Orchestrator. | CRITICO |  
| INV-04-AGENTCARD-DRAFT | AgentCard en DRAFT no es visible para discovery ni delegaciones. | CRITICO |  
| INV-04-AGENTCARD-CHANGES | Campo changes OBLIGATORIO al publicar nueva version. | ALTO |  
| INV-RES034 | Agent Manager NUNCA pasa model\_id directamente al Model Router. | CRITICO |  
| INV\_HALLGUARD\_1 | HallucinationGuard NO cancela la tarea — deja pasar con warning tras max\_attempts. | ALTO |  
| INV\_HALLGUARD\_2 | El usuario NUNCA ve los re-prompts intermedios. La correccion es transparente. | CRITICO |

\---

\#\# 8\. DEUDA TECNICA AL CIERRE V3\_02 Y PENDIENTES V4

| DT | Descripcion | Estado |  
|----|-------------|--------|  
| FUT.19 | HallucinationGuard | CERRADO (RES.055) |  
| BRECHA.10 | InferenceProfile schema | CERRADO (RES.034) |  
| M.5 | ModelPolicy fallback qwen3:8b | CERRADO (RES.051) |  
| PEND-04-V4-01 | Feedback Loop RLHF Educativo | ABIERTO → V4 |  
| PEND-04-V4-02 | Audit Trail E2EE | ABIERTO → V4 |  
| PEND-04-V4-03 | Streaming chunks audio via WebSocket | ABIERTO → V4 |  
| PEND-04-V4-04 | RES.XXX-A/B/C formalizacion | ABIERTO → V4 |

\---

\*CAPA\_04\_MASTER\_V4\_migrado.md · MPAT4 · mpat.andrea · 2026-05-23\*  
\*Consolida: V2\_04 (base) \+ V2\_33 (RES.034) \+ V2\_46 (RES.051) \+ V2\_49 (RES.055) \+ Frontera\*  
\*Migrado desde: ariel.garcia.traba@gmail.com · CAPA\_04\_MASTER\_V3\_02.md\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
