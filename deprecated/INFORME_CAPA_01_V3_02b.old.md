# INFORME CAPA 01 — API Gateway / QUICGateway + eBPF
**Version fuente:** V3_02
**Alumno:** andrea.bio
**Fecha:** 2026-05-20
**Porcion RELAY_029:** BETA
**Basado en canonico:** 1Yub-mYbTtl_F7bhpeFwIcjGdPdhDcqt0
**RES que afectan esta capa:** RES.115, RES.139, RES.143, RES.155, RES.094, RES.157 (FORMALIZADA)
**Paradigma predominante:** IA Generativa y Agentica + Post-Automation Paradigm

## 1. Descripcion de la capa

CAPA_01 es la puerta de entrada autenticada del sistema MPAT. Recibe requests de CAPA_00, autentica JWT, valida el tenant, aplica rate-limiting, y encola el request hacia CAPA_02/03.

En V3_02, CAPA_01 incorpora el stack eBPF/QUIC (RES.155), reemplazando el endpoint HTTP/1.1 en el hot path. HTTP/1.1 permanece como fallback (P6).

Lo que NO hace: No interpreta semantica del request (CAPA_03), no gestiona estado del agente (CAPA_04/06), no aplica logica de orquestacion (CAPA_03), no gestiona memoria (CAPA_08).

## 2. Componentes de la capa

### 2.1 QUICGateway (V3_02 — RES.155)

StreamTypes definidos (RES.155 + RES.157):

| StreamType | Prioridad | Descripcion | RES |
|---|---|---|---|
| AGENT_TASK | normal/high/critical | Tarea nueva al Orchestrator | RES.155 |
| AGENT_RESULT | normal | Resultado al Delivery | RES.155 |
| SUBQ_NOTIFY | low | Notificacion SubQ asincrona | RES.155 |
| HEARTBEAT | low | Keepalive por stream | RES.155 |
| OTEL_SPAN | low | Exportacion spans OTel al colector (write-only) | RES.157 |

OTEL_SPAN: write-only hacia el colector. No acepta mensajes entrantes de agentes. No incluido en zero_rtt_allowed_stream_types (spans llevan tenant_id — riesgo replay en 0-RTT). Ver RES.157.md (ID: 1yz-tNYDFN4KLMIGYTz203Tw4iGHeMGXB).

**Design-by-Contract: QUICGateway**

```
Precondicion:  cert TLS 1.3 valido disponible en startup.
               policy.yaml cargado con transport.quic.* configurado.
               eBPFPacketFilter inicializado y verificado por kernel verifier.

Postcondicion: conexiones QUIC con TLS 1.3 integrado aceptadas.
               Streams clasificados por StreamType con prioridad correcta.
               HTTP/1.1 activo como fallback (P6).
               Spans OTel emitidos via OTEL_SPAN stream (RES.157).

Invariante INV-QUIC.1: TLS 1.3 integrado en todo handshake QUIC.
               Cert invalido → rechazo total + alerta CAPA_10.
Invariante INV-QUIC.2: stream failure es aislado. Nunca bloquea
               otros streams de la misma conexion QUIC.
Invariante INV-QUIC.5: 0-RTT solo para HEARTBEAT y SUBQ_NOTIFY.
               AGENT_TASK y OTEL_SPAN siempre 1-RTT completo.
```

Namespaces Redis:
| Namespace | TTL | Tipo | RES origen |
|---|---|---|---|
| `mpat:quic:session:{tenant_id}:{connection_id}` | 3600s | String (QUICConnectionState) | RES.155 |
| `mpat:quic:ticket:{tenant_id}` | 86400s | String (session ticket 0-RTT) | RES.155 |
| `mpat:quic:metrics:{tenant_id}:hourly` | 3600s | Hash (metricas streams) | RES.155 |

Invariantes criticos:
INV-QUIC.1: QUIC NUNCA opera sin TLS 1.3 integrado. Cert invalido → rechazo total.
INV-QUIC.2: Perdida de un stream NUNCA bloquea otros streams.
INV-QUIC.3: Una conexion NUNCA supera max_streams_per_connection activos.
INV-QUIC.5: 0-RTT SOLO para HEARTBEAT y SUBQ_NOTIFY. AGENT_TASK y OTEL_SPAN siempre 1-RTT.

### 2.2 eBPFPacketFilter (V3_02 — RES.155)

Opera en kernel space: rate-limiting por tenant sin context switch.

INV-EBPF.1: Programa eBPF NUNCA accede a memoria fuera del buffer del paquete. Kernel verifier lo garantiza en carga.
INV-EBPF.2: Recarga de programa eBPF es zero downtime.
INV-QUIC.4: BPF map de quotas NUNCA excede el budget del tenant. Orden: actualizar Redis PRIMERO, luego BPF map.
INV-QUIC.6: Si Redis no disponible durante sincronizacion BPF map, mantener ultimo valor conocido. NUNCA resetear a 0.

Namespaces Redis:
| Namespace | TTL | Tipo | RES origen |
|---|---|---|---|
| `mpat:ebpf:quota:{tenant_id}` | 60s | String (contador ventana) | RES.155 |

### 2.3 JWTValidator

INV-JWT.1: JWTValidator NUNCA deja pasar un request sin JWT valido hacia CAPA_02. Excepcion: /health y /metrics (policy.yaml).

Namespaces Redis:
| Namespace | TTL | Tipo | RES origen |
|---|---|---|---|
| `mpat:jwt:blacklist:{jti}` | jwt_expiry | String | base |

### 2.4 TenantRouter

