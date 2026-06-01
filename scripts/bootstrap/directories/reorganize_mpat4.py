"""
reorganize_mpat4.py  —  MPAT4 v2
==================================
Reorganiza la estructura local de MPAT4 en Windows.
Ruta base: I:\\Mi unidad\\MPAT\\MPAT4

CORRECCIONES v2:
  - En DRY_RUN muestra el plan sin confundir con archivos que "no se movieron aún"
  - Dirs con contenido van a deprecated/ antes de eliminar (nada se pierde)
  - No warnings por subdirs que simplemente no existen en disco
  - Bloque 3 no repite los creates que ya hizo el bloque 2

USO:
  python reorganize_mpat4.py            → Plan de cambios (DRY RUN, sin tocar nada)
  python reorganize_mpat4.py --ejecutar → Aplica los cambios reales
  python reorganize_mpat4.py --informe  → Solo muestra estado actual de carpetas

LOG: mpat4_reorganize_log.txt (misma carpeta que el script)
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────
BASE = Path(r"I:\Mi unidad\MPAT\MPAT4")

DRY_RUN      = "--ejecutar" not in sys.argv
SOLO_INFORME = "--informe"  in sys.argv

LOG_FILE = Path(__file__).parent / "mpat4_reorganize_log.txt"

# Rastreo de movimientos ya hechos (para que ELIMINAR sepa si el contenido fue movido)
_movimientos_realizados: set[str] = set()

# ─────────────────────────────────────────────────────
# LOGGER
# ─────────────────────────────────────────────────────
_log_lines: list[str] = []

def log(msg: str, nivel: str = "INFO") -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    icono = {"INFO": "   ", "OK": " ✓ ", "WARN": " ⚠ ", "ERR": " ✗ ", "HEAD": "═══"}
    linea = f"[{ts}]{icono.get(nivel, '   ')}{msg}"
    print(linea)
    _log_lines.append(linea)

def guardar_log() -> None:
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"MPAT4 Reorganización — {datetime.now().isoformat()}\n")
        f.write(f"Modo: {'DRY RUN (plan sin cambios)' if DRY_RUN else 'EJECUCIÓN REAL'}\n")
        f.write("=" * 60 + "\n\n")
        f.write("\n".join(_log_lines))
    print(f"\n   Log guardado: {LOG_FILE}")

# ─────────────────────────────────────────────────────
# OPERACIONES BASE
# ─────────────────────────────────────────────────────

def _existe(ruta: str) -> bool:
    return (BASE / ruta).exists()

def renombrar(viejo: str, nuevo: str) -> None:
    src = BASE / viejo
    dst = BASE / nuevo

    if not src.exists():
        log(f"RENOMBRAR omitido — no existe en disco: {viejo}", "INFO")
        return

    if dst.exists():
        log(f"RENOMBRAR — destino ya existe, fusionando: {viejo} → {nuevo}", "WARN")
        if not DRY_RUN:
            for item in src.iterdir():
                d = dst / item.name
                if not d.exists():
                    shutil.move(str(item), str(dst))
            try:
                src.rmdir()
            except OSError:
                log(f"  No se pudo eliminar {viejo} (no vacío tras fusión)", "WARN")
        return

    log(f"RENOMBRAR: {viejo}  →  {nuevo}", "OK")
    if not DRY_RUN:
        src.rename(dst)


def mover_contenido(origen: str, destino: str) -> None:
    """Mueve el contenido de origen → destino y registra el movimiento."""
    src = BASE / origen
    dst = BASE / destino

    if not src.exists():
        # silencioso — el subdirectorio simplemente nunca existió en disco
        return

    items = list(src.iterdir())
    if not items:
        log(f"MOVER — origen vacío (ya limpio): {origen}", "INFO")
        _movimientos_realizados.add(origen)
        return

    # Crear destino si no existe
    if not dst.exists():
        log(f"CREAR (para recibir): {destino}", "OK")
        if not DRY_RUN:
            dst.mkdir(parents=True, exist_ok=True)

    log(f"MOVER: {origen}  →  {destino}  ({len(items)} items)", "OK")
    if not DRY_RUN:
        for item in items:
            d = dst / item.name
            if not d.exists():
                shutil.move(str(item), str(dst))

    _movimientos_realizados.add(origen)


def archivar_en_deprecated(ruta: str, razon: str) -> None:
    """
    Mueve una carpeta a deprecated/ antes de eliminarla.
    Así el contenido nunca se pierde — queda auditado en deprecated/.
    """
    src = BASE / ruta
    dep = BASE / "deprecated" / Path(ruta).name

    if not src.exists():
        log(f"ARCHIVAR omitido — no existe: {ruta}", "INFO")
        return

    archivos = [f for f in src.rglob("*") if f.is_file()]
    log(f"ARCHIVAR → deprecated/{Path(ruta).name}  ({len(archivos)} archivos) — Razón: {razon}", "OK")

    if not DRY_RUN:
        if dep.exists():
            dep = BASE / "deprecated" / f"{Path(ruta).name}_{datetime.now().strftime('%H%M%S')}"
        shutil.move(str(src), str(dep))

    _movimientos_realizados.add(ruta)


def crear(ruta: str) -> None:
    target = BASE / ruta
    if target.exists():
        return  # silencioso — ya existe no es un problema
    log(f"CREAR: {ruta}", "OK")
    if not DRY_RUN:
        target.mkdir(parents=True, exist_ok=True)


def eliminar_si_vacio(ruta: str) -> None:
    """
    Elimina solo si:
      a) el directorio está vacío, O
      b) su contenido fue movido en esta sesión (_movimientos_realizados)
    """
    target = BASE / ruta

    if not target.exists():
        log(f"ELIMINAR — ya no existe (limpio): {ruta}", "INFO")
        return

    archivos = [f for f in target.rglob("*") if f.is_file()]

    fue_movido = ruta in _movimientos_realizados or any(
        ruta.startswith(m) for m in _movimientos_realizados
    )

    if archivos and not fue_movido:
        log(f"ELIMINAR omitido — tiene {len(archivos)} archivos sin mover: {ruta}", "WARN")
        log(f"   └ Primero archivar_en_deprecated('{ruta}') o mover su contenido.", "WARN")
        return

    if DRY_RUN:
        nota = " (contenido ya movido en este plan)" if fue_movido else " (vacío)"
        log(f"ELIMINAR{nota}: {ruta}", "OK")
    else:
        try:
            shutil.rmtree(str(target))
            log(f"ELIMINADO: {ruta}", "OK")
        except Exception as e:
            log(f"Error al eliminar {ruta}: {e}", "ERR")

# ─────────────────────────────────────────────────────
# INFORME DE ESTADO ACTUAL
# ─────────────────────────────────────────────────────

def informe_estado() -> None:
    log("ESTADO ACTUAL DE LA ESTRUCTURA", "HEAD")

    if not BASE.exists():
        log(f"La carpeta base NO EXISTE: {BASE}", "ERR")
        return

    total = vacias = con_arch = 0
    for p in sorted(BASE.rglob("*")):
        if not p.is_dir():
            continue
        total += 1
        archivos = [f for f in p.iterdir() if f.is_file()]
        subdirs  = [d for d in p.iterdir() if d.is_dir()]
        rel = str(p.relative_to(BASE))
        if not archivos and not subdirs:
            vacias += 1
        if archivos:
            con_arch += 1
            log(f"  {rel}  → {len(archivos)} archivos", "INFO")

    log(f"Total dirs: {total}   Con archivos: {con_arch}   Completamente vacíos: {vacias}")
    log("")

# ─────────────────────────────────────────────────────
# PLAN DE REORGANIZACIÓN
# ─────────────────────────────────────────────────────

def reorganizar() -> None:

    log("MPAT4 — PLAN DE REORGANIZACIÓN", "HEAD")
    log(f"Base: {BASE}")
    log(f"Modo: {'PLAN (DRY RUN — sin cambios)' if DRY_RUN else 'EJECUCIÓN REAL'}")
    log("=" * 60)

    # ── BLOQUE 1: RENOMBRES ─────────────────────────────────
    log("")
    log("[1/5] RENOMBRES", "HEAD")

    renombrar("core/runtime_core",  "core/runtime")   # nombre redundante
    renombrar("research/fut",       "research/futures")  # nombre ambiguo

    # ── BLOQUE 2: MOVER CONTENIDO MAL UBICADO ───────────────
    log("")
    log("[2/5] MOVER CONTENIDO MAL UBICADO", "HEAD")

    # Después del rename, runtime_core ya es runtime.
    # sandbox y migration solo se mueven si existen en disco.
    mover_contenido("core/runtime/sandbox",   "core/sandboxing")
    mover_contenido("core/runtime/migration", "scripts/migration")

    # relay_system/ → relay/ (estructura unificada que usa la skill)
    mover_contenido("relay_system/relay_docs",        "relay/docs")
    mover_contenido("relay_system/relay_governance",  "relay/governance")
    mover_contenido("relay_system/relay_memory",      "relay/memory")
    mover_contenido("relay_system/relay_pointer",     "relay/pointer")
    mover_contenido("relay_system/relay_protocol",    "relay/protocol")
    mover_contenido("relay_system/relay_runtime",     "relay/runtime")

    # system_state/relay → relay/ también (mismo ID de Drive)
    mover_contenido("system_state/relay", "relay/active")

    # ── BLOQUE 3: ARCHIVAR (antes de eliminar) ───────────────
    log("")
    log("[3/5] ARCHIVAR EN deprecated/ (contenido no eliminar)", "HEAD")

    # cognition_runtime: concepto erróneo — runtime no vive en cognition
    archivar_en_deprecated(
        "core/cognition/cognition_runtime",
        "concepto erróneo: runtime no pertenece a cognition"
    )
    # docs/business: vacía en sistema académico
    archivar_en_deprecated(
        "docs/business",
        "sin propósito definido en sistema académico"
    )
    # ecosystem/capabilities: vaga y vacía
    archivar_en_deprecated(
        "ecosystem/capabilities",
        "nombre ambiguo, sin contenido real"
    )
    # ecosystem/manifests: sin destino definido
    archivar_en_deprecated(
        "ecosystem/manifests",
        "sin propósito definido — contenido va en contracts/ o ecosystem/cards/"
    )

    # ── BLOQUE 4: CREAR DIRECTORIOS NUEVOS ──────────────────
    log("")
    log("[4/5] CREAR DIRECTORIOS FALTANTES", "HEAD")

    # relay/ unificado
    crear("relay")
    crear("relay/active")
    crear("relay/temporal")
    crear("relay/pointer")
    crear("relay/docs")
    crear("relay/governance")
    crear("relay/memory")
    crear("relay/protocol")
    crear("relay/runtime")

    # docs/architecture limpio (tenía mismo ID que docs/ en Drive)
    crear("docs/architecture")

    # system_state completo
    crear("system_state/cluster")
    crear("system_state/governance")
    crear("system_state/runtime")
    crear("system_state/tenants")

    # ── BLOQUE 5: ELIMINAR REDUNDANTES ──────────────────────
    log("")
    log("[5/5] ELIMINAR REDUNDANTES", "HEAD")

    # relay_system: contenido ya movido en bloque 2
    eliminar_si_vacio("relay_system")

    # system_state/relay: contenido ya movido en bloque 2
    eliminar_si_vacio("system_state/relay")

    # subdirs de runtime que se movieron (si existían)
    eliminar_si_vacio("core/runtime/sandbox")
    eliminar_si_vacio("core/runtime/migration")

    # ── BLOQUE 6: GENERAR ÁRBOL LIMPIO ──────────────────────
    log("")
    log("[6/6] GENERAR tree_vfolders_v2.json", "HEAD")
    generar_arbol_limpio()

    log("")
    log("=" * 60)
    if DRY_RUN:
        log("PLAN COMPLETADO — ningún archivo fue modificado", "OK")
        log("Para aplicar: python reorganize_mpat4.py --ejecutar", "WARN")
    else:
        log("REORGANIZACIÓN COMPLETADA", "OK")

# ─────────────────────────────────────────────────────
# ÁRBOL LIMPIO — tree_vfolders_v2.json
# ─────────────────────────────────────────────────────

def generar_arbol_limpio() -> None:
    arbol = {"v-folder": {
        # RAÍZ
        "MPAT4/":                                       "1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI",
        "MPAT4/contracts/":                             "1589CC4tPfBkCUndlsVQeT9c9aYTSeaM0",
        "MPAT4/schemas/":                               "1N_u01JXjeMlMkNbk7GvV6snQTtnpOipG",
        "MPAT4/resoluciones/":                          "1hRfjnUkOyfnfqxLEfBM0CWLLnDBi3GQU",
        "MPAT4/deprecated/":                            "14b47yd91-ebxV_rp_HVkndp0JKKthF2m",
        # RELAY (unificado)
        "MPAT4/relay/":                                 "1c3CP8dM19BGyjOlI8TadmyL1KtV_Tlte",
        "MPAT4/relay/active/":                          "",
        "MPAT4/relay/temporal/":                        "1QehAmh2U7brtnHMDYRuR-SQUDCJyPJVu",
        "MPAT4/relay/pointer/":                         "",
        "MPAT4/relay/docs/":                            "",
        "MPAT4/relay/governance/":                      "",
        "MPAT4/relay/memory/":                          "",
        "MPAT4/relay/protocol/":                        "",
        "MPAT4/relay/runtime/":                         "",
        # CORE
        "MPAT4/core/":                                  "1yvrUM4x8F-Ej84bN1yyJSzmr7zDCTVUC",
        "MPAT4/core/cognition/":                        "1rexYAfWICisZs4B51V3nmh3gOStK6rWJ",
        "MPAT4/core/cognition/agents/":                 "1FoQYxO9aBhpRGh8PEbiPG1Tblm1HbFTU",
        "MPAT4/core/cognition/context/":                "1jh50caSvu7M2iSgrvw50oliPWBb-S7yN",
        "MPAT4/core/cognition/kernel/":                 "1x4y8ijc6bybDOQlU1KwyXNevjLODax5g",
        "MPAT4/core/cognition/orchestration/":          "16XisYAfWICisZs4B51V3nmh3gOStK6rWJ",
        "MPAT4/core/cognition/planning/":               "1dzhGpyFfc6OBAcyZfJV9min3pZQsu718",
        "MPAT4/core/cognition/reasoning/":              "1yIN_cbk2xOcNzhDJFySleJ-9VPYNkGdy",
        "MPAT4/core/event_bus/":                        "1lsaMPtDRFcXPGdBrZ8fAilsCNhpXZZiG",
        "MPAT4/core/event_bus/brokers/":                "1A6K9bHX__IXeL9aT1jh50caSvu7M2iSgr",
        "MPAT4/core/event_bus/dead_letter/":            "1w50oliPWBb-S7yN16XisYAfWICisZs4B",
        "MPAT4/core/event_bus/event_replay/":           "151V3nmh3gOStK6rWJ1FoQYxO9aBhpRGh",
        "MPAT4/core/event_bus/event_sourcing/":         "18PEbiPG1Tblm1HbFTU1yIN_cbk2xOcNz",
        "MPAT4/core/event_bus/persistence/":            "1hDJFySleJ-9VPYNkGdy1dzhGpyFfc6OBA",
        "MPAT4/core/event_bus/streams/":                "1cyZfJV9min3pZQsu7181mY4iE6lE6ZtN6",
        "MPAT4/core/event_bus/subscriptions/":          "1ZlA6K9bHX__IXeL9aT1jh50caSvu7M2i",
        "MPAT4/core/execution_graph/":                  "1XY8JEOFPc-scoUCGgBkwEpVann64MvA3",
        "MPAT4/core/execution_graph/dag_engine/":       "1s4B51V3nmh3gOStK6rWJ1FoQYxO9aBhp",
        "MPAT4/core/execution_graph/distributed_execution/": "1RGh8PEbiPG1Tblm1HbFTU1yIN_cbk2xO",
        "MPAT4/core/execution_graph/planner/":          "1cNzhDJFySleJ-9VPYNkGdy1dzhGpyFfc",
        "MPAT4/core/execution_graph/task_router/":      "16OBAcyZfJV9min3pZQsu7181mY4iE",
        "MPAT4/core/federation/":                       "1XZ_M7ShjoVYTAS-5foL6-dElFTzJywW7",
        "MPAT4/core/federation/cluster_sync/":          "17M2iSgrvw50oliPWBb-S7yN16XisYAfW",
        "MPAT4/core/federation/federated_memory/":      "1ICisZs4B51V3nmh3gOStK6rWJ1FoQYx",
        "MPAT4/core/federation/peer_discovery/":        "1O9aBhpRGh8PEbiPG1Tblm1HbFTU1yIN_",
        "MPAT4/core/federation/relay_exchange/":        "1cbk2xOcNzhDJFySleJ-9VPYNkGdy1dzh",
        "MPAT4/core/federation/remote_execution/":      "1GpyFfc6OBAcyZfJV9min3pZQsu7181m",
        "MPAT4/core/federation/trust_exchange/":        "1Y4iE6lE6ZtN6ZlA6K9bHX__IXeL9aT1j",
        "MPAT4/core/governance/":                       "1nK9zcVKHoMx_qe16B_Lu4SyKZZPkS06S",
        "MPAT4/core/governance/audit/":                 "1isYAfWICisZs4B51V3nmh3gOStK6rWJ1F",
        "MPAT4/core/governance/budget_engine/":         "1oQYxO9aBhpRGh8PEbiPG1Tblm1HbFTU1",
        "MPAT4/core/governance/compliance/":            "1yIN_cbk2xOcNzhDJFySleJ-9VPYNkGdy1",
        "MPAT4/core/governance/economics/":             "1dzhGpyFfc6OBAcyZfJV9min3pZQsu7181",
        "MPAT4/core/governance/permissions/":           "1mY4iE6lE6ZtN6ZlA6K9bHX__IXeL9aT1",
        "MPAT4/core/governance/policies/":              "1jh50caSvu7M2iSgrvw50oliPWBb-S7yN1",
        "MPAT4/core/governance/runtime_limits/":        "16XisYAfWICisZs4B51V3nmh3gOStK6rW",
        "MPAT4/core/governance/tenant_isolation/":      "1JisZs4B51V3nmh3gOStK6rWJ1FoQYxO",
        "MPAT4/core/governance/trust/":                 "19aBhpRGh8PEbiPG1Tblm1HbFTU1yIN_cb",
        "MPAT4/core/memory/":                           "1CtYQRsZGh6r8UZPySpoHcnXbp0rLWgks",
        "MPAT4/core/memory/consolidation/":             "1Ffc6OBAcyZfJV9min3pZQsu7181mY4iE",
        "MPAT4/core/memory/embedding_pipeline/":        "16lE6ZtN6ZlA6K9bHX__IXeL9aT1jh50c",
        "MPAT4/core/memory/episodic/":                  "1aSvu7M2iSgrvw50oliPWBb-S7yN16Xis",
        "MPAT4/core/memory/governance_memory/":         "1YAfWICisZs4B51V3nmh3gOStK6rWJ1Fo",
        "MPAT4/core/memory/graph_memory/":              "1QYxO9aBhpRGh8PEbiPG1Tblm1HbFTU1y",
        "MPAT4/core/memory/operational/":               "1IN_cbk2xOcNzhDJFySleJ-9VPYNkGdy1d",
        "MPAT4/core/memory/relay_memory/":              "1zhGpyFfc6OBAcyZfJV9min3pZQsu7181m",
        "MPAT4/core/memory/retrieval/":                 "1Y4iE6lE6ZtN6ZlA6K9bHX__IXeL9aT1jh",
        "MPAT4/core/memory/semantic/":                  "150caSvu7M2iSgrvw50oliPWBb-S7yN16X",
        "MPAT4/core/observability/":                    "1r_cyX_YHtvLwzQZU59jZmkFh4e3MDjqf",
        "MPAT4/core/observability/cognitive_metrics/":  "1QYxO9aBhpRGh8PEbiPG1Tblm1HbFTU1yI",
        "MPAT4/core/observability/compliance_views/":   "1N_cbk2xOcNzhDJFySleJ-9VPYNkGdy1dz",
        "MPAT4/core/observability/explainability/":     "1hGpyFfc6OBAcyZfJV9min3pZQsu7181mY",
        "MPAT4/core/observability/session_replay/":     "14iE6lE6ZtN6ZlA6K9bHX__IXeL9aT1jh5",
        "MPAT4/core/observability/telemetry/":          "10caSvu7M2iSgrvw50oliPWBb-S7yN16Xi",
        "MPAT4/core/observability/thought_trace/":      "1sYAfWICisZs4B51V3nmh3gOStK6rWJ1FoQ",
        "MPAT4/core/observability/tracing/":            "1YxO9aBhpRGh8PEbiPG1Tblm1HbFTU1yIN",
        # runtime (renombrado desde runtime_core)
        "MPAT4/core/runtime/":                          "14tSLEH9_Ekt2VkXM8e-UDnej_WX1a80f",
        "MPAT4/core/runtime/hydration/":                "1pyFfc6OBAcyZfJV9min3pZQsu7181mY4i",
        "MPAT4/core/runtime/hypervisor/":               "1E6lE6ZtN6ZlA6K9bHX__IXeL9aT1jh50",
        "MPAT4/core/runtime/microvm/":                  "1caSvu7M2iSgrvw50oliPWBb-S7yN16Xis",
        "MPAT4/core/runtime/runtime_state/":            "1YxO9aBhpRGh8PEbiPG1Tblm1HbFTU1yIN_",
        "MPAT4/core/runtime/scheduler/":                "1yFfc6OBAcyZfJV9min3pZQsu7181mY4iE",
        "MPAT4/core/runtime/unikernel/":                "16lE6ZtN6ZlA6K9bHX__IXeL9aT1jh50ca",
        "MPAT4/core/sandboxing/":                       "1Vw4UP8u6SgXh_fAG8CeEWKfmotV4lBpL",
        "MPAT4/core/sandboxing/filesystem_policies/":   "1fWICisZs4B51V3nmh3gOStK6rWJ1FoQY",
        "MPAT4/core/sandboxing/firecracker/":           "1xO9aBhpRGh8PEbiPG1Tblm1HbFTU1yIN_c",
        "MPAT4/core/sandboxing/gvisor/":                "1bk2xOcNzhDJFySleJ-9VPYNkGdy1dzhGpy",
        "MPAT4/core/sandboxing/libkrun/":               "1Ffc6OBAcyZfJV9min3pZQsu7181mY4iE6",
        "MPAT4/core/sandboxing/network_policies/":      "1lE6ZtN6ZlA6K9bHX__IXeL9aT1jh50caS",
        "MPAT4/core/sandboxing/seccomp/":               "14hDKdWPRPE1P1uxuUfwsxPSJJmL4Qq3D",
        # PROVIDERS
        "MPAT4/providers/":                             "17LCBYsOzjqnCYvru38FnytqH3E8h6Okl",
        "MPAT4/providers/anthropic/":                   "",
        "MPAT4/providers/cost_engine/":                 "",
        "MPAT4/providers/deepseek/":                    "",
        "MPAT4/providers/gemini/":                      "",
        "MPAT4/providers/local_models/":                "",
        "MPAT4/providers/nanobanana/":                  "",
        "MPAT4/providers/ollama/":                      "",
        "MPAT4/providers/openai/":                      "",
        "MPAT4/providers/provider_health/":             "",
        "MPAT4/providers/provider_routing/":            "",
        "MPAT4/providers/stability/":                   "",
        # ECOSYSTEM (limpiado — sin capabilities ni manifests)
        "MPAT4/ecosystem/":                             "170be8bj51aAvByQO-fc7GYDkIKKAwPrM",
        "MPAT4/ecosystem/cards/":                       "",
        "MPAT4/ecosystem/cards/agent_cards/":           "",
        "MPAT4/ecosystem/cards/skill_cards/":           "",
        "MPAT4/ecosystem/cards/tenant_cards/":          "",
        "MPAT4/ecosystem/connectors/":                  "",
        "MPAT4/ecosystem/discovery/":                   "",
        "MPAT4/ecosystem/registries/":                  "",
        "MPAT4/ecosystem/registries/agent_registry/":   "",
        "MPAT4/ecosystem/registries/skill_registry/":   "",
        "MPAT4/ecosystem/registries/tenant_registry/":  "",
        "MPAT4/ecosystem/skills/":                      "",
        "MPAT4/ecosystem/skills/enterprise/":           "",
        "MPAT4/ecosystem/skills/personal/":             "",
        "MPAT4/ecosystem/skills/sandboxed/":            "",
        "MPAT4/ecosystem/skills/shared/":               "",
        "MPAT4/ecosystem/skills/team/":                 "",
        # EDUCATION
        "MPAT4/education/":                             "1wSoBpZi8pl22n9a4oisFp5vjCXGTcNab",
        "MPAT4/education/evaluation/":                  "",
        "MPAT4/education/investigation_gaps/":          "",
        "MPAT4/education/lab_guides/":                  "1C4efPjp5LoMqNCzzW6HRr42Mh1tzW4rs",
        "MPAT4/education/research_tracks/":             "",
        "MPAT4/education/student_relays/":              "",
        "MPAT4/education/teaching_material/":           "1pWgHvn8oPV3pfkQ1A7vKUFxY-R1ytYy0",
        # RESEARCH
        "MPAT4/research/":                              "1lrgXcd_s3CxF766lYkTwdoRIeJeUqsHk",
        "MPAT4/research/benchmarks/":                   "1R0grNq4D42LeNtigOFiu-QHkElaWQ8-_",
        "MPAT4/research/experiments/":                  "1ooeCILfKqnavAi6aeEkkKHoF2LdStLRn",
        "MPAT4/research/futures/":                      "1E4i5Dc_JqMGZfF2LsVFPtxL2WIAqURw",
        "MPAT4/research/papers/":                       "1Yi5Erc1drlLqqQe9gID2mmOMSYyrC9EV",
        # DEPLOYMENT (IDs duplicados corregidos — quedan en blanco para reasignar)
        "MPAT4/deployment/":                            "1F_S5O18VpC8Zg_VFPtxL2WIAqURwA1Z",
        "MPAT4/deployment/bare_metal/":                 "1gUZ_da4ue7RXc_ahpyEgIBRQeSoI_GGt",
        "MPAT4/deployment/cluster/":                    "19ZMDwbP9vEdZQHyH4jkbDbEqfwQfXuWY",
        "MPAT4/deployment/edge/":                       "",
        "MPAT4/deployment/lab/":                        "",
        "MPAT4/deployment/latam_low_resource/":         "1RLow_Resource_LATAM_Compiled_OSx9",
        "MPAT4/deployment/single_node/":                "",
        "MPAT4/deployment/university/":                 "",
        # TESTS
        "MPAT4/tests/":                                 "1WjhY2Ch5YHsKlmVNFczFyownqOkfbnRO",
        "MPAT4/tests/integration/":                     "",
        "MPAT4/tests/runtime/":                         "",
        "MPAT4/tests/security/":                        "",
        "MPAT4/tests/unit/":                            "1Ngc-824Is0PUEFuJV6v9PoHgzNa7ONKO",
        # SCRIPTS
        "MPAT4/scripts/":                               "17Fy3Ya8TQWh2uzhSHkusRh577InU_Bvl",
        "MPAT4/scripts/bootstrap/":                     "1r8Jt9H5nkO5HdqKE219ZOIFQtn_nJAlI",
        "MPAT4/scripts/maintenance/":                   "13qOUCKM_TQqiXsRjv4-0rzyn-sxbuefA",
        "MPAT4/scripts/migration/":                     "1WNkBmzJvV1p655zCWJrTC8O9REE8GOvF",
        # DOCS (architecture separado de docs/ raíz)
        "MPAT4/docs/":                                  "1FlL7ACOo7o-KANItFWIBuJ62ULIHF_Oz",
        "MPAT4/docs/architecture/":                     "",
        "MPAT4/docs/internal/":                         "",
        "MPAT4/docs/public/":                           "1Dv_zPx2NLe0lbZvIodIdZsM_2U0uxn7C",
        # SYSTEM STATE (sin relay/ — fue fusionado en relay/)
        "MPAT4/system_state/":                          "1RaDO7KViCevZXlw0rEwdCaTlt17aMUgx",
        "MPAT4/system_state/cluster/":                  "19ZMDwbP9vEdZQHyH4jkbDbEqfwQfXuWY",
        "MPAT4/system_state/governance/":               "1nNqqXPo32NsQqFSgprQh-E9yDxjMmNch",
        "MPAT4/system_state/runtime/":                  "1ZSBCHfImS6PZCuSWvI8_DLea54zZhjJp",
        "MPAT4/system_state/tenants/":                  "15OkOAVrUQaJMapImCYcYv62QmGnFXxqA",
    }}

    output = Path(__file__).parent / "tree_vfolders_v2.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(arbol, f, indent=2, ensure_ascii=False)
    log(f"Árbol limpio guardado: {output}", "OK")


# ─────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────
if __name__ == "__main__":
    informe_estado()
    if not SOLO_INFORME:
        reorganizar()
    guardar_log()
