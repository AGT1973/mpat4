# MPAT4_DEST
# destino: resoluciones
# nombre: RESOLUCION_BUDGET_PERSISTENCE_SOTA_V1.md
# alumno: cursos.agt.ia@gmail.com

---

# Resolución SOTA — BudgetWindowPersistence
## Autor: cursos.agt.ia@gmail.com · 2026-05-27
## Módulo: persistence · Versión: V4_01
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Tipo: RESOLUCIÓN TÉCNICA COMPLETA — Cierre de análisis SOTA

---

## ÍNDICE

1. Contexto y alcance
2. Inventario de decisiones de diseño
3. Análisis profundo — Decisión 1: Inmutabilidad `frozen=True`
4. Análisis profundo — Decisión 2: Repositorio externo
5. Análisis profundo — Decisión 3: Hidratación por reconstrucción
6. Análisis profundo — Decisión 4: `fragment_id` determinista
7. Análisis profundo — Decisión 5: `load()` fail-safe
8. Brechas críticas identificadas — con solución completa
9. Implementación de referencia — código completo
10. Matriz de tests ampliada (15 → 22)
11. Nuevos invariantes propuestos
12. Resoluciones formales
13. Deuda técnica residual
14. Conclusión y veredicto SOTA

---

## 1. CONTEXTO Y ALCANCE

Este documento cierra el análisis SOTA iniciado sobre las decisiones de diseño de
`BudgetWindowPersistence` en el módulo de persistencia de MPAT4.

El análisis cubre:
- Validación de cada decisión de diseño contra el SOTA (mayo 2026)
- Identificación de brechas que el diseño original no cubre
- Solución concreta para cada brecha
- Código de referencia listo para integrar
- Tests adicionales para alcanzar cobertura completa
- Invariantes nuevos que emergen de este análisis
- Resoluciones formales de cada punto abierto

Fuentes consultadas: documentación Pydantic v2.13.4, Redis 8.6.2 (AGPL),
LiteLLM circuit breaker (abril 2026), literatura de sistemas distribuidos
(idempotencia, optimistic locking, graceful degradation).

---

## 2. INVENTARIO DE DECISIONES DE DISEÑO

| # | Decisión | INV relacionado | Estado previo | Estado post-análisis |
|---|----------|-----------------|---------------|----------------------|
| D1 | `frozen=True` en BudgetWindow | INV-AESP-006 | Correcto parcial | Requiere inmutabilidad profunda |
| D2 | Repositorio externo sin tocar instancia | INV-PERSIST-001 | Correcto | Requiere ABC base |
| D3 | Hidratación por construcción nueva | Sin INV asignado | Correcto parcial | Requiere especificar variante validada |
| D4 | `fragment_id` determinista | Sin INV asignado | SOTA completo | Documentar como INV |
| D5 | `load()` fail-safe retorna None | INV-PERSIST-00X | Correcto parcial | `save()` fail-safe sin documentar |
| D6 | 15 tests definidos | INV-PERSIST-001:006 | Cobertura básica | 7 tests adicionales requeridos |

---

## 3. DECISIÓN 1 — INMUTABILIDAD `frozen=True`

### 3.1 Lo que el diseño garantiza

`model_config = {"frozen": True}` en Pydantic v2 activa:
- Bloqueo de `__setattr__`: cualquier asignación directa lanza `ValidationError`
- Generación automática de `__hash__()`: la instancia es hashable si todos sus campos lo son
- Compatibilidad con `model_copy(update={})`: para crear variantes sin mutar

### 3.2 La brecha crítica — Inmutabilidad superficial

`frozen=True` es inmutabilidad **superficial** (shallow). No cubre campos con
tipos mutables internos. Este comportamiento está documentado como "faux-immutability"
en la documentación oficial de Pydantic v2.

**Ejemplo del problema:**

```python
class BudgetWindow(BaseModel):
    model_config = ConfigDict(frozen=True)
    allowed_models: list[str]       # PELIGRO: mutable interno

bw = BudgetWindow(allowed_models=["gpt-4o"])
bw.allowed_models = ["gpt-3.5"]    # Falla correctamente
bw.allowed_models.append("claude") # SILENCIOSO: no falla, muta la instancia
```

El segundo caso viola INV-AESP-006 sin que ningún mecanismo lo detecte.
Este es el tipo de bug que no aparece en tests simples y emerge en producción
bajo concurrencia.

### 3.3 Solución — Inmutabilidad profunda

**Regla:** todo campo de `BudgetWindow` que sea colección debe usar el tipo
inmutable equivalente:

| Tipo mutable | Reemplazar por | Notas |
|---|---|---|
| `list[T]` | `tuple[T, ...]` | Pydantic convierte automáticamente |
| `set[T]` | `frozenset[T]` | Pydantic convierte automáticamente |
| `dict[K, V]` | Sin soporte nativo | Ver nota abajo |
| `list[list[T]]` | `tuple[tuple[T, ...], ...]` | Anidamiento recursivo |

Para `dict`: Pydantic no tiene un tipo `frozendict` nativo. Las opciones SOTA son:

**Opción A (recomendada):** usar `pydantic.types.FrozenSet` o modelar como
`tuple[tuple[str, str], ...]` (pares clave-valor). Adecuado para diccionarios
pequeños y estáticos.

