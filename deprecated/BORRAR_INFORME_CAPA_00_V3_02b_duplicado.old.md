# INFORME_CAPA_00_V3_02b
**Alumno:** ariel.garcia.traba@gmail.com | **Fecha:** 2026-05-19 | **RELAY_029 BETA**
**Canonico base:** 1dNMA8Ia0aqXxIiUd8hKEDFkEgxrXc86l (andrea.bio, DT-004, RELAY_027)
**RES:** RES.115, RES.132, RES.155
*que has usado el formato de razonamiento adaptado por AGT*

---

## BRECHAS RESUELTAS EN V3_02b

Las siguientes brechas se suman al canonico V3_02 DT-004 sin modificar su contenido.

---

## BRECHA 00-1 — Diagrama ASCII del flujo de entrada

```
FLUJO DE ENTRADA CAPA_00:

[Browser]    ─┐
[Telegram]   ─┤──→ [ChannelAdapter] ──→ [PlatformDetector] ──→ [UnifiedInputBuilder]
[WhatsApp]   ─┤         │                      │                        │
[API REST]   ─┘  adapta protocolo      adjunta platform_id      construye UnifiedInput
              (JSON Telegram            ("telegram" | "whatsapp"  frozen, sin inventar
              → UnifiedInput parcial)   | "browser" | "api_rest"  campos desconocidos
                                        | "unknown" si ambiguo)

             UnifiedInput (frozen)
                    │
                    ↓
             CAPA_01 QUICGateway (o HTTP/1.1 fallback segun P6)

Invariantes activos:
  INV-CH.1: contenido semantico nunca modificado en ninguna etapa
  INV-CH.2: pipeline nunca bloqueado por platform_id desconocido
  P10: raw_content NUNCA logueado en texto plano
```

---

## BRECHA 00-2 — DbC formal del UnifiedInputValidator (componente critico)

El UnifiedInputBuilder opera como validador implicito. V3_02b formaliza su contrato:

**Design-by-Contract: UnifiedInputBuilder.build()**
Precondicion: ChannelAdapter ha extraido raw_content no vacio. platform_id asignado (puede ser "unknown"). received_at timestamp valido.
Postcondicion: UnifiedInput frozen con todos los campos presentes. Los campos no determinables desde el canal tienen valor None (nunca inventados). transport="quic" si el request llego via QUIC stream, "http11" si fallback.
Invariante INV-CH.1: UnifiedInputBuilder NUNCA modifica el raw_content semanticamente. Transformacion de protocolo (Telegram JSON → campos) si; interpretacion del contenido no.
Invariante INV-CH.3: Si raw_content no puede extraerse del canal (payload corrupto), el ChannelAdapter descarta el request con log explicito. NUNCA propaga un UnifiedInput con raw_content=None hacia CAPA_01.

---

## BRECHA 00-3 — RES.132 con estructura completa de 8 subsecciones

### RES.132 — Edge LATAM: 10 nodos con ping < 40ms

#### 3.1 Problema que resolvia
MPAT en V2 operaba desde un unico punto de presencia (datacenter principal). Para usuarios en America Latina con latencia base de 150-200ms al datacenter, el handshake QUIC de 1-RTT + autenticacion JWT representaba 300-400ms antes del primer token de respuesta. Con 50ms RTT a un nodo edge regional, el mismo ciclo baja a 100-150ms — reduccion del 60-70%.

#### 3.2 Alternativas evaluadas
- **Opcion A: CDN estandar (Cloudflare, Fastly)** — descartada: los CDNs no pueden ejecutar logica de autenticacion JWT ni NHP (CAPA_09). Solo sirven contenido estatico o hacen proxy simple. MPAT requiere validacion de tenant antes de levantar unikernel.
- **Opcion B: 10 nodos edge con MPAT parcial** — elegida: cada nodo edge ejecuta CAPA_00 + CAPA_01 completas (autenticacion, QUIC). Las capas cognitivas (CAPA_03 a CAPA_08) se ejecutan en el datacenter principal o en el nodo edge segun la carga. El nodo edge actua como punto de autenticacion regional.
- **Opcion C: Solo nodo principal** — descartada: latencia inaceptable para usuarios LATAM. RTT > 100ms degrada la experiencia de streaming SSE (chunks percibidos como "lentos").

#### 3.3 Decision elegida y justificacion
Opcion B. Los 10 nodos edge ejecutan el stack CAPA_00+CAPA_01 completo con QUIC + eBPF (RES.155). El beneficio de 0-RTT QUIC (RES.155) es especialmente relevante en LATAM: con sesion previa, el handshake es 0ms vs 50ms (1-RTT). Esto requiere que el session ticket Redis (mpat:quic:ticket:{tenant_id}, TTL=86400s) se replique entre nodos del mismo tenant.

#### 3.4 Parametros resultantes
| Parametro | Default | Rango | Descripcion |
|---|---|---|---|
| edge.nodes_count | 10 | [1,50] | Nodos edge activos |
| edge.target_rtt_ms | 40 | [10,100] | RTT objetivo por nodo |
| edge.regions | LATAM | lista | Regiones cubiertas |
| edge.session_ticket_replication | true | bool | Replica ticket 0-RTT entre nodos del tenant |

#### 3.5 Namespaces Redis
| Namespace | TTL | Tipo | Descripcion |
|---|---|---|---|
| mpat:quic:ticket:{tenant_id} | 86400s | String | Session ticket 0-RTT — replicado entre nodos edge |
| mpat:edge:node:{node_id}:health | 30s | Hash | Estado de salud del nodo edge |

#### 3.6 Integraciones con otras capas
- CAPA_01 (QUICGateway): usa session tickets replicados por RES.132 para habilitar 0-RTT en nodos edge
- CAPA_09 (NHP): el NHP handshake ocurre en el nodo edge, no en el datacenter principal
- CAPA_14 (policy.yaml): seccion `edge.*` controla nodos, regiones y replicacion

#### 3.7 OTel spans definidos
- Span `edge.request.routed`: atributos: node_id, region, tenant_id, rtt_ms_to_primary
- Span `edge.session_ticket.replication`: atributos: tenant_id, source_node, target_node, success

#### 3.8 Nota para V3_02b
RES.132 impacta CAPA_00 solo indirectamente: el ChannelAdapter de cada nodo edge opera identicamente al del datacenter. El campo `transport` del UnifiedInput incluye el `edge_node_id` como atributo adicional para trazabilidad OTel.

---

## BRECHA 00-4 — DbC formal de ChannelAdapter

**Design-by-Contract: ChannelAdapter.adapt(raw_request)**
Precondicion: raw_request tiene estructura valida para el protocolo del canal (Telegram JSON, WhatsApp webhook, etc.). El protocolo fue identificado por la capa de red antes de llegar al ChannelAdapter.
Postcondicion: UnifiedInput parcial con raw_content extraido y platform_id asignado. Si el payload esta corrupto: request descartado con log — NUNCA UnifiedInput parcial propagado hacia PlatformDetector.
Invariante INV-CH.1: raw_content == contenido original del mensaje. Sin modificacion semantica, sin truncamiento, sin interpretacion.
Invariante INV-CH.3: payload corrupto → descarte silencioso con log. NUNCA propagar raw_content=None.

---

## NAMESPACES REDIS COMPLETOS — CAPA_00

Ninguno. CAPA_00 es completamente stateless. Todo estado de sesion comienza en CAPA_01.

---

*INFORME_CAPA_00_V3_02b · ariel.garcia.traba@gmail.com · 2026-05-19 · RELAY_029 BETA*
*que has usado el formato de razonamiento adaptado por AGT*
