"""
mpat4_worker.py — MPAT4 Drop Zone Worker
Version: V1_00
Fecha: 2026-05-27
Autor: Docente MPAT4 (ai.mpat.info@gmail.com)
Sistema: MPAT4 — Infraestructura Cognitiva Distribuida

PROPOSITO:
  Lee la carpeta _DROPZONE en el Drive local del docente.
  Para cada archivo encontrado:
    1. Lee el bloque MPAT4_DEST en las primeras 10 lineas (archivos texto)
       o en un archivo .meta separado (archivos binarios o sin cabecera)
    2. Valida que el destino sea una ruta conocida del sistema
    3. Crea la estructura de carpetas recursivamente si no existe
    4. Si el archivo es Google Doc exportado (.gdoc): lo convierte a .md
    5. Mueve el archivo al destino correcto
    6. Registra la operacion en el log
    7. Borra el archivo de la drop zone

USO:
  python mpat4_worker.py             # procesa una vez y termina
  python mpat4_worker.py --watch     # corre cada 60 minutos (usa Task Scheduler en su lugar)
  python mpat4_worker.py --dry-run   # muestra que haria sin hacer nada

INSTALACION EN TASK SCHEDULER DE WINDOWS:
  Accion: python "I:\\Scripts\\mpat4_worker.py"
  Trigger: cada 1 hora
  Condicion: solo si hay red disponible (Drive montado)

NOTA SOBRE GDRIVE MONTADO:
  Este script asume que Drive esta montado en I:\\Mi unidad\\
  y que MPAT4 esta en I:\\Mi unidad\\MPAT\\MPAT4\\
  No requiere API de Google. Solo os y shutil.
"""

import os
import sys
import re
import shutil
import logging
import json
import argparse
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIGURACION — ajustar segun la PC del docente
# ─────────────────────────────────────────────

DRIVE_BASE = Path(r"I:\Mi unidad\MPAT\MPAT4")
DROPZONE   = DRIVE_BASE / "_DROPZONE"
LOG_FILE   = DRIVE_BASE / "_DROPZONE" / "_worker.log"
REGISTRO   = DRIVE_BASE / "_DROPZONE" / "_registro.jsonl"

# Mapa de rutas semanticas a rutas fisicas relativas a DRIVE_BASE
# Basado en CARPETAS_MPAT4.json V4_15
# El alumno declara el vfolder (columna "vfolder" del JSON) y el script
# resuelve la ruta real. Esto desacopla los skills de la estructura fisica.

VFOLDER_MAP: dict[str, Path] = {
    "skills":       DRIVE_BASE / "herramientas" / "skills",
    "contracts":    DRIVE_BASE / "contracts",
    "resoluciones": DRIVE_BASE / "resolutions",
    "relay":        DRIVE_BASE / "relay",
    "relay_active": DRIVE_BASE / "relay" / "active",
    "relay_temporal": DRIVE_BASE / "relay" / "temporal",
    "trashcan":     DRIVE_BASE / "relay" / "descarte",
    "core":         DRIVE_BASE / "core",
    "cognition":    DRIVE_BASE / "core" / "cognition",
    "runtime":      DRIVE_BASE / "core" / "runtime",
    "rust":         DRIVE_BASE / "core" / "rust",
    "research":     DRIVE_BASE / "research",
    "tech_radar":   DRIVE_BASE / "research" / "tech_radar",
    "docs":         DRIVE_BASE / "docs",
    "deployment":   DRIVE_BASE / "deployment",
    "audits":       DRIVE_BASE / "audits",
    "artifacts":    DRIVE_BASE / "artifacts",
}

# Extensiones que se tratan como texto y tienen cabecera MPAT4_DEST interna
TEXT_EXTENSIONS = {".md", ".py", ".skill", ".txt", ".rs", ".toml", ".yaml", ".yml", ".json"}

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────

def setup_logging(dry_run: bool) -> logging.Logger:
    DROPZONE.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("mpat4_worker")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    if dry_run:
        logger.info("=== DRY RUN — no se modificara nada ===")
    return logger


# ─────────────────────────────────────────────
# PARSEO DE CABECERA MPAT4_DEST
# ─────────────────────────────────────────────

