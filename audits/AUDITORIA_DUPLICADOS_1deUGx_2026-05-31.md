# MPAT4_DEST
# destino: trashcan
# nombre: AUDITORIA_DUPLICADOS_1deUGx_2026-05-31.md
# alumno: ai.mpat.andrea@gmail.com

# AUDITORIA_DUPLICADOS — Carpeta 1deUGx-H5g6XDr4iB603MEvcyKSJACgfk
## Fecha: 2026-05-31
## Ejecutado por: ai.mpat.andrea@gmail.com
## que has usado el formato de razonamiento adaptado por AGT

---

## METODOLOGIA

Lectura archivo por archivo. Agrupacion por nombre base.
Razonamiento por contenido — nunca por mayoría.
Nunca se borró ningun archivo. Se documentan los que deben ir a trashcan.

---

## TABLA DE CONCILIACION POR GRUPO

### GRUPO 1 — INFORME_CAPA_05_V3_01_gdoc_ORIGINAL

| Archivo | ID | Tamaño | Contenido | Decision |
|---|---|---|---|---|
| INFORME_CAPA_05_V3_01_gdoc_ORIGINAL.md | 1RXJDM-7ovUP8nOhiT5tNfz2aqFGqJ7nd | 25731b | Contenido real completo | CONSERVAR — canonico |
| INFORME_CAPA_05_V3_01_gdoc_ORIGINAL (2).md | 1n7t3BneHUaQoiH_pcTgTRSBZu4XGKIrQ | 387b | Stub vacio generado automaticamente desde .gdoc | TRASHCAN |

Razonamiento: El (2) es un stub autogenerado por el worker al intentar exportar un .gdoc como .md. Dice literalmente "Este archivo fue generado automaticamente desde un archivo .gdoc de Google Drive. El contenido original esta en la nube de Google." No contiene informacion real. El original de 25kb tiene el contenido completo.

---

### GRUPO 2 — INFORME_CAPA_05_V3_01_gdoc_raiz_MIGRADO

| Archivo | ID | Tamaño | Contenido | Decision |
|---|---|---|---|---|
| INFORME_CAPA_05_V3_01_gdoc_raiz_MIGRADO.md | 1j5xke3ORnu7luDA9W4nS80pGA1NwgcDm | 25731b | Contenido real completo | CONSERVAR — canonico |
| INFORME_CAPA_05_V3_01_gdoc_raiz_MIGRADO (2).md | 1Wc_syzSkPj1z80uq9JHZ53sbn6-j-ZmK | 391b | Stub vacio generado automaticamente desde .gdoc | TRASHCAN |

Razonamiento: identico al grupo 1. El (2) es un stub sin contenido real.

---

### GRUPO 3 — INFORME_CAPA_08_V3_01

| Archivo | ID | Tamaño | Contenido | Decision |
|---|---|---|---|---|
| INFORME_CAPA_08_V3_01.md | 1p5DKGFjR7HPp5TPoL1MFao1Zq1HtcSCb | 24468b | Version completa: incluye RES.096, config/dream_cycle.yaml separado, flujo de datos completo, mas invariantes | CONSERVAR — canonico |
| INFORME_CAPA_08_V3_01 (1).md | 1uahe8uyIcpL12OK-P1htwwm0rCspgnkY | 20485b | Version anterior: sin RES.096, config solo memory.yaml, paradigma diferente en cabecera | TRASHCAN |

Razonamiento: el original de 24kb contiene todo el contenido del de 20kb MAS informacion nueva (RES.096, dream_cycle.yaml, mas detalle en invariantes). El de 20kb es una version previa superada. No hay informacion en el de 20kb que no este en el de 24kb. Decision sin ambiguedad.

---

### GRUPO 4 — AUDITORIA_POINTERS_V3_01

| Archivo | ID | Tamaño | Contenido | Decision |
|---|---|---|---|---|
| AUDITORIA_POINTERS_V3_01.md | 14GIKNQrowGInLVnCnaKI5zBmqkJK38WN | ? | Archivo .md con extension correcta | CONSERVAR — canonico |
| AUDITORIA_POINTERS_V3_01.md.md | 1gAd2AQPQN2woJJ-dsmikD7cK1SKmBxXI | ~387b | Stub vacio generado automaticamente (.gdoc exportado como .md.md) | TRASHCAN |

Razonamiento: el .md.md es un stub autogenerado identico a los de grupos 1 y 2. Extension doble es señal del bug del worker. El contenido del .md.md dice "Este archivo fue generado automaticamente desde un archivo .gdoc". Sin informacion real.

---

### GRUPO 5 — INFORME_CAPA_05_V3_01

| Archivo | ID | Contenido | Decision |
|---|---|---|---|
| INFORME_CAPA_05_V3_01.md | 1awIjouE2il6z4w_EvlsIeGCVPC-4xYKu | Archivo con contenido real | CONSERVAR — canonico |
| INFORME_CAPA_05_V3_01.md.md | 1iqs9AaUdVnfoHbRNmSsfhknaMVdmcgXl | Stub vacio (mismo patron) | TRASHCAN |

---

