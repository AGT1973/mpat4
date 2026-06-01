\# INVESTIGACION\_FUT20\_OTEL\_V3\_01.md  
\#\# MPAT — FUT.20 · OpenTelemetry Distributed Tracing  
\#\# Autor: ariel.garcia.traba@gmail.com · RELAY\_005 · 2026-05-12  
\#\# RES efectiva: RES.071 (catalogo) / implementacion real: RES.030 \+ RES.110-112 (CAPA\_10 V3\_01)

\*que has usado el formato de razonamiento adaptado por AGT\*

\---

\#\# IDENTIFICACION DEL GAP

| Campo | Valor |  
|---|---|  
| FUT | FUT.20 |  
| Descripcion original | OpenTelemetry Distributed Tracing |  
| Capa asignada | Capa 4 |  
| RES catalogo | RES.071 |  
| RES real implementada | RES.030 \+ RES.110 \+ RES.111 \+ RES.112 (CAPA\_10 V3\_01) |  
| Estado anterior | PARCIAL — cubierto en CAPA\_10 V3\_01 pero sin investigacion FUT.20 formal |  
| Estado post-RELAY\_005 | CERRADO — investigacion formal generada |

\---

\#\# CONTEXTO ARQUITECTURAL

FUT.20 fue planificado como un sistema de trazabilidad distribuida para MPAT  
usando el estandar OpenTelemetry (OTel). Su implementacion se distribuyo a lo  
largo de multiples versiones y capas, con el grueso concentrado en CAPA\_10  
(Monitoring \+ OTel) en V3\_01.

La implementacion cubre 4 areas criticas:

1\. \*\*RES.030\*\* — Trazabilidad base de inferencia (spans de ciclo de vida del agente)  
2\. \*\*RES.110\*\* — LongContext Spans (spans de atencion sub-cuadratica, ShadowRadix+CSA/HCA)  
3\. \*\*RES.111\*\* — NVFP4 Alerts (spans de cuantizacion FP4, hardware allowlist)  
4\. \*\*RES.112\*\* — ZTS+NHP Spans (spans de seguridad, ZeroTrustSession \+ NHP Protocol)

Los 4 bloques conforman el sistema OTel completo de MPAT en V3\_01.

\---

\#\# DECISION TECNICA — RES.030 (BASE)

| Campo | Valor |  
|---|---|  
| Item | FUT.20 base |  
| Decision | OpenTelemetry SDK integrado en el ciclo de vida del agente. Un span raiz por tarea (task\_span). Spans hijos por fase: PLAN, EXECUTE, VERIFY, EMIT. Propagacion de contexto via W3C TraceContext en headers HTTP/gRPC. |  
| Exportador | OTLP sobre gRPC (configurable) |  
| Backend | Compatible con Jaeger, Tempo, cualquier backend OTLP |

\---

\#\# ARQUITECTURA DE SPANS EN MPAT

\#\#\# Jerarquia de spans por tarea

