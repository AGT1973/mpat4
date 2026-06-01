# INV_PERSIST_REGISTRY_V2.md
# Autor: cursos.agt.ia@gmail.com · 2026-05-28
# Módulo: persistence · Versión: V4_01
# Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
# Tipo: REGISTRO DE INVARIANTES — BudgetWindowPersistence
# Fuente: RESOLUCION_BUDGET_PERSISTENCE_SOTA_V1
# que has usado el formato de razonamiento adaptado por AGT

---

# Registro de Invariantes — BudgetWindowPersistence · V2

## ESTADO GLOBAL

| Total INV | ACTIVO | PENDIENTE_INV | OBSOLETO |
|-----------|--------|---------------|----------|
| 17 | 15 | 2 | 0 |

Cobertura: 22 tests — todos los INV ACTIVO tienen al menos 1 test.

---

## INVARIANTES — CONTRATO GENERAL

| ID | Descripción | Estado | Test |
|----|-------------|--------|------|
| INV-PERSIST-001 | BudgetWindowPersistence NUNCA modifica BudgetWindow. | ACTIVO | test_inv_persist_001 |
| INV-PERSIST-002 | save_strict() idempotente: delete + store. | ACTIVO | test_inv_persist_002 |
| INV-PERSIST-003 | load() retorna None si no existe estado previo. | ACTIVO | test_inv_persist_003 |
| INV-PERSIST-004 | NUNCA importa AESPEngine directamente. | ACTIVO | test_inv_persist_004 |
| INV-PERSIST-005 | Todos los errores capturados. load() fail-safe. | ACTIVO | test_inv_persist_005 |
| INV-PERSIST-006 | fragment_id determinista: aesp:budget:{tenant}:{agent} | ACTIVO | test_inv_persist_006 |

## INVARIANTES — ABC Y CONTRATO DE INTERFAZ

| ID | Descripción | Estado | Test |
|----|-------------|--------|------|
| INV-PERSIST-ABC-001 | BudgetWindowPersistence hereda de BudgetWindowRepository (ABC). | ACTIVO | test_hereda_de_abc |
| INV-PERSIST-ABC-002 | save() y save_strict() coexisten — compatibilidad con DT-AESP-004. | ACTIVO | test_save_strict_retorna_str |

## INVARIANTES — FRAGMENT_ID

| ID | Descripción | Estado | Test |
|----|-------------|--------|------|
| INV-PERSIST-FRAG-001 | Esquema aesp:budget:{tenant}:{agent} inmutable entre versiones. Cambios requieren migración. | ACTIVO | test_fragment_id_esquema |

## INVARIANTES — LOAD FAIL-SAFE

| ID | Descripción | Estado | Test |
|----|-------------|--------|------|
| INV-PERSIST-LOAD-001 | load() nunca raise. Retorna None ante cualquier excepción. | ACTIVO | FAILSAFE-LOAD-001/002/003 |
| INV-PERSIST-LOAD-002 | Hidratación validada: BudgetWindow(**data). model_construct() prohibido. | ACTIVO | test_hydrate_001 |

## INVARIANTES — SAVE FAIL-SOFT

| ID | Descripción | Estado | Test |
|----|-------------|--------|------|
| INV-PERSIST-SAVE-001 | save() fail-soft: nunca raise. Retorna False ante error. | ACTIVO | test_save_001 |
| INV-PERSIST-SAVE-002 | save() retorna True/False. | ACTIVO | test_save_003 |
| INV-PERSIST-SAVE-003 | Fallo loggea ERROR con agent_id, tenant_id, consumo actual, error_type. | ACTIVO | test_save_002 |
| INV-PERSIST-SAVE-004 | BudgetWindow en memoria es fuente de verdad. Persistencia best-effort. | ACTIVO | (documentado) |

## INVARIANTES — TTL Y CICLO DE VIDA

| ID | Descripción | Estado | Test |
|----|-------------|--------|------|
| INV-PERSIST-TTL-001 | TTL 7 días en MemoryFragment como red de seguridad. Ciclo de vida via delete(). | ACTIVO | test_ttl_001 |

## INVARIANTES — INMUTABILIDAD PROFUNDA

| ID | Descripción | Estado | Test |
|----|-------------|--------|------|
| INV-AESP-006-DEEP | BudgetWindow no debe tener list/set/dict. Usar tuple/frozenset. Test falla si se viola. | ACTIVO | test_deep_001 |

## INVARIANTES — CONCURRENCIA (PENDIENTE_INV)

| ID | Descripción | Estado | Test |
|----|-------------|--------|------|
| INV-PERSIST-CONC-001 | Atomicidad delegada a MemoryFabric backend. Este módulo no implementa WATCH/MULTI/EXEC. Comportamiento: last-write-wins. | PENDIENTE_INV | Sin test — verificar CONTRACT de MemoryFabric |

Condición de resolución: verificar CONTRACT de MemoryFabric para confirmar atomicidad.
Si no garantiza: diseñar save_atomic() antes de despliegue multi-instancia.

---

## REGLAS DE MODIFICACIÓN

1. Agregar INV requiere: descripción, estado, test.
2. OBSOLETO requiere: razón y versión documentadas.
3. PENDIENTE_INV requiere: condición de resolución explícita.
4. Nunca eliminar — solo marcar OBSOLETO.
5. Si cambia descripción: nota de conciliación obligatoria.

---

*INV_PERSIST_REGISTRY_V2.md · MPAT4 · 2026-05-28*
*que has usado el formato de razonamiento adaptado por AGT*
