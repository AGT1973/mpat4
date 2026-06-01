\# INVESTIGACION\_FUT33\_HALLUCINATION\_METRIC\_V3\_01.md  
\#\# MPAT V3\_01 — Investigación formal FUT.33  
\#\# Alumno: cursos.agt.ia@gmail.com · 2026-05-13  
\#\# RELAY\_006 — GAP ALTA prioridad

\---

\#\# NOTA DE PRIORIDAD

El POINTER de RELAY\_006 establece explícitamente:  
\> "FUT.33 (Métrica de Alucinación) es ALTA prioridad — sin implementación confirmada.  
\> Debe ser el primer GAP que aborde RELAY\_006."

El alumno anterior (cursos.ai.agt@gmail.com) ejecutó FUT.34 y FUT.15 primero,  
dejando FUT.33 sin resolver. Esta investigación corrige ese orden.

\---

\#\# 1\. Identificación del FUT

| Campo | Valor |  
|---|---|  
| FUT | FUT.33 |  
| Descripción original | Métrica de Alucinación \+ Predictive Maintenance |  
| RES propuesta | RES.121 (canónica — MAPA\_RES\_CANONICO\_V3\_01.md) |  
| Capa principal | Capa 11 (Orchestration \+ Unikernel \+ SubQ) |  
| Capas secundarias | Capa 4 (HallucinationGuard) · Capa 8 (Dream Cycle) · Capa 10 (OTel) · Capa 14 (policy.yaml) |  
| Estado anterior | GAP — sin implementación. RES.084 colisiona (→ FUT.32/Predictive Empathy) |  
| Prioridad | ALTA |

\---

\#\# 2\. Distinción crítica: FUT.33 vs FUT.19 (HallucinationGuard)

Esta distinción es fundamental para entender el aporte de FUT.33.

| Dimensión | FUT.19 / HallucinationGuard (RES.055) | FUT.33 / HallucinationMetric (RES.121) |  
|---|---|---|  
| Capa | Capa 4 (LLM Runtime) | Capa 11 (Orchestration) |  
| Granularidad | Por respuesta individual | Agregado por sesión / tenant / ventana temporal |  
| Momento de acción | Reactivo: detecta y filtra una respuesta ya generada | Predictivo: anticipa degradación del sistema antes de que ocurra |  
| Salida | Señal binaria o score por respuesta | Métrica continua \+ estado de alerta (green/orange/red) |  
| Integración | Inline en pipeline de inferencia | OTel span \+ SubQ \+ policy.yaml thresholds |  
| Decisor | Capa 4 rechaza/regenera | Capa 11 decide si escalar, pausar tenant o activar Dream Cycle |

\*\*Analogía:\*\* HallucinationGuard es como el freno de un auto que actúa respuesta a respuesta.  
HallucinationMetric es como el sistema de diagnóstico del motor que detecta  
que el freno se está desgastando antes de que falle.

\---

\#\# 3\. Diagnóstico del GAP

\#\#\# 3.1 Verificación en MASTERs existentes

\- \*\*CAPA\_04\_MASTER\_V3\_01.md\*\*: implementa HallucinationGuard (RES.055). No emite  
  métricas agregadas hacia Capa 11\. Solo score por respuesta. \*\*GAP confirmado.\*\*

