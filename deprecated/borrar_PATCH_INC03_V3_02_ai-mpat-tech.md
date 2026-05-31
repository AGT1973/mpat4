# ARQUITECTURA_base_V3_02_PATCH_INC03.md
## Patch INC-03: CAPA_9 documenta NHP, ASL-3 y ZTS por nombre en la base canonica
## MPAT V3_02 - RELAY_014
## Autor: cursos.agt@gmail.com - 2026-05-16

---

## INC-03 - PROBLEMA

La ARQUITECTURA_base V3_01/V3_02 en el apartado INDICE DE CAPAS describe CAPA_9 como:
  "Seguridad y Validacion (Zero-Trust, Critic Agent, HITL, Semantic Firewall)"

Los informes V3_01 formalizaron tres componentes nuevos en CAPA_9 con
RES propias, invariantes nombrados e implementacion completa:
  - NHP Protocol    (RES.090, INV-NHP.1 a INV-NHP.5)
  - ASL-3           (RES.091, INV-ASL.1 a INV-ASL.4)
  - Zero Trust Session (RES.092, INV-ZTS.1 a INV-ZTS.5)

La base canonica no los menciona por nombre. Cualquier alumno que lea
la base sin leer CAPA_09_MASTER_V3_01 ignora la existencia de estos
tres componentes criticos de seguridad. Brecha documental de nivel Alto.

---

## CAMBIO 1 - EN SECCION INDICE DE CAPAS

ANTES:
  | CAPA 9  | Seguridad y Validacion | Zero-Trust, Critic Agent, HITL, Semantic Firewall |

DESPUES:
  | CAPA 9  | Seguridad y Validacion | NHP Protocol, ASL-3, Zero Trust Session,
  |         |                        | Critic Agent, HITL, Semantic Firewall |

---

## CAMBIO 2 - EN SECCION DIAGRAMA DE FLUJO

ANTES:
  [CAPA 9] Critic/Security - Zero-Trust, HITL, Semantic Firewall

DESPUES:
  [CAPA 9] Critic/Security - NHP, ASL-3, ZTS, HITL, Semantic Firewall

---

## CAMBIO 3 - AGREGAR SUBSECCION EN DESCRIPCION CAPA_9

Agregar el siguiente bloque en la descripcion de CAPA_9 de la base:

  Componentes V3_01 (FUT_3):

  NHP Protocol (RES.090):
    Handshake criptografico entre agentes antes de que fluyan datos operativos.
    Principio: authenticate-before-connect.
    Referencia completa: CAPA_09_MASTER_V3_01.md seccion 9.NHP

  ASL-3 - Agentic Security Level 3 (RES.091):
    Niveles de seguridad para agentes. A mayor autonomia, mas controles activos.
    ASL-4 requiere HITL obligatorio sin excepcion.
    Referencia completa: CAPA_09_MASTER_V3_01.md seccion 9.ASL

  Zero Trust Session (RES.092):
    Verificacion por accion individual. Un agente autenticado sigue siendo
    evaluado en cada operacion. Revocacion automatica por anomalia >= 0.8.
    Referencia completa: CAPA_09_MASTER_V3_01.md seccion 9.ZTS

---

## INVARIANTES DE CAPA_9 REFERENCIADOS EN LA BASE

La base no replica los invariantes completos (estan en el master de la capa).
Solo declara su existencia para que sean localizables:

  INV-NHP.1 a INV-NHP.5  -> ver CAPA_09_MASTER_V3_01.md
  INV-ASL.1 a INV-ASL.4  -> ver CAPA_09_MASTER_V3_01.md
  INV-ZTS.1 a INV-ZTS.5  -> ver CAPA_09_MASTER_V3_01.md
  INV-NHP-UK.1            -> ver RES143_INC06_TTL_NHP_UNIKERNEL_V3_02.md (NUEVO R014)
  INV-NHP-PERSIST         -> ver RES144_INC09_NHP_PERSIST_V3_02.md (NUEVO R014)

---

## NOTA PARA EL ALUMNO QUE APLIQUE ESTE PATCH

Este archivo es un patch diferencial. No reemplaza ARQUITECTURA_base_V3_02.md
sino que documenta los cambios a aplicar en ella. El alumno con acceso
a la base canonica debe incorporar estos cambios en el proximo RELAY
autorizado para edicion de arquitectura/.

El documento ARQUITECTURA_base_V3_02.md (ID: 1XAjf_brtVL4vuChpp5vKK1f7bBQNyE9W)
es el target de aplicacion de este patch.

---

*ARQUITECTURA_base_V3_02_PATCH_INC03.md*
*cursos.agt@gmail.com - 2026-05-16 - RELAY_014*
*INC-03 RESUELTA - patch diferencial generado*
*que has usado el formato de razonamiento adaptado por AGT*