**Opción B:** usar la librería `freeze` (PyPI: `frz`), que provee `FDict`,
`FList` y `FSet` con inmutabilidad recursiva. Verificar compatibilidad con
Pydantic v2 antes de adoptar.

**Opción C (sin dependencias extra):** modelo auxiliar frozen para cada dict complejo.

### 3.4 Resolución formal — D1

**Estado:** RESUELTO con acción requerida

**Acción:** auditar todos los campos de `BudgetWindow`. Cualquier `list`, `set`
o `dict` debe migrarse a su equivalente inmutable. El INV-AESP-006 debe
actualizarse para especificar que la inmutabilidad es profunda (deep), no solo
superficial (shallow).

**INV nuevo:** ver sección 11.

---

## 4. DECISIÓN 2 — REPOSITORIO EXTERNO

### 4.1 Evaluación

El patrón es correcto y está completamente alineado con SOTA (Clean Architecture,
DDD, y con la dirección que toma pydantic-ai en su propia API de persistencia).

La separación `dominio / repositorio` es la decisión más estructuralmente sana
del diseño. `BudgetWindowPersistence` nunca muta la instancia: solo serializa
y deserializa. Esto hace que el objeto de dominio sea completamente agnóstico
a su mecanismo de persistencia.

### 4.2 Brecha — Sin ABC base

El diseño actual no tiene una interfaz abstracta que defina el contrato del
repositorio. Esto genera dos problemas concretos:

- Si en el futuro Memory Fabric cambia de Redis a Valkey, DynamoDB o disco,
  no hay contrato que el nuevo backend deba cumplir
- Los tests actuales prueban la implementación Redis directamente, no el contrato

### 4.3 Solución — ABC base

```python
# schemas/budget_window_repository.py
from abc import ABC, abstractmethod
from typing import Optional
from ..core.budget_window import BudgetWindow

class BudgetWindowRepository(ABC):
    """
    Contrato de persistencia para BudgetWindow.
    INV-PERSIST-ABC-001: cualquier implementación debe respetar estas firmas.
    """

    @abstractmethod
    async def save(self, window: BudgetWindow) -> bool:
        """
        Persiste el estado de un BudgetWindow.
        Retorna True si tuvo éxito, False si falló (nunca raise).
        INV: save() es idempotente — múltiples llamadas con el mismo
             window producen el mismo resultado en el backend.
        """
        ...

    @abstractmethod
    async def load(
        self,
        tenant_id: str,
        agent_id: str
    ) -> Optional[BudgetWindow]:
        """
        Recupera un BudgetWindow o retorna None si no existe o hay error.
        INV: load() nunca raise — el sistema puede operar sin estado persistido.
        """
        ...
```

### 4.4 Resolución formal — D2

**Estado:** CORRECTO con mejora recomendada (no bloqueante)

**Acción:** crear `BudgetWindowRepository` como ABC en `schemas/`.
`BudgetWindowPersistence` hereda de ella. Tests futuros pueden probar contra
la ABC con mocks. Si Memory Fabric cambia, solo se implementa la nueva clase.

---

## 5. DECISIÓN 3 — HIDRATACIÓN POR RECONSTRUCCIÓN

### 5.1 Contexto

El diseño establece que `load()` construye una nueva instancia frozen con los
datos recuperados de Memory Fabric. Esto es correcto en principio.

El detalle que no está especificado: ¿se usa `BudgetWindow(**data)` (validado)
o `BudgetWindow.model_construct(**data)` (sin validación)?

### 5.2 Análisis de las dos variantes

**Variante A — Construcción validada:** `BudgetWindow(**data)`

Ventajas:
- Todos los validadores Pydantic se ejecutan
- Detecta corrupción de datos en Redis (tipos incorrectos, campos faltantes)
- Si Redis tiene datos inválidos, `load()` recibe `ValidationError`, lo captura
  y retorna `None` activando el fail-safe. El sistema arranca con default limpio.

Desventajas:
- Ligeramente más lento (ejecución de validadores)
- Para objetos muy grandes con validación compleja, el overhead puede ser medible

**Variante B — Construcción sin validación:** `BudgetWindow.model_construct(**data)`

Ventajas:
- Más rápido (bypasea validadores)

Desventajas:
- Carga silenciosamente un estado inválido si Redis tiene datos corruptos
- Viola el principio de fail-safe: es peor cargar estado inválido que no cargarlo

### 5.3 Decisión

Para `BudgetWindow` (objeto de presupuesto — datos financieros), la Variante A
es obligatoria. La validación en hidratación es parte del contrato de seguridad
del sistema: datos corruptos en Redis no deben contaminar el estado operativo del agente.

La diferencia de rendimiento es despreciable para objetos de esta escala.

### 5.4 Implementación correcta de load()

```python
async def load(
    self,
    tenant_id: str,
    agent_id: str
) -> Optional[BudgetWindow]:
    """
    Fail-safe por diseño.
    INV-PERSIST-LOAD-001: cualquier excepción retorna None, nunca raise.
    INV-PERSIST-LOAD-002: la hidratación es siempre validada (no model_construct).
    """
    try:
        fragment_id = self._fragment_id(tenant_id, agent_id)
        raw = await self._redis.get(fragment_id)

        if raw is None:
            return None  # Clave no existe — arranque limpio

        data = json.loads(raw)
        # Variante A obligatoria: validación completa en hidratación
        return BudgetWindow(**data)

    except json.JSONDecodeError as e:
        # Datos corruptos en Redis — tratado igual que clave inexistente
        self._logger.error(
            "BudgetWindow deserialization failed",
            tenant_id=tenant_id,
            agent_id=agent_id,
            error=str(e)
        )
        return None

    except ValidationError as e:
        # Datos con schema inválido — activar fail-safe
        self._logger.error(
            "BudgetWindow validation failed on hydration",
            tenant_id=tenant_id,
            agent_id=agent_id,
            error=str(e)
        )
        return None

    except Exception as e:
        # Redis caído u error de conexión — fail-safe general
        self._logger.error(
            "BudgetWindowPersistence.load unexpected error",
            tenant_id=tenant_id,
            agent_id=agent_id,
            error=str(e)
        )
        return None
```

### 5.5 Resolución formal — D3

**Estado:** RESUELTO con especificación explícita

**Acción:** documentar en el contrato del módulo que la hidratación usa
`BudgetWindow(**data)`, no `model_construct`. Agregar `INV-PERSIST-LOAD-002`.

---

## 6. DECISIÓN 4 — `fragment_id` DETERMINISTA

### 6.1 Evaluación

Esta es la decisión más sólida del diseño. El esquema `aesp:budget:{tenant_id}:{agent_id}`
cumple con todos los criterios SOTA para claves de idempotencia en sistemas distribuidos:

- **Estable:** la misma combinación lógica siempre produce la misma clave
- **Jerárquica:** `namespace:tipo:tenant:entidad` — legible y debuggeable
- **Determinista:** no requiere búsqueda en índice ni generación aleatoria
- **Idempotente:** `save()` es un upsert seguro sin race condition de inserción

La literatura de sistemas distribuidos (2026) confirma que las claves compuestas
del tipo `{namespace}:{entity}:{tenant}:{id}` son el patrón recomendado para
deduplicación y operaciones idempotentes.

### 6.2 Advertencia — JSON-in-string

El SOTA actual de Redis identifica el **anti-patrón JSON-in-string**: serializar
objetos completos como string en Redis significa que cada operación requiere
deserializar el objeto entero, incluso para acceder a un solo campo.

Para `BudgetWindow`, que probablemente se lee con frecuencia durante la ejecución
del agente, esto puede impactar en latencia si el objeto crece.

**Alternativas:**

| Opción | Descripción | Pros | Contras |
|--------|-------------|------|---------|
| JSON-in-string (actual) | `SET key json_string` | Simple, sin dependencias | Deserialización completa siempre |
| Redis Hash | `HSET key field value` | Acceso por campo sin deserializar | Más complejo, requiere manejo de tipos |
| RedisJSON (módulo) | Acceso nativo a campos JSON | SOTA para objetos complejos | Dependencia de módulo Redis |

**Para MPAT4 / Memory Fabric:** si `BudgetWindow` tiene menos de 10 campos
y se accede siempre completo, JSON-in-string es aceptable y su simplicidad
tiene valor real. Si en el futuro el objeto crece o se necesita acceso parcial,
migrar a Redis Hash o RedisJSON.

### 6.3 Resolución formal — D4

**Estado:** CORRECTO — elevar a INV

**Acción:** documentar el esquema de `fragment_id` como invariante formal.
Ver sección 11.

---

## 7. DECISIÓN 5 — `load()` FAIL-SAFE

### 7.1 Evaluación

El fail-safe en `load()` es correcto y está alineado con el SOTA de AI Gateways
en producción (LiteLLM, abril 2026). Retornar `None` ante cualquier error
es la degradación elegante correcta.

### 7.2 Brecha crítica — `save()` sin fail-safe documentado

El diseño documenta el fail-safe de `load()` en detalle pero no especifica
qué sucede cuando `save()` falla (Redis caído, timeout, pool exhausto).

Este es un escenario crítico: si el agente ejecuta trabajo y luego `save()` falla,
el estado de presupuesto se pierde entre reinicios. El siguiente arranque verá
`load()` retornar `None` y arrancará con un `BudgetWindow` default vacío,
lo que puede causar que el agente sobreconsumo recursos (budget overflow).

### 7.3 Solución — `save()` fail-soft con logging

```python
async def save(self, window: BudgetWindow) -> bool:
    """
    Persiste BudgetWindow en Memory Fabric.

    INV-PERSIST-SAVE-001: save() nunca raise — es fail-soft.
    INV-PERSIST-SAVE-002: save() retorna bool indicando éxito.
    INV-PERSIST-SAVE-003: fallo de save() se loggea con nivel ERROR
                          para detección en observabilidad.
    INV-PERSIST-SAVE-004: el objeto BudgetWindow vive en memoria del
                          agente independientemente del resultado de save().
                          La persistencia es best-effort, no bloqueante.

    Por qué best-effort:
        Un fallo de Redis no debe detener la ejecución del agente.
        El budget en memoria sigue siendo la fuente de verdad durante
        la sesión activa. La pérdida ocurre solo en un reinicio posterior.
    """
    try:
        fragment_id = self._fragment_id(window.tenant_id, window.agent_id)
        serialized = window.model_dump_json()
        await self._redis.set(fragment_id, serialized)
        return True

    except Exception as e:
        self._logger.error(
            "BudgetWindowPersistence.save failed — state not persisted",
            tenant_id=window.tenant_id,
            agent_id=window.agent_id,
            error=str(e),
            # Incluir el valor actual del budget para recuperación manual
            consumed=str(window.consumed),
            allocated=str(window.allocated),
        )
        return False
```

### 7.4 Brecha adicional — Circuit breaker ausente

El diseño actual llama directamente a Redis en cada `save()` y `load()`. Si
Redis está caído, cada llamada incurre en el timeout completo antes de fallar.
Con muchos agentes activos, esto puede generar una cascada de timeouts que
degrada el sistema entero.

El SOTA de AI Gateways en producción (LiteLLM, abril 2026) implementa un
circuit breaker que detecta 5 fallos consecutivos y abre el circuito, haciendo
que las llamadas siguientes fallen inmediatamente (0ms) en lugar de esperar
el timeout completo.

**Solución con `purgatory` (async circuit breaker):**

```python
from purgatory import AsyncCircuitBreakerRegistry

# Inicialización del registry (singleton del módulo de persistencia)
_cb_registry = AsyncCircuitBreakerRegistry(
    default_threshold=5,       # Abre tras 5 fallos consecutivos
    default_ttl=30,            # Intenta recuperar tras 30 segundos
)
_budget_breaker = await _cb_registry.get_breaker("budget_persistence")

async def save(self, window: BudgetWindow) -> bool:
    try:
        async with _budget_breaker:
            fragment_id = self._fragment_id(window.tenant_id, window.agent_id)
            await self._redis.set(fragment_id, window.model_dump_json())
            return True
    except CircuitBreakerOpen:
        # Redis confirmado como no disponible — fail inmediato, sin timeout
        self._logger.warning("BudgetPersistence circuit open — Redis unavailable")
        return False
    except Exception as e:
        self._logger.error("BudgetWindowPersistence.save failed", error=str(e))
        return False
```

### 7.5 Resolución formal — D5

**Estado:** PARCIALMENTE RESUELTO

**Acciones requeridas:**
1. Implementar `save()` con fail-soft (retorno bool, logging estructurado)
2. Evaluar adopción de circuit breaker (`purgatory` o implementación propia)
3. Documentar que la pérdida de estado entre sesiones es el riesgo residual
   aceptado del diseño fail-soft
4. Agregar tests para `save()` con Redis caído (ver sección 10)

---

## 8. BRECHAS CRÍTICAS — CONCURRENCIA Y TTL

### 8.1 Brecha — Concurrencia sin documentar

El diseño actual no especifica el comportamiento cuando dos instancias del mismo
agente (mismo `tenant_id` + `agent_id`) hacen `save()` simultáneamente.

La clave `aesp:budget:{tenant_id}:{agent_id}` es única por agente. Si dos
procesos escriben concurrentemente, Redis aplica **last-write-wins** sin notificación.
Para datos de presupuesto (financieros), esto puede causar:

- Agente A escribe: consumed=100
- Agente B escribe: consumed=150 (más reciente, basado en estado desactualizado)
- Resultado en Redis: consumed=150 (incorrecto: el consumo real es 100+150=250)

Esta situación es poco probable si cada agente tiene una sola instancia activa,
pero posible en escenarios de reinicio con overlap.

**Solución — Optimistic locking con WATCH/MULTI/EXEC:**

```python
async def save_atomic(
    self,
    window: BudgetWindow,
    max_retries: int = 3
) -> bool:
    """
    Save con optimistic locking para prevenir race conditions.
    Usa WATCH/MULTI/EXEC de Redis (disponible en Redis 8.6.2).

    Para la mayoría de los casos (un agente = una instancia), save() simple
    es suficiente. Este método es para escenarios de alta concurrencia o
    durante ventanas de reinicio con overlap.
    """
    fragment_id = self._fragment_id(window.tenant_id, window.agent_id)

    for attempt in range(max_retries):
        try:
            async with self._redis.pipeline() as pipe:
                await pipe.watch(fragment_id)
                pipe.multi()
                pipe.set(fragment_id, window.model_dump_json())
                await pipe.execute()
                return True

        except WatchError:
            # Otro proceso modificó la clave entre WATCH y EXEC
            if attempt < max_retries - 1:
                await asyncio.sleep(0.01 * (2 ** attempt))  # backoff
                continue
            self._logger.error(
                "BudgetWindow save: concurrent write conflict after retries",
                tenant_id=window.tenant_id,
                agent_id=window.agent_id,
            )
            return False

        except Exception as e:
            self._logger.error("save_atomic unexpected error", error=str(e))
            return False

    return False
```

**Decisión de diseño:** para MPAT4 V4_01, usar `save()` simple (last-write-wins)
con logging de concurrencia como deuda técnica monitoreable. Escalar a
`save_atomic()` cuando se detecte contención en producción. Documentar como
INV-PERSIST-CONC-001.

### 8.2 Brecha — TTL no especificado

El diseño no menciona si las claves Redis tienen TTL (Time-To-Live).

**Análisis:**

Si `fragment_id` no tiene TTL:
- La clave vive indefinidamente en Redis
- Riesgo: acumulación de claves para agentes dados de baja sin limpieza explícita
- Beneficio: el budget sobrevive cualquier cantidad de reinicios

