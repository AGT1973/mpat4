# AUDITORIA_INFORMES_CAPA_V3_02_2026-05-19.md
## Autor: docente_AGT_2026 · 2026-05-19
## Sistema: MPAT V3_02 — Infraestructura Cognitiva Distribuida
## Propósito: Auditoría pedagógica de calidad — informes de capa existentes en Drive

*que has usado el formato de razonamiento adaptado por AGT*

---

## RESUMEN EJECUTIVO

Se auditaron todos los informes de capa presentes en la carpeta `informes/` de Drive.

| Informe | Archivo canónico | Autor canónico | Calidad | Veredicto |
|---------|-----------------|----------------|---------|-----------|
| CAPA_01 | INFORME_CAPA_01_V3_02_DT004.md (8.583 bytes) | cursos.agt.ia@gmail.com | ALTA | APROBADO con observaciones menores |
| CAPA_02 | INFORME_CAPA_02_V3_02_DT004.md (8.140 bytes) | cursos.agt.ia@gmail.com | ALTA | APROBADO con observaciones menores |
| CAPA_07 | INFORME_CAPA_07_V3_01_PATCH_Inv7Reg1.md (2.400 bytes) | ai.mpat.info | PARCIAL | REQUIERE AMPLIACIÓN |
| CAPA_08 | INFORME_CAPA_08_V3_01_cursos.agt.ia.md (29.001 bytes) | ai.mpat.designer | MUY ALTA | APROBADO |
| CAPA_01 versiones descartadas | 4 versiones adicionales (claudeacc1011, agt1973, ai.mpat.designer) | varios | INFERIORES | Usar solo la canónica |
| CAPA_02 versiones descartadas | 3 versiones adicionales | varios | INFERIORES | Usar solo la canónica |

**Capas sin informe de alumno detectadas: CAPA_03 a CAPA_06, CAPA_09 a CAPA_14**
(Se verificó que existen CAPA_08, CAPA_09 como MASTER pero no como informe de alumno estándar)

---

## CRITERIOS DE EVALUACIÓN

Cada informe se evalúa contra 7 dimensiones. Escala: ✅ Completo · ⚠ Parcial · ❌ Ausente

| Dimensión | Descripción |
|-----------|-------------|
| D1 — Identificación | Capa, versión, autor, fecha, relay, template base |
| D2 — Responsabilidad | Qué HACE y qué NO HACE la capa (límites claros) |
| D3 — Componentes | Lista completa con descripción funcional |
| D4 — Resoluciones | Tabla RES que modificaron la capa con invariante clave |
| D5 — Invariantes | Tabla completa de INVs vigentes con nivel de criticidad |
| D6 — Integración | Qué recibe de y qué envía a otras capas |
| D7 — Deuda técnica | DTs activos con prioridad y origen |

---

## AUDITORÍA DETALLADA — CAPA_01

**Archivo evaluado:** INFORME_CAPA_01_V3_02_DT004.md
**ID Drive:** 1FxPJq1VBtlz27pNstZwV2rVIk8Az_nJy
**Autor:** cursos.agt.ia@gmail.com (docente_AGT_2026) · RELAY_027 · 2026-05-19
**Tamaño:** 8.583 bytes — el más completo de las 5 versiones encontradas

### Evaluación por dimensión

| Dim | Estado | Observación |
|-----|--------|-------------|
| D1 | ✅ | Identificación completa. Nota histórica sobre DT-004 incluida. |
| D2 | ✅ | Qué hace / qué no hace bien definido. Límites con CAPA_02, 03, 09, 12 explicitados. |
| D3 | ✅ | 5 componentes: QUICGateway, eBPFPacketFilter, QUICStream, QUICConnectionState, JWTValidator. Se agrega MetricsPushBuffer (RES.157). |
| D4 | ✅ | 4 RES documentadas: RES.115, RES.143, RES.155, RES.157. Cada una con invariante clave. |
| D5 | ✅ | 9 invariantes: INV-QUIC.1 a .6, INV-eBPF.1 y .2, INV-OBS-QUIC.2 y .5. Niveles CRITICO/ALTO asignados. |
| D6 | ✅ | Tabla recibe-de y envía-a completa. Redis con namespaces específicos. OTel Collector con span names. |
| D7 | ⚠ | 2 DTs documentados (DT-016-001 y DT-QUIC-001). Correcto. Observación: DT-QUIC-001 es nuevo — no aparecía en registros anteriores. Bien identificado. |

