---
tipo: investigacion_preliminar
migrado_desde: MPAT3/arquitectura/Arquitectura_Capa5.md + Arquitectura de Capa 5.gdoc.md
             + Arquitectura de Capa 5_1.md (unificados — contenido complementario)
autor_original: ariel.garcia.traba@gmail.com + cursos.agt.ia@gmail.com
fecha_original: 2026-05-10 a 2026-05-22
autor_archivo: ai.mpat.tech@gmail.com
fecha_migracion: 2026-05-24
lote: LOTE_003 (cierre)
estado: REFERENCIA_HISTORICA
adoptado_en: CAPA_05_MASTER_V4_00.md (LOTE_002) — 19 optimizaciones activas incorporadas
nota: tres archivos (Capa5.md, Capa5.gdoc.md, Capa5_1.md) unificados en este archivo.
      Los primeros dos eran idénticos (3.5KB c/u). El tercero (9.4KB) era análisis más completo.
      El canónico real es INFORME_CAPA_05_V3_01_.md (25.7KB) — ya migrado en LOTE_002.
---

# Arquitectura_Capa5 (Motor de Inferencia + Embeddings) — Investigación Preliminar Unificada
## MPAT4 docs/research · Archivado desde MPAT3/arquitectura/
## Fuentes unificadas: Arquitectura_Capa5.md + Arquitectura_Capa5.gdoc.md + Arquitectura_Capa5_1.md
## Adoptado en: CAPA_05_MASTER_V4_00.md

*que has usado el formato de razonamiento adaptado por AGT*

---

## FUENTE A — Pipeline de Embeddings y Memoria Semántica (Mayo 2026)

### 1. Estado del Arte en Modelos de Embedding (MTEB Mayo 2026)

| Rank | Modelo | Proveedor | Ventaja 2026 |
|:---|:---|:---|:---|
| 1 | Qwen3-Embedding-8B | Alibaba | #1 en MTEB Multilingual (Score 70.6). Apache 2.0. |
| 2 | Gemini Embedding 2 | Google | Nativamente multimodal (PDF, Audio, Video, Imagen). |
| 3 | Voyage-3.5-Large | Voyage AI | Especializado en código y documentos legales. Ventana 32K. |
| 4 | nomic-embed-text-v2 | Nomic AI | Ultra-ligero (137M params). Ideal para CPUs de 2012. |

### 2. Personalidad Vectorizada y Memoria Híbrida

- Ahorro de Personalidad (96%): vectorización de secciones, recuperación por similitud.
- Memoria Semántica de 10k Conversaciones: ChromaDB + FAISS con aislamiento por tenant.

### 3. Eficiencia: Matryoshka (MRL) y Quantization

- MRL: truncar vectores de 3072d a 256d reteniendo 98.37% de precisión con 4x menos storage.
- Recuperación en Dos Etapas: Shortlisting (FAISS, 64d/128d) + Reranking (BGE-Reranker-v2-m3).

### 4. Optimización Rust (PyO3 + Maturin)

- Dot Product y Similitud de Coseno: ~120s en Python vs ~1.2s en Rust (100x mejor).
- Tokenización BPE: paralelización total en todos los núcleos liberando el GIL.

### 5. Multi-Tenant y Seguridad

- Namespace Isolation: filtro tenant_id en consultas vectoriales.
- AuditLog Inmutable: firma criptográfica en operaciones de escritura.

---

## FUENTE B — Optimizaciones de Capa 5: SGLang, NVFP4 y NHP (análisis 9.4KB)

### A. ShadowRadix y RadixAttention v2

Intercambio asíncrono de páginas HBM↔RAM mediante política LRU (HiSparse Coordinator).
Rendimiento plano hasta 1M tokens, reducción del 90% en penalización de latencia.
**Estado V4:** ADOPTADO — RES.052 en CAPA_05_MASTER_V4_00.md.

### B. Atención Híbrida (CSA/HCA)

SGLang con Compressed Sparse Attention y Heavily Compressed Attention.
Reducción 90% en KV Cache y 73% en FLOPs por token.
**Estado V4:** ADOPTADO — RES.052 en CAPA_05_MASTER_V4_00.md.

### C. Inferencia NVFP4 (NVIDIA Blackwell)

Migración de FP8 a NVFP4 (4-bit). 3x throughput vs FP8, 16x más usuarios/GPU.
**Estado V4:** ADOPTADO — RES.053 en CAPA_05_MASTER_V4_00.md.

### D. XGrammar-2 para Tool-Calling

Acelera compilación de gramáticas 6x, validación JSON a nivel de token.
**Estado V4:** ADOPTADO — RES.054 en CAPA_05_MASTER_V4_00.md.

### E. Seguridad NHP

NHP para autenticación antes de conexión. Mencionado aquí como sugerencia.
**Estado V4:** ADOPTADO formalmente como protocolo completo — RES.090 en CAPA_09_MASTER_V4_00.md.

### F. EPD Disaggregation (Prefill-Decode)

Separación del procesamiento de visión del procesamiento de lenguaje.
Escala horizontal independiente de servidores ViT.
**Estado V4:** DT abierta — no adoptada en V3_02. Candidata para V4.

---

## TABLA DE ADOPCIÓN

| Componente | Estado V3_01 | Mejora Sugerida | Adoptado en V4 |
|:---|:---|:---|:---|
| Capa 3: Orquestación | No-GIL, Python 3.14t | Scheduler C++ | No — CognitiveScheduler Python suficiente |
| Capa 5: Inferencia | SGLang, NVFP4 | ShadowRadix + CSA/HCA | SÍ — RES.052/053 |
| Capa 7: Herramientas | MCP 2.0 | XGrammar-2 | SÍ — RES.054 |
| Capa 9: Seguridad | Semantic Firewall | NHP Protocol | SÍ — RES.090 |
| Capa 11: Workers | Subinterpreters | Sandboxes efímeros | DT abierta — V4 |

---

*Arquitectura_Capa5_research_unificado.md · MPAT4 docs/ · ai.mpat.tech@gmail.com · 2026-05-24*
*Investigación preliminar unificada (3 archivos) — canónico en CAPA_05_MASTER_V4_00.md*
*que has usado el formato de razonamiento adaptado por AGT*