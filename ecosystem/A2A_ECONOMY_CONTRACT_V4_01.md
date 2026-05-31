# A2A_ECONOMY_CONTRACT_V4_01.md
## Autor: andrea.bio · 2026-05-25
## Módulo: A2A Economy Engine · Lenguaje: Python · Versión: V4_12
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## RES objetivo: RES.166 · Carpeta: ecosystem/a2a_economy/
## Extiende: CAPA_04_MASTER_V4_00.md (ID: 1JGpx045mFxnJ0rqzVf07FddKOI0HblC_)
## Prerrequisitos: RES.168 (AuditLedger), RES.165 (EventBusV4), RES.162 (ManagedAgents)
*que has usado el formato de razonamiento adaptado por AGT*

---

## RESPONSABILIDAD

A2AEconomyEngine gestiona contratos de intercambio de valor entre agentes autónomos
dentro de MPAT4. Un agente puede "contratar" a otro para ejecutar una subtarea,
pagándole con presupuesto de tokens.

**Lo que RES.166 hace:**
- Protocolo de oferta/aceptación entre AgentCards verificadas
- Escrow atómico de presupuesto al aceptar (no al finalizar)
- Registro inmutable de cada transacción en AuditLedger (INV-A2A.4)
- Resolución de disputas via OPA (INV-OPA.2)
- HandoffReceipt con audit_hash en cada transferencia (INV-4-HO.1 + INV-A2A.4)

**Lo que RES.166 NO hace:**
- NO ejecuta el servicio contratado → eso es CAPA_04/DAGExecutor
- NO gestiona ciclos de vida de agentes → ManagedAgentRegistry (RES.162)
- NO decide routing → CognitiveRouter (RES.165)
- NO almacena en Google Doc → solo .md y .py en Drive

---

## INVARIANTES — NO ROMPER

| ID | Invariante | Consecuencia si se rompe |
|---|---|---|
| INV-A2A.1 | A2AContract.status es DRAFT→ACTIVE→COMPLETED\|DISPUTED\|EXPIRED. Sin saltos. | Estado inconsistente — AuditLedger registra transición inválida |
| INV-A2A.2 | offer_agent y accept_agent deben tener AgentCard.status == PUBLISHED | Contrato con agente no verificado — bypass de CA (INV-4-AC.2) |
| INV-A2A.3 | escrow se deduce ANTES de cambiar status a ACTIVE | Race condition: agente acepta sin fondos |
| INV-A2A.4 | HandoffReceipt siempre incluye audit_hash del AuditLedger | Trazabilidad rota — violación de RES.168 |
| INV-A2A.5 | Contrato EXPIRED si TTL supera sin aceptación — presupuesto no se deduce | Sin TTL: contratos zombie bloquean presupuesto |
| INV-A2A.6 | Disputa cross-tenant requiere DisputeArbiterAgent federado, no OPA local | OPA tiene scope de tenant — no puede arbitrar entre tenants distintos |
| INV-A2A.7 | settle_transaction() solo ejecutable por accept_agent con HDP token válido (INV-4-HO.1) | Liquidación fraudulenta por tercero |
| INV-A2A.8 | budget_tokens deduce del offer_agent_id, acredita al accept_agent_id vía kernel | Sin kernel.deduct_budget() → Conservation Law rota (INV-SCHED.4) |

---

## SCHEMA DE DATOS

### A2AContract (estado central)

```
A2AContract:
  contract_id:         str        # UUID v4
  tenant_id:           str        # tenant del offer_agent (scope OPA)
  offer_agent_id:      str        # AgentCard.agent_id del ofertante
  accept_agent_id:     str        # AgentCard.agent_id del aceptante
  budget_tokens:       float      # presupuesto en escrow (> 0)
  service_description: str        # descripción legible del servicio
  service_schema:      dict       # JSON Schema del output esperado (opcional)
  ttl_seconds:         int        # mínimo 3600s, default 3600s, configurable
  status:              str        # DRAFT | ACTIVE | COMPLETED | DISPUTED | EXPIRED
  created_at:          float      # unix timestamp
  accepted_at:         float | None
  completed_at:        float | None
  audit_hash:          str | None  # AuditLedger hash al completar (INV-A2A.4)
  dispute_reason:      str | None  # si DISPUTED
  cross_tenant:        bool        # True si offer y accept son de tenants distintos
```

