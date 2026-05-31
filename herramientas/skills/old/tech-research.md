---
name: tech-research
version: V1_00
description: >
  Skill de investigacion de nuevas tecnologias para aplicar a MPAT4 y planificar V5.
  Activar cuando el alumno diga 'investigar tecnologia', 'tech radar', 'evaluar framework',
  'que hay nuevo en rust', 'investigar front', 'novedades para v4', 'evaluar node vs fastapi',
  'investigar stack', o cuando la skill mpat4-relay detecte una decision tecnologica pendiente.
  Produce TECH_RADAR_[FECHA].md en research/tech_radar/ y si la decision es adoptar,
  produce RESOLUCION_TECH_[NOMBRE].md en resoluciones/.
  NUNCA adoptar una tecnologia sin evaluarla contra los 5 criterios.
  NUNCA guardar una investigacion sin encabezado de estado (abierta/resuelta/descartada).
---

# tech-research — Investigacion de Nuevas Tecnologias · V1_00
## ⛔ NUNCA adoptar una tecnologia sin pasar los 5 criterios de evaluacion
## ⛔ NUNCA guardar investigacion sin estado explicito (abierta / resuelta / descartada)
## ⛔ NUNCA bloquear el relay activo por una investigacion no bloqueante
## ⛔ NUNCA proponer tecnologia sin verificar compatibilidad con unikernel + PyO3 + MCP

---

## Proposito

MPAT4 es un sistema vivo. Nuevas tecnologias aparecen constantemente y algunas
pueden mejorar el stack actual (Python + Rust) o resolver problemas abiertos
(front, observabilidad, federation, protocolo A2A).

Esta skill estructura el proceso de investigacion para que:
- Cualquier alumno pueda investigar sin bloquear el relay principal
- Las decisiones queden documentadas y sean rastreables
- El grupo no adopte tecnologias incompatibles con la arquitectura base
- El front (Node.js, Django, Flask, FastAPI) tenga una evaluacion sistematica

**La investigacion es trabajo colaborativo. Varias personas pueden investigar
distintas tecnologias en paralelo sin conflicto.**

---

## Cuando abrir una investigacion

| Trigger | Tipo | Bloqueante |
|---|---|---|
| El docente la asigna explicitamente | asignada | segun docente |
| Al codificar aparece incompatibilidad tecnica | experimento | puede bloquear |
| Hay decision de front sin resolver | evaluacion | si bloquea deploy |
| Se publica una version mayor de dependencia clave | radar | no |
| Un alumno encuentra una mejora potencial | propuesta | no |
| La skill mpat4-relay detecta DEC-NNN sin resolver | decision | si |

---

## Estructura de archivos en Drive

```
research/
├── tech_radar/          ← evaluaciones generales (ID: PENDIENTE_CREAR)
│   └── TECH_RADAR_[FECHA]_[TEMA].md
├── experiments/         ← prototipos que requieren codigo (ID: 1ooeCILfKqnavAi6aeEkkKHoF2LdStLRn)
│   └── EXP_NNN_[TEMA].md / .py / .rs
├── futures/             ← propuestas para V5 (ID: 1E4i5Dc_JqMGZfF2LsVFPtxL2WIAqURw)
│   └── FUT_NNN_[TEMA].md
└── papers/              ← analisis de papers academicos (ID: 1Yi5Erc1drlLqqQe9gID2mmOMSYyrC9EV)
    └── PAPER_NNN_[AUTOR]_[TITULO].md

resoluciones/            ← decisiones adoptadas (ID: 1hRfjnUkOyfnfqxLEfBM0CWLLnDBi3GQU)
    └── RESOLUCION_TECH_[NOMBRE]_[FECHA].md
```

---

## Flujo de investigacion — paso a paso

### INICIO

