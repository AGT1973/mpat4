---
name: python-rust-production
version: V1_00
description: >
  Skill de produccion de codigo multilenguaje para MPAT4. Activar cuando el alumno
  diga 'escribir codigo', 'implementar modulo', 'crear parser', 'crear codec',
  'implementar en rust', 'bridge ffi', 'hot path', 'implementar en python',
  o cuando la skill mpat4-relay indique que el siguiente paso es implementacion.
  Clasifica el modulo por lenguaje, genera el artefacto correcto en el orden
  correcto (contrato → types/schema → impl → tests → FFI si aplica), y lo guarda
  en la carpeta correcta de Drive.
  NUNCA escribir codigo sin contrato aprobado.
  NUNCA cruzar la frontera Python-Rust sin un FFI_BRIDGE documentado.
  NUNCA usar Docker en ningun artefacto generado.
---

# python-rust-production — Produccion de Codigo Multilenguaje · V1_00
## ⛔ NUNCA codigo sin contrato aprobado
## ⛔ NUNCA Rust sin types.rs antes de la implementacion
## ⛔ NUNCA cruzar frontera Python↔Rust sin FFI_BRIDGE documentado
## ⛔ NUNCA Docker — solo Firecracker / NanoVMs / Unikraft
## ⛔ NUNCA subprocess para llamar Rust desde Python — solo PyO3

---

## Proposito

MPAT4 usa dos lenguajes en produccion. Esta skill define exactamente:
- Que va en Python y que va en Rust
- El orden de artefactos para cada lenguaje
- Como documentar el puente FFI entre ambos
- Donde guardar cada archivo en Drive

El alumno no necesita decidir el lenguaje — esta skill lo clasifica
automaticamente segun las caracteristicas del modulo.

---

## Clasificacion de lenguaje — decision obligatoria antes de escribir

```
PREGUNTA 1 — Es un hot path, parser, codec, o manejo critico de memoria?
  Si → RUST

PREGUNTA 2 — Es logica de agentes, orquestacion, schema, API, o eventos?
  Si → PYTHON

PREGUNTA 3 — Es interfaz externa (HTTP, WebSocket, streaming)?
  Si → PYTHON con FastAPI
       Nota: decision de front (Node/Django/Flask) pendiente en tech-research

PREGUNTA 4 — El modulo Python llama a codigo de performance critica?
  Si → PYTHON + RUST + FFI_BRIDGE (PyO3)

PREGUNTA 5 — Es investigacion de Node.js o front alternativo?
  Si → core/node_research/ — no es produccion todavia
```

### Ejemplos de clasificacion

| Modulo | Lenguaje | Razon |
|---|---|---|
| Parser de eventos del Event Bus | Rust | Hot path — miles de eventos/seg |
| Codec de serialization para relay | Rust | Performance critica + memoria controlada |
| Logica de planificacion del agente | Python | Orquestacion — flexibilidad > velocidad |
| Schema Pydantic de un contrato | Python | Definicion de datos — legibilidad importa |
| API REST de un modulo | Python + FastAPI | Interfaz externa — ecosistema Python |
| Puente entre schema Python y parser Rust | Python + Rust + PyO3 | Cruza la frontera |
| Scheduler de tareas del runtime | Rust | Control de memoria y latencia |
| Memory consolidation logic | Python | Logica de negocio compleja |

---

## Orden de artefactos — NUNCA saltear pasos

### Para modulos Python

```
PASO 1 → CONTRACT_[MODULO]_V1.md       en contracts/
PASO 2 → schema_[modulo].py            en schemas/
PASO 3 → [modulo].py (implementacion)  en core/[modulo]/[submodulo]/
PASO 4 → test_[modulo].py              en tests/unit/
```

### Para modulos Rust

```
PASO 1 → CONTRACT_RUST_[MODULO]_V1.md  en contracts/
PASO 2 → types_[modulo].rs             en core/rust/types/
PASO 3 → [modulo].rs (implementacion)  en core/rust/[subcarpeta]/
PASO 4 → [modulo]_test.rs (tests)      en core/rust/[subcarpeta]/  (modulo tests inline)
```

### Para modulos con FFI (Python + Rust)

