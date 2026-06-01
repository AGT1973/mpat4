"""
mpat4_worker.py — MPAT4 Drop Zone Worker
Version: V1_01
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

  ADICIONALMENTE — sincronizacion de estructura de carpetas:
    Al final de cada ciclo escanea DRIVE_BASE completo y compara
    contra CARPETAS_MPAT4.json. Si encuentra carpetas fisicas sin vfolder:
    - Las agrega al JSON con vfolder autogenerado (prefijo AUTO_)
    - Marca en el JSON las carpetas que ya no existen en disco (prefijo MISSING_)
    - Escribe el JSON actualizado en disco (Drive lo sincroniza a la nube)
    - Los alumnos descargan el JSON en su proxima sesion y ya conocen los nuevos vfolders

USO:
  python mpat4_worker.py             # procesa drop zone + sincroniza estructura
  python mpat4_worker.py --watch     # repite cada 60 minutos
  python mpat4_worker.py --dry-run   # simula sin mover ni escribir nada
  python mpat4_worker.py --sync-only # solo sincroniza estructura, no procesa drop zone

INSTALACION EN TASK SCHEDULER DE WINDOWS:
  Accion: python "I:\\Scripts\\mpat4_worker.py"
  Trigger: cada 1 hora
  Condicion: solo si hay red disponible (Drive montado)

NOTA SOBRE GDRIVE MONTADO:
  Este script asume que Drive esta montado en I:\\Mi unidad\\
  y que MPAT4 esta en I:\\Mi unidad\\MPAT\\MPAT4\\
  No requiere API de Google. Solo os, shutil y json.
"""

import os
import sys
import shutil
import logging
import json
import argparse
from datetime import datetime
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACION — ajustar segun la PC del docente
# ─────────────────────────────────────────────────────────────────────────────

DRIVE_BASE    = Path(r"I:\Mi unidad\MPAT\MPAT4")
DROPZONE      = DRIVE_BASE / "_DROPZONE"
LOG_FILE      = DROPZONE / "_worker.log"
REGISTRO      = DROPZONE / "_registro.jsonl"
CARPETAS_JSON = DRIVE_BASE / "herramientas" / "CARPETAS_MPAT4.json"

# Carpetas fisicas que el worker ignora al escanear la estructura.
# Son infraestructura del worker o del sistema operativo, no contenido MPAT4.
CARPETAS_IGNORAR: set[str] = {
    "_DROPZONE", "_sin_destino", "_destino_invalido", "_revisar",
    "old", ".git", "__pycache__",
}

# Extensiones que se tratan como texto y pueden tener cabecera MPAT4_DEST interna
TEXT_EXTENSIONS: set[str] = {
    ".md", ".py", ".skill", ".txt", ".rs", ".toml", ".yaml", ".yml", ".json"
}

# Mapa de rutas semanticas a rutas fisicas relativas a DRIVE_BASE.
# Basado en CARPETAS_MPAT4.json V4_15.
# FUENTE DE VERDAD EN TIEMPO DE EJECUCION: se reconstruye desde CARPETAS_JSON al inicio.
# Este dict es el fallback si el JSON no esta disponible.
VFOLDER_MAP_FALLBACK: dict[str, Path] = {
    "skills":         DRIVE_BASE / "herramientas" / "skills",
    "contracts":      DRIVE_BASE / "contracts",
    "resoluciones":   DRIVE_BASE / "resolutions",
    "relay":          DRIVE_BASE / "relay",
    "relay_active":   DRIVE_BASE / "relay" / "active",
    "relay_temporal": DRIVE_BASE / "relay" / "temporal",
    "trashcan":       DRIVE_BASE / "relay" / "descarte",
    "core":           DRIVE_BASE / "core",
    "cognition":      DRIVE_BASE / "core" / "cognition",
    "runtime":        DRIVE_BASE / "core" / "runtime",
    "rust":           DRIVE_BASE / "core" / "rust",
    "research":       DRIVE_BASE / "research",
    "tech_radar":     DRIVE_BASE / "research" / "tech_radar",
    "docs":           DRIVE_BASE / "docs",
    "deployment":     DRIVE_BASE / "deployment",
    "audits":         DRIVE_BASE / "audits",
    "artifacts":      DRIVE_BASE / "artifacts",
}


