#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MPAT Drive Organizer v2 — Reorganización completa del proyecto
Estructura real (captura de pantalla 2026-05-20):

I:\MPAT\MPAT3\
    ├── _BORRAR\
    ├── arquitectura\
    ├── borrar\              ← carpeta "borrar" existente → todo a _BORRAR
    ├── capas\
    ├── estado\
    ├── historico_V2\
    ├── informes\
    │   ├── V3_01\           ← se crea si no existe
    │   └── V3_02\           ← se crea si no existe
    ├── investigaciones\
    ├── plantillas\
    ├── resoluciones\
    ├── zzz_proximo_relay\
    └── zzz_relay\

Uso:
  python mpat_organizar_v2.py              → dry run (solo muestra, no mueve nada)
  python mpat_organizar_v2.py --ejecutar   → ejecuta de verdad (pide confirmación)
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════

ROOT = Path(r"I:\Mi unidad\MPAT\MPAT3")

DRY_RUN = True  # se sobreescribe con --ejecutar

# ═══════════════════════════════════════════════════════════
# CARPETAS DESTINO
# Las que ya existen en tu Drive — el script las respeta.
# V3_01 y V3_02 dentro de informes/ se crean si no existen.
# ═══════════════════════════════════════════════════════════

def destinos(root: Path) -> dict:
    return {
        "informes_v3_01":  root / "informes" / "V3_01",
        "informes_v3_02":  root / "informes" / "V3_02",
        "capas":           root / "capas",
        "resoluciones":    root / "resoluciones",
        "estado":          root / "estado",
        "relay_activo":    root / "zzz_proximo_relay",
        "relay_historico": root / "zzz_relay",
        "historico_v2":    root / "historico_V2",
        "arquitectura":    root / "arquitectura",
        "investigaciones": root / "investigaciones",
        "plantillas":      root / "plantillas",
        "borrar":          root / "_BORRAR",
    }

# ═══════════════════════════════════════════════════════════
# LOG
# ═══════════════════════════════════════════════════════════

log_lines = []

