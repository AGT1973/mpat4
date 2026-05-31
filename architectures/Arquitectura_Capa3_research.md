---
tipo: investigacion_preliminar
migrado_desde: MPAT3/arquitectura/Arquitectura_Capa3.md
autor_original: ariel.garcia.traba@gmail.com
fecha_original: 2026-05-22
autor_archivo: ai.mpat.tech@gmail.com
fecha_migracion: 2026-05-24
lote: LOTE_003 (cierre)
estado: REFERENCIA_HISTORICA
adoptado_en: CAPA_06_MASTER_V4_00.md (LOTE_003) — memoria persistente, swarm, MCP integrados
nota: el titulo dice "Capa 3" pero el contenido es sobre Capa 6 (memoria y swarm).
      Conservado como trazabilidad. LangGraph mencionado aqui fue evaluado y no adoptado.
      La arquitectura de swarm vigente en V4 usa Python 3.14t No-GIL + CognitiveScheduler.
---

# Arquitectura_Capa3 (Capa 6 Memoria + Swarm) — Investigación Preliminar
## MPAT4 docs/research · Archivado desde MPAT3/arquitectura/
## Adoptado en: CAPA_06_MASTER_V4_00.md

*que has usado el formato de razonamiento adaptado por AGT*

---

# Especificación de Ingeniería: Evolución de la Capa 6 y Arquitectura Agéntica MPAT V10

## 1. Filosofía de Diseño: Agnosticismo Total y Modularidad

La arquitectura MPAT V10 se define por su agnosticismo de modelos y proveedores.

- Conmutación Dinámica: modelos de razonamiento pesado para planificación, modelos
  ligeros para ejecución y edición de código.
- Agnosticismo de Stack: compatible con proveedores Cloud (OpenAI, Anthropic, Google)
  y locales (Ollama), con fallbacks automáticos.

## 2. Capa 6: Arquitectura de Memoria Persistente (SOTA 2026)

### 2.1 Jerarquía de Memoria y Benchmarks (LOCOMO)

- Memoria Semántica (ChromaDB/FAISS): Context Tree (ByteRover 2.0) — 92.2% de precisión.
- Detector de Conflictos: identifica contradicciones antes de escribir nuevas memorias.
- Razonamiento Temporal: metadatos temporales para preguntas tipo "¿qué sabía el martes?".

### 2.2 Modelos de Embedding Sugeridos (investigación 2026)

| Modelo | Uso | Ventaja |
|:---|:---|:---|
| nomic-embed-text (Local) | Default | Gratis, privado, funciona en CPU vieja |
| Qwen-Embedding | RAG Local | Estándar práctico para pipelines locales |
| text-embedding-3 (Cloud) | Precisión | Alta dimensionalidad (hasta 3072) |

## 3. Lógica de Swarm y Orquestación (Fase 6)

> **NOTA DE MIGRACIÓN:** Las sugerencias de LangGraph y AutoGen v0.4 aquí descritas
> fueron evaluadas y NO adoptadas en V4. La arquitectura de swarm vigente usa
> CognitiveScheduler con Python 3.14t No-GIL (RES.095). Ver CAPA_03_MASTER_V4_00.md.

- LangGraph como Estándar (evaluado, no adoptado): control determinista sobre flujos.
- Patrón Actor (AutoGen v0.4, evaluado): actores concurrentes con mensajes asíncronos.
- Blackboard Pattern: agentes leen/escriben en Redis gestionado por Swarm Coordinator.
  Este patrón SÍ fue adoptado — es el ECS + CognitiveScheduler de CAPA_03.

## 4. Conectividad y Protocolo MCP (SEP-1865)

MCP Apps (SEP-1865): servidores MCP que devuelven interfaces UI interactivas (React/HTML).
Implementado en CAPA_07 (MCPAppsRenderer) — ver CAPA_07_MASTER_V4_00.md.

## 5. Seguridad Multi-Tenant

- Aislamiento Lógico por tenant_id: adoptado (INV-ECS-NS.1 en CAPA_06).
- Identidad de Ejecución vs. Atribución: adoptado (NHP en CAPA_09).
- KeyVault: adoptado (policy.yaml con IMMUTABLE_KEYS en CAPA_14).

---

*Arquitectura_Capa3_research.md · MPAT4 docs/ · ai.mpat.tech@gmail.com · 2026-05-24*
*Investigación preliminar — canónico en CAPA_06_MASTER_V4_00.md*
*que has usado el formato de razonamiento adaptado por AGT*