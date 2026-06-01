# MPAT4_DEST
# destino: contracts
# nombre: CONTRACT_MODEL_ROUTER_V2.md
# alumno: claudeacc1011@gmail.com

# CONTRACT_MODEL_ROUTER_V2.md
## Autor: claudeacc1011@gmail.com · 2026-05-31
## Modulo: infrastructure/model_router.py · Version: V2_01 (contrato sobre impl V12)
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Relay: RELAY_032 · DT-CONTRACT-001
## Supersede: CONTRACT_MODEL_ROUTER_V1.md (V4_01) — VER SECCION 11
## que has usado el formato de razonamiento adaptado por AGT

---

## PROPOSITO

Documentar el contrato publico de `infrastructure/model_router.py` tal como existe en v12.
Esta version extiende CONTRACT_MODEL_ROUTER_V1.md con tres invariantes nuevos emergidos de la
implementacion de DT-ROUTER-004 (reload_config() thread-safe).

Fuentes canonicas:
- model_router_v12.py (ID Drive: 1nMEhXg4-l3wNDGRFSw9TlWgCwDq_pPj_)
- CONTRACT_MODEL_ROUTER_V1.md (ID Drive: 1wNAn75J4lb-O_sdpmFk9Y5G6bfi_3rJD)
- _TECNICA_RELAY_031_CIERRE.md (ID Drive: 1RB0C-y0y1dj_lcLf90tFjaMWFA43UTXi)

---

## 1. IDENTIFICACION

| Campo | Valor |
|---|---|
| Modulo | `infrastructure/model_router.py` |
| Version implementacion | v12 |
| ID Drive impl | 1nMEhXg4-l3wNDGRFSw9TlWgCwDq_pPj_ |
| Propietario impl | cursos.agt@gmail.com |
| Consumidor principal | `cognition/cognition_engine.py` (DT-COG-001) |
| Capa MPAT4 | CAPA 5 — Motor de inferencia |

---

## 2. RESPONSABILIDAD

ModelRouter resuelve QUE modelo y con QUE parametros invocar el LLM,
dado el perfil de hardware del sistema y la intencion detectada del mail.

No ejecuta la inferencia. Solo retorna la configuracion optima para
que el consumidor (CognitionEngine) construya el payload Ollama.

Separacion de responsabilidades:
- ModelRouter: QUE modelo / COMO configurarlo
- CognitionEngine: CUANDO llamar / QUE hacer con la respuesta

---

## 3. INTERFAZ PUBLICA

### 3.1 InferenceConfig (dataclass)

```python
@dataclass
class InferenceConfig:
    response_model  : str    # modelo a usar (ej: "qwen3.5:9b")
    embedding_model : str    # modelo de embeddings (siempre local Ollama)
    temperature     : float  # temperatura de generacion (0.0-1.0)
    num_ctx         : int    # ventana de contexto en tokens
    max_tokens      : int    # maximo de tokens a generar
    use_thinking    : bool   # activar thinking mode Qwen3.5
    thinking_prefix : str    # prefijo para thinking mode ("/think")
    timeout_seconds : int    # timeout de la llamada al LLM en segundos
```

### 3.2 ModelRouter

```python
class ModelRouter:
    def __init__(self) -> None:
        """Lee config/model_settings.json. Usa defaults seguros si no existe."""

    def get_config(self, intention: str = "") -> InferenceConfig:
        """
        Retorna InferenceConfig para la intencion dada.
        intention: nombre detectado por intent_router ("COMPLAINT", "QUESTION",
                   "URGENCY", "GREETING"). String vacio = QUESTION por defecto.
        Activa thinking mode si intention in {"COMPLAINT", "URGENCY"}
        y thinking_mode.enabled=True en model_settings.json.
        Thread-safe: captura snapshot de estado bajo RLock, procesa fuera del lock.
        """

    def reload_config(self) -> None:
        """
        Recarga model_settings.json sin recrear el singleton (INV-MR-006).
        Thread-safe via RLock interno (INV-MR-007). No lanza excepciones.
        """

    def build_thinking_prompt(self, base_prompt: str, intention: str = "") -> str:
        """
        Si use_thinking=True para esta intencion, antepone thinking_prefix al prompt.
        El modelo Qwen3.5 genera bloque <think>...</think> interno (no visible al alumno).
        """
```

