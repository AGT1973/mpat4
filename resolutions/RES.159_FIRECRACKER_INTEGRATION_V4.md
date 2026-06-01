# RES.159 — Firecracker MicroVM Integration
## MPAT4 · T-004 · RELAY_004
## Autor: cursos.agt.ia@gmail.com (docente_AGT_2026) · 2026-05-21
## Cierra: INV-ECS-V4.1 (todo ECS ACTIVE tiene unikernel_id)

*que has usado el formato de razonamiento adaptado por AGT*

---

## 1. PROBLEMA QUE RESUELVE

En V3, el aislamiento de ejecucion era gVisor (sandbox) o thread (No-GIL).
Ambos comparten el kernel del host: un exploit de kernel compromete todos los tenants.
En MPAT4, el requisito es aislamiento soberano: cada sesion de agente corre en
un kernel dedicado sin superficie de ataque compartida.

Firecracker MicroVM es la respuesta: boot < 50ms, 5MB de footprint de memoria,
superficie de ataque de ~50K lineas de codigo (vs ~27M de QEMU).

---

## 2. DECISION ARQUITECTURAL

**Opcion A**: gVisor mejorado — mas rapido que Docker pero sigue compartiendo kernel.
**Opcion B**: Firecracker MicroVM — kernel dedicado por sesion.
**Opcion C**: WASM sandbox — portable pero sin soporte de red real ni filesystem completo.

**ELEGIDA: Opcion B.** El requisito de aislamiento soberano (un tenant no puede afectar
a otro por bugs de kernel) solo lo cumple un kernel dedicado. El costo de boot < 50ms
es aceptable para sesiones que duran minutos o horas. WASM no tiene el ecosistema
Python necesario para ejecutar los agentes.

---

## 3. INVARIANTES (RES.159)

```
INV-FIRE.1: un MicroVM NUNCA es compartido entre tenants ni entre sesiones.
  Un MicroVM = un tenant_id + un session_id. ABSOLUTO.

INV-FIRE.2: boot_latency_ms DEBE ser < 50ms para warm pool.
  Si boot_latency_ms >= 50ms: alerta OTel severity=WARNING.
  Si boot_latency_ms >= 200ms: alerta OTel severity=ERROR + escalar a ops.

INV-FIRE.3: al DESTROY, el MicroVM libera TODA la memoria asignada antes de
  retornar control al UnikerManager. No lazy-free. El budget de memoria del
  nodo debe reflejar la liberacion en < 100ms.

INV-FIRE.4: todo MicroVM tiene un TTL maximo (default 3600s).
  Si la sesion supera el TTL: el kernel envia SIGTERM al agente,
  espera 30s para teardown graceful, luego SIGKILL + DESTROY.

INV-FIRE.5: INV-NHP-UK.1 de V3 heredado — TTL del MicroVM <= TTL de la sesion NHP.
  Si unikernel.ttl > nhp.session_ttl: ZTS emite renovacion automatica.

INV-FIRE.6: MicroVM sin AgentCard registrado en agent_registry/ NO puede ser spawneado.
  P13 aplica antes del boot — no solo antes de la invocacion de tools.
```

---

## 4. CICLO DE VIDA

```
[ALLOCATING]
  UnikerManager.allocate(tenant_id, session_id, agent_card_id)
  → verificar AgentCard en agent_registry/ (INV-FIRE.6 + P13)
  → reservar slot en warm_pool o crear nuevo (si pool vacio)
  → asignar unikernel_id = UUID v4

[BOOTING]
  → cargar vmlinux + rootfs del agente
  → configurar network (virtio-net, IP privada por tenant)
  → configurar vsock (comunicacion con Cognitive Kernel)
  → medir boot_latency_ms (INV-FIRE.2)
  → emitir agent.spawned en EventBusV4

[READY]
  → MicroVM aceptando conexiones vsock
  → ECS.unikernel_id = unikernel_id (INV-ECS-V4.1)
  → TTL timer iniciado (INV-FIRE.4)

[RUNNING]
  → agente ejecutando tareas
  → health checks cada 30s via vsock
  → budget monitoreado por Cognitive Kernel

[TEARDOWN]  ← disparado por: session.teardown | budget.exhausted | TTL expirado
  → SIGTERM al agente (30s grace period)
  → RelayExporter.export() si relay_export_required
  → emitir session.teardown en EventBusV4

[DESTROYING]
  → SIGKILL si el agente no respondio al SIGTERM
  → liberar memoria (INV-FIRE.3)
  → liberar IP privada del pool de red
  → actualizar agent_registry/ (estado DESTROYED)

[DESTROYED]
  → unikernel_id marcado como expirado en Redis TTL=60s
  → budget liberado retorna al padre (P7 conservation law)
```

