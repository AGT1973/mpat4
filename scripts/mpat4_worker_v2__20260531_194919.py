"""
mpat4_worker_v2.py — MPAT4 Root Reorganizer + Drop Zone Worker
# mpat4_worker_v2.py
## Autor: ai.mpat.designer@gmail.com · 2026-05-29
## Modulo: root-reorganizer · Version: V2_00
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida

PROPOSITO:
  Resuelve el problema de 243 archivos sueltos en la raiz de MPAT4.
  Opera sobre el Drive montado localmente (I:\\Mi unidad\\MPAT\\MPAT4\\).
  No requiere API de Google. Solo os, shutil, json, re.

DECISIONES DE DISENO (SOTA — razonadas, no votadas):
  1. Clasificacion por patron de nombre (regex) — mas robusto que extension sola
  2. Deduplicacion por contenido (hash MD5) — no por nombre con _ o __
  3. Archivos marcados borrar_ → _DEPRECATED automaticamente
  4. Solo el RELAY_POINTER mas reciente queda en raiz — el resto va a relay/
  5. Registro auditado en _registro.jsonl — cada movimiento trazable
  6. Carpetas con mismo proposito → unificadas (evolution→research, borrar→_DEPRECATED)
  7. --dry-run simula sin tocar nada — siempre usar primero

COMANDOS:
  python mpat4_worker_v2.py --dry-run        # simula, muestra plan completo
  python mpat4_worker_v2.py                  # ejecuta reorganizacion
  python mpat4_worker_v2.py --drop-only      # solo procesa drop zone (comportamiento v1)
  python mpat4_worker_v2.py --unify-folders  # unifica carpetas duplicadas -
  python mpat4_worker_v2.py --report         # genera reporte del estado actual sin mover

CARPETAS UNIFICADAS (razonamiento):
  evolution/    → research/     (misma semantica: investigacion)
  borrar/       → _DEPRECATED/  (borrar es una intencion, _DEPRECATED es el vfolder)
  pendientes/   → relay/        (pendientes son tareas de relay no cerradas)
  agent_registry/ → core/       (registro de agentes es parte del core)
  reports/      → audits/       (reportes son auditorias)
  test/         → tests/        (singular vs plural — unificar en tests/)
"""

import os
import sys
import re
import shutil
import hashlib
import logging
import json
import argparse
from datetime import datetime
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACION — ajustar si el Drive esta montado en otra letra
# ─────────────────────────────────────────────────────────────────────────────

DRIVE_BASE     = Path(r"I:\Mi unidad\MPAT\MPAT4")
DROPZONE       = DRIVE_BASE / "_DROPZONE"
LOG_FILE       = DROPZONE / "_worker.log"
REGISTRO       = DROPZONE / "_registro.jsonl"
CARPETAS_JSON  = DRIVE_BASE / "herramientas" / "CARPETAS_MPAT4.json"

# ─────────────────────────────────────────────────────────────────────────────
# IDS DE DRIVE — verificados 2026-05-29
# Usados solo para referencia en el registro. El worker opera en filesystem.
# ─────────────────────────────────────────────────────────────────────────────