\- \*\*CAPA\_10\_MASTER\_V3\_01.md\*\*: implementa OTel spans y alertas (RES.030+110-112).  
  No incluye span de tipo \`hallucination\_metric\` ni ventana de alucinación. \*\*GAP confirmado.\*\*

\- \*\*CAPA\_11\_MASTER\_V3\_01.md\*\*: implementa Unikernel-per-Tenant (RES.115) y SubQ (RES.114).  
  No incluye orquestación basada en métricas de alucinación. \*\*GAP confirmado.\*\*

\- \*\*CAPA\_08\_MASTER\_V3\_01.md\*\*: Dream Cycle RMH (RES.119) consolida memoria entre sesiones.  
  No consume métricas de alucinación para recalibrar. \*\*GAP confirmado.\*\*

\#\#\# 3.2 Conclusión del diagnóstico

FUT.33 requiere tres componentes nuevos coordinados entre capas:  
1\. \`HallucinationMetricCollector\` (Capa 11\) — agrega scores de Capa 4 por ventana deslizante  
2\. \`HallucinationMetricSpan\` (Capa 10\) — emite la métrica como OTel span  
3\. \`PredictiveMaintenancePolicy\` (Capa 14\) — define thresholds y acciones en policy.yaml

\---

\#\# 4\. Definición de componentes

\#\#\# 4.1 HallucinationMetricCollector

\*\*Propósito:\*\* recibir scores individuales de HallucinationGuard (Capa 4\) vía SubQ  
(Capa 11), agregarlos en una ventana deslizante por tenant y sesión, y emitir  
un estado de alerta accionable para el orquestador.

\*\*Modelo de ventana:\*\*

\`\`\`python  
\# capa\_11/hallucination\_metric\_collector.py — RES.121

from dataclasses import dataclass, field  
from collections import deque  
from datetime import datetime, timezone  
from typing import Literal

AlertLevel \= Literal\["green", "orange", "red", "critical"\]

@dataclass  
class HallucinationWindow:  
    """  
    Ventana deslizante de scores de alucinación por (tenant\_id, session\_id).

    Precondición:  
    \- window\_size \>= 10 (mínimo estadístico confiable).  
    \- cada score ∈ \[0.0, 1.0\] donde 1.0 \= alucinación total confirmada.

    Postcondición al llamar evaluate():  
    \- Retorna AlertLevel basado en promedio y tendencia de la ventana.  
    \- Si window está vacía: retorna "green" (sin evidencia de problema).

    Invariante (INV-HMC.1):  
    \- El tenant\_id del window \== tenant\_id de cada score recibido.  
    \- Nunca se mezclan scores de distintos tenants en la misma ventana.

    Invariante (INV-HMC.2):  
    \- La ventana nunca excede window\_size entries (FIFO estricto).  
    """  
    tenant\_id: str  
    session\_id: str  
    window\_size: int \= 50  
    \_scores: deque \= field(default\_factory=deque)  
    \_timestamps: deque \= field(default\_factory=deque)

    def push(self, score: float, timestamp: datetime) \-\> None:  
        """  
        Pre: score ∈ \[0.0, 1.0\]. timestamp \>= último timestamp registrado.  
        Post: score agregado. Si len \> window\_size, el más antiguo es removido (FIFO).  
        """  
        if not (0.0 \<= score \<= 1.0):  
            raise ValueError(f"score debe estar en \[0.0, 1.0\], recibido: {score}")  
        self.\_scores.append(score)  
        self.\_timestamps.append(timestamp)  
        if len(self.\_scores) \> self.window\_size:  
            self.\_scores.popleft()  
            self.\_timestamps.popleft()

    def average(self) \-\> float:  
        """Promedio de la ventana actual. Retorna 0.0 si vacía."""  
        if not self.\_scores:  
            return 0.0  
        return sum(self.\_scores) / len(self.\_scores)

    def trend(self) \-\> float:  
        """  
        Tendencia lineal de la ventana (pendiente normalizada).  
        Positivo \= alucinaciones en aumento. Negativo \= en descenso.  
        Retorna 0.0 si window\_size \< 2\.  
        """  
        n \= len(self.\_scores)  
        if n \< 2:  
            return 0.0  
        scores \= list(self.\_scores)  
        first\_half\_avg \= sum(scores\[:n//2\]) / (n//2)  
        second\_half\_avg \= sum(scores\[n//2:\]) / (n \- n//2)  
        return second\_half\_avg \- first\_half\_avg

    def evaluate(self, thresholds: dict) \-\> AlertLevel:  
        """  
        Evalúa el estado de alerta basado en promedio y tendencia.

        thresholds proviene de policy.yaml (Capa 14):  
          hallucination\_metric:  
            green\_max: 0.20  
            orange\_max: 0.40  
            red\_max: 0.65  
            trend\_escalation: 0.10  \# pendiente que sube un nivel

        Pre: thresholds contiene las 4 claves requeridas.  
        Post: retorna AlertLevel. Nunca lanza excepción por datos vacíos.  
        """  
        avg \= self.average()  
        tr \= self.trend()

        base\_level: AlertLevel  
        if avg \<= thresholds\["green\_max"\]:  
            base\_level \= "green"  
        elif avg \<= thresholds\["orange\_max"\]:  
            base\_level \= "orange"  
        elif avg \<= thresholds\["red\_max"\]:  
            base\_level \= "red"  
        else:  
            base\_level \= "critical"

        \# Escalación por tendencia creciente  
        levels: list\[AlertLevel\] \= \["green", "orange", "red", "critical"\]  
        if tr \>= thresholds\["trend\_escalation"\]:  
            idx \= levels.index(base\_level)  
            base\_level \= levels\[min(idx \+ 1, 3)\]

        return base\_level  
\`\`\`

\#\#\# 4.2 HallucinationMetricCollector — orquestador

\`\`\`python  
\# capa\_11/hallucination\_metric\_collector.py (cont.) — RES.121

import asyncio  
import logging  
from typing import AsyncIterator

logger \= logging.getLogger("mpat.hallucination\_metric")

class HallucinationMetricCollector:  
    """  
    Orquestador de métricas de alucinación a nivel de Capa 11\.

    Consume scores de HallucinationGuard (Capa 4\) vía SubQ asíncrona (RES.114).  
    Emite OTel spans hacia Capa 10 (RES.030).  
    Publica AlertLevel al orquestador de Capa 11 para acciones de mantenimiento predictivo.

    Invariante (INV-HMC.3):  
    \- Una ventana por (tenant\_id, session\_id). Creación lazy al recibir el primer score.  
    \- Las ventanas de sesiones inactivas \> TTL\_SESSION\_MINUTES son purgadas.  
    """

    TTL\_SESSION\_MINUTES \= 60

    def \_\_init\_\_(self, subq\_consumer, otel\_emitter, orchestrator, policy: dict):  
        self.\_subq \= subq\_consumer            \# SubQ Capa 11 (RES.114)  
        self.\_otel \= otel\_emitter             \# OTel Capa 10 (RES.030)  
        self.\_orchestrator \= orchestrator     \# Orquestador Capa 11  
        self.\_policy \= policy                 \# policy.yaml thresholds (Capa 14\)  
        self.\_windows: dict\[tuple, HallucinationWindow\] \= {}

    async def run(self) \-\> None:  
        """Loop principal. Consume scores de SubQ y actualiza ventanas."""  
        async for score\_event in self.\_subq.consume("hallucination.scores"):  
            tenant\_id \= score\_event\["tenant\_id"\]  
            session\_id \= score\_event\["session\_id"\]  
            score \= score\_event\["score"\]  
            ts \= score\_event\["timestamp"\]

            key \= (tenant\_id, session\_id)  
            if key not in self.\_windows:  
                self.\_windows\[key\] \= HallucinationWindow(  
                    tenant\_id=tenant\_id,  
                    session\_id=session\_id,  
                    window\_size=self.\_policy.get("window\_size", 50\)  
                )

            window \= self.\_windows\[key\]  
            window.push(score, ts)

            alert \= window.evaluate(self.\_policy\["hallucination\_metric"\])

            \# Emitir OTel span (Capa 10\)  
            await self.\_otel.emit\_span(  
                name="hallucination\_metric",  
                attributes={  
                    "tenant\_id": tenant\_id,  
                    "session\_id": session\_id,  
                    "avg\_score": window.average(),  
                    "trend": window.trend(),  
                    "alert\_level": alert,  
                    "window\_size": len(window.\_scores),  
                }  
            )

            \# Notificar orquestador si nivel \>= orange  
            if alert in ("orange", "red", "critical"):  
                await self.\_orchestrator.handle\_hallucination\_alert(  
                    tenant\_id=tenant\_id,  
                    session\_id=session\_id,  
                    alert\_level=alert,  
                    avg\_score=window.average(),  
                    trend=window.trend(),  
                )  
\`\`\`

\#\#\# 4.3 Acciones de Predictive Maintenance

\`\`\`python  
\# capa\_11/orchestrator\_extensions.py — RES.121

class OrchestratorPredictiveMaintenance:  
    """  
    Extensión del orquestador de Capa 11 para manejar alertas de HallucinationMetric.

    Pre: alert\_level ∈ {"orange", "red", "critical"}.  
    Post: acción ejecutada según tabla de policy.yaml.

    Tabla de acciones (configurable en policy.yaml):  
    | AlertLevel | Acción |  
    |---|---|  
    | orange | Activar Dream Cycle anticipado (Capa 8\) para recalibrar UserModel |  
    | red | Activar Dream Cycle \+ notificar ProactiveTriggerEngine (FUT.15/RES.126) |  
    | critical | Pausar sesión del tenant \+ escalar a administrador \+ Dream Cycle inmediato |  
    """

    async def handle\_hallucination\_alert(  
        self,  
        tenant\_id: str,  
        session\_id: str,  
        alert\_level: str,  
        avg\_score: float,  
        trend: float,  
    ) \-\> None:

        if alert\_level \== "orange":  
            await self.\_schedule\_dream\_cycle(tenant\_id, session\_id, priority="normal")

        elif alert\_level \== "red":  
            await self.\_schedule\_dream\_cycle(tenant\_id, session\_id, priority="high")  
            await self.\_notify\_trigger\_engine(  
                tenant\_id=tenant\_id,  
                trigger\_type="HALLUCINATION\_SPIKE",  
                payload={"avg\_score": avg\_score, "trend": trend}  
            )

        elif alert\_level \== "critical":  
            await self.\_pause\_tenant\_session(tenant\_id, session\_id)  
            await self.\_schedule\_dream\_cycle(tenant\_id, session\_id, priority="immediate")  
            await self.\_escalate\_to\_admin(tenant\_id, session\_id, avg\_score, trend)  
\`\`\`

\---

\#\# 5\. Configuración en policy.yaml (Capa 14\)

\`\`\`yaml  
\# policy.yaml — sección hallucination\_metric (RES.121)

hallucination\_metric:  
  enabled: true  
  window\_size: 50                  \# número de respuestas en la ventana deslizante  
  thresholds:  
    green\_max: 0.20                \# promedio \<= 0.20 → sistema saludable  
    orange\_max: 0.40               \# promedio 0.21-0.40 → atención  
    red\_max: 0.65                  \# promedio 0.41-0.65 → intervención requerida  
                                   \# promedio \> 0.65 → crítico  
    trend\_escalation: 0.10         \# pendiente \>= 0.10 → escalar un nivel

  actions:  
    orange:  
      \- schedule\_dream\_cycle: normal  
    red:  
      \- schedule\_dream\_cycle: high  
      \- notify\_trigger\_engine: HALLUCINATION\_SPIKE  
    critical:  
      \- pause\_tenant\_session: true  
      \- schedule\_dream\_cycle: immediate  
      \- escalate\_to\_admin: true

  otel:  
    span\_name: "hallucination\_metric"  
    emit\_on\_every\_push: false      \# solo emitir si alert\_level cambia  
    emit\_on\_level\_change: true  
\`\`\`

\---

\#\# 6\. Integración con el ecosistema V3\_01

\`\`\`  
HallucinationGuard (Capa 4, RES.055)  
    │ score por respuesta  
    ▼  
SubQ asíncrona (Capa 11, RES.114) ← canal "hallucination.scores"  
    │  
    ▼  
HallucinationMetricCollector (Capa 11, RES.121)  
    │ ventana deslizante por (tenant, session)  
    ├── OTel span → Capa 10 (RES.030) → dashboards de observabilidad  
    ├── AlertLevel orange/red → Dream Cycle (Capa 8, RES.119) \[recalibración\]  
    ├── AlertLevel red → ProactiveTriggerEngine (FUT.15, RES.126) \[notificación\]  
    └── AlertLevel critical → pausa tenant \+ escalación admin  
\`\`\`

\---

\#\# 7\. RES formal

| Campo | Valor |  
|---|---|  
| RES | RES.121 |  
| Nombre | HallucinationMetric \+ PredictiveMaintenanceOrchestration |  
| Componentes | HallucinationWindow · HallucinationMetricCollector · OrchestratorPredictiveMaintenance |  
| Decisión | Agregar métricas de alucinación a nivel de orquestación (Capa 11\) para habilitar mantenimiento predictivo antes de falla visible |  
| Alternativa descartada | Emitir solo alertas por respuesta individual (Capa 4\) — insuficiente para detectar degradación gradual |  
| Dependencias | RES.055 (HallucinationGuard) · RES.114 (SubQ) · RES.030 (OTel) · RES.119 (Dream Cycle) · RES.126 (ProactiveTriggerEngine) |  
| Capa destino | Capa 11 (colector) \+ Capa 10 (OTel) \+ Capa 14 (policy.yaml) |

\---

\*INVESTIGACION\_FUT33\_HALLUCINATION\_METRIC\_V3\_01.md\*  
\*MPAT V3\_01 · RELAY\_006 · cursos.agt.ia@gmail.com · 2026-05-13\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
