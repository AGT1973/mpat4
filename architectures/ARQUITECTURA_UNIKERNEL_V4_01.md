# ARQUITECTURA_UNIKERNEL_V4_01.md
## MPAT — Arquitectura de Aislamiento Unikernel y MicroVM
## Versión V4_01 · AGT 2026
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Fusiona: ARQUITECTURA_UNIKERNEL_V3_01 (RELAY_001, agt1973, 2026-05-11)
##          + especificación V4 completa (Claude Sonnet 4.6, RELAY_024, 2026-05-29)
## Razonamiento de fusión: ver INDICE_ARQUITECTURA_V4_01.md § Conciliación UNIKERNEL
*que has usado el formato de razonamiento adaptado por AGT*

> **Relación con otros documentos:**
> - `ARQUITECTURA_base_V4.md` (ID: 1cyg9BL...) → arquitectura general por capas — canónico V4
> - `MPAT_V4_0_ESPECIFICACION_MAESTRA.md` → pilar: "Unikernel-First"
> - `ARQUITECTURA_SUBQ_V4_01.md` → sub-queues que corren dentro de estas VMs
> - `config_policy_V4_02.yaml` (ID: 1HNxjZw...) → parámetros configurables (P4)

---

## HISTORIAL DE VERSIONES

| Versión | Cambio | Autor | Fecha | Relay |
|---|---|---|---|---|
| V3_01 | Creación inicial — concepto pedagógico + OPS/Unikraft | agt1973 | 2026-05-11 | RELAY_001 |
| V3_01b | Recuperación y subida a Drive | cursos.ai.agt@gmail.com | 2026-05-11 | RELAY_001 |
| V4_01 | Fusión completa: V3_01 preservado + especificación V4 producción | Claude Sonnet 4.6 | 2026-05-29 | RELAY_025 |

---

## PARTE I — CONCEPTO PEDAGÓGICO (preservado de V3_01, agt1973)

### I.1 Qué es un Unikernel

Un unikernel fusiona el código de la aplicación con solo las funciones mínimas del
kernel necesarias, resultando en un único binario ejecutable.

Analogía:
- Linux tradicional: navaja suiza completa
- Contenedor Docker: la navaja suiza en una caja más chica
- Unikernel: solo el filo que necesitas para ese cable específico

En MPAT V4, cada ECS (Ephemeral Cognitive Session) corre en un unikernel o MicroVM
aislado. Esta es la propiedad arquitectural central del sistema.

### I.2 Aplicación en MPAT — Tres propósitos

1. **Aislamiento de sesión:** cada `mpat_user_id` tiene su `unikernel_session_id` propio.
2. **Prefijo caching (RadixAttention):** warm start reduce TTFT más del 85%.
3. **Budget enforcement:** teardown inmediato al agotar `budget_tokens_total` (P7).

### I.3 Rendimiento — Comparativa

| Métrica | Unikernel | Firecracker MicroVM | Docker |
|---|---|---|---|
| Boot time | ~5–20ms | ~125ms | ~200–500ms |
| Imagen Nginx/Python | 2.8–8 MB | 64–128 MB | 200 MB |
| Daemon persistente | No | No | Sí (dockerd) |
| Estado entre sesiones | Imposible | Imposible | Posible fuga |

**Trampa educativa:** NO es siempre más rápido. Cold start puede ser peor que Docker
para tareas de alta complejidad. El selector automático (ver §II.2) elige el nivel
correcto según el perfil de la tarea.

### I.4 Python en Unikernel (V3_01 — preservado)

Python no se compila al kernel. Se usan unikernels pre-compilados con runtime Python incluido.

**OPS (Nanos) — proveedor primario MPAT:**
```
ops pkg list | grep python
ops pkg load nanovms/python:3.x.x -a app.py
ops build app.py -c config.json
```

**Unikraft — agentes con dependencias específicas:**
```
kraft build --arch x86_64 --plat kvm
kraft run --volume ./agents:/agents python3 /agents/mpat_agent.py
```