FOLDER_IDS = {
    "root":             "1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI",
    "relay":            "1DN0-L3tjW0TVPy2EaAU40aUsUpcJ2aXQ",
    "contracts":        "1589CC4tPfBkCUndlsVQeT9c9aYTSeaM0",
    "schemas":          "1N_u01JXjeMlMkNbk7GvV6snQTtnpOipG",
    "core":             "1yvrUM4x8F-Ej84bN1yyJSzmr7zDCTVUC",
    "docs":             "1gEYtc9tX1BeVVLoqutrG0yJGyrqBAia-",
    "tests":            "1WjhY2Ch5YHsKlmVNFczFyownqOkfbnRO",
    "scripts":          "17Fy3Ya8TQWh2uzhSHkusRh577InU_Bvl",
    "research":         "1lrgXcd_s3CxF766lYkTwdoRIeJeUqsHk",
    "audits":           "1deUGx-H5g6XDr4iB603MEvcyKSJACgfk",
    "resolutions":      "1hRfjnUkOyfnfqxLEfBM0CWLLnDBi3GQU",
    "architectures":    "17OW_VQ8PYaxQ69vBUIrzVRD-AE88krnW",
    "artifacts":        "1cvd65sXZsMwdevQrBl0YT9mfBuXN0D-Z",
    "deprecated":       "14b47yd91-ebxV_rp_HVkndp0JKKthF2m",
    "_DEPRECATED":      "1AO3i9bq13ZyNr5Y97pTnAwlLtI5ahbCr",
    "migration":        "17r_pu8X27cYl8sr8a6HoxcbwmfMeMZbl",
    "deployment":       "1l4-fIdx2UAYbRDcIV5a23-bDYfdET8Hs",
    "herramientas":     "1bj3eHn0CSuE_CTGjJ3pG0lGtcVXYmtPg",
    "education":        "1wSoBpZi8pl22n9a4oisFp5vjCXGTcNab",
    "ecosystem":        "170be8bj51aAvByQO-fc7GYDkIKKAwPrM",
    "session_scheduler":"1CAi2DxOCLNq6Z27m498YVfVXedzQX-1C",
    "hydration":        "1jj3T8Aiu8vdqBVbabXI5qtyUpckRk4_V",
    "runtime_core":     "1KeVBmevatdx_ErsM8_JKv4LNv0fThe38",
    "runtime_allocator":"1wTwGE7pArnzGqIIfuVU_aBtxm4b4dg_s",
    "checkpointing":    "1mVXCrgfeL1jJvosZ7hF4yAMdlNIVre2Y",
    "lifecycle":        "1zhac_IrlZJ_RWIr2v9U-8dr937hj4aUS",
    "cold_boot":        "19nmJi_guH1NEhh4nc6re6E11cNRkqrR5",
    "warm_pool":        "1iRW_ZpAznnQP4xyoDqonP4wyND1z5JvG",
    "teardown":         "1R1d8Vz-HrFjEC0v2QhpZNji3L9s-h4uk",
    "providers":        "17LCBYsOzjqnCYvru38FnytqH3E8h6Okl",
    "_DROPZONE":        "1vFLH7V4Pb6SOhws9ewdMbAbTu5Rb3aVW",
}

# ─────────────────────────────────────────────────────────────────────────────
# CARPETAS QUE SE UNIFICAN — razonadas
# (carpeta_fisica_a_eliminar, carpeta_destino_unificada)
# ─────────────────────────────────────────────────────────────────────────────

UNIFICACIONES: list[tuple[str, str, str]] = [
    # (carpeta_origen, carpeta_destino, motivo)
    ("evolution",     "research",    "evolution es investigacion — misma semantica que research"),
    ("borrar",        "_DEPRECATED", "borrar es intencion temporal — el vfolder correcto es _DEPRECATED"),
    ("pendientes",    "relay",       "pendientes son tareas de relay sin cerrar"),
    ("agent_registry","core",        "registro de agentes es parte del core del sistema"),
    ("reports",       "audits",      "reportes son auditorias — misma semantica"),
    ("test",          "tests",       "singular vs plural — canonico es tests/"),
]

# ─────────────────────────────────────────────────────────────────────────────
# REGLAS DE CLASIFICACION — orden importa, primera que matchea gana
# ─────────────────────────────────────────────────────────────────────────────
# Formato: (patron_regex, subcarpeta_destino, descripcion)