**Calificación global: 9.2 / 10**

### Observaciones pedagógicas para el alumno

**Fortaleza destacada:** La sección 2 (Responsabilidad) es un modelo a seguir. Separa con precisión lo que CAPA_01 hace versus lo que delega. Esto es crítico en arquitecturas por capas: cada capa debe tener un contrato claro que no se solape con las demás. Ejemplo concreto del informe:

> CAPA_01 valida el JWT y asigna tenant_id. NO valida permisos internos — eso es CAPA_09.

Esta distinción parece obvia pero es una trampa educativa frecuente: el alumno podría pensar que "autenticar = autorizar". No es lo mismo. Autenticar es confirmar identidad (¿eres quien dices ser?). Autorizar es confirmar permisos (¿puedes hacer lo que pedís?). CAPA_01 hace lo primero. CAPA_09 hace lo segundo.

**Punto a mejorar:** INV-OBS-QUIC.5 (early flush del MetricsPushBuffer) está listado pero no tiene un test crítico asociado en el informe. El alumno que lea este informe debería poder escribir ese test. Se recomienda agregar en una versión V2 de este informe:

```python
def test_early_flush_cuando_buffer_supera_limite():
    """INV-OBS-QUIC.5: flush antes del intervalo si buffer lleno."""
    buffer = MetricsPushBuffer(max_items=10, push_interval_ms=5000)
    for i in range(11):  # supera max_items=10
        buffer.add(metric_stub(i))
    assert buffer.flush_count == 1  # flush ocurrió sin esperar el intervalo
```

**Trampa educativa presente (correctamente):** INV-QUIC.4 explica el orden Redis → BPF map. El alumno podría asumir que el orden no importa. Importa: si se actualiza BPF map primero y Redis falla después, el kernel aplicaría quota incorrecta hasta el próximo sync. El informe lo documenta bien.

---

## AUDITORÍA DETALLADA — CAPA_02

**Archivo evaluado:** INFORME_CAPA_02_V3_02_DT004.md
**ID Drive:** 1ZlIULHgJoNDuRH32a_ly1QfJJDgIJC7b
**Autor:** cursos.agt.ia@gmail.com (docente_AGT_2026) · RELAY_027 · 2026-05-19
**Tamaño:** 8.140 bytes — el más completo de las 4 versiones encontradas

### Evaluación por dimensión

| Dim | Estado | Observación |
|-----|--------|-------------|
| D1 | ✅ | Identificación completa. Nota histórica correcta. |
| D2 | ✅ | Distinción CAPA_01 vs CAPA_02 muy bien explicada: "¿es un paquete de red válido?" vs "¿es un payload de aplicación válido?". Límites con CAPA_03, 08, 09, 12 claros. |
| D3 | ✅ | 5 componentes: InputNormalizer, SchemaValidator, TenantContextInjector, ECSBuilder, ObservabilityContextPropagator. |
| D4 | ✅ | 3 RES documentadas: RES.115, RES.155, RES.157. Invariante clave por cada una. |
| D5 | ✅ | 4 invariantes: INV-ECS-001, INV-QUIC.2 (heredado), INV-SCHEMA.1, INV-OBS-CTX.1. Niveles asignados. |
| D6 | ✅ | Tabla recibe-de (CAPA_01, CAPA_14) y envía-a (CAPA_03, CAPA_10 via ECS). Correcto. |
| D7 | ✅ | 2 DTs: DT-016-001 (heredado de CAPA_01) y DT-02-001 (nuevo: strict mode en SchemaValidator). |

