---
name: mpat4-relay
description: "Skill de trabajo colaborativo relay para MPAT4 — Infraestructura Cognitiva Distribuida. Activar SIEMPRE cuando el alumno diga 'continuar', 'continuar con mpat4', 'seguimos', 'siguiente pendiente mpat4', 'retomar mpat4', o al inicio de sesión si hay archivos RELAY_*.md o contratos MPAT4 en contexto. La skill accede a Google Drive carpeta MPAT4, lee el último relay activo, determina el módulo de menor prioridad pendiente, genera los artefactos correspondientes (contrato, schema, evento, implementación o relay), los guarda en Drive con firma del alumno, y evalúa si continuar o traspasar. NUNCA sobreescribe versiones anteriores. NUNCA escribe código antes de tener contrato aprobado. Usar aunque el usuario no mencione la skill explícitamente si el contexto es claramente de trabajo MPAT4."
---

# MPAT4 — Skill de Trabajo Relay Colaborativo · V4_01
## ⛔ NUNCA sobreescribir — siempre archivo nuevo con versión
## ⛔ NUNCA código antes de contrato
## ⛔ NUNCA módulo sin schema Pydantic V3

---

## Propósito

MPAT4 es una Infraestructura Cognitiva Distribuida construida bimestre a
bimestre por alumnos en modo relay. No es un chatbot. No es un wrapper de LLM.
Es un sistema operativo cognitivo distribuido.

Un alumno dice "continuar con mpat4". La skill hace todo lo demás:
lee el último relay en Drive, determina el módulo a trabajar, verifica
qué contratos existen, genera el artefacto correspondiente, lo guarda
en Drive con firma del alumno, y evalúa si continuar o traspasar.

**El estado vive en Drive, no en la memoria de Claude.**

---

## Configuración requerida (una sola vez por alumno)

El alumno debe tener el servidor MCP `Google Drive` activo en su sesión de Claude.

Carpeta raíz del proyecto **MPAT4**:
```
FOLDER_ID_ROOT: 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI
```

---

## Estructura de archivos en Drive · MPAT4

```
MPAT4/                          ← 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI
│
├── LEER_PRIMERO_MPAT4_DOCUMENTACION_COMPLETA.md  ← LEER SIEMPRE PRIMERO
├── EVALUACION_ESTRUCTURA_MPAT4_*.md              ← evaluación de estado
├── README_MPAT4.md                               ← filosofía del proyecto
├── SKILL.md                                      ← este archivo
│
├── contracts/                  ← PRIORIDAD 1 — empezar aquí
├── schemas/                    ← PRIORIDAD 2
├── event_bus/                  ← PRIORIDAD 3
├── governance_engine/          ← PRIORIDAD 4
├── memory_fabric/              ← PRIORIDAD 5
├── session_scheduler/          ← PRIORIDAD 6
├── runtimes/                   ← PRIORIDAD 7
├── observability/              ← PRIORIDAD 8
├── agent_registry/             ← PRIORIDAD 9
├── cognition/                  ← PRIORIDAD 10
│
├── investigaciones/            ← INV_NNN_TEMA.md
├── resoluciones/               ← RES_NNN_DECISION.md
├── relay/                      ← RELAY_NNN.md  ← LEER AL INICIO
├── estado/                     ← STATUS_NNN_HITO.md
└── docs/                       ← documentación general
```

---

## Orden de prioridad de módulos — INVIOLABLE

| Prioridad | Módulo | ¿Tiene contrato? | ¿Tiene schema? | ¿Implementado? |
|---|---|---|---|---|
| 1 | contracts/ | — | — | — |
| 2 | schemas/ | — | — | — |
| 3 | event_bus/ | — | — | — |
| 4 | governance_engine/ | — | — | — |
| 5 | memory_fabric/ | — | — | — |
| 6 | session_scheduler/ | — | — | — |
| 7 | runtimes/ | — | — | — |
| 8 | observability/ | — | — | — |
| 9 | agent_registry/ | — | — | — |
| 10 | cognition/ | — | — | — |

---

## Flujo relay — INICIO DE SESIÓN

Cuando el alumno dice "continuar con mpat4":

