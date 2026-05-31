---
name: versionado-mpat
description: >
  Skill de trabajo colaborativo relay para el proyecto MPAT. Activar SIEMPRE
  cuando el usuario diga "continuar", "seguimos", "continuar con mpat",
  "siguiente pendiente", "retomar mpat", o al inicio de sesión si hay archivos
  ARQUITECTURA_* en contexto. La skill accede a Google Drive, elige el pendiente
  de menor complejidad abierto, lo resuelve, genera la nueva versión, la guarda
  en Drive y registra la autoría del alumno. Si los tokens se agotan, genera
  el mensaje de traspaso al grupo. NUNCA sobreescribe versiones anteriores.
  Usar aunque el usuario no mencione la skill explícitamente si el contexto
  es claramente de trabajo MPAT.
---

# MPAT — Skill de Trabajo Relay Colaborativo · V3_02

## Propósito

Un alumno dice "continuar". La skill hace todo lo demás: lee Drive, elige
la tarea más pequeña abierta, la resuelve, guarda la nueva versión con la
firma del alumno, y decide si continúa o traspasa al siguiente.

**El estado vive en Drive, no en la memoria de Claude.**

---

## Configuración requerida (una sola vez por alumno)

El alumno debe tener el servidor MCP `Google Drive` activo en su sesión de Claude.
Ver `README_INSTALACION.md` entregado por el docente.

Carpeta raíz del proyecto **V3_01**:
```
FOLDER_ID_ROOT:      1vy_pTgB1UIfDQd3UMpO-XwYvZyt2KAoM
```

---

## Estructura de archivos en Drive · V3_01

```
MPAT_V3_0/                              ← 1vy_pTgB1UIfDQd3UMpO-XwYvZyt2KAoM
├── arquitectura/                       ← 1L5lKKqC7ixa8MAOjYe0OE1EbebmB0iJF
│   ├── ARQUITECTURA_base_V3_01.md      ← canónico — leer primero
│   ├── ARQUITECTURA_pendientes_V2_102.md
│   ├── ARQUITECTURA_UNIKERNEL_V3_01.md ← generado en RELAY_009
│   └── ARQUITECTURA_SUBQ_V3_01.md      ← generado en RELAY_009
├── capas/                              ← 19G6ZNwHRc5mzMAsUq82NS7XyYuSWvJ9e
│   ├── CAPA_01_MASTER.md ... CAPA_14_MASTER.md
│   └── CAPA_XX_MASTER_V3_01.md        ← versiones actualizadas post-RELAY_001
├── estado/                             ← 1OkJa4Spj8wXRp7YmVSarUcBbN_3Fu976
│   ├── MPAT_PROYECTO_ESTADO_V3_01.md
│   └── PROMPT_CONTINUIDAD_V3_01.md
├── informes/                           ← carpeta de alumnos (vacía inicial)
├── investigaciones/                    ← 1vZzX0ouJOwPMIRFpX-U6TeBVzxNS5V1G
│   └── INVESTIGACION_FUT3_INTEGRACION_V3_01.md
├── plantillas/                         ← 1imVwMNte04FESokf8CnZCxR-xGTaHi38
│   ├── TEMPLATE_INFORME_CAPA_V3_01.md
│   ├── INDICE_INFORMES_V3_01.md
│   └── PROMPT_ALUMNO_PASO1_RECOMPILACION.md
├── resoluciones/                       ← 1IaeQLsxhjoNctFWf3PEP4OeBz4GfFHHZ
│   ├── RESOLUCIONES_CONSOLIDADAS_V3_01.md  ← leer para contexto
│   └── RESOLUCIONES_PATCHES_VALIDADAS_2026-05-11.md
└── zzz_proximo_relay/                  ← 1oaXdMNDlVL5s7VYLotfL_M4-N8Y6JTFq
    ├── RELAY_001_MPAT_V3_01.md
    ├── RELAY_NEXT_POINTER.md           ← indica el próximo relay activo
    └── RELAY_ESTADO_SESION_*.md
```

---

## Flujo relay — INICIO DE SESIÓN

Cuando el alumno dice "continuar":

