# PROMPT ‚Äî ALUMNO PASO 1: RECOMPILACION POR CAPA
# MPAT ‚Äî My Personal Agents Team ¬∑ AGT 2026
# Version: V3_01_R2 ¬∑ 2026-05-12 ¬∑ RELAY_003 actualizado
# Cambios respecto a V3_01: incorpora RES.119 (Dream Cycle+Hebbiano) + RES.120 (NHP+ASL-3+ZTS)


---


## CONTEXTO DEL PROYECTO V3_01


Estas trabajando en MPAT V3_01. Las novedades respecto a V2_102 son:


| Componente V3_01 | RES | Capas afectadas | Config |
|---|---|---|---|
| A2A v1.0 Protocol | RES.113 | 12, 13 | config/a2a.yaml |
| SubQ Async | RES.114 | 11, 12, 13 | config/subq.yaml |
| Unikernel-per-Tenant | RES.115 | 11, 12, 13 | config/unikernel.yaml |
| MCP 2.0 Streaming | RES.116 | 7 | config/mcp.yaml |
| Tool Registry | RES.117 | 7 | config/tool_registry.yaml |
| Skill Validation Pipeline | RES.118 | 7 | config/skill_validation.yaml |
| Dream Cycle + Ori-Mnemos RMH + Hebbiano | RES.119 | 6, 8 | config/dream_cycle.yaml + config/memory.yaml |
| NHP Protocol + ASL-3 + Zero Trust Session | RES.120 | 9 | config/nhp.yaml + config/security.yaml |
| ShadowRadix + CSA/HCA | RES.030 actualizado | 5, 10 | ‚Äî (RELAY_005 pendiente) |
| policy.yaml gobernanza | ‚Äî | 14 | policy.yaml |


Python target V3_01: 3.13t (no-GIL ‚Äî paralelismo real sin GIL overhead)


Carpeta raiz del proyecto:
MPAT_V3_0/ ‚Äî ID: 1vy_pTgB1UIfDQd3UMpO-XwYvZyt2KAoM


Archivos clave:
- CAPA_XX_MASTER_V3_01.md (tu capa asignada) ‚Äî en capas/ (ID: 19G6ZNwHRc5mzMAsUq82NS7XyYuSWvJ9e)
- ARQUITECTURA_base_V3_01.md ‚Äî en arquitectura/ (ID: 1L5lKKqC7ixa8MAOjYe0OE1EbebmB0iJF)
- TEMPLATE_INFORME_CAPA_V3_01.md ‚Äî ID: 1qXP60IjCmUhuo2_Lh-D3vwSNJuQE2QqP ‚Äî en plantillas/
- RESOLUCIONES_V3_01.md ‚Äî ID: 1rXrQDwsvDU_GvQtDZGpVegE6U-2G5Yc0 ‚Äî OBLIGATORIO si tu capa es 7/11/12/13
- RESOLUCIONES_V3_01_ALTA_PRIORIDAD.md ‚Äî ID: 1cgX1mahbnf3xgP3KyI8ioshA9mkO9w9kAs2rxPBFuE8 ‚Äî OBLIGATORIO si tu capa es 6/8/9
- RESOLUCIONES_CONSOLIDADAS_V3_01.md ‚Äî en resoluciones/ ‚Äî contexto acumulado


---


## TU TAREA: PASO 1 ‚Äî RECOMPILACION DE CAPA V3_01


**Capa asignada:** [COMPLETAR]
**Archivo fuente principal:** [COMPLETAR ‚Äî ej: CAPA_07_MASTER_V3_01.md]


### Que tenes que producir


Un informe completo usando TEMPLATE_INFORME_CAPA_V3_01.md con:


1. Descripcion funcional ‚Äî que hace esta capa, cual es su responsabilidad en V3_01
2. Por que existe ‚Äî razon de diseno, que problema resuelve
3. Limites de responsabilidad ‚Äî que NO hace esta capa (igual de importante)
4. Historia de decisiones ‚Äî como evoluciono de V2_102 a V3_01
5. Componentes principales ‚Äî clases y metodos con su logica explicada
6. Design-by-Contract ‚Äî precondiciones, postcondiciones e invariantes
7. Diagrama de flujo ‚Äî ASCII del flujo de datos en la capa
8. Namespaces Redis ‚Äî todos los mpat:XX: con descripcion
9. Config files V3_01 ‚Äî YAML que controlan la capa
10. Resoluciones que afectan ‚Äî ver tabla de RES por capa abajo
11. Cadena A2A -> SubQ -> Unikernel ‚Äî OBLIGATORIA para capas 11/12/13
12. Cadena seguridad NHP -> ZTS -> ASL ‚Äî OBLIGATORIA para capa 9
13. Cadena Dream Cycle -> Ori-Mnemos -> Hebbiano ‚Äî OBLIGATORIA para capas 6/8
14. Pendientes abiertos
15. Relaciones con otras capas