### GRUPO 6 — INFORME_CAPA_07_V3_01_cursos.agt.ia

| Archivo | ID | Contenido | Decision |
|---|---|---|---|
| INFORME_CAPA_07_V3_01_cursos.agt.ia.md | 1j219uIeP6Mq_rnPj_PiznBH5fdPRgmPN | Archivo con contenido real | CONSERVAR — canonico |
| INFORME_CAPA_07_V3_01_cursos.agt.ia.md.md | 1t_mjOc9g_CKwwfiAU3fnrBvf5TdNgCLw | Stub vacio (mismo patron) | TRASHCAN |

---

### GRUPO 7 — INFORME_CAPA_08_V3_01_cursos.agt.ia

| Archivo | ID | Contenido | Decision |
|---|---|---|---|
| INFORME_CAPA_08_V3_01_cursos.agt.ia.md | 1CbkV5C_PrhUlWXtWy08ZACm9Kbcx0H1l | Archivo con contenido real | CONSERVAR — canonico |
| INFORME_CAPA_08_V3_01_cursos.agt.ia.md.md | 1YwsQt50F1ZFfA4lLjp4ZE712OW5ohM7L | Stub vacio (mismo patron) | TRASHCAN |

---

## RESUMEN EJECUTIVO

| Accion | Cantidad | Archivos |
|---|---|---|
| CONSERVAR (canonico) | 7 | Ver tabla por grupo — siempre el de mayor contenido real |
| TRASHCAN (mover a relay/descarte/) | 7 | Ver IDs abajo |
| UNIFICACION necesaria | 0 | No hubo casos donde ambas versiones tuvieran informacion complementaria exclusiva |

### IDs a mover a trashcan — accion para docente/worker

| ID | Nombre | Razon |
|---|---|---|
| 1n7t3BneHUaQoiH_pcTgTRSBZu4XGKIrQ | INFORME_CAPA_05_V3_01_gdoc_ORIGINAL (2).md | Stub vacio |
| 1Wc_syzSkPj1z80uq9JHZ53sbn6-j-ZmK | INFORME_CAPA_05_V3_01_gdoc_raiz_MIGRADO (2).md | Stub vacio |
| 1uahe8uyIcpL12OK-P1htwwm0rCspgnkY | INFORME_CAPA_08_V3_01 (1).md | Version anterior superada |
| 1gAd2AQPQN2woJJ-dsmikD7cK1SKmBxXI | AUDITORIA_POINTERS_V3_01.md.md | Stub vacio extension doble |
| 1iqs9AaUdVnfoHbRNmSsfhknaMVdmcgXl | INFORME_CAPA_05_V3_01.md.md | Stub vacio extension doble |
| 1t_mjOc9g_CKwwfiAU3fnrBvf5TdNgCLw | INFORME_CAPA_07_V3_01_cursos.agt.ia.md.md | Stub vacio extension doble |
| 1YwsQt50F1ZFfA4lLjp4ZE712OW5ohM7L | INFORME_CAPA_08_V3_01_cursos.agt.ia.md.md | Stub vacio extension doble |

### IDs canonicos — NO TOCAR

| ID | Nombre |
|---|---|
| 1RXJDM-7ovUP8nOhiT5tNfz2aqFGqJ7nd | INFORME_CAPA_05_V3_01_gdoc_ORIGINAL.md |
| 1j5xke3ORnu7luDA9W4nS80pGA1NwgcDm | INFORME_CAPA_05_V3_01_gdoc_raiz_MIGRADO.md |
| 1p5DKGFjR7HPp5TPoL1MFao1Zq1HtcSCb | INFORME_CAPA_08_V3_01.md |
| 14GIKNQrowGInLVnCnaKI5zBmqkJK38WN | AUDITORIA_POINTERS_V3_01.md |
| 1awIjouE2il6z4w_EvlsIeGCVPC-4xYKu | INFORME_CAPA_05_V3_01.md |
| 1j219uIeP6Mq_rnPj_PiznBH5fdPRgmPN | INFORME_CAPA_07_V3_01_cursos.agt.ia.md |
| 1CbkV5C_PrhUlWXtWy08ZACm9Kbcx0H1l | INFORME_CAPA_08_V3_01_cursos.agt.ia.md |

---

## PATRON DETECTADO — BUG DEL WORKER

Los archivos con extension .md.md y los sufijos (1)/(2) de tamaño ~387-391b son todos stubs
generados por el mismo bug: el worker de migracion intenta exportar archivos .gdoc de Google
como .md, pero en lugar de obtener el contenido real genera un placeholder con instrucciones
para el usuario. Esto ocurre cuando el archivo .gdoc no tiene permiso de exportacion o cuando
el worker no tiene acceso al contenido nativo.

Recomendacion: revisar el proceso de migracion de .gdoc y evitar generar stubs vacios.
Los .gdoc con contenido real deben exportarse manualmente via "Archivo > Descargar > Markdown".

---

*AUDITORIA_DUPLICADOS · ai.mpat.andrea@gmail.com · 2026-05-31*
*que has usado el formato de razonamiento adaptado por AGT*