```
PASO 0 — IDENTIFICACION
  Preguntar: "Nombre o email para registrar la investigacion?"
  Guardar como ALUMNO_ID

PASO 1 — DEFINIR EL OBJETO DE INVESTIGACION
  Preguntar si el alumno ya sabe que investigar.
  Si no: leer RELAY_POINTER activo y buscar decisiones tecnicas abiertas (DEC-NNN sin resolver).
  Definir:
    TEMA:      [nombre de la tecnologia o decision]
    TIPO:      evaluacion | experimento | propuesta | paper | radar
    BLOQUEANTE: si [modulo bloqueado] | no

PASO 2 — EVALUAR TOKENS
  Tokens > 60% → investigacion completa (todos los criterios)
  Tokens 40-60% → investigacion parcial (criterios 1-3 + conclusion preliminar)
  Tokens < 40%  → solo encabezado + fuentes + delegar al siguiente alumno
```

### INVESTIGAR

```
PASO 3 — INVESTIGACION WEB
  Buscar informacion actual sobre la tecnologia.
  Fuentes prioritarias:
    - Documentacion oficial (docs.rust-lang.org, fastapi.tiangolo.com, etc.)
    - GitHub releases y changelogs
    - Benchmarks recientes (TechEmpower, arewefastyet, etc.)
    - Experiencias de produccion en HackerNews, Reddit r/rust, r/Python

PASO 4 — APLICAR LOS 5 CRITERIOS DE EVALUACION

  CRITERIO 1 — Compatibilidad con unikernel
    ¿La tecnologia puede correr en Firecracker / NanoVMs / Unikraft?
    ¿Requiere kernel completo, systemd, o servicios del SO?
    Resultado: COMPATIBLE | INCOMPATIBLE | REQUIERE_INVESTIGACION

  CRITERIO 2 — Compatibilidad con el stack actual
    ¿Puede integrarse con Python 3.14 No-GIL?
    ¿Puede integrarse con Rust via PyO3 si es necesario?
    ¿Rompe algun invariante existente (Event Bus, Memory Fabric, sandboxing)?
    Resultado: COMPATIBLE | INCOMPATIBLE | PARCIALMENTE_COMPATIBLE

  CRITERIO 3 — Compatibilidad con MCP y A2A
    ¿La tecnologia puede exponer tools via MCP?
    ¿Puede participar en protocolos A2A v1.0?
    Resultado: COMPATIBLE | INCOMPATIBLE | NEUTRAL

  CRITERIO 4 — Impacto en el relay actual
    ¿Adoptar esta tecnologia requiere cambios en modulos ya completados?
    ¿Cuantos contratos habria que revisar?
    Resultado: SIN_IMPACTO | IMPACTO_MENOR (1-3 modulos) | IMPACTO_MAYOR (4+)

  CRITERIO 5 — Madurez y mantenimiento
    ¿Tiene releases estables en los ultimos 6 meses?
    ¿Tiene comunidad activa y soporte empresarial?
    ¿Tiene CVEs criticos abiertos?
    Resultado: MADURA | EN_DESARROLLO | ABANDONADA | RIESGO_SEGURIDAD

PASO 5 — DECISION FINAL

  ADOPTAR:
    Todos los criterios 1-3 son COMPATIBLE o mejor.
    Criterio 4 es SIN_IMPACTO o IMPACTO_MENOR.
    Criterio 5 es MADURA.
    → Generar RESOLUCION_TECH en resoluciones/

  EVALUAR_MAS:
    Algun criterio tiene REQUIERE_INVESTIGACION o PARCIALMENTE_COMPATIBLE.
    → Crear EXP_NNN en research/experiments/ para prototipo
    → Marcar investigacion como abierta, no bloqueante

  DESCARTAR:
    Criterio 1 o 2 es INCOMPATIBLE.
    Criterio 4 es IMPACTO_MAYOR sin justificacion arquitectural fuerte.
    Criterio 5 es ABANDONADA o RIESGO_SEGURIDAD.
    → Documentar en tech_radar con razon explicita
    → No abrir experimento
```

### GUARDAR RESULTADOS

