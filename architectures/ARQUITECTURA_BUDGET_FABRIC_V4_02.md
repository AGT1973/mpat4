# ARQUITECTURA_BUDGET_FABRIC_V4_02.md
## Autor: claudeacc1011@gmail.com · 2026-05-29
## Modulo: aesp / budget · Version: V4_02
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## que has usado el formato de razonamiento adaptado por AGT

---

## 1. VISIÓN GENERAL

BudgetFabric es el único componente del sistema MPAT4 que lee y escribe
el estado de presupuesto (BudgetWindow) de cada agente cognitivo.
Este documento describe su arquitectura interna en V4_02, que extiende
V4_01 (DT-AESP-004, InMemory) con soporte para backend Redis (DT-BF-001).

---

## 2. DIAGRAMA DE CAPAS

```
┌─────────────────────────────────────────────────────────┐
│  CALLER (AESPEngine / scheduler / tests)                │
│                                                         │
│  budget = fabric.get(agent_id)          [lectura]       │
│  fabric.consume(agent_id, amount)       [escritura]     │
│  fabric.reset_transactions(agent_id)   [mantenimiento]  │
└────────────────────┬────────────────────────────────────┘
                     │ inyección de dependencias
┌────────────────────▼────────────────────────────────────┐
│  BudgetFabric                                           │
│  ├── _meta_lock: Lock          (crear locks por agente) │
│  ├── _locks: dict[str, Lock]   (un lock por agent_id)   │
│  ├── _backend: BudgetBackend   (inyectado)              │
│  └── _emit: EmitFn             (inyectado)              │
│                                                         │
│  INV-BF-001: consume() atómico via lock por agent_id    │
│  INV-BF-002: _apply_resets() detecta cambio de período  │
│  INV-BF-003: min(used + amount, limit) — clamp          │
│  INV-BF-004: get() fail-open — default si no existe     │
│  INV-BF-005: cada reset emite aesp.budget.window_reset  │
└────────────────────┬────────────────────────────────────┘
                     │ interfaz abstracta BudgetBackend
          ┌──────────┴───────────┐
          │                      │
┌─────────▼──────┐    ┌──────────▼──────────┐
│ InMemoryBudget │    │ RedisBudgetBackend   │
│ Backend        │    │                      │
│                │    │ KEY: mpat4:budget:ID │
│ dict[str,      │    │ TTL: 40 días         │
│   BudgetWindow]│    │ Serialización: JSON  │
│                │    │ fail-open en load()  │
│ Tests / dev    │    │ Producción           │
└────────────────┘    └──────────────────────┘
                                │
                     ┌──────────▼──────────┐
                     │ redis.Redis          │
                     │ fakeredis.FakeRedis  │
                     │ (mismo contrato)     │
                     └─────────────────────┘
```

---

## 3. FLUJO DE consume() — OPERACIÓN CRÍTICA

```
consume(agent_id, amount)
│
├─ _agent_lock(agent_id)          ← lock por agente (INV-BF-001)
│
├─ backend.load(agent_id)         ← leer estado actual
│   └─ None → _default_window()  ← fail-open (INV-BF-004)
│
├─ _apply_resets(window)          ← resetear si cambió período
│   ├─ ¿cambió día?  → daily_used=0, txns=0, emit(window_reset, daily)
│   ├─ ¿cambió semana? → weekly_used=0, emit(window_reset, weekly)
│   └─ ¿cambió mes?  → monthly_used=0, emit(window_reset, monthly)
│
├─ new_daily   = min(used + amount, daily_limit)   ← INV-BF-003
├─ new_weekly  = min(used + amount, weekly_limit)
├─ new_monthly = min(used + amount, monthly_limit)
├─ new_txns    = txns + 1
│
├─ window = window.model_copy(update={...})  ← inmutable (frozen=True)
│
├─ backend.save(window)           ← persistir
│
└─ if daily_remaining < 20% → emit(aesp.budget.warning, payload)
```

---

## 4. DECISIONES ARQUITECTÓNICAS CLAVE

### 4.1 BudgetWindow frozen=True (inmutable)

Razón: Elimina bugs de estado compartido entre threads. Cada modificación
produce un nuevo objeto. El lock garantiza que solo un thread genera el
nuevo objeto a la vez para un agent_id dado.

### 4.2 Lock por agent_id, no lock global

Razón: Un lock global serializa todas las operaciones de todos los agentes.
Con lock por agent_id, agentes distintos operan en paralelo sin bloquearse.
El meta_lock solo se usa para crear el lock por agente — operación O(1) amortizada.

### 4.3 Backend como interfaz abstracta

Razón: Permite tests con InMemory y producción con Redis sin cambiar
BudgetFabric. Futuros backends (DynamoDB, PostgreSQL) siguen el mismo contrato.

### 4.4 emit inyectado, no importado

Razón: INV-AESP-008. BudgetFabric no importa el event bus — lo recibe como
parámetro. En tests se usa MockEmitter. En producción se pasa el bus real.
Elimina acoplamiento de imports y facilita testing aislado.

---

## 5. RELACIÓN CON OTROS MÓDULOS

```
AESPEngine (stateless)
  └── recibe BudgetWindow de BudgetFabric.get()
  └── NO persiste nada — INV-AESP-006

BudgetFabric (stateful owner)
  └── único writer de BudgetWindow — INV-AESP-006
  └── delega persistencia al backend inyectado

RedisBudgetBackend
  └── producción — DT-BF-001
  └── requiere Redis >= 6.0

InMemoryBudgetBackend
  └── tests y desarrollo local
  └── sin dependencias externas

MockEmitter (de TEMPORAL_mock_biometrics.py)
  └── captura eventos en tests
  └── misma firma que el bus real de producción
```

---

## 6. EXTENSIBILIDAD PLANIFICADA

| Tarea | Descripción | Impacto en arquitectura |
|---|---|---|
| DT-BF-002 | Circuit breaker Redis → fallback InMemory | Nuevo decorator o wrapper sobre BudgetFabric |
| DT-BF-003 | Cleanup de locks inactivos | WeakValueDictionary o TTL de locks |
| DT-SCHEMA-001 | Unificar BudgetWindow con aesp_schema | Remover duplicación cuando INV-AESP-008 permita import controlado |
| DT-COG-001 | LLM real via ModelRouter | No afecta BudgetFabric directamente |

---

*ARQUITECTURA_BUDGET_FABRIC_V4_02.md · claudeacc1011@gmail.com · 2026-05-29*
*que has usado el formato de razonamiento adaptado por AGT*
