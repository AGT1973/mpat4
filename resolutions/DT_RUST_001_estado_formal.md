# MPAT4_DEST
# destino: docs
# nombre: DT_RUST_001_estado_formal.md
# alumno: andrea.proyecto.ia@gmail.com

# DT_RUST_001_estado_formal.md
## Autor: andrea.proyecto.ia@gmail.com · 2026-05-29
## Módulo: core/rust/ — Kernel Crítico Rust
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida

*que has usado el formato de razonamiento adaptado por AGT*

---

## PROPÓSITO DE ESTE DOCUMENTO

Cierre formal de la brecha documental detectada en sesión 2026-05-29:
el estado Rust no estaba registrado como Deuda Técnica con ID formal
en ningún relay. Este documento lo registra y evita que el próximo
alumno tenga que redescubrir la situación.

---

## ESTADO RUST — VERIFICADO EN DRIVE 2026-05-29

| Componente | Estado real en Drive | Especificado en |
|------------|---------------------|-----------------|
| Kernel crítico Rust | NO DETECTADO — ningún archivo .rs ni carpeta rust/ | MPAT_V4_0 especificación maestra |
| Bridge FFI PyO3 | NO DETECTADO — ningún Cargo.toml, ningún lib.rs | MPAT_V4_0 especificación maestra |
| Bindings Python↔Rust | NO DETECTADO | MPAT_V4_0 especificación maestra |

**Búsquedas realizadas:** "rust", "pyo3", "kernel_critico", "ffi", "Cargo"
**Resultado:** cero archivos Rust en todo el Drive MPAT4.

Estado correcto: FASE DE DISEÑO — esto es coherente con la hoja de ruta.
NO es una brecha de implementación. ES una brecha documental.

---

## DEUDA TÉCNICA FORMAL

### DT-RUST-001 — Ausencia de especificación Rust ejecutable

| Campo | Valor |
|-------|-------|
| ID | DT-RUST-001 |
| Descripción | No existe CONTRACT_RUST_V4_01.md ni especificación ejecutable del kernel Rust |
| Prioridad | BAJA — el stack actual Python puro es funcional |
| Bloqueado por | La arquitectura Python no está estabilizada. Rust prematuro = deuda técnica mayor |
| Precondición para avanzar | Todos los módulos Python core/ deben estar completos y testeados |
| Acción cuando se active | Generar CONTRACT_RUST_V4_01.md con INV-RUST.1-N antes de cualquier código |
| Responsable | Quien tome la tarea cuando las precondiciones estén satisfechas |
| Estado | ABIERTO — BLOQUEADO (esperando estabilización Python) |

### DT-RUST-002 — Ausencia de especificación Bridge FFI PyO3

| Campo | Valor |
|-------|-------|
| ID | DT-RUST-002 |
| Descripción | No existe CONTRACT_FFI_V4_01.md ni schema del bridge Python↔Rust |
| Prioridad | BAJA — depende de DT-RUST-001 |
| Bloqueado por | DT-RUST-001 (el kernel debe existir antes del bridge) |
| Precondición para avanzar | DT-RUST-001 resuelto + interfaz PyO3 definida en contrato |
| Acción cuando se active | Generar schema_ffi.py (tipos cruzados) + CONTRACT_FFI_V4_01.md |
| Estado | ABIERTO — BLOQUEADO (esperando DT-RUST-001) |

### INV-CADENAS-001 — Cadenas de relay paralelas sin índice maestro

| Campo | Valor |
|-------|-------|
| ID | INV-CADENAS-001 |
| Descripción | Existen 3 cadenas activas (andrea/ariel, cursos.agt, docente) con numeración superpuesta |
| Impacto | El próximo alumno no puede determinar qué relay leer sin tabla de cadenas |
| Resolución | Docente debe generar RELAY_INDEX_CADENAS.md con mapa de cada cadena |
| Responsable | ai.mpat.info@gmail.com / cursos.agt.ia@gmail.com |
| Estado | PENDIENTE_INV — requiere decisión del docente, no del alumno |

---

## RAZONAMIENTO — POR QUÉ NO IMPLEMENTAR RUST AHORA

El error más común al ver "Rust: NO DETECTADO" es interpretarlo como
"hay que implementar Rust". Ese razonamiento es incorrecto.

La secuencia correcta es:

1. Estabilizar arquitectura Python (módulos core/ completos y testeados)
2. Identificar los cuellos de botella de performance con datos reales
3. Diseñar el kernel Rust solo para las funciones donde Python falla
4. Generar CONTRACT_RUST_V4_01.md con invariantes verificables
5. Implementar con PyO3 y test de integración Python↔Rust
6. Nunca antes

Implementar Rust antes de la estabilización Python:
- Duplica la superficie de bugs
- Invalida el contrato Rust cada vez que cambia la interfaz Python
- Viola P1 (modularidad) si el bridge no está correctamente especificado
- Genera deuda técnica mayor que la que resuelve

**El estado "Rust en fase de diseño" es correcto para el momento actual del proyecto.**

---

## ESTADO RUST — MAPA DE PRECONDICIONES

```
Python core/ estabilizado
    ↓
INV-LOCAL-01/02/03 resueltos
    ↓
Performance profiling con datos reales
    ↓
Identificar funciones candidatas a Rust
    ↓
CONTRACT_RUST_V4_01.md   ← DT-RUST-001
    ↓
schema_ffi.py + CONTRACT_FFI_V4_01.md   ← DT-RUST-002
    ↓
kernel_critico.rs + lib.rs (PyO3)
    ↓
tests de integración Python↔Rust
```

---

## PARA EL DOCENTE

Se recomienda:
1. Resolver INV-CADENAS-001 generando un RELAY_INDEX_CADENAS.md
2. Confirmar que DT-RUST-001 y DT-RUST-002 son las IDs correctas
   (pueden existir IDs previas en otras cadenas no leídas)
3. Actualizar WORK_INDEX.md con el estado Rust si existe

---

*DT_RUST_001_estado_formal.md · andrea.proyecto.ia@gmail.com · 2026-05-29 · MPAT4*
*que has usado el formato de razonamiento adaptado por AGT*
