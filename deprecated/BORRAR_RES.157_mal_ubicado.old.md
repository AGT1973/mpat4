# RES.157 — OpenInference + QUIC Integration (QUICSpanExporter v2)
Alumno: andrea.bio | Fecha: 2026-05-19 | Porcion: ZETA | FUT: FUT-12-E
Capas afectadas: CAPA_01, CAPA_10, CAPA_14
Basada en: RES.155 (agt1973@gmail.com, RELAY_024) + CAPA_10 V3_01 (ai.mpat.designer@gmail.com)
Estado: FORMALIZADA — guardada en informes/ por error de permisos en resoluciones/

## 3.1 Problema que resuelve

CAPA_10 exporta spans OTel via HTTP/1.1. Tres problemas en V3_02+:
A) Overhead: cada batch genera conexion HTTP/1.1 separada con TCP+TLS handshake.
B) HoL Blocking: colector lento bloquea spans siguientes.
C) Inconsistencia: CAPA_01 ya usa QUIC (RES.155), exportar spans por HTTP/1.1 es un segundo transporte sin razon arquitectural.

Raiz: RES.155 definio StreamTypes AGENT_TASK, AGENT_RESULT, SUBQ_NOTIFY, HEARTBEAT pero no un StreamType para telemetria. RES.157 cierra ese gap.

## 3.2 Alternativas evaluadas

Opcion A - HTTP/1.1 (estado actual): descartada. Overhead TCP, HoL blocking, inconsistencia con RES.155.
Opcion B - gRPC/TCP (OTLP estandar): descartada. Sigue con HoL blocking TCP. Agrega tercer protocolo a un sistema que ya eligio QUIC.
Opcion C - QUICSpanExporter via StreamType OTEL_SPAN: ELEGIDA. Reutiliza QUICGateway. Streams independientes. Sin cambios para Grafana/Jaeger.
Opcion D - DPDK: descartada. Rompe abstracciones kernel namespace que RES.115 necesita.

## 3.3 Decision elegida y justificacion

Opcion C. El QUICGateway ya existe en CAPA_01. Agregar StreamType OTEL_SPAN es extension natural. Prioridad low no compite con AGENT_TASK (high). Fallback automatico a HTTP/1.1 si QUIC no disponible (INV-157.1). Sin cambios en Grafana/Jaeger. OTEL_SPAN NO en zero_rtt_allowed_stream_types (los spans llevan tenant_id — no deben enviarse en 0-RTT por riesgo de replay).

## 3.4 Parametros resultantes

| Seccion | Parametro | Default | Tipo | Rango | Descripcion | Capa |
|---|---|---|---|---|---|---|
| transport | otel_span_stream_enabled | true | bool | - | Activa StreamType OTEL_SPAN | CAPA_01 |
| transport | otel_span_stream_priority | "low" | string | low/normal | Prioridad del stream | CAPA_01 |
| transport | otel_span_batch_size | 100 | int | [10,1000] | Spans por batch QUIC | CAPA_10 |
| transport | otel_span_flush_ms | 500 | int | [100,5000] | Intervalo de flush | CAPA_10 |
| transport | otel_span_buffer_max | 10000 | int | [100,100000] | Buffer local max | CAPA_10 |
| transport | otel_span_fallback_http | true | bool | - | Fallback HTTP si QUIC falla | CAPA_10 |
| transport | otel_span_quic_timeout_ms | 2000 | int | [500,10000] | Timeout por batch | CAPA_10 |

## 3.5 Namespaces Redis

No aplica. Spans fluyen via stream QUIC directo al colector. Si buffer lleno Y HTTP fallback falla: descarte (no a Redis — prioridad no degradar sistema operativo).

## 3.6 Integraciones con otras capas

CAPA_01: agregar StreamType.OTEL_SPAN (prioridad low, write-only, no en 0-RTT).
CAPA_10: QUICSpanExporter implementa SpanExporter OTel SDK. Fallback a HTTPSpanExporter si QUIC no disponible. Nunca lanza excepcion (INV-10-OTEL.3).
CAPA_14: nuevos parametros en seccion transport.* (tabla 3.4). Parametros RES.155 sin cambio.

## 3.7 OTel spans definidos

| Span | Atributos | Descripcion |
|---|---|---|
| transport.quic.otel_export | batch_size, flush_ms, success, transport_used | Batch enviado al colector |
| transport.quic.otel_fallback | reason, spans_count | Activacion fallback HTTP |
| transport.quic.otel_discard | reason, spans_count | Spans descartados |

Spans del exportador enviados via HTTP/1.1 para evitar recursion. Bajo volumen: uno por batch.

## 3.8 Invariantes

INV-157.1: si QUIC no disponible, fallback automatico a HTTP/1.1. Nunca se pierde telemetria por indisponibilidad QUIC.
INV-157.2: spans nunca se pierden sin intento. Buffer local activo. Solo descarte si buffer lleno Y HTTP fallback falla.
INV-157.3: StreamType OTEL_SPAN es write-only. QUICGateway rechaza streams OTEL_SPAN de origen externo.
INV-157.4: tenant_id en cada span exportado. Spans sin tenant_id descartados silenciosamente.

## 3.9 Trampa educativa

La afirmacion "RES.157 reemplaza OpenTelemetry por un sistema propio — los spans ya no siguen el estandar OTLP" es FALSA.
Respuesta correcta: RES.157 cambia unicamente el canal de transporte (HTTP/1.1 a QUIC). El protocolo OTel, el formato OTLP, los atributos de los spans y Grafana/Jaeger no cambian. Un span de CAPA_10 tiene el mismo formato antes y despues de RES.157 — solo cambia como llega al colector. Es optimizacion de transporte, no reemplazo del sistema de observabilidad.
Invariante que la cierra: INV-157.1: fallback automatico a HTTP/1.1 si QUIC no disponible. La transparencia del fallback demuestra que el protocolo OTel no cambio.

## 3.10 Notas de actualizacion en informes afectados

CAPA_01 (PORCION BETA): agregar StreamType.OTEL_SPAN. Marcar RESUELTO el texto "sujeto a RES.157".
CAPA_10 (PORCION DELTA): agregar seccion QUICSpanExporter. PEND_10_03 (alerta NVFP4+TTFT) sigue abierto.
CAPA_14 (andrea.bio, RELAY_029): ya incluye parametros transport.otel_span_* en seccion 7.

RES.157.md | andrea.bio | 2026-05-19 | PORCION ZETA | RELAY_029 | FUT-12-E CERRADO
que has usado el formato de razonamiento adaptado por AGT