---

## 5. WARM POOL

El warm pool mantiene MicroVMs pre-booteados sin agente para minimizar
latencia de SPAWN. Un MicroVM del warm pool tiene el kernel iniciado
pero sin rootfs de agente cargado — solo el kernel base.

Al SPAWN desde warm pool:
1. Tomar MicroVM del pool (ya en estado BOOTING parcial)
2. Cargar rootfs del agente especifico via overlay filesystem
3. Tiempo reducido: < 15ms (vs < 50ms desde cero)

```
INV-WARM.1: warm pool size es configurable por nodo (default: 5 MicroVMs).
INV-WARM.2: warm pool se repone en background despues de cada SPAWN.
INV-WARM.3: MicroVM del warm pool sin uso por > 300s es destruido (evitar
  recursos ociosos con TTL abierto).
```

Config en policy.yaml:
```yaml
firecracker:
  warm_pool_size: 5
  warm_pool_replenish_on_spawn: true
  warm_pool_idle_ttl_seconds: 300
  boot_latency_warn_ms: 50
  boot_latency_error_ms: 200
  unikernel_ttl_seconds: 3600
  teardown_grace_seconds: 30
  memory_mb_default: 512
  memory_mb_max: 4096
  vcpu_count: 2
```

---

## 6. COMUNICACION vsock

El Cognitive Kernel se comunica con el agente dentro del MicroVM via
AF_VSOCK (Virtual Socket). No hay red TCP entre kernel y agente — vsock
opera en el hypervisor layer, sin stack de red.

```
CID del MicroVM: unikernel_id[:8] como uint32 (collision improbable con UUID)
Puerto kernel → agente: 5000 (comandos, tool_calls)
Puerto agente → kernel: 5001 (resultados, eventos)
```

Protocolo: length-prefixed Protobuf messages sobre vsock stream.
El Cognitive Kernel envía `KernelCommand` y recibe `AgentResponse`.

---

## 7. INTEGRACION CON EVENT BUS (T-007)

| Evento | Cuando | Payload |
|---|---|---|
| `agent.spawned` | Boot completado, MicroVM en READY | AgentSpawnedPayload (unikernel_boot_ms) |
| `session.teardown` | MicroVM iniciando shutdown | SessionTeardownPayload |
| `budget.exhausted` | Kernel detecta budget >= tokens | BudgetExhaustedPayload |
| `governance.violation` | Policy bloquea accion del agente | GovernanceViolationPayload |

---

## 8. INTEGRACION CON RELAY (T-002)

Al entrar en TEARDOWN con `relay_export_required=True`:
1. Cognitive Kernel llama `RelayExporter.export(session_id, tenant_id)`
2. RelayExporter consolida memoria episodica + semantica
3. RelayPacket firmado con HMAC del Cognitive Kernel (V4-INV-MEMORY.3)
4. RelayPacket escrito en relay_store/ con TTL=30 dias
5. relay_packet_id retornado y registrado en agent_registry/
6. MicroVM puede continuar hacia DESTROYING

---

## 9. DEUDA TECNICA ABIERTA

| DT | Descripcion | Prioridad |
|---|---|---|
| DT-FIRE-001 | Live migration de MicroVM entre nodos (para balanceo de carga sin teardown) | BAJA — V5 |
| DT-FIRE-002 | Snapshot/restore de MicroVM (alternativa a RelayPacket para sesiones muy largas) | MEDIA — V4.1 |
| DT-FIRE-003 | Metricas de densidad de MicroVMs por nodo en OTel | ALTA — implementar en observability/ |

---

## 10. TRAMPA EDUCATIVA

**"Firecracker es lo mismo que Docker con --privileged=false. Ambos aislan el proceso."**

Falso. Docker, incluso sin privilegios, comparte el kernel del host. Si hay un bug
en el syscall handler del kernel, un proceso Docker puede explotarlo y escalar a root
en el host — afectando todos los contenedores. Firecracker corre un kernel Linux
SEPARADO dentro de la MicroVM. Si hay un bug en el kernel del agente, el exploit
llega hasta el hypervisor de Firecracker — cuya superficie de ataque son ~50K lineas
de Rust (memory-safe), no los 27M de lineas de QEMU. El atacante necesita explotar
Firecracker (Rust, sin unsafe en el path critico) para llegar al host. La diferencia
no es de configuracion — es de arquitectura de aislamiento.

---

*RES.159_FIRECRACKER_INTEGRATION_V4.md · MPAT4 · 2026-05-21*
*cursos.agt.ia@gmail.com (docente_AGT_2026) · T-004 · RELAY_004*
*que has usado el formato de razonamiento adaptado por AGT*
