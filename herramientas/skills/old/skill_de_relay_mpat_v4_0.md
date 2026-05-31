Skill relay para MPAT4. Activar cuando el alumno diga: '.', 'continuar', 'continuar con mpat4', 'seguimos', 'retomar mpat4', 'siguiente pendiente mpat4'. Lee RELAY\_POINTER en Drive, determina el modulo pendiente, genera artefactos, los guarda firmados, actualiza el pointer y genera el prompt para el siguiente alumno. NUNCA sobreescribe. NUNCA codigo sin contrato. NUNCA Google Doc. SIEMPRE 10 secciones en relay. SIEMPRE actualizar RELAY\_POINTER al cerrar.

# MPAT4 — Skill Relay Colaborativo V4\_10

## Reglas absolutas

- NUNCA formato Google Doc (.gdoc)

- NUNCA sobre escribir archivo — siempre versión nueva que consolide con a versión anterior. Se guarda, se cierra y a la versión anterior se la renombre con nombre archivo original se agrega ‘.old’ y la extensión original

- NUNCA código sin contrato aprobado (aprobado: python,json,ymal, rust, js,html,css,php)

- NUNCA schema sin contrato

- NUNCA Docker — solo UNIKERENEL -NanoVMs / Unikraft / Firecracker

- NUNCA cerrar sin: RELAY\_NNN + RELAY\_POINTER + prompt proximo alumno

- NUNCA relay sin las 10 secciones obligatorias

## Configuración

```
\`FOLDER\\\_ID\\\_ROOT: 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI\`  
  
\`MCP requerido: Google Drive\`
```

## IDs de carpetas Drive (verificados 2026-05-13)

```
\`MPAT4 raiz : 	  1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI\`  
  
\`agent\\\_registry/ 		: 11u7yEBhHjjOnEIP5-C5zvHDZsq3\\\_3mNO\`  
  
trust/  			: 1i9Z-BuiTUzJeNnI-iZjec-hebviwVlQQ  
  
capabilities/  		: 1v6SKL5iDXwHKfIpVWWkI21hlKX0eVGbm  
  
cards/  			: 15cLLDxO7nHm85CRtTOKvSRHUwVI6TWiO  
  
discovery/  		: 1FaR3k-CYM2937HOeBs0Fa5BjB5too3fk  
  
manifests/  		: 1EaIu-\\\_cshcwEInXQcbnoTYKtpcQmQ2BF  
  
routing/  			: 1Lehyeycb6Wou6zKtVPEmOVEQu89veNrs  
  
skills/  			: 1hi5sQoODGVVhKuoDBXmXnX1ke7zloqft  
  
\`cognition/       		: 1K1dR78NjVNT70g6VTTWv4LZxFsnbnrJU\`  
  
\`cognitive\\\_kernel/	: 1TBggzxIFCYOJEIBypAtI6YpDQ7CQ21Km\`  
  
\`connectors/      		: 1qDHX5ALRAaX443zJX89jfsp1fscSr2dk\`  
  
\`contracts/      		: 1a9-q9pqldwmgoVB9nd0SC3a2FGAQPgZ1\`  
  
\`docs/           		: 1FlL7ACOo7o-KANItFWIBuJ62ULIHF\\\_Oz\`  
  
  
\`event\\\_bus/      	: 1bzk-39gmCPe70nGmZXkVNR9bQWBwBE18\`
```

`brokers/                		: 1jX77pbwfYB9d\\\_LtsWJ64zspR3OnZnEqG `

`dead\\\_letter/            		: 14g4bjX8CDIxYAXFyhtuS1myKMjxskSeI `

`event\\\_sourcing/         		: 1FOfKvSmaAkPp2pP2pCUX\\\_TpNeGJKAPQZ `

`persistence/            		: 1eLA\\\_qOq9M0gltK8PC\\\_LewImhxtJJeFy2 `

`replay/                 		: 1V3VytkHTa1KMx68HeXDq9BQERHKdhxLO `

`streams/               		: 1GoHjiLqGx6jXLbuhJ3kGZu1mWSXGG-UW`

`subscriptions/          		: 1Qhb0LDpHNTTlQpHJpqyh2iWecWJkRrR6 `

