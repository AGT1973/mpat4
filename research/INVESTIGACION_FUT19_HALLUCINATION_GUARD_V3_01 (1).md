\# INVESTIGACION\_FUT19\_HALLUCINATION\_GUARD\_V3\_01.md  
\#\# MPAT — FUT.19: Feedback Loop \+ HallucinationGuard  
\#\# Generado por: cursos.au.agt@gmail.com · 2026-05-12  
\#\# RELAY\_005 — Investigaciones · RES propuesta: RES.124

\---

\#\# ESTADO PREVIO

| Campo             | Valor                                             |  
|-------------------|---------------------------------------------------|  
| FUT original      | FUT.19                                            |  
| Capa              | 4 — Motor de Agentes (Agent Manager)              |  
| Descripción FUT   | Feedback Loop \+ auto-corrección de alucinaciones  |  
| Implementado en   | CAPA\_04\_MASTER\_V3\_01.md §4.6 (desde V2\_49)       |  
| RES en catálogo   | Sin RES numerada propia — colisión con RES.055    |  
| RES propuesta     | \*\*RES.124\*\*                                       |  
| Estado            | PARCIAL → CERRADO con este documento              |

\---

\#\# 1\. PROBLEMA QUE RESUELVE

Los modelos de lenguaje generan respuestas que pueden contener:  
\- Fechas o datos numéricos incorrectos ("alucinaciones factuales")  
\- Entidades no presentes en el contexto de la conversación ("entidades inventadas")  
\- Contradicciones internas dentro de una misma respuesta  
\- Colapso de confianza: el modelo responde con alta certeza sobre algo que debería dudar

En un sistema educativo como MPAT, entregar estas respuestas al alumno sin filtro tiene  
consecuencias graves: aprende contenido incorrecto y pierde confianza en el sistema.

\*\*El problema central:\*\* ¿cómo detectar y corregir alucinaciones antes de que el alumno  
las vea, sin interrumpir la experiencia ni revelar que el sistema se autocorrigió?

\---

\#\# 2\. DECISIÓN ARQUITECTURAL

\*\*Decisión:\*\* implementar un HallucinationGuard como capa de verificación post-inferencia,  
transparente al usuario, que opera en el ciclo EXECUTE → VERIFY del agente (§4 ciclo de vida).

\*\*Alternativas descartadas:\*\*  
\- Filtrar en Capa 13 (Delivery): demasiado tarde — el agente ya emitió el output.  
\- Validar antes de inferencia: no es posible — no se conoce el output antes de generarlo.  
\- Rechazar output y generar error al usuario: rompe la experiencia educativa.

\*\*Elección:\*\* re-prompt transparente. Si se detecta una señal, el agente regenera  
su respuesta internamente con instrucciones adicionales. El alumno nunca lo sabe.

\---

\#\# 3\. IMPLEMENTACIÓN — 5 TIPOS DE SEÑAL

El HallucinationGuard detecta 5 tipos de señal sobre el output del agente:

| Señal                     | Descripción                                                        | Ejemplo                                      |  
|---------------------------|--------------------------------------------------------------------|----------------------------------------------|  
| DATE\_INCONSISTENCY        | Fechas que contradicen el contexto o son físicamente imposibles    | "En 2031 Einstein publicó su teoría..."     |  
| NUMERIC\_OUTLIER           | Valores numéricos estadísticamente anómalos dado el contexto       | "La suma de 2+2 es 5 en este caso..."       |  
| ENTITY\_NOT\_IN\_CONTEXT     | Personas, lugares o conceptos mencionados sin base en el contexto  | Citar un autor que no figura en la pregunta |  
| SELF\_CONTRADICTION        | Dos afirmaciones en la misma respuesta que se contradicen          | "X es siempre verdadero. En este caso X es falso." |  
| CONFIDENCE\_COLLAPSE       | Alta certeza expresada en dominio de alta incertidumbre            | Responder con absoluta certeza sobre predicciones futuras |

\---

\#\# 4\. FLUJO DE OPERACIÓN

