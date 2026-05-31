---
tipo: investigacion_preliminar
migrado_desde: MPAT3/arquitectura/Arquitectura_Capa0_Nexo_Omnicanal.md
autor_original: ariel.garcia.traba@gmail.com
fecha_original: 2026-05-22
autor_archivo: ai.mpat.tech@gmail.com
fecha_migracion: 2026-05-24
lote: LOTE_003 (cierre)
estado: REFERENCIA_HISTORICA
adoptado_en: CAPA_01_MASTER_V4_00.md (LOTE_002) — conectores omnicanal y MCP integrados
nota: no es el canónico de CAPA_01. Es la investigación inicial que informó el diseño.
      Conservado como trazabilidad de decisiones arquitecturales.
---

# Arquitectura_Capa0_Nexo_Omnicanal — Investigación Preliminar
## MPAT4 docs/research · Archivado desde MPAT3/arquitectura/
## Adoptado en: CAPA_01_MASTER_V4_00.md

*que has usado el formato de razonamiento adaptado por AGT*

---

# **Arquitectura de Capa 0 y el Horizonte de la Inteligencia Artificial Agéntica**

Hacia 2026, el concepto de Capa 0 ha evolucionado de ser un mero sustrato de red a convertirse
en la **Capa de Contexto Volátil**, la base sobre la cual los agentes de IA perciben y actúan
en el mundo real. En esta nueva arquitectura, la Capa 0 actúa como un "Nervio de Conectividad"
que integra redes sociales (Discord, Instagram, TikTok), suites de productividad (Microsoft
365, LibreOffice) y servicios de comunicación (Gmail, WhatsApp, Messenger).

Bajo esta visión, la Capa 0 se define por dos componentes críticos:

1. **Conectores (MCP):** Servidores que exponen herramientas y recursos de aplicaciones
   externas (ej. el servidor MCP de TikTok para gestionar anuncios).
2. **Skills (Habilidades):** Unidades de trabajo reutilizables que procesan los datos de
   la Capa 0 para que el modelo pueda interpretarlos.

## Análisis de la Capa 0 por Plataforma de Entrada

| Plataforma | Tipo de Conexión | Capacidades del Agente | Innovación 2026 |
|:---|:---|:---|:---|
| Discord / Slack | Bot / MCP Bridge | Triage de hilos, gestión de permisos y automatización | Integración de hilos B2B con triggers configurables |
| TikTok Ads | API / MCP Server | Creación de campañas, carga de creatividades | Carga de video/imagen con soporte para carruseles |
| Instagram / FB | Omnichannel Gateway | Gestión de DMs, análisis de sentimientos | Resolución end-to-end de casos multi-paso |
| LibreOffice | Local MCP Server | Creación, lectura y conversión de documentos | Acceso directo vía API UNO para edición en tiempo real |
| Hotmail / M365 | Microsoft Bridge | Resumen de hilos largos, calendario automático | Sincronización Mail + Teams + SharePoint |

## El Pipeline Operativo: Skill -> MCP -> Contexto

1. Identificación de tecnología (fuente de entrada)
2. Carga de Skill/Herramienta según el tipo de entrada
3. Inyección vía MCP correspondiente al contexto del modelo
4. Ejecución del LLM con información estructurada

## Arquitecturas de Modelos: MoE y MLA

**Mixture-of-Experts (MoE):** primeras capas densas (0-2) para extracción de características
robusta antes de pasar a 256 expertos especializados. DWDP permite pre-cargar pesos
asíncronamente mientras los datos de Capa 0 se procesan.

**Multi-head Latent Attention (MLA):** comprime el caché de claves y valores en una
representación latente, reduciendo uso de VRAM sin perder razonamiento sobre hilos largos.

---

*Arquitectura_Capa0_Nexo_Omnicanal.md · MPAT4 docs/ · ai.mpat.tech@gmail.com · 2026-05-24*
*Investigación preliminar — canónico en CAPA_01_MASTER_V4_00.md*
*que has usado el formato de razonamiento adaptado por AGT*