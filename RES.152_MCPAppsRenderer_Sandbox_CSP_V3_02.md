# MPAT4_DEST
# destino: resoluciones
# nombre: RES.152_MCPAppsRenderer_Sandbox_CSP_V3_02.md
# alumno: agt1973@gmail.com

# RES.152 — Contrato formal: MCPAppsRenderer · Sandbox iframe + CSP
## MPAT V3_02 · CAPA_07
## 2026-05-31 · agt1973@gmail.com
## RES relacionadas: RES.116, RES.117, RES.118, RES.136, RES.151
## Capas afectadas: CAPA_07 (owner), CAPA_09 (SemanticFirewall — consumidor), CAPA_14 (config)
## Próxima RES disponible: RES.153

*que has usado el formato de razonamiento adaptado por AGT*

---

## 1. PROBLEMA

CAPA_07 en V3_02 permite a los agentes retornar componentes HTML/React interactivos
(MCPAppsRenderer, §1.2 de CAPA_07_MASTER_V3_02). Sin embargo, no existe un contrato
formal que especifique:

a) El ciclo de vida completo de una UISession y sus transiciones de estado.
b) El contrato de seguridad del sandbox iframe: qué atributos CSP son obligatorios,
   cuáles son invariantes inviolables, y cómo se integra con SemanticFirewall (CAPA_09).
c) Las precondiciones y postcondiciones del método render() de MCPAppsRenderer.
d) El protocolo postMessage bidireccional entre el iframe y el host.
e) La política de degradacion graceful cuando el sandbox no puede establecerse.

La ausencia de este contrato formal deja a los implementadores con invariantes
documentados en CAPA_07_MASTER pero sin especificación ejecutable de comportamiento
en error, secuencia de validación obligatoria, y ownership de cada verificación.

---

## 2. AUDITORÍA DE OWNERSHIP POR COMPONENTE

### 2.1 firewall_cleared — quién lo setea

Pregunta: "¿quién tiene autoridad para marcar que el HTML de un MCPAppResource
es seguro para renderizar?"

Propietario: CAPA_09 SemanticFirewall — es el componente que inspecciona el HTML.
CAPA_07 MCPAppsRenderer NO hace inspección propia. Solo consulta.
Razón: la inspección de contenido arbitrario (XSS, exfiltración, scripts maliciosos)
es responsabilidad del SemanticFirewall. Delegar esa decisión a CAPA_07 violaría
la separación de responsabilidades y el modelo de Zero Trust de CAPA_09.

INV-7D-001 ya lo expresa: "NUNCA marcar firewall_cleared sin inspección real del
SemanticFirewall." Este contrato lo formaliza como precondición ejecutable.

### 2.2 Atributos CSP del iframe — quién los define

Propietario: CAPA_14 (mcp_apps.yaml) para los valores de política.
              CAPA_07 MCPAppsRenderer para la aplicación en render().
Razón: los valores de CSP dependen del entorno de deployment (sandbox_level,
allow_scripts, allowed_origins). Hardcodearlos en el código viola INV-PE-2 pattern
(sin hardcoding — todo valor de cap proviene de configuración).

### 2.3 UISession — quién persiste, quién lee

Propietario de escritura: CAPA_07 MCPAppsRenderer (crea, actualiza, destruye).
Propietario de lectura: cualquier componente que necesite el estado actual de la UI.
Redis es la única fuente de verdad (INV-7D-008).
La memoria in-process es caché temporal — nunca fuente canónica.

### 2.4 Comunicación postMessage — quién valida el origen

Propietario: CAPA_07 MCPAppsRenderer en el handler del host.
El iframe no puede validar su propio origen (es el punto de entrada de ataques).
El host DEBE verificar event.origin contra allowed_origins antes de procesar.

---

## 3. DISEÑO FORMAL

### 3.1 Componentes y responsabilidades únicas

