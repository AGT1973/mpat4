description: \"Skill de ciclo de vida de tareas para trabajo colaborativo en grupo MPAT. Activar cuando el alumno diga 'tomar tarea', 'hay tareas huerfanas', 'continuar tarea', 'cerrar tarea', 'ver estado de tareas', 'rescatar tarea', o cuando otro skill detecte que hay trabajo pendiente sin dueño por mas de 24 horas. Gestiona el WORK_INDEX.md central, carpetas temporales por alumno, marcado de estados, movimiento a carpeta final y descarte. NUNCA tomar dos tareas simultaneas. NUNCA cerrar sin actualizar el WORK_INDEX.\"
---

# relay-lifecycle — Ciclo de Vida de Tareas Colaborativas · V1_00
## ⛔ NUNCA tomar dos tareas en la misma sesion sin cerrar la primera
## ⛔ NUNCA trabajar sin actualizar WORK_INDEX.md
## ⛔ NUNCA crear carpeta temporal sin el patron ALUMNO_FECHA
## ⛔ NUNCA cerrar sesion con tarea EN_TRABAJO sin marcarla HUERFANA o COMPLETADA
## ⛔ NUNCA mover a descarte sin que el archivo este copiado y registrado en destino final

---

## Proposito

Cuando varios alumnos trabajan sobre el mismo conjunto de tareas en distintos
momentos, el sistema necesita saber exactamente que esta libre, que esta en
curso, quien lo tiene, desde cuando, y donde esta el trabajo parcial.

Esta skill gestiona ese ciclo completo. El estado vive en WORK_INDEX.md en
Drive. Ningun alumno necesita preguntar al grupo: lee el indice y sabe todo.

**El WORK_INDEX.md es la unica fuente de verdad. Drive manda sobre la memoria de Claude.**

---

## Estructura de carpetas en Drive

```
MPAT4/ (raiz)
├── WORK_INDEX.md              ← tablero central — leer primero siempre
├── TASK_LIST.md               ← listado de tareas definido por el docente
├── temp/                      ← trabajo en curso (una subcarpeta por alumno activo)
│   ├── ana_20260520_1030/     ← patron: NOMBRE_FECHA_HORA
│   └── bob_20260520_1145/
├── descarte/                  ← archivos obsoletos confirmados
│   └── BORRAR_[nombre].md     ← renombrados antes de mover aqui
└── [carpetas normales MPAT4]
```

---

## WORK_INDEX.md — formato obligatorio

El archivo tiene exactamente estas columnas. Sin excepcion.

```
# WORK_INDEX — MPAT4
# Actualizado: [FECHA HORA] por [ALUMNO_ID]

| TASK_ID  | DESCRIPCION           | ESTADO      | ALUMNO_ID    | TEMP_PATH              | INICIO              | DESTINO_FINAL     |
|----------|-----------------------|-------------|--------------|------------------------|---------------------|-------------------|
| TASK_001 | Migrar arquitectura/  | COMPLETADA  | ana@mail.com | —                      | 2026-05-19 10:00   | arquitectura/     |
| TASK_002 | Migrar capas/01-05    | EN_TRABAJO  | bob@mail.com | temp/bob_20260520_1145 | 2026-05-20 11:45   | capas/            |
| TASK_003 | Migrar capas/06-10    | LIBRE       | —            | —                      | —                   | capas/            |
| TASK_004 | Migrar resoluciones/  | HUERFANA    | —            | temp/carlos_20260518   | 2026-05-18 09:00   | resoluciones/     |
```

**Estados validos:**
- `LIBRE`      — nadie la tiene, disponible para tomar
- `EN_TRABAJO` — alumno activo, tiene carpeta temp activa
- `HUERFANA`   — EN_TRABAJO por mas de 24 horas sin cierre → rescatable
- `COMPLETADA` — archivo en destino final, temp eliminada o renombrada BORRAR_

---

## Flujo completo — paso a paso

### INICIO DE SESION