# ─────────────────────────────────────────────────────────────────────────────
# CARGA Y ESCRITURA DE CARPETAS_MPAT4.json
# ─────────────────────────────────────────────────────────────────────────────

def cargar_json(logger: logging.Logger) -> tuple[dict, dict[str, Path]]:
    """
    Carga CARPETAS_MPAT4.json y construye el VFOLDER_MAP en tiempo de ejecucion.
    Retorna (datos_json, vfolder_map).
    Si el JSON no existe o esta corrupto usa el fallback estatico.
    """
    if not CARPETAS_JSON.exists():
        logger.warning(f"CARPETAS_MPAT4.json no encontrado en {CARPETAS_JSON}")
        logger.warning("Usando VFOLDER_MAP de fallback estatico.")
        return {}, dict(VFOLDER_MAP_FALLBACK)

    try:
        datos = json.loads(CARPETAS_JSON.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Error leyendo CARPETAS_MPAT4.json: {e}")
        logger.warning("Usando VFOLDER_MAP de fallback estatico.")
        return {}, dict(VFOLDER_MAP_FALLBACK)

    vfolder_map: dict[str, Path] = {}
    for entrada in datos.get("carpetas", []):
        vfolder = entrada.get("vfolder", "").strip()
        nombre  = entrada.get("nombre", "").strip()
        if vfolder and nombre and not vfolder.startswith("MISSING_"):
            # nombre es la ruta relativa a DRIVE_BASE con "/" como separador
            ruta = DRIVE_BASE / Path(nombre.replace("/", os.sep))
            vfolder_map[vfolder] = ruta

    if not vfolder_map:
        logger.warning("CARPETAS_MPAT4.json no tiene entradas validas. Usando fallback.")
        return datos, dict(VFOLDER_MAP_FALLBACK)

    logger.info(f"CARPETAS_MPAT4.json cargado: {len(vfolder_map)} vfolders activos")
    return datos, vfolder_map


def guardar_json(datos: dict, logger: logging.Logger, dry_run: bool) -> None:
    """Escribe CARPETAS_MPAT4.json actualizado al disco."""
    if dry_run:
        logger.info("[DRY RUN] Escribiria CARPETAS_MPAT4.json actualizado")
        return
    try:
        CARPETAS_JSON.parent.mkdir(parents=True, exist_ok=True)
        CARPETAS_JSON.write_text(
            json.dumps(datos, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        logger.info(f"CARPETAS_MPAT4.json actualizado en disco → Drive lo sincroniza")
    except Exception as e:
        logger.error(f"Error escribiendo CARPETAS_MPAT4.json: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# SINCRONIZACION DE ESTRUCTURA DE DIRECTORIOS
# ─────────────────────────────────────────────────────────────────────────────

def _generar_vfolder(ruta_relativa: str) -> str:
    """
    Genera un vfolder provisional para una carpeta nueva.
    Usa el path relativo con separadores reemplazados por _.
    Prefijo AUTO_ para que el docente sepa que necesita revision.
    Ejemplo: "core/ia/nuevasubcarpeta" -> "AUTO_core_ia_nuevasubcarpeta"
    """
    limpio = ruta_relativa.replace("/", "_").replace("\\", "_").strip("_")
    return f"AUTO_{limpio}"


def sincronizar_estructura(
    datos: dict,
    vfolder_map: dict[str, Path],
    logger: logging.Logger,
    dry_run: bool,
) -> tuple[dict, dict[str, Path], bool]:
    """
    Escanea DRIVE_BASE y compara contra CARPETAS_MPAT4.json.

    Detecta:
      A) Carpetas fisicas que no tienen entrada en el JSON → las agrega con AUTO_vfolder
      B) Entradas en el JSON cuya carpeta fisica ya no existe → las marca con MISSING_

    Retorna (datos_actualizado, vfolder_map_actualizado, hubo_cambios).
    """
    if not datos:
        logger.warning("JSON no disponible. Saltando sincronizacion de estructura.")
        return datos, vfolder_map, False

    # Construir set de rutas fisicas ya conocidas en el JSON
    # (relativas a DRIVE_BASE, con / como separador, normalizadas)
    rutas_en_json: dict[str, dict] = {}
    for entrada in datos.get("carpetas", []):
        nombre = entrada.get("nombre", "").strip()
        if nombre:
            rutas_en_json[nombre] = entrada

    # ── A) Escanear disco buscando carpetas nuevas ──────────────────────────

    carpetas_nuevas: list[dict] = []

    for carpeta in sorted(DRIVE_BASE.rglob("*")):
        if not carpeta.is_dir():
            continue

        # Ignorar carpetas del sistema
        if any(part in CARPETAS_IGNORAR for part in carpeta.parts):
            continue

        # Calcular ruta relativa normalizada con / como separador
        try:
            rel = carpeta.relative_to(DRIVE_BASE)
        except ValueError:
            continue

        rel_str = rel.as_posix()  # siempre con /

        if rel_str in rutas_en_json:
            continue  # ya esta registrada

        # Carpeta fisica nueva: generar entrada provisional
        vfolder_auto = _generar_vfolder(rel_str)

        # Asegurarse de no colisionar con vfolders existentes
        existentes = {e.get("vfolder", "") for e in datos.get("carpetas", [])}
        suffix = 0
        vfolder_final = vfolder_auto
        while vfolder_final in existentes:
            suffix += 1
            vfolder_final = f"{vfolder_auto}_{suffix}"

        entrada_nueva = {
            "nombre":    rel_str,
            "vfolder":   vfolder_final,
            "id":        "PENDIENTE_VERIFICAR",
            "proposito": "PENDIENTE — carpeta creada por docente, sin descripcion aun.",
            "auto_detectada": True,
            "detectada_ts": datetime.now().isoformat(),
        }
        carpetas_nuevas.append(entrada_nueva)
        logger.info(f"  NUEVA carpeta detectada: {rel_str}  →  vfolder: {vfolder_final}")

    # ── B) Verificar carpetas del JSON que ya no existen en disco ───────────

    hubo_missing = False
    for entrada in datos.get("carpetas", []):
        nombre  = entrada.get("nombre", "").strip()
        vfolder = entrada.get("vfolder", "").strip()
        if not nombre or vfolder.startswith("MISSING_"):
            continue

        ruta_fisica = DRIVE_BASE / Path(nombre.replace("/", os.sep))
        if not ruta_fisica.exists():
            entrada["vfolder"] = f"MISSING_{vfolder}"
            entrada["missing_ts"] = datetime.now().isoformat()
            logger.warning(f"  MISSING: '{nombre}' no existe en disco → vfolder marcado MISSING_{vfolder}")
            # Quitar del vfolder_map activo
            if vfolder in vfolder_map:
                del vfolder_map[vfolder]
            hubo_missing = True

    # ── Aplicar cambios ─────────────────────────────────────────────────────

    hubo_cambios = bool(carpetas_nuevas) or hubo_missing

    if carpetas_nuevas:
        datos.setdefault("carpetas", []).extend(carpetas_nuevas)
        # Actualizar version menor del JSON
        version_actual = datos.get("version", "V4_15")
        datos["version"] = _incrementar_version(version_actual)
        datos["fecha"] = datetime.now().strftime("%Y-%m-%d")
        datos["ultima_sincronizacion"] = datetime.now().isoformat()

        # Agregar nuevas al vfolder_map activo
        for entrada in carpetas_nuevas:
            vf = entrada["vfolder"]
            ruta = DRIVE_BASE / Path(entrada["nombre"].replace("/", os.sep))
            vfolder_map[vf] = ruta

        logger.info(f"  {len(carpetas_nuevas)} carpeta(s) nueva(s) agregadas al JSON")
    else:
        logger.info("  Estructura de carpetas sincronizada — sin cambios nuevos")

    return datos, vfolder_map, hubo_cambios


def _incrementar_version(version: str) -> str:
    """
    Incrementa el numero menor de una version tipo "V4_15" -> "V4_16".
    Si el formato es inesperado devuelve la version con sufijo _sync.
    """
    try:
        partes = version.lstrip("V").split("_")
        if len(partes) == 2:
            mayor, menor = int(partes[0]), int(partes[1])
            return f"V{mayor}_{menor + 1}"
    except (ValueError, IndexError):
        pass
    return f"{version}_sync"


# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────

def setup_logging(dry_run: bool) -> logging.Logger:
    DROPZONE.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("mpat4_worker")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    if dry_run:
        logger.info("=== DRY RUN — no se modificara nada en disco ===")
    return logger


# ─────────────────────────────────────────────────────────────────────────────
# PARSEO DE CABECERA MPAT4_DEST
# ─────────────────────────────────────────────────────────────────────────────

def parse_dest_from_text(filepath: Path) -> dict | None:
    """
    Lee las primeras 15 lineas buscando un bloque:

        # MPAT4_DEST
        # destino: relay_temporal
        # nombre: RELAY_042.md
        # alumno: juan@ejemplo.com

    Retorna dict con keys: destino, nombre, alumno  o  None.
    """
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
                break  # linea vacia o sin : termina el bloque

    if "destino" in result and "nombre" in result:
        return result
    return None


def parse_dest_from_meta(filepath: Path) -> dict | None:
    """
    Busca DROPZONE/nombre_archivo.meta con contenido:
        destino: relay_temporal
        nombre: RELAY_042.md
        alumno: juan@ejemplo.com
    """
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

    if "destino" in result and "nombre" in result:
        return result
    return None


def parse_dest(filepath: Path, vfolder_map: dict[str, Path]) -> dict | None:
    """
    Obtiene la declaracion de destino por prioridad:
    1. Cabecera interna MPAT4_DEST (archivos texto)
    2. Archivo .meta separado
    3. Convencion de nombre VFOLDER__nombre_real.ext
    """
    if filepath.suffix.lower() in TEXT_EXTENSIONS:
        result = parse_dest_from_text(filepath)
        if result:
            return result

    result = parse_dest_from_meta(filepath)
    if result:
        return result

    # Convencion de nombre: relay_temporal__RELAY_042.md
    if "__" in filepath.name:
        parts = filepath.name.split("__", 1)
        if len(parts) == 2 and parts[0] in vfolder_map:
            return {"destino": parts[0], "nombre": parts[1], "alumno": "desconocido"}

    return None


# ─────────────────────────────────────────────────────────────────────────────
# CONVERSION GDOC / DOCX -> MD
# ─────────────────────────────────────────────────────────────────────────────

def convert_gdoc_to_md(filepath: Path, logger: logging.Logger) -> Path:
    suffix = filepath.suffix.lower()

    if suffix == ".gdoc":
        logger.warning(f"  GDOC SHORTCUT detectado: {filepath.name}")
        logger.warning("  El alumno debe exportar desde Drive como .md o .txt")
        logger.warning("  Archivo movido a _DROPZONE/_revisar/ para accion manual")
        revisar_dir = DROPZONE / "_revisar"
        revisar_dir.mkdir(exist_ok=True)
        dest = revisar_dir / filepath.name
        shutil.move(str(filepath), str(dest))
        return dest

    if suffix == ".docx":
        try:
            from docx import Document
            doc = Document(str(filepath))
            md_lines = []
            for para in doc.paragraphs:
                if para.style.name.startswith("Heading"):
                    level = int(para.style.name.split()[-1]) if para.style.name[-1].isdigit() else 1
                    md_lines.append(f"{'#' * level} {para.text}")
                else:
                    md_lines.append(para.text)
            md_path = filepath.with_suffix(".md")
            md_path.write_text("\n\n".join(md_lines), encoding="utf-8")
            filepath.unlink()
            logger.info(f"  DOCX convertido a MD: {md_path.name}")
            return md_path
        except ImportError:
            logger.warning("  python-docx no instalado. Ejecutar: pip install python-docx")
            return filepath
        except Exception as e:
            logger.warning(f"  Error convirtiendo DOCX: {e}")
            return filepath

    return filepath


# ─────────────────────────────────────────────────────────────────────────────
# REGISTRO DE OPERACIONES
# ─────────────────────────────────────────────────────────────────────────────

def registrar(entry: dict) -> None:
    with open(REGISTRO, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# PROCESAMIENTO DE UN ARCHIVO DE LA DROP ZONE
# ─────────────────────────────────────────────────────────────────────────────

def procesar_archivo(
    filepath: Path,
    vfolder_map: dict[str, Path],
    dry_run: bool,
    logger: logging.Logger,
) -> str:
    """
    Procesa un archivo de la drop zone.
    Retorna: "ok" | "sin_dest" | "destino_invalido" | "error" | "ignorado" | "gdoc_manual"
    """
    if filepath.name.startswith("_") or filepath.suffix == ".meta" or filepath.name == ".gitkeep":
        return "ignorado"

    logger.info(f"Procesando: {filepath.name}")

    filepath = convert_gdoc_to_md(filepath, logger)
    if "_revisar" in str(filepath):
        return "gdoc_manual"

    dest_info = parse_dest(filepath, vfolder_map)

    if dest_info is None:
        logger.warning(f"  SIN DESTINO: {filepath.name} — falta cabecera MPAT4_DEST o .meta")
        if not dry_run:
            sin_dest = DROPZONE / "_sin_destino"
            sin_dest.mkdir(exist_ok=True)
            shutil.move(str(filepath), str(sin_dest / filepath.name))
        return "sin_dest"

    vfolder = dest_info.get("destino", "").strip()
    nombre  = dest_info.get("nombre", filepath.name).strip()
    alumno  = dest_info.get("alumno", "desconocido").strip()

    if vfolder not in vfolder_map:
        logger.error(f"  DESTINO INVALIDO: '{vfolder}' no esta en el mapa de vfolders")
        logger.error(f"  Validos: {sorted(vfolder_map.keys())}")
        if not dry_run:
            invalido = DROPZONE / "_destino_invalido"
            invalido.mkdir(exist_ok=True)
            shutil.move(str(filepath), str(invalido / filepath.name))
        return "destino_invalido"

    destino_dir   = vfolder_map[vfolder]
    destino_final = destino_dir / nombre

    logger.info(f"  Alumno  : {alumno}")
    logger.info(f"  vfolder : {vfolder}")
    logger.info(f"  Destino : {destino_final}")

    if dry_run:
        logger.info(f"  [DRY RUN] Crearia carpeta: {destino_dir}")
        logger.info(f"  [DRY RUN] Moveria: {filepath.name} → {destino_final}")
        return "ok"

    destino_dir.mkdir(parents=True, exist_ok=True)

    if destino_final.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        destino_final = destino_dir / f"{destino_final.stem}__{ts}{destino_final.suffix}"
        logger.warning(f"  Conflicto de nombre — renombrado a: {destino_final.name}")

    shutil.move(str(filepath), str(destino_final))
    logger.info(f"  OK — movido a: {destino_final}")

    meta_path = DROPZONE / (filepath.name + ".meta")
    if meta_path.exists():
        meta_path.unlink()
        logger.info(f"  .meta eliminado: {meta_path.name}")

    registrar({
        "ts":               datetime.now().isoformat(),
        "alumno":           alumno,
        "archivo_original": filepath.name,
        "destino":          str(destino_final),
        "vfolder":          vfolder,
        "estado":           "ok",
    })

    return "ok"


# ─────────────────────────────────────────────────────────────────────────────
# LOOP PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def run(dry_run: bool, sync_only: bool, logger: logging.Logger) -> None:
    logger.info("=" * 60)
    logger.info("mpat4_worker V1_01 — iniciando ciclo")
    logger.info(f"Drop zone : {DROPZONE}")
    logger.info(f"JSON      : {CARPETAS_JSON}")
    logger.info("=" * 60)

    # ── Cargar JSON y construir VFOLDER_MAP en tiempo de ejecucion ──────────
    datos, vfolder_map = cargar_json(logger)

    # ── Procesar Drop Zone (si no es --sync-only) ────────────────────────────
    if not sync_only:
        if not DROPZONE.exists():
            logger.warning(f"Drop zone no existe: {DROPZONE}")
            if not dry_run:
                DROPZONE.mkdir(parents=True, exist_ok=True)
                logger.info("Drop zone creada.")
        else:
            archivos = [f for f in DROPZONE.iterdir() if f.is_file()]
            if not archivos:
                logger.info("Drop zone vacia. Nada que procesar.")
            else:
                stats: dict[str, int] = {
                    "ok": 0, "sin_dest": 0, "destino_invalido": 0,
                    "error": 0, "ignorado": 0, "gdoc_manual": 0,
                }
                for filepath in sorted(archivos):
                    try:
                        resultado = procesar_archivo(filepath, vfolder_map, dry_run, logger)
                        stats[resultado] = stats.get(resultado, 0) + 1
                    except Exception as e:
                        logger.error(f"  ERROR inesperado: {filepath.name} — {e}")
                        stats["error"] += 1

                logger.info("-" * 60)
                logger.info(
                    f"Drop Zone — ok={stats['ok']} | sin_dest={stats['sin_dest']} | "
                    f"invalido={stats['destino_invalido']} | gdoc={stats['gdoc_manual']} | "
                    f"error={stats['error']}"
                )

    # ── Sincronizar estructura de carpetas con el JSON ───────────────────────
    logger.info("-" * 60)
    logger.info("Sincronizando estructura de carpetas con CARPETAS_MPAT4.json ...")

    datos, vfolder_map, hubo_cambios = sincronizar_estructura(
        datos, vfolder_map, logger, dry_run
    )

    if hubo_cambios:
        guardar_json(datos, logger, dry_run)
        logger.info("JSON actualizado. Los alumnos lo descargaran en su proxima sesion.")
    else:
        logger.info("Sin cambios en la estructura. JSON no modificado.")

    logger.info("=" * 60)
    logger.info("Ciclo completado.")


# ─────────────────────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="MPAT4 Drop Zone Worker V1_01",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python mpat4_worker.py                # ciclo completo
  python mpat4_worker.py --dry-run      # simula sin tocar nada
  python mpat4_worker.py --sync-only    # solo actualiza el JSON de carpetas
  python mpat4_worker.py --watch        # repite cada hora (prefiere Task Scheduler)
        """,
    )
    parser.add_argument("--dry-run",   action="store_true", help="Simula sin modificar disco ni JSON")
    parser.add_argument("--watch",     action="store_true", help="Repite cada 60 min indefinidamente")
    parser.add_argument("--sync-only", action="store_true", help="Solo sincroniza estructura, no procesa drop zone")
    args = parser.parse_args()

    logger = setup_logging(args.dry_run)

    if args.watch:
        import time
        while True:
            run(args.dry_run, args.sync_only, logger)
            logger.info("Esperando 60 minutos para el proximo ciclo...")
            time.sleep(3600)
    else:
        run(args.dry_run, args.sync_only, logger)


if __name__ == "__main__":
    main()
