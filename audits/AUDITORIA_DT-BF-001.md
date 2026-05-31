# AUDITORIA_DT-BF-001.md
## Autor: claudeacc1011@gmail.com · 2026-05-29
## Modulo: aesp / budget · Version: V4_02
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## que has usado el formato de razonamiento adaptado por AGT

---

## 1. ALCANCE

Auditoría de la tarea DT-BF-001: BudgetFabric backend Redis.
Cubre diseño, implementación, tests y cumplimiento de invariantes.

---

## 2. INVARIANTES AUDITADOS

| INV | Descripción | Verificación | Estado |
|---|---|---|---|
| INV-BF-001 | consume() atómico thread-safe | T-BF-029..032: 50 threads concurrentes, resultado exacto | PASS |
| INV-BF-002 | Resets automáticos por periodo | _apply_resets() detecta cambio de día/semana/mes | PASS |
| INV-BF-003 | *_used nunca supera *_limit | min(used + amount, limit) — T-BF-007 clamp test | PASS |
| INV-BF-004 | get() fail-open | T-BF-001..003: nunca lanza, default si no existe | PASS |
| INV-BF-005 | Resets emiten aesp.budget.window_reset | _apply_resets() emite por cada tipo de reset | PASS |
| INV-AESP-006 | AESPEngine stateless | BudgetFabric es el único writer de BudgetWindow | PASS |
| INV-AESP-008 | Sin imports MPAT4 directos | Solo emit inyectado — T-MOCK-036 equivalente | PASS |
| INV-BF-006 | Backends intercambiables | T-BF-025..028: mismo escenario InMemory y Redis | PASS |

---

## 3. DECISIONES DE DISEÑO AUDITADAS

### 3.1 Por qué BudgetWindow está duplicado en budget_fabric.py

**Opción A:** Importar desde aesp_schema.py
**Opción B:** Duplicar la clase localmente

**Razonamiento:**
INV-AESP-008 prohíbe imports directos de módulos MPAT4. Si budget_fabric.py
importa de aesp_schema.py, cualquier cambio en el schema rompe budget_fabric
sin aviso. La duplicación es explícita y documentada — el comentario en el
código indica la condición bajo la cual migrar al import real.

**Decisión adoptada:** B — duplicación documentada.
**Estado:** RESUELTO. Sin conflicto de fuentes.

### 3.2 Por qué el lock está en BudgetFabric y no en RedisBudgetBackend

**Razonamiento:**
Redis es single-threaded en operaciones individuales, pero la secuencia
load→modify→save es una operación compuesta que no es atómica sin control
externo. Poner el lock en el Fabric garantiza atomicidad para cualquier
backend sin requerir transacciones Redis (MULTI/EXEC). Simplifica el
backend y centraliza la lógica de concurrencia.

**Decisión adoptada:** Lock en BudgetFabric, por agent_id.
**Estado:** RESUELTO. T-BF-029 verifica 50 threads sin pérdida.

### 3.3 TTL de 40 días en Redis

**Razonamiento:**
La ventana más larga es mensual (30 días). TTL = 40 días garantiza que
ninguna ventana activa expire durante el periodo. No hay configuración
de TTL infinito para evitar acumulación de claves huérfanas.

**Decisión adoptada:** DEFAULT_TTL_SECONDS = 40 * 24 * 3600.
**Estado:** RESUELTO.

### 3.4 setex → set(ex=) 

**Razonamiento:**
fakeredis marca setex como deprecado. La API moderna de redis-py usa
set(name, value, ex=ttl). Misma semántica, sin warning.

**Decisión adoptada:** set(name=..., value=..., ex=...).
**Estado:** RESUELTO. 32/32 sin warnings.

---

## 4. COBERTURA DE TESTS

| Clase | Tests | Resultado |
|---|---|---|
| TestGet | 4 | 4/4 PASS |
| TestConsume | 6 | 6/6 PASS |
| TestResetTransactions | 3 | 3/3 PASS |
| TestSetLimits | 3 | 3/3 PASS |
| TestRedisBudgetBackend | 8 | 8/8 PASS |
| TestBackendInterchange | 4 | 4/4 PASS |
| TestThreadSafety | 4 | 4/4 PASS |
| **TOTAL** | **32** | **32/32 PASS** |

Tiempo de ejecución: 0.76s

---

## 5. RIESGOS IDENTIFICADOS

| ID | Riesgo | Mitigación | Estado |
|---|---|---|---|
| RIESGO-BF-001 | Redis caído — save() propaga excepción | El caller (BudgetFabric) debe implementar circuit breaker o fallback a InMemory | PENDIENTE — DT-BF-002 |
| RIESGO-BF-002 | Acumulación de locks en _locks dict | Sin cleanup de agents inactivos — memoria crece con número de agentes únicos | PENDIENTE — DT-BF-003 |
| RIESGO-BF-003 | BudgetWindow duplicado puede desincronizarse de aesp_schema | Requiere proceso de sincronización al actualizar schema | PENDIENTE — DT-SCHEMA-001 |

---

## 6. VEREDICTO

DT-BF-001 APROBADO.
32/32 tests PASSED. Todos los INV verificados.
Riesgos identificados registrados como deuda técnica.

---

*AUDITORIA_DT-BF-001.md · claudeacc1011@gmail.com · 2026-05-29*
*que has usado el formato de razonamiento adaptado por AGT*