Si `fragment_id` tiene TTL:
- La clave expira después del período configurado
- Riesgo: si el agente tarda más que el TTL entre operaciones, pierde su estado
- Beneficio: limpieza automática de agentes inactivos

**Decisión para MPAT4:**

Para objetos de presupuesto (datos financieros críticos), **no usar TTL automático**.
El ciclo de vida de las claves debe ser controlado explícitamente:
- Creación: en el primer `save()`
- Actualización: en cada `save()` subsiguiente
- Eliminación: explícita al finalizar la sesión del agente o al dar de baja el agente

Si se requiere limpieza de agentes inactivos, implementar un proceso de limpieza
separado (background job) que revise el estado del agente antes de eliminar su budget.

**Nuevo INV:** ver sección 11.

---

## 9. IMPLEMENTACIÓN DE REFERENCIA COMPLETA

```python
"""
BudgetWindowPersistence — Implementación de referencia SOTA
Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
Versión: V4_01
Módulo: persistence/budget_window_persistence.py

Aplica resoluciones:
  - RESOLUCION_BUDGET_PERSISTENCE_SOTA_V1 (este documento)
  - INV-AESP-006: BudgetWindow frozen (inmutabilidad profunda)
  - INV-PERSIST-001 a 006 (preexistentes)
  - INV-PERSIST-LOAD-001, 002 (nuevos)
  - INV-PERSIST-SAVE-001 a 004 (nuevos)
  - INV-PERSIST-TTL-001 (nuevo)
  - INV-PERSIST-CONC-001 (nuevo)
  - INV-PERSIST-FRAG-001 (nuevo)
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationError

# ─── Modelo de dominio ────────────────────────────────────────────────────────

class BudgetWindow(BaseModel):
    """
    Ventana de presupuesto para un agente dentro de un tenant.

    INV-AESP-006: instancia inmutable por contrato (frozen=True).
    INV-AESP-006-DEEP: la inmutabilidad es profunda — todos los campos
                       usan tipos Python inmutables (no list, no set, no dict).

    Para modificar: usar model_copy(update={}) que retorna nueva instancia.
    """
    model_config = ConfigDict(frozen=True)

    tenant_id: str
    agent_id: str
    allocated: float       # Presupuesto total asignado
    consumed: float        # Presupuesto consumido hasta ahora
    # Colecciones: SIEMPRE tipos inmutables
    allowed_models: tuple[str, ...] = ()   # No list[str]
    tags: frozenset[str] = frozenset()     # No set[str]


# ─── Contrato del repositorio ─────────────────────────────────────────────────

class BudgetWindowRepository(ABC):
    """
    INV-PERSIST-ABC-001: cualquier implementación de persistencia para
    BudgetWindow debe cumplir estas firmas. Nunca acoplar código de
    dominio a una implementación concreta.
    """

    @abstractmethod
    async def save(self, window: BudgetWindow) -> bool:
        """Persiste. Retorna True=éxito, False=fallo. Nunca raise."""
        ...

    @abstractmethod
    async def load(
        self,
        tenant_id: str,
        agent_id: str
    ) -> Optional[BudgetWindow]:
        """Recupera o retorna None. Nunca raise."""
        ...


# ─── Implementación Redis (Memory Fabric) ────────────────────────────────────

class BudgetWindowPersistence(BudgetWindowRepository):
    """
    Repositorio de BudgetWindow sobre Redis (Memory Fabric de MPAT4).

    Decisiones de diseño aplicadas:
      - fragment_id determinista: aesp:budget:{tenant_id}:{agent_id}
      - save() es fail-soft: retorna bool, nunca raise, loggea con nivel ERROR
      - load() es fail-safe: retorna None ante cualquier error, nunca raise
      - Hidratación validada: BudgetWindow(**data), no model_construct
      - Sin TTL automático: ciclo de vida controlado explícitamente
      - Serialización: JSON-in-string (aceptable para objeto de esta escala)
    """

    _NAMESPACE = "aesp:budget"

    def __init__(self, redis_client, logger=None):
        """
        Args:
            redis_client: cliente Redis async (redis.asyncio.Redis o compatible)
            logger: logger estructurado opcional — si None se crea uno local
        """
        self._redis = redis_client
        self._logger = logger or logging.getLogger(__name__)

    # ─── INV-PERSIST-FRAG-001 ────────────────────────────────────────────────
    def _fragment_id(self, tenant_id: str, agent_id: str) -> str:
        """
        Genera el fragment_id determinista para el par (tenant_id, agent_id).

        INV-PERSIST-FRAG-001: el fragment_id es determinista. La misma
        combinación (tenant_id, agent_id) siempre produce el mismo ID.
        Esto hace save() idempotente: múltiples saves del mismo estado
        producen el mismo resultado en Redis (upsert).

        Formato: aesp:budget:{tenant_id}:{agent_id}
        """
        return f"{self._NAMESPACE}:{tenant_id}:{agent_id}"

    # ─── save() ──────────────────────────────────────────────────────────────
    async def save(self, window: BudgetWindow) -> bool:
        """
        INV-PERSIST-SAVE-001: save() es fail-soft — nunca raise.
        INV-PERSIST-SAVE-002: retorna True si persistió, False si falló.
        INV-PERSIST-SAVE-003: fallo se loggea como ERROR con contexto completo.
        INV-PERSIST-SAVE-004: BudgetWindow en memoria es la fuente de verdad
                              durante la sesión. La persistencia es best-effort.
        """
        try:
            fragment_id = self._fragment_id(window.tenant_id, window.agent_id)
            serialized = window.model_dump_json()
            await self._redis.set(fragment_id, serialized)
            return True

        except Exception as e:
            self._logger.error(
                "BudgetWindowPersistence.save failed",
                extra={
                    "tenant_id": window.tenant_id,
                    "agent_id": window.agent_id,
                    "allocated": window.allocated,
                    "consumed": window.consumed,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    # Loggear valores críticos para recuperación manual
                    # si Redis no se recupera en tiempo
                }
            )
            return False

    # ─── load() ──────────────────────────────────────────────────────────────
    async def load(
        self,
        tenant_id: str,
        agent_id: str
    ) -> Optional[BudgetWindow]:
        """
        INV-PERSIST-LOAD-001: load() es fail-safe — nunca raise.
        INV-PERSIST-LOAD-002: la hidratación es validada (BudgetWindow(**data)).
                              model_construct() está prohibido en este método.
        INV-PERSIST-LOAD-003: retorna None en cualquier condición de error.
                              El sistema debe poder arrancar sin estado persistido.
        """
        try:
            fragment_id = self._fragment_id(tenant_id, agent_id)
            raw = await self._redis.get(fragment_id)

            if raw is None:
                # Clave no existe: primer arranque o agente nuevo — normal
                return None

            data = json.loads(raw)

            # Hidratación validada: ejecuta todos los validadores Pydantic.
            # Si los datos están corruptos, ValidationError activa fail-safe.
            return BudgetWindow(**data)

        except json.JSONDecodeError as e:
            self._logger.error(
                "BudgetWindow deserialization failed — datos corruptos en Redis",
                extra={
                    "tenant_id": tenant_id,
                    "agent_id": agent_id,
                    "error": str(e),
                }
            )
            return None  # Activar fail-safe

        except ValidationError as e:
            self._logger.error(
                "BudgetWindow hydration failed — schema inválido en Redis",
                extra={
                    "tenant_id": tenant_id,
                    "agent_id": agent_id,
                    "validation_errors": e.errors(),
                }
            )
            return None  # Activar fail-safe

        except Exception as e:
            self._logger.error(
                "BudgetWindowPersistence.load unexpected error",
                extra={
                    "tenant_id": tenant_id,
                    "agent_id": agent_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )
            return None  # Fail-safe general

    # ─── delete() ─────────────────────────────────────────────────────────────
    async def delete(self, tenant_id: str, agent_id: str) -> bool:
        """
        Elimina el estado persistido de un agente.
        Llamar al dar de baja el agente o al finalizar su sesión formalmente.

        INV-PERSIST-TTL-001: las claves de BudgetWindow no tienen TTL automático.
                             El ciclo de vida es controlado explícitamente por
                             este método. No hay expiración silenciosa.
        """
        try:
            fragment_id = self._fragment_id(tenant_id, agent_id)
            await self._redis.delete(fragment_id)
            return True
        except Exception as e:
            self._logger.error(
                "BudgetWindowPersistence.delete failed",
                extra={
                    "tenant_id": tenant_id,
                    "agent_id": agent_id,
                    "error": str(e),
                }
            )
            return False
```

