# CAPA_07_MASTER_V4_00.md
## Capa 07 — Herramientas y Protocolos / MCP 2.0 / MCPAppsRenderer / PaymentDispatcher / RPCRouter / ToolRegistry
## Versión: V4_00 · Consolidación MPAT4
## Consolidado por: Claude Sonnet 4.6 · 2026-05-23
## Fuentes fusionadas:
##   - CAPA_07_MASTER_V3_02.md (2026-05-21, docente_AGT) — arquitectura conceptual, invariantes, integraciones
##   - PATCH_CAPA_07_TOOL_REGISTRY_V3_02.md (2026-05-19, cursos.agt) — implementación Python + tests de regresión
## RES activas: RES.080, RES.094, RES.095, RES.117, RES.128, RES.136, RES.152
## Relays origen: RELAY_001, RELAY_012, RELAY_015, RELAY_016
## Sistema: MPAT V4_00 — Infraestructura Cognitiva Distribuida

---

## 1. IDENTIDAD Y PROPÓSITO

CAPA_07 es el motor de ejecución de herramientas de MPAT. Media entre la intención
del Orchestrator (CAPA_03) y la ejecución concreta de skills, APIs, servicios externos,
UIs ricas y pagos automatizados.

**Principio rector:** P13 — AI Specifiers Rule. Toda herramienta que ingresa al ecosistema
debe presentar un contrato legible por máquina antes de ser invocada.

**Evolución V3_02 → V4_00:** de "llamadas a funciones" a "contratos de ejecución verificados".
El PATCH_TOOL_REGISTRY cierra la vulnerabilidad HITL-override de V3_01 e incorpora
la implementación de referencia con tests de regresión.

---

## 2. ARQUITECTURA — CUATRO SUBSISTEMAS

### 2.1 MCP 2.0 — Servidores de Skills (base, RELAY_001)

Todos los skills de MPAT se implementan como servidores MCP 2.0 independientes
comunicados via JSON-RPC 2.0. El Orchestrator conecta solo los servidores necesarios
por sesión, reduciendo contexto y consumo de tokens.

**Componentes:**

`ToolRegistry` (RES.117): registro central con búsqueda semántica lazy.
Invariante INV-7-REG-1: el Orchestrator NUNCA carga más de top_k=10 skills por sesión.
Superar este límite requiere HITL gate explícito.

`SkillValidationPipeline`: 3 etapas obligatorias antes de cualquier ejecución:
- Etapa 1 — Schema Validation: agent_card bien formado
- Etapa 2 — Trust Tier Assignment (0=core, 1=verificado, 2=externo, 3=experimental)
- Etapa 3 — Sandbox Check

Invariante INV-7-VAL-1: ningún skill de Tier 2 o 3 puede ejecutarse sin sandbox_ok=True.
Invariante INV-7-VAL-2: la validación es síncrona y previa a la ejecución. Sin "ejecución optimista".

`MPATSkillServer`: servidor MCP 2.0 base. Expone: tools, resources, prompts via JSON-RPC 2.0.
Soporta streaming SSE para herramientas de larga duración.
Invariante INV-7-STREAM-1: todo chunk de streaming debe incluir `tool` y `type`.

**Parámetros config:**

| Parámetro | Default | Rango | Descripción |
|---|---|---|---|
| registry_top_k | 5 | 1–10 | Skills máximos inyectados por sesión |
| registry_ttl_seconds | 3600 | 300–86400 | TTL de entradas en ToolRegistry |
| stream_chunk_timeout_ms | 5000 | 1000–30000 | Timeout por chunk de streaming |
| trust_tier_min_external | 2 | 1–3 | Trust mínimo para skills externos |
| sandbox_type | "docker" | docker/wasm/inmemory | Tipo de sandbox para Tier 2+ |

---

#### Implementación de referencia: ToolRegistry (patch_tool_registry_v3_02.py)

> **Nota de consolidación V4_00:** el PATCH del 2026-05-19 corrige la vulnerabilidad
> `set_override_top_k()` presente en V3_01, que permitía eludir INV-7-REG-1 via
> `hitl_override=True`. En V4_00 esa rama no existe. El límite se fija en construcción,
> una sola vez, y es inmutable durante la vida del objeto.