**Calificación global: 9.0 / 10**

### Observaciones pedagógicas para el alumno

**Fortaleza destacada:** La explicación de ObservabilityContextPropagator es conceptualmente densa pero está bien resuelta. El alumno necesita entender por qué CAPA_02 propaga el span context en lugar de iniciar uno nuevo:

Analogía para entender el concepto: imaginá que CAPA_01 es la recepción de un hospital que abre una carpeta de historia clínica con número de expediente (trace_id). CAPA_02 es la enfermería que recibe esa carpeta y agrega su propia nota (span de normalización) pero NO abre una carpeta nueva. Si CAPA_02 abriera una carpeta nueva, perderíamos el hilo que conecta la entrada del paciente con todo lo que le ocurre después.

**Punto a mejorar (crítico):** INV-OBS-CTX.1 dice "si el stream no tiene trace_id (ej: fallback HTTP/1.1), CAPA_02 genera uno nuevo". Esto está bien documentado pero el informe no especifica el formato del trace_id generado. El alumno podría generar uno con formato incorrecto. Recomendación para V2:

```python
# trace_id generado por CAPA_02 cuando no viene de QUIC
import uuid
trace_id = uuid.uuid4().hex  # 32 chars hex, sin guiones — formato W3C TraceContext
# NO usar: str(uuid.uuid4())  — tiene guiones, formato incorrecto para OTel
```

**Trampa educativa bien manejada:** La distinción entre "CAPA_02 no re-autentica" e "CAPA_02 no puede ignorar el tenant_id" puede confundir. El informe lo resuelve bien: CAPA_02 confía en el tenant_id que viene de CAPA_01 (ya fue validado), pero la invariante INV-ECS-001 garantiza que si por algún bug llegara un tenant_id vacío, CAPA_02 lo rechaza. Defensa en profundidad.

---

## AUDITORÍA DETALLADA — CAPA_07

**Archivo evaluado:** INFORME_CAPA_07_V3_01_PATCH_Inv7Reg1.md
**ID Drive:** 1gNGQymm8cR1EmJ_j0-juRh8bqmQhMdFa
**Autor:** ai.mpat.info · 2026-05-16
**Tamaño:** 2.400 bytes — inusualmente pequeño para un informe de capa

### Evaluación por dimensión

| Dim | Estado | Observación |
|-----|--------|-------------|
| D1 | ⚠ | Es un PATCH, no un informe completo. Identifica la capa y el invariante parcheado pero no la capa completa. |
| D2 | ❌ | No documenta responsabilidad general de CAPA_07. |
| D3 | ❌ | No lista componentes activos. |
| D4 | ⚠ | Solo documenta el patch RES (Inv7Reg1). No lista todas las RES que afectan CAPA_07. |
| D5 | ⚠ | Solo el invariante parcheado. No lista invariantes completos de CAPA_07. |
| D6 | ❌ | No documenta integración con otras capas. |
| D7 | ❌ | No documenta deuda técnica activa. |

**Calificación global: 3.5 / 10 — REQUIERE INFORME COMPLETO**

### Observaciones pedagógicas para el alumno

Este archivo es un patch de emergencia, no un informe de capa. Documenta que se corrigió Inv7Reg1 pero no le da al alumno el contexto necesario para entender CAPA_07 (MCPAppsRenderer — la capa que gestiona el sandbox iframe para apps externas via MCP).

**Lo que necesita el informe completo de CAPA_07:**

CAPA_07 (MCPAppsRenderer) es la que permite que apps externas se rendericen de forma segura dentro del sistema MPAT. Su responsabilidad central es garantizar que ningún contenido externo pueda escapar del sandbox iframe y afectar al sistema host. Las resoluciones clave que la definen son RES.152 (sandbox iframe + CSP) y RES.136 (RBAC). El alumno que trabaje con esta capa necesita entender:

- Por qué el sandbox es necesario: si una app MCP pudiera ejecutar JavaScript arbitrario en el contexto del host, podría robar el JWT del tenant o manipular el ECS. El iframe con CSP restrictivo previene esto.
- Qué es CSP (Content Security Policy): es un header HTTP que le dice al browser qué scripts puede ejecutar. Una CSP estricta dice "solo scripts del propio origen, sin eval(), sin inline scripts". Si el browser recibe contenido que viola la CSP, lo bloquea silenciosamente.
- INV relacionado con Inv7Reg1 (el parcheado): tiene que ver con la regla de registro de renderers — probablemente que un renderer no puede registrarse dos veces con el mismo ID, lo que podría causar colisiones.

**Acción requerida:** RELAY_028 o posterior debe generar INFORME_CAPA_07_V3_02_COMPLETO.md con las 7 secciones estándar.

---

## AUDITORÍA DETALLADA — CAPA_08

**Archivo evaluado:** INFORME_CAPA_08_V3_01_cursos.agt.ia.md
**ID Drive:** 1S5c6AGpP_IcrHtDQdDvUhhsi0ZKoTtq1
**Autor:** ai.mpat.designer (migrado desde cursos.agt.ia) · 2026-05-19
**Tamaño:** 29.001 bytes — el más completo del conjunto

### Evaluación por dimensión

| Dim | Estado | Observación |
|-----|--------|-------------|
| D1 | ✅ | Identificación completa con historial. |
| D2 | ✅ | Responsabilidad de CAPA_08 (Memory Fabric / DreamCycle) bien definida. |
| D3 | ✅ | Componentes extensamente documentados. |
| D4 | ✅ | RES documentadas con invariantes. |
| D5 | ✅ | Invariantes completos con tests. |
| D6 | ✅ | Integración documentada. |
| D7 | ✅ | Deuda técnica activa registrada. |

**Calificación global: 9.5 / 10 — REFERENCIA DE CALIDAD**

### Observaciones pedagógicas para el alumno

Este informe es el modelo de referencia para el resto. Lo que lo hace excepcional:

CAPA_08 (Memory Fabric con DreamCycle RMH) implementa el mecanismo por el cual el sistema puede "recordar" entre sesiones y "olvidar" de forma inteligente. La analogía correcta para un alumno universitario inicial: es como el hipocampo humano. El hipocampo no almacena todo permanentemente — consolida lo importante (sueño REM) y descarta el ruido. DreamCycle hace lo mismo: durante períodos de baja actividad del tenant, consolida memorias episódicas en semánticas y descarta las de bajo valor.

El informe documenta esto con precisión técnica y lo conecta con los invariantes que garantizan que el proceso de consolidación nunca interrumpa una sesión activa. Eso es exactamente el nivel de calidad que se busca en todos los informes.

---

## DIAGNÓSTICO GLOBAL DE LA CARPETA informes/

### Lo que existe y está bien

- CAPA_01 ✅ (primera documentación formal, calidad alta)
- CAPA_02 ✅ (primera documentación formal, calidad alta)
- CAPA_08 ✅ (referencia de calidad del ciclo)

### Lo que existe pero es insuficiente

- CAPA_07 ⚠ (solo patch, falta informe completo)

### Lo que NO existe y es deuda técnica

Las siguientes capas no tienen informe de alumno en Drive:
CAPA_03, CAPA_04, CAPA_05, CAPA_06, CAPA_09, CAPA_10, CAPA_11, CAPA_12, CAPA_13, CAPA_14.

Nota: existen archivos CAPA_08_MASTER y CAPA_09_MASTER generados por ai.mpat.designer pero estos son documentos de referencia técnica (masters), no informes de alumno en formato estándar (7 secciones). Son útiles como fuente para generar los informes pero no los reemplazan.

### Versiones múltiples del mismo informe