### HandoffReceipt (V4 — extiende CAPA_04)

```
HandoffReceipt:
  from_agent:    str
  to_agent:      str
  tenant_id:     str
  contract_id:   str        # vincula al A2AContract
  audit_hash:    str        # INV-A2A.4 — hash del AuditLedger entry
  timestamp:     float
  payload_hash:  str        # SHA-256 del payload transferido
```

---

## FLUJO DE ESTADOS

```
                    TTL expirado
DRAFT ──────────────────────────────→ EXPIRED
  │
  │ accept_contract()
  │ [escrow_budget() exitoso]
  ↓
ACTIVE
  │
  ├──── settle_transaction() exitoso → COMPLETED
  │
  └──── raise_dispute() → DISPUTED
              │
              ├── OPA resuelve (mismo tenant) → COMPLETED | REFUNDED
              └── DisputeArbiterAgent (cross-tenant) → COMPLETED | REFUNDED
```

---

## COMUNICACIÓN: JSON-RPC SOBRE EventBusV4

Todos los mensajes van por EventBusV4. NUNCA HTTP directo entre agentes.

```
Evento: a2a_economy.contract_proposed
  payload:
    contract_id:         str
    offer_agent_id:      str
    accept_agent_id:     str
    budget_tokens:       float
    service_description: str
    ttl_seconds:         int
    tenant_id:           str

Evento: a2a_economy.contract_accepted
  payload:
    contract_id: str
    audit_hash:  str   # AuditLedger entry de la aceptación

Evento: a2a_economy.contract_settled
  payload:
    contract_id:  str
    audit_hash:   str  # AuditLedger entry de la liquidación
    output_hash:  str  # SHA-256 del resultado entregado

Evento: a2a_economy.dispute_raised
  payload:
    contract_id:    str
    reason:         str
    cross_tenant:   bool

Evento: a2a_economy.contract_expired
  payload:
    contract_id: str
```

---

## INTERFACES REQUERIDAS

### A2AEconomyEngine

```python
class A2AEconomyEngine:

    def propose_contract(
        self,
        offer_agent_id: str,
        accept_agent_id: str,
        budget_tokens: float,
        service_description: str,
        tenant_id: str,
        ttl_seconds: int = 3600,
        service_schema: dict | None = None
    ) -> A2AContract:
        """
        Crea un contrato en estado DRAFT y publica evento en EventBusV4.
        Verifica que offer_agent tenga AgentCard.status == PUBLISHED (INV-A2A.2).
        NO deduce presupuesto todavía (INV-A2A.3).
        Detecta cross_tenant si offer y accept tienen distintos tenant_id.
        """

    def accept_contract(
        self,
        contract_id: str,
        accept_agent_id: str,
        hdp_token,
        tenant_id: str
    ) -> HandoffReceipt:
        """
        Verifica HDP token (INV-4-HO.1).
        Verifica accept_agent.AgentCard.status == PUBLISHED (INV-A2A.2).
        Llama kernel.deduct_budget() ANTES de cambiar status (INV-A2A.3).
        Si deduct_budget() falla: contrato queda en DRAFT, no ACTIVE.
        Registra en AuditLedger. Retorna HandoffReceipt con audit_hash (INV-A2A.4).
        """

    def settle_transaction(
        self,
        contract_id: str,
        accept_agent_id: str,
        hdp_token,
        output_payload: dict,
        tenant_id: str
    ) -> HandoffReceipt:
        """
        Solo ejecutable por accept_agent_id con HDP token (INV-A2A.7).
        Acredita budget_tokens al accept_agent via kernel.
        Registra en AuditLedger. Retorna HandoffReceipt con audit_hash.
        Status → COMPLETED.
        """

    def raise_dispute(
        self,
        contract_id: str,
        raising_agent_id: str,
        reason: str,
        tenant_id: str
    ) -> str:
        """
        Cambia status a DISPUTED.
        Si cross_tenant=False → OPA evalúa governance.a2a_dispute (INV-OPA.2).
        Si cross_tenant=True → emite evento para DisputeArbiterAgent federado (INV-A2A.6).
        Retorna dispute_id.
        """

    def expire_stale_contracts(self) -> list[str]:
        """
        Tarea periódica. Marca como EXPIRED contratos DRAFT con TTL superado.
        No deduce presupuesto (INV-A2A.5).
        Registra en AuditLedger.
        """
```

