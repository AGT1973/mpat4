# RES.170 — MCP 2.0 Providers para MPAT4
## Autor: ai.mpat.designer@gmail.com · 2026-05-26
## Módulo: providers/mcp/ · Lenguaje: Python 3.14 · Versión: V4_15
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Estado: APROBADA Y COMPLETADA

*que has usado el formato de razonamiento adaptado por AGT*

---

## 1. Problema que resuelve

MPAT4 V4 necesita integrar herramientas externas (Google Drive, sistemas de ficheros,
APIs de terceros) de forma uniforme, auditada y compatible con el protocolo MCP 2.0.

Sin esta resolución, cada módulo que necesita acceder a una herramienta externa
implementa su propia integración ad-hoc. El resultado es:
- Código duplicado entre módulos.
- Sin trazabilidad unificada de llamadas a herramientas.
- Sin registro central de qué herramientas están disponibles por tenant.
- Sin política de autorización consistente (cualquier módulo puede llamar a cualquier
  herramienta sin validación).

---

## 2. Decisión arquitectural

**MCP 2.0 (Model Context Protocol) como protocolo estándar de integración de herramientas.**

MCP define un contrato claro entre el agente (consumidor) y el servidor de herramienta
(proveedor): el servidor expone un endpoint de discovery, una lista tipada de tools con
sus schemas de entrada/salida, y un endpoint de invocación. El agente nunca llama
directamente a la herramienta — siempre pasa por el servidor MCP.

**Por qué MCP 2.0 en lugar de alternativas:**

| Alternativa | Problema |
|---|---|
| Llamadas directas a APIs | Sin trazabilidad, sin autorización central, sin discovery |
| LangChain tools | Dependencia externa pesada, no compatible con el stack V4 |
| Plugins propietarios | Vendor lock-in, sin estándar entre agentes |
| gRPC directo | Overhead de compilación, sin discovery dinámico |

MCP es el estándar emergente en 2026 para interoperabilidad agente-herramienta.
Es adoptado por Anthropic, OpenAI, y los principales frameworks de agentes.
MPAT4 adopta MCP como capa de providers para asegurar compatibilidad futura.

---

## 3. Arquitectura de la capa providers/mcp/

```
providers/
  mcp/
    mcp_schema.py       — Tipos Pydantic: MCPToolSchema, MCPRequest, MCPResponse, MCPError
    mcp_server_base.py  — Clase base abstracta MCPServer con discovery + invoke
    mcp_registry.py     — MCPRegistry: registro central de servidores MCP por tenant
    drive_mcp_server.py — Implementación concreta: Google Drive como servidor MCP
```

### Flujo de invocación

```
Agente (cognitive_kernel)
  → MCPRegistry.get_server(tenant_id, server_name)
  → MCPServer.discover_tools()  → lista de MCPToolSchema
  → MCPServer.invoke(MCPRequest) → MCPResponse

MCPRegistry
  → valida que el agente tiene autorización para ese servidor
  → emite evento "mcp.tool_invoked" via EventBus (INV-KERNEL.3)
  → registra latencia en observability
```

---

## 4. Contratos de interfaz

### MCPToolSchema (mcp_schema.py)
```python
class MCPToolSchema(BaseModel, frozen=True):
    name: str                    # Identificador único de la tool
    description: str             # Para el agente — qué hace la tool
    input_schema: dict           # JSON Schema del input
    output_schema: dict          # JSON Schema del output
    requires_auth: bool          # True si necesita credenciales del tenant
```

### MCPRequest (mcp_schema.py)
```python
class MCPRequest(BaseModel, frozen=True):
    tenant_id: str               # INV-SCHEMA-001: no vacío
    session_id: str
    tool_name: str
    call_id: str                 # UUID v4 — para deduplicación
    arguments: dict              # Según input_schema de la tool
    timestamp_utc: datetime      # INV-ET-002: siempre UTC
```

### MCPResponse (mcp_schema.py)
```python
class MCPResponse(BaseModel, frozen=True):
    call_id: str                 # Mismo call_id del request
    success: bool
    result: dict | None          # Si success=True
    error: MCPError | None       # Si success=False
    tokens_used: int             # Para deduct_budget() (INV-VSOCK.6)
    latency_ms: float
```

---

## 5. Invariantes

```
INV-MCP.1: MCPRegistry es el ÚNICO punto de acceso a servidores MCP.
  Ningún módulo llama directamente a MCPServer — siempre via Registry.

INV-MCP.2: toda invocación de tool genera un evento "mcp.tool_invoked"
  via EventBus (INV-KERNEL.3). Sin excepción.

INV-MCP.3: el call_id es UUID v4 único por invocación.
  El servidor MCP es idempotente: dos requests con el mismo call_id
  retornan el mismo resultado sin ejecutar la operación dos veces.

INV-MCP.4: MCPServer.invoke() nunca lanza excepción no capturada.
  Siempre retorna MCPResponse con success=False y MCPError en caso de falla.

INV-MCP.5: los tokens_used en MCPResponse son consumidos por deduct_budget()
  inmediatamente después de la respuesta (INV-VSOCK.6 heredado).

INV-MCP.6: discover_tools() es cacheado por tenant con TTL de 300 segundos.
  No se hace discovery en cada invocación — solo al instanciar o al expirar.
```

---

## 6. Artefactos completados

| Archivo | Tamaño | ID Drive | Autor | Fecha |
|---|---|---|---|---|
| mcp_schema.py | 5.4 KB | 1IN4lxwkB3EEird1mGL0YF0SS0YMBrM65 | backup45122021@gmail.com | 2026-05-25 |
| mcp_server_base.py | 7.1 KB | 1XBejKo7J1KyWamFaIJ5TrSiUwo5UP0XZ | backup45122021@gmail.com | 2026-05-25 |
| mcp_registry.py | 7.6 KB | 1_wAy9FcDj5gW2QT6EBKKlyy1gl5A0Kvb | backup45122021@gmail.com | 2026-05-25 |
| drive_mcp_server.py | 8.8 KB | 18vdZ7T4ZTfb0Eg7HOLZ5wQq2tmfNszB5 | backup45122021@gmail.com | 2026-05-25 |

Carpeta: providers/mcp/ (ID: 1Lxck_YrWELin8lXBD2E7ZohDmHsbT_t0)

---

## 7. Deuda técnica post-RES.170

| ID | Descripción | Prioridad |
|---|---|---|
| DT-MCP-001 | Tests unitarios para mcp_registry.py | ALTA |
| DT-MCP-002 | Implementar FileSystem MCP server (acceso local NanoVM) | MEDIA |
| DT-MCP-003 | Política de autorización MCP por tenant en OPA (T-005) | ALTA |
| DT-MCP-004 | Métricas OTel: latencia por tool, tokens por server | MEDIA |

---

## 8. Integración con otras resoluciones

| Resolución | Integración |
|---|---|
| RES.159 (Firecracker) | Los agentes en MicroVMs usan MCPRegistry para acceder a tools |
| T-003 (Cognitive Kernel) | KernelBridge.publish_event() emite mcp.tool_invoked |
| T-005 (OPA) | MCPRegistry consulta OPA para autorización por tenant |
| T-007 (EventBus) | Todos los eventos MCP pasan por EventBus |

---

*RES.170_MCP_PROVIDERS_V4.md · V4_15 · ai.mpat.designer@gmail.com · 2026-05-26*
*Resolución: APROBADA Y COMPLETADA*
*que has usado el formato de razonamiento adaptado por AGT*
