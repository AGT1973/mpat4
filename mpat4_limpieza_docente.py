#!/usr/bin/env python3
"""
mpat4_limpieza_docente.py
Script de limpieza y organización Drive — ejecutar ANTES de dar prompt a alumnos
Autor: generado por auditoría MPAT4 · 2026-05-31
Sistema: MPAT4 — Infraestructura Cognitiva Distribuida

REQUISITOS:
  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

AUTENTICACIÓN:
  1. Ir a Google Cloud Console → APIs & Services → Credentials
  2. Crear OAuth 2.0 Client ID (Desktop app)
  3. Descargar credentials.json y ponerlo en el mismo directorio
  4. Primera ejecución: abrirá browser para autorizar
  5. Genera token.json para ejecuciones siguientes

USO:
  python mpat4_limpieza_docente.py --dry-run    # solo muestra qué haría
  python mpat4_limpieza_docente.py --ejecutar   # ejecuta los movimientos

IMPORTANTE: Ejecutar --dry-run primero. Revisar output antes de --ejecutar.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Optional

# ---------------------------------------------------------------------------
# Dependencias opcionales — avisar si no están
# ---------------------------------------------------------------------------
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_LIBS = True
except ImportError:
    GOOGLE_LIBS = False

# ---------------------------------------------------------------------------
# IDs de carpetas canónicas
# ---------------------------------------------------------------------------

DROP_ZONE          = "1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI"
RELAY_ACTIVE       = "1DN0-L3tjW0TVPy2EaAU40aUsUpcJ2aXQ"
RELAY_TEMPORAL     = "1uC3StJMvPpOizTZOa_OyKPt12oIzTLe_"
CONTRACTS          = "1589CC4tPfBkCUndlsVQeT9c9aYTSeaM0"
RESOLUCIONES       = "1IaeQLsxhjoNctFWf3PEP4OeBz4GfFHHZ"
INVESTIGACIONES    = "1vZzX0ouJOwPMIRFpX-U6TeBVzxNS5V1G"
ARTIFACTS_FOLDER   = "1Y02GMJ9CPp4_qmDliZkKQr0mP28rFjv0"  # carpeta raíz MPAT4

# Carpetas que el worker crea / ya deben existir en Drive:
# Si no existen, el script las crea automáticamente bajo ARTIFACTS_FOLDER.
DESTINO_SCHEMAS    = None   # se resuelve en runtime: busca "schemas" bajo raíz
DESTINO_TESTS      = None   # busca "tests" bajo raíz
DESTINO_CORE       = None   # busca "core" bajo raíz
DESTINO_DEPLOYMENT = None   # busca "deployment" bajo raíz
DESTINO_ECOSYSTEM  = None   # busca "ecosystem" bajo raíz

SCOPES = ["https://www.googleapis.com/auth/drive"]

# ---------------------------------------------------------------------------
# Plan de acciones — construido desde la auditoría
# ---------------------------------------------------------------------------

# Formato: (file_id, nombre_actual, destino_carpeta_id_o_nombre, accion, nota)
# accion: "mover" | "marcar_descarte" | "verificar" | "crear_alias"

PLAN_ACCIONES = [
    # -----------------------------------------------------------------------
    # 1. MOVER artefactos de Drop Zone a destino correcto
    # -----------------------------------------------------------------------
    {
        "file_id":   "1vpzQOiYMKlc38W5kXmwCS-JGOPv1foZz",
        "nombre":    "_TECNICA_RELAY_036_ARIEL.md",
        "destino_id": RELAY_ACTIVE,
        "destino_nombre": "relay/active/",
        "accion":    "mover",
        "nota":      "Relay ARIEL 036 — producido hoy, en Drop Zone",
    },
    {
        "file_id":   "1PXZ2lQK0fZtQKlpc3ddLHXZpDe-11Bjr",
        "nombre":    "_TECNICA_RELAY_033_MPAT.md",
        "destino_id": RELAY_ACTIVE,
        "destino_nombre": "relay/active/",
        "accion":    "mover",
        "nota":      "Relay MPAT 033 — producido hoy, en Drop Zone",
    },
    {
        "file_id":   "1y9LfBoidrIOukTB3GrumNSjPAu-EAZOk",
        "nombre":    "_TECNICA_RELAY_026_AGT.md",
        "destino_id": RELAY_ACTIVE,
        "destino_nombre": "relay/active/",
        "accion":    "mover",
        "nota":      "Relay AGT 026 — producido hoy, en Drop Zone",
    },
    {
        "file_id":   "1W4jpBNcQ3cUI6sOMvbIAVh8yCMpHC1Kv",
        "nombre":    "RELAY_NEXT_POINTER_V3_02_R026.md",
        "destino_id": RELAY_ACTIVE,
        "destino_nombre": "relay/active/",
        "accion":    "mover",
        "nota":      "Pointer R026 AGT — en Drop Zone",
    },
    {
        "file_id":   "1sp5b7WtSQX7m_OWtNlCsrdMhz_Pr7aim",
        "nombre":    "CONTRACT_RES185_V4_01.md",
        "destino_id": CONTRACTS,
        "destino_nombre": "contracts/",
        "accion":    "mover",
        "nota":      "Contrato RES.185 Agent Reputation System — en Drop Zone",
    },
    {
        "file_id":   "1UPEaMyqlkjpZmeC1k3JiJRHHDzs0igNO",
        "nombre":    "reputation_system.py",
        "destino_id": None,  # necesita subcarpeta ecosystem/reputation/
        "destino_nombre": "ecosystem/reputation/",
        "accion":    "mover_subcarpeta",
        "nota":      "Implementación RES.185 — crear ecosystem/reputation/ si no existe",
    },
    {
        "file_id":   "1xaTniKRQC-HiacHp9kNETqGPgciMMNGL",
        "nombre":    "schema_res185.py",
        "destino_id": None,  # subcarpeta schemas/
        "destino_nombre": "schemas/",
        "accion":    "mover_subcarpeta",
        "nota":      "Schema Pydantic RES.185 — mover a schemas/",
    },
    {
        "file_id":   "1kf-AaPKwOjxFi8J6oL3b5sZskeG4axFm",
        "nombre":    "test_reputation_system.py",
        "destino_id": None,
        "destino_nombre": "tests/",
        "accion":    "mover_subcarpeta",
        "nota":      "Tests RES.185 — mover a tests/",
    },
    {
        "file_id":   "1TVkN-F0sOU11nop0_UzDRbt7q0Lixp2m",
        "nombre":    "test_cognition_eventbus_integration_DT_COG_002.py",
        "destino_id": None,
        "destino_nombre": "artifacts/",
        "accion":    "mover_subcarpeta",
        "nota":      "Test integración DT-COG-002 — mover a artifacts/",
    },
    {
        "file_id":   "15EQdj2rjUeWByq5h9MwXIdpN1rqkQB4O",
        "nombre":    "mpat4_worker_v2.py",
        "destino_id": None,
        "destino_nombre": "deployment/",
        "accion":    "mover_subcarpeta",
        "nota":      "Worker v2 — mover a deployment/",
    },

    # -----------------------------------------------------------------------
    # 2. ELIMINAR / MARCAR DESCARTE
    # -----------------------------------------------------------------------
    {
        "file_id":   "12OxGZr3_JqgfLa0VF_hW3ZT9-0jbrfzILMZme65TXJAg",
        "nombre":    "gdoc obsoleto en informes/",
        "destino_id": None,
        "destino_nombre": "TRASH",
        "accion":    "eliminar",
        "nota":      "PM-001: gdoc obsoleto confirmado por docente en auditoría R026",
    },
    {
        "file_id":   "1gP96eP_z9ekGEUm9AsbvdJ4mjERGumhg",
        "nombre":    "carpeta ./borrar (gdocs obsoletos)",
        "destino_id": None,
        "destino_nombre": "TRASH",
        "accion":    "eliminar_carpeta",
        "nota":      "Carpeta de descarte acumulada — admin elimina contenido completo",
    },

    # -----------------------------------------------------------------------
    # 3. VERIFICAR / RENOMBRAR (DT-PERM-001)
    # -----------------------------------------------------------------------
    {
        "file_id":   None,
        "nombre":    "CONTRACT_RES181_*.md / CONTRACT_RES182_*.md / CONTRACT_RES180_IDENTITY_*.md",
        "destino_id": None,
        "destino_nombre": "contracts/",
        "accion":    "renombrar_manual",
        "nota":      (
            "DT-PERM-001: estos contratos tienen cabeceras con número RES incorrecto.\n"
            "  CONTRACT_RES181 previos → contenido de RES.211 (Browser Operators) — renombrar a CONTRACT_RES211_*.md\n"
            "  CONTRACT_RES182 previos → contenido de RES.220 (Multimodal Cognition) — renombrar a CONTRACT_RES220_*.md\n"
            "  CONTRACT_RES180_IDENTITY → cabecera dice RES.168, canónico dice RES.180 → dejar como está, corregir cabecera interna\n"
            "  ACCIÓN: editar cabecera '# RES.168' → '# RES.180' en agent_identity.py y agent_identity_schema.py"
        ),
    },
    {
        "file_id":   None,
        "nombre":    "CONTRACT_RES180_V1.md vs CONTRACT_RES180_v1.md vs CONTRACT_RES180_V4_01.md",
        "destino_id": None,
        "destino_nombre": "contracts/",
        "accion":    "unificar_manual",
        "nota":      (
            "Tres versiones de FederatedMeshNode en contracts/.\n"
            "  Canónico: CONTRACT_RES180_V4_01.md (ai.mpat.info, más completo)\n"
            "  Marcar para descarte: CONTRACT_RES180_V1.md (cursos.agt, versión anterior)\n"
            "  Marcar para descarte: CONTRACT_RES180_v1.md (cursos.agt, duplicado)\n"
            "  ACCIÓN: mover las dos versiones anteriores a relay/descarte/ con prefijo OBSOLETO_"
        ),
    },

    # -----------------------------------------------------------------------
    # 4. CREAR — RELAY_INDEX_CADENAS.md (INV-CADENAS-001)
    # -----------------------------------------------------------------------
    {
        "file_id":   None,
        "nombre":    "RELAY_INDEX_CADENAS.md",
        "destino_id": RELAY_ACTIVE,
        "destino_nombre": "relay/",
        "accion":    "crear_manual",
        "nota":      (
            "INV-CADENAS-001: múltiples alumnos reportan necesidad de índice de cadenas de relays.\n"
            "  Contenido mínimo: tabla relay_NNN → alumno → fecha → módulo → estado\n"
            "  Cubrir: 001–036 conocidos. Ver relay/active/ y relay/temporal/ para completar.\n"
            "  ACCIÓN: docente genera y sube a relay/ antes de próxima sesión"
        ),
    },
]

# ---------------------------------------------------------------------------
# Helpers de autenticación
# ---------------------------------------------------------------------------

def autenticar() -> object:
    """Autentica con OAuth2 y retorna el servicio Drive."""
    if not GOOGLE_LIBS:
        print("ERROR: Instalar dependencias:")
        print("  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        sys.exit(1)

    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                print("ERROR: No se encontró credentials.json")
                print("  Descargar desde Google Cloud Console → APIs & Services → Credentials")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)

# ---------------------------------------------------------------------------
# Operaciones Drive
# ---------------------------------------------------------------------------

def mover_archivo(service, file_id: str, destino_folder_id: str, nombre: str, dry_run: bool) -> bool:
    """Mueve un archivo a una carpeta destino."""
    if dry_run:
        print(f"  [DRY-RUN] MOVER: {nombre} → {destino_folder_id}")
        return True
    try:
        # Obtener parent actual
        file = service.files().get(fileId=file_id, fields="parents").execute()
        prev_parents = ",".join(file.get("parents", []))
        # Mover
        service.files().update(
            fileId=file_id,
            addParents=destino_folder_id,
            removeParents=prev_parents,
            fields="id, parents",
        ).execute()
        print(f"  ✓ MOVIDO: {nombre} → {destino_folder_id}")
        return True
    except HttpError as e:
        print(f"  ✗ ERROR moviendo {nombre}: {e}")
        return False

def buscar_carpeta(service, nombre_carpeta: str, parent_id: str) -> Optional[str]:
    """Busca una carpeta por nombre dentro de un parent. Retorna ID o None."""
    query = (
        f"name = '{nombre_carpeta}' "
        f"and mimeType = 'application/vnd.google-apps.folder' "
        f"and '{parent_id}' in parents "
        f"and trashed = false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    return files[0]["id"] if files else None

def crear_carpeta(service, nombre_carpeta: str, parent_id: str, dry_run: bool) -> Optional[str]:
    """Crea una carpeta. Retorna el ID creado."""
    if dry_run:
        print(f"  [DRY-RUN] CREAR CARPETA: {nombre_carpeta} en {parent_id}")
        return "dry-run-id"
    try:
        meta = {
            "name": nombre_carpeta,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        }
        folder = service.files().create(body=meta, fields="id").execute()
        print(f"  ✓ CARPETA CREADA: {nombre_carpeta} (ID: {folder['id']})")
        return folder["id"]
    except HttpError as e:
        print(f"  ✗ ERROR creando carpeta {nombre_carpeta}: {e}")
        return None

def eliminar_archivo(service, file_id: str, nombre: str, dry_run: bool) -> bool:
    """Mueve a papelera (trashea) un archivo."""
    if dry_run:
        print(f"  [DRY-RUN] ELIMINAR (trash): {nombre} ({file_id})")
        return True
    try:
        service.files().update(fileId=file_id, body={"trashed": True}).execute()
        print(f"  ✓ ELIMINADO (trash): {nombre}")
        return True
    except HttpError as e:
        print(f"  ✗ ERROR eliminando {nombre}: {e}")
        return False

# ---------------------------------------------------------------------------
# Resolver destinos de subcarpetas
# ---------------------------------------------------------------------------

SUBCARPETA_MAP = {
    "schemas/":                  "schemas",
    "tests/":                    "tests",
    "artifacts/":                "artifacts",
    "deployment/":               "deployment",
    "ecosystem/reputation/":     ("ecosystem", "reputation"),
    "core/":                     "core",
}

def resolver_destino_subcarpeta(service, destino_nombre: str, dry_run: bool) -> Optional[str]:
    """Resuelve o crea la carpeta destino a partir del nombre de vfolder."""
    ruta = SUBCARPETA_MAP.get(destino_nombre)
    if ruta is None:
        print(f"  [WARN] destino_nombre '{destino_nombre}' no mapeado — skip")
        return None

    if isinstance(ruta, tuple):
        # Ruta anidada: primero resolver parent
        parent_nombre, hijo_nombre = ruta
        parent_id = buscar_carpeta(service, parent_nombre, ARTIFACTS_FOLDER)
        if not parent_id:
            parent_id = crear_carpeta(service, parent_nombre, ARTIFACTS_FOLDER, dry_run)
        if not parent_id or parent_id == "dry-run-id":
            return parent_id
        folder_id = buscar_carpeta(service, hijo_nombre, parent_id)
        if not folder_id:
            folder_id = crear_carpeta(service, hijo_nombre, parent_id, dry_run)
        return folder_id
    else:
        folder_id = buscar_carpeta(service, ruta, ARTIFACTS_FOLDER)
        if not folder_id:
            folder_id = crear_carpeta(service, ruta, ARTIFACTS_FOLDER, dry_run)
        return folder_id

# ---------------------------------------------------------------------------
# Ejecutor principal
# ---------------------------------------------------------------------------

def ejecutar_plan(dry_run: bool) -> None:
    log_lines = [f"# mpat4_limpieza_docente — {'DRY-RUN' if dry_run else 'EJECUCION'} — {datetime.now().isoformat()}\n"]

    service = None if dry_run and not GOOGLE_LIBS else autenticar()

    ok = 0
    skip = 0
    warn = 0

    for i, accion in enumerate(PLAN_ACCIONES, 1):
        print(f"\n[{i}/{len(PLAN_ACCIONES)}] {accion['accion'].upper()}: {accion['nombre']}")
        print(f"  Nota: {accion['nota'][:120]}...")

        if accion["accion"] == "mover":
            if not accion["file_id"]:
                print("  [SKIP] file_id no definido")
                skip += 1
                continue
            resultado = mover_archivo(service, accion["file_id"], accion["destino_id"], accion["nombre"], dry_run)
            ok += 1 if resultado else 0

        elif accion["accion"] == "mover_subcarpeta":
            if not accion["file_id"]:
                print("  [SKIP] file_id no definido")
                skip += 1
                continue
            destino_id = resolver_destino_subcarpeta(service, accion["destino_nombre"], dry_run)
            if destino_id:
                resultado = mover_archivo(service, accion["file_id"], destino_id, accion["nombre"], dry_run)
                ok += 1 if resultado else 0
            else:
                print(f"  [WARN] No se pudo resolver/crear destino para {accion['destino_nombre']}")
                warn += 1

        elif accion["accion"] == "eliminar":
            if not accion["file_id"]:
                print("  [SKIP] file_id no definido")
                skip += 1
                continue
            resultado = eliminar_archivo(service, accion["file_id"], accion["nombre"], dry_run)
            ok += 1 if resultado else 0

        elif accion["accion"] == "eliminar_carpeta":
            print(f"  [MANUAL] Carpeta — eliminar manualmente en Drive: ID {accion['file_id']}")
            print(f"  URL: https://drive.google.com/drive/folders/{accion['file_id']}")
            warn += 1

        elif accion["accion"] in ("renombrar_manual", "unificar_manual", "crear_manual"):
            print(f"  [MANUAL DOCENTE] {accion['nota']}")
            warn += 1

        log_lines.append(f"[{i}] {accion['accion']} | {accion['nombre']} | {'OK' if ok else 'WARN/SKIP'}\n")

    print(f"\n{'='*60}")
    print(f"RESUMEN: {ok} automatizados · {warn} requieren acción manual · {skip} skipped")
    print(f"{'='*60}")

    # Guardar log
    log_file = f"mpat4_limpieza_log_{'dryrun' if dry_run else 'ejecucion'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(log_file, "w") as f:
        f.writelines(log_lines)
    print(f"\nLog guardado: {log_file}")

    if not dry_run:
        print("\n✓ Limpieza ejecutada. Verificar Drive antes de dar prompt a alumnos.")
        print("  Acciones manuales pendientes:")
        for a in PLAN_ACCIONES:
            if a["accion"] in ("renombrar_manual", "unificar_manual", "crear_manual", "eliminar_carpeta"):
                print(f"  → {a['nombre']}: {a['nota'][:80]}")

# ---------------------------------------------------------------------------
# Checklist de verificación post-limpieza (imprime en consola)
# ---------------------------------------------------------------------------

CHECKLIST = """
╔══════════════════════════════════════════════════════════════════╗
║  CHECKLIST POST-LIMPIEZA — verificar antes de dar prompt alumno  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  RELAY                                                           ║
║  [ ] RELAY_027 está en relay/active/ (no en Drop Zone)          ║
║  [ ] RELAY_POINTER_V4_027 en relay/pointer/                     ║
║  [ ] Relays 026/033/036 en relay/active/                        ║
║                                                                  ║
║  CONTRATOS                                                       ║
║  [ ] CONTRACT_RES185 en contracts/                              ║
║  [ ] Contratos RES.181/182 previos renombrados a RES.211/220    ║
║  [ ] Duplicados RES.180 V1/v1 movidos a relay/descarte/         ║
║  [ ] Cabecera RES.168 en identity corregida a RES.180           ║
║                                                                  ║
║  CÓDIGO                                                          ║
║  [ ] reputation_system.py en ecosystem/reputation/              ║
║  [ ] schema_res185.py en schemas/                               ║
║  [ ] test_reputation_system.py en tests/                        ║
║  [ ] test_cognition_eventbus_integration_DT_COG_002.py          ║
║      en artifacts/                                              ║
║  [ ] mpat4_worker_v2.py en deployment/                          ║
║                                                                  ║
║  LIMPIEZA                                                        ║
║  [ ] gdoc PM-001 eliminado (ID: 12OxGZr3...)                   ║
║  [ ] Drop Zone vacía (o solo archivos de hoy que ya se movieron)║
║                                                                  ║
║  PENDIENTES DOCENTE (no bloquean dar prompt)                    ║
║  [ ] RELAY_INDEX_CADENAS.md creado (INV-CADENAS-001)           ║
║  [ ] FUT.31 identity resuelto (XR vs eBPF — decisión docente)  ║
║  [ ] FUT.17 y FUT.18 con número RES definitivo asignado        ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Script de limpieza MPAT4 — ejecutar como docente antes de dar prompt a alumnos"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Solo muestra qué haría, sin ejecutar")
    group.add_argument("--ejecutar", action="store_true", help="Ejecuta los movimientos reales en Drive")
    group.add_argument("--checklist", action="store_true", help="Imprime checklist de verificación manual")
    args = parser.parse_args()

    if args.checklist:
        print(CHECKLIST)
        return

    print(f"\n{'='*60}")
    print(f"  MPAT4 Script de limpieza docente")
    print(f"  Modo: {'DRY-RUN (sin cambios reales)' if args.dry_run else '⚠ EJECUCIÓN REAL'}")
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Acciones planificadas: {len(PLAN_ACCIONES)}")
    print(f"{'='*60}\n")

    if args.ejecutar:
        confirm = input("¿Confirmar ejecución real en Drive? (escribir 'si' para confirmar): ")
        if confirm.strip().lower() != "si":
            print("Abortado.")
            return

    ejecutar_plan(dry_run=args.dry_run)

    if not args.dry_run:
        print(CHECKLIST)

if __name__ == "__main__":
    main()