```
\`execution\\\_graph/	: 1rffqC4Wckp19AAl-gDxJ-ozBPXSJ6TZN\`  
  
governance\\\_engine/	: 1mLcTCsNbiZHkgHQNZiLzZ8IoW5fxcY5J  
  
    trust\\\_scoring/			: 1fWbmfChx6Ee25L611DV1G\\\_zXYK79VlSv  
  
    audit/				: 1XYMC9SLHcToPCiUjki92thJ5tn-W0Oar  
  
    budget\\\_engine/			: 1eCz8MmUM\\\_HftAdB-Yogsrdae4o5auZGx  
  
    compliance/			: 19AfGRt\\\_1aBHsv2RvKXXiVSxPzVJ9dhb8  
  
    permissions/			: 1MdnKyMZLLUQZbS-dZNwXG0Uiix-ywQnr  
  
    policies/			: 1TUNIfqUAobsqMhGRQYniMY5\\\_v9sjPy1Y  
  
    runtime\\\_limits/			: 1fIX4QKDE6cwEd4VTxYjoDUPeu-5gO0gC  
  
    tenant\\\_isolation/		: 1ux4SA5owuXBOK0ST6MjQ\\\_ZibN5JsL6NW  
  
information/	 	:1P9J08R-JERwUDQQU77Yr7lgTA04oSTG9  
  
\`memory\\\_fabric/  	: 1ovXyzv6zkDu4OGW7JDLJXzD9M9uB2bXl\`
```

`consolidation/         		:1a1U75mvkpBS5xDXYI6cxRlFUe5ywgbUm `

`semantic/         			:1IjOZ2OUZFEh\\\_vnRV2ZPV\\\_oxuuy5395vz `

`embedding\\\_pipeline/         	:1BkqpDesZfQl9iBTXYZHQMbQ2DyLC9t\\\_Y `

`episodic/         			:1KWIbN49lIUrT6oT\\\_N47xud-nm3ABz7I3 `

`governance\\\_memory/         	:1Jhs3IX4hSg2CZa8RQEzitPB0F8vETFp9 `

`graph\\\_memory/         		:1wFxD2dp0-Qzi6qjfw4iyOT-\\\_k4V2FcKM `

`operational/ 			:1Ge2Lkdvd6InS67slwCWn5komEPogO46M `

`relay\\\_memory/         		:1IgAgdZrF1hU3hRVTBuEigeNkkzyl5jIh `

`retrieval/         			:1nslaMGcjdWbdXABdne8PGQXowXXYUlGi`

```
\`observability/  		: 1EQYjLU2oCg\\\_acPG67zw0mdNz7J2168uP\`
```

`tracing/         			:18YcJvsQ7JAA-gmPT8GUHzSyocwx\\\_NvHt `

`cognitive\\\_metrics/        		:1hXHoJbumOAZy\\\_H0DW\\\_M6rrnqk7ht9iy2 `

`compliance\\\_views/         	:1ui1YuerCo3K4e\\\_56I7DJO6XK4Z5sUDhE `

`explainability/         		:1gGsWevmhTi6WVXw3oF-fNqIWFobTEOga `

`replay/         			:1M529Ip5jiAnYdTZJC4l7QDqnwQyLtMI7 `

`telemetry/         			:1b19DXXudVB4R4Ku814OQ\\\_sHXH5HjzXlO `

`thought\\\_trace/         		:13uPlgpgy3UprUDysPyeti-QoyM0m7qMm`

`session\\\_sched/  	: 1zAYhSy54VLSvQ3HBpa6cSMtkVCW5fb2m`

`runtimes/       	: 1DA-xFa780YrUZp3tAVqt8B8a1ApxLaP8`

`relay/          	: 1c3CP8dM19BGyjOlI8TadmyL1KtV\\\_Tlte`

`research/       	: 1Kig0Oxe0s4CvDSi6x1GrmW3xdLq7CYuo`

`state/          : 1VFhCNqvZAfCL2lpZ\\\_M5zPCqiMpW2h6Gw`

`schemas/        	: 1qffIdQ01UCXx9L00UuJRehGuyp2tlJeH`

`resoluciones/   : 16VKDIKpDO8sWa6NxI3sGFbWlN3QHP8fj`

`para\\\_borrar/    : 1vwJ80Gs2DegcYQEgyjP2N9zq-WKB3t68`

## Estado del sistema (2026-05-13)

