\# INVESTIGACION\_FUT20\_OTEL\_V3\_01.md  
\#\# MPAT — FUT.20: OpenTelemetry Distributed Tracing  
\#\# Generado por: cursos.au.agt@gmail.com · 2026-05-12  
\#\# RELAY\_005 — Investigaciones · RES propuesta: RES.125

\---

\#\# ESTADO PREVIO

| Campo             | Valor                                                         |  
|-------------------|---------------------------------------------------------------|  
| FUT original      | FUT.20                                                        |  
| Capa              | 4 (origen) → 10 (implementación real)                        |  
| Descripción FUT   | OpenTelemetry Distributed Tracing para el sistema MPAT        |  
| Implementado en   | CAPA\_10\_MASTER\_V3\_01.md §§2-4 (desde V2\_29 · RES.030)       |  
| RES en catálogo   | RES.071 (estimada) — nunca asignada formalmente a OTel        |  
| RES real usada    | RES.030 (V2\_29, spans de disaggregation inferencia)           |  
| RES propuesta     | \*\*RES.125\*\* — formalización completa FUT.20 en V3\_01         |  
| Estado            | PARCIAL → CERRADO con este documento                          |

\---

\#\# 1\. PROBLEMA QUE RESUELVE

Un sistema multi-agente como MPAT ejecuta tareas que atraviesan múltiples capas:  
la petición entra por Capa 0, pasa por Capa 3 (Orchestrator), activa un agente (Capa 4),  
que infiere en Capa 5, accede a memoria en Capa 8, y entrega por Capa 13\.

Sin tracing distribuido, un fallo en producción genera la pregunta imposible:  
\*\*"¿en qué capa falló y por qué?"\*\* Sin contexto causal, el diagnóstico es  
ensayo y error sobre un sistema de 14 capas.

OpenTelemetry resuelve esto: cada operación genera un span vinculado al trace de la tarea  
original. Se puede reconstruir el camino completo de cualquier tarea, medir latencias  
por fase, y detectar exactamente dónde se degradó el rendimiento.

\---

\#\# 2\. DECISIÓN ARQUITECTURAL

\*\*Decisión:\*\* adoptar OpenTelemetry (OTel) como estándar único de tracing en MPAT.  
No reinventar logging propio. Usar el SDK oficial de Python con exportación a backend  
configurable (Jaeger/Tempo para desarrollo, vendor-agnostic para producción).

\*\*Principio rector de Capa 10:\*\*  
\> La observabilidad nunca interrumpe el flujo de ejecución.  
\> Todo fallo de tracing es silencioso — degraded mode, nunca propagado al agente.

\*\*Alternativas descartadas:\*\*  
\- Logging estructurado sin tracing: no captura causalidad entre capas.  
\- Tracing propio: reinvención del estándar sin beneficio. OTel es vendedor-neutral.  
\- Sentry/Datadog con SDK propietario: lock-in a vendor inaceptable para el proyecto.

\---

\#\# 3\. ARQUITECTURA DE SPANS EN MPAT

\#\#\# Jerarquía de spans por tarea

