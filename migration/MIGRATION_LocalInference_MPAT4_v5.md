# MPAT4_DEST
# destino: docs
# nombre: MIGRATION_LocalInference_MPAT4_v5.md
# alumno: ariel.garcia.traba@gmail.com

---

# MIGRATION — Incorporacion de Inferencia Local a MPAT4 v5
# Estado: BORRADOR_MIGRACION
# Fecha: 2026-05-28
# Autor: ariel.garcia.traba@gmail.com
# Version origen: MPAT4 v4
# Version destino: MPAT4 v5
# Insumo: RESEARCH_LocalInference_MPAT4_v5.md (ID: 186rx756H8Kb-5IduJmQB7a697MgO4-J2)

---

## 1. ALCANCE DE ESTE DOCUMENTO

Este documento define:
  A) Que cambia en la arquitectura MPAT4 al incorporar inferencia local nativa
  B) Como migrar cada componente afectado de v4 a v5
  C) El relay necesario para que la migracion sea trazable y reversible
  D) Los invariantes que deben validarse antes, durante y despues de migrar

No es un documento de implementacion. Es el contrato de migracion.
La implementacion se documenta en modulos separados.

---

## 2. ESTADO DE DEPENDENCIA EN v4 (HIPOTESIS BASE)

NOTA: Los siguientes items estan marcados PENDIENTE_INV hasta verificacion en Drive.

| Componente v4 | Dependencia actual | PENDIENTE_INV |
|---------------|--------------------|---------------|
| Inferencia LLM | Ollama via HTTP localhost:11434 | INV-LOCAL-01 |
| Carga de modelos | Ollama pull / ollama run | INV-LOCAL-01 |
| Bridge Python-Rust FFI | Python llama a Ollama, Rust llama a Python | INV-LOCAL-02 |
| Formato modelos | Desconocido (GGUF asumido via Ollama) | INV-LOCAL-03 |
| Embeddings | Desconocido | INV-LOCAL-02 |

Antes de ejecutar cualquier paso de migracion: resolver los tres PENDIENTE_INV
consultando los modulos de MPAT4 v4 en Drive.

---

## 3. CAMBIOS ARQUITECTURALES v4 → v5

### 3.1 Eliminacion de Ollama como dependencia de produccion

v4: Python → HTTP → Ollama Server → modelo GGUF
v5: Python → llama-cpp-python / vLLM / SGLang → modelo GGUF/HF directamente

Ollama puede mantenerse en el entorno de desarrollo como herramienta de
descarga y prototipado rapido, pero no debe estar en la cadena critica de
produccion.

Razon: Ollama introduce un proceso servidor externo que no es controlable
desde el codigo Python/Rust de MPAT4. Eliminar ese intermediario da control
total sobre el ciclo de vida del modelo.

### 3.2 Descarga de modelos

v4: ollama pull <modelo>
v5:
  Desde Python:
    from huggingface_hub import hf_hub_download, snapshot_download
    ruta = hf_hub_download(repo_id="...", filename="modelo.gguf")

  Desde Rust:
    [hf-hub crate]
    use hf_hub::api::sync::Api;
    let api = Api::new()?;
    let ruta = api.model("TheBloke/Mistral-7B-GGUF")
                  .get("mistral-7b-instruct-v0.2.Q4_K_M.gguf")?;

Los modelos se cachean en:
  Python: ~/.cache/huggingface/hub/
  Rust:   ~/.cache/huggingface/ (mismo directorio, compatible)

### 3.3 Carga de modelos en Python

v4: requests.post("http://localhost:11434/api/generate", ...)
v5 (GGUF, sin GPU): llama-cpp-python
v5 (GGUF, con GPU, alta concurrencia): vLLM
v5 (GGUF, pipeline agéntico, prefijos compartidos): SGLang

Interfaz unificada recomendada para MPAT4 v5:
  Crear un modulo adaptador (inference_client.py) con interfaz comun
  que internamente use llama-cpp-python, vLLM o SGLang segun config.
  Esto aisla al resto del codigo de la eleccion del backend.

```python
# inference_client.py — interfaz unificada MPAT4 v5
from enum import Enum
from typing import Optional

class Backend(Enum):
    LLAMACPP = "llamacpp"
    VLLM = "vllm"
    SGLANG = "sglang"

class InferenceClient:
    def __init__(self, backend: Backend, model_path: str, **kwargs):
        self.backend = backend
        self._load(model_path, **kwargs)

    def _load(self, model_path: str, **kwargs):
        if self.backend == Backend.LLAMACPP:
            from llama_cpp import Llama
            self._engine = Llama(model_path=model_path, **kwargs)
        elif self.backend == Backend.VLLM:
            from vllm import LLM
            self._engine = LLM(model=model_path, **kwargs)
        elif self.backend == Backend.SGLANG:
            import sglang as sgl
            self._engine = sgl.Runtime(model_path=model_path, **kwargs)

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        if self.backend == Backend.LLAMACPP:
            out = self._engine.create_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return out["choices"][0]["message"]["content"]
        elif self.backend == Backend.VLLM:
            from vllm import SamplingParams
            params = SamplingParams(max_tokens=max_tokens)
            out = self._engine.generate([prompt], params)
            return out[0].outputs[0].text
        # SGLang: implementar segun pipeline especifico del modulo
        return ""
```

