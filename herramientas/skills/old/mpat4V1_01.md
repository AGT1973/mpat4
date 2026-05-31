---
name: mpat4-alumno
version: V1_01
description: >
  Bootstrap y router local MPAT4. Activar con CUALQUIER frase de trabajo:
  '.', 'continuar', 'seguimos', 'retomar mpat4', 'siguiente pendiente',
  'tomar tarea', 'hay tareas huerfanas', 'migrar', 'continuar migracion',
  'hay lotes huerfanos', 'investigar tecnologia', 'tech radar', 'evaluar framework',
  'implementar modulo', 'escribir codigo', 'implementar en rust', 'bridge ffi'.
  Este skill identifica al alumno, verifica el MCP MPAT4, detecta el contexto,
  carga la skill correcta desde Drive por ID, verifica la carga, y transfiere
  el control. Una sola instalacion por alumno. Nunca reinstalar.
  SIEMPRE leer desde Drive. NUNCA operar desde memoria.
requires:
  - Google Drive MCP (conector oficial Claude.ai)
  - MCP MPAT4 local (mcp_mpat4.py corriendo en la maquina del alumno)
install: una sola vez — el docente actualiza las skills en Drive sin que el alumno reinstale
---

# MPAT4 Alumno — Bootstrap y Router de Skills · V1_01

---

## QUE HACE ESTE SKILL

Este es el unico archivo que cada alumno instala en su Claude.ai.

Su trabajo:
```
1. Identificar al alumno (ALUMNO_ID)
2. Verificar que el MCP MPAT4 esta activo
3. Detectar que tipo de trabajo viene a hacer el alumno
4. Cargar desde Drive la skill correcta para esa tarea
5. Verificar que la carga fue exitosa
6. Transferir el control a esa skill con ALUMNO_ID ya registrado
```

Cuando el docente actualiza cualquiera de las skills (A, B, C, D o la
principal), el alumno no reinstala nada. La proxima sesion este bootstrap
la lee desde Drive automaticamente.

---

## MAPA DE SKILLS EN DRIVE

```
SKILL PRINCIPAL — relay general MPAT4
  Archivo: SKILL_V4_12_en_gdrive.md
  ID:      1W-HaIBSzUbRZmQt4OFkvmrqC3uUJkvGD

SKILL A — relay-lifecycle (ciclo de vida de tareas del grupo)
  Archivo: relay-lifecycle.skill
  ID:      18wM1X5djvheqWx5v4bv2aYXqlTvdOEiO

SKILL B — mpat3-to-mpat4 (migracion por lotes)
  Archivo: mpat3-to-mpat4.skill
  ID:      1lLECsKOTme5h3Em7U1F6nteas-G-Ypt6

SKILL C — tech-research (investigacion de tecnologias)
  Archivo: tech-research.skill
  ID:      1UDq8sZynJQXTM4iidw62JSlkUngwO7Zo

SKILL D — python-rust-production (produccion de codigo)
  Archivo: python-rust-production.skill
  ID:      1DHcnOC_KN1vzsEJkLiP5qbBsDS9Qx7eE

Todas en carpeta: mpat/herramientas/skills/
ID carpeta:       1rrDNblne6P_IwpCnDfmAHKen4KUuua4f
```

---

## SECUENCIA DE ARRANQUE — EJECUTAR SIEMPRE EN ORDEN

### PASO 0 — IDENTIFICACION DEL ALUMNO

```
Preguntar: "Nombre o email para registrar tu trabajo en MPAT4?"
Guardar como ALUMNO_ID.
⛔ No avanzar sin ALUMNO_ID confirmado.
```

---

### PASO 1 — VERIFICAR MCP MPAT4

```
Llamar: mcp_mpat4.list_paths("mpat/mpat4/")

RESULTADO OK — responde con lista de rutas:
  Informar: "MCP MPAT4 activo — [N] rutas cargadas."
  Continuar a PASO 2.

RESULTADO ERROR — no responde o falla:
  Informar al alumno exactamente esto:
  ┌─────────────────────────────────────────────────────┐
  │ El MCP MPAT4 no esta activo.                        │
  │ Para activarlo:                                     │
  │   1. Abrir una terminal                             │
  │   2. Ejecutar: python /ruta/a/mcp_mpat4.py          │
  │   3. Reiniciar esta conversacion                    │
  │                                                     │
  │ Si no tenes el archivo mcp_mpat4.py:                │
  │   Descargarlo desde Drive:                          │
  │   mpat/herramientas/mcps/mcp_mpat4.py               │
  │   ID: 1S7ps8Obi9s14hix1-rRBfsRYwg0Olr8U            │
  └─────────────────────────────────────────────────────┘
  ⛔ No continuar sin MCP MPAT4 activo.
  ⛔ No operar con IDs hardcodeados como reemplazo del MCP.
```