```
PASO 6 — ARCHIVO TECH_RADAR

  Nombre: TECH_RADAR_[FECHA]_[TEMA].md
  Carpeta: research/tech_radar/ (ID: PENDIENTE_CREAR — crear si no existe)

  Encabezado obligatorio:
    ---
    tecnologia: [nombre y version]
    autor: [ALUMNO_ID]
    fecha: [FECHA]
    tipo: evaluacion | experimento | propuesta | paper | radar
    bloqueante: si [modulo] | no
    estado: abierta | resuelta | descartada
    decision: ADOPTAR | EVALUAR_MAS | DESCARTAR
    relay_origen: RELAY_[NNN] (si viene de un relay)
    ---

  Contenido minimo:
    ## Que es
    ## Por que se evalua (contexto en MPAT4)
    ## Criterios (tabla con los 5 resultados)
    ## Fuentes consultadas (con URLs)
    ## Decision y justificacion
    ## Impacto si se adopta (modulos afectados)
    ## Proximos pasos (si EVALUAR_MAS o ADOPTAR)

PASO 7 — SI LA DECISION ES ADOPTAR: RESOLUCION_TECH

  Nombre: RESOLUCION_TECH_[NOMBRE]_[FECHA].md
  Carpeta: resoluciones/ (ID: 1hRfjnUkOyfnfqxLEfBM0CWLLnDBi3GQU)

  Encabezado:
    ---
    resolucion: TECH_[NOMBRE]
    autor: [ALUMNO_ID]
    fecha: [FECHA]
    estado: APROBADA_PROVISIONAL (requiere revision del docente)
    ---

  Contenido:
    ## Tecnologia adoptada
    ## Version minima requerida
    ## Modulos de MPAT4 que se actualizan
    ## Contratos que requieren revision
    ## Deuda tecnica generada
    ## Plan de integracion (en que relay se implementa)
    ## Riesgos y mitigacion
    ## Como revertir si falla

PASO 8 — MENSAJE AL GRUPO
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    TECH-RESEARCH · RESULTADO
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Alumno:       [ALUMNO_ID]
    Tecnologia:   [TEMA]
    Decision:     ADOPTAR | EVALUAR_MAS | DESCARTAR
    Bloqueante:   si [modulo] | no
    Archivo:      TECH_RADAR_[FECHA]_[TEMA].md
    Resolucion:   RESOLUCION_TECH_[NOMBRE].md (si ADOPTAR)
    Impacto:      [modulos afectados o "ninguno"]
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Tecnologias en evaluacion prioritaria — V4_12

Estas evaluaciones estan pendientes y bloquean decisiones de arquitectura:

| Tecnologia | Pregunta clave | Tipo | Bloqueante |
|---|---|---|---|
| Node.js + Express | ¿Puede ser el front de MPAT4? | evaluacion | si — decision de front |
| Django | ¿Mejor que FastAPI para el front de MPAT4? | evaluacion | si — decision de front |
| Flask | ¿Mas liviano que Django para APIs internas? | evaluacion | si — decision de front |
| FastAPI 0.115+ | ¿Ya es el front elegido? ¿Que falta? | evaluacion | si — decision de front |
| ConnectRPC | ¿Reemplaza gRPC en comunicacion inter-modulo? | radar | no |
| Pydantic V3 | ¿Cambios breaking respecto a V2? | radar | no |
| Unikraft 0.17+ | ¿Mejoras en compatibilidad con Python? | radar | no |
| PyO3 0.22+ | ¿Nuevas features para el FFI bridge? | radar | no |

**La decision de front (Node / Django / Flask / FastAPI) es la mas urgente.**
Bloquea el diseno de los modulos de interfaz externa.

---

## Reglas de calidad

| Regla | Consecuencia si se viola |
|---|---|
| Aplicar los 5 criterios antes de decidir | Decision no fundamentada — puede ser revertida |
| Estado explicito en encabezado | Investigacion queda flotando sin conclusion |
| RESOLUCION_TECH si se adopta | La decision no es oficial sin resolucion |
| No bloquear relay por investigacion no bloqueante | Paraliza el trabajo del grupo |
| Verificar compatibilidad con unikernel siempre | Adoptar algo incompatible rompe la arquitectura |

---

*tech-research.skill · V1_00 · AGT 2026-05-20*