```
\`P1  contracts/         COMPLETO  ECS\\\_CONTRACT\\\_V1.md\`  
  
\`P2  schemas/           COMPLETO  ecs\\\_schema.py\`  
  
\`                                 event\\\_schema.py\`  
  
\`                                 event\\\_bus\\\_schema.py\`  
  
\`P3  event\\\_bus/         PARCIAL   EVENT\\\_BUS\\\_CONTRACT\\\_V4\\\_01.md OK\`  
  
\`                       PENDIENTE event\\\_bus.py\`  
  
\`P4  governance\\\_engine/ PENDIENTE\`  
  
\`P5  memory\\\_fabric/     PENDIENTE\`  
  
\`P6  session\\\_scheduler/ PENDIENTE\`  
  
\`P7  runtimes/          PENDIENTE\`  
  
\`P8  observability/     PENDIENTE\`  
  
\`P9  agent\\\_registry/    PENDIENTE\`  
  
\`P10 cognition/         PENDIENTE\`
```

## Regla de formato — INVIOLABLE

```
\`NUNCA: mimeType application/vnd.google-apps.document\`  
  
\`NUNCA: omitir disableConversionToGoogleType: true\`  
  
  
\`SIEMPRE en create\\\_file:\`  
  
\`  contentMimeType: "text/plain"       (para .skill .md .yaml .toml)\`  
  
\`  contentMimeType: "text/x-python"    (para .py)\`  
  
\`  contentMimeType: "application/json" (para .json)\`  
  
\`  disableConversionToGoogleType: true  (SIEMPRE)\`  
  
  
\`ERROR "No approval received" al guardar .py largo:\`  
  
\`  Solucion: dividir en partes y guardar por separado.\`  
  
\`  Si persiste: guardar como .md provisional + nota en relay.\`
```

## Flujo de sesion

```
\`PASO 0  Preguntar nombre/email del alumno → ALUMNO\\\_ID\`  
  
  
\`PASO 1  Leer RELAY\\\_POINTER\\\_V4\\\*.md mas reciente en raiz\`  
  
\`        Leer RELAY\\\_NNN.md activo en relay/\`  
  
\`        Informar: "Relay activo: RELAY\\\_\\\[NNN\\\]"\`  
  
  
\`PASO 2  list\\\_files en carpeta del modulo activo\`  
  
\`        NO confiar en el relay — verificar Drive siempre\`  
  
\`        Si Drive difiere del relay → creer a Drive, documentar\`  
  
  
\`PASO 3  Leer SOLO lo del modulo activo:\`  
  
\`        1. RELAY\\\_POINTER (cual modulo)\`  
  
\`        2. RELAY\\\_NNN.md activo\`  
  
\`        3. Contrato del modulo\`  
  
\`        4. Schemas relacionados\`  
  
  
\`PASO 4  Generar artefacto segun estado:\`  
  
\`        Sin contrato  → CONTRACT\\\_V1.md (10 secciones)\`  
  
\`        Sin schema    → schema.py Pydantic V3\`  
  
\`        Sin impl.     → modulo Python con invariantes\`  
  
\`        Todo completo → investigacion o resolucion pendiente\`  
  
  
\`PASO 5  Guardar en Drive\`  
  
\`        Solo en carpeta del modulo activo + relay/\`  
  
\`        Encabezado en cada archivo:\`  
  
\`          \\\# \\\[NOMBRE\\\]\`  
  
\`          \\\#\\\# Autor: \\\[ALUMNO\\\_ID\\\] · \\\[FECHA\\\]\`  
  
\`          \\\#\\\# Modulo: \\\[modulo\\\] · Version: V4\\\_01\`  
  
\`          \\\#\\\# Sistema: MPAT4 — Infraestructura Cognitiva Distribuida\`  
  
  
\`PASO 6  Cierre — 3 artefactos OBLIGATORIOS:\`  
  
\`        6a. relay/RELAY\\\_NNN+1.md — 10 secciones\`  
  
\`        6b. RELAY\\\_POINTER\\\_V4\\\_ACTUALIZADO\\\_\\\[FECHA\\\].md en raiz\`  
  
\`        6c. docs/PROMPT\\\_ALUMNO\\\_RELAY\\\_NNN+1.md\`  
  
  
\`        Token check:\`  
  
\`          \\\>60% → continuar\`  
  
\`          \\\<60% → preparar cierre\`  
  
\`          \\\<40% → CERRAR AHORA, nada mas\`
```

## Alcance por modulo