```
PASO 0 — IDENTIFICACIÓN
  Preguntar si no está claro: "¿Tu nombre o email para registrar tu autoría?"
  Guardar como ALUMNO_ID para firmar todos los archivos de esta sesión.

PASO 1 — LEER ESTADO ACTUAL
  Leer relay/ → buscar el RELAY_NNN.md con número más alto (el activo)
  Leer LEER_PRIMERO_MPAT4_DOCUMENTACION_COMPLETA.md
  Leer EVALUACION_ESTRUCTURA_MPAT4_*.md
  Informar: "Sesión MPAT4 iniciada. Relay activo: RELAY_[NNN]"

PASO 2 — DETERMINAR MÓDULO A TRABAJAR
  Verificar estado de cada módulo en Drive
  Elegir el módulo de MENOR PRIORIDAD que esté PENDIENTE
  Nunca saltar prioridades

PASO 3 — CARGAR SOLO LO NECESARIO
  Leer SOLO los archivos del módulo activo + contratos previos relacionados
  NO cargar módulos no relacionados con la tarea actual

PASO 4 — GENERAR EL ARTEFACTO
  → Sin contrato: generar CONTRACT_V1.md con las 10 secciones obligatorias
  → Sin schema: generar schema.py con Pydantic V3 basado en el contrato
  → Sin implementación: generar el módulo Python con invariantes documentadas
  → Todo completo: generar investigación o resolución pendiente

PASO 5 — GUARDAR EN DRIVE
  Guardar ÚNICAMENTE en la carpeta del módulo activo + relay/
  Encabezado obligatorio en cada archivo generado:
    Autor: [ALUMNO_ID] · [FECHA]
    Módulo: [módulo] · Versión: V4_01
  ⛔ NUNCA sobreescribir — siempre archivo nuevo con versión

PASO 6 — EVALUAR CONTINUACIÓN
  Tokens > 60% restantes → continuar con la siguiente tarea del mismo módulo
  Tokens < 60% restantes → preparar relay
  Tokens < 40% restantes → GENERAR RELAY INMEDIATAMENTE
```

---

## Reglas de alcance por módulo

| Módulo activo | Carpeta donde SE PUEDE escribir | Siempre permitido |
|---|---|---|
| contracts | contracts/ | relay/ · resoluciones/ |
| schemas | schemas/ | relay/ · resoluciones/ |
| event_bus | event_bus/ | relay/ · resoluciones/ |
| governance_engine | governance_engine/ | relay/ · resoluciones/ |
| memory_fabric | memory_fabric/ | relay/ · resoluciones/ |
| session_scheduler | session_scheduler/ | relay/ · resoluciones/ |
| runtimes | runtimes/ | relay/ · resoluciones/ |
| observability | observability/ | relay/ · resoluciones/ |
| agent_registry | agent_registry/ | relay/ · resoluciones/ |
| cognition | cognition/ | relay/ · resoluciones/ |

---

## Estructura obligatoria de un CONTRATO

```markdown
# [NOMBRE]_CONTRACT_V1.md

1. OBJETIVO
2. MOTIVACIÓN ARQUITECTURAL
3. CAMPOS / INTERFACE (tipos de datos)
4. EVENTOS QUE EMITE
5. EVENTOS QUE CONSUME
6. FLUJO OPERACIONAL
7. INVARIANTES (cada ítem: INV-[COD]: descripción)
8. RIESGOS
9. OBSERVABILIDAD (logs + namespace Redis)
10. SIGUIENTE ALUMNO
```

---

## Estructura obligatoria de un SCHEMA

```python
# schemas/[modulo]_schema.py
from pydantic import BaseModel, Field

class [Modulo]Schema(BaseModel):
    """
    Referencia: contracts/[MODULO]_CONTRACT_V1.md
    """
    tenant_id: str = Field(..., description="ID del alumno/usuario. Obligatorio.")
    # Todos los campos del contrato, tipados estrictamente
    
    class Config:
        validate_assignment = True
        str_strip_whitespace = True
```

---

## Estructura obligatoria de un RELAY

```markdown
# RELAY_[NNN].md · Autor: [ALUMNO_ID] · [FECHA]

1. ESTADO ACTUAL
2. CONTRATOS DEFINIDOS
3. SCHEMAS DEFINIDOS
4. EVENTOS DEFINIDOS
5. DECISIONES ARQUITECTURALES (ref. RES_NNN.md)
6. RIESGOS DETECTADOS
7. PRÓXIMA PRIORIDAD (módulo + tarea concreta)
8. ARCHIVOS CRÍTICOS A LEER PRIMERO
9. INVARIANTES — NO ROMPER
10. DEUDA TÉCNICA
```

