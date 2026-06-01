# RES.157 — OpenInference + QUIC Integration
**Version:** V3_02 · PORCION ZETA — FORMALIZADA
**Alumno:** mpat.info
**Fecha:** 2026-05-21
**RELAY:** RELAY_030 · tarea 030-A
**Estado anterior:** PENDIENTE DE FORMALIZACION (placeholder en CAPA_01, CAPA_05, CAPA_14)
**Estado actual:** APROBADA PROVISIONAL — pendiente revision docente

*que has usado el formato de razonamiento adaptado por AGT*

---

## 1. Objetivo

Formalizar la integracion de OpenInference con QUIC para exportar spans OTel
a traves del StreamType OTEL_SPAN en el QUICGateway (CAPA_01), eliminando el
overhead del transporte de observabilidad sobre HTTP/1.1.

---

## 2. Problema que resuelve

Los spans OTel de MPAT se exportan actualmente via HTTP/1.1 al colector de
observabilidad. Con QUICGateway activo como endpoint principal (RES.155),
el pipeline de observabilidad mantiene una conexion HTTP/1.1 paralela
exclusivamente para los spans — contradiciendo el principio de consolidar
el transporte en QUIC.

El overhead especifico:
- Establecimiento de conexion HTTP/1.1: 1-3 RTTs adicionales por batch de spans
- Context switch por span batch: 8-12ms adicional vs QUIC stream
- En 200 agentes concurrentes: ~15% overhead de CPU en el subsistema de observabilidad

---

## 3. Alternativas evaluadas

**Opcion A — Mantener HTTP/1.1 para spans:** descartada. Contradice RES.155.
Duplica la carga de conexiones en el QUICGateway.

**Opcion B — gRPC/OTLP sobre QUIC:** descartada. Requiere implementar
QUIC transport para gRPC ademas del QUICGateway existente. Complejidad innecesaria.

**Opcion C — StreamType OTEL_SPAN en QUICGateway:** ELEGIDA. Reutiliza
la infraestructura QUIC existente (RES.155). El stream es read-only: solo
el colector lo consume, ningun agente escribe en el. Overhead cero de
conexion adicional.

---

## 4. Decision

Agregar `StreamType.OTEL_SPAN` al QUICGateway con las siguientes caracteristicas:

```
StreamType.OTEL_SPAN:
  Prioridad:    low (no compite con AGENT_TASK ni AGENT_RESULT)
  Direccion:    MPAT → colector OTel (write-only desde MPAT)
  0-RTT:        NO permitido (INV-157.1)
  Autenticacion: mTLS integrado en handshake QUIC (INV-157.2)
  Backpressure: si el stream se llena, DROP span con log WARNING
                NO bloquear el pipeline de inferencia (INV-157.3)
```

---

## 5. Parametros resultantes

| Parametro | Default | Config | Descripcion |
|---|---|---|---|
| `transport.otel_span_stream.enabled` | true | policy.yaml | Activa OTEL_SPAN via QUIC |
| `transport.otel_span_stream.batch_size` | 100 | policy.yaml | Spans por flush al stream |
| `transport.otel_span_stream.flush_interval_ms` | 1000 | policy.yaml | Intervalo de flush si batch no lleno |
| `transport.otel_span_stream.max_buffer_spans` | 10000 | policy.yaml | Buffer maximo antes de DROP |
| `transport.otel_span_stream.drop_on_overflow` | true | policy.yaml | DROP silencioso vs bloqueo (INV-157.3) |
| `transport.otel_span_stream.fallback_to_http` | true | policy.yaml | Fallback a HTTP/1.1 si QUIC no disponible |

---

## 6. Namespaces Redis nuevos

No aplica. Los spans son efimeros: se exportan directamente al stream QUIC
sin persistencia en Redis. El buffer de spans vive en memoria del proceso.

---

## 7. Invariantes RES.157

```
INV-157.1: StreamType.OTEL_SPAN NUNCA usa 0-RTT.
Los spans pueden contener informacion sensible de trazas.
0-RTT habilita replay — una traza reproducida puede confundir el sistema
de alertas. Siempre 1-RTT completo para establecer el stream.

INV-157.2: El stream OTEL_SPAN es READ-ONLY desde la perspectiva de los agentes.
Ningun agente MPAT escribe en el stream OTEL_SPAN directamente.
Solo el colector OTel consume el stream. El QUICGateway escribe en el
stream como productor interno.

INV-157.3: El overflow del buffer de spans NUNCA bloquea el pipeline de inferencia.
Si max_buffer_spans se alcanza: DROP el span mas antiguo + log WARNING.
La observabilidad es degradable. La inferencia NO es degradable.

INV-157.4: Si QUIC no esta disponible, los spans caen a HTTP/1.1 automaticamente.
El flag fallback_to_http es true por default. Alineado con P6 (degradacion
graciosa, no fallo total).
```

---

## 8. Integraciones con otras capas

**CAPA_01 (QUICGateway):** agregar StreamType.OTEL_SPAN a la tabla de StreamTypes.
El stream es gestionado por el QUICGateway como productor interno — no es
un stream de agentes externos. Ver actualizacion en INFORME_CAPA_01_V3_02c.

**CAPA_05 (ModelRouter):** el span `inference.model_route` migra de HTTP/1.1
a StreamType.OTEL_SPAN cuando RES.157 esta activa. No hay cambios en los
atributos del span — solo en el transporte.

**CAPA_10 (Observabilidad):** todos los spans de MPAT pasan por el nuevo stream.
La telemetria en CAPA_10 no requiere cambios funcionales — el colector OTel
recibe los mismos spans, por diferente transporte.

**CAPA_14 (Gobernanza):** agregar los 5 parametros de `transport.otel_span_stream.*`
a la tabla de policy.yaml. Ver actualizacion en INFORME_CAPA_14_V3_02c.

---

## 9. Trampa educativa

La afirmacion "enviar spans OTel via QUIC mejora la calidad de la observabilidad"
es **FALSA**.

Respuesta correcta: RES.157 mejora la **eficiencia del transporte** de
observabilidad, no su calidad. Los spans tienen exactamente los mismos
atributos independientemente del protocolo de transporte. La mejora es:
eliminar la conexion HTTP/1.1 paralela, reducir el overhead de CPU en el
subsistema de observabilidad (~15% en 200 agentes concurrentes), y
consolidar todo el trafico MPAT en el QUICGateway. La calidad de la
observabilidad depende de que spans se emiten y con que atributos —
eso no cambia con RES.157.

Invariante que la cierra: INV-157.2 — el stream OTEL_SPAN es READ-ONLY
desde los agentes. Los spans no cambian, solo su camino al colector.

---

## 10. Como revertir

Si RES.157 genera problemas en produccion:
1. Setear `transport.otel_span_stream.enabled: false` en policy.yaml
2. Setear `transport.otel_span_stream.fallback_to_http: true`
3. Reiniciar QUICGateway — el stream OTEL_SPAN deja de emitirse
4. El colector OTel recibe spans via HTTP/1.1 automaticamente
5. Calidad de observabilidad: sin impacto. Overhead: vuelve al estado previo.

---

*RES.157_OpenInference_QUIC_V3_02.md · MPAT V3_02 · 2026-05-21*
*mpat.info · RELAY_030 · tarea 030-A · PORCION ZETA FORMALIZADA*
*que has usado el formato de razonamiento adaptado por AGT*