**INV-UK.PY.1:** el runtime Python en el unikernel es el único Python del binario.
No puede importar librerías del sistema host. Todas las dependencias deben estar
compiladas en el binario o inyectadas vía volumen.

---

## PARTE II — ESPECIFICACIÓN V4 DE PRODUCCIÓN

### II.1 Principio Fundacional

MPAT V4 abandona Docker como núcleo de aislamiento.
La razón no es ideológica: es de footprint y superficie de ataque.

Docker introduce un daemon persistente, un filesystem de capas y una red
virtual que permanecen activos entre ejecuciones. Para sesiones efímeras
(ECE — Ephemeral Cognitive Execution), ese overhead es indefendible.

**La regla del sistema:**
```
Un ECS (Ephemeral Cognitive Session) existe exactamente
el tiempo que dura la tarea. Al terminar, su VM muere.
No hay proceso zombie. No hay memoria residual. No hay estado implícito.
```

### II.2 Stack de Aislamiento — Tres Niveles

```
NIVEL 3 — Unikernel puro (NanoVM / Unikraft)
          Uso: tareas de baja memoria, inferencia local SLM, clasificadores
          Boot: < 5ms · RAM: 16–64 MB · Sin kernel Linux completo
          Limitación: sin llamadas de sistema arbitrarias
          Provider primario MPAT: OPS (Nanos)

NIVEL 2 — MicroVM (Firecracker)
          Uso: tareas de media complejidad, skills Python con dependencias
          Boot: < 125ms · RAM: 128–512 MB · Kernel Linux mínimo
          Limitación: sin dispositivos de bloque complejos
          INV-FIRE.1: mem_size_mib mínimo = 128 MB (ver §II.4)

NIVEL 1 — Container ligero (gVisor / kata)
          Uso: fallback cuando se requieren syscalls no soportadas en L2/L3
          Boot: < 500ms · RAM: hasta 2 GB
          Regla: solo usar si L2 no es viable — documentar la razón en audit log
```

**Selector automático (`vm_selector.py`):**
```python
# Regla de selección — no hardcodeada (P4) — lee de config_policy_V4_02.yaml
if task.memory_mb <= 64 and task.syscall_profile == "minimal":
    return IsolationLevel.UNIKERNEL
elif task.memory_mb <= 512:
    return IsolationLevel.FIRECRACKER
else:
    return IsolationLevel.GVISOR  # con alerta de auditoría P5
```

### II.3 Ciclo de Vida de un ECS (Ephemeral Cognitive Session)

```
SPAWN
  │
  ├─ vm_selector() → elige nivel de aislamiento
  ├─ boot VM (< 125ms Firecracker / < 5ms Unikernel)
  ├─ inyectar ECS snapshot desde Memory Fabric
  ├─ capturar skill versions snapshot (P8 — inmutable durante ejecución)
  │
EXECUTE
  │
  ├─ Orchestrator → Plan → Execute → Reflect → Replan
  ├─ Budget deducido en tiempo real (P7 — Conservation Law)
  ├─ OTel spans emitidos por cada tool call (P10 — observabilidad)
  │
TEARDOWN
  │
  ├─ Memory delta → Memory Fabric (consolidar episódico)
  ├─ Budget no usado → retorna al padre INMEDIATAMENTE (P7)
  ├─ Relay Packet serializado → relay/ en Drive
  ├─ VM destruida — sin proceso residual
  ├─ Dream Cycle trigger (RES.119 — si dream_cycle.trigger = "on_destroy")
```

**INV-ECE.1:** El budget no usado retorna al padre antes de destruir la VM.
Orden obligatorio: (1) serializar relay, (2) retornar budget, (3) destruir VM.
Invertir el orden viola P7 (Conservation Law).

**INV-ECE.2:** El skill snapshot capturado en SPAWN es inmutable durante
toda la sesión. Si una skill se actualiza externamente durante la ejecución,
el ECS activo ignora el cambio. El nuevo snapshot aplica al siguiente SPAWN.