---

## Protocolo de traspaso

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  MPAT4 · TRASPASO AL SIGUIENTE ALUMNO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Sesión cerrada por: [ALUMNO_ID]
  Relay generado:     RELAY_[NNN].md
  Módulo trabajado:   [nombre]
  Artefactos creados: [lista]
  Próximo módulo:     [nombre] — [primera tarea concreta]

  COPIAR AL GRUPO:
  "Terminé mi sesión MPAT4. Generé RELAY_[NNN].
   Trabajé: [módulo]. Creé: [artefactos].
   Próximo: [módulo] — [tarea]."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Los 12 principios — NUNCA violar

| # | Principio | Regla práctica |
|---|---|---|
| P1 | Modularidad total | Ningún módulo llama directamente a otro. Solo via event_bus |
| P2 | Serializabilidad | Todo estado guarda en Redis con TTL definido |
| P3 | Zero Trust | Todo se autentica, valida y registra |
| P4 | Nada hardcodeado | Todo parámetro en config_policy.yaml o env vars |
| P5 | Toda decisión auditable | Si no hay log, no ocurrió |
| P6 | Degradación graceful | Timeout → cold start, nunca crash |
| P7 | Budget inviolable | budget_spent >= budget_total → el agente para |
| P8 | Policy first | La gobernanza define lo que el código puede hacer |
| P9 | Event driven | Comunicación solo via event_bus.emit() |
| P10 | Relay cognitivo | ECS serializable siempre |
| P11 | Observabilidad total | Explainability3D: 3 niveles para toda decisión |
| P12 | Cognición persistente | El conocimiento sobrevive a los reinicios |

---

## Stack tecnológico

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.14 No-GIL | Lenguaje principal |
| Pydantic | V3 | Validación de schemas |
| FastAPI | 0.115+ | API interna |
| gRPC / ConnectRPC | — | Transporte entre módulos |
| Redis | 7+ | Estado distribuido |
| NanoVMs (OPS) | — | Unikernels Python |
| OpenTelemetry | — | Observabilidad |
| MCP | 2025 | Protocolo de herramientas |
| A2A | v1.0 | Colaboración entre agentes |
| min_memory_mb | 128 | NUNCA menos para Python |

---

## IDs de carpetas Drive — MPAT4

| Carpeta | ID |
|---|---|
| MPAT4 (raíz) | `1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI` |
| contracts/ | `1a9-q9pqldwmgoVB9nd0SC3a2FGAQPgZ1` |
| schemas/ | `1qffIdQ01UCXx9L00UuJRehGuyp2tlJeH` |
| event_bus/ | `1bzk-39gmCPe70nGmZXkVNR9bQWBwBE18` |
| governance_engine/ | `1mLcTCsNbiZHkgHQNZiLzZ8IoW5fxcY5J` |
| memory_fabric/ | `1ovXyzv6zkDu4OGW7JDLJXzD9M9uB2bXl` |
| session_scheduler/ | `1zAYhSy54VLSvQ3HBpa6cSMtkVCW5fb2m` |
| runtimes/ | `1DA-xFa780YrUZp3tAVqt8B8a1ApxLaP8` |
| observability/ | `1EQYjLU2oCg_acPG67zw0mdNz7J2168uP` |
| agent_registry/ | `11u7yEBhHjjOnEIP5-C5zvHDZsq3_3mNO` |
| cognition/ | `1K1dR78NjVNT70g6VTTWv4LZxFsnbnrJU` |
| investigaciones/ | `1Kig0Oxe0s4CvDSi6x1GrmW3xdLq7CYuo` |
| resoluciones/ | `16VKDIKpDO8sWa6NxI3sGFbWlN3QHP8fj` |
| relay/ | `1c3CP8dM19BGyjOlI8TadmyL1sqSqI` |
| estado/ | `1VFhCNqvZAfCL2lpZ_M5zPCqiMpW2h6Gw` |
| docs/ | `1FlL7ACOo7o-KANItFWIBuJ62ULIHF_Oz` |

---

*SKILL.md · mpat4-relay · V4_01 · AGT 2026-05-12*
*Drive raíz: 1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI*
*Primer relay activo: relay/RELAY_001.md*
*que has usado el formato de razonamiento adaptado por AGT*