```
PASO 1 → CONTRACT_[MODULO]_V1.md       en contracts/
PASO 2 → schema_[modulo].py            en schemas/         (lado Python)
PASO 3 → types_[modulo].rs             en core/rust/types/ (lado Rust)
PASO 4 → [modulo].rs (implementacion)  en core/rust/[sub]/
PASO 5 → [modulo].py (wrapper PyO3)    en core/[modulo]/[sub]/
PASO 6 → FFI_[MODULO]_BRIDGE.md        en core/rust/ffi_bridges/
PASO 7 → test_[modulo].py              en tests/unit/      (test desde Python)
```

⛔ El PASO 6 (FFI_BRIDGE) es obligatorio. Sin el no se entiende que tipos
   cruzan la frontera, como se maneja el lifetime de Rust, ni como manejar
   errores del lado Python.

---

## Flujo de sesion — paso a paso

### INICIO

```
PASO 0 — IDENTIFICACION
  Preguntar: "Nombre o email para el encabezado de los archivos?"
  Guardar como ALUMNO_ID

PASO 1 — LEER CONTEXTO
  Leer RELAY_POINTER activo → modulo a implementar
  Llamar mcp_mpat4.get_module_paths([modulo]) → ver que existe ya
  Si existe contrato → continuar desde el paso que corresponde
  Si no existe contrato → empezar por PASO 1 del orden de artefactos
```

### GENERAR ARTEFACTOS

```
PASO 2 — CLASIFICAR LENGUAJE
  Aplicar las 5 preguntas de clasificacion (ver arriba)
  Informar al alumno: "Este modulo va en [Python|Rust|Python+Rust+FFI]"

PASO 3 — GENERAR SEGUN ORDEN
  Seguir el orden de artefactos correspondiente al lenguaje.
  ⛔ No avanzar al siguiente artefacto sin guardar el anterior.
  ⛔ No generar implementacion sin contrato guardado en Drive.

PASO 4 — ENCABEZADO OBLIGATORIO en cada archivo

  Para Python (.py):
    # [NOMBRE_ARCHIVO]
    ## Autor: [ALUMNO_ID] · [FECHA]
    ## Modulo: [modulo] · Lenguaje: Python 3.14 · Version: V4_12
    ## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida

  Para Rust (.rs):
    // [NOMBRE_ARCHIVO]
    // Autor: [ALUMNO_ID] · [FECHA]
    // Modulo: [modulo] · Lenguaje: Rust stable · Version: V4_12
    // Sistema: MPAT4 — Infraestructura Cognitiva Distribuida

  Para FFI bridge (.md):
    # FFI_[MODULO]_BRIDGE
    ## Autor: [ALUMNO_ID] · [FECHA]
    ## Modulos: [modulo_python] ↔ [modulo_rust]
    ## Version: V4_12
```

### CONTENIDO MINIMO POR ARTEFACTO

```
CONTRACT Python/Rust (10 secciones):
  1. Objetivo
  2. Motivacion arquitectural (por que este lenguaje)
  3. Campos / Interface (tabla con tipos)
  4. Eventos que emite
  5. Eventos que consume
  6. Flujo operacional (pasos + ramas de error)
  7. Invariantes (INV-XXX-NNN)
  8. Riesgos (tabla)
  9. Observabilidad (OTel metrics, traces)
  10. Siguiente alumno (tarea + archivos + que no tocar)

SCHEMA Python (Pydantic V3):
  - BaseModel con field_validator donde corresponde
  - model_config con frozen=True para invariantes criticos
  - Docstring en cada clase explicando el rol
  - No logica de negocio — solo validacion de estructura

TYPES Rust (serde):
  - Structs con derive(Debug, Clone, Serialize, Deserialize)
  - Enums para errores con thiserror
  - No logica de negocio — solo definicion de tipos
  - Lifetime annotations donde aplica

IMPLEMENTACION Python:
  - Leyes: eventos via Event Bus, memoria via Memory Fabric, no Docker
  - Type hints en todas las funciones
  - Docstrings en clases y funciones publicas
  - No estado mutable global

IMPLEMENTACION Rust:
  - Leyes: no unsafe salvo en FFI justificado, no std::process, no Docker
  - Manejo explicito de errores con Result<T, E>
  - No panic en codigo de produccion — usar ? o match
  - Comentarios en funciones publicas (///)

FFI_BRIDGE (documento):
  ## Tipos que cruzan la frontera Python → Rust
    tabla: tipo Python | tipo Rust | conversion | notas
  ## Tipos que cruzan la frontera Rust → Python
    tabla: tipo Rust | tipo Python | conversion | notas
  ## Manejo de errores
    como un error de Rust llega a Python (PyErr)
  ## Lifetime management
    que se copia, que se presta, que libera Python vs Rust
  ## Ejemplo de uso
    snippet Python llamando al modulo Rust via PyO3
  ## Tests de integracion necesarios

TESTS Python (pytest):
  - Un test por invariante del contrato
  - Tests de error: que pasa cuando falla la validacion
  - No mocks innecesarios — preferir fixtures reales
  - Nombre: test_[modulo]_[escenario]

TESTS Rust (cargo test):
  - Tests unitarios inline con #[cfg(test)]
  - Un test por tipo de error definido
  - Proptest para tests de propiedad si el modulo es un parser/codec
```