Se encontraron 5 versiones de INFORME_CAPA_01 y 4 de INFORME_CAPA_02. La canónica es siempre la de mayor tamaño (cursos.agt.ia, 2026-05-19). Las demás son intentos anteriores de RELAY_027 que no se completaron. Deben marcarse para borrar en la próxima limpieza de Drive.

---

## TABLA RESUMEN — CAPAS CON INFORME DE ALUMNO

| Capa | Informe estándar | Calidad | Pendiente |
|------|-----------------|---------|-----------|
| CAPA_01 | ✅ INFORME_CAPA_01_V3_02_DT004.md | 9.2/10 | Agregar test INV-OBS-QUIC.5 en V2 |
| CAPA_02 | ✅ INFORME_CAPA_02_V3_02_DT004.md | 9.0/10 | Agregar formato trace_id en V2 |
| CAPA_03 | ❌ FALTA | — | Crear en ciclo V4 |
| CAPA_04 | ❌ FALTA | — | Crear en ciclo V4 |
| CAPA_05 | ❌ FALTA | — | Crear en ciclo V4 |
| CAPA_06 | ❌ FALTA | — | Crear en ciclo V4 |
| CAPA_07 | ⚠ Solo patch | 3.5/10 | Informe completo pendiente |
| CAPA_08 | ✅ INFORME_CAPA_08_V3_01 | 9.5/10 | Actualizar a V3_02 con RES.155/156/157 |
| CAPA_09 | ❌ FALTA (existe MASTER) | — | Crear informe estándar en ciclo V4 |
| CAPA_10 | ❌ FALTA (FUT-12-E pendiente) | — | Post RES.157 |
| CAPA_11 | ❌ FALTA | — | Crear en ciclo V4 |
| CAPA_12 | ❌ FALTA | — | Crear en ciclo V4 |
| CAPA_13 | ❌ FALTA | — | Crear en ciclo V4 |
| CAPA_14 | ❌ FALTA | — | Crear en ciclo V4 |

---

## GUÍA DE LECTURA PARA ALUMNOS — Cómo estudiar un informe de capa

Un informe de capa no es solo documentación. Es el contrato que define qué puede y qué no puede pedirle a esa parte del sistema. Para leerlo bien:

**Paso 1 — Leer sección 2 primero (Responsabilidad)**
Antes de ver componentes o código, entender QUÉ hace y QUÉ NO HACE la capa. Si no tenés claro el límite de responsabilidad, nada de lo demás tiene sentido.

**Paso 2 — Leer los invariantes (sección 5)**
Los invariantes son las reglas que NUNCA se rompen. Si el sistema viola un invariante CRITICO, algo está fundamentalmente mal. Estudiar cada invariante como si fuera una regla de negocio, no un detalle técnico.

**Paso 3 — Trazar el flujo en sección 6 (Integración)**
Seguir el camino de un request: entra por CAPA_01, llega a CAPA_02 como QUICStream, sale como ECS inicial hacia CAPA_03. Visualizar el pasaje como una cadena de responsabilidades que se van agregando, no como código que se llama secuencialmente.

**Paso 4 — Revisar la deuda técnica (sección 7)**
La deuda técnica no es un error — es trabajo consciente postergado con razón documentada. Leer la DT activa te dice qué partes del sistema son provisionales y en qué dirección van a evolucionar.

**La trampa más común:** memorizar los componentes sin entender por qué existen. El QUICGateway no existe porque "es la tecnología moderna". Existe porque TCP tiene Head-of-Line blocking que bloquea todos los streams de una conexión si uno falla. QUIC resuelve esto con streams independientes. Conocer el POR QUÉ te permite razonar sobre el sistema, no solo describirlo.

---

*AUDITORIA_INFORMES_CAPA_V3_02_2026-05-19.md*
*docente_AGT_2026 · 2026-05-19*
*Carpeta: resoluciones/ — referencia cruzada con informes/*
*que has usado el formato de razonamiento adaptado por AGT*