```
MCPAppResource
  Owner: CAPA_07
  ─────────────────────────────────────────────────
  uri: str               # ui://{tenant_id}/{resource_id}
  html_content: str      # HTML/React compilado
  firewall_cleared: bool # INMUTABLE una vez True (INV-7D-005)
  content_hash: str      # SHA-256 del html_content en el momento de clearance
  created_at: float      # Unix timestamp — para TTL audit

UISession
  Owner: CAPA_07
  ─────────────────────────────────────────────────
  session_id: str        # UUID v4 — ÚNICO GLOBAL (INV-7D-007)
  tenant_id: str
  resource_uri: str
  state: dict            # Estado autorizado del componente (INV-7D-009)
  created_at: float
  last_active: float
  status: Literal["active", "suspended", "destroyed"]

MCPAppsRenderer
  Owner: CAPA_07
  ─────────────────────────────────────────────────
  render(resource, tenant_id) -> RenderResult
  send_event(session_id, event) -> bool
  destroy_session(session_id) -> None
  _build_iframe_html(resource, session_id, csp_policy) -> str [privado]

SemanticFirewall (Protocol — consumido por MCPAppsRenderer)
  Owner: CAPA_09
  ─────────────────────────────────────────────────
  inspect_html(html_content: str, tenant_id: str) -> FirewallResult
```

### 3.2 Protocolo SEP-1865 — Ciclo de vida completo

```
Agente genera HTML/React
        │
        ▼
[1] Registrar MCPAppResource
    uri = ui://{tenant_id}/{resource_id}
    firewall_cleared = False
        │
        ▼
[2] SemanticFirewall.inspect_html(html_content, tenant_id)
    → FirewallResult(cleared=bool, reason=str, blocked_patterns=list)
    SI cleared=False: retornar text_fallback INMEDIATAMENTE (INV-7D-010)
    SI cleared=True: continuar
        │
        ▼
[3] MCPAppResource.firewall_cleared = True  ← SOLO AQUÍ
    MCPAppResource.content_hash = SHA-256(html_content)
    (INV-7D-005: INMUTABLE a partir de este punto)
        │
        ▼
[4] Crear UISession (UUID v4, Redis, TTL=session_ttl_s)
    INV-7D-007: session_id es UUID v4 único global
    INV-7D-008: persistir en Redis ANTES de retornar al caller
        │
        ▼
[5] _build_iframe_html(resource, session_id, csp_policy)
    → HTML con sandbox iframe + atributos CSP de mcp_apps.yaml
        │
        ▼
[6] Retornar RenderResult(
        session_id,
        iframe_html,
        text_fallback   ← SIEMPRE presente (INV-7D-010)
    )
```

### 3.3 Design-by-Contract: MCPAppsRenderer.render()

```
Precondición:
  1. mcp_apps.enabled == True en mcp_apps.yaml (INV-7D-006)
  2. len(active_sessions[tenant_id]) < max_concurrent_ui (INV-7D-002)
  3. resource.firewall_cleared == True
     (garantizado por [2]-[3] del ciclo de vida — nunca asumir)
  4. resource.content_hash == SHA-256(resource.html_content)
     (detecta modificación post-clearance)
  5. RBACChecker.check_permission(tenant_id, "ui:render", "execute")
     → RBACResult.allowed == True
     (RES.136 §3 — autorización de renderizado)

Postcondición si todas las precondiciones pasan:
  - Retorna RenderResult con iframe_html y session_id válidos
  - UISession persiste en Redis (INV-7D-008)
  - UISession.state == {} (estado inicial vacío)
  - active_sessions[tenant_id] incrementado en 1

Postcondición si cualquier precondición falla:
  - Retorna RenderResult con iframe_html=None y text_fallback con motivo
  - NO lanza excepciones (degradación graceful — INV-7D-010)
  - NO persiste UISession
  - active_sessions[tenant_id] no cambia

Invariante transversal:
  - render() NUNCA lanza. Toda condición de error → text_fallback.
  - render() NUNCA modifica resource.firewall_cleared.
  - render() NUNCA bypasea la verificación de content_hash.
```

### 3.4 Sandbox iframe — Atributos CSP obligatorios