```python
"""
MPAT V4_00 — CAPA_07 — ToolRegistry
Consolidado: CAPA_07_MASTER_V3_02 + PATCH_TOOL_REGISTRY_V3_02
Fuentes: docente_AGT_2026 + cursos.agt@gmail.com

INV-7-REG.1 (CORREGIDO):
  top_k = min(policy.yaml.registry_top_k, 10). ABSOLUTO.
  No existe HITL gate ni override. set_override_top_k() ELIMINADO.

Design-by-Contract: ToolRegistry.search()
  Pre:  capability != "". top_k >= 1. Al menos 1 skill registrado.
  Post: len(resultado) <= min(top_k, _effective_top_k).
  INV:  _effective_top_k = min(registry_top_k, 10). Fijo en construcción.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from typing import Any

import redis


@dataclass
class AgentCard:
    skill_id: str
    name: str
    version: str
    capabilities: list[str]
    trust_tier: int = 2
    has_signature: bool = False
    origin: str = "external"
    embedding: list[float] = field(default_factory=list)


@dataclass
class RegistrySearchResult:
    cards: list[AgentCard]
    top_k_applied: int
    capability_queried: str


class ToolRegistry:
    """
    Catalogo centralizado de skills con busqueda semantica lazy.
    Thread-safe para uso concurrente en MAS (RES.095).
    INV-7-REG.1 aplicado en construccion — no en cada llamada.
    set_override_top_k() ELIMINADO en V3_02. No reinstaurar en V4.
    """

    _HARD_TOP_K_LIMIT: int = 10  # techo absoluto — no configurable

    _NS_CARD      = "mpat:registry:{skill_id}"
    _NS_SEARCH    = "mpat:registry:search:{capability_hash}"
    _NS_EMBEDDING = "mpat:registry:embedding:{skill_id}"

    def __init__(
        self,
        redis_client: redis.Redis,
        registry_top_k: int,        # de policy.yaml
        registry_ttl_seconds: int,  # de policy.yaml
    ) -> None:
        if registry_top_k < 1:
            raise ValueError(f"registry_top_k debe ser >= 1: {registry_top_k}")

        # INV-7-REG.1 — aplicado UNA SOLA VEZ en construccion
        self._effective_top_k = min(registry_top_k, self._HARD_TOP_K_LIMIT)
        self._ttl  = registry_ttl_seconds
        self._redis = redis_client
        self._lock  = threading.RLock()  # RES.095

    # ----------------------------------------------------------------
    # Registro
    # ----------------------------------------------------------------

    def register(self, card: AgentCard) -> None:
        """
        Pre:  card.skill_id != "". card.capabilities no vacio.
        Post: card disponible para search() con TTL configurado.
        """
        if not card.skill_id:
            raise ValueError("AgentCard.skill_id no puede ser vacio")
        if not card.capabilities:
            raise ValueError("AgentCard.capabilities no puede estar vacio")

        key     = self._NS_CARD.format(skill_id=card.skill_id)
        payload = json.dumps({
            "skill_id":      card.skill_id,
            "name":          card.name,
            "version":       card.version,
            "capabilities":  card.capabilities,
            "trust_tier":    card.trust_tier,
            "has_signature": card.has_signature,
            "origin":        card.origin,
        })
        with self._lock:
            self._redis.set(key, payload, ex=self._ttl)
            if card.embedding:
                emb_key = self._NS_EMBEDDING.format(skill_id=card.skill_id)
                self._redis.set(emb_key, json.dumps(card.embedding), ex=86400)

    def deregister(self, skill_id: str, reason: str = "") -> None:
        with self._lock:
            self._redis.delete(self._NS_CARD.format(skill_id=skill_id))
            self._redis.delete(self._NS_EMBEDDING.format(skill_id=skill_id))

    # ----------------------------------------------------------------
    # Busqueda — INV-7-REG.1 aplicado
    # ----------------------------------------------------------------

    def search(self, capability: str, top_k: int) -> RegistrySearchResult:
        """
        Retorna los skills mas similares semanticamente a `capability`.

        INV-7-REG.1 (V4_00): el limite efectivo es _effective_top_k,
        calculado en construccion como min(registry_top_k, 10).
        No existe branch de override, HITL gate ni excepcion.
        """
        if not capability:
            raise ValueError("capability no puede ser vacio")
        if top_k < 1:
            raise ValueError(f"top_k debe ser >= 1: {top_k}")

        effective_k = min(top_k, self._effective_top_k)
        candidates = self._semantic_search_stub(capability, effective_k)

        return RegistrySearchResult(
            cards=candidates[:effective_k],  # doble garantia
            top_k_applied=effective_k,
            capability_queried=capability,
        )

    # ----------------------------------------------------------------
    # Stub semantico (PEND_07_01 — pendiente V4)
    # ----------------------------------------------------------------

    def _semantic_search_stub(
        self, capability: str, k: int
    ) -> list[AgentCard]:
        """
        Busqueda semantica sobre embeddings en Redis.
        PEND_07_01: implementacion real pendiente en V4.
        Retorna primeros k skills registrados (sin scoring).
        """
        results: list[AgentCard] = []
        with self._lock:
            cursor = 0
            while True:
                cursor, keys = self._redis.scan(
                    cursor=cursor, match="mpat:registry:*", count=100
                )
                for raw_key in keys:
                    key_str = (
                        raw_key.decode()
                        if isinstance(raw_key, bytes) else raw_key
                    )
                    if ":search:" in key_str or ":embedding:" in key_str:
                        continue
                    raw = self._redis.get(key_str)
                    if raw:
                        d = json.loads(raw)
                        results.append(AgentCard(
                            skill_id=d["skill_id"],
                            name=d["name"],
                            version=d["version"],
                            capabilities=d["capabilities"],
                            trust_tier=d["trust_tier"],
                            has_signature=d["has_signature"],
                            origin=d["origin"],
                        ))
                    if len(results) >= k:
                        break
                if cursor == 0 or len(results) >= k:
                    break
        return results[:k]
```

