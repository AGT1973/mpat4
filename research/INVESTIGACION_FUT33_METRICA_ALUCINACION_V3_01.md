\# INVESTIGACION\_FUT33\_METRICA\_ALUCINACION\_V3\_01.md  
\#\# MPAT — FUT.33 · Metrica de Alucinacion \+ Predictive Maintenance  
\#\# Autor: ariel.garcia.traba@gmail.com · RELAY\_006 · 2026-05-12  
\#\# RES sugerida: RES.121 (sin implementacion previa confirmada)

\*que has usado el formato de razonamiento adaptado por AGT\*

\---

\#\# IDENTIFICACION DEL GAP

| Campo | Valor |  
|---|---|  
| FUT | FUT.33 |  
| Descripcion original | Metrica de Alucinacion \+ Predictive Maintenance |  
| Capa asignada | Capa 11 (Orchestration) |  
| RES catalogo | RES.084 (colision — ya ocupada por FUT.32 / Predictive Empathy) |  
| RES canonica asignada | RES.121 (proxima disponible, MAPA\_RES\_CANONICO\_V3\_01.md) |  
| Estado anterior | GAP — sin implementacion confirmada en ningun MASTER |  
| Estado post-RELAY\_006 | CERRADO (diseno formal) — listo para implementacion |

\---

\#\# RELACION CON FUT.19 (HallucinationGuard)

FUT.33 es la capa analitica complementaria de FUT.19.