\`\`\`  
trace\_id: \<task\_id\>  
│  
├── span: task.receive (Capa 0 — Webhook/API)  
│   └── span: auth.validate (Capa 2\)  
│  
├── span: orchestrator.plan (Capa 3\)  
│   ├── span: agent.spawn (Capa 4\)  
│   │   ├── span: inference.execute (Capa 5\)  
│   │   │   ├── span: inference.prefill  
│   │   │   └── span: inference.decode  
│   │   ├── span: memory.retrieve (Capa 8\)  
│   │   └── span: hallucination.guard (Capa 4\)  
│   └── span: a2a.delegate (si hay delegación)  
│       └── span: agent.spawn (sub-agente)  
│  
└── span: delivery.emit (Capa 13\)  
    └── span: zts.verify (Capa 9\)  
\`\`\`

\#\#\# Atributos estándar por span

\`\`\`python  
\# Atributos obligatorios en TODOS los spans de MPAT  
SPAN\_REQUIRED\_ATTRS \= {  
    "mpat.task\_id": str,          \# ID único de la tarea  
    "mpat.agent\_id": str,         \# ID del agente ejecutando  
    "mpat.tenant\_id": str,        \# Tenant del alumno  
    "mpat.capa": int,             \# Número de capa (1-14)  
    "mpat.relay\_version": str,    \# Versión del relay ("V3\_01")  
}  
\`\`\`

\---

\#\# 4\. IMPLEMENTACIÓN — SPANS POR CATEGORÍA

\#\#\# 4.1 Spans de Inferencia (RES.030 — V2\_29, extendido en V3\_01)

\`\`\`python  
\# capa\_10/tracing/inference\_spans.py — V3\_01

from opentelemetry import trace  
from opentelemetry.trace import SpanKind

tracer \= trace.get\_tracer("mpat.capa\_05.inference")

def trace\_inference(task\_id: str, agent\_id: str, model\_id: str):  
    """Context manager para trazado de inferencia."""  
    with tracer.start\_as\_current\_span(  
        "inference.execute",  
        kind=SpanKind.INTERNAL  
    ) as span:  
        span.set\_attribute("mpat.task\_id", task\_id)  
        span.set\_attribute("mpat.agent\_id", agent\_id)  
        span.set\_attribute("inference.model\_id", model\_id)  
        \# Métricas de latencia (RES.030)  
        span.set\_attribute("inference.ttft\_ms", \-1)   \# Time to First Token  
        span.set\_attribute("inference.tpot\_ms", \-1)   \# Time Per Output Token  
        span.set\_attribute("inference.total\_tokens", 0\)  
        \# V3\_01: nuevos atributos de disaggregation  
        span.set\_attribute("inference.longcontext\_strategy", "none")  
        span.set\_attribute("inference.quantization", "none")  
        span.set\_attribute("inference.kv\_cache\_hit\_rate", 0.0)  
        yield span  
\`\`\`

\#\#\# 4.2 Spans de LongContext (V3\_01 — RES.110-112)

\`\`\`python  
\# Atributos para spans cuando se activa inferencia de largo contexto

LONGCONTEXT\_SPAN\_ATTRS \= {  
    "inference.longcontext\_activated": bool,  
    "inference.strategy": "ShadowRadix|CSA|HCA|combined",  
    "inference.threshold\_tokens": int,      \# tokens donde se activó la estrategia  
    "inference.kv\_hit\_rate": float,         \# tasa de acierto en KV cache  
    "inference.nvfp4\_active": bool,         \# cuantización NVFP4 activa  
    "inference.xgrammar2\_schema\_id": str,   \# schema usado si XGrammar-2 activo  
    "inference.xgrammar2\_compilation\_ms": int,  
}  
\`\`\`

\#\#\# 4.3 Spans de Seguridad (V3\_01 — RES.120)

\`\`\`python  
\# Atributos para spans de NHP \+ ZeroTrustSession

SECURITY\_SPAN\_ATTRS \= {  
    "security.nhp\_verified": bool,  
    "security.zts\_session\_id": str,  
    "security.zts\_created\_at\_utc": str,  
    "security.zts\_revoked": bool,  
    "security.zts\_revocation\_reason": str,  \# si fue revocada  
    "security.asl\_level": int,              \# ASL 1-4 del agente  
}  
\`\`\`

\#\#\# 4.4 Spans de A2A (V3\_01 — RES.113)

\`\`\`python  
\# Atributos para spans de delegación Agent-to-Agent

A2A\_SPAN\_ATTRS \= {  
    "a2a.delegation\_depth": int,  
    "a2a.delegator\_agent\_id": str,  
    "a2a.receiver\_agent\_id": str,  
    "a2a.agentcard\_version\_at\_delegation": str,  
    "a2a.agentcard\_mismatch\_detected": bool,  
    "a2a.budget\_delegated\_usd": float,  
    "a2a.handoff\_receipt\_id": str,          \# si fue handoff (no delegación)  
}  
\`\`\`

\#\#\# 4.5 Spans de HallucinationGuard (V3\_01 — RES.124)

\`\`\`python  
\# Atributos para spans del HallucinationGuard (integración con FUT.19)

HALLGUARD\_SPAN\_ATTRS \= {  
    "hallguard.signal\_detected": bool,  
    "hallguard.signal\_type": str,           \# DATE\_INCONSISTENCY, etc.  
    "hallguard.severity": float,  
    "hallguard.reprompt\_attempts": int,  
    "hallguard.final\_warning": bool,        \# True si pasó con warning después de max\_attempts  
}  
\`\`\`

\---

\#\# 5\. CÓDIGO DE INICIALIZACIÓN OTel

\`\`\`python  
\# capa\_10/tracing/setup.py — V3\_01

from opentelemetry import trace  
from opentelemetry.sdk.trace import TracerProvider  
from opentelemetry.sdk.trace.export import BatchSpanProcessor  
from opentelemetry.exporter.otlp.proto.grpc.trace\_exporter import OTLPSpanExporter  
from opentelemetry.sdk.resources import Resource

def setup\_tracing(config: dict) \-\> TracerProvider:  
    """  
    Inicializa OpenTelemetry para MPAT.

    Principio de Capa 10: si la inicialización falla, el sistema  
    continúa en modo degradado (sin tracing), nunca falla por observabilidad.  
    """  
    try:  
        resource \= Resource.create({  
            "service.name": "mpat",  
            "service.version": config.get("mpat.version", "V3\_01"),  
            "deployment.environment": config.get("mpat.environment", "production"),  
        })

        provider \= TracerProvider(resource=resource)

        otlp\_endpoint \= config.get("observability.otlp\_endpoint", "http://localhost:4317")  
        exporter \= OTLPSpanExporter(endpoint=otlp\_endpoint)  
        provider.add\_span\_processor(BatchSpanProcessor(exporter))

        trace.set\_tracer\_provider(provider)  
        return provider

    except Exception as e:  
        \# Fallo silencioso — observabilidad nunca bloquea el sistema  
        import logging  
        logging.getLogger("mpat.tracing").warning(  
            f"OTel initialization failed — degraded mode: {e}"  
        )  
        return trace.get\_tracer\_provider()  \# NoOp provider como fallback  
\`\`\`

\---

\#\# 6\. PARÁMETROS CONFIGURABLES (config\_policy.yaml)

\`\`\`yaml  
observability:  
  otlp\_endpoint: "http://localhost:4317"  
  \# Endpoint del backend OTel (Jaeger, Tempo, o OTLP collector).  
  \# En producción: URL del colector centralizado.

  tracing\_enabled: true  
  \# Habilita/deshabilita el tracing. Default: true.  
  \# Deshabilitar solo en entornos con restricciones de red estrictas.

  trace\_sample\_rate: 1.0  
  \# Tasa de muestreo de trazas. 1.0 \= 100% de trazas.  
  \# Rango: \[0.0, 1.0\]. Reducir en producción de alto volumen.

  span\_export\_batch\_size: 512  
  \# Tamaño del batch de spans exportados por ciclo.  
  \# Rango: \[1, 2048\]. Aumentar en sistemas de alto throughput.

  longcontext\_spans\_enabled: true  
  \# Habilita spans detallados de estrategias LongContext (RES.110-112).  
  \# Puede generar volumen alto de datos — deshabilitar en producción de alto volumen.  
\`\`\`

\---

\#\# 7\. RESOLUCIÓN FORMAL — RES.125

\*\*RES.125 — OpenTelemetry Distributed Tracing: implementación completa en MPAT V3\_01\*\*

\*\*Problema:\*\* el sistema multi-agente de 14 capas necesita trazabilidad causal completa.  
Sin tracing distribuido, el diagnóstico de fallos en producción es inviable.

\*\*Decisión:\*\* OpenTelemetry como estándar único. SDK Python oficial. Exportación  
vía OTLP a backend configurable. Degraded mode garantizado: fallo de tracing  
nunca propaga excepción al agente.

\*\*Alcance:\*\* todas las capas del sistema. Spans obligatorios en: Capa 0 (entrada),  
Capa 3 (Orchestrator), Capa 4 (Agente), Capa 5 (Inferencia), Capa 8 (Memoria),  
Capa 9 (Seguridad), Capa 13 (Delivery).

\*\*Impacto:\*\* CAPA\_10 (implementación), configuración en CAPA\_14 (policy.yaml).

\*\*Relación con RES anteriores:\*\*  
\- RES.030 (V2\_29): spans de disaggregation de inferencia — incluidos en esta RES.  
\- RES.110-112: spans específicos de ShadowRadix, NVFP4, XGrammar-2 — incluidos.  
\- RES.120: spans de NHP \+ ZTS — incluidos.  
\- RES.113: spans A2A — incluidos.  
\- RES.124: spans HallucinationGuard — incluidos.

\*\*RES asignada:\*\* RES.125 (nueva — consolida y formaliza todo el tracing V3\_01).

\---

\#\# 8\. RELACIÓN CON OTRAS RESOLUCIONES

| RES    | Relación                                                                  |  
|--------|---------------------------------------------------------------------------|  
| RES.030 | Spans de disaggregation de inferencia (TTFT/TPOT) — absorbido en RES.125 |  
| RES.110 | ShadowRadix+CSA/HCA — span attributes definidos en RES.125               |  
| RES.111 | NVFP4 — span attribute \`inference.nvfp4\_active\` en RES.125               |  
| RES.112 | XGrammar-2 — span attributes \`xgrammar2\_\*\` en RES.125                    |  
| RES.113 | A2A — span attributes \`a2a.\*\` en RES.125                                  |  
| RES.120 | NHP+ZTS — span attributes \`security.\*\` en RES.125                        |  
| RES.124 | HallucinationGuard — span attributes \`hallguard.\*\` en RES.125            |

\---

\*INVESTIGACION\_FUT20\_OTEL\_V3\_01.md · RELAY\_005 · AGT 2026-05-12\*  
\*Generado por: cursos.au.agt@gmail.com · 2026-05-12\*  
\*Basado en: CAPA\_10\_MASTER\_V3\_01.md §§2-4 \+ REPORTE\_GAPS\_FUT\_V3\_01\_2026-05-12.md\*  
\*que has usado el formato de razonamiento adaptado por AGT\*  