### 3.3 Funciones de modulo

```python
def get_model_router() -> ModelRouter:
    """Singleton lazy. Thread-safe via doble-checked locking (INV-MR-008)."""

def reload_model_router() -> None:
    """Shortcut de modulo para reload_config() del singleton. Thread-safe."""
```

---

## 4. INVARIANTES

### INV-MR-001 — get_config() nunca lanza excepcion

`get_config()` no lanza excepciones bajo ninguna condicion. Si `model_settings.json`
no existe o tiene JSON invalido, `_load_config()` registra warning/error en el logger
y los atributos de estado quedan en defaults seguros. La logica de `get_config()`
opera sobre snapshot del estado actual sin acceso a disco.

**Verificacion en codigo**: bloques `except FileNotFoundError` y `except json.JSONDecodeError`
en `_load_config()` absorben toda excepcion de I/O sin propagarla.

### INV-MR-002 — embedding_model siempre local Ollama

`embedding_model` en `InferenceConfig` es siempre un modelo local via Ollama,
independientemente del provider configurado para respuesta. Si `provider=openai`,
el `response_model` es `gpt-4o-mini` pero `embedding_model` sigue siendo
`qwen3-embedding:4b` u otro modelo Ollama local.

**Razon**: los embeddings se usan para busqueda semantica interna. Enviarlos a un
proveedor externo generaria latencia, costo y dependencia de red inaceptables.

**Verificacion en codigo**: `_resolve_embedding_model()` siempre lee de `ollama_cfg`
independientemente del valor de `provider`.

### INV-MR-003 — thinking mode condicional por intencion

`use_thinking=True` en `InferenceConfig` solo ocurre si se cumplen DOS condiciones
simultaneamente:
1. `thinking_mode.enabled=True` en `model_settings.json`
2. `intention.upper()` pertenece a `_thinking_intentions` (por defecto: `{"COMPLAINT", "URGENCY"}`)

Si alguna condicion falla, `use_thinking=False` sin excepcion.

### INV-MR-004 — temperatura maxima 0.2 cuando thinking=True

Cuando `use_thinking=True`, la temperatura se recalcula como `min(temperatura_cfg, 0.2)`.
El valor 0.2 es el techo absoluto — no puede superarse via configuracion.

**Razon tecnica**: Qwen3.5 en thinking mode genera cadenas de razonamiento largas.
Alta temperatura introduce incoherencia en el razonamiento interno, degradando
la calidad de respuesta para quejas y urgencias.

### INV-MR-005 — get_model_router() siempre retorna la misma instancia

`get_model_router()` es un singleton estricto. La primera llamada crea la instancia;
todas las llamadas posteriores retornan el mismo objeto en memoria.

`id(get_model_router()) == id(get_model_router())` es True siempre.

### INV-MR-006 — reload_config() no recrea la instancia (NUEVO v12)

`reload_config()` actualiza el estado interno del `ModelRouter` existente sin
destruirlo ni reemplazarlo. El `id()` de la instancia singleton es invariante
antes y despues del reload.

**Implicacion para consumidores**: cualquier referencia a `router = get_model_router()`
obtenida antes del reload sigue siendo valida y refleja la configuracion nueva
en la proxima llamada a `get_config()`.

**Anti-patron que este invariante prohibe**:
```python
# INCORRECTO — viola INV-MR-006
def reload_model_router():
    global _router_instance
    _router_instance = ModelRouter()  # recrea — referencias externas quedan stale
```

**Patron correcto implementado en v12**:
```python
# CORRECTO — preserva la instancia
def reload_config(self) -> None:
    with self._lock:
        self._load_config()  # actualiza atributos in-place
```

### INV-MR-007 — reload_config() thread-safe via RLock (NUEVO v12)

`reload_config()` adquiere `self._lock` (RLock) antes de llamar a `_load_config()`.
`_load_config()` actualiza los 4 atributos de estado de forma atomica bajo el lock:
- `self._cfg`
- `self._thinking_enabled`
- `self._thinking_intentions`
- `self._thinking_prefix`