---

## 10. MATRIZ DE TESTS AMPLIADA (15 → 22)

### Tests preexistentes (mantenidos)

| ID | Nombre | Tipo | Estado |
|----|--------|------|--------|
| INV-PERSIST-001 | save retorna True con Redis OK | Invariante | Mantener |
| INV-PERSIST-002 | load retorna instancia correcta | Invariante | Mantener |
| INV-PERSIST-003 | fragment_id es determinista | Invariante | Mantener |
| INV-PERSIST-004 | load retorna None si clave no existe | Invariante | Mantener |
| INV-PERSIST-005 | BudgetWindow no es mutada por save | Invariante | Mantener |
| INV-PERSIST-006 | BudgetWindow no es mutada por load | Invariante | Mantener |
| ROUNDTRIP-001 | save → load recupera estado idéntico | Integration | Mantener |
| RESTART-001 | save → load tras reinicio de proceso | End-to-end | Mantener |
| FAILSAFE-LOAD-001 | load con Redis caído retorna None | Error path | Mantener |
| FAILSAFE-LOAD-002 | load con datos corruptos retorna None | Error path | Mantener |
| FAILSAFE-LOAD-003 | load con ValidationError retorna None | Error path | Mantener |
| ... | (4 tests adicionales del diseño original) | | |

### Tests nuevos — resoluciones de este documento

| ID | Nombre | Tipo | Brecha que cubre |
|----|--------|------|-----------------|
| INV-PERSIST-SAVE-001 | save retorna False con Redis caído | Error path | D5 — save() fail-soft |
| INV-PERSIST-SAVE-002 | save loggea ERROR con contexto completo | Observabilidad | D5 — logging |
| INV-PERSIST-SAVE-003 | save es idempotente (múltiples saves del mismo estado) | Idempotencia | D4 |
| INV-PERSIST-DEEP-001 | campos tuple de BudgetWindow no son mutables | Inmutabilidad | D1 — deep immutability |
| INV-PERSIST-DEEP-002 | campos frozenset de BudgetWindow no son mutables | Inmutabilidad | D1 — deep immutability |
| INV-PERSIST-HYDRATE-001 | load usa BudgetWindow(**data), no model_construct | Hidratación | D3 |
| INV-PERSIST-TTL-001 | claves en Redis no tienen TTL por defecto | Ciclo de vida | brecha TTL |