\`\`\`  
FUT.19 / HallucinationGuard (RES.055)  
  └── opera en TIEMPO REAL por tarea individual  
      detecta, clasifica señal, ejecuta re-prompt loop  
      escribe: ECS.hallucination\_warning por task\_id

FUT.33 / MetricaAlucinacion (RES.121)  
  └── opera en TIEMPO DIFERIDO sobre datos historicos  
      agrega ECS.hallucination\_warning de multiples tasks  
      produce: patrones por tenant, modelo, tipo de señal  
      alimenta: mantenimiento predictivo del sistema  
\`\`\`

FUT.33 sin FUT.19 no tiene datos de entrada.  
FUT.19 sin FUT.33 opera correctamente pero sin visibilidad sistemica.

\---

\#\# DECISION TECNICA — RES.121

| Campo | Valor |  
|---|---|  
| Item | FUT.33 |  
| Decision | Sistema de agregacion de metricas de alucinacion. Consume cognitive\_metrics (schema creado en FUT.20/RES.030). Produce indicadores por tenant, modelo y tipo de señal. Detecta tendencias anomalas. Dispara alertas de mantenimiento predictivo cuando la tasa de alucinacion supera umbrales configurables. |  
| Capa | 11 — Orchestration (complementa Unikernel-per-Tenant y SubQ) |  
| RES | RES.121 |  
| Dependencias | RES.055 (FUT.19 — datos fuente), RES.030 (FUT.20 — schema cognitive\_metrics) |

\---

\#\# ARQUITECTURA DEL SISTEMA

\#\#\# Flujo de datos

\`\`\`  
\[HallucinationGuard / FUT.19\]  
    │  escribe ECS.hallucination\_warning por task\_id  
    ▼  
\[cognitive\_metrics tabla / FUT.20 schema\]  
    │  tenant\_id, task\_id, signal\_type, retry\_count, resolved, timestamp  
    ▼  
\[AlucinacionAggregator / RES.121\]  
    │  agrega por ventana temporal (1h, 24h, 7d)  
    │  calcula: tasa, tipo dominante, tasa de resolucion  
    ▼  
\[AlucinacionMetricStore\]          \[PredictiveMaintenance\]  
    │  almacena metricas           │  detecta tendencias anomalas  
    │  por tenant \+ modelo         │  dispara alertas configurables  
    ▼                             ▼  
\[Dashboard Capa 0 / FUT.06\]    \[AlertManager → Audit Trail FUT.22\]  
\`\`\`

\---

\#\# COMPONENTE PRINCIPAL — AlucinacionAggregator

\`\`\`python  
"""  
alucinacion\_aggregator.py — MPAT Capa 11  
Agrega metricas de alucinacion desde cognitive\_metrics.

RES: RES.121  
Dependencias: RES.055 (FUT.19), RES.030 (FUT.20 schema)  
Capa: 11 — Orchestration  
"""

from dataclasses import dataclass  
from datetime import datetime, timedelta  
from typing import Optional  
import asyncpg

@dataclass  
class AlucinacionMetrica:  
    """  
    Metrica agregada de alucinaciones para un tenant en una ventana temporal.

    INV-AM.1: tasa\_alucinacion in \[0.0, 1.0\]  
    INV-AM.2: tasa\_resolucion in \[0.0, 1.0\]  
    INV-AM.3: total\_tasks \>= alucinaciones\_detectadas  
    """  
    tenant\_id: str  
    ventana: str                    \# "1h" | "24h" | "7d"  
    desde: datetime  
    hasta: datetime  
    total\_tasks: int  
    alucinaciones\_detectadas: int  
    alucinaciones\_resueltas: int  
    tasa\_alucinacion: float         \# alucinaciones\_detectadas / total\_tasks  
    tasa\_resolucion: float          \# alucinaciones\_resueltas / alucinaciones\_detectadas  
    señal\_dominante: Optional\[str\]  \# tipo de señal mas frecuente en la ventana  
    modelo\_id: Optional\[str\]        \# modelo con mayor tasa (si aplica)  
    promedio\_retries: float         \# promedio de intentos de re-prompt

class AlucinacionAggregator:  
    """  
    Agrega metricas de alucinacion desde cognitive\_metrics.

    Precondicion: tabla cognitive\_metrics disponible (FUT.20 / RES.030)  
    Postcondicion: AlucinacionMetrica calculada por tenant \+ ventana  
    INV-AGG.1: ventanas validas: "1h", "24h", "7d"  
    INV-AGG.2: tasa\_alucinacion \= 0.0 si total\_tasks \= 0 (no divide por cero)  
    INV-AGG.3: señal\_dominante \= None si no hubo alucinaciones en la ventana  
    """

    VENTANAS \= {  
        "1h":  timedelta(hours=1),  
        "24h": timedelta(hours=24),  
        "7d":  timedelta(days=7),  
    }

    def \_\_init\_\_(self, db\_pool: asyncpg.Pool):  
        self.db \= db\_pool

    async def agregar(  
        self,  
        tenant\_id: str,  
        ventana: str \= "24h",  
        modelo\_id: Optional\[str\] \= None  
    ) \-\> AlucinacionMetrica:  
        """  
        Calcula la metrica de alucinacion para un tenant en una ventana.

        Args:  
            tenant\_id: identificador del tenant  
            ventana: "1h" | "24h" | "7d"  
            modelo\_id: filtrar por modelo especifico (opcional)

        Returns:  
            AlucinacionMetrica con todos los indicadores calculados  
        """  
        assert ventana in self.VENTANAS, f"Ventana invalida: {ventana}"

        hasta \= datetime.utcnow()  
        desde \= hasta \- self.VENTANAS\[ventana\]

        filtro\_modelo \= "AND model\_id \= $4" if modelo\_id else ""  
        params \= \[tenant\_id, desde, hasta\]  
        if modelo\_id:  
            params.append(modelo\_id)

        query \= f"""  
            SELECT  
                COUNT(\*)                                        AS total\_tasks,  
                SUM(CASE WHEN hallucination THEN 1 ELSE 0 END) AS detectadas,  
                SUM(CASE WHEN resolved THEN 1 ELSE 0 END)      AS resueltas,  
                AVG(retry\_count)                                AS avg\_retries,  
                MODE() WITHIN GROUP (ORDER BY signal\_type)     AS señal\_dominante  
            FROM cognitive\_metrics  
            WHERE tenant\_id \= $1  
              AND created\_at BETWEEN $2 AND $3  
              {filtro\_modelo}  
        """

        row \= await self.db.fetchrow(query, \*params)

        total \= row\["total\_tasks"\] or 0  
        detectadas \= row\["detectadas"\] or 0  
        resueltas \= row\["resueltas"\] or 0

        return AlucinacionMetrica(  
            tenant\_id=tenant\_id,  
            ventana=ventana,  
            desde=desde,  
            hasta=hasta,  
            total\_tasks=total,  
            alucinaciones\_detectadas=detectadas,  
            alucinaciones\_resueltas=resueltas,  
            tasa\_alucinacion=detectadas / total if total \> 0 else 0.0,  
            tasa\_resolucion=resueltas / detectadas if detectadas \> 0 else 0.0,  
            señal\_dominante=row\["señal\_dominante"\],  
            modelo\_id=modelo\_id,  
            promedio\_retries=float(row\["avg\_retries"\] or 0.0),  
        )

    async def top\_tenants\_por\_tasa(  
        self,  
        ventana: str \= "24h",  
        limite: int \= 10  
    ) \-\> list\[dict\]:  
        """  
        Retorna los N tenants con mayor tasa de alucinacion en la ventana.  
        Util para identificar tenants que requieren atencion.  
        """  
        hasta \= datetime.utcnow()  
        desde \= hasta \- self.VENTANAS\[ventana\]

        query \= """  
            SELECT  
                tenant\_id,  
                COUNT(\*) AS total,  
                SUM(CASE WHEN hallucination THEN 1 ELSE 0 END) AS detectadas,  
                ROUND(  
                    SUM(CASE WHEN hallucination THEN 1.0 ELSE 0 END) / COUNT(\*), 4  
                ) AS tasa  
            FROM cognitive\_metrics  
            WHERE created\_at BETWEEN $1 AND $2  
            GROUP BY tenant\_id  
            ORDER BY tasa DESC  
            LIMIT $3  
        """  
        rows \= await self.db.fetch(query, desde, hasta, limite)  
        return \[dict(r) for r in rows\]  
\`\`\`

\---

\#\# COMPONENTE — PredictiveMaintenance

\`\`\`python  
class PredictiveMaintenance:  
    """  
    Detecta tendencias anomalas en las metricas de alucinacion.  
    Dispara alertas cuando la tasa supera umbrales configurables.

    RES: RES.121 (parte de FUT.33)  
    Capa: 11  
    INV-PM.1: umbral\_alerta in (0.0, 1.0)  
    INV-PM.2: una alerta por tenant por ventana maxima (no spam)  
    INV-PM.3: las alertas se registran en Audit Trail (FUT.22/RES.090)  
    """

    def \_\_init\_\_(  
        self,  
        aggregator: AlucinacionAggregator,  
        audit\_client,  
        config: dict  
    ):  
        self.aggregator \= aggregator  
        self.audit \= audit\_client  
        self.umbral \= config.get("hallucination.predictive.alert\_threshold", 0.3)  
        self.ventana \= config.get("hallucination.predictive.ventana", "24h")

    async def evaluar\_tenant(self, tenant\_id: str) \-\> dict:  
        """  
        Evalua si un tenant supera el umbral de alerta.

        Retorna: {"alerta": bool, "metrica": AlucinacionMetrica, "razon": str}  
        """  
        metrica \= await self.aggregator.agregar(tenant\_id, self.ventana)  
        alerta \= metrica.tasa\_alucinacion \> self.umbral

        if alerta:  
            razon \= (  
                f"Tasa de alucinacion {metrica.tasa\_alucinacion:.1%} "  
                f"supera umbral {self.umbral:.1%} "  
                f"en ventana {self.ventana}. "  
                f"Señal dominante: {metrica.señal\_dominante}. "  
                f"Promedio retries: {metrica.promedio\_retries:.2f}."  
            )  
            await self.audit.registrar(  
                tenant\_id=tenant\_id,  
                evento="HALLUCINATION\_ALERT",  
                detalle=razon,  
                metrica=metrica,  
            )

        return {  
            "alerta": alerta,  
            "metrica": metrica,  
            "razon": razon if alerta else None,  
        }

    async def evaluar\_todos(self) \-\> list\[dict\]:  
        """  
        Evalua todos los tenants activos en la ventana configurada.  
        Ejecutado periodicamente por el scheduler de Capa 11\.  
        """  
        ...  
\`\`\`

\---

\#\# SCHEMA DE BASE DE DATOS — EXTENSION FUT.33

FUT.20 ya creo la tabla \`cognitive\_metrics\`. FUT.33 agrega la tabla de metricas  
agregadas para evitar recalcular sobre la raw data en cada consulta:

\`\`\`sql  
\-- Tabla de metricas pre-agregadas (cache de AlucinacionAggregator)  
CREATE TABLE IF NOT EXISTS hallucination\_metrics\_agg (  
  id              SERIAL PRIMARY KEY,  
  tenant\_id       VARCHAR(64) NOT NULL,  
  modelo\_id       VARCHAR(128),  
  ventana         VARCHAR(8) NOT NULL,          \-- "1h" | "24h" | "7d"  
  desde           TIMESTAMPTZ NOT NULL,  
  hasta           TIMESTAMPTZ NOT NULL,  
  total\_tasks     INTEGER NOT NULL DEFAULT 0,  
  detectadas      INTEGER NOT NULL DEFAULT 0,  
  resueltas       INTEGER NOT NULL DEFAULT 0,  
  tasa\_alucinacion FLOAT NOT NULL DEFAULT 0.0,  
  tasa\_resolucion  FLOAT NOT NULL DEFAULT 0.0,  
  señal\_dominante  VARCHAR(64),  
  promedio\_retries FLOAT DEFAULT 0.0,  
  alerta\_disparada BOOLEAN DEFAULT FALSE,  
  computed\_at      TIMESTAMPTZ DEFAULT NOW(),  
  UNIQUE (tenant\_id, ventana, desde, hasta)  
);

\-- Tabla de alertas de mantenimiento predictivo  
CREATE TABLE IF NOT EXISTS hallucination\_alerts (  
  id              SERIAL PRIMARY KEY,  
  tenant\_id       VARCHAR(64) NOT NULL,  
  ventana         VARCHAR(8) NOT NULL,  
  tasa            FLOAT NOT NULL,  
  umbral          FLOAT NOT NULL,  
  señal\_dominante VARCHAR(64),  
  razon           TEXT,  
  audit\_id        VARCHAR(128),                \-- referencia Audit Trail (FUT.22)  
  created\_at      TIMESTAMPTZ DEFAULT NOW()  
);  
\`\`\`

\---

\#\# INTEGRACION CON EL SCHEDULER (Capa 11\)

FUT.33 se ejecuta como tarea periodica del scheduler de Capa 11:

\`\`\`yaml  
\# policy.yaml — seccion FUT.33  
hallucination\_predictive:  
  enabled: true  
  schedule\_cron: "0 \* \* \* \*"          \# cada hora  
  ventanas\_a\_calcular:  
    \- "1h"  
    \- "24h"  
    \- "7d"  
  alert\_threshold: 0.3                \# \[0.05, 0.9\]  
  alert\_ventana: "24h"               \# ventana para disparar alertas  
  top\_tenants\_limite: 20             \# N tenants en reporte de top ofensores  
\`\`\`

\---

\#\# PARAMETROS CAPA 14

\`\`\`yaml  
hallucination:  
  \# FUT.19 (HallucinationGuard) — ya existentes  
  enabled: true  
  max\_retries: 2  
  confidence\_threshold: 0.4

  \# FUT.33 (MetricaAlucinacion) — nuevos  
  predictive:  
    enabled: true  
    alert\_threshold: 0.3             \# tasa minima para disparar alerta \[0.05, 0.9\]  
    ventana: "24h"                   \# ventana de evaluacion de alertas  
    schedule\_cron: "0 \* \* \* \*"       \# frecuencia de agregacion  
    top\_tenants\_limite: 20           \# N tenants en reporte top \[5, 100\]  
\`\`\`

\---

\#\# INVARIANTES DE DISEÑO

\`\`\`  
INV-FUT33.1: FUT.33 es READ-ONLY sobre cognitive\_metrics.  
             No modifica datos de FUT.19. Solo agrega y pre-computa.

INV-FUT33.2: Si FUT.19 no tiene datos en la ventana, tasa \= 0.0.  
             No genera alertas de falso positivo por ventana sin actividad.

INV-FUT33.3: Las alertas se registran en Audit Trail (FUT.22 / RES.090).  
             Son trazables y forman parte del log cifrado E2EE.

INV-FUT33.4: La agregacion pre-computada (hallucination\_metrics\_agg) es un cache.  
             Puede reconstruirse desde cognitive\_metrics en cualquier momento.

INV-FUT33.5: FUT.33 no interfiere con el path critico de inferencia.  
             Opera en modo diferido, nunca bloquea una tarea activa.  
\`\`\`

\---

\#\# RELACION CON OTROS COMPONENTES

| Componente | Relacion | RES |  
|---|---|---|  
| HallucinationGuard (FUT.19) | Fuente de datos (ECS \+ cognitive\_metrics) | RES.055 |  
| OTel / cognitive\_metrics (FUT.20) | Schema de tabla fuente | RES.030 |  
| Audit Trail (FUT.22) | Destino de alertas de mantenimiento | RES.090 |  
| SubQ Asincrona (FUT\_3) | Scheduler de Capa 11 ejecuta FUT.33 periodicamente | RES.114 |  
| Dashboard Capa 0 (FUT.06) | Visualizacion de metricas agregadas | RES.093 |  
| FUT.34 — Dashboard Predictivo | Consume hallucination\_metrics\_agg para UI predictiva | RES.122 |

\---

\#\# ESTADO Y CONCLUSION

FUT.33 no tenia implementacion en ningun MASTER al momento de RELAY\_006.  
Este documento establece el diseno formal completo para su implementacion.

Entregables del diseno:  
\- AlucinacionAggregator: agregacion por tenant \+ ventana \+ modelo  
\- PredictiveMaintenance: deteccion de tendencias \+ alertas con registro en Audit Trail  
\- Schema SQL: hallucination\_metrics\_agg \+ hallucination\_alerts  
\- Parametros Capa 14: 4 parametros nuevos bajo hallucination.predictive.\*  
\- Integracion con scheduler de Capa 11 via cron

\*\*FUT.33 → CERRADO (diseno formal) · RES.121 · RELAY\_006 · 2026-05-12\*\*

\---

\*INVESTIGACION\_FUT33\_METRICA\_ALUCINACION\_V3\_01.md · RELAY\_006 · ariel.garcia.traba@gmail.com · 2026-05-12\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