```
\`contracts/         → relay/ resoluciones/\`  
  
\`schemas/           → relay/ resoluciones/\`  
  
\`event\\\_bus/         → relay/ resoluciones/\`  
  
\`governance\\\_engine/ → relay/ resoluciones/\`  
  
\`memory\\\_fabric/     → relay/ resoluciones/\`  
  
\`session\\\_scheduler/ → relay/ resoluciones/\`  
  
\`runtimes/          → relay/ resoluciones/\`  
  
\`observability/     → relay/ resoluciones/\`  
  
\`agent\\\_registry/    → relay/ resoluciones/\`  
  
\`cognition/         → relay/ resoluciones/\`  
  
  
\`Excepcion: rescate de archivo con "No approval received"\`  
  
\`→ puede escribir en carpeta original. Documentar en relay.\`
```

## Relay — 10 secciones obligatorias

```
\`\\\# RELAY\\\_NNN.md\`  
  
\`\\\#\\\# Autor: \\\[ALUMNO\\\_ID\\\] · \\\[FECHA\\\]\`  
  
\`\\\#\\\# Modulo: \\\[modulo\\\] · Sistema: MPAT4\`  
  
\`\\\#\\\# Relay anterior: RELAY\\\_NNN-1.md\`  
  
  
\`\\\[APERTURA\\\] — modulo, prioridad, situacion\`  
  
\`\\\[INFO\\\_ALUMNO\\\] — que leer primero, que NO tocar\`  
  
  
\`1. OBJETIVO DE ESTA SESION\`  
  
\`   Que se hizo efectivamente.\`  
  
  
\`2. ARTEFACTOS CREADOS\`  
  
\`   archivo | carpeta | ID Drive | estado\`  
  
  
\`3. SCHEMAS DEFINIDOS\`  
  
\`   archivo | clases | ID Drive | invariantes\`  
  
  
\`4. EVENTOS DEFINIDOS\`  
  
\`   tipo\\\_evento | clase | cuando se emite\`  
  
  
\`5. DECISIONES ARQUITECTURALES\`  
  
\`   DEC-NNN: decision → razon → consecuencia\`  
  
  
\`6. RIESGOS DETECTADOS\`  
  
\`   RIESGO-NNN: descripcion → impacto → mitigacion\`  
  
\`   Estado: Activo | Heredado | Resuelto\`  
  
  
\`7. PROXIMA PRIORIDAD\`  
  
\`   Modulo + tarea exacta + precondiciones\`  
  
  
\`8. ARCHIVOS CRITICOS A LEER PRIMERO\`  
  
\`   Lista con IDs de Drive — no solo nombres\`  
  
  
\`9. INVARIANTES — NO ROMPER\`  
  
\`   Lista completa — no "ver contrato"\`  
  
  
\`10. DEUDA TECNICA\`  
  
\`    Que quedo incompleto · por que · quien lo resuelve\`  
  
  
\`\\\[TRASPASO → RELAY\\\_NNN+1\\\]\`  
  
\`  Mensaje listo para copiar al grupo.\`
```

## Contrato — 10 secciones obligatorias

```
\`1. OBJETIVO\`  
  
\`2. MOTIVACION ARQUITECTURAL\`  
  
\`3. CAMPOS / INTERFACE (tabla con tipos)\`  
  
\`4. EVENTOS QUE EMITE (tipo | payload minimo)\`  
  
\`5. EVENTOS QUE CONSUME\`  
  
\`6. FLUJO OPERACIONAL (pasos numerados + ramas de error)\`  
  
\`7. INVARIANTES (INV-XXX-NNN)\`  
  
\`8. RIESGOS (tabla)\`  
  
\`9. OBSERVABILIDAD (Redis + OTel + metricas)\`  
  
\`10. SIGUIENTE ALUMNO (tarea + archivos + que no tocar)\`
```

Skill de trabajo colaborativo relay para el proyecto MPAT. Activar SIEMPRE cuando el usuario diga "continuar", "seguimos", "continuar con mpat", "siguiente pendiente", "retomar mpat", o al inicio de sesión si hay archivos ARQUITECTURA\_\* en contexto. La skill accede a Google Drive, elige el pendiente de menor complejidad abierto, lo resuelve, genera la nueva versión, la guarda en Drive y registra la autoría del alumno. Si los tokens se agotan, genera el mensaje de traspaso al grupo. NUNCA sobreescribe versiones anteriores. Usar aunque el usuario no mencione la skill explícitamente si el contexto es claramente de trabajo MPAT.

# MPAT — Skill de Trabajo Relay Colaborativo · V3\_02

⛔ NUNCA sobreescribir — siempre versión nueva md NUNCA en gdoc

## Propósito

