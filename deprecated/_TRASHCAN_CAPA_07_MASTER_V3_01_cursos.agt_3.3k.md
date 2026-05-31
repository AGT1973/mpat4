# CAPA_07_MASTER_V3_01.md
## MPAT — MCP 2.0 + Tool Registry + Skill Validation
### Version V3_01 · RELAY_001 · PORCION ALPHA cerrada
### Autor: cursos.agt@gmail.com · Fecha: 2026-05-21
### Fuente: INFORME_CAPA_07_V3_02b.md (ID: 190p7V-qO_wHg-3D-ujcHfRTBrz9Oiqt7)
### PATCH aplicado: INV-7-REG.1 CORREGIDO (RESOLUCION_PATCH_INV7REG1_V3_02.md)

---

## REGISTRO DE CIERRE ALPHA

| Campo | Valor |
|---|---|
| Porcion RELAY_029 | ALPHA |
| Capas | CAPA_07 + CAPA_14 |
| Alumno cierre | cursos.agt@gmail.com |
| Fecha cierre | 2026-05-21 |
| Calidad inicial | 7.0/10 |
| Calidad final | 9.5/10 |
| Informe V3_02b | ID: 190p7V-qO_wHg-3D-ujcHfRTBrz9Oiqt7 |
| PATCH codigo | ID: 1dCpxVfhbfgXep3tTjHVrxriDZytTttXQ |
| PATCH resolucion | ID: 1UHUEq8ujmH47yTbVr0zjvWZtrRCezN8p |

---

## BRECHAS CERRADAS EN ALPHA

| Brecha | Estado | Detalle |
|---|---|---|
| INV-7-REG.1 incorrecto (HITL gate) | CERRADO | top_k = min(registry_top_k,10) ABSOLUTO |
| RES.116 superficial | CERRADO | 8 subsecciones completas |
| RES.117 superficial | CERRADO | 8 subsecciones completas |
| RES.118 superficial | CERRADO | 8 subsecciones completas |
| DbC MCPToolValidator | CERRADO | Formato B con INV-7-VAL.1/2 |
| DbC ToolRegistry.search() | CERRADO | Formato B con INV-7-REG.1 corregido |
| Namespaces Redis | CERRADO | Tabla Formato C — 9 entradas |
| Trampas educativas | CERRADO | 4 en Formato A |

## COMPONENTES ACTIVOS V3_01

**§7.01 — MCP 2.0 Streaming (RES.116)**
- Transport SSE para herramientas de larga duracion
- INV-7-STREAM.1: cada chunk incluye `tool` y `type`
- Degradacion silenciosa — no interrumpe la sesion

**§7.02 — Tool Registry (RES.117)**
- Catalogo centralizado con busqueda semantica lazy
- INV-7-REG.1 (CORREGIDO): top_k = min(registry_top_k, 10). ABSOLUTO.
- NO existe HITL gate para exceder el limite

**§7.03 — Skill Validation Pipeline (RES.118)**
- Tres etapas: Schema → Trust Tier → Sandbox
- INV-7-VAL.1: Tier 2/3 requiere sandbox_ok=True. Sin excepciones.
- INV-7-VAL.2: validacion sincrona y previa. Sin ejecucion optimista.

## NAMESPACES REDIS (Formato C)

| Namespace | TTL | Tipo | RES |
|---|---|---|---|
| `mpat:registry:{skill_id}` | 3600s | String(JSON) | RES.117 |
| `mpat:registry:search:{capability_hash}` | 300s | List[JSON] | RES.117 |
| `mpat:registry:embedding:{skill_id}` | 86400s | String | RES.117 |
| `mpat:bench:{skill_id}:history` | 604800s | List[JSON] | RES.080 |
| `mpat:bench:{skill_id}:tier` | 3600s | String | RES.080 |
| `mpat:stream:{session_id}:{skill_id}:status` | 600s | String | RES.116 |
| `mpat:stream:{session_id}:{skill_id}:chunks` | 600s | List | RES.116 |
| `mpat:validation:{skill_id}:result` | 3600s | String | RES.118 |
| `mpat:validation:{skill_id}:sandbox_ok` | 1800s | String | RES.118 |

## DEUDA TECNICA ACTIVA

| ID | Descripcion | Estado |
|---|---|---|
| PEND_07_01 | ToolRegistry: busqueda semantica real (embeddings) | Pendiente V3_02 |
| PEND_07_02 | Trust Tier por historial de uso | Pendiente V3_02 |
| PEND_07_03 | _check_docker_or_wasm_available() sin implementar | Pendiente V3_02 |
| PEND_07_06 | RES.157 pendiente — StreamType OTEL_SPAN | RESUELTO (RES.157.md) |

---

*CAPA_07_MASTER_V3_01.md · cursos.agt@gmail.com · 2026-05-21 · ALPHA CERRADO*
*que has usado el formato de razonamiento adaptado por AGT*