### RES criticas por capa ‚Äî tabla de lectura obligatoria


| Capa | RES a leer ANTES de generar el informe |
|---|---|
| 5 | RES.030 (V2 ‚Äî contexto) |
| 6 | RES.076 + RES.077 + RES.096 (V2) + **RES.119** |
| 7 | **RES.116 + RES.117 + RES.118** |
| 8 | RES.096 (V2) + **RES.119** |
| 9 | **RES.120** |
| 10 | RES.030 + RES.110-112 |
| 11 | **RES.114 + RES.115** |
| 12 | **RES.113 + RES.114 + RES.115** |
| 13 | **RES.113 + RES.114 + RES.115** |
| 1,2,3,4,14 | Ver RESOLUCIONES_CONSOLIDADAS_V3_01.md |


### Instrucciones de trabajo V3_01


Paso 1.1 ‚Äî Leer primero:
- Tu CAPA_XX_MASTER_V3_01.md completo
- ARQUITECTURA_base_V3_01.md (principios P1-P12)
- TEMPLATE_INFORME_CAPA_V3_01.md
- Las RES de tu capa segun la tabla de arriba


Paso 1.2 ‚Äî Verificar RES segun tu capa:
- Capa 6 o 8: leer RES.119 (Dream Cycle + Ori-Mnemos RMH + Aprendizaje Hebbiano)
  Archivo: RESOLUCIONES_V3_01_ALTA_PRIORIDAD.md (ID: 1cgX1mahbnf3xgP3KyI8ioshA9mkO9w9kAs2rxPBFuE8)
- Capa 9: leer RES.120 (NHP Protocol + ASL-3 + Zero Trust Session)
  Archivo: RESOLUCIONES_V3_01_ALTA_PRIORIDAD.md (ID: 1cgX1mahbnf3xgP3KyI8ioshA9mkO9w9kAs2rxPBFuE8)
- Capa 7, 11, 12 o 13: leer RES.113-118
  Archivo: RESOLUCIONES_V3_01.md (ID: 1rXrQDwsvDU_GvQtDZGpVegE6U-2G5Yc0)


Paso 1.3 ‚Äî Generar el informe:
Decile a Claude: "Lee el CAPA_XX_MASTER_V3_01.md de mi capa y genera el informe completo
usando TEMPLATE_INFORME_CAPA_V3_01.md. Para cada componente explica el PORQUE de cada
decision, no solo el QUE. Incluye invariantes, Design-by-Contract, diagramas ASCII,
namespaces Redis, config files V3_01, y las cadenas de integracion que correspondan a
tu capa segun la tabla de RES criticas."


Paso 1.4 ‚Äî Guardar en Drive:
Nombre: INFORME_CAPA_XX_V3_01_[TU_NOMBRE].md
Carpeta: informes/ (FOLDER_INFORMES: 1WP9ONU49N1TtzjYmsmdY2r1cZ7wJeH4a)


Paso 1.5 ‚Äî Actualizar el indice:
Actualizar INDICE_INFORMES_V3_01.md con tu capa como COMPLETADO.


---


## PROMPT INICIAL PARA PEGAR EN CLAUDE


```
Sos el editor tecnico del proyecto MPAT (My Personal Agents Team) ‚Äî Version V3_01.
Tenes acceso a mi Google Drive donde esta toda la arquitectura del sistema.


El proyecto es un sistema multi-agente en Python 3.13t (no-GIL) ‚Äî Mayo 2026:
- 14 capas activas (CAPA 1 a CAPA 14)
- RES documentadas: RES.113 a RES.120 (V3_01) + RES hasta RES.112 (V2)
- Ciclo V3_01 activo


Mi tarea de hoy es generar el informe completo de [NOMBRE DE TU CAPA].


Por favor:
1. Acede al Drive y lee:
   - CAPA_XX_MASTER_V3_01.md (ID de tu capa en capas/)
   - ARQUITECTURA_base_V3_01.md (en arquitectura/)
   - TEMPLATE_INFORME_CAPA_V3_01.md (ID: 1qXP60IjCmUhuo2_Lh-D3vwSNJuQE2QqP)
   - Las RES correspondientes a tu capa (ver tabla arriba)
2. Genera el informe completo usando el template
3ååãà›X\ôH[à[ôõ‹õY\À»
QàU‘S”ïMSåUöñW€YLúåX÷ç›“ôRJCBòBÉBÉBãKKCBÉBÉBäìTU0≠»ì”T–SSSSì◊‘T”ÃW‘ëP””TSP“S”ó’å◊ÃH0≠»å◊ÃW‘åà0≠»Q’åçãLKLLäÉBäì–î””U»8†%€‹XY»\ŸHŸÿ»HõY‹àY›NMÃ–€XZ[ò€€HåçãLKLN
ÉBäú]YH\»\ÿY»[õ‹õX]»Hò^õ€ò[ZY[ù»Y\Y»‹àQ’
