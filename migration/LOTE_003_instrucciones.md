# LOTE_003 — Capas 06-10
## Instrucciones de trabajo para el alumno que tome este lote
## Complejidad: ALTA · Tomar solo si tokens > 70%
## ESTADO PARCIAL: CAPA_09 ya migrada por docente (2026-05-23)
## ID CAPA_09 en Drive: 1zUxctWskIitWbPlsR2U8rkgHDapVngXX

---

## FUENTE
Carpeta MPAT3: capas/ (CAPA_06 a CAPA_10)
Canonicos en informes/ — IDs de la AUDITORIA_TOTAL.

## ESTADO DE CADA CAPA

### CAPA_06 — Estado Cognitivo / RLHF / Multi-Expert
ID canonico informe: 1T6f9jbBuXijoMlA1eWuPX_Sm8wRW8pSM
Decision: MIGRAR (DT-06-01 cerrado por RES.159)
Destino MPAT4: core/cognition/kernel/
Verificar: DT-06-01 marcado CERRADO (namespace experts con tenant_id)
Estado: PENDIENTE

### CAPA_07 — MCP 2.0 / ToolRegistry / Skill Validation
ID canonico informe: 190p7V-qO_wHg-3D-ujcHfRTBrz9Oiqt7
Decision: MIGRAR
Destino MPAT4: core/cognition/agents/
Estado: PENDIENTE

### CAPA_08 — Dream Cycle / Hebbiano / RMH — REFERENCIA 10/10
ID canonico informe: 1IsmJH4-35F35lDSnZ9_5m3KRJm-_uBQZ
Decision: MIGRAR INTACTO — NO MODIFICAR NINGUNA LINEA
Destino MPAT4: core/memory/
Nota: Es el template de calidad. Solo agregar encabezado de procedencia.
Estado: PENDIENTE

### CAPA_09 — NHP Protocol / ZeroTrustSession / ASL-3
Decision: COMPLETADO
ID archivo migrado en Drive: 1zUxctWskIitWbPlsR2U8rkgHDapVngXX
Alumno que retome: registrar en MIGRATION_LOG ARCHIVOS_OK += 1 al tomar el lote.

### CAPA_10 — Monitoring / OTel / LongContext / NVFP4
ID canonico informe: 17Ssti1YleqYZz3chy2j97RLigflO1lvp
Decision: MIGRAR (OTel vigente, RES.157 OpenInference+QUIC vigente)
Destino MPAT4: core/observability/
Verificar: RES.157 referenciada (ID artefacto: 1nnkblb6tCdwfVnp-m0KLDTh9NKUH7Zac)
Estado: PENDIENTE

---

## TABLA DE TRADUCCION V3→V4 (obligatoria para capas pendientes)

| Termino V3 | Reemplazar por |
|---|---|
| Docker | unikernel (NanoVMs / Firecracker / Unikraft) |
| Python 3.11 / 3.12 | Python 3.14 No-GIL |
| Pydantic V2 | Pydantic V3 |
| RELAY_NNN_MPAT_V3 | RELAY_NNN_MPAT4 |

## ENCABEZADO OBLIGATORIO

```
---
migrado_desde: MPAT3/informes/[nombre_original]
id_fuente: [ID Drive]
autor_migracion: [tu email]
fecha_migracion: [fecha]
lote: LOTE_003
capa: CAPA_0X
estado: MIGRADO | MIGRADO_ADAPTADO
cambios: [descripcion o "ninguno"]
destino_mpat4: core/[subcarpeta]/
---
```

## CONTRASTE CONTRA CAPA_08
La CAPA_08 migrada en este lote es la referencia 10/10.
Usarla para contrastar CAPA_06, 07 y 10.

## MIGRATION_LOG CANONICO
ID: 1fHZsPrgTMlYBXrDVp0aPVoTE2oY7REqJ
Al tomar: marcar LOTE_003 EN_CURSO y sumar ARCHIVOS_OK = 1 (CAPA_09 ya migrada).

---

*LOTE_003_instrucciones.md · docente · 2026-05-23*
*que has usado el formato de razonamiento adaptado por AGT*