CLASIFICACION: list[tuple[str, str, str]] = [
    # --- BORRAR (primero — antes de cualquier otra regla)
    (r"^borrar_", "_DEPRECATED", "marcado explicitamente para borrar"),

    # --- RELAY POINTERS — solo el mas reciente queda en raiz
    # Todos los RELAY_POINTER van a relay/, excepto el de numero mas alto
    (r"^RELAY_POINTER_V4_\d+\.md$", "relay", "RELAY_POINTER historico — solo el mas reciente en raiz"),

    # --- RELAYS (el historial completo va a relay/)
    (r"^RELAY_\d+_MPAT_V[34].*\.md$", "relay", "relay historico MPAT V4"),
    (r"^RELAY_\d+_.*\.md$", "relay", "relay historico"),
    (r"^RELAY_POINTER.*\.md$", "relay", "RELAY_POINTER historico"),

    # --- CONTRATOS
    (r"^CONTRACT_.*\.md$", "contracts", "contrato de modulo"),

    # --- SCHEMAS Python
    (r"^schema_.*\.py$", "schemas", "schema Pydantic"),

    # --- ARQUITECTURAS
    (r"^Arquitectura de Capa.*\.md$", "architectures", "documento de arquitectura de capa"),
    (r"^ARQUITECTURA.*\.md$", "architectures", "documento de arquitectura"),
    (r"^CAPA_\d+.*\.md$", "architectures", "especificacion de capa"),

    # --- AUDITORIAS / INVENTARIOS
    (r"^AUDITORIA.*\.md$", "audits", "auditoria"),
    (r"^INVENTARIO.*\.md$", "audits", "inventario de estado"),
    (r"^REPORTE.*\.md$", "audits", "reporte"),

    # --- RESOLUCIONES TECNICAS
    (r"^RESOLUCION.*\.md$", "resolutions", "resolucion tecnica"),
    (r"^CONCILIACION.*\.md$", "resolutions", "conciliacion de fuentes"),
    (r"^CORRECCION.*\.md$", "resolutions", "correccion de historial"),
    (r"^DT_.*\.md$", "resolutions", "decision tecnica"),

    # --- RESEARCH / INVESTIGACION
    (r"^TECH_RADAR.*\.md$", "research", "tech radar"),
    (r"^FUT\d+.*\.md$", "research", "investigacion futura"),
    (r"^INV_.*\.md$", "research", "investigacion"),

    # --- DOCS / GUIAS
    (r"^GUIA_.*\.md$", "docs", "guia de integracion"),
    (r"^MAPA_.*\.md$", "docs", "mapa del sistema"),
    (r"^INDICE_.*\.md$", "docs", "indice del sistema"),
    (r"^MPAT_V.*_ESPECIFICACION.*\.md$", "docs", "especificacion maestra"),
    (r"^README.*\.md$", "docs", "README"),
    (r"^.*_GUIA_.*\.md$", "docs", "guia modular"),

    # --- MIGRATION
    (r"^MIGRATION.*\.md$", "migration", "log de migracion"),

    # --- TESTS Python
    (r"^test_.*\.py$", "tests", "test unitario Python"),
    (r"^TEMPORAL_.*\.py$", "tests", "mock temporal para test"),

    # --- SCRIPTS / WORKERS / TOOLS Python
    (r"^mpat4_worker.*\.py$", "scripts", "worker del sistema"),
    (r"^mcp_mpat4.*\.py$", "scripts", "script MCP principal"),
    (r"^reorganize.*\.py$", "scripts", "script de reorganizacion"),
    (r"^.*_orchestrator.*\.py$", "scripts", "orquestador"),
    (r"^ai_devops.*\.py$", "scripts", "script devops"),
    (r"^code_analyzer.*\.py$", "scripts", "analizador de codigo"),

    # --- CORE Python (agentes, modulos de IA)
    (r"^.*_agent.*\.py$", "core", "agente Python"),
    (r"^.*_agents.*\.py$", "core", "modulo de agentes Python"),
    (r"^.*_pipeline.*\.py$", "core", "pipeline Python"),
    (r"^.*_clients.*\.py$", "core", "clientes externos"),
    (r"^.*_roles.*\.py$", "core", "roles del sistema"),
    (r"^synthetic_team.*\.py$", "core", "equipo sintetico"),
    (r"^htn_.*\.py$", "core", "HTN decomposer"),
    (r"^voice_.*\.py$", "core", "modulo de voz"),
    (r"^social_.*\.py$", "core", "modulo social"),
    (r"^instagram_.*\.py$", "core", "cliente social"),
    (r"^devops_.*\.py$", "core", "modulo devops"),

    # --- SESSION SCHEDULER
    (r"^T008__session_scheduler.*\.py$", "session_scheduler", "scheduler de sesiones"),

    # --- HYDRATION
    (r"^T008__hydration.*\.py$", "hydration", "loader de hidratacion"),

    # --- SCHEMAS con prefijo T00X
    (r"^T\d+__.*_schema.*\.py$", "schemas", "schema de tarea"),

    # --- JSON de estructura
    (r"^Directory Structures\.json$", "docs", "estructura de directorios"),
    (r"^CARPETAS_MPAT4\.json$", "herramientas", "JSON de carpetas — no mover"),

    # --- DEPRECATED / PARCHES
    (r"^PARCHE_.*\.txt$", "_DEPRECATED", "parche legacy"),
    (r"^.*\.txt$", "_DEPRECATED", "archivo texto plano legacy"),

    # --- INDEX en raiz (conservar)
    (r"^INDEX_ARCHIVOS_ACTIVOS\.md$", "CONSERVAR_EN_RAIZ", "indice raiz — conservar"),
    (r"^README\.md$", "CONSERVAR_EN_RAIZ", "README raiz — conservar"),

    # --- FALLBACK: .md sin patron claro → docs/
    (r"^.*\.md$", "docs", "documento sin patron especifico → docs/"),

    # --- FALLBACK: .py sin patron claro → core/
    (r"^.*\.py$", "core", "modulo Python sin patron especifico → core/"),
]