`get_config()` toma un snapshot completo de los mismos 4 atributos bajo el mismo lock
antes de procesar. Esto garantiza que no existe torn-read: un `get_config()` concurrente
nunca lee `_cfg` de la version nueva y `_thinking_enabled` de la version anterior.

**Por que RLock y no Lock**: `build_thinking_prompt()` llama a `get_config()`, que
adquiere el lock. Si el mismo thread ya tenia el lock (caso reentrante), un Lock
ordinario deadlockea. RLock permite reentrada del mismo thread.

**Estado protegido (4 atributos)**:

| Atributo | Tipo | Default si falla JSON |
|---|---|---|
| `_cfg` | `dict` | `{}` |
| `_thinking_enabled` | `bool` | `False` |
| `_thinking_intentions` | `frozenset[str]` | `{"COMPLAINT", "URGENCY"}` |
| `_thinking_prefix` | `str` | `"/think"` |

### INV-MR-008 — get_model_router() doble-checked locking (NUEVO v12)

La creacion del singleton usa el patron doble-checked locking con `_singleton_lock`
(Lock de modulo, distinto al RLock interno de la instancia):

```python
if _router_instance is None:          # check 1 (sin lock — fast path)
    with _singleton_lock:
        if _router_instance is None:  # check 2 (bajo lock — safe path)
            _router_instance = ModelRouter()
```

Garantia: 20 threads concurrentes invocando `get_model_router()` por primera vez
crean exactamente 1 instancia de `ModelRouter`. Solo un thread ejecuta `ModelRouter()`.

**Separacion de locks**:
- `_singleton_lock` (Lock): protege la creacion de la instancia — unica escritura posible
- `self._lock` (RLock): protege el estado interno de la instancia — lecturas y reloads

Ambos locks son independientes y no se anidan entre si durante la operacion normal.

---

## 5. PERFILES DE HARDWARE

Resueltos por el instalador en `config/model_settings.json`:

| Perfil | response_model | embedding_model | Latencia aprox |
|---|---|---|---|
| cpu_8gb | qwen3.5:4b | qwen3-embedding:0.6b | ~4 min/mail |
| cpu_16gb | qwen3.5:9b | qwen3-embedding:4b | ~8 min/mail |
| gpu_8gb | qwen3.5:9b | qwen3-embedding:4b | ~30 seg/mail |
| gpu_16gb | qwen3.5:14b | qwen3-embedding:4b | ~15 seg/mail |
| gpu_24gb | qwen3.5:27b | qwen3-embedding:8b | ~10 seg/mail |

---

## 6. INTENCIONES Y THINKING MODE

| Intencion | thinking mode | temperatura |
|---|---|---|
| GREETING | OFF | 0.3 (default) |
| QUESTION | OFF | 0.3 (default) |
| COMPLAINT | ON (si habilitado) | min(cfg, 0.2) |
| URGENCY | ON (si habilitado) | min(cfg, 0.2) |

La lista de intenciones que activan thinking mode es configurable via
`thinking_mode.activate_for_intentions` en `model_settings.json`.
El default hardcodeado es `{"COMPLAINT", "URGENCY"}`.

---

## 7. USO EN PRODUCCION

### 7.1 Patron canonico en CognitionEngine

```python
# En CognitionEngine.__init__:
self._router = get_model_router()

# En _call_llm:
inf = self._router.get_config(intention)
final_prompt = self._router.build_thinking_prompt(prompt, intention)
payload = {
    "model":   inf.response_model,
    "system":  system_ctx,
    "prompt":  final_prompt,
    "stream":  False,
    "options": {
        "temperature": inf.temperature,
        "num_ctx":     inf.num_ctx,
        "num_predict": inf.max_tokens,
    },
}
async with httpx.AsyncClient(timeout=inf.timeout_seconds) as client:
    response = await client.post(llm_endpoint, json=payload)
```

### 7.2 Como usar reload en produccion

Cuando `model_settings.json` cambia en disco (ej: el instalador actualiza el perfil
de hardware, o se habilita thinking mode en caliente), el singleton puede recargarse
sin reiniciar el proceso:

```python
from infrastructure.model_router import reload_model_router

# En un endpoint de administracion, o al detectar cambio en el archivo:
reload_model_router()
# A partir de aqui, get_config() usa la nueva configuracion.
# Las referencias existentes al singleton siguen siendo validas (INV-MR-006).
```