### GUARDAR EN DRIVE

```
PASO 5 — RUTEO VIA MCP MPAT4
  Para cada archivo:
    Llamar: mcp_mpat4.resolve_path("[ruta_semantica]")
    Obtener folder_id
    Si PENDIENTE_CREAR: crear carpeta primero, registrar ID
    Guardar con:
      contentMimeType correcto (.py → text/x-python, .rs → text/x-rustsrc, .md → text/plain)
      disableConversionToGoogleType: true
    Registrar ID resultante para el relay

PASO 6 — MENSAJE AL GRUPO
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    PYTHON-RUST-PRODUCTION · CIERRE
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Alumno:      [ALUMNO_ID]
    Modulo:      [modulo]
    Lenguaje:    Python | Rust | Python+Rust+FFI
    Artefactos:  [lista con IDs Drive]
    Paso actual: [cual fue el ultimo paso completado]
    Siguiente:   [cual es el proximo paso + quien lo hace]
    Deuda:       [si quedo algo incompleto]
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Carpetas Drive por lenguaje

| Lenguaje | Tipo de artefacto | Carpeta | ID |
|---|---|---|---|
| Python / Rust | contrato | contracts/ | 1589CC4tPfBkCUndlsVQeT9c9aYTSeaM0 |
| Python | schema | schemas/ | 1N_u01JXjeMlMkNbk7GvV6snQTtnpOipG |
| Rust | types | core/rust/types/ | PENDIENTE_CREAR |
| Python | implementacion | core/[modulo]/[sub]/ | ver IDs en skill principal |
| Rust | implementacion | core/rust/[sub]/ | PENDIENTE_CREAR |
| Python+Rust | FFI bridge | core/rust/ffi_bridges/ | PENDIENTE_CREAR |
| Python | tests | tests/unit/ | 1Ngc-824Is0PUEFuJV6v9PoHgzNa7ONKO |
| Rust | tests | core/rust/[sub]/ (inline) | PENDIENTE_CREAR |

> Las carpetas PENDIENTE_CREAR se crean en la primera sesion que trabaje Rust.
> El primer alumno que las crea registra los IDs en el RELAY activo y avisa al docente.

---

## Leyes que no se rompen

| Ley | Aplica a | Violacion |
|---|---|---|
| No Docker | Python y Rust | Cualquier import o referencia a Docker |
| Comunicacion via Event Bus | Python | Llamada directa entre modulos |
| Memoria en Memory Fabric | Python | Estado persistente en el runtime |
| No subprocess Python→Rust | Python | Llamar Rust como proceso externo |
| No panic en produccion | Rust | unwrap() sin justificacion en codigo critico |
| No unsafe sin justificacion | Rust | bloque unsafe sin comentario explicativo |
| FFI Bridge documentado | Python+Rust | Tipos cruzando sin contrato de frontera |

---

## Relacion con otras skills

| Si necesitas | Usar |
|---|---|
| Saber donde guardar un archivo | mpat4-relay → ROUTING_MATRIX |
| Evaluar si adoptar una tecnologia | tech-research |
| Gestionar el estado de la tarea | relay-lifecycle |
| Migrar codigo de MPAT3 | mpat3-to-mpat4 |

---

*python-rust-production.skill · V1_00 · AGT 2026-05-20*