**Tests de regresión INV-7-REG.1** — deben pasar en V4:

```python
# ANTES (V3_01 — comportamiento INCORRECTO, eliminado):
# registry.search("analizar", top_k=15, hitl_override=True) → 15 cards
# VIOLA INV-7-REG.1. hitl_override no existe en V4.

def test_top_k_hard_limit():
    registry = ToolRegistry(redis, registry_top_k=5, registry_ttl_seconds=3600)
    result = registry.search("analizar", top_k=15)
    # top_k solicitado=15, effective_top_k=min(5,10)=5
    assert len(result.cards) <= 5
    assert result.top_k_applied == 5

def test_top_k_policy_yaml_capped():
    # registry_top_k en policy.yaml puede ser > 10, pero el techo es 10
    registry = ToolRegistry(redis, registry_top_k=20, registry_ttl_seconds=3600)
    result = registry.search("analizar", top_k=20)
    assert result.top_k_applied == 10  # min(20, 10) = 10
```

---

### 2.2 MCPAppsRenderer — UI Rica via SEP-1865 (RELAY_012, FUT-7-D)

Permite a los agentes retornar componentes HTML/React interactivos en lugar de solo texto.
Implementa el protocolo SEP-1865: registro de recursos ui://, validación, renderizado,
comunicación bidireccional via JSON-RPC postMessage, y degradación graceful.

**Componentes:**

`MCPAppResource`: recurso UI registrado. Invariante INV-7D-005: `firewall_cleared` es
INMUTABLE una vez seteado a True. Si el HTML cambia: crear nuevo MCPAppResource con nuevo URI.

`UISession` + `UISessionStore`: sesión activa de UI persistida en Redis con TTL.
Invariante INV-7D-007: session_id es UUID v4 único global. Nunca reutilizar.
Invariante INV-7D-008: toda UISession vive en Redis con TTL. Nunca solo en memoria.
Invariante INV-7D-009: UISession.state es el único estado autorizado del componente.

`MCPAppsRenderer`: componente principal. Orquesta registro, validación de Firewall,
creación de sesión, entrega via CAPA_13, y degradación a texto si algo falla.
Invariante INV-7D-001: NUNCA marcar firewall_cleared sin inspección real del SemanticFirewall.
Invariante INV-7D-002: len(active_sessions) < max_concurrent_ui.
Invariante INV-7D-006: mcp_apps.enabled debe ser True para renderizar.
Invariante INV-7D-010: SIEMPRE retornar text_fallback si render() falla.

**Redis namespaces MCPAppsRenderer:**

| Clave | TTL | Tipo |
|---|---|---|
| mpat:ui:{tenant_id}:{session_id} | session_ttl_seconds | String (JSON) |
| mpat:ui:active:{tenant_id} | session_ttl_seconds | Set |

**Config mcp_apps.yaml:**

| Parámetro | Default | Rango |
|---|---|---|
| mcp_apps.enabled | false | bool |
| mcp_apps.max_concurrent_ui | 5 | [1, 50] |
| mcp_apps.session_ttl_seconds | 1800 | [60, 86400] |
| mcp_apps.max_html_size_kb | 512 | [1, 2048] |
| mcp_apps.sandbox_permissions | "" | string CSP |
| mcp_apps.firewall_check_required | true | NUNCA false en producción |

---

### 2.3 RPCRouter — JSON-RPC 2.0 Bidireccional (RELAY_016, DT-012-002 cerrado)

Reemplaza el stub de handle_rpc() de RELAY_012. Implementa routing real de mensajes
JSON-RPC 2.0 entre el iframe (UI) y el agente host.