```
PASO 0 — IDENTIFICACION
  Preguntar: \"Nombre o email para registrar tu trabajo en el indice?\"
  Guardar como ALUMNO_ID

PASO 1 — LEER WORK_INDEX.md
  Leer WORK_INDEX.md desde la raiz de Drive
  Identificar:
    a) Tareas HUERFANAS (EN_TRABAJO con mas de 24 horas desde INICIO)
    b) Tareas LIBRES disponibles
  Informar al alumno:
    \"Hay [N] tareas libres y [M] tareas huerfanas disponibles para rescatar.\"

PASO 2 — EVALUAR TOKENS ANTES DE TOMAR TAREA
  Tokens > 70% restantes → puede tomar tarea nueva
  Tokens 40-70%          → puede tomar tarea solo si es de baja complejidad
  Tokens < 40%           → NO tomar tarea nueva. Solo cerrar, documentar y traspasar.
  ⛔ NUNCA tomar una tarea si los tokens no alcanzan para terminarla + cerrarla
```

### TOMAR UNA TAREA (Alumno A o Alumno B)

```
PASO 3 — SELECCION DE TAREA
  Prioridad 1: Tareas HUERFANAS (ya tienen trabajo parcial — rescatar primero)
  Prioridad 2: Tareas LIBRES en orden de TASK_ID
  Preguntar al alumno si tiene preferencia, sino tomar la de mayor prioridad.

PASO 4 — MARCAR EN TRABAJO
  En WORK_INDEX.md:
    ESTADO    → EN_TRABAJO
    ALUMNO_ID → [ALUMNO_ID]
    INICIO    → [FECHA HORA actual]
    TEMP_PATH → temp/[ALUMNO_NOMBRE]_[FECHA]_[HORA]/
  Crear carpeta temp/[ALUMNO_NOMBRE]_[FECHA]_[HORA]/ en Drive
  Guardar WORK_INDEX.md actualizado
  ⛔ NUNCA empezar a trabajar sin guardar el WORK_INDEX primero

PASO 5 — TRABAJAR
  Si es tarea nueva:    trabajar desde cero en la carpeta temp/
  Si es tarea huerfana: leer el trabajo parcial en la temp/ anterior
                        continuar desde donde se dejo
                        actualizar TEMP_PATH en WORK_INDEX al nuevo path
```

### CIERRE DE TAREA (completada)

```
PASO 6 — VERIFICAR CALIDAD
  El archivo producido cumple los criterios del TASK_LIST.md para esa tarea?
  Si no: documentar que falta en NOTA_PENDIENTE.md dentro de la temp/

PASO 7 — COPIAR A DESTINO FINAL
  Copiar el archivo terminado a la carpeta DESTINO_FINAL del WORK_INDEX
  Nombre del archivo: [nombre]_V4_[version].md (o .py, .rs, segun corresponda)
  Encabezado obligatorio del archivo:
    ## Autor: [ALUMNO_ID] · [FECHA]
    ## Tarea: [TASK_ID] — [descripcion]
    ## Sistema: MPAT4

PASO 8 — MARCAR COMO BORRAR EN TEMP
  Renombrar el archivo original en temp/ a BORRAR_[nombre_original]
  Esto marca que ya fue copiado y procesado

PASO 9 — ACTUALIZAR WORK_INDEX
  ESTADO        → COMPLETADA
  DESTINO_FINAL → [carpeta donde quedo el archivo]
  TEMP_PATH     → (dejar el path para auditoria, no borrar el registro)

PASO 10 — EVALUAR SIGUIENTE TAREA
  Tokens > 70% → leer WORK_INDEX, tomar siguiente tarea disponible (volver a PASO 3)
  Tokens < 70% → ejecutar PROTOCOLO DE CIERRE DE SESION
```

### CIERRE DE SESION (tokens bajos o fin de trabajo)