# ─────────────────────────────────────────────────────────────────────────────
# VFOLDER MAP — filesystem local
# ─────────────────────────────────────────────────────────────────────────────

VFOLDER_MAP: dict[str, Path] = {
    "relay":            DRIVE_BASE / "relay",
    "contracts":        DRIVE_BASE / "contracts",
    "schemas":          DRIVE_BASE / "schemas",
    "core":             DRIVE_BASE / "core",
    "docs":             DRIVE_BASE / "docs",
    "tests":            DRIVE_BASE / "tests",
    "scripts":          DRIVE_BASE / "scripts",
    "research":         DRIVE_BASE / "research",
    "audits":           DRIVE_BASE / "audits",
    "resolutions":      DRIVE_BASE / "resolutions",
    "architectures":    DRIVE_BASE / "architectures",
    "artifacts":        DRIVE_BASE / "artifacts",
    "deprecated":       DRIVE_BASE / "deprecated",
    "_DEPRECATED":      DRIVE_BASE / "_DEPRECATED",
    "migration":        DRIVE_BASE / "migration",
    "deployment":       DRIVE_BASE / "deployment",
    "herramientas":     DRIVE_BASE / "herramientas",
    "education":        DRIVE_BASE / "education",
    "ecosystem":        DRIVE_BASE / "ecosystem",
    "session_scheduler":DRIVE_BASE / "session_scheduler",
    "hydration":        DRIVE_BASE / "hydration",
    "runtime_core":     DRIVE_BASE / "runtime_core",
    "runtime_allocator":DRIVE_BASE / "runtime_allocator",
    "checkpointing":    DRIVE_BASE / "checkpointing",
    "lifecycle":        DRIVE_BASE / "lifecycle",
    "cold_boot":        DRIVE_BASE / "cold_boot",
    "warm_pool":        DRIVE_BASE / "warm_pool",
    "teardown":         DRIVE_BASE / "teardown",
    "providers":        DRIVE_BASE / "providers",
    "CONSERVAR_EN_RAIZ": DRIVE_BASE,  # no se mueven
}

