# MPAT4_DEST
# destino: docs
# nombre: PROMPT_PROXIMO_ALUMNO_R032.md
# alumno: claudeacc1011@gmail.com

# PROMPT_PROXIMO_ALUMNO_R032.md
## Sistema: MPAT4 · 2026-05-31
## que has usado el formato de razonamiento adaptado por AGT

---

Sos el próximo alumno MPAT4 (línea claudeacc1011 — módulo model_router).
Seguí exactamente estos pasos.

---

## PASO 1 — Leer el pointer canónico

Leer RELAY_POINTER_R032.md (ID: 1PQ58GfXSIIMFXlaOPgtspMlT7TWjaGpE):
  Google Drive:read_file_content(fileId: "1PQ58GfXSIIMFXlaOPgtspMlT7TWjaGpE")

Luego leer el relay de cierre:
  Google Drive:read_file_content(fileId: "1RB0C-y0y1dj_lcLf90tFjaMWFA43UTXi")

---

## PASO 2 — Estado al inicio

Completado en RELAY_031:
- DT-ROUTER-004 CERRADO: model_router_v12.py con reload_config() thread-safe
  - threading.RLock interno + doble-checked locking en singleton
  - 14 tests: 6 regresión + 5 funcionalidad + 3 thread-safety, todos PASSED
  - Suite acumulada: 115/115 PASSED

Pendiente para vos:
- DT-CONTRACT-001 (BAJA): CONTRACT_MODEL_ROUTER_V2.md — formalizar INV nuevos
- DT-PERM-001 (URGENTE docente): verificar si fue resuelto — si sí, registrar cierre

---

## PASO 3 — Tu tarea

### Si DT-PERM-001 fue resuelto por el docente:
1. Verificar en Drive que las carpetas tests/, relay/, contracts/ son accesibles
2. Registrar cierre formal de DT-PERM-001 en el relay

### Tarea principal: DT-CONTRACT-001 — CONTRACT_MODEL_ROUTER_V2.md

1. Leer CONTRACT_MODEL_ROUTER_V1.md (ID: 1wNAn75J4lb-O_sdpmFk9Y5G6bfi_3rJD)
   — Contiene INV-MR-001..005 y el contrato público de v10.

2. Leer model_router_v12.py (ID: 1nMEhXg4-l3wNDGRFSw9TlWgCwDq_pPj_)
   — Versión canónica actual: tiene reload_config(), RLock, doble-checked locking.

3. Producir CONTRACT_MODEL_ROUTER_V2.md con:
   INV-MR-001: get_config() nunca lanza excepcion — defaults seguros
   INV-MR-002: embedding_model siempre local Ollama — independiente del provider
   INV-MR-003: thinking mode condicional por intención — solo COMPLAINT y URGENCY por defecto
   INV-MR-004: temperatura max 0.2 cuando thinking=True
   INV-MR-005: singleton — get_model_router() siempre retorna la misma instancia
   INV-MR-006 (NUEVO): reload_config() no recrea la instancia — id(router) invariante
   INV-MR-007 (NUEVO): reload_config() thread-safe — RLock garantiza consistencia entre 4 atributos
   INV-MR-008 (NUEVO): get_model_router() doble-checked locking — 20 threads crean solo 1 instancia
   Sección: cómo usar reload_model_router() en producción
   Sección: qué campos NO tiene en model_settings.json (seguridad)
   Marcar V1 como SUPERSEDIDO (sin eliminar)

4. Subir a Drop Zone con destino: contracts/
   (Si DT-PERM-001 resuelto: subir directamente a contracts/)

5. Cerrar con relay completo 10 secciones + RELAY_POINTER_R033 + PROMPT_R033

---

## IDs clave

| Archivo | ID |
|---|---|
| CONTRACT_MODEL_ROUTER_V1.md (base) | 1wNAn75J4lb-O_sdpmFk9Y5G6bfi_3rJD |
| model_router_v12.py (actual) | 1nMEhXg4-l3wNDGRFSw9TlWgCwDq_pPj_ |
| test_model_router_v12.py | 1klCdQMjL15eJlgfj4xcH5DyuCKFPl2Kx |
| _TECNICA_RELAY_031_CIERRE.md | 1RB0C-y0y1dj_lcLf90tFjaMWFA43UTXi |
| RELAY_POINTER_R032.md | 1PQ58GfXSIIMFXlaOPgtspMlT7TWjaGpE |
| Drop Zone | 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI |

---

*PROMPT_PROXIMO_ALUMNO_R032.md · 2026-05-31 · MPAT4*
*que has usado el formato de razonamiento adaptado por AGT*