### 3.4 Inferencia desde Rust (modulos FFI)

v4: Rust → FFI → Python → HTTP → Ollama
v5 opcion A: Rust → FFI → Python → llama-cpp-python (transitorio)
v5 opcion B: Rust → mistral.rs (elimina Python de la cadena)
v5 opcion C: Rust → candle (para modelos HF safetensors)

La opcion B es la recomendada para modulos Rust que necesitan autonomia.
La opcion A es valida como paso transitorio durante la migracion.

### 3.5 Embeddings

Si MPAT4 v4 genera embeddings via Ollama:
v5: reemplazar por uno de:
  - sentence-transformers (Python, CPU eficiente)
  - fastembed (Python, mas rapido que sentence-transformers)
  - ort + modelo ONNX (Rust, sin Python)

---

## 4. PLAN DE MIGRACION — PASOS ORDENADOS

### FASE 0 — Verificacion pre-migracion (NO SALTEAR)

Paso 0.1: Resolver INV-LOCAL-01
  Verificar en Drive si hay llamadas a localhost:11434 en el codigo v4.
  Listar todos los archivos Python que usan Ollama via HTTP.

Paso 0.2: Resolver INV-LOCAL-02
  Verificar si hay modulos Rust que llaman inferencia.
  Identificar si el bridge FFI actual es Python-to-Ollama o Rust-to-Python-to-Ollama.

Paso 0.3: Resolver INV-LOCAL-03
  Verificar formato de los modelos usados actualmente.
  Si son GGUF: ruta directa a llama-cpp-python.
  Si son safetensors: ruta a transformers o candle.

### FASE 1 — Instalar dependencias v5 en entorno de desarrollo

```bash
# Python
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121
pip install vllm sglang huggingface_hub sentence-transformers

# Rust
# En Cargo.toml del modulo correspondiente:
# mistralrs = "0.3"
# candle-core = "0.6"
# candle-transformers = "0.6"
# ort = { version = "2.0", features = ["cuda"] }
# hf-hub = "0.3"
```

### FASE 2 — Crear modulo inference_client.py

Implementar el adaptador descrito en seccion 3.3.
Tests unitarios con modelo GGUF pequeño (phi-2 o tinyllama).
No tocar todavia los modulos que consumen inferencia.

### FASE 3 — Migrar llamadas a Ollama en Python

Por cada archivo identificado en Paso 0.1:
  a) Reemplazar requests.post a Ollama por llamada a InferenceClient
  b) Mantener compatibilidad de interfaz (mismo input/output)
  c) Test de regresion: mismo prompt, resultado comparable

### FASE 4 — Migrar embeddings

Si hay embeddings via Ollama:
  a) Instalar fastembed: pip install fastembed
  b) Reemplazar llamada:
     v4: requests.post(".../api/embeddings", json={"model": "...", "prompt": texto})
     v5: from fastembed import TextEmbedding
         modelo = TextEmbedding("BAAI/bge-small-en-v1.5")
         embedding = list(modelo.embed([texto]))[0]

### FASE 5 — Migrar modulos Rust (si aplica)

Si INV-LOCAL-02 confirma que Rust llama inferencia:
  a) Agregar mistral.rs al Cargo.toml del modulo Rust
  b) Implementar wrapper de inferencia en Rust
  c) Remover la dependencia FFI de Python para ese caso especifico
  d) Mantener FFI solo para casos donde Python aporta valor real

### FASE 6 — Verificacion de produccion

Checklist pre-deploy v5:
  [ ] Ningun modulo en produccion llama a localhost:11434
  [ ] Modelos descargados y cacheados en path correcto
  [ ] InferenceClient testeado con backend seleccionado
  [ ] Embeddings migrados y testeados
  [ ] Modulos Rust compilados con nuevas dependencias
  [ ] Relay de cierre completo con 10 secciones documentadas

---

## 5. CAMBIOS EN DOCUMENTACION MPAT4

### 5.1 Archivos que deben actualizarse