\`\`\`  
\[task\_span\]  ← span raiz, task\_id como atributo  
  ├── \[plan\_span\]      — calculo E(tarea), definicion subtareas  
  ├── \[execute\_span\]   — inferencia LLM \+ llamadas MCP  
  │     ├── \[llm\_span\]         — latencia de inferencia, tokens  
  │     ├── \[mcp\_tool\_span\]    — cada llamada a tool MCP  
  │     └── \[a2a\_delegate\_span\] — delegacion a agente hijo (si aplica)  
  ├── \[verify\_span\]    — validacion Orchestrator  
  └── \[emit\_span\]      — entrega a Capa 13  
\`\`\`

\#\#\# Atributos estandar por span

\`\`\`python  
\# Atributos presentes en TODOS los spans MPAT  
SPAN\_ATTRS\_BASE \= {  
    "mpat.tenant\_id": str,           \# tenant propietario  
    "mpat.task\_id": str,             \# identificador de tarea  
    "mpat.agent\_id": str,            \# agente ejecutor  
    "mpat.capa": int,                \# capa arquitectural  
    "mpat.version": str,             \# V3\_01  
}

\# Atributos adicionales en llm\_span  
SPAN\_ATTRS\_LLM \= {  
    "mpat.model\_id": str,            \# modelo LLM usado  
    "mpat.tokens\_input": int,        \# tokens de entrada  
    "mpat.tokens\_output": int,       \# tokens de salida  
    "mpat.latency\_ms": float,        \# latencia total de inferencia  
    "mpat.hallucination\_warning": bool,  \# FUT.19 — si se detecto alucinacion  
    "mpat.entropy": float,           \# entropia de la respuesta (ERR)  
}

\# Atributos en mcp\_tool\_span  
SPAN\_ATTRS\_MCP \= {  
    "mpat.tool\_name": str,           \# nombre del tool invocado  
    "mpat.tool\_version": str,        \# version del tool (Tool Registry)  
    "mpat.tool\_latency\_ms": float,   \# latencia del tool  
    "mpat.tool\_success": bool,       \# resultado de la invocacion  
}  
\`\`\`

\---

\#\# EXTENSION V3\_01 — SPANS DE LARGO CONTEXTO (RES.110)

CAPA\_10 V3\_01 introduce spans especificos para las nuevas capacidades de  
atencion sub-cuadratica (ShadowRadix \+ CSA/HCA de CAPA\_05):

\`\`\`python  
\# LongContext span — RES.110  
\# Presente cuando context\_tokens \> longcontext.threshold

SPAN\_ATTRS\_LONGCONTEXT \= {  
    "mpat.longcontext.context\_tokens": int,    \# tokens en contexto  
    "mpat.longcontext.kv\_hit\_rate": float,     \# hit rate de KV cache \[0.0, 1.0\]  
    "mpat.longcontext.attention\_mode": str,    \# "standard" | "shadowradix" | "csa\_hca"  
    "mpat.longcontext.segments\_processed": int, \# segmentos procesados por CSA/HCA  
}

\# Alerta cuando kv\_hit\_rate \< longcontext.kv\_hit\_rate\_alert\_threshold  
\# La alerta se propaga como span event, no como span separado  
\`\`\`

\---

\#\# EXTENSION V3\_01 — SPANS DE CUANTIZACION NVFP4 (RES.111)

\`\`\`python  
\# NVFP4 span — RES.111  
\# Presente cuando el modelo usa cuantizacion FP4 (hardware Blackwell)

SPAN\_ATTRS\_NVFP4 \= {  
    "mpat.nvfp4.hardware\_id": str,             \# GPU en uso  
    "mpat.nvfp4.in\_allowlist": bool,           \# hardware en lista blanca  
    "mpat.nvfp4.quantization\_active": bool,    \# FP4 activo en inferencia  
    "mpat.nvfp4.precision\_loss\_estimated": float, \# perdida de precision estimada  
}

\# Alerta cuando in\_allowlist \= False (hardware no verificado para FP4)  
\`\`\`

\---

\#\# EXTENSION V3\_01 — SPANS DE SEGURIDAD ZTS+NHP (RES.112)

\`\`\`python  
\# ZeroTrustSession \+ NHP span — RES.112  
\# Presente en cada handshake agente-a-agente

SPAN\_ATTRS\_ZTS\_NHP \= {  
    "mpat.security.nhp\_handshake\_ms": float,   \# duracion del handshake NHP  
    "mpat.security.zts\_session\_id": str,       \# ID de sesion ZTS  
    "mpat.security.zts\_established": bool,     \# sesion establecida exitosamente  
    "mpat.security.asl\_level": int,            \# nivel ASL activo (1-4)  
    "mpat.security.trust\_verified": bool,      \# trust verification superada  
}  
\`\`\`

\---

\#\# IMPLEMENTACION: otel\_manager.py

\`\`\`python  
"""  
otel\_manager.py — MPAT Capa 10  
OpenTelemetry Manager: instrumentacion distribuida del sistema MPAT.

RES: RES.030 (base) \+ RES.110 (LongContext) \+ RES.111 (NVFP4) \+ RES.112 (ZTS+NHP)  
Estandar: OpenTelemetry 1.x, OTLP sobre gRPC  
Propagacion: W3C TraceContext  
"""

from opentelemetry import trace  
from opentelemetry.sdk.trace import TracerProvider  
from opentelemetry.sdk.trace.export import BatchSpanProcessor  
from opentelemetry.exporter.otlp.proto.grpc.trace\_exporter import OTLPSpanExporter  
from opentelemetry.propagate import set\_global\_textmap  
from opentelemetry.propagators.b3 import B3MultiFormat

class MPATOtelManager:  
    """  
    Inicializa y gestiona el provider OTel para MPAT.

    Precondicion: config OTLP disponible en Capa 14  
    Postcondicion: tracer global configurado, spans exportados a backend OTLP  
    INV-OTEL.1: cada task\_id mapea a exactamente un trace\_id  
    INV-OTEL.2: propagacion W3C activa en todos los boundary HTTP/gRPC  
    INV-OTEL.3: span de alucinacion (FUT.19) siempre hijo de llm\_span  
    """

    def \_\_init\_\_(self, config: dict):  
        self.config \= config  
        self.\_provider \= None  
        self.\_tracer \= None

    def initialize(self) \-\> None:  
        """Configura TracerProvider \+ BatchSpanProcessor \+ OTLP exporter."""  
        exporter \= OTLPSpanExporter(  
            endpoint=self.config\["otel.otlp\_endpoint"\],  
            insecure=self.config.get("otel.insecure", False),  
        )  
        processor \= BatchSpanProcessor(  
            exporter,  
            max\_export\_batch\_size=self.config.get("otel.batch\_size", 512),  
            export\_timeout\_millis=self.config.get("otel.export\_timeout\_ms", 5000),  
        )  
        self.\_provider \= TracerProvider()  
        self.\_provider.add\_span\_processor(processor)  
        trace.set\_tracer\_provider(self.\_provider)  
        self.\_tracer \= trace.get\_tracer("mpat.core", schema\_url="V3\_01")

    def get\_tracer(self) \-\> trace.Tracer:  
        """Retorna el tracer activo para instrumentacion inline."""  
        return self.\_tracer

    def create\_task\_span(self, task\_id: str, tenant\_id: str, agent\_id: str):  
        """  
        Crea el span raiz de una tarea.  
        Context manager — usar con 'with'.  
        """  
        return self.\_tracer.start\_as\_current\_span(  
            "mpat.task",  
            attributes={  
                "mpat.task\_id": task\_id,  
                "mpat.tenant\_id": tenant\_id,  
                "mpat.agent\_id": agent\_id,  
                "mpat.version": "V3\_01",  
            }  
        )  
\`\`\`

\---

\#\# SCHEMA DE BASE DE DATOS — EXTENSION V3\_01

CAPA\_10 V3\_01 extiende las tablas de metricas para incluir datos OTel:

\`\`\`sql  
\-- Extension de inference\_metrics (RES.030 base)  
ALTER TABLE inference\_metrics  
  ADD COLUMN trace\_id       VARCHAR(32),   \-- OTel trace\_id (hex 128-bit)  
  ADD COLUMN span\_id        VARCHAR(16),   \-- OTel span\_id (hex 64-bit)  
  ADD COLUMN kv\_hit\_rate    FLOAT,         \-- RES.110 LongContext  
  ADD COLUMN context\_tokens INTEGER,       \-- RES.110 LongContext  
  ADD COLUMN fp4\_active     BOOLEAN,       \-- RES.111 NVFP4  
  ADD COLUMN nhp\_ms         FLOAT;         \-- RES.112 ZTS+NHP

\-- cognitive\_metrics: alucinaciones por sesion (FUT.19 → FUT.33)  
CREATE TABLE IF NOT EXISTS cognitive\_metrics (  
  id              SERIAL PRIMARY KEY,  
  tenant\_id       VARCHAR(64) NOT NULL,  
  task\_id         VARCHAR(64) NOT NULL,  
  trace\_id        VARCHAR(32),  
  hallucination   BOOLEAN DEFAULT FALSE,  
  signal\_type     VARCHAR(64),             \-- tipo de señal FUT.19  
  retry\_count     INTEGER DEFAULT 0,  
  resolved        BOOLEAN DEFAULT FALSE,  
  created\_at      TIMESTAMPTZ DEFAULT NOW()  
);  
\`\`\`

\---

\#\# PARAMETROS CAPA 14

\`\`\`yaml  
otel:  
  enabled: true  
  otlp\_endpoint: "http://localhost:4317"     \# endpoint OTLP gRPC  
  insecure: false                             \# TLS requerido en produccion  
  service\_name: "mpat-core"  
  batch\_size: 512                             \# spans por batch \[64, 2048\]  
  export\_timeout\_ms: 5000                    \# timeout exportacion \[1000, 30000\]  
  longcontext:  
    enabled: true  
    threshold: 8192                          \# tokens minimos para LongContext span  
    kv\_hit\_rate\_alert\_threshold: 0.5         \# alerta si kv\_hit\_rate \< este valor  
  nvfp4:  
    hardware\_allowlist:                      \# GPUs verificadas para FP4  
      \- "H100"  
      \- "B100"  
      \- "B200"  
\`\`\`

\---

\#\# INTEGRACION CON OTROS COMPONENTES

| Componente | Relacion | RES |  
|---|---|---|  
| HallucinationGuard (FUT.19) | Span event de alucinacion en llm\_span | RES.055 |  
| ShadowRadix \+ CSA/HCA (FUT\_3) | LongContext spans (RES.110) | RES.110 |  
| NVFP4 (FUT\_3) | Cuantizacion spans (RES.111) | RES.111 |  
| NHP \+ ZTS (FUT\_3) | Security spans (RES.112) | RES.112 |  
| A2A v1.0 (FUT\_3) | Propagacion de trace context en delegaciones | RES.113 |  
| Audit Trail (FUT.22) | OTel como complemento del audit log | RES.090 |  
| FUT.34 — Dashboard Predictivo | Consume metricas de cognitive\_metrics | pendiente |

\---

\#\# ESTADO Y CONCLUSION

FUT.20 fue implementado de forma distribuida en CAPA\_10 V3\_01, cubriendo:

\- Trazabilidad base de agentes (RES.030): ciclo de vida completo por tarea  
\- LongContext Spans (RES.110): spans especificos para atencion sub-cuadratica  
\- NVFP4 Alerts (RES.111): instrumentacion de cuantizacion FP4  
\- ZTS+NHP Spans (RES.112): spans de seguridad agente-a-agente

La implementacion es conforme con OpenTelemetry 1.x y OTLP sobre gRPC.  
El schema de base de datos fue extendido para persistir trace\_id y span\_id.

\*\*FUT.20 → CERRADO · RES.030+RES.110+RES.111+RES.112 · RELAY\_005 · 2026-05-12\*\*

\---

\#\# COLISION DE NUMERACION DETECTADA

| Campo | Valor |  
|---|---|  
| RES catalogo para FUT.20 | RES.071 |  
| RES real implementada | RES.030 \+ RES.110-112 |  
| Resolucion | Ver MAPA\_RES\_CANONICO\_V3\_01.md — FUT.20 tiene cobertura multi-RES |

\---

\*INVESTIGACION\_FUT20\_OTEL\_V3\_01.md · RELAY\_005 · ariel.garcia.traba@gmail.com · 2026-05-12\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