Un alumno dice "continuar". La skill hace todo lo demás: lee Drive, elige la tarea más pequeña abierta, la resuelve, guarda la nueva versión con la firma del alumno, y decide si continúa o traspasa al siguiente. SIEMPRE documentar MPAT\_V3\_0/ \<- 1vy\_pTgB1UIfDQd3UMpO-XwYvZyt2KAoM ├── sobe el sistema ├── arquitectura/ \<- 1L5lKKqC7ixa8MAOjYe0OE1EbebmB0iJF │ └── registros de modificacion o ampliacion en arquitectura del sistema ├── capas/ \<- 19G6ZNwHRc5mzMAsUq82NS7XyYuSWvJ9e │ └── registros de modificacion o ampliacion en arquitectura de cada capa ├── estado/ \<- 1OkJa4Spj8wXRp7YmVSarUcBbN\_3Fu976 │ └── registros de cambio de etapo, cierre de rama de propmt ├── informes/ \<- 1vy\_pTgB1UIfDQd3UMpO-XwYvZyt2KAoM │ └── registros toda actividad ├── investigaciones/ \<- 1vZzX0ouJOwPMIRFpX-U6TeBVzxNS5V1G │ └── fuente de todo avance (todos los "Investigación Capa X", "Arquitectura Capa X", "Análisis Comparativo") ├── plantillas/ \<- 1imVwMNte04FESokf8CnZCxR-xGTaHi38 │ └── registra template ├── resoluciones/ \<- 1IaeQLsxhjoNctFWf3PEP4OeBz4GfFHHZ │ └── registra la explicacion de porque se adopto un cambio o modificacion de estructura, conceptos, tipo de datos, etc. └── zzz\_proximo\_relay \<- 1oaXdMNDlVL5s7VYLotfL\_M4-N8Y6JTFq └── registra los relay del alumno actual al proximo alumno

**El estado vive en Drive, no en la memoria de Claude.**

## Configuración requerida (una sola vez por alumno)

El alumno debe tener el servidor MCP `Google Drive` activo en su sesión de Claude. Ver `README\\\_INSTALACION.md` entregado por el docente.

Carpeta raíz del proyecto **V3\_01**:

```
\`FOLDER\\\_ID\\\_ROOT:      1vy\\\_pTgB1UIfDQd3UMpO-XwYvZyt2KAoM\`
```

## Estructura de archivos en Drive · V3\_01

```
\`MPAT\\\_V3\\\_0/                              ← 1vy\\\_pTgB1UIfDQd3UMpO-XwYvZyt2KAoM\`  
  
\`├── arquitectura/                       ← 1L5lKKqC7ixa8MAOjYe0OE1EbebmB0iJF\`  
  
\`│   ├── ARQUITECTURA\\\_base\\\_V3\\\_01.md      ← canónico — leer primero\`  
  
\`│   ├── ARQUITECTURA\\\_pendientes\\\_V2\\\_102.md\`  
  
\`│   ├── ARQUITECTURA\\\_UNIKERNEL\\\_V3\\\_01.md ← generado en RELAY\\\_009\`  
  
\`│   └── ARQUITECTURA\\\_SUBQ\\\_V3\\\_01.md      ← generado en RELAY\\\_009\`  
  
\`├── capas/                              ← 19G6ZNwHRc5mzMAsUq82NS7XyYuSWvJ9e\`  
  
\`│   ├── CAPA\\\_01\\\_MASTER.md ... CAPA\\\_14\\\_MASTER.md\`  
  
\`│   └── CAPA\\\_XX\\\_MASTER\\\_V3\\\_01.md        ← versiones actualizadas post-RELAY\\\_001\`  
  
\`├── estado/                             ← 1OkJa4Spj8wXRp7YmVSarUcBbN\\\_3Fu976\`  
  
\`│   ├── MPAT\\\_PROYECTO\\\_ESTADO\\\_V3\\\_01.md\`  
  
\`│   └── PROMPT\\\_CONTINUIDAD\\\_V3\\\_01.md\`  
  
\`├── informes/                           ← carpeta de alumnos (vacía inicial)\`  
  
\`├── investigaciones/                    ← 1vZzX0ouJOwPMIRFpX-U6TeBVzxNS5V1G\`  
  
\`│   └── INVESTIGACION\\\_FUT3\\\_INTEGRACION\\\_V3\\\_01.md\`  
  
\`├── plantillas/                         ← 1imVwMNte04FESokf8CnZCxR-xGTaHi38\`  
  
\`│   ├── TEMPLATE\\\_INFORME\\\_CAPA\\\_V3\\\_01.md\`  
  
\`│   ├── INDICE\\\_INFORMES\\\_V3\\\_01.md\`  
  
\`│   └── PROMPT\\\_ALUMNO\\\_PASO1\\\_RECOMPILACION.md\`  
  
\`├── resoluciones/                       ← 1IaeQLsxhjoNctFWf3PEP4OeBz4GfFHHZ\`  
  
\`│   ├── RESOLUCIONES\\\_CONSOLIDADAS\\\_V3\\\_01.md  ← leer para contexto\`  
  
\`│   └── RESOLUCIONES\\\_PATCHES\\\_VALIDADAS\\\_2026-05-11.md\`  
  
\`└── zzz\\\_proximo\\\_relay/                  ← 1oaXdMNDlVL5s7VYLotfL\\\_M4-N8Y6JTFq\`  
  
\`    ├── RELAY\\\_001\\\_MPAT\\\_V3\\\_01.md\`  
  
\`    ├── RELAY\\\_NEXT\\\_POINTER.md           ← indica el próximo relay activo\`  
  
\`    └── RELAY\\\_ESTADO\\\_SESION\\\_\\\*.md\`
```