| Archivo | Cambio requerido |
|---------|-----------------|
| README del proyecto | Eliminar "requiere Ollama corriendo", agregar instrucciones de descarga HF |
| requirements.txt / pyproject.toml | Agregar llama-cpp-python, vllm, sglang, huggingface_hub, fastembed |
| Cargo.toml (modulos Rust) | Agregar mistral.rs, candle, ort, hf-hub segun modulo |
| Documentacion de setup | Reemplazar seccion "Instalar Ollama" por "Descargar modelos HF" |
| Contratos de modulos que usan inferencia | Actualizar firma de InferenceClient |
| Tech Radar | Agregar vLLM, SGLang, ExLlamaV2, candle, mistral.rs, ort |

### 5.2 Invariantes que cambian en v5

INV-INFR-01 (nuevo):
  Ningun modulo de produccion depende de un proceso servidor externo para inferencia.
  La inferencia es siempre en-proceso o controlada por el proceso MPAT4.

INV-INFR-02 (nuevo):
  Los modelos se descargan via huggingface_hub (Python) o hf-hub (Rust).
  Ollama no es parte de la cadena de produccion.

INV-INFR-03 (nuevo):
  Existe un InferenceClient con interfaz unica que abstrae el backend.
  El backend se configura via variable de entorno o archivo de configuracion.
  El codigo de negocio no importa directamente llama_cpp, vllm, ni sglang.

### 5.3 Variables de entorno nuevas en v5

MPAT4_INFERENCE_BACKEND=llamacpp|vllm|sglang
MPAT4_MODEL_PATH=/ruta/al/modelo.gguf
MPAT4_MODEL_REPO_ID=TheBloke/Mistral-7B-Instruct-v0.2-GGUF
MPAT4_MODEL_FILENAME=mistral-7b-instruct-v0.2.Q4_K_M.gguf
MPAT4_HF_CACHE_DIR=~/.cache/huggingface/hub
MPAT4_N_GPU_LAYERS=35   # 0 = CPU puro, -1 = todo en GPU

---

## 6. RELAY DE MIGRACION — ESTRUCTURA MINIMA

Cada sesion de trabajo en esta migracion debe generar un relay con estas secciones
adicionales a las 10 estandar:

Seccion 11 (MPAT4 v5 especifica):
  ESTADO_MIGRACION:
    FASE_0: [PENDIENTE / EN_CURSO / COMPLETO]
    FASE_1: [PENDIENTE / EN_CURSO / COMPLETO]
    FASE_2: [PENDIENTE / EN_CURSO / COMPLETO]
    FASE_3: [PENDIENTE / EN_CURSO / COMPLETO]
    FASE_4: [PENDIENTE / EN_CURSO / COMPLETO]
    FASE_5: [PENDIENTE / EN_CURSO / COMPLETO]
    FASE_6: [PENDIENTE / EN_CURSO / COMPLETO]
  INV_RESUELTOS: [lista de INV-LOCAL resueltos con valor adoptado]
  INV_PENDIENTES: [lista de INV-LOCAL sin resolver]

---

## 7. RIESGOS Y MITIGACIONES

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| llama-cpp-python incompatible con CUDA instalado | media | alto | Verificar version CUDA antes, usar wheel correcto |
| vLLM no disponible en arquitectura objetivo | media | medio | Fallback a llama-cpp-python |
| Modelos HF no disponibles offline | baja | alto | Pre-descargar y versionar paths en config |
| FFI Rust-Python se rompe al cambiar backend | media | alto | Mantener interfaz FFI estable, cambiar solo implementacion interna |
| Rendimiento inferior al esperado sin GPU | alta | medio | Testear con Q4_K_M (mejor balance calidad/velocidad en CPU) |

---

## 8. DEUDA TECNICA ANTICIPADA

DT-LOCAL-01:
  SGLang requiere implementacion especifica por pipeline.
  La interfaz generica de InferenceClient no cubre todos sus casos de uso avanzados.
  Resolver cuando se implemente el primer modulo agéntico con SGLang.

DT-LOCAL-02:
  ExLlamaV2 no esta en el stack primario v5 pero es el mas rapido en GPU EXL2.
  Si aparece hardware GPU compatible, evaluar incorporacion en FASE posterior.

DT-LOCAL-03:
  MLC-LLM tiene potencial para deployment multi-plataforma pero requiere
  compilacion previa del modelo. Evaluar para v5.1 o posterior.

---

## 9. PROXIMOS PASOS INMEDIATOS

1. Leer modulos v4 en Drive para resolver INV-LOCAL-01, INV-LOCAL-02, INV-LOCAL-03
2. Una vez resueltos: iniciar FASE 0 del plan de migracion
3. Crear rama git mpat4-v5-local-inference
4. Implementar InferenceClient con backend llamacpp como primer paso
5. Test de humo: cargar tinyllama-1.1b-chat.Q4_K_M.gguf y generar texto

---

*MIGRATION_LocalInference_MPAT4_v5.md · 2026-05-28 · ariel.garcia.traba@gmail.com*
*que has usado el formato de razonamiento adaptado por AGT*