```
Nivel de sandbox definido en mcp_apps.yaml: sandbox_level ∈ {strict, standard, permissive}

sandbox_level=strict (default recomendado):
  sandbox="allow-scripts allow-same-origin"
  CSP: "default-src 'none'; script-src 'nonce-{nonce}'; style-src 'unsafe-inline'"
  allow="": vacío — sin acceso a cámara, micrófono, geolocalización, etc.
  referrerpolicy="no-referrer"

sandbox_level=standard:
  sandbox="allow-scripts allow-same-origin allow-forms"
  CSP: "default-src 'self'; script-src 'nonce-{nonce}' 'strict-dynamic'"
  allow="": vacío

sandbox_level=permissive (requiere justificación en audit log):
  sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
  CSP: configurable vía allowed_csp_directives en mcp_apps.yaml

INV-7D-CSP-1: el nonce CSP es ÚNICO POR SESIÓN — generado en _build_iframe_html(),
  nunca reutilizado entre sesiones.
INV-7D-CSP-2: sandbox_level=permissive requiere que RBACChecker confirme
  check_permission(tenant_id, "ui:permissive_render", "execute") → allowed=True.
INV-7D-CSP-3: el atributo sandbox del iframe NUNCA puede omitirse.
  Un iframe sin sandbox=... tiene acceso completo al DOM del host — violación crítica.
```

### 3.5 Protocolo postMessage bidireccional

```
Mensajes del iframe hacia el host:
  { "type": "ui_event", "session_id": str, "payload": dict }
  { "type": "ui_state_update", "session_id": str, "state": dict }
  { "type": "ui_ready", "session_id": str }
  { "type": "ui_error", "session_id": str, "error": str }

Mensajes del host hacia el iframe:
  { "type": "host_event", "session_id": str, "payload": dict }
  { "type": "host_destroy", "session_id": str }

Validación OBLIGATORIA en el handler del host (antes de procesar):
  1. event.origin ∈ allowed_origins (mcp_apps.yaml)
  2. message.session_id existe en UISessionStore
  3. UISession.status == "active"
  4. message.type ∈ tipos conocidos

Si cualquier validación falla:
  - Descartar mensaje silenciosamente
  - Incrementar contador mpat:ui:suspicious:{tenant_id} en Redis
  - Log WARNING con event.origin y session_id

INV-7D-PM-1: el host NUNCA ejecuta código del iframe directamente.
  Solo lee el payload y actualiza UISession.state.
INV-7D-PM-2: UISession.state se actualiza en Redis ANTES de procesar
  el evento en la lógica de negocio.
```

### 3.6 Degradación graceful — árbol de decisión

```
render() llamado
    │
    ├─ mcp_apps.enabled=False → text_fallback: "UI rendering disabled"
    │
    ├─ max_concurrent_ui alcanzado → text_fallback: "Max concurrent UI sessions reached"
    │
    ├─ firewall_cleared=False → text_fallback: "Content blocked by SemanticFirewall"
    │
    ├─ content_hash mismatch → text_fallback: "Content integrity violation"
    │
    ├─ RBAC denied → text_fallback: "Insufficient permissions for UI rendering"
    │
    ├─ Redis no disponible → text_fallback: "Session storage unavailable"
    │
    └─ Excepción inesperada → text_fallback: "UI rendering error — text mode active"
                              + log ERROR con traceback
```

---

## 4. INVARIANTES CANÓNICOS RES.152

| ID | Enunciado | Severidad |
|---|---|---|
| INV-7D-001 | firewall_cleared NUNCA se setea sin inspección real de SemanticFirewall | CRÍTICO |
| INV-7D-002 | len(active_sessions[tenant_id]) < max_concurrent_ui siempre | ALTO |
| INV-7D-003 | — (reservado) | — |
| INV-7D-004 | — (reservado) | — |
| INV-7D-005 | firewall_cleared es INMUTABLE una vez True. Cambio de HTML → nuevo MCPAppResource | CRÍTICO |
| INV-7D-006 | mcp_apps.enabled debe ser True para que render() proceda | ALTO |
| INV-7D-007 | session_id es UUID v4 único global. NUNCA reutilizar | CRÍTICO |
| INV-7D-008 | UISession persiste en Redis con TTL antes de retornar al caller | ALTO |
| INV-7D-009 | UISession.state es el único estado autorizado del componente. No hay estado en memoria | ALTO |
| INV-7D-010 | render() SIEMPRE retorna text_fallback. NUNCA lanza. NUNCA retorna None | CRÍTICO |
| INV-7D-CSP-1 | nonce CSP es único por sesión | ALTO |
| INV-7D-CSP-2 | sandbox_level=permissive requiere RBAC check adicional | ALTO |
| INV-7D-CSP-3 | El atributo sandbox del iframe NUNCA puede omitirse | CRÍTICO |
| INV-7D-PM-1 | El host NUNCA ejecuta código del iframe directamente | CRÍTICO |
| INV-7D-PM-2 | UISession.state se persiste en Redis antes de procesar el evento | ALTO |

