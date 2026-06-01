\# INVESTIGACION\_FUT19\_HALLUCINATION\_GUARD\_V3\_01.md  
\#\# MPAT — FUT.19 · HallucinationGuard · Feedback Loop \+ Auto-corrección de alucinaciones  
\#\# Autor: ariel.garcia.traba@gmail.com · RELAY\_005 · 2026-05-12  
\#\# RES efectiva: RES.055 (implementada en CAPA\_04 V2\_49)

\*que has usado el formato de razonamiento adaptado por AGT\*

\---

\#\# IDENTIFICACION DEL GAP

| Campo | Valor |  
|---|---|  
| FUT | FUT.19 |  
| Descripcion original | Feedback Loop \+ auto-corrección alucinaciones |  
| Capa asignada | Capa 4 |  
| RES catalogo | RES.070 |  
| RES real implementada | RES.055 (CAPA\_04 V2\_49) |  
| Estado anterior | PARCIAL — HallucinationGuard implementado en CAPA\_04 pero FUT.19 original sin RES formal en catalogo |  
| Estado post-RELAY\_005 | CERRADO — investigacion formal generada \+ colision RES documentada |

\---

\#\# CONTEXTO ARQUITECTURAL

FUT.19 fue concebido como un mecanismo de deteccion y corrección automatica de  
alucinaciones del LLM en tiempo de inferencia. Su implementacion se materializo  
en CAPA\_04 (Motor de Agentes) como el componente \`HallucinationGuard\`.

La implementacion fue registrada en el historial de CAPA\_04:

\`\`\`  
V2\_49 (RES.055) | FUT.19 CERRADO — §4.6 HallucinationGuard.  
                   5 tipos de señal, re-prompt loop transparente,  
                   campo ECS hallucination\_warning, 3 parámetros Capa 14\.  
\`\`\`

La colision ocurrio porque el catalogo asigno RES.070 al FUT.19, pero la  
implementacion real ocupo RES.055 (que en el catálogo estaba sin asignar a este FUT).

\---

\#\# DECISION TECNICA — RES.055

| Campo | Valor |  
|---|---|  
| Item cerrado | FUT.19 |  
| Version | CAPA\_04 V2\_49 |  
| Seccion | §4.6 HallucinationGuard |  
| Decision | Deteccion de alucinaciones en 5 categorias de señal. Re-prompt loop transparente para el usuario. Campo ECS dedicado. 3 parametros configurables en Capa 14\. |  
| Capa afectada | Capa 4 — Motor de Agentes |

\---

\#\# LOS 5 TIPOS DE SEÑAL DE ALUCINACION

HallucinationGuard detecta alucinaciones mediante 5 categorias de señal:

\#\#\# Señal 1 — Contradiccion factual con ECS  
El agente afirma algo que contradice datos estructurados presentes en el  
Entity-Component System. La contradiccion se detecta comparando entidades  
nombradas en la respuesta contra el estado validado en ECS.

\`\`\`python  
\# Ejemplo: agente afirma "el presupuesto restante es $50"  
\# pero ECS.budget\_remaining \= 30.00  
\# → HALLUCINATION\_TYPE: FACTUAL\_CONTRADICTION  
\`\`\`

\#\#\# Señal 2 — Referencia a herramienta inexistente  
El agente menciona o intenta invocar una herramienta (MCP tool, skill) que  
no figura en el Tool Registry activo de la sesion.

\`\`\`python  
\# Ejemplo: agente invoca "search\_database\_v3"  
\# pero Tool Registry activo no contiene ese tool\_name  
\# → HALLUCINATION\_TYPE: TOOL\_REFERENCE\_ERROR  
\`\`\`

\#\#\# Señal 3 — Identidad del agente incorrecta  
El agente hace afirmaciones sobre sus propias capacidades que no coinciden  
con su AgentCard publicado (capabilities\[\], trust\_level, max\_budget).

\`\`\`python  
\# Ejemplo: agente afirma "puedo acceder a internet en tiempo real"  
\# pero AgentCard.capabilities no incluye "web\_search"  
\# → HALLUCINATION\_TYPE: IDENTITY\_MISMATCH  
\`\`\`

\#\#\# Señal 4 — Inconsistencia temporal  
El agente mezcla informacion de sesiones distintas o hace referencias  
temporales imposibles dada la historia del ECS (ej: "como dijiste antes"  
cuando no hay historial de esa afirmacion).

\`\`\`python  
\# → HALLUCINATION\_TYPE: TEMPORAL\_INCONSISTENCY  
\`\`\`

\#\#\# Señal 5 — Confianza de inferencia baja con afirmacion de alta certeza  
La metrica interna de confianza del LLM (cuando disponible) indica  
incertidumbre alta mientras la respuesta usa lenguaje de certeza absoluta.

\`\`\`python  
\# Ejemplo: modelo con confidence\_score \< 0.4  
\# mientras genera "El resultado exacto es 42"  
\# → HALLUCINATION\_TYPE: CONFIDENCE\_MISMATCH  
\`\`\`

\---

\#\# RE-PROMPT LOOP TRANSPARENTE

Cuando se detecta una alucinacion, HallucinationGuard no falla la tarea  
directamente. Ejecuta un loop de re-prompt transparente para el usuario:

\`\`\`  
DETECT → clasificar señal → construir re-prompt correctivo  
       → re-inferencia con contexto corregido  
       → re-validar → si pasa: emitir respuesta corregida  
                    → si falla (N intentos): HALLUCINATION\_ABORT  
\`\`\`

\`\`\`python  
class HallucinationGuard:  
    """  
    Detector y corrector de alucinaciones del agente en tiempo de inferencia.

    RES: RES.055  
    Capa: 4 — Motor de Agentes  
    Posicion en pipeline: post-inferencia, pre-EMIT

    Precondicion: respuesta de inferencia disponible \+ ECS actual accesible  
    Postcondicion: respuesta validada o HALLUCINATION\_ABORT emitido  
    INV-HG.1: el re-prompt loop no supera hallucination.max\_retries  
    INV-HG.2: el usuario nunca recibe una respuesta con señal activa confirmada  
    INV-HG.3: cada hallucination detectado se registra en ECS.hallucination\_warning  
    """

    SIGNAL\_TYPES \= \[  
        "FACTUAL\_CONTRADICTION",  
        "TOOL\_REFERENCE\_ERROR",  
        "IDENTITY\_MISMATCH",  
        "TEMPORAL\_INCONSISTENCY",  
        "CONFIDENCE\_MISMATCH",  
    \]

    def \_\_init\_\_(self, config: dict, ecs\_client, tool\_registry, agentcard):  
        self.config \= config  
        self.ecs \= ecs\_client  
        self.registry \= tool\_registry  
        self.agentcard \= agentcard  
        self.max\_retries \= config.get("hallucination.max\_retries", 2\)  
        self.enabled \= config.get("hallucination.enabled", True)

    async def validate(self, response: str, context: dict) \-\> dict:  
        """  
        Valida una respuesta de inferencia.  
        Retorna: {"valid": bool, "signal": str|None, "corrected\_response": str|None}  
        """  
        if not self.enabled:  
            return {"valid": True, "signal": None, "corrected\_response": None}

        signal \= await self.\_detect(response, context)  
        if signal is None:  
            return {"valid": True, "signal": None, "corrected\_response": None}

        \# Registrar en ECS antes del re-prompt  
        await self.ecs.set\_field(  
            context\["task\_id"\],  
            "hallucination\_warning",  
            {"signal": signal, "attempt": context.get("retry\_count", 0)}  
        )

        corrected \= await self.\_reprompt(response, signal, context)  
        return {  
            "valid": corrected is not None,  
            "signal": signal,  
            "corrected\_response": corrected  
        }

    async def \_detect(self, response: str, context: dict) \-\> str | None:  
        """Detecta el primer tipo de señal activa. Retorna None si no hay alucinacion."""  
        ...

    async def \_reprompt(self, original: str, signal: str, context: dict) \-\> str | None:  
        """  
        Ejecuta re-prompt loop correctivo.  
        Retorna respuesta corregida o None si supera max\_retries.  
        """  
        ...  
\`\`\`

\---

\#\# CAMPO ECS — hallucination\_warning

Cuando se detecta una alucinacion, el ECS del task recibe el campo:

\`\`\`python  
ecs\["hallucination\_warning"\] \= {  
    "signal": "FACTUAL\_CONTRADICTION",    \# tipo de señal detectada  
    "attempt": 1,                          \# numero de intento de re-prompt  
    "timestamp": 1715000000.0,             \# cuando fue detectada  
    "resolved": True                       \# True si el re-prompt tuvo exito  
}  
\`\`\`

Este campo queda disponible para:  
\- Audit Trail (FUT.22) — registro de incidentes de alucinacion  
\- RLHF on-the-fly (FUT.25) — señal de feedback negativo automatico  
\- OpenTelemetry (FUT.20) — span de alucinacion para trazabilidad

\---

\#\# PARAMETROS CAPA 14

\`\`\`yaml  
hallucination:  
  enabled: true                      \# habilita/deshabilita el guard  
  max\_retries: 2                     \# intentos de re-prompt antes de ABORT \[1, 5\]  
  confidence\_threshold: 0.4          \# umbral para señal CONFIDENCE\_MISMATCH \[0.1, 0.9\]  
\`\`\`

\---

\#\# INTEGRACION CON OTROS COMPONENTES

| Componente | Relacion | RES |  
|---|---|---|  
| ECS (Entity-Component System) | Campo hallucination\_warning | — |  
| Tool Registry (FUT\_3) | Verificacion de tool\_reference | RES.117 |  
| AgentCard (FUT\_3 / A2A) | Verificacion de identity claims | RES.113 |  
| RLHF on-the-fly (FUT.25) | Usa hallucination\_warning como feedback negativo | RES.076 |  
| Audit Trail (FUT.22) | Logging de incidentes | RES.090 |  
| OpenTelemetry (FUT.20) | Spans de deteccion | RES.030 |  
| FUT.33 — Metrica de Alucinacion | Agregacion estadistica de hallucination\_warning | pendiente RELAY\_005 |

\---

\#\# RELACION CON FUT.33

FUT.33 (Metrica de Alucinacion \+ Predictive Maintenance) es la capa analitica  
sobre FUT.19. Mientras HallucinationGuard opera en tiempo real por tarea,  
FUT.33 agrega las metricas historicas para deteccion de patrones y mantenimiento  
predictivo del sistema.

FUT.33 es un GAP separado — sin implementacion confirmada. Ver REPORTE\_GAPS\_FUT\_V3\_01.

\---

\#\# ESTADO Y CONCLUSION

FUT.19 fue implementado en CAPA\_04 V2\_49 como \`HallucinationGuard\` (RES.055).  
La implementacion es funcional y completa en 5 tipos de señal, re-prompt loop,  
campo ECS y 3 parametros de configuracion.

La ausencia de investigacion formal en el catalogo se debia a una colision de  
numeracion: el catalogo asigno RES.070 al FUT.19 pero la implementacion real  
quedo registrada bajo RES.055.

\*\*FUT.19 → CERRADO · RES.055 · RELAY\_005 · 2026-05-12\*\*

\---

\#\# COLISION DE NUMERACION DETECTADA

| Campo | Valor |  
|---|---|  
| RES catalogo para FUT.19 | RES.070 |  
| RES real implementada | RES.055 |  
| Resolucion | RES.055 es la canonica. Ver MAPA\_RES\_CANONICO\_V3\_01.md |

\---

\*INVESTIGACION\_FUT19\_HALLUCINATION\_GUARD\_V3\_01.md · RELAY\_005 · ariel.garcia.traba@gmail.com · 2026-05-12\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