---

### PASO 2 — DETECTAR CONTEXTO Y ELEGIR SKILL

```
Leer lo que el alumno escribio para activar este skill.
Aplicar esta tabla de deteccion en orden — primera coincidencia gana:

TRIGGER DETECTADO                          → SKILL A CARGAR
─────────────────────────────────────────────────────────────
"tomar tarea"                              → SKILL A (relay-lifecycle)
"hay tareas huerfanas"                     → SKILL A (relay-lifecycle)
"continuar tarea"                          → SKILL A (relay-lifecycle)
"cerrar tarea"                             → SKILL A (relay-lifecycle)
"ver estado de tareas"                     → SKILL A (relay-lifecycle)
"rescatar tarea"                           → SKILL A (relay-lifecycle)
─────────────────────────────────────────────────────────────
"migrar"                                   → SKILL B (mpat3-to-mpat4)
"continuar migracion"                      → SKILL B (mpat3-to-mpat4)
"tomar lote"                               → SKILL B (mpat3-to-mpat4)
"hay lotes huerfanos"                      → SKILL B (mpat3-to-mpat4)
"lote de migracion"                        → SKILL B (mpat3-to-mpat4)
─────────────────────────────────────────────────────────────
"investigar tecnologia"                    → SKILL C (tech-research)
"tech radar"                               → SKILL C (tech-research)
"evaluar framework"                        → SKILL C (tech-research)
"evaluar node"                             → SKILL C (tech-research)
"evaluar django"                           → SKILL C (tech-research)
"evaluar flask"                            → SKILL C (tech-research)
"evaluar fastapi"                          → SKILL C (tech-research)
"novedades para v4"                        → SKILL C (tech-research)
"investigar stack"                         → SKILL C (tech-research)
─────────────────────────────────────────────────────────────
"implementar modulo"                       → SKILL D (python-rust-production)
"escribir codigo"                          → SKILL D (python-rust-production)
"implementar en rust"                      → SKILL D (python-rust-production)
"implementar en python"                    → SKILL D (python-rust-production)
"bridge ffi"                               → SKILL D (python-rust-production)
"hot path"                                 → SKILL D (python-rust-production)
"crear parser"                             → SKILL D (python-rust-production)
"crear codec"                              → SKILL D (python-rust-production)
─────────────────────────────────────────────────────────────
"." / "continuar" / "seguimos"             → SKILL PRINCIPAL (mpat4-relay)
"continuar con mpat4" / "retomar mpat4"    → SKILL PRINCIPAL (mpat4-relay)
"siguiente pendiente"                      → SKILL PRINCIPAL (mpat4-relay)
─────────────────────────────────────────────────────────────
NINGUN TRIGGER CLARO                       → PREGUNTAR (ver abajo)

SI NO HAY TRIGGER CLARO:
  Preguntar:
  "Que vas a hacer hoy en MPAT4?
   a) Trabajo general de relay (continuar donde quedo el proyecto)
   b) Gestionar tareas del grupo (tomar, cerrar, rescatar)
   c) Migrar archivos de MPAT3 a MPAT4
   d) Investigar una tecnologia nueva
   e) Escribir codigo Python o Rust"
  Esperar respuesta y mapear a la skill correspondiente.
```

---

### PASO 3 — CARGAR SKILL DESDE DRIVE

```
Segun la decision del PASO 2, ejecutar la carga correspondiente:

SKILL PRINCIPAL:
  Llamar: Google Drive:download_file_content
    fileId: "1W-HaIBSzUbRZmQt4OFkvmrqC3uUJkvGD"

SKILL A:
  Llamar: Google Drive:download_file_content
    fileId: "18wM1X5djvheqWx5v4bv2aYXqlTvdOEiO"

SKILL B:
  Llamar: Google Drive:download_file_content
    fileId: "1lLECsKOTme5h3Em7U1F6nteas-G-Ypt6"

SKILL C:
  Llamar: Google Drive:download_file_content
    fileId: "1UDq8sZynJQXTM4iidw62JSlkUngwO7Zo"

SKILL D:
  Llamar: Google Drive:download_file_content
    fileId: "1DHcnOC_KN1vzsEJkLiP5qbBsDS9Qx7eE"
```