## Flujo relay — INICIO DE SESIÓN

Cuando el alumno dice "continuar": MPAT\_V3\_0/ \<- 1vy\_pTgB1UIfDQd3UMpO-XwYvZyt2KAoM ├── arquitectura/ \<- 1L5lKKqC7ixa8MAOjYe0OE1EbebmB0iJF │ └── registros de modificacion o ampliacion en arquitectura del sistema ├── capas/ \<- 19G6ZNwHRc5mzMAsUq82NS7XyYuSWvJ9e │ └── registros de modificacion o ampliacion en arquitectura de cada capa ├── estado/ \<- 1OkJa4Spj8wXRp7YmVSarUcBbN\_3Fu976 │ └── registros de cambio de etapo, cierre de rama de propmt ├── informes/ \<- 1vy\_pTgB1UIfDQd3UMpO-XwYvZyt2KAoM │ └── registros toda actividad ├── investigaciones/ \<- 1vZzX0ouJOwPMIRFpX-U6TeBVzxNS5V1G │ └── fuente de todo avance (todos los "Investigación Capa X", "Arquitectura Capa X", "Análisis Comparativo") ├── plantillas/ \<- 1imVwMNte04FESokf8CnZCxR-xGTaHi38 │ └── registra template ├── resoluciones/ \<- 1IaeQLsxhjoNctFWf3PEP4OeBz4GfFHHZ │ └── registra la explicacion de porque se adopto un cambio o modificacion de estructura, conceptos, tipo de datos, etc. └── zzz\_proximo\_relay \<- 1oaXdMNDlVL5s7VYLotfL\_M4-N8Y6JTFq └── registra los relay del alumno actual al proximo alumno