def log(msg, nivel="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    linea = f"[{ts}][{nivel:4s}] {msg}"
    print(linea)
    log_lines.append(linea)

def guardar_log(root: Path):
    borrar_dir = root / "_BORRAR"
    borrar_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = borrar_dir / f"mpat_organizar_log_{ts}.txt"
    log_path.write_text("\n".join(log_lines), encoding="utf-8")
    print(f"\nLog guardado en: {log_path}")

# ═══════════════════════════════════════════════════════════
# RESOLVER CONFLICTOS DE NOMBRE
# ═══════════════════════════════════════════════════════════

def resolver_conflicto(destino: Path) -> Path:
    """Si el destino ya existe, agrega _DUP_N al nombre."""
    if not destino.exists():
        return destino
    base = destino.stem
    ext  = destino.suffix
    n = 1
    while True:
        nuevo = destino.parent / f"{base}_DUP_{n}{ext}"
        if not nuevo.exists():
            return nuevo
        n += 1

# ═══════════════════════════════════════════════════════════
# CLASIFICADOR
# Determina a qué carpeta destino pertenece cada archivo.
# ═══════════════════════════════════════════════════════════

def clasificar(archivo: Path, root: Path) -> str | None:
    """
    Retorna clave de destinos() o None si no hay que mover.
    """
    nombre = archivo.name
    n = nombre.upper()

    # ── 1. BORRAR ─────────────────────────────────────────────────
    if n.startswith("BORRAR_"):
        return "borrar"
    # carpeta "borrar" existente (distinta de _BORRAR) → todo a _BORRAR
    try:
        if (root / "borrar") in archivo.parents:
            return "borrar"
    except Exception:
        pass
    # Google Docs marcados como obsoletos/duplicados/originales no deseados
    if any(x in n for x in ("GDOC_OBSOLETO", "GDOC_DUPLICADO", "GDOC_ORIGINAL")):
        return "borrar"
    # Archivos con prefijo BORRAR en el nombre (cualquier variante)
    if nombre.lower().startswith("borrar"):
        return "borrar"

    # ── 2. INFORMES DE CAPA ───────────────────────────────────────
    if "INFORME" in n and "CAPA" in n:
        # V3_02 explícito
        if any(x in n for x in ("V3_02B", "V3_02b", "V3_02_", "_DELTA", "R030")):
            return "informes_v3_02"
        if "V3_02" in n:
            return "informes_v3_02"
        # V3_01 explícito
        if "V3_01" in n:
            return "informes_v3_01"
        # Sin versión → más reciente = V3_02
        return "informes_v3_02"

    # ── 3. INFORME AVANCE / EVALUACIÓN ────────────────────────────
    if "INFORME_AVANCE" in n or "INFORME_EVALUACION" in n:
        if "V3_02" in n:
            return "informes_v3_02"
        return "informes_v3_01"

    # ── 4. CAPA_XX_MASTER (canónicos internos) ────────────────────
    if "CAPA_" in n and "MASTER" in n:
        if "V3_01" in n:
            return "capas"
        return "capas"

    # ── 5. RESOLUCIONES ───────────────────────────────────────────
    if n.startswith("RES") and ("V3" in n or "_V3" in n):
        return "resoluciones"
    if "RESOLUCIONES_V3" in n:
        return "resoluciones"
    if "RESOLUCIONES_MPAT_V3" in n:
        return "resoluciones"
    if "MAPA_RES" in n:
        return "resoluciones"

    # ── 6. RESOLUCIONES V2 (histórico) ────────────────────────────
    if "RESOLUCIONES_MPAT_V2" in n:
        return "historico_v2"

    # ── 7. ARQUITECTURA V2 (histórico) ────────────────────────────
    if "ARQUITECTURA_BASE_V2" in n or "ARQUITECTURA_base_V2" in nombre:
        return "historico_v2"

    # ── 8. CAPA_X_V2 o capa_x_V2 (histórico) ─────────────────────
    if nombre.startswith("capa_") and "_V2_" in nombre:
        return "historico_v2"
    if n.startswith("CAPA_") and "_V2_" in n:
        return "historico_v2"

    # ── 9. INVESTIGACIONES ────────────────────────────────────────
    if "INVESTIGACION" in n:
        return "investigaciones"

    # ── 10. ESTADO DEL PROYECTO ───────────────────────────────────
    if "MPAT_PROYECTO_ESTADO" in n:
        return "estado"
    if "ESTADO_CIERRE" in n:
        return "estado"
    if "MPAT_V4_0" in n or "ESPECIFICACION_MAESTRA" in n:
        return "estado"
    if "DOSSIER" in n:
        return "estado"

    # ── 11. RELAYS ────────────────────────────────────────────────
    # RELAYs recientes (V3_02, RELAY_018 en adelante) → zzz_proximo_relay
    if n.startswith("RELAY_") and n.endswith(".MD"):
        # Extraer número de relay si existe
        partes = nombre.replace("_", " ").split()
        for p in partes:
            digitos = ''.join(c for c in p if c.isdigit())
            if digitos:
                num = int(digitos)
                if num >= 12:
                    return "relay_activo"
                else:
                    return "relay_historico"
        return "relay_activo"  # sin número → reciente

    if "RELAY_NEXT_POINTER" in n or "RELAY_TRASPASO" in n:
        return "relay_activo"
    if "RELAY_029" in n or "RELAY_028" in n or "RELAY_027" in n:
        return "relay_activo"
    if "PROMPT_RETOMA" in n or "PROMPT_ALUMNO" in n:
        return "relay_historico"

    # ── 12. RELAY_MPAT antiguos ───────────────────────────────────
    if "RELAY_" in n and ("V2_" in n or "V3_01" in n):
        return "relay_historico"

    # ── 13. SKILL / MCP ───────────────────────────────────────────
    if "SKILL" in n and "MPAT" in n:
        return "plantillas"
    if nombre.endswith(".skill") or nombre.endswith(".zip"):
        return "plantillas"

    # ── 14. TEMPLATE / PLANTILLA ──────────────────────────────────
    if "TEMPLATE" in n:
        return "plantillas"

    return None  # sin clasificar → no mover, reportar


# ═══════════════════════════════════════════════════════════
# MOVER ARCHIVO
# ═══════════════════════════════════════════════════════════

def mover(archivo: Path, destino_dir: Path, borrar_dir: Path):
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / archivo.name

    accion = "MOVER"

    if destino.exists():
        # Mismo tamaño → duplicado exacto → el origen va a _BORRAR
        if destino.stat().st_size == archivo.stat().st_size:
            accion = "DUPLICADO_EXACTO→_BORRAR"
            destino_final = resolver_conflicto(borrar_dir / archivo.name)
            log(f"  [{accion}] {archivo.name}", "WARN")
            log(f"    origen:  {archivo}")
            log(f"    destino: {destino_final}")
            if not DRY_RUN:
                borrar_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(archivo), str(destino_final))
            return "duplicado"
        else:
            # Mismo nombre, distinto contenido → renombrar con _DUP_N
            destino = resolver_conflicto(destino)
            log(f"  [CONFLICTO_RENOMBRADO] {archivo.name} → {destino.name}", "WARN")

    log(f"  [{accion}] {archivo.name}")
    log(f"    de:  {archivo.parent}")
    log(f"    a:   {destino_dir}")

    if not DRY_RUN:
        shutil.move(str(archivo), str(destino))
    return "movido"