```
PASO 0 — IDENTIFICACIÓN
  Preguntar: "¿Nombre o email para registrar tu autoría?"
  Guardar como ALUMNO_ID

PASO 1 — LEER ESTADO ACTUAL
  Leer RELAY_NEXT_POINTER.md de zzz_proximo_relay/ → saber qué relay ejecutar
  Leer MPAT_PROYECTO_ESTADO_V3_01.md → estado del proyecto
  Leer RESOLUCIONES_CONSOLIDADAS_V3_01.md → contexto de resoluciones

PASO 2 — LEER EL RELAY ACTIVO
  Leer RELAY_NNN_MPAT_V3_01.md desde zzz_proximo_relay/
  Identificar la tarea exacta (capa, archivo, acción)
  Informar: "Ejecutaré RELAY_[NNN] — [descripción breve]"

PASO 3 — CARGAR SOLO LO NECESARIO
  Leer el archivo de capa o carpeta indicado en el relay
  Leer ARQUITECTURA_base_V3_01.md → referencia maestra
  NO cargar capas no relacionadas con el relay activo

PASO 4 — RESOLVER
  Ejecutar la tarea definida en el prompt relay
  Integrar mejoras de FUT_3.md si corresponde a la capa
  Generar el archivo nuevo o actualizado con versión V3_01

PASO 5 — GUARDAR NUEVA VERSIÓN
  Guardar ÚNICAMENTE en las carpetas autorizadas por el relay activo (ver tabla abajo)
  Nombre: [ARCHIVO]_V3_01.md (nunca sobreescribir el original)
  Registrar: ALUMNO_ID + fecha en el encabezado del archivo
  Actualizar RELAY_NEXT_POINTER.md → próximo relay
  ⛔ NUNCA sobreescribir — siempre versión nueva
  ⛔ NUNCA escribir en carpetas fuera del alcance del relay activo

PASO 6 — EVALUAR CONTINUACIÓN
  Tokens > 60% restantes → continuar con sub-tarea del mismo relay
  Tokens < 60% restantes → ejecutar PROTOCOLO DE TRASPASO
```

---

## Alcance de escritura por RELAY ← REGLA CRÍTICA

Cada RELAY tiene carpetas de destino estrictamente definidas.
**Escribir fuera de estas carpetas es una violación grave — detener y avisar al alumno.**

| RELAY | Carpetas donde SE PUEDE escribir | Carpetas PROHIBIDAS |
|---|---|---|
| RELAY_001 | `capas/` + `zzz_proximo_relay/RELAY_NEXT_POINTER.md` | arquitectura/, estado/, informes/, investigaciones/, plantillas/, resoluciones/ |
| RELAY_002 | `resoluciones/` + `zzz_proximo_relay/RELAY_NEXT_POINTER.md` | capas/, arquitectura/, estado/, informes/, investigaciones/, plantillas/ |
| RELAY_003 | `plantillas/` + `zzz_proximo_relay/RELAY_NEXT_POINTER.md` | capas/, arquitectura/, estado/, informes/, investigaciones/, resoluciones/ |
| RELAY_004 | `informes/` + `zzz_proximo_relay/RELAY_NEXT_POINTER.md` | capas/, arquitectura/, estado/, investigaciones/, plantillas/, resoluciones/ |
| RELAY_005 | `investigaciones/` + `zzz_proximo_relay/RELAY_NEXT_POINTER.md` | capas/, arquitectura/, estado/, informes/, plantillas/, resoluciones/ |
| RELAY_006 | `arquitectura/` + `zzz_proximo_relay/RELAY_NEXT_POINTER.md` | capas/, estado/, informes/, investigaciones/, plantillas/, resoluciones/ |
| RELAY_007 | `estado/` + `zzz_proximo_relay/RELAY_NEXT_POINTER.md` | capas/, arquitectura/, informes/, investigaciones/, plantillas/, resoluciones/ |
| RELAY_008 | `zzz_proximo_relay/` (todos los archivos) | capas/, arquitectura/, estado/, informes/, investigaciones/, plantillas/, resoluciones/ |
| RELAY_009 | `arquitectura/` (UNIKERNEL + SUBQ) + `zzz_proximo_relay/RELAY_NEXT_POINTER.md` | capas/, estado/, informes/, investigaciones/, plantillas/, resoluciones/ |

> **Regla de oro:** si el relay activo no menciona explícitamente una carpeta,
> esa carpeta está PROHIBIDA en esa sesión. La duda = no escribir.