INV-TENANT.1: CAPA_01 NUNCA encola un request hacia CAPA_02 sin tenant_id verificado y unikernel_id asignado. Tenant inexistente → 404 antes de CAPA_02.

Namespaces Redis:
| Namespace | TTL | Tipo | RES origen |
|---|---|---|---|
| `mpat:tenant:{tenant_id}:unikernel` | session | String (unikernel_id) | RES.115 |

### 2.5 RateLimiter (user space — Redis)

Complementa al eBPFPacketFilter. Ventana deslizante configurable en user space.

Namespaces Redis:
| Namespace | TTL | Tipo | RES origen |
|---|---|---|---|
| `mpat:rl:{tenant_id}:{window}` | window | String (contador) | base |

## 3. Trampas educativas

**Trampa educativa 1:**
La afirmacion "QUIC elimina la necesidad de TLS 1.3 — usa su propio cifrado nativo" es **FALSA**.
Respuesta correcta: QUIC encapsula TLS 1.3 dentro del handshake — no lo reemplaza. INV-QUIC.1 exige TLS 1.3 integrado. Un stream QUIC sin TLS 1.3 es rechazado por el eBPFPacketFilter antes de llegar al Gateway. La confusion ocurre porque QUIC y TLS 1.3 comparten el handshake en un solo viaje de red (1-RTT). En realidad: QUIC gestiona el transporte multiplexado; TLS 1.3 gestiona autenticacion y cifrado. Ambos son obligatorios e independientes.
Invariante que la cierra: INV-QUIC.1: QUIC NUNCA opera sin TLS 1.3 integrado. Cert invalido → rechazo total.

**Trampa educativa 2:**
La afirmacion "eBPF filtra en userspace, igual que un firewall de aplicacion — la ventaja es solo la velocidad" es **FALSA**.
Respuesta correcta: eBPF opera en kernel space. El paquete que no pasa el filtro eBPF NUNCA llega a userspace. Es la diferencia entre un portero en la puerta del edificio (kernel) vs en la puerta del departamento (userspace). El costo de CPU es radicalmente menor porque no hay context switch por paquete — el kernel verifier ejecuta el programa eBPF directamente en el path de recepcion. Un firewall de aplicacion en userspace ya pago el costo del context switch antes de poder decidir.
Invariante que la cierra: INV-EBPF.1: el programa eBPF opera en kernel space verificado. INV-QUIC.4: las quotas se actualizan en kernel space antes de que el paquete llegue a userspace.

## 4. Flujo de datos completo

```
UnifiedInput (de CAPA_00)
  => QUICGateway (o HTTP/1.1 fallback — P6)
       => eBPFPacketFilter [kernel space]: quota check
            - Si quota excedida: DROP + span ebpf.packet.filter
       => JWTValidator: si invalido → 401
       => TenantRouter: si tenant inexistente → 404
            unikernel_id adjuntado si OK
       => RateLimiter [Redis user space]: si exceeded → 429
  => CAPA_02 con request enriquecido

OTel spans: quic.connection.established, quic.stream.received,
ebpf.packet.filter, auth.jwt.validate, routing.tenant.assign
[via OTEL_SPAN stream → colector — RES.157]
```

## 5. Estado final de la capa en V3_02

**Componentes activos:** QUICGateway, eBPFPacketFilter, JWTValidator, TenantRouter, RateLimiter
**Invariantes vigentes:** INV-QUIC.1 a INV-QUIC.6, INV-EBPF.1/2, INV-JWT.1, INV-TENANT.1
**RES.157:** StreamType OTEL_SPAN incluido — FORMALIZADA (andrea.bio, RELAY_029)

## 6. Config files V3_02

| Seccion | Parametro | Default | Rango | Descripcion | RES |
|---|---|---|---|---|---|
| transport.quic | enabled | true | bool | Activa QUICGateway | RES.155 |
| transport.quic | max_streams_per_connection | 100 | int | Max streams por conexion | RES.155 |
| transport.quic | zero_rtt_enabled | true | bool | 0-RTT para HEARTBEAT/SUBQ_NOTIFY | RES.155 |
| transport.quic | session_ticket_ttl_seconds | 86400 | int | TTL session ticket 0-RTT | RES.155 |
| transport.quic | fallback_to_tcp | true | bool | Fallback HTTP/1.1 (P6) | RES.155 |
| transport.ebpf | quota_window_seconds | 60 | int | Ventana de quota en kernel | RES.155 |
| transport.ebpf | default_quota_packets_per_window | 10000 | int | Quota default por tenant | RES.155 |
| transport.ebpf | on_redis_unavailable | keep_last_known | string | Comportamiento si Redis falla | RES.155 |
| transport | otel_span_stream_enabled | true | bool | Activa StreamType OTEL_SPAN | RES.157 |
| transport | otel_span_stream_priority | "low" | string | Prioridad OTEL_SPAN | RES.157 |

## Checklist de calidad V3_02b

- [x] 2 trampas educativas en formato A
- [x] 1 bloque DbC formato B para QUICGateway
- [x] Namespaces Redis formato C para todos los componentes
- [x] StreamType OTEL_SPAN incluido — RES.157 FORMALIZADA
- [x] ALUMNO_ID (andrea.bio) y fecha (2026-05-20)
- [x] Nombre V3_02b

INFORME_CAPA_01_V3_02b.md | andrea.bio | 2026-05-20 | PORCION BETA | RELAY_029
Elevacion 8.0/10 → 9.5/10
que has usado el formato de razonamiento adaptado por AGT