```
\`PASO 0 — IDENTIFICACIÓN\`  
  
\`  ALUMNO\\\_ID es el usuario o mail del claude de este momento\`  
  
\`  si no hay dato Preguntar: "¿Nombre o email para registrar tu autoría?"\`  
  
\`  Guardar como ALUMNO\\\_ID\`  
  
  
\`PASO 1 — LEER ESTADO ACTUAL\`  
  
\`  Leer RELAY\\\_NEXT\\\_POINTER.md de zzz\\\_proximo\\\_relay/ → saber qué relay ejecutar\`  
  
\`  Leer MPAT\\\_PROYECTO\\\_ESTADO\\\_V3\\\_01.md → estado del proyecto\`  
  
\`  Leer RESOLUCIONES\\\_CONSOLIDADAS\\\_V3\\\_01.md → contexto de resoluciones\`  
  
  
\`PASO 2 — LEER EL RELAY ACTIVO\`  
  
\`  Leer RELAY\\\_NNN\\\_MPAT\\\_V3\\\_01.md desde zzz\\\_proximo\\\_relay/\`  
  
\`  Identificar la tarea exacta (capa, archivo, acción)\`  
  
\`  Informar: "Ejecutaré RELAY\\\_\\\[NNN\\\] — \\\[descripción breve\\\]"\`  
  
  
\`PASO 3 — CARGAR SOLO LO NECESARIO\`  
  
\`  Leer el archivo de capa o carpeta indicado en el relay\`  
  
\`  Leer ARQUITECTURA\\\_base\\\_V3\\\_01.md → referencia maestra\`  
  
\`  NO cargar capas no relacionadas con el relay activo\`  
  
  
\`PASO 4 — RESOLVER\`  
  
\`  Ejecutar la tarea definida en el prompt relay\`  
  
\`  Integrar mejoras de FUT\\\_3.md si corresponde a la capa\`  
  
\`  Generar el archivo nuevo o actualizado con versión V3\\\_01\`  
  
  
\`PASO 5 — GUARDAR NUEVA VERSIÓN\`  
  
\`  Guardar ÚNICAMENTE en las carpetas autorizadas por el relay activo (ver tabla abajo)\`  
  
\`  Nombre: \\\[ARCHIVO\\\]\\\_V3\\\_01.md (nunca sobreescribir el original)\`  
  
\`  Registrar: ALUMNO\\\_ID + fecha en el encabezado del archivo\`  
  
\`  Actualizar RELAY\\\_NEXT\\\_POINTER.md → próximo relay\`  
  
\`  ⛔ NUNCA sobreescribir — siempre versión nueva\`  
  
\`  ⛔ NUNCA dejar un relay activo cortado. siempre evaluar la cantidad de tokens y el consumo de la tarea. Avisar. Esto interrumpe el trabajo de muchos alumnos\`  
  
  
\`PASO 6 — EVALUAR CONTINUACIÓN\`  
  
\`  Tokens \\\> 60% restantes → continuar con sub-tarea del mismo relay\`  
  
\`  Tokens \\\< 60% restantes → ejecutar PROTOCOLO DE TRASPASO\`  
  
\`  Tokens \\\< 80% restantes → ejecutar SOLO CHARLA E INVSETIGACIONES. NINGUNA TAREA NUEVA SOLO CIERRE\`
```

## Alcance de escritura por RELAY ← REGLA CRÍTICA

Cada RELAY tiene carpetas de destino estrictamente definidas. **Escribir fuera de estas carpetas es una violación grave — detener y avisar al alumno.**

| RELAY | Carpetas donde SE PUEDE escribir | Carpetas PROHIBIDAS |
| :-: | :-: | :-: |
| RELAY\_001 | `capas/` + `zzz\\\_proximo\\\_relay/RELAY\\\_NEXT\\\_POINTER.md` | arquitectura/, estado/, informes/, investigaciones/, plantillas/, resoluciones/ |
| RELAY\_002 | `resoluciones/` + `zzz\\\_proximo\\\_relay/RELAY\\\_NEXT\\\_POINTER.md` | capas/, arquitectura/, estado/, informes/, investigaciones/, plantillas/ |
| RELAY\_003 | `plantillas/` + `zzz\\\_proximo\\\_relay/RELAY\\\_NEXT\\\_POINTER.md` | capas/, arquitectura/, estado/, informes/, investigaciones/, resoluciones/ |
| RELAY\_004 | `informes/` + `zzz\\\_proximo\\\_relay/RELAY\\\_NEXT\\\_POINTER.md` | capas/, arquitectura/, estado/, investigaciones/, plantillas/, resoluciones/ |
| RELAY\_005 | `investigaciones/` + `zzz\\\_proximo\\\_relay/RELAY\\\_NEXT\\\_POINTER.md` | capas/, arquitectura/, estado/, informes/, plantillas/, resoluciones/ |
| RELAY\_006 | `arquitectura/` + `zzz\\\_proximo\\\_relay/RELAY\\\_NEXT\\\_POINTER.md` | capas/, estado/, informes/, investigaciones/, plantillas/, resoluciones/ |
| RELAY\_007 | `estado/` + `zzz\\\_proximo\\\_relay/RELAY\\\_NEXT\\\_POINTER.md` | capas/, arquitectura/, informes/, investigaciones/, plantillas/, resoluciones/ |
| RELAY\_008 | `zzz\\\_proximo\\\_relay/` (todos los archivos) | capas/, arquitectura/, estado/, informes/, investigaciones/, plantillas/, resoluciones/ |
| RELAY\_009 | `arquitectura/` (UNIKERNEL + SUBQ) + `zzz\\\_proximo\\\_relay/RELAY\\\_NEXT\\\_POINTER.md` | capas/, estado/, informes/, investigaciones/, plantillas/, resoluciones/ |


**Regla de oro:** si el relay activo no menciona explícitamente una carpeta, esa carpeta está PROHIBIDA en esa sesión. La duda = no escribir.

## Protocolo de traspaso