---

## Protocolo de traspaso

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  MPAT · TRASPASO AL SIGUIENTE ALUMNO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Sesión cerrada por: [ALUMNO_ID]
  RELAY ejecutado:    RELAY_[NNN]
  Tarea completada:   [descripción]
  Próximo relay:      RELAY_[NNN+1] — [descripción]

  COPIAR AL GRUPO:
  "Terminé mi sesión MPAT V3_01. Ejecuté RELAY_[NNN].
   Completé: [tarea]. Próximo: RELAY_[NNN+1].
   El siguiente puede arrancar desde MPAT_V3_0."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Reglas de calidad — NUNCA violar

| Regla | Consecuencia si se viola |
|---|---|
| Nunca sobreescribir versiones anteriores | Detener, avisar al alumno, no guardar |
| Siempre registrar ALUMNO_ID y fecha en cada archivo | Sin firma = no válido |
| Solo cargar lo necesario para el relay activo | Economía de tokens, contexto limpio |
| Nunca borrar ítems de resoluciones | Solo agregar nuevas |
| Respetar el orden de los RELAYs 001-009 | Cada relay depende del anterior |
| Nunca implementar sin leer el relay completo | Leer antes de escribir |
| CAPA_00 NO EXISTE en V3_01 | Es placeholder eliminado |
| Solo escribir en las carpetas autorizadas por el relay activo | Detener, avisar al alumno, no guardar |

---

## IDs de carpetas Drive — V3_01

| Carpeta | ID |
|---|---|
| MPAT_V3_0 (raíz) | `1vy_pTgB1UIfDQd3UMpO-XwYvZyt2KAoM` |
| arquitectura/ | `1L5lKKqC7ixa8MAOjYe0OE1EbebmB0iJF` |
| capas/ | `19G6ZNwHRc5mzMAsUq82NS7XyYuSWvJ9e` |
| estado/ | `1OkJa4Spj8wXRp7YmVSarUcBbN_3Fu976` |
| investigaciones/ | `1vZzX0ouJOwPMIRFpX-U6TeBVzxNS5V1G` |
| plantillas/ | `1imVwMNte04FESokf8CnZCxR-xGTaHi38` |
| resoluciones/ | `1IaeQLsxhjoNctFWf3PEP4OeBz4GfFHHZ` |
| zzz_proximo_relay/ | `1oaXdMNDlVL5s7VYLotfL_M4-N8Y6JTFq` |

---

## Novedades V3_01 que el alumno debe conocer

1. **A2A v1.0** — Protocol Agent-to-Agent: los agentes pueden invocar agentes externos
2. **Unikernel por usuario** — cada sesión de usuario corre en un unikernel aislado
3. **SubQ** — Sub-Queue asíncrona para tareas de agentes sin bloquear el orquestador
4. **ShadowRadix + CSA/HCA** — Capa 5 de inferencia optimizada para largo contexto
5. **NHP Protocol** — seguridad Capa 9, authenticate-before-connect
6. **Dream Cycle RMH** — Capa 8 con Q-Value Reranking y aprendizaje hebbiano
7. **policy.yaml** — contrato de gobernanza global activo en Capa 14

---

## RELAYs disponibles en zzz_proximo_relay/

| RELAY | Área | Estado inicial |
|---|---|---|
| RELAY_001 | Capas 0-14: Documentación y depuración | ACTIVO |
| RELAY_002 | Resoluciones | pendiente RELAY_001 |
| RELAY_003 | Plantillas | pendiente RELAY_002 |
| RELAY_004 | Informes | pendiente RELAY_003 |
| RELAY_005 | Investigaciones | pendiente RELAY_004 |
| RELAY_006 | Arquitectura consolidación | pendiente RELAY_005 |
| RELAY_007 | Estado y snapshot | pendiente RELAY_006 |
| RELAY_008 | zzz_proximo_relay sistema | pendiente RELAY_007 |
| RELAY_009 | FUT_3 + Unikernel + SubQ | pendiente RELAY_008 |

---

*versionado-mpat SKILL · V3_02 · AGT 2026-05-11*
*Cambios V3_02: tabla de alcance de escritura por RELAY; regla CAPA_00 corregida (CAPA_04 existe)*
*que has usado el formato de razonamiento adaptado por AGT*
