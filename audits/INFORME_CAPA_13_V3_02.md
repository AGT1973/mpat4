# INFORME_CAPA_13_V3_02.md
## Capa 13 — Delivery Layer / Output Router
## Autor: agt1973@gmail.com (docente) · cierre V3 · 2026-05-19
## Template: TEMPLATE_INFORME_CAPA_V3_01.md

*que has usado el formato de razonamiento adaptado por AGT*

---

## 1. Identificacion

| Campo | Valor |
|---|---|
| Capa | CAPA_13 |
| Nombre | Delivery Layer — Output Router / Channel Adapter |
| Version | V3_02 |
| Autor | agt1973@gmail.com (docente) |
| Fecha | 2026-05-19 |
| RES mas reciente | RES.154 (Delivery Layer canonico — declaracion formal) |

---

## 2. Responsabilidad

**Que hace:**
- Es el punto de salida de todas las respuestas del sistema hacia el usuario final.
- Enruta la respuesta al canal correcto: browser, API, WhatsApp, Telegram, voz.
- Adapta el formato de la respuesta al canal de entrega (markdown → HTML, texto → audio TTS, etc.).
- Aplica rate-limiting de salida por tenant y por canal.
- Gestiona streaming de respuesta (chunks) para canales que lo soportan.
- Confirma entrega y registra receipt en CAPA_10.

**Que NO hace:**
- No genera la respuesta — eso es el modelo LLM a traves de CAPA_05.
- No gestiona autenticacion del canal — CAPA_09.
- No persiste el historico de respuestas — CAPA_08 (MemoriaEpisodica).
- No aplica politicas GRPO — CAPA_05.
- No gestiona el transporte de red hacia el sistema — CAPA_01 (QUIC/eBPF).

---

## 3. Componentes activos (V3_02)

| Componente | Descripcion |
|---|---|
| `OutputRouter` | Selecciona el ChannelAdapter correcto segun el canal del request original. Lee canal de ECS (CAPA_06). |
| `ChannelAdapter` | Interfaz base. Implementaciones: BrowserAdapter, APIAdapter, WhatsAppAdapter, TelegramAdapter, VoiceAdapter (TTS). |
| `StreamingDeliveryManager` | Gestiona entrega de chunks en streaming. Buffer configurable. Reintento automatico si canal temporalmente no disponible. |
| `DeliveryRateLimiter` | Rate-limiting de salida por tenant y por canal. Independiente del rate-limiting de entrada (CAPA_01). |
| `DeliveryReceiptLogger` | Registra confirmacion de entrega en CAPA_10. Si el canal no confirma en delivery_timeout_ms: registra delivery_unconfirmed. |

---

## 4. Resoluciones que la afectan

| RES | Descripcion | Invariante clave |
|---|---|---|
| RES.154 | Delivery Layer canonico | declaracion formal de CAPA_13 como capa de entrega |

---

## 5. Invariantes criticos vigentes

| ID | Invariante | Nivel |
|---|---|---|
| INV-DEL.1 | Toda respuesta entregada DEBE tener un DeliveryReceipt registrado en CAPA_10. Entrega sin traza es violacion de auditoria. | ALTO |
| INV-DEL.2 | OutputRouter NUNCA enruta a un canal distinto del canal de origen del request. El canal es inmutable durante el flujo de respuesta. | ALTO |
| INV-DEL.3 | StreamingDeliveryManager NUNCA descarta un chunk sin registrar el descarte en CAPA_10. | ALTO |
| INV-DEL.4 | DeliveryRateLimiter opera independientemente del eBPF rate-limiter de CAPA_01. Son capas distintas de control: red (CAPA_01) vs entrega de contenido (CAPA_13). | MEDIO |

---

## 6. Integracion con otras capas

**Recibe de:** modelo LLM (chunks de respuesta via CAPA_05/router), CAPA_06 (canal de destino en ECS).
**Envia a:** canal externo (browser, API, WhatsApp, etc.), CAPA_10 (DeliveryReceipts, alertas de entrega no confirmada).
**No tiene dependencia directa con:** CAPA_02, CAPA_03, CAPA_04, CAPA_07, CAPA_08, CAPA_09, CAPA_11, CAPA_12.

---

## 7. Deuda tecnica activa

Ninguna. RES.154 formaliza la capa. Sin FUTs abiertos en V3_02.

---

*INFORME_CAPA_13_V3_02.md · agt1973@gmail.com · 2026-05-19*
*que has usado el formato de razonamiento adaptado por AGT*