**Métodos soportados:**

Categoría A (interacción UI): ui.ready, ui.click, ui.input, ui.submit, ui.navigate
Categoría B (tool calls desde UI): tool_call, tool_call.cancel
Categoría C (sincronización de estado): state.get, state.patch, session.ping, session.close

**Métodos PROHIBIDOS desde UI (lista negra P3 Zero-Trust):**
budget.*, system.*, payment.*, admin.*, capa.*

**Invariantes RPCRouter:**

| ID | Invariante |
|---|---|
| INV-RPC-1 | jsonrpc DEBE ser "2.0" exactamente |
| INV-RPC-2 | method no puede ser None ni vacío |
| INV-RPC-3 | id puede ser str/int/None. None = notificación sin respuesta |
| INV-RPC-4 | result y error son mutuamente excluyentes |
| INV-RPC-5 | id de la respuesta SIEMPRE coincide con id del request |
| INV-RPC-6 | Solo los métodos de METHOD_ROUTER son accesibles. Todo lo demás: METHOD_FORBIDDEN |
| INV-RPC-7 | tool_call: el tool_name debe estar en ToolRegistry del tenant |
| INV-RPC-8 | Notificaciones (id=None) no generan respuesta |
| INV-RPC-9 | state.patch no puede modificar claves privadas (_*) |
| INV-RPC-10 | RPCRouter NUNCA lanza excepción al caller. Toda excepción → RPCResponse de error |

---

### 2.4 PaymentDispatcher — x402 + MPP (RELAY_015, FUT-7-C)

Abstrae los dos protocolos de pago automatizado bajo una interfaz única para el Orchestrator.
El Orchestrator llama solo `pay_for_tool()` — no conoce el protocolo usado.

**Componentes:**

`BudgetAdapter`: adaptador USD → fracción para la API de CAPA_12 (que trabaja con fracciones).
Invariante INV-BA-1: la fracción calculada siempre es <= saldo disponible en ese momento.
Invariante INV-BA-2: si no hay suficiente, retorna None (no reservar).
Invariante INV-BA-3: si tenant_budget_total es 0 o desconocido: rechazar.

`X402PaymentProcessor`: ciclo HTTP 402 Payment Required via stablecoin (Coinbase Base/Ethereum).
Invariante INV-X402-1: amount_usd NUNCA supera MAX_PAYMENT_PER_CALL_USD (anti RIESGO-PD-05).
Invariante INV-X402-2: tx_hash único por transacción (anti replay).
Invariante INV-X402-3: debit ocurre SOLO tras retry exitoso con proof.
Invariante INV-X402-4: network debe estar en allowlist de policy.yaml.

`MPPPaymentProcessor` + `MPPSession`: sesiones preautorizadas para alta frecuencia.
Invariante INV-PD-4: MPPSession.spent NUNCA supera spending_limit_usd.
Invariante INV-MPP-1: session_id UUID único, nunca reutilizado.
Invariante INV-PD-7: tokens no usados SIEMPRE se devuelven al Budget al cerrar.

`PaymentDispatcher`: orquestador. Selector automático de protocolo (MPP si hay sesión activa
o monto >= threshold_mpp_usd; x402 para pagos esporádicos de bajo monto).
Invariante INV-PD-1: Budget check ANTES de cualquier pago.
Invariante INV-PD-2: ASL check ANTES de cualquier pago (pago es acción irreversible).
Invariante INV-PD-5: PaymentDispatcher NUNCA lanza excepción al caller.
Invariante INV-PD-6: PaymentResult SIEMPRE incluye tx_id único (P5 auditabilidad).

**Config payment.yaml:**

| Parámetro | Default | Descripción |
|---|---|---|
| payment.threshold_mpp_usd | "1.00" | Monto mínimo para usar MPP |
| payment.usd_to_tokens_ratio | 1000 | 1 USD = 1000 tokens presupuesto |
| payment.x402.network_allowlist | [base, ethereum, polygon] | Redes permitidas |
| payment.x402.max_payment_per_call_usd | "10.00" | Límite anti-manipulación de precio |

---

## 3. INTEGRACIÓN CON OTRAS CAPAS