---

### PASO 4 — VERIFICAR CARGA

```
VERIFICACION OBLIGATORIA. No asumir que la carga fue correcta.

CHEQUEO 1 — El archivo se recibio?
  El contenido descargado tiene mas de 100 caracteres?
  Si no → fallo silencioso. Ver tabla de errores.

CHEQUEO 2 — Es la skill correcta?
  El contenido incluye el campo "name:" en el encabezado YAML?
  El valor coincide con la skill solicitada?
    SKILL PRINCIPAL → name: mpat4-relay
    SKILL A         → name: relay-lifecycle
    SKILL B         → name: mpat3-to-mpat4
    SKILL C         → name: tech-research
    SKILL D         → name: python-rust-production
  Si no coincide → carga incorrecta. Ver tabla de errores.

CHEQUEO 3 — Tiene reglas?
  El contenido incluye al menos una linea con "NUNCA"?
  Si no → archivo corrupto o incompleto. Ver tabla de errores.

SI TODOS LOS CHEQUEOS PASAN:
  Informar:
  ┌─────────────────────────────────────────────────────┐
  │ Skill cargada: [valor del campo name:]              │
  │ Alumno:        [ALUMNO_ID]                          │
  │ MCP MPAT4:     activo                               │
  │ Estado:        LISTO                                │
  └─────────────────────────────────────────────────────┘
  Continuar a PASO 5.

SI ALGUN CHEQUEO FALLA:
  Ver tabla de errores al final de este skill.
  ⛔ No continuar con skill incompleta o incorrecta.
  ⛔ No inventar reglas del proyecto desde memoria.
```

---

### PASO 5 — TRANSFERIR CONTROL

```
La skill cargada toma el control completo de la sesion.
Pasar como datos ya resueltos:
  ALUMNO_ID: [el que se capturo en PASO 0]
  MCP_STATUS: activo (verificado en PASO 1)

La skill cargada NO vuelve a preguntar el nombre — ya esta registrado.

Este skill queda en segundo plano y se reactiva solo si:
  a) El alumno escribe un trigger de una skill distinta a la activa
  b) Ocurre un error de Drive durante la sesion
```

---

### CAMBIO DE SKILL EN MID-SESION

```
Si durante la sesion el alumno escribe un trigger de otra skill:

  Ejemplo: esta en SKILL D y escribe "investigar tecnologia"

  PROTOCOLO:
    1. Preguntar: "Estas trabajando con [skill actual].
                  Queres cambiar a [skill nueva]?
                  El trabajo actual queda guardado donde esta."
    2. Si confirma:
       a) Ejecutar PASO 3 con el ID de la nueva skill
       b) Ejecutar PASO 4 (verificacion)
       c) Transferir control a la nueva skill
    3. Si no confirma: continuar con la skill actual.

  ⛔ No cambiar de skill sin confirmacion del alumno.
  ⛔ No perder el contexto del trabajo en curso al cambiar.
```

---

## TABLA DE ERRORES Y SOLUCIONES

| Error | Causa probable | Accion |
|---|---|---|
| MCP MPAT4 no responde | Servidor no iniciado | Dar instrucciones del PASO 1 |
| MCP Drive no accesible | Conector desconectado | Claude.ai → Herramientas → Google Drive |
| fileId no encontrado | ID desactualizado | Buscar en carpeta 1rrDNblne6P_IwpCnDfmAHKen4KUuua4f |
| Contenido menor a 100 chars | Fallo silencioso de Drive | Reintentar la descarga una vez |
| name: no coincide | Archivo equivocado descargado | Verificar ID en MAPA DE SKILLS arriba |
| Sin lineas con NUNCA | Archivo corrupto o vacio | Avisar al docente: ai.mpat.designer@gmail.com |
| Sin permisos de lectura | Alumno sin acceso a herramientas/ | Avisar al docente para otorgar permisos |

---

## NOTA PARA EL ALUMNO

Este es el unico archivo que necesitas instalar. Una vez instalado:

- Escribi lo que vas a hacer y Claude elige la skill correcta
- Si el contexto no es claro, te pregunta con 5 opciones
- Si el docente actualiza las reglas, las tenes automaticamente en la proxima sesion
- Si algo falla, este skill te dice exactamente que hacer y a quien avisar

No necesitas saber cual skill usar ni que ID tiene cada archivo.
Solo decir que vas a hacer hoy.

---

*skill_alumno.skill · V1_01 · AGT 2026-05-20*
*que has usado el formato de razonamiento adaptado por AGT*