**INV-ECE.3 (nuevo V4 — RES.158):** Todo namespace de ECS incluye `tenant_id`
como segundo segmento. Patrón: `mpat:cx:{tenant_id}:{session_id}:{componente}`

### II.4 Firecracker — Configuración Base

```yaml
# firecracker_base_config.yaml — parámetros configurables (P4)
# Fuente canónica: config_policy_V4_02.yaml → runtime.min_memory_mb
vcpu_count: 1               # ajustable hasta 4 para tareas paralelas
mem_size_mib: 128           # mínimo = 128 MB (INV-FIRE.1)
kernel_image_path: /opt/mpat/vmlinux-5.10-unikernel
rootfs_path: /opt/mpat/rootfs-mpat-minimal.ext4
network_interfaces:
  - iface_id: eth0
    guest_mac: "AA:FC:00:00:00:01"
    host_dev_name: tap0
boot_args: "console=ttyS0 reboot=k panic=1 pci=off"
```

**INV-FIRE.1:** `mem_size_mib` mínimo = 128 MB.

Conciliación de fuentes (tabla obligatoria por skill-trabajo-mpat4):

| Fuente | Valor | Fecha | Evidencia | Confianza |
|---|---|---|---|---|
| RELAY_003_MPAT_V4 | 128 MB | 2026-05-13 | CPython falla en ciclo GC con múltiples ECS simultáneos < 128 MB | ALTA |
| ARQUITECTURA_UNIKERNEL_V3_01 (original) | 128 MB | 2026-05-11 | config YAML: `min_memory_mb: 128` en parámetros CAPA_14 | ALTA |
| config_policy_V4_02.yaml | 128 MB | 2026-05-19 | `runtime.min_memory_mb: 128` | ALTA |
| Documentos V3 genéricos (referenciados en RELAY_003) | 64 MB | anterior | Sin referencia técnica | BAJA |

**Decisión:** 128 MB. Tres fuentes independientes con evidencia técnica. RESUELTO.

### II.5 Unikraft — Perfil Cognitivo Mínimo

Para tareas de inferencia local con SLM (Phi-3, Llama 3.2 1B):

```
Unikraft build profile: mpat-cognitive-minimal
  Libs incluidas: musl, lwip, vfscore, ramfs
  Libs excluidas: posix-process, pthread-embedded (no multithreading)
  Python: MicroPython 1.22 (no CPython — sin GC overhead)
  Tamaño imagen: < 8 MB
  Boot time objetivo: < 5ms
  Caso de uso: clasificador de routing, extractor de entidades, scoring rápido
```

### II.6 Memory Fabric — Interfaz con el ECS

El ECS no tiene memoria interna persistente. Toda la memoria es externa.

```
Memory Fabric (externo al ECS)
├── Episódica       → eventos de sesiones anteriores (ChromaDB)
├── Semántica       → embeddings de conocimiento (FAISS)
├── Operacional     → estado de ejecución en curso (Redis)
├── Relay           → traspaso cognitivo entre sesiones (Drive)
└── Gobernanza      → políticas y contratos activos (OPA)

Al SPAWN: ECS recibe snapshot relevante de los 5 tipos.
Al TEARDOWN: ECS entrega delta de Episódica + Operacional.
Semántica y Gobernanza son de solo lectura durante ejecución.
```

### II.7 Integración con CAPA_03 (Orchestrator)

El Orchestrator (`ARQUITECTURA_base_V4.md` CAPA_03) es el único componente
autorizado para SPAWN y TEARDOWN de ECS.

```
Orchestrator
    │
    ├─ vm_pool_manager.py → warm pool de VMs pre-booteadas
    │   INV: warm_pool_miss_rate > 10% → auto-escalar pool (P4)
    │
    ├─ ecs_spawner.py → asigna VM del pool, inyecta ECS snapshot
    │
    └─ ecs_teardown.py → consolida memory delta, retorna budget, destruye VM
```

**Warm pool:** VMs pre-booteadas en estado idle para reducir latencia.
Tamaño por defecto: 3 Firecracker + 2 Unikernel.
Parámetro: `session_scheduler.warm_pool_size: 3` en `config_policy_V4_02.yaml` (P4).