---

## 5. NAMESPACES REDIS

| Namespace | TTL | Tipo | Descripción |
|---|---|---|---|
| `mpat:ui:{tenant_id}:{session_id}` | session_ttl_s | String(JSON) | UISession completa |
| `mpat:ui:active:{tenant_id}` | session_ttl_s | Set | session_ids activos por tenant |
| `mpat:ui:suspicious:{tenant_id}` | 3600s | Counter | Mensajes postMessage inválidos |
| `mpat:ui:nonce:{session_id}` | session_ttl_s | String | Nonce CSP de la sesión |

session_ttl_s default: 1800s (30 min) — configurable en mcp_apps.yaml.

---

## 6. CONFIGURACIÓN — mcp_apps.yaml

| Parámetro | Default | Rango | Descripción |
|---|---|---|---|
| mcp_apps.enabled | false | bool | Kill switch global |
| mcp_apps.max_concurrent_ui | 5 | 1-50 | Sesiones activas por tenant |
| mcp_apps.session_ttl_s | 1800 | 60-86400 | TTL de UISession en Redis |
| mcp_apps.sandbox_level | strict | strict/standard/permissive | Nivel de sandbox iframe |
| mcp_apps.allowed_origins | [] | list[str] | Orígenes válidos para postMessage |
| mcp_apps.firewall_timeout_ms | 2000 | 100-10000 | Timeout para inspect_html() |
| mcp_apps.text_fallback_max_chars | 500 | 100-2000 | Longitud máx del text_fallback |

---

## 7. INTEGRACIÓN CON RES RELACIONADAS

| RES | Punto de integración |
|---|---|
| RES.116 | MCP 2.0 Streaming — MCPAppsRenderer puede usarse en combinación con tool calls de larga duración (el iframe hace polling via postMessage mientras el tool call está en curso) |
| RES.117 | ToolRegistry — MCPAppResource se registra como un tipo especial de AgentCard con mime_type="text/html+mpat-ui" |
| RES.118 | SkillValidationPipeline Etapa 3 (SandboxChecker) — verifica sandbox_ok para el recurso UI igual que para skills de Tier 2/3 |
| RES.136 | RBACChecker.check_permission(tenant_id, "ui:render", "execute") — precondición 5 de render() |
| RES.151 | RBACChecker formal — mismo Protocol que consume MCPAppsRenderer para RBAC check |

---

## 8. DEUDA TÉCNICA ABIERTA

| ID | Descripción | Prioridad |
|---|---|---|
| DT-7D-01 | Implementar MCPAppsRenderer.render() con DBC completo de esta RES | ALTA |
| DT-7D-02 | Implementar UISessionStore con Redis backend | ALTA |
| DT-7D-03 | Integrar SemanticFirewall.inspect_html() en el ciclo de vida | ALTA |
| DT-7D-04 | Suite de tests: INV-7D-001, INV-7D-005, INV-7D-010, INV-7D-CSP-3 como casos críticos | ALTA |
| DT-7D-05 | Implementar handler postMessage con validación de origen | MEDIA |

---

*RES.152_MCPAppsRenderer_Sandbox_CSP_V3_02.md · agt1973@gmail.com · 2026-05-31*
*Contrato formal generado en sesión R031 — sistema limpio post-sprint*
*que has usado el formato de razonamiento adaptado por AGT*
