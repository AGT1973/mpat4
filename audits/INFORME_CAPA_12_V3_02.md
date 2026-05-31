# INFORME_CAPA_12_V3_02.md
## Capa 12 — Multi-tenancy / Budget / VMAOVerifier
## Autor: agt1973@gmail.com (docente) · cierre V3 · 2026-05-19
## Template: TEMPLATE_INFORME_CAPA_V3_01.md

*que has usado el formato de razonamiento adaptado por AGT*

---

## 1. Identificacion

| Campo | Valor |
|---|---|
| Capa | CAPA_12 |
| Nombre | Multi-tenancy — Budget Manager / VMAOVerifier / A2A Dispatcher |
| Version | V3_02 |
| Autor | agt1973@gmail.com (docente) |
| Fecha | 2026-05-19 |
| RES mas reciente | RES.153 (P13 patch VMAOVerifier), RES.155 (eBPF rate-limiting por tenant) |

---

## 2. Responsabilidad

**Que hace:**
- Garantiza el aislamiento completo entre tenants (Conservation Law P7).
- Gestiona el presupuesto de tokens/requests por tenant.
- Verifica que los OrchestrationPlans VMAO cumplen P13 antes de despachar (VMAOVerifier).
- Gestiona el A2A Dispatcher: enruta tareas cross-tenant con verificacion P13.
- Sincroniza el budget consumido con BPF maps de eBPF via Redis (CAPA_01).
- Rechaza requests que superan el budget con BUDGET_EXCEEDED error.

**Que NO hace:**
- No gestiona la autenticacion del tenant — CAPA_09.
- No decide que modelo usar — CAPA_05.
- No gestiona el transporte de red — CAPA_01.
- No persiste el estado de sesion cognitiva — CAPA_06.
- No aplica politicas GRPO — CAPA_05.

---

## 3. Componentes activos (V3_02)

| Componente | Descripcion |
|---|---|
| `TenantBudgetManager` | Gestiona presupuesto por tenant en Redis. Operaciones atomicas: decrementar al consumir, incrementar al liberar. INV-P7.1. |
| `VMAOVerifier` | Verifica OrchestrationPlans VMAO: primero P13 (contratos), luego P7 (budget por nodo). INV-MT-P13.2. |
| `A2ADispatcher` | Despacha tareas cross-tenant. Verifica P13 del receptor antes de construir A2ADeliveryEnvelope. INV-MT-P13.1. |
| `BudgetSyncAgent` | Sincroniza budget consumido en Redis con BPF maps de CAPA_01. Orden: actualizar Redis PRIMERO, luego BPF map (INV-QUIC.4). |
| `TenantIsolationGuard` | Verifica que operaciones cross-tenant tengan autorizacion explicita. Rechaza con ISOLATION_VIOLATION si no hay permiso. |

---

## 4. Resoluciones que la afectan

| RES | Descripcion | Invariante clave |
|---|---|---|
| RES.115 | Unikernel por tenant | aislamiento de red por tenant en capa de red |
| RES.146 | VMAO DAGExecutor | VMAOVerifier verifica planes VMAO |
| RES.153 | P13 patches | INV-MT-P13.1/2/3 formalizados |
| RES.155 | Transport eBPF/QUIC | BudgetSyncAgent sincroniza con BPF maps; INV-QUIC.4 |
| RES.125 | P13 formal (renumerado) | base formal INV-MT-P13 |

---

## 5. Invariantes criticos vigentes

| ID | Invariante | Nivel |
|---|---|---|
| INV-P7.1 | Conservation Law: el budget total del tenant NUNCA se excede. Operacion de decremento atomica. Si budget insuficiente: BUDGET_EXCEEDED antes de ejecutar. | CRITICO |
| INV-QUIC.4 (heredado) | Orden de sincronizacion: actualizar Redis PRIMERO, luego BPF map. Nunca a la inversa. | CRITICO |
| INV-MT-P13.1 | A2A Dispatcher NUNCA construye A2ADeliveryEnvelope sin verificar contrato P13 del receptor. | CRITICO |
| INV-MT-P13.2 | VMAOVerifier NUNCA aprueba OrchestrationPlan con AgentTasks sin AgentCard PUBLISHED. | ALTO |
| INV-MT-P13.3 | Verificacion P13 siempre antes de P7. Si P13 falla: abort sin consumir budget. | ALTO |
| INV-ISO.1 | Un tenant NUNCA puede acceder a datos, colas o estado de otro tenant sin autorizacion explicita registrada en TenantIsolationGuard. | CRITICO |

---

## 6. Integracion con otras capas

**Consultado por:** CAPA_01 (TenantBudgetGuard antes de abrir stream QUIC), CAPA_03 (verifica budget antes de despachar plan), CAPA_04 (por nodo DAG via VMAOVerifier).
**Sincroniza con:** CAPA_01 (BudgetSyncAgent → BPF maps via Redis).
**Emite a:** CAPA_10 (spans de consumo de budget, BUDGET_EXCEEDED alerts, P13 violations).

---

## 7. Deuda tecnica activa

| DT | Descripcion | Prioridad |
|---|---|---|
| DT-012-003 | (ver documento DT activo V3_02) | BAJA — pasa a V4 |

---

*INFORME_CAPA_12_V3_02.md · agt1973@gmail.com · 2026-05-19*
*que has usado el formato de razonamiento adaptado por AGT*