| Capa | Relación con CAPA_07 |
|---|---|
| CAPA_03 (Orchestrator) | Invoca ToolRegistry.search() y ejecuta skills validados; llama pay_for_tool() |
| CAPA_04 (A2A) | Registra Agent Cards externas en ToolRegistry |
| CAPA_09 (Seguridad) | SemanticFirewall.inspect_html() para MCPAppsRenderer; ASL check para PaymentDispatcher |
| CAPA_10 (Observabilidad) | OTel spans de ui.rendered, ui.interaction, ui.tool_call, payment.* |
| CAPA_12 (Budget) | BudgetAdapter integra con budget.reserve/release/consume de CAPA_12 |
| CAPA_13 (Delivery) | MCPAppChannel en CAPA_13 es el canal de entrega de componentes UI |
| CAPA_14 (Config) | policy.yaml define top_k, trust_tier_min, quic_slo_ms, payment thresholds |

---

## 4. RESOLUCIONES APLICADAS

| RES | Descripción |
|---|---|
| RES.080 | Autonomous Benchmarking — pipeline de auto-evaluación de skills |
| RES.094 | Scheduler No-GIL — ejecución paralela de skills |
| RES.095 | Orquestación MAS — múltiples skills concurrentes sin bloqueo |
| RES.117 | Tool Registry dinámico — búsqueda semántica de skills |
| RES.128 | PolicyEnforcer V3 RBAC — integrado en SkillValidationPipeline |
| RES.136 | RBAC Ownership — PaymentDispatcher verifica ownership antes de pagar |
| RES.152 | MCPAppsRenderer V2 — versión canónica del renderer en V3_02 |

---

## 5. DEUDA TÉCNICA ACTIVA

| ID | Descripción | Prioridad | Origen |
|---|---|---|---|
| DT-016-001 | tool_call delegación real via SubQ al Orchestrator (actualmente stub) | ALTA | RELAY_016 |
| DT-015-001 | SDK x402 real (Coinbase/Cloudflare x402-python) | ALTA | RELAY_015 |
| DT-015-004 | Stripe MPP API real (STRIPE_MPP_API_KEY) | ALTA | RELAY_015 |
| DT-012-003 | OTel spans reales ui.interaction, ui.tool_call (actualmente logging) | MEDIA | RELAY_012 |
| DT-012-004 | Frontend postMessage real en cliente | ALTA | RELAY_012 |
| DT-015-003 | MPPSession persistencia en Redis con TTL | MEDIA | RELAY_015 |
| DT-016-003 | Rate limiting en handle_rpc() (max N RPCs/seg por sesión) | MEDIA | RELAY_016 |
| PEND_07_01 | _semantic_search_stub → implementación real con embeddings | ALTA | V4_00 |

---

## 6. PENDIENTES FUT (V4)

| FUT | Descripción |
|---|---|
| FUT-7-A | Self-Evolving Code: el sistema sugiere refactorizaciones en su propio código |
| FUT-7-B | Autonomous Benchmarking: generación de benchmarks propios para auto-evaluación |
| FUT-7-C | Micropagos x402: integración con Stripe for Agents / AWS Bedrock AgentCore Payments |
| FUT-7-D | SEP-1865 MCP Apps: UIs ricas — canal postMessage real en cliente |

---

## TRAMPA EDUCATIVA

**"El routing JSON-RPC es simplemente un if/elif sobre el method name"**

FALSO. El routing tiene tres capas no triviales:
1. Validación del envelope (jsonrpc, id, method, params bien formados).
2. Autorización: no todo método es accesible desde la UI (P3 Zero-Trust). Un iframe
   no puede llamar `system.shutdown` o `budget.debit` directamente.
3. Resultado vs Notificación: en JSON-RPC 2.0, mensajes sin `id` son notificaciones —
   no requieren respuesta. Mensajes con `id` requieren respuesta con el mismo `id`.
   Confundirlos viola el protocolo y genera timeouts silenciosos en el cliente.

INV-RPC-5, INV-RPC-8 e INV-RPC-10 cierran la trampa.

**"BudgetAdapter simplemente divide amount_usd / tenant_budget_total"**

FALSO. El `tenant_budget_total` puede cambiar entre la reserva y el pago si otro agente
del mismo tenant está gastando en paralelo. La solución correcta: reservar ANTES del pago
y calcular la fracción sobre el saldo disponible en el momento exacto de la reserva,
no sobre el total teórico. INV-BA-1 cierra la trampa.

---

*CAPA_07_MASTER_V4_00.md · MPAT V4_00 · 2026-05-23*
*Consolidado desde: CAPA_07_MASTER_V3_02 (docente_AGT) + PATCH_CAPA_07_TOOL_REGISTRY_V3_02 (cursos.agt)*
*Razonamiento de consolidación: el MASTER tenía la arquitectura conceptual e invariantes;
el PATCH tenía la implementación Python y los tests de regresión que cierran INV-7-REG.1.
Ambos eran necesarios — no eran redundantes. V4_00 los fusiona en un único artefacto.*