```
PASO 11 — PROTOCOLO DE CIERRE
  Si hay tarea EN_TRABAJO sin terminar:
    a) Guardar el avance parcial en la carpeta temp/
    b) Crear ESTADO_PARCIAL.md en la temp/ con:
       - Que se hizo
       - Que falta
       - Archivos generados hasta ahora
       - Siguiente paso concreto para quien retome
    c) En WORK_INDEX: dejar EN_TRABAJO (no cambiar a HUERFANA — eso es automatico a las 24hs)
    d) Actualizar la columna INICIO con la ultima vez que se toco

  Si todas las tareas tomadas estan COMPLETADAS:
    a) No hay trabajo pendiente — cerrar normalmente

PASO 12 — MENSAJE AL GRUPO
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    RELAY-LIFECYCLE · CIERRE DE SESION
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Alumno:            [ALUMNO_ID]
    Tareas completadas:[TASK_IDs]
    Tareas en curso:   [TASK_ID o ninguna]
    Temp activa:       [path o ninguna]
    Siguiente libre:   [TASK_ID — descripcion]
    Huerfanas activas: [lista o ninguna]
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### RESCATE DE TAREA HUERFANA (Alumno C)

```
CUANDO RESCATAR:
  El alumno ve en WORK_INDEX una tarea con ESTADO=EN_TRABAJO
  cuyo campo INICIO tiene mas de 24 horas de antiguedad.
  Esa tarea es HUERFANA aunque el indice no lo diga todavia.

PROTOCOLO DE RESCATE:
  1. Marcar la tarea como HUERFANA en WORK_INDEX (actualizar estado)
  2. Leer el contenido de la TEMP_PATH de la tarea huerfana
  3. Leer ESTADO_PARCIAL.md si existe — es el mapa del trabajo anterior
  4. Crear nueva carpeta temp: temp/[ALUMNO_RESCATE]_[FECHA]_[HORA]/
  5. Copiar el trabajo parcial de la temp huerfana a la nueva temp
  6. Actualizar WORK_INDEX: ESTADO=EN_TRABAJO, ALUMNO_ID=[nuevo], TEMP_PATH=[nueva]
  7. Continuar desde donde se dejo segun ESTADO_PARCIAL.md
  8. Al completar: la temp huerfana original se renombra BORRAR_ en su lugar
```

### MOVIMIENTO A DESCARTE

```
CUANDO MOVER A DESCARTE:
  Condicion A: el archivo esta COMPLETADA + copiado a destino final
               + la temp tiene sus archivos renombrados BORRAR_
  Condicion B: el archivo fue evaluado como obsoleto (no aplica a V4)

PROTOCOLO:
  1. Verificar que el archivo destino existe y tiene contenido correcto
  2. Mover los archivos BORRAR_ de la temp/ a descarte/
  3. Registrar en WORK_INDEX columna extra: DESCARTE=[fecha]
  4. La carpeta temp/ queda vacia — se puede eliminar
  ⛔ NUNCA mover a descarte sin verificar que el destino final existe
```

---

## Reglas de calidad

| Regla | Consecuencia si se viola |
|---|---|
| WORK_INDEX actualizado antes de empezar a trabajar | Otro alumno puede tomar la misma tarea |
| Una sola tarea EN_TRABAJO por alumno | Confusion de contexto, trabajo perdido |
| Evaluar tokens ANTES de tomar tarea nueva | Tarea queda huerfana innecesariamente |
| ESTADO_PARCIAL.md al dejar tarea incompleta | El siguiente alumno no sabe por donde seguir |
| Copiar a destino ANTES de marcar BORRAR_ | Perdida de trabajo |
| TEMP_PATH siempre con patron NOMBRE_FECHA_HORA | Imposible encontrar trabajo de otro alumno |

---

## IDs de carpetas Drive

| Carpeta | ID |
|---|---|
| MPAT4 raiz | 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI |
| relay/temporal/ | 1QehAmh2U7brtnHMDYRuR-SQUDCJyPJVu |
| deprecated/ | 14b47yd91-ebxV_rp_HVkndp0JKKthF2m |

> El docente agrega los IDs de temp/ y descarte/ antes de distribuir.

---

*relay-lifecycle.skill · V1_00 · AGT 2026-05-20*