### Código de tests nuevos (ejemplos)

```python
# Test INV-PERSIST-SAVE-001
@pytest.mark.asyncio
async def test_save_returns_false_when_redis_is_down(redis_mock):
    redis_mock.set.side_effect = ConnectionError("Redis unavailable")
    persistence = BudgetWindowPersistence(redis_mock)
    window = BudgetWindow(
        tenant_id="t1", agent_id="a1",
        allocated=1000.0, consumed=250.0
    )
    result = await persistence.save(window)
    assert result is False  # Fail-soft: no raise, retorna False

# Test INV-PERSIST-DEEP-001
def test_budget_window_tuple_fields_are_truly_immutable():
    window = BudgetWindow(
        tenant_id="t1", agent_id="a1",
        allocated=1000.0, consumed=0.0,
        allowed_models=("gpt-4o", "claude-sonnet")
    )
    # Intentar mutar el contenido del tuple debe fallar
    with pytest.raises((TypeError, AttributeError)):
        window.allowed_models[0] = "gpt-3.5"  # tuple no soporta asignación

# Test INV-PERSIST-SAVE-003 (idempotencia)
@pytest.mark.asyncio
async def test_save_is_idempotent(redis_client):
    persistence = BudgetWindowPersistence(redis_client)
    window = BudgetWindow(
        tenant_id="t1", agent_id="a1",
        allocated=1000.0, consumed=300.0
    )
    # Múltiples saves del mismo estado
    await persistence.save(window)
    await persistence.save(window)
    await persistence.save(window)
    # El estado en Redis es el mismo que el del objeto
    loaded = await persistence.load("t1", "a1")
    assert loaded.consumed == 300.0
    assert loaded.allocated == 1000.0

# Test INV-PERSIST-TTL-001
@pytest.mark.asyncio
async def test_saved_keys_have_no_ttl(redis_client):
    persistence = BudgetWindowPersistence(redis_client)
    window = BudgetWindow(
        tenant_id="t1", agent_id="a1",
        allocated=500.0, consumed=100.0
    )
    await persistence.save(window)
    fragment_id = persistence._fragment_id("t1", "a1")
    ttl = await redis_client.ttl(fragment_id)
    # -1 significa sin TTL; -2 significa clave inexistente
    assert ttl == -1, f"Expected no TTL, got {ttl}"
```

---

## 11. NUEVOS INVARIANTES PROPUESTOS

| INV ID | Descripción | Módulo | Severidad |
|--------|-------------|--------|-----------|
| INV-AESP-006-DEEP | La inmutabilidad de BudgetWindow es profunda: todos los campos usan tipos Python inmutables. Ningún campo puede ser list, set o dict. | aesp | ALTA |
| INV-PERSIST-ABC-001 | Toda implementación de persistencia para BudgetWindow implementa BudgetWindowRepository (ABC). El código de dominio nunca depende de la implementación concreta. | persistence | MEDIA |
| INV-PERSIST-FRAG-001 | El fragment_id es determinista: f"aesp:budget:{tenant_id}:{agent_id}". Esta fórmula es inmutable — no cambia entre versiones del sistema sin migración explícita. | persistence | ALTA |
| INV-PERSIST-LOAD-001 | load() nunca raise. Ante cualquier excepción retorna None. | persistence | ALTA |
| INV-PERSIST-LOAD-002 | load() usa BudgetWindow(**data) para hidratación. model_construct() está prohibido en este método. | persistence | ALTA |
| INV-PERSIST-SAVE-001 | save() nunca raise. Es fail-soft. Retorna bool. | persistence | ALTA |
| INV-PERSIST-SAVE-002 | save() retorna True si persistió exitosamente, False si falló. | persistence | ALTA |
| INV-PERSIST-SAVE-003 | fallo de save() se loggea como ERROR con tenant_id, agent_id, allocated, consumed, error type. | persistence | MEDIA |
| INV-PERSIST-SAVE-004 | El objeto BudgetWindow en memoria del agente es la fuente de verdad durante la sesión. La persistencia es best-effort, no bloqueante. | persistence | ALTA |
| INV-PERSIST-TTL-001 | Las claves Redis de BudgetWindow no tienen TTL automático. El ciclo de vida es controlado explícitamente (delete() al dar de baja el agente). | persistence | MEDIA |
| INV-PERSIST-CONC-001 | El comportamiento ante escrituras concurrentes es last-write-wins. Para escenarios de alta concurrencia, usar save_atomic() con WATCH/MULTI/EXEC. Este INV debe revisarse si se detecta contención en producción. | persistence | BAJA (monitorear) |

---

## 12. RESOLUCIONES FORMALES

### RESOLUCION-PERSIST-001

**Asunto:** inmutabilidad superficial en BudgetWindow  
**Estado:** RESUELTO  
**Decisión:** auditar todos los campos de BudgetWindow y migrar `list` → `tuple`,
`set` → `frozenset`. Documentar en INV-AESP-006-DEEP.  
**Responsable:** desarrollador que modifique BudgetWindow en el siguiente ciclo  
**Validación:** test INV-PERSIST-DEEP-001 y INV-PERSIST-DEEP-002 deben pasar