def parse_dest_from_text(filepath: Path) -> dict | None:
    """
    Lee las primeras 15 lineas buscando un bloque:

        # MPAT4_DEST
        # destino: relay_temporal
        # nombre: RELAY_042.md
        # alumno: juan@ejemplo.com

    Retorna dict con keys: destino, nombre, alumno
    o None si no encuentra el bloque.
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = [f.readline() for _ in range(15)]
    except Exception:
        return None

    in_block = False
    result = {}
    for line in lines:
        line = line.strip().lstrip("#").strip()
        if "MPAT4_DEST" in line:
            in_block = True
            continue
        if in_block:
            if ":" in line:
                key, _, val = line.partition(":")
                result[key.strip().lower()] = val.strip()
            else:
                # linea vacia o sin : termina el bloque
                if result:
                    break

    if "destino" in result and "nombre" in result:
        return result
    return None


def parse_dest_from_meta(filepath: Path) -> dict | None:
    """
    Busca un archivo .meta con el mismo nombre base.
    Ejemplo: RELAY_042.md.meta
    Formato del .meta (texto plano):
        destino: relay_temporal
        nombre: RELAY_042.md
        alumno: juan@ejemplo.com
    """
    meta_path = filepath.parent / (filepath.name + ".meta")
    if not meta_path.exists():
        return None
    result = {}
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    key, _, val = line.partition(":")
                    result[key.strip().lower()] = val.strip()
    except Exception:
        return None

    if "destino" in result and "nombre" in result:
        return result
    return None


def parse_dest(filepath: Path) -> dict | None:
    """
    Intenta obtener la declaracion de destino:
    1. Desde cabecera interna (archivos texto)
    2. Desde archivo .meta separado
    3. Desde nombre del archivo con convencion DESTINO__ruta__nombre
    """
    # Opcion 1: cabecera interna
    if filepath.suffix.lower() in TEXT_EXTENSIONS:
        result = parse_dest_from_text(filepath)
        if result:
            return result

    # Opcion 2: archivo .meta
    result = parse_dest_from_meta(filepath)
    if result:
        return result

    # Opcion 3: nombre con doble guion bajo como separador
    # Formato: VFOLDER__nombre_real.ext
    # Ejemplo: relay_temporal__RELAY_042.md
    name = filepath.name
    if "__" in name:
        parts = name.split("__", 1)
        if len(parts) == 2:
            vfolder = parts[0]
            nombre  = parts[1]
            if vfolder in VFOLDER_MAP:
                return {"destino": vfolder, "nombre": nombre, "alumno": "desconocido"}

    return None


# ─────────────────────────────────────────────
# CONVERSION GDOC -> MD
# ─────────────────────────────────────────────

def convert_gdoc_to_md(filepath: Path, logger: logging.Logger) -> Path:
    """
    Google Drive a veces exporta archivos .gdoc (JSON con link al doc online).
    En otros casos exporta directamente como .docx si se configura bien.
    
    Para el caso MPAT4:
    - Si el archivo es .gdoc (JSON de Drive): lo marcamos y avisamos,
      no podemos convertir sin API.
    - Si es .docx: usamos python-docx para extraer texto a .md.
    - Si es texto plano exportado de GDoc: ya es util tal cual.
    
    En la practica, el alumno debe exportar desde Drive como "texto sin formato"
    o "Markdown" antes de subir a la drop zone. El script igual intenta lo que puede.
    """
    suffix = filepath.suffix.lower()

    if suffix == ".gdoc":
        # Es un shortcut JSON de Google Drive, no el contenido real
        logger.warning(f"  GDOC SHORTCUT detectado: {filepath.name}")
        logger.warning(f"  El alumno debe exportar desde Drive como .md o .txt")
        logger.warning(f"  Archivo movido a _DROPZONE/_revisar/ para accion manual")
        revisar_dir = DROPZONE / "_revisar"
        revisar_dir.mkdir(exist_ok=True)
        dest = revisar_dir / filepath.name
        shutil.move(str(filepath), str(dest))
        return dest  # no continuar con este archivo

    if suffix == ".docx":
        try:
            from docx import Document  # python-docx
            doc = Document(str(filepath))
            md_lines = []
            for para in doc.paragraphs:
                if para.style.name.startswith("Heading"):
                    level = int(para.style.name.split()[-1]) if para.style.name[-1].isdigit() else 1
                    md_lines.append(f"{'#' * level} {para.text}")
                else:
                    md_lines.append(para.text)
            md_content = "\n\n".join(md_lines)
            md_path = filepath.with_suffix(".md")
            md_path.write_text(md_content, encoding="utf-8")
            filepath.unlink()
            logger.info(f"  DOCX convertido a MD: {md_path.name}")
            return md_path
        except ImportError:
            logger.warning(f"  python-docx no instalado. pip install python-docx")
            logger.warning(f"  El .docx se mueve tal cual sin conversion")
            return filepath
        except Exception as e:
            logger.warning(f"  Error convirtiendo DOCX: {e}")
            return filepath

    return filepath  # sin conversion necesaria


# ─────────────────────────────────────────────
# REGISTRO DE OPERACIONES
# ─────────────────────────────────────────────

def registrar(entry: dict):
    """Agrega una linea JSON al registro de operaciones."""
    with open(REGISTRO, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ─────────────────────────────────────────────
# PROCESAMIENTO DE UN ARCHIVO
# ─────────────────────────────────────────────

def procesar_archivo(filepath: Path, dry_run: bool, logger: logging.Logger) -> str:
    """
    Procesa un archivo de la drop zone.
    Retorna: "ok", "sin_dest", "destino_invalido", "error", "meta_ignorado", "gdoc_manual"
    """
    # Ignorar archivos del sistema del worker
    if filepath.name.startswith("_"):
        return "meta_ignorado"
    if filepath.suffix == ".meta":
        return "meta_ignorado"
    if filepath.name == ".gitkeep":
        return "meta_ignorado"

    logger.info(f"Procesando: {filepath.name}")

    # Convertir si es necesario (gdoc, docx)
    filepath = convert_gdoc_to_md(filepath, logger)

    # Si fue movido a _revisar por gdoc shortcut
    if "_revisar" in str(filepath):
        return "gdoc_manual"

    # Parsear declaracion de destino
    dest_info = parse_dest(filepath)

    if dest_info is None:
        logger.warning(f"  SIN DESTINO: {filepath.name} — falta cabecera MPAT4_DEST o archivo .meta")
        logger.warning(f"  Moviendo a _DROPZONE/_sin_destino/")
        if not dry_run:
            sin_dest = DROPZONE / "_sin_destino"
            sin_dest.mkdir(exist_ok=True)
            shutil.move(str(filepath), str(sin_dest / filepath.name))
        return "sin_dest"

    vfolder  = dest_info.get("destino", "").strip()
    nombre   = dest_info.get("nombre", filepath.name).strip()
    alumno   = dest_info.get("alumno", "desconocido").strip()

    # Validar que el vfolder es conocido
    if vfolder not in VFOLDER_MAP:
        logger.error(f"  DESTINO INVALIDO: '{vfolder}' no esta en VFOLDER_MAP")
        logger.error(f"  Valores validos: {sorted(VFOLDER_MAP.keys())}")
        if not dry_run:
            invalido = DROPZONE / "_destino_invalido"
            invalido.mkdir(exist_ok=True)
            shutil.move(str(filepath), str(invalido / filepath.name))
        return "destino_invalido"

    destino_dir = VFOLDER_MAP[vfolder]
    destino_final = destino_dir / nombre

    logger.info(f"  Alumno   : {alumno}")
    logger.info(f"  vfolder  : {vfolder}")
    logger.info(f"  Destino  : {destino_final}")

    if dry_run:
        logger.info(f"  [DRY RUN] Crearia: {destino_dir}")
        logger.info(f"  [DRY RUN] Moveria: {filepath.name} -> {destino_final}")
        return "ok"

    # Crear carpetas recursivamente
    destino_dir.mkdir(parents=True, exist_ok=True)

    # Resolver conflictos de nombre: si ya existe, versionar
    if destino_final.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = destino_final.stem
        ext  = destino_final.suffix
        destino_final = destino_dir / f"{stem}__{ts}{ext}"
        logger.warning(f"  Conflicto de nombre — renombrado a: {destino_final.name}")

    # Mover
    shutil.move(str(filepath), str(destino_final))
    logger.info(f"  OK: movido a {destino_final}")

    # Borrar .meta si existe
    meta_path = DROPZONE / (filepath.name + ".meta")
    if meta_path.exists():
        meta_path.unlink()
        logger.info(f"  .meta eliminado: {meta_path.name}")

    # Registrar operacion
    registrar({
        "ts": datetime.now().isoformat(),
        "alumno": alumno,
        "archivo_original": filepath.name,
        "destino": str(destino_final),
        "vfolder": vfolder,
        "estado": "ok"
    })

    return "ok"


# ─────────────────────────────────────────────
# LOOP PRINCIPAL
# ─────────────────────────────────────────────

def run(dry_run: bool, logger: logging.Logger):
    logger.info("=" * 60)
    logger.info(f"mpat4_worker V1_00 — iniciando ciclo")
    logger.info(f"Drop zone: {DROPZONE}")
    logger.info("=" * 60)

    if not DROPZONE.exists():
        logger.warning(f"Drop zone no existe: {DROPZONE}")
        logger.warning("Creando...")
        if not dry_run:
            DROPZONE.mkdir(parents=True, exist_ok=True)
        return

    archivos = [f for f in DROPZONE.iterdir() if f.is_file()]
    if not archivos:
        logger.info("Drop zone vacia. Nada que procesar.")
        return

    stats = {"ok": 0, "sin_dest": 0, "destino_invalido": 0, "error": 0, "meta_ignorado": 0, "gdoc_manual": 0}

    for filepath in sorted(archivos):
        try:
            resultado = procesar_archivo(filepath, dry_run, logger)
            stats[resultado] = stats.get(resultado, 0) + 1
        except Exception as e:
            logger.error(f"  ERROR inesperado procesando {filepath.name}: {e}")
            stats["error"] += 1

    logger.info("-" * 60)
    logger.info(f"Resumen: ok={stats['ok']} | sin_dest={stats['sin_dest']} | "
                f"invalido={stats['destino_invalido']} | gdoc_manual={stats['gdoc_manual']} | "
                f"error={stats['error']}")
    logger.info("Ciclo completado.")


# ─────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="MPAT4 Drop Zone Worker V1_00")
    parser.add_argument("--dry-run", action="store_true", help="Simula sin mover archivos")
    parser.add_argument("--watch", action="store_true", help="Repite cada 60 min (usar Task Scheduler en su lugar)")
    args = parser.parse_args()

    logger = setup_logging(args.dry_run)

    if args.watch:
        import time
        while True:
            run(args.dry_run, logger)
            logger.info("Esperando 60 minutos...")
            time.sleep(3600)
    else:
        run(args.dry_run, logger)


if __name__ == "__main__":
    main()