# Carpetas del sistema — no se procesan como archivos sueltos
CARPETAS_SISTEMA: set[str] = {
    "_DROPZONE", "_DEPRECATED", "_sin_destino", "_destino_invalido", "_revisar",
    ".git", "__pycache__",
}


# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────

def setup_logging(dry_run: bool) -> logging.Logger:
    DROPZONE.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("mpat4_worker_v2")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8", mode="a")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    if dry_run:
        logger.info("=== DRY RUN — cero cambios en disco ===")
    return logger


# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────────────────────

def md5(filepath: Path) -> str:
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def registrar(entry: dict) -> None:
    with open(REGISTRO, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def clasificar(nombre: str) -> tuple[str, str]:
    """
    Retorna (subcarpeta_destino, descripcion) para un nombre de archivo.
    Primera regla que matchea gana.
    """
    for patron, destino, desc in CLASIFICACION:
        if re.match(patron, nombre, re.IGNORECASE):
            return destino, desc
    return "docs", "sin patron — fallback docs/"


def relay_pointer_mas_reciente(archivos: list[Path]) -> str | None:
    """
    De todos los RELAY_POINTER_V4_NNN.md en la lista,
    retorna el nombre del mas reciente (numero mas alto).
    """
    pointers = [
        f for f in archivos
        if re.match(r"^RELAY_POINTER_V4_\d+\.md$", f.name, re.IGNORECASE)
    ]
    if not pointers:
        return None
    return max(pointers, key=lambda f: int(re.search(r"(\d+)", f.name).group(1))).name


# ─────────────────────────────────────────────────────────────────────────────
# REPORTE — sin mover nada
# ─────────────────────────────────────────────────────────────────────────────

def generar_reporte(logger: logging.Logger) -> None:
    archivos = [f for f in DRIVE_BASE.iterdir() if f.is_file()]
    logger.info(f"REPORTE — {len(archivos)} archivos sueltos en raiz")
    logger.info("=" * 60)

    por_destino: dict[str, list[str]] = {}
    for f in sorted(archivos):
        destino, desc = clasificar(f.name)
        por_destino.setdefault(destino, []).append(f.name)

    for destino, nombres in sorted(por_destino.items()):
        logger.info(f"\n[{destino}/]  ({len(nombres)} archivos)")
        for n in nombres:
            logger.info(f"  → {n}")

    logger.info("=" * 60)
    logger.info(f"Total: {len(archivos)} archivos → {len(por_destino)} destinos distintos")


# ─────────────────────────────────────────────────────────────────────────────
# UNIFICACION DE CARPETAS DUPLICADAS
# ─────────────────────────────────────────────────────────────────────────────

def unificar_carpetas(dry_run: bool, logger: logging.Logger) -> None:
    logger.info("=" * 60)
    logger.info("UNIFICACION DE CARPETAS")
    logger.info("=" * 60)

    for origen_nombre, destino_nombre, motivo in UNIFICACIONES:
        origen_path  = DRIVE_BASE / origen_nombre
        destino_path = VFOLDER_MAP.get(destino_nombre, DRIVE_BASE / destino_nombre)

        if not origen_path.exists():
            logger.info(f"  {origen_nombre}/ no existe — ok")
            continue

        archivos_en_origen = list(origen_path.rglob("*"))
        files_en_origen = [f for f in archivos_en_origen if f.is_file()]

        logger.info(f"\n  {origen_nombre}/ → {destino_nombre}/ ({motivo})")
        logger.info(f"  {len(files_en_origen)} archivos a mover")

        for filepath in files_en_origen:
            rel = filepath.relative_to(origen_path)
            destino_final = destino_path / rel

            if dry_run:
                logger.info(f"    [DRY] {filepath.name} → {destino_final}")
                continue

            destino_final.parent.mkdir(parents=True, exist_ok=True)

            if destino_final.exists():
                # Deduplicar por contenido
                if md5(filepath) == md5(destino_final):
                    logger.info(f"    DUP (mismo contenido) — eliminar origen: {filepath.name}")
                    filepath.unlink()
                    registrar({
                        "ts": datetime.now().isoformat(),
                        "accion": "dedup_eliminar",
                        "archivo": str(filepath),
                        "motivo": "contenido identico al destino",
                        "origen": "unificar_carpetas",
                    })
                    continue
                else:
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    destino_final = destino_final.parent / f"{destino_final.stem}__{ts}{destino_final.suffix}"
                    logger.warning(f"    CONFLICTO nombre — renombrado: {destino_final.name}")

            shutil.move(str(filepath), str(destino_final))
            logger.info(f"    OK: {filepath.name} → {destino_nombre}/")
            registrar({
                "ts": datetime.now().isoformat(),
                "accion": "mover",
                "origen_dir": origen_nombre,
                "destino_dir": destino_nombre,
                "archivo": filepath.name,
                "destino_final": str(destino_final),
                "motivo": motivo,
                "origen": "unificar_carpetas",
            })

        # Si la carpeta origen quedo vacia, eliminarla
        if not dry_run:
            archivos_restantes = list(origen_path.rglob("*"))
            if not any(f.is_file() for f in archivos_restantes):
                shutil.rmtree(str(origen_path))
                logger.info(f"  Carpeta {origen_nombre}/ eliminada (vacia)")
                registrar({
                    "ts": datetime.now().isoformat(),
                    "accion": "eliminar_carpeta",
                    "carpeta": origen_nombre,
                    "motivo": f"unificada en {destino_nombre}/",
                    "origen": "unificar_carpetas",
                })

    logger.info("=" * 60)
    logger.info("Unificacion completada.")


# ─────────────────────────────────────────────────────────────────────────────
# REORGANIZACION PRINCIPAL — mueve archivos sueltos de la raiz
# ─────────────────────────────────────────────────────────────────────────────

def reorganizar_raiz(dry_run: bool, logger: logging.Logger) -> None:
    logger.info("=" * 60)
    logger.info("REORGANIZACION DE RAIZ MPAT4")
    logger.info(f"Base: {DRIVE_BASE}")
    logger.info("=" * 60)

    archivos = [f for f in DRIVE_BASE.iterdir() if f.is_file()]
    logger.info(f"{len(archivos)} archivos sueltos en raiz")

    # Identificar el RELAY_POINTER mas reciente para conservarlo en raiz
    pointer_mas_reciente = relay_pointer_mas_reciente(archivos)
    if pointer_mas_reciente:
        logger.info(f"RELAY_POINTER en raiz: {pointer_mas_reciente} (el resto van a relay/)")

    stats = {
        "ok": 0, "conservado": 0, "dedup_eliminado": 0,
        "error": 0, "ya_en_destino": 0
    }

    # Agrupar por destino para log ordenado
    plan: list[tuple[Path, str, str]] = []
    for f in sorted(archivos):
        destino, desc = clasificar(f.name)

        # El RELAY_POINTER mas reciente se conserva en raiz
        if (re.match(r"^RELAY_POINTER_V4_\d+\.md$", f.name, re.IGNORECASE)
                and f.name == pointer_mas_reciente):
            plan.append((f, "CONSERVAR_EN_RAIZ", "RELAY_POINTER mas reciente — permanece en raiz"))
        else:
            plan.append((f, destino, desc))

    # Ejecutar plan
    for filepath, destino, desc in plan:
        if destino == "CONSERVAR_EN_RAIZ":
            logger.info(f"  CONSERVAR: {filepath.name}")
            stats["conservado"] += 1
            continue

        destino_dir = VFOLDER_MAP.get(destino)
        if not destino_dir:
            logger.error(f"  DESTINO INVALIDO: '{destino}' para {filepath.name}")
            stats["error"] += 1
            continue

        destino_final = destino_dir / filepath.name

        logger.info(f"  {filepath.name}")
        logger.info(f"    → {destino}/ ({desc})")

        if dry_run:
            stats["ok"] += 1
            continue

        try:
            destino_dir.mkdir(parents=True, exist_ok=True)

            if destino_final.exists():
                if md5(filepath) == md5(destino_final):
                    # Contenido identico — eliminar el de la raiz
                    logger.info(f"    DUP (mismo contenido) — eliminando raiz: {filepath.name}")
                    filepath.unlink()
                    stats["dedup_eliminado"] += 1
                    registrar({
                        "ts": datetime.now().isoformat(),
                        "accion": "dedup_eliminar",
                        "archivo": str(filepath),
                        "destino": str(destino_final),
                        "motivo": "contenido identico en destino",
                        "origen": "reorganizar_raiz",
                    })
                    continue
                else:
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    destino_final = destino_dir / f"{filepath.stem}__{ts}{filepath.suffix}"
                    logger.warning(f"    CONFLICTO — renombrado: {destino_final.name}")

            shutil.move(str(filepath), str(destino_final))
            logger.info(f"    OK → {destino_final}")
            stats["ok"] += 1

            registrar({
                "ts":             datetime.now().isoformat(),
                "accion":         "mover",
                "archivo":        filepath.name,
                "destino":        str(destino_final),
                "vfolder":        destino,
                "descripcion":    desc,
                "origen":         "reorganizar_raiz",
            })

        except Exception as e:
            logger.error(f"    ERROR: {e}")
            stats["error"] += 1

    logger.info("-" * 60)
    logger.info(
        f"Resultado: ok={stats['ok']} | conservado={stats['conservado']} | "
        f"dedup={stats['dedup_eliminado']} | error={stats['error']}"
    )
    logger.info("=" * 60)


# ─────────────────────────────────────────────────────────────────────────────
# DROP ZONE (comportamiento v1 — sin cambios funcionales)
# ─────────────────────────────────────────────────────────────────────────────

TEXT_EXTENSIONS: set[str] = {".md", ".py", ".skill", ".txt", ".rs", ".toml", ".yaml", ".yml", ".json"}


def parse_dest_from_text(filepath: Path) -> dict | None:
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = [f.readline() for _ in range(15)]
    except Exception:
        return None
    in_block = False
    result: dict[str, str] = {}
    for line in lines:
        line = line.strip().lstrip("#").strip()
        if "MPAT4_DEST" in line:
            in_block = True
            continue
        if in_block:
            if ":" in line:
                key, _, val = line.partition(":")
                result[key.strip().lower()] = val.strip()
            elif result:
                break
    return result if ("destino" in result and "nombre" in result) else None


def parse_dest_from_meta(filepath: Path) -> dict | None:
    meta_path = filepath.parent / (filepath.name + ".meta")
    if not meta_path.exists():
        return None
    result: dict[str, str] = {}
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    key, _, val = line.partition(":")
                    result[key.strip().lower()] = val.strip()
    except Exception:
        return None
    return result if ("destino" in result and "nombre" in result) else None


def procesar_dropzone(dry_run: bool, logger: logging.Logger) -> None:
    logger.info("=" * 60)
    logger.info("PROCESANDO DROP ZONE")
    logger.info("=" * 60)

    if not DROPZONE.exists():
        logger.info("Drop zone no existe.")
        return

    archivos = [f for f in DROPZONE.iterdir() if f.is_file() and not f.name.startswith("_")]
    if not archivos:
        logger.info("Drop zone vacia.")
        return

    stats = {"ok": 0, "sin_dest": 0, "invalido": 0, "error": 0}

    for filepath in sorted(archivos):
        if filepath.suffix == ".meta" or filepath.name == ".gitkeep":
            continue

        logger.info(f"Drop zone: {filepath.name}")

        # Obtener destino
        dest_info = None
        if filepath.suffix.lower() in TEXT_EXTENSIONS:
            dest_info = parse_dest_from_text(filepath)
        if not dest_info:
            dest_info = parse_dest_from_meta(filepath)
        if not dest_info and "__" in filepath.name:
            parts = filepath.name.split("__", 1)
            if parts[0] in VFOLDER_MAP:
                dest_info = {"destino": parts[0], "nombre": parts[1], "alumno": "desconocido"}

        if not dest_info:
            logger.warning(f"  SIN DESTINO — moviendo a _sin_destino/")
            if not dry_run:
                sin_dest = DROPZONE / "_sin_destino"
                sin_dest.mkdir(exist_ok=True)
                shutil.move(str(filepath), str(sin_dest / filepath.name))
            stats["sin_dest"] += 1
            continue

        vfolder = dest_info.get("destino", "").strip()
        nombre  = dest_info.get("nombre", filepath.name).strip()

        if vfolder not in VFOLDER_MAP:
            logger.error(f"  DESTINO INVALIDO: '{vfolder}'")
            if not dry_run:
                inv = DROPZONE / "_destino_invalido"
                inv.mkdir(exist_ok=True)
                shutil.move(str(filepath), str(inv / filepath.name))
            stats["invalido"] += 1
            continue

        destino_dir   = VFOLDER_MAP[vfolder]
        destino_final = destino_dir / nombre

        if dry_run:
            logger.info(f"  [DRY] → {vfolder}/{nombre}")
            stats["ok"] += 1
            continue

        try:
            destino_dir.mkdir(parents=True, exist_ok=True)
            if destino_final.exists():
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                destino_final = destino_dir / f"{destino_final.stem}__{ts}{destino_final.suffix}"
            shutil.move(str(filepath), str(destino_final))
            logger.info(f"  OK → {destino_final}")
            stats["ok"] += 1
            registrar({
                "ts": datetime.now().isoformat(),
                "accion": "mover",
                "archivo": filepath.name,
                "destino": str(destino_final),
                "vfolder": vfolder,
                "alumno": dest_info.get("alumno", "desconocido"),
                "origen": "dropzone",
            })
        except Exception as e:
            logger.error(f"  ERROR: {e}")
            stats["error"] += 1

    logger.info(f"Drop Zone — ok={stats['ok']} | sin_dest={stats['sin_dest']} | invalido={stats['invalido']} | error={stats['error']}")


# ─────────────────────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="MPAT4 Root Reorganizer V2_00",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Flujo recomendado:
  1. python mpat4_worker_v2.py --report          # ver plan sin tocar nada
  2. python mpat4_worker_v2.py --dry-run         # simular todo
  3. python mpat4_worker_v2.py --unify-folders --dry-run  # simular unificacion
  4. python mpat4_worker_v2.py --unify-folders   # unificar carpetas duplicadas
  5. python mpat4_worker_v2.py                   # ejecutar reorganizacion completa
        """,
    )
    parser.add_argument("--dry-run",       action="store_true", help="Simula sin modificar nada")
    parser.add_argument("--report",        action="store_true", help="Solo muestra el plan, no ejecuta")
    parser.add_argument("--drop-only",     action="store_true", help="Solo procesa drop zone")
    parser.add_argument("--unify-folders", action="store_true", help="Unifica carpetas con mismo proposito")
    args = parser.parse_args()

    logger = setup_logging(args.dry_run or args.report)

    logger.info(f"mpat4_worker_v2 V2_00 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.report:
        generar_reporte(logger)
        return

    if args.unify_folders:
        unificar_carpetas(args.dry_run, logger)
        return

    if args.drop_only:
        procesar_dropzone(args.dry_run, logger)
        return

    # Flujo completo
    reorganizar_raiz(args.dry_run, logger)
    procesar_dropzone(args.dry_run, logger)

    logger.info("Ciclo V2 completado.")


if __name__ == "__main__":
    main()
