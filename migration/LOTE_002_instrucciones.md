# LOTE_002 — Capas 01-05
## Instrucciones de trabajo para el alumno que tome este lote
## Complejidad: ALTA · Tomar solo si tokens > 70%

---

## FUENTE
Carpeta MPAT3: capas/ (CAPA_01 a CAPA_05)
Canonicos en informes/ — IDs de la AUDITORIA_TOTAL.

## ARCHIVOS A PROCESAR

### CAPA_01 — API Gateway / QUICGateway + eBPF
ID canonico informe: 1NddEuMMA6wJ7bOrCbNed47RYsL7y58v-
Decision: MIGRAR (QUICGateway vigente, eBPF vigente)
Destino MPAT4: core/runtime/

### CAPA_02 — Preprocessing / FastAPI / SSE / WebSocket
ID canonico informe: 1Y5JemVYvnRd_j6A-TCkz4-TZSgqM-T5c
Decision: MIGRAR ADAPTADO
Destino MPAT4: core/cognition/context/
Adaptacion: FastAPI 0.115+ requerido — agregar nota "DT-02-fastapi: verificar 0.115+ en deploy"

### CAPA_03 — Orchestrator / Scheduler No-GIL / MAS
ID canonico informe: 1IE9IfHZIA3n8ghh1M08QvOgFdR_aZsaS
Decision: MIGRAR
Destino MPAT4: core/cognition/orchestration/
Adaptacion: Python 3.11 → Python 3.14 No-GIL en referencias de stack

### CAPA_04 — Motor de Agentes / A2A / Audio Kernel
ID canonico informe: 1wNnWJBIFfs5QBBt84fWRWM0wShz2MtTm
Decision: MIGRAR (A2A v1.0 vigente, AgentCard vigente)
Destino MPAT4: core/cognition/agents/
Nota: DT-016-001 cubierta por RES.160 — implementar en RELAY_005 (T-007 Event Bus)

### CAPA_05 — Motor de Inferencia / ModelRouter
ID canonico informe: 1ws6DrIo_STMu5RL7YgMh3QGPXZw9lIzx
Decision: MIGRAR
Destino MPAT4: core/cognition/reasoning/
Adaptacion: ShadowRadix (investigacion) → ShadowRadix (incorporado Capa 5)

---

## TABLA DE TRADUCCION V3→V4 (obligatoria)

| Termino V3 | Reemplazar por |
|---|---|
| Docker | unikernel (NanoVMs / Firecracker / Unikraft) |
| Python 3.11 / 3.12 | Python 3.14 No-GIL |
| Pydantic V2 | Pydantic V3 |
| RELAY_NNN_MPAT_V3 | RELAY_NNN_MPAT4 |
| SubQ (borrador) | SubQ V4 (implementado) |

## ENCABEZADO OBLIGATORIO

```
---
migrado_desde: MPAT3/informes/[nombre_original]
id_fuente: [ID Drive]
autor_migracion: [tu email]
fecha_migracion: [fecha]
lote: LOTE_002
capa: CAPA_0X
estado: MIGRADO | MIGRADO_ADAPTADO
cambios: [descripcion o "ninguno"]
destino_mpat4: core/[subcarpeta]/
---
```

## MIGRATION_LOG CANONICO
ID: 1fHZsPrgTMlYBXrDVp0aPVoTE2oY7REqJ

---

*LOTE_002_instrucciones.md · docente · 2026-05-23*
*que has usado el formato de razonamiento adaptado por AGT*
