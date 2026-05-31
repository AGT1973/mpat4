---
migrado_desde: MPAT3/arquitectura/ARQUITECTURA_base_V3_03.md
id_fuente: 1maihtP8yxoVodu5b3QdzS89tzPzEyF02
autor_migracion: agt1973@gmail.com
fecha_migracion: 2026-05-23
lote: LOTE_001
estado: REFERENCIA_HISTORICA
cambios: |
  Archivado sin modificacion como referencia inmutable del ciclo V3_03.
  La version adaptada para V4 es ARQUITECTURA_base_V4_UNIF.md (ID: 1JlZPRoYVk33jy51Z_pk2yIFEP5wUrtnq).
  NO editar este archivo — es el punto de referencia del estado al cierre de V3.
destino_mpat4: docs/public/
nota: |
  V3_03 incorpora PATCH INC-03 (CAPA_9 con NHP/ASL/ZTS — RES.143) y
  PATCH INC-05 (CAPA_14 jerarquia dos niveles — RES.137).
  Es el ultimo estado canonico de V3 antes del salto a V4.
  Autores del patch: ariel.garcia.traba@gmail.com · 2026-05-18
---

# ARQUITECTURA_base_V3_03.md — REFERENCIA HISTORICA
## MPAT — My Personal Agents Team
## Version V3_03 — ARCHIVADA — Ver V4 en ARQUITECTURA_base_V4_UNIF.md
*que has usado el formato de razonamiento adaptado por AGT_2026*

> Este archivo es SOLO LECTURA. Es la referencia del estado V3 al momento del cierre.
> Para trabajar con la arquitectura V4: usar ARQUITECTURA_base_V4_UNIF.md (ID: 1JlZPRoYVk33jy51Z_pk2yIFEP5wUrtnq)

---

[CONTENIDO ORIGINAL PRESERVADO — leer desde fuente: ID 1maihtP8yxoVodu5b3QdzS89tzPzEyF02 en MPAT3/arquitectura/]

Cambios V3_03 respecto a V3_02:
- PATCH INC-03: CAPA_9 nombra explicitamente NHP Protocol, ASL-3, ZTS (RES.143 — cierra DT-017-002)
- PATCH INC-05: CAPA_14 documenta jerarquia de dos niveles de config files (RES.137 — cierra DT-017-003)
Autor del patch: ariel.garcia.traba@gmail.com · 2026-05-18

Principales diferencias que V4 incorpora sobre esta base:
- RES.155: QUICGateway + eBPF reemplaza API Gateway clasico en CAPA_01
- RES.156: Payment Dispatcher x402/Stripe MPP
- RES.157: QUICSpanExporter — observabilidad semantica LLM en CAPA_10
- RES.158: Namespace ECS incluye tenant_id (patron canonico V4)
- FlowGRPO: hint de tier de inferencia en CAPA_01 (FUT.40)
- AgentCard JSON-LD + ManagedAgents + A2AHandoffManager en CAPA_04 (FUT.41-43)
- Planner V4 en CAPA_03 (FUT.44)
- Python 3.13t No-GIL en produccion

*REFERENCIA_HISTORICA_ARQUITECTURA_V3_03.md · LOTE_001 · agt1973@gmail.com · 2026-05-23*
