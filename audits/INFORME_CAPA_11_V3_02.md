# INFORME_CAPA_11_V3_02.md
## Capa 11 — SubQ / Message Bus / Async Transport
## Autor: agt1973@gmail.com (docente) · cierre V3 · 2026-05-19
## Template: TEMPLATE_INFORME_CAPA_V3_01.md

*que has usado el formato de razonamiento adaptado por AGT*

---

## 1. Identificacion

| Campo | Valor |
|---|---|
| Capa | CAPA_11 |
| Nombre | SubQ — Message Bus / Async Transport Layer |
| Version | V3_02 |
| Autor | agt1973@gmail.com (docente) |
| Fecha | 2026-05-19 |
| RES mas reciente | RES.138 (SubQ extendido), RES.156 (FlowGRPO trigger via SubQ) |

---

## 2. Responsabilidad

**Que hace:**
- Provee el bus de mensajes asincrono entre componentes del sistema.
- Transporta tareas de CAPA_03 a CAPA_04 cuando el flujo es asincrono (no A2A directo).
- Transporta notificaciones de estado entre capas (SUBQ_NOTIFY streams QUIC).
- Recibe triggers de FlowGRPO (RES.156) para notificar ajuste de politica.
- Garantiza entrega at-least-once con deduplicacion por message_id.
- Gestiona colas por tenant con aislamiento (no cross-tenant leakage).

**Que NO hace:**
- No es el transport layer de red — CAPA_01 (QUIC/eBPF) es la capa de transporte.
- No toma decisiones de routing cognitivo — CAPA_03.
- No persiste mensajes a largo plazo — TTL configurable, maximo 24h.
- No aplica rate-limiting de paquetes — CAPA_01.
- No gestiona presupuesto — CAPA_12.

---

## 3. Componentes activos (V3_02)

| Componente | Descripcion |
|---|---|
| `SubQBroker` | Broker central. Gestiona colas por tenant. Deduplicacion por message_id. Entrega at-least-once. |
| `SubQConsumer` | Consumer registrado por capa. Lee de su cola de tenant. Confirma receipt. |
| `SubQProducer` | Productor de mensajes. Inyecta tenant_id y message_id automaticamente. |
| `SubQNotifyChannel` | Canal SUBQ_NOTIFY sobre QUIC streams (CAPA_01). Para notificaciones de baja latencia entre capas. Permite 0-RTT (INV-QUIC.5). |
| `GRPOTriggerConsumer` | Consumer especial para eventos grpo.policy_adjusted de CAPA_05. Notifica a consumidores registrados (CAPA_04). |

---

## 4. Resoluciones que la afectan

| RES | Descripcion | Invariante clave |
|---|---|---|
| RES.114 | SubQ v1 base | protocolo de cola inicial |
| RES.138 | SubQ extendido | deduplicacion, at-least-once, TTL por tenant |
| RES.156 | FlowGRPO trigger | GRPOTriggerConsumer para eventos grpo.policy_adjusted |

---

## 5. Invariantes criticos vigentes

| ID | Invariante | Nivel |
|---|---|---|
| INV-SUBQ.1 | Un mensaje de tenant A NUNCA es entregado a un consumer de tenant B. Aislamiento de colas por tenant es absoluto. | CRITICO |
| INV-SUBQ.2 | Deduplicacion por message_id: un mensaje con el mismo ID no es entregado dos veces dentro de la ventana de deduplicacion (TTL del mensaje). | ALTO |
| INV-SUBQ.3 | SubQBroker NUNCA descarta un mensaje sin registrar el descarte en CAPA_10. Descarte silencioso es violacion de trazabilidad. | ALTO |
| INV-SUBQ.4 | SUBQ_NOTIFY channels permiten 0-RTT (INV-QUIC.5 — streams de notificacion, no de tareas). AGENT_TASK channels siempre 1-RTT. | MEDIO |

---

## 6. Integracion con otras capas

**Recibe mensajes de:** CAPA_03 (tareas async), CAPA_05 (eventos grpo.policy_adjusted), CAPA_09 (alertas SemanticFirewall), cualquier capa que necesite comunicacion async.
**Entrega mensajes a:** CAPA_04 (tareas de agentes), CAPA_05 (GRPOTriggerConsumer), CAPA_10 (eventos de descarte/error de cola).
**Infraestructura:** Redis Streams (backend de SubQBroker). TTL por mensaje configurable en policy.yaml.

---

## 7. Deuda tecnica activa

| DT | Descripcion | Prioridad |
|---|---|---|
| DT-016-001 | tool_call delegation real via SubQ — paths legacy usan delegacion sincrona | MEDIA |

---

*INFORME_CAPA_11_V3_02.md · agt1973@gmail.com · 2026-05-19*
*que has usado el formato de razonamiento adaptado por AGT*