---

### RESOLUCION-PERSIST-002

**Asunto:** ausencia de ABC para repositorio  
**Estado:** RESUELTO con prioridad BAJA  
**Decisión:** crear `BudgetWindowRepository` ABC en `schemas/`. No bloqueante para V4_01.  
**Responsable:** implementar en el primer ciclo disponible con tiempo

---

### RESOLUCION-PERSIST-003

**Asunto:** variante de hidratación no especificada  
**Estado:** RESUELTO  
**Decisión:** hidratación validada obligatoria (`BudgetWindow(**data)`).
Documentado en INV-PERSIST-LOAD-002.  
**Validación:** test INV-PERSIST-HYDRATE-001

---

### RESOLUCION-PERSIST-004

**Asunto:** fragment_id sin INV formal  
**Estado:** RESUELTO  
**Decisión:** elevar el esquema de fragment_id a INV-PERSIST-FRAG-001.
Cualquier cambio en el esquema requiere migración explícita de claves en Redis.

---

### RESOLUCION-PERSIST-005

**Asunto:** `save()` sin comportamiento fail-soft documentado  
**Estado:** RESUELTO  
**Decisión:** implementar save() con retorno bool y logging estructurado.
INV-PERSIST-SAVE-001 a 004 documentan el contrato completo.  
**Validación:** tests INV-PERSIST-SAVE-001, INV-PERSIST-SAVE-002

---

### RESOLUCION-PERSIST-006

**Asunto:** TTL no especificado para claves Redis  
**Estado:** RESUELTO  
**Decisión:** sin TTL automático. Ciclo de vida controlado por delete() explícito.
Documentado en INV-PERSIST-TTL-001.  
**Validación:** test INV-PERSIST-TTL-001

---

### RESOLUCION-PERSIST-007

**Asunto:** concurrencia en save() — comportamiento no especificado  
**Estado:** RESUELTO PARCIALMENTE — PENDIENTE_INV para monitoreo  
**Decisión provisional:** last-write-wins es aceptable si cada agente tiene
una sola instancia activa. Implementar save_atomic() como método alternativo.
Documentar en INV-PERSIST-CONC-001.  
**Revisión:** obligatoria si se detecta contención en producción

---

## 13. DEUDA TÉCNICA RESIDUAL

| ID | Descripción | Prioridad | Condición de revisión |
|----|-------------|-----------|----------------------|
| DT-PERSIST-001 | Circuit breaker para Redis no implementado | MEDIA | Implementar si Redis muestra inestabilidad en producción |
| DT-PERSIST-002 | save_atomic() con WATCH/MULTI/EXEC no activado por defecto | BAJA | Activar si se detecta contención concurrente |
| DT-PERSIST-003 | JSON-in-string vs RedisJSON no evaluado en producción | BAJA | Evaluar si BudgetWindow crece o se necesita acceso parcial |
| DT-PERSIST-004 | Proceso de limpieza de claves huérfanas no implementado | MEDIA | Implementar cuando la plataforma tenga ciclo de baja de agentes definido |
| DT-PERSIST-005 | Tests de carga (tamaño máximo de BudgetWindow) ausentes | BAJA | Agregar cuando el schema de BudgetWindow esté estabilizado |

---

## 14. CONCLUSIÓN Y VEREDICTO SOTA

### Veredicto general

El diseño de `BudgetWindowPersistence` está **mayoritariamente alineado con el SOTA**
de mayo 2026. Las decisiones estructurales son sólidas:

- El patrón repositorio externo es correcto y está en la dirección del ecosistema pydantic-ai
- El fragment_id determinista es SOTA para idempotencia en sistemas distribuidos
- El fail-safe en load() es el patrón que AI Gateways de producción usan

Las brechas identificadas no invalidan el diseño — lo completan:

1. La inmutabilidad profunda es un detalle de implementación que el diseño no especificaba
2. El fail-soft en save() era una omisión de documentación, no de implementación
3. El TTL y la concurrencia son decisiones de diseño que ahora están formalizadas

### Lo que este análisis agrega

Antes de este análisis: 15 tests, 6 INV, comportamiento de save() no documentado.

Después de este análisis: 22 tests, 17 INV (6 preexistentes + 11 nuevos),
comportamiento completo documentado incluyendo concurrencia, TTL, hidratación,
fail-soft en save(), y la trampa de inmutabilidad superficial de Pydantic.

### Recomendación final

Implementar en orden de prioridad:

1. Inmutabilidad profunda en BudgetWindow (todos los campos con tipos inmutables)
2. save() con retorno bool y logging estructurado
3. Tests INV-PERSIST-SAVE-001 a 003 y INV-PERSIST-DEEP-001 a 002
4. delete() para ciclo de vida explícito de claves
5. ABC base para repositorio (mejora futura, no urgente)

El diseño puede ir a producción una vez resueltos los puntos 1 y 2.

---

*RESOLUCION_BUDGET_PERSISTENCE_SOTA_V1.md*
*Generado: 2026-05-27 · Módulo: persistence · Sistema: MPAT4*
*que has usado el formato de razonamiento adaptado por AGT*
