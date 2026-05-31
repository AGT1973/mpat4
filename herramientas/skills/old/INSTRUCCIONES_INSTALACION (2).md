# Cómo instalar los Skills MPAT4 en tu Claude.ai · V4_12

## Qué son estos skills

Son las herramientas que guían tu trabajo en el proyecto MPAT4.
Cuando decís "continuar" o "seguimos", Claude sabe exactamente
qué hacer: leer el estado del proyecto, tomar el trabajo pendiente,
clasificar el código por lenguaje (Python o Rust), generar los
artefactos correctos y guardarlos firmados.

Los instalás **una sola vez**. Si el docente actualiza las instrucciones,
tu skill las lee automáticamente desde Drive — sin reinstalar.

---

## Skills disponibles — instalar según tu tarea

| Skill | Cuándo instalarlo | Archivo |
|---|---|---|
| **mpat4-relay** | Siempre — trabajo general en MPAT4 | `SKILL_V4_12_en_gdrive.md` |
| **relay-lifecycle** | Cuando gestionás tareas del grupo | `relay-lifecycle.skill` |
| **mpat3-to-mpat4** | Cuando migrás archivos de MPAT3 | `mpat3-to-mpat4.skill` |

Los skills `tech-research` y `python-rust-production` estarán disponibles próximamente.

---

## Paso 1 — Tener el MCP de Google Drive activo

Antes de instalar cualquier skill, confirmá que tenés el MCP de Google Drive
conectado en Claude.ai.

En Claude.ai → menú lateral → **Herramientas** → verificar que
"Google Drive" aparece activo.

---

## Paso 2 — Instalar el MCP MPAT4 (una sola vez, en tu máquina)

El MCP MPAT4 es un servidor local que resuelve rutas semánticas a IDs de Drive.
Solo lo instalan alumnos que trabajan en módulos con código (Python o Rust).

1. Descargar `mcp_mpat4.py` desde `mpat/herramientas/mcps/`
2. Instalar dependencias:
   ```
   pip install mcp
   ```
3. Agregar en la configuración MCP de Claude Desktop (`claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "mcp-mpat4": {
         "command": "python",
         "args": ["/ruta/a/mcp_mpat4.py"]
       }
     }
   }
   ```
4. Reiniciar Claude Desktop.

Si ves el MCP `mcp-mpat4` en la lista de herramientas, está funcionando.

---

## Paso 3 — Descargar e instalar los skills

1. Descargar los archivos `.skill` y `.md` desde `mpat/herramientas/skills/`
2. En **claude.ai**:
   - Click en tu avatar (esquina superior derecha)
   - **Preferencias** → **Personalizar**
   - Sección **Skills** → **Agregar skill**
   - Subir el archivo
   - Confirmar instalación

Repetir para cada skill que necesites.

---

## Paso 4 — Verificar

Abrí una nueva conversación en Claude.ai y escribí:

```
continuar con mpat4
```

Claude debería responder preguntando tu nombre o email.
Si lo hace, el skill está funcionando.

---

## Triggers — cómo activar cada skill

**mpat4-relay** (trabajo general):
`.` · `continuar` · `continuar con mpat4` · `seguimos` · `retomar mpat4`

**relay-lifecycle** (tareas del grupo):
`tomar tarea` · `ver estado de tareas` · `hay tareas huérfanas` · `cerrar tarea`

**mpat3-to-mpat4** (migración):
`migrar` · `tomar lote de migración` · `continuar migración` · `hay lotes huérfanos`

---

## Stack del proyecto — V4_12

El proyecto usa **Python + Rust**. No es necesario saber Rust para empezar —
los primeros módulos son Python puro. Rust aparece gradualmente en los
módulos de performance crítica.

```
Python 3.14  → lógica de agentes, orquestación, schemas, FastAPI
Rust (stable) → parsers, codecs, hot paths, memoria controlada
PyO3         → puente FFI entre Python y Rust
```

---

## Problemas frecuentes

**"No encuentro la sección Skills en Preferencias"**
→ Verificar que tu cuenta tiene acceso a Skills (feature en rollout).
Contactar al docente si no aparece.

**"Claude no reacciona al skill"**
→ Verificar que el MCP de Google Drive está activo en esa conversación.
→ Intentar con el trigger explícito: "continuar con mpat4".

**"Error al guardar archivos en Drive"**
→ El docente debe darte permisos de escritura en la carpeta MPAT4.
Contactar a: ai.mpat.designer@gmail.com

**"El MCP retorna PENDIENTE_CREAR para una carpeta Rust"**
→ Esa carpeta aún no existe en Drive. Ver instrucciones en READMEinstalacion.md
en la carpeta mcps/.