\`\`\`  
Agente genera output  
        ↓  
HallucinationGuard.analyze(output, contexto)  
        ↓  
    ¿Señal detectada?  
   /              \\  
  NO              SÍ  
  ↓               ↓  
Emitir         severity \>= threshold?  
output         /              \\  
normal        NO              SÍ  
              ↓               ↓  
         Registrar        re-prompt interno  
         warning          (transparente)  
         en ECS           ↓  
                      ¿Intentos \< max\_reprompmt\_attempts?  
                         /              \\  
                        SÍ              NO  
                        ↓               ↓  
                   Re-generar      Emitir con  
                   respuesta       hallucination\_warning  
                   (loop)          en ECS \+ severity  
\`\`\`

\---

\#\# 5\. CÓDIGO DE REFERENCIA

\`\`\`python  
\# agent\_manager/hallucination\_guard.py — V2\_49 (formalizado en RES.124)

from dataclasses import dataclass, field  
from enum import Enum  
from typing import Optional  
import re

class HallucinationSignal(Enum):  
    DATE\_INCONSISTENCY \= "DATE\_INCONSISTENCY"  
    NUMERIC\_OUTLIER \= "NUMERIC\_OUTLIER"  
    ENTITY\_NOT\_IN\_CONTEXT \= "ENTITY\_NOT\_IN\_CONTEXT"  
    SELF\_CONTRADICTION \= "SELF\_CONTRADICTION"  
    CONFIDENCE\_COLLAPSE \= "CONFIDENCE\_COLLAPSE"

@dataclass  
class HallucinationAnalysis:  
    has\_signal: bool  
    signal\_type: Optional\[HallucinationSignal\]  
    severity: float  \# 0.0 \- 1.0  
    detail: str

class HallucinationGuard:  
    """  
    Analiza output del agente antes de emitirlo.

    Precondición (analyze): output es string no vacío, contexto disponible.  
    Postcondición (analyze): retorna HallucinationAnalysis con has\_signal y severity.

    Invariante (INV\_HALLGUARD\_1):  
    No cancela la tarea. Después de max\_reprompmt\_attempts, deja pasar con warning.

    Invariante (INV\_HALLGUARD\_2):  
    El usuario NUNCA ve el re-prompt ni la señal.  
    La corrección es completamente transparente.  
    """

    def \_\_init\_\_(self, config: dict):  
        self.enabled \= config.get("agent.hallucination\_guard\_enabled", True)  
        self.threshold \= config.get("agent.hallucination\_severity\_threshold", 0.4)  
        self.max\_attempts \= config.get("agent.hallucination\_max\_reprompmt\_attempts", 2\)

    def analyze(self, output: str, context: dict) \-\> HallucinationAnalysis:  
        """  
        Analiza el output del agente buscando señales de alucinación.  
        Retorna análisis con tipo de señal y severidad estimada.  
        """  
        if not self.enabled:  
            return HallucinationAnalysis(  
                has\_signal=False, signal\_type=None, severity=0.0, detail="guard\_disabled"  
            )

        \# Verificar cada tipo de señal (orden por impacto)  
        checks \= \[  
            self.\_check\_self\_contradiction(output),  
            self.\_check\_date\_inconsistency(output, context),  
            self.\_check\_entity\_not\_in\_context(output, context),  
            self.\_check\_numeric\_outlier(output, context),  
            self.\_check\_confidence\_collapse(output),  
        \]

        \# Retornar la señal de mayor severidad detectada  
        detected \= \[c for c in checks if c.has\_signal\]  
        if not detected:  
            return HallucinationAnalysis(  
                has\_signal=False, signal\_type=None, severity=0.0, detail="clean"  
            )

        return max(detected, key=lambda x: x.severity)

    def \_check\_self\_contradiction(self, output: str) \-\> HallucinationAnalysis:  
        """  
        Detecta patrones de autocontradicción en el texto.  
        Heurística: busca afirmaciones negadas en la misma respuesta.  
        """  
        \# Ejemplo simplificado de heurística — producción usaría NLI model  
        contradiction\_patterns \= \[  
            (r'\\bsiempre\\b.\*\\bnunca\\b', 0.7),  
            (r'\\bes verdad\\b.\*\\bes falso\\b', 0.8),  
            (r'\\bimpossible\\b.\*\\bes posible\\b', 0.6),  
        \]  
        for pattern, severity in contradiction\_patterns:  
            if re.search(pattern, output.lower()):  
                return HallucinationAnalysis(  
                    has\_signal=True,  
                    signal\_type=HallucinationSignal.SELF\_CONTRADICTION,  
                    severity=severity,  
                    detail=f"Patrón de contradicción detectado: {pattern}"  
                )  
        return HallucinationAnalysis(  
            has\_signal=False, signal\_type=None, severity=0.0, detail=""  
        )

    def \_check\_confidence\_collapse(self, output: str) \-\> HallucinationAnalysis:  
        """  
        Detecta alta certeza expresada sobre predicciones o dominios inciertos.  
        """  
        high\_certainty\_on\_uncertain \= \[  
            (r'\\bciertamente\\b.\*\\b(futuro|predicción|va a)\\b', 0.5),  
            (r'\\bsin duda\\b.\*\\b(siempre|nunca|todos)\\b', 0.6),  
        \]  
        for pattern, severity in high\_certainty\_on\_uncertain:  
            if re.search(pattern, output.lower()):  
                return HallucinationAnalysis(  
                    has\_signal=True,  
                    signal\_type=HallucinationSignal.CONFIDENCE\_COLLAPSE,  
                    severity=severity,  
                    detail=f"Certeza excesiva detectada: {pattern}"  
                )  
        return HallucinationAnalysis(  
            has\_signal=False, signal\_type=None, severity=0.0, detail=""  
        )

    def \_check\_date\_inconsistency(self, output: str, context: dict) \-\> HallucinationAnalysis:  
        """Placeholder — implementación completa requiere NLP de fechas."""  
        return HallucinationAnalysis(has\_signal=False, signal\_type=None, severity=0.0, detail="")

    def \_check\_entity\_not\_in\_context(self, output: str, context: dict) \-\> HallucinationAnalysis:  
        """Placeholder — implementación completa requiere NER \+ comparación con contexto."""  
        return HallucinationAnalysis(has\_signal=False, signal\_type=None, severity=0.0, detail="")

    def \_check\_numeric\_outlier(self, output: str, context: dict) \-\> HallucinationAnalysis:  
        """Placeholder — implementación completa requiere extracción numérica \+ estadísticas."""  
        return HallucinationAnalysis(has\_signal=False, signal\_type=None, severity=0.0, detail="")  
\`\`\`

\---

\#\# 6\. INTEGRACIÓN CON ECS

Cuando HallucinationGuard detecta una señal que supera el umbral  
(después de agotar intentos de re-prompt), registra en el ECS:

\`\`\`python  
\# Campo en ECS (Estado Cognitivo de Sesión)  
ecs\_update \= {  
    "hallucination\_warning": {  
        "detected": True,  
        "signal\_type": analysis.signal\_type.value,  
        "severity": analysis.severity,  
        "reprompmt\_attempts": attempts\_used,  
        "detail": analysis.detail,  
        "timestamp\_utc": datetime.now(timezone.utc).isoformat()  
    }  
}  
\`\`\`

Este campo es accesible para:  
\- CAPA\_10 (Monitoring): tracing y alertas de calidad  
\- CAPA\_06 (ECS): ajuste del RLHF on-the-fly basado en frecuencia de warnings  
\- CAPA\_14 (Config): parámetros ajustables en \`config\_policy.yaml\`

\---

\#\# 7\. PARÁMETROS CONFIGURABLES (config\_policy.yaml)

\`\`\`yaml  
agent:  
  hallucination\_guard\_enabled: true  
  \# Habilita/deshabilita el guard. Default: true.  
  \# Solo deshabilitar en entornos de testing controlado.

  hallucination\_severity\_threshold: 0.4  
  \# Severidad mínima para activar re-prompt.  
  \# Rango: \[0.0, 1.0\]. Default: 0.4.  
  \# Valores más bajos \= más sensible \= más re-prompts.

  hallucination\_max\_reprompmt\_attempts: 2  
  \# Intentos máximos de re-prompt antes de emitir con warning.  
  \# Rango: \[1, 5\]. Default: 2\.  
  \# Aumentar en dominios de alta precisión (medicina, derecho).  
\`\`\`

\---

\#\# 8\. RESOLUCIÓN FORMAL — RES.124

\*\*RES.124 — HallucinationGuard: detección y corrección transparente de alucinaciones\*\*

\*\*Problema:\*\* los agentes pueden generar outputs con alucinaciones factuales, contradicciones  
o entidades inventadas. Sin detección activa, estos llegan al alumno como respuesta definitiva.

\*\*Decisión:\*\* implementar HallucinationGuard como paso obligatorio en la fase VERIFY  
del ciclo de vida del agente (CAPA\_04). Opera post-inferencia, es transparente al usuario,  
y usa re-prompt interno antes de emitir con warning.

\*\*Alcance:\*\* todos los agentes del sistema. Configurable por perfil en \`config\_policy.yaml\`.

\*\*Impacto:\*\* CAPA\_04 (implementación), CAPA\_06 (RLHF feedback), CAPA\_10 (trazabilidad),  
CAPA\_14 (parámetros).

\*\*Invariantes críticos:\*\*  
\- INV\_HALLGUARD\_1: nunca cancela la tarea — solo advierte después de max\_attempts.  
\- INV\_HALLGUARD\_2: el usuario nunca ve el re-prompt — la corrección es invisible.

\*\*RES asignada:\*\* RES.124 (nueva — no colisiona con ningún RES existente).

\---

\#\# 9\. RELACIÓN CON OTRAS RESOLUCIONES

| RES      | Relación                                                             |  
|----------|----------------------------------------------------------------------|  
| RES.055  | RES anterior asignada a esta misma área en V2\_49. RES.124 la complementa formalmente. |  
| RES.121  | FUT.33 Métrica de Alucinación — pendiente de investigación propia. RES.121 extenderá RES.124. |  
| RES.076  | RLHF on-the-fly (CAPA\_06) consume \`hallucination\_warning\` del ECS para ajustar el modelo. |  
| RES.030  | OTel (CAPA\_10) registra spans de HallucinationGuard para auditoría de calidad. |

\---

\*INVESTIGACION\_FUT19\_HALLUCINATION\_GUARD\_V3\_01.md · RELAY\_005 · AGT 2026-05-12\*  
\*Generado por: cursos.au.agt@gmail.com · 2026-05-12\*  
\*Basado en: CAPA\_04\_MASTER\_V3\_01.md §4.6 \+ REPORTE\_GAPS\_FUT\_V3\_01\_2026-05-12.md\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