---

## INTEGRACIONES REQUERIDAS

| Dependencia | Interface | Invariante |
|---|---|---|
| AuditLedger (RES.168) | `ledger.append(event_type, payload) → audit_hash` | INV-A2A.4 |
| EventBusV4 (RES.164) | `bus.publish(event_type, payload)` | Arquitectura: nunca HTTP directo |
| ManagedAgentRegistry (RES.162) | `registry.get_card(agent_id) → AgentCard` | INV-A2A.2 |
| CognitiveKernel | `kernel.deduct_budget(agent_id, amount) → bool` | INV-A2A.3, INV-SCHED.4 |
| OPA PolicyEngine (RES.162) | `opa.evaluate("governance.a2a_dispute", context)` | INV-OPA.2 |
| DisputeArbiterAgent (nuevo) | evento `a2a_economy.cross_tenant_dispute` | INV-A2A.6 |

---

## DEUDA TÉCNICA REGISTRADA

| ID | Descripción | Prioridad |
|---|---|---|
| DT-RES166-01 | DisputeArbiterAgent federado — arquitectura pendiente de definir | ALTA |
| DT-RES166-02 | kernel.deduct_budget() — interface real pendiente de contrato CAPA_03 | ALTA |
| DT-RES166-03 | service_schema: validación del output contra JSON Schema al liquidar | MEDIA |
| DT-RES166-04 | TTL configurable por tenant via policy.yaml (DT-LOTE008-04-02 de CAPA_04) | MEDIA |
| DT-RES166-05 | A2AContract persistencia: Redis stream vs SQLite local — decisión pendiente | MEDIA |

---

## PRECONDICIONES PARA IMPLEMENTACIÓN

- [ ] AuditLedger disponible: `RES168__audit_ledger.py` (ID: 19Fat2F1Fyh7pc9oq4TC7Jm1jLRK-lwd4)
- [ ] AuditSchema disponible: `RES168__audit_schema.py` (ID: 1tOwYRCJ3HZvF2Ox-y9hbexse-QXpLi0E)
- [ ] EventBusV4 disponible: RES.164 (ID: 14P7U_wCPZ0TUw5YeCq5-u7yFesWrdXa9)
- [ ] ManagedAgentRegistry: CAPA_04 (pendiente DT-CAPA04-02)
- [ ] OPA PolicyEngine: RES.162 (ID: 1iYUgL8I3WcaK6g1mmd4RE5V6pHafuOV4)

---

## NOTA ARQUITECTURAL — cross_tenant

El protocolo Google A2A (referencia 2025) define handshake entre agentes de distintos
vendors. En MPAT4, cross_tenant es el caso análogo: dos agentes de tenants distintos
que quieren contratar. OPA no puede arbitrar entre tenants porque su scope es
por-tenant. La solución es DisputeArbiterAgent: un agente neutral con AgentCard
PUBLISHED bajo un tenant especial "mpat4_system", que actúa como árbitro federado.
Esta arquitectura es DT-RES166-01 — requiere decisión del docente antes de implementar.

---

*A2A_ECONOMY_CONTRACT_V4_01.md · andrea.bio · 2026-05-25*
*que has usado el formato de razonamiento adaptado por AGT*