```
\`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\`  
  
\`  MPAT · TRASPASO AL SIGUIENTE ALUMNO\`  
  
\`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\`  
  
\`  Sesión cerrada por: \\\[ALUMNO\\\_ID\\\]\`  
  
\`  RELAY ejecutado:    RELAY\\\_\\\[NNN\\\]\`  
  
\`  Tarea completada:   \\\[descripción\\\]\`  
  
\`  Próximo relay:      RELAY\\\_\\\[NNN+1\\\] — \\\[descripción\\\]\`  
  
  
\`  COPIAR AL GRUPO:\`  
  
\`  "Terminé mi sesión MPAT V3\\\_01. Ejecuté RELAY\\\_\\\[NNN\\\].\`  
  
\`   Completé: \\\[tarea\\\]. Próximo: RELAY\\\_\\\[NNN+1\\\].\`  
  
\`   El siguiente puede arrancar desde MPAT\\\_V3\\\_0."\`  
  
\`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\`
```

## Reglas de calidad — NUNCA violar

| Regla | Consecuencia si se viola |
| :-: | :-: |
| Nunca sobreescribir versiones anteriores | Detener, avisar al alumno, no guardar |
| Siempre registrar ALUMNO\_ID y fecha en cada archivo | Sin firma = no válido |
| Solo cargar lo necesario para el relay activo | Economía de tokens, contexto limpio |
| Nunca borrar ítems de resoluciones | Solo agregar nuevas |
| Respetar el orden de los RELAYs 001-009 | Cada relay depende del anterior |
| Nunca implementar sin leer el relay completo | Leer antes de escribir |
| CAPA\_00 NO EXISTE en V3\_01 | Es placeholder eliminado |
| Solo escribir en las carpetas autorizadas por el relay activo | Detener, avisar al alumno, no guardar |


## IDs de carpetas Drive — V3\_01

| Carpeta | ID |
| :-: | :-: |
| MPAT\_V3\_0 (raíz) | `1vy\\\_pTgB1UIfDQd3UMpO-XwYvZyt2KAoM` |
| arquitectura/ | `1L5lKKqC7ixa8MAOjYe0OE1EbebmB0iJF` |
| capas/ | `19G6ZNwHRc5mzMAsUq82NS7XyYuSWvJ9e` |
| estado/ | `1OkJa4Spj8wXRp7YmVSarUcBbN\\\_3Fu976` |
| investigaciones/ | `1vZzX0ouJOwPMIRFpX-U6TeBVzxNS5V1G` |
| plantillas/ | `1imVwMNte04FESokf8CnZCxR-xGTaHi38` |
| resoluciones/ | `1IaeQLsxhjoNctFWf3PEP4OeBz4GfFHHZ` |
| zzz\_proximo\_relay/ | `1oaXdMNDlVL5s7VYLotfL\\\_M4-N8Y6JTFq` |


## Novedades V3\_01 que el alumno debe conocer

1. **A2A v1.0** — Protocol Agent-to-Agent: los agentes pueden invocar agentes externos

2. **Unikernel por usuario** — cada sesión de usuario corre en un unikernel aislado

3. **SubQ** — Sub-Queue asíncrona para tareas de agentes sin bloquear el orquestador

4. **ShadowRadix + CSA/HCA** — Capa 5 de inferencia optimizada para largo contexto

5. **NHP Protocol** — seguridad Capa 9, authenticate-before-connect

6. **Dream Cycle RMH** — Capa 8 con Q-Value Reranking y aprendizaje hebbiano

7. **policy.yaml** — contrato de gobernanza global activo en Capa 14

## RELAYs disponibles en zzz\_proximo\_relay/

| RELAY | Área | Estado inicial |
| :-: | :-: | :-: |
| RELAY\_001 | Capas 0-14: Documentación y depuración | ACTIVO |
| RELAY\_002 | Resoluciones | pendiente RELAY\_001 |
| RELAY\_003 | Plantillas | pendiente RELAY\_002 |
| RELAY\_004 | Informes | pendiente RELAY\_003 |
| RELAY\_005 | Investigaciones | pendiente RELAY\_004 |
| RELAY\_006 | Arquitectura consolidación | pendiente RELAY\_005 |
| RELAY\_007 | Estado y snapshot | pendiente RELAY\_006 |
| RELAY\_008 | zzz\_proximo\_relay sistema | pendiente RELAY\_007 |
| RELAY\_009 | FUT\_3 + Unikernel + SubQ | pendiente RELAY\_008 |


*versionado-mpat SKILL · V3\_02 · AGT 2026-05-11* *Cam*