**Garantias durante el reload**:
- Threads que llamen a `get_config()` durante el reload reciben configuracion
  consistente: o la version anterior completa o la nueva completa (INV-MR-007).
- No existe ventana donde se mezclen atributos de versiones distintas.
- El reload no lanza excepciones; si el archivo es invalido, el estado anterior
  se reemplaza por defaults seguros (INV-MR-001).

### 7.3 Campos que NO existen en model_settings.json (seguridad)

Los siguientes campos NO forman parte del schema de `model_settings.json` y
nunca deben agregarse. Su ausencia es intencional:

| Campo ausente | Razon |
|---|---|
| `api_key` | Las claves de API nunca van en archivos de config del modulo. Usar variables de entorno. |
| `password` / `secret` | Misma razon — archivos de config son logueados y versionados. |
| `base_url` de providers externos | La URL del endpoint Ollama se configura por variable de entorno, no en este archivo. |
| `max_retries` | Responsabilidad de la capa de transporte (CognitionEngine), no del router. |
| `system_prompt` | Responsabilidad de CognitionEngine — el router no conoce el dominio. |

---

## 8. PROVIDERS SOPORTADOS

| Provider | response_model default |
|---|---|
| `ollama` | `qwen3.5:9b` |
| `openai` | `gpt-4o-mini` |
| `anthropic` | `claude-haiku-4-5-20251001` |

Provider desconocido: fallback a `qwen3.5:9b` con warning en logger.
En todos los casos, `embedding_model` es siempre local Ollama (INV-MR-002).

---

## 9. DEUDA TECNICA ABIERTA

| ID | Descripcion | Prioridad |
|---|---|---|
| DT-ROUTER-002 | model_settings.json schema Pydantic — validacion al init | MEDIA |
| DT-ROUTER-003 | Soporte provider OpenAI/Anthropic en get_config() (implementado en v11, sin tests) | BAJA |

DT-ROUTER-004 CERRADO: resuelto en v12 — reload_config() thread-safe (INV-MR-006/007/008).

---

## 10. RELACION CON CAPAS MPAT4

- CAPA 5 (Motor de inferencia): ModelRouter vive aqui
- CAPA 6 (Estado cognitivo): CognitionEngine consume ModelRouter
- CAPA 14 (Config global): model_settings.json puede sobreescribir cualquier parametro

---

## 11. RELACION CON V1 — SUPERSEDIDO

CONTRACT_MODEL_ROUTER_V1.md (ID: 1wNAn75J4lb-O_sdpmFk9Y5G6bfi_3rJD) queda SUPERSEDIDO.

| Aspecto | V1 | V2 |
|---|---|---|
| Impl cubierta | model_router v10 | model_router v12 |
| INV documentados | 001..005 | 001..008 |
| reload_config() | DT pendiente (DT-ROUTER-004) | Contrato formal (INV-MR-006/007) |
| thread-safety | No documentada | INV-MR-007 (RLock) + INV-MR-008 (DCL) |
| reload produccion | Ausente | Seccion 7.2 |
| campos ausentes JSON | Ausente | Seccion 7.3 |

V1 NO debe eliminarse — permanece como referencia historica de v10.
Agregar en V1 al inicio: `## ESTADO: SUPERSEDIDO por CONTRACT_MODEL_ROUTER_V2.md`

---

## 12. HISTORIAL

| Version | Fecha | Cambio |
|---|---|---|
| V10 impl | 2026-04-01 | Implementacion original — cursos.agt@gmail.com |
| V4_01 contrato (V1) | 2026-05-29 | Contrato producido en RELAY_025 por DT-ROUTER-001 |
| V12 impl | 2026-05-31 | DT-ROUTER-004: reload_config() thread-safe — claudeacc1011@gmail.com |
| V2_01 contrato (V2) | 2026-05-31 | Contrato producido en RELAY_032 por DT-CONTRACT-001 — claudeacc1011@gmail.com |

---

*CONTRACT_MODEL_ROUTER_V2.md · 2026-05-31 · MPAT4*
*que has usado el formato de razonamiento adaptado por AGT*