# ═══════════════════════════════════════════════════════════
# DEDUPLICAR RELAY_NEXT_POINTER
# Hay múltiples copias sin numeración — conservar solo la más reciente
# ═══════════════════════════════════════════════════════════

def dedup_relay_pointers(root: Path):
    relay_dir = root / "zzz_proximo_relay"
    if not relay_dir.exists():
        return

    pointers = [
        p for p in relay_dir.iterdir()
        if p.is_file() and "RELAY_NEXT_POINTER" in p.name.upper()
        and not any(c.isdigit() for c in p.stem.replace("RELAY_NEXT_POINTER", ""))
    ]

    if len(pointers) <= 1:
        return

    pointers.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    mas_nuevo = pointers[0]
    ts = datetime.fromtimestamp(mas_nuevo.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    log(f"\nDEDUP RELAY_NEXT_POINTER — más nuevo: {mas_nuevo.name} ({ts})")

    borrar_dir = root / "_BORRAR"
    for viejo in pointers[1:]:
        ts_v = datetime.fromtimestamp(viejo.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        log(f"  [DEDUP→_BORRAR] {viejo.name} ({ts_v})", "WARN")
        if not DRY_RUN:
            borrar_dir.mkdir(parents=True, exist_ok=True)
            dest = resolver_conflicto(borrar_dir / viejo.name)
            shutil.move(str(viejo), str(dest))


# ═══════════════════════════════════════════════════════════
# ESCANEO PRINCIPAL
# ═══════════════════════════════════════════════════════════

def escanear(root: Path):
    D = destinos(root)
    borrar_dir = D["borrar"]

    # Crear subcarpetas de informes si no existen
    for k in ("informes_v3_01", "informes_v3_02"):
        if not DRY_RUN:
            D[k].mkdir(parents=True, exist_ok=True)
        else:
            if not D[k].exists():
                log(f"  [DRY] Crear carpeta: {D[k].relative_to(root)}")

    stats = {
        "escaneados":  0,
        "movidos":     0,
        "duplicados":  0,
        "borrar":      0,
        "ya_ok":       0,
        "sin_clas":    0,
    }

    sin_clasificar = []

    # Carpetas que NO hay que re-escanear como origen
    # (son destinos — si el archivo ya está ahí, está bien)
    destinos_set = set(D.values())

    extensiones = {
        ".md", ".txt", ".docx", ".zip", ".skill",
        ".gdoc", ".gsheet", ".gslides", ".pdf"
    }

    log(f"\nEscaneando: {root}")
    log("─" * 60)

    for archivo in sorted(root.rglob("*")):
        if not archivo.is_file():
            continue

        # Saltar el propio script
        if archivo.suffix == ".py":
            continue

        # Saltar extensiones no relevantes
        if archivo.suffix.lower() not in extensiones:
            continue

        # ¿Está dentro de alguna carpeta destino correcta?
        # Excepción: informes/ raíz SÍ hay que revisar (mover a V3_01 o V3_02)
        padre_es_destino = False
        for dest in destinos_set:
            if archivo.parent == dest:
                padre_es_destino = True
                break
            # informes/ raíz → revisar de todas formas
            if archivo.parent == root / "informes":
                padre_es_destino = False
                break

        if padre_es_destino:
            stats["ya_ok"] += 1
            continue

        stats["escaneados"] += 1
        clave = clasificar(archivo, root)

        if clave is None:
            sin_clasificar.append(archivo)
            stats["sin_clas"] += 1
            log(f"  [SIN_CLAS] {archivo.relative_to(root)}", "WARN")
            continue

        resultado = mover(archivo, D[clave], borrar_dir)
        if resultado == "duplicado":
            stats["duplicados"] += 1
        elif clave == "borrar":
            stats["borrar"] += 1
        else:
            stats["movidos"] += 1

    # ── REPORTE ──────────────────────────────────────────────
    log("\n" + "═" * 60)
    log("RESUMEN FINAL:")
    log(f"  Archivos procesados:     {stats['escaneados']}")
    log(f"  Movidos a destino:       {stats['movidos']}")
    log(f"  Mandados a _BORRAR:      {stats['borrar']}")
    log(f"  Duplicados exactos:      {stats['duplicados']}")
    log(f"  Ya en carpeta correcta:  {stats['ya_ok']}")
    log(f"  Sin clasificar:          {stats['sin_clas']}")

    if sin_clasificar:
        log("\nARCHIVOS SIN CLASIFICAR — revisar manualmente:", "WARN")
        for f in sin_clasificar:
            try:
                log(f"  → {f.relative_to(root)}", "WARN")
            except ValueError:
                log(f"  → {f}", "WARN")

    log("═" * 60)

    if DRY_RUN:
        log("\nMODO DRY RUN — nada fue movido.")
        log("Ejecutá con --ejecutar cuando estés conforme.")
    else:
        log("\nReorganización completada.")


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    global DRY_RUN

    if "--ejecutar" in sys.argv:
        DRY_RUN = False
        print("=" * 60)
        print("  MPAT Organizer — MODO EJECUCIÓN REAL")
        print(f"  ROOT: {ROOT}")
        print("=" * 60)
        respuesta = input("¿Confirmar reorganización? (s/N): ").strip().lower()
        if respuesta != "s":
            print("Cancelado.")
            sys.exit(0)
    else:
        print("=" * 60)
        print("  MPAT Organizer — MODO DRY RUN (simulación)")
        print(f"  ROOT: {ROOT}")
        print("  Para ejecutar: python mpat_organizar_v2.py --ejecutar")
        print("=" * 60)

    if not ROOT.exists():
        print(f"\n❌ No se encontró la carpeta: {ROOT}")
        print("   Verificá que Google Drive esté sincronizado en I:\\")
        print("   o ajustá ROOT al inicio del script.")
        sys.exit(1)

    escanear(ROOT)
    dedup_relay_pointers(ROOT)
    guardar_log(ROOT)


if __name__ == "__main__":
    main()