---

## PARTE III — PARÁMETROS CAPA_14 (preservado de V3_01, extendido V4)

```yaml
# config_policy_V4_02.yaml — sección unikernel (P4)
unikernel:
  enabled: true
  warm_ttl_seconds: 300
  budget_tokens_default: 50000
  provider: "nanos"
  python:
    runtime_version: "3.11"
    min_memory_mb: 128
    max_memory_mb: 512
    cold_start_timeout_ms: 2000
    serverless_mode: true

session_scheduler:
  warm_pool_size: 3
  cold_boot_timeout_seconds: 10
  max_concurrent_sessions_per_tenant: 5

tools:
  allowed_runtimes:
    - "nanovm"
    - "unikraft"
    - "firecracker"
```

**P15 — Aislamiento de sesión es configurable, no implícito (RES.138/RES.127):**
- `isolation_mode: unikernel` → UnikerManager (default)
- `isolation_mode: sandbox` → SandboxManager (gVisor, para entornos sin hypervisor)
- Son mutuamente excluyentes por sesión (INV-ISO.1)
- Cambio de `isolation_mode` requiere restart del tenant (INV-ISO.3)

---

## PARTE IV — SEGURIDAD Y COHERENCIA

### IV.1 Superficie de Ataque

| Vector | Mitigación | Nivel |
|---|---|---|
| Escape de VM | Firecracker: sin dispositivos de bloque, sin USB | ALTO |
| Memory leak entre sesiones | TEARDOWN destruye VM completamente | ALTO |
| Exfiltración de datos | Network solo hacia MCP endpoints allowlisted (P1) | ALTO |
| Código malicioso en skill | Skill sandbox pre-validación (VOL1 item 15) | MEDIO |
| Syscall injection | Seccomp-BPF profile mínimo en Firecracker | ALTO |
| Cross-tenant | INV-ECE.3: namespace incluye tenant_id (RES.158) | ALTO |

### IV.2 Coherencia con Principios Transversales

| Principio | Estado | Referencia |
|---|---|---|
| P3 — Zero Trust | IMPLEMENTADO | Destrucción VM garantiza sin residuo |
| P4 — Nada hardcodeado | IMPLEMENTADO | Todos los parámetros en config_policy_V4_02.yaml |
| P5 — Auditable | IMPLEMENTADO | OTel spans en EXECUTE + teardown log |
| P7 — Budget Conservation Law | IMPLEMENTADO | INV-ECE.1: budget retorna antes de destruir VM |
| P8 — Skill versioning | IMPLEMENTADO | INV-ECE.2: snapshot inmutable durante sesión |
| P15 — Aislamiento configurable | IMPLEMENTADO | isolation_mode en policy.yaml (RES.138) |

---

## PARTE V — DEUDA TÉCNICA

| ID | Descripción | Prioridad |
|---|---|---|
| DT-UNI-01 | Integración con Self-Healing Runtime (VOL2 item 47) | MEDIA |
| DT-UNI-02 | Warm pool dinámico basado en métricas OTel (RES.168) | MEDIA |
| DT-UNI-03 | Perfil Unikraft para inferencia WASM (VOL1 item 15) | ALTA |
| DT-UNI-04 | Tensor Parallelism entre ECS (VOL2 item 56) | BAJA |
| DT-UNI-05 | RadixAttention implementación en Nivel-3 — documentada, no implementada | ALTA |

---

## REGISTRO DE ARCHIVOS REEMPLAZADOS

- `ARQUITECTURA_UNIKERNEL_V3_01 (4).md` (ID: 1TlIuiF...) — OBSOLETO
- `ARQUITECTURA_UNIKERNEL_V3_01.md` (ID: 1X_94gz...) — OBSOLETO

---

*ARQUITECTURA_UNIKERNEL_V4_01.md · Fusión: agt1973 (V3_01) + Claude Sonnet 4.6 (V4)*
*RELAY_025 · 2026-05-29*
*que has usado el formato de razonamiento adaptado por AGT*
