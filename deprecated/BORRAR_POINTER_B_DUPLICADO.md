═══════════════════════════════════════════════════════════════
 RELAY_NEXT_POINTER_V3_02_R017.md
 RELAY_016 CERRADO — RELAY_017 ACTIVO
 Autor: docente_AGT_2026 · 2026-05-16
 Reemplaza: RELAY_NEXT_POINTER_V3_02_R016.md (ID: 1HjU8jBxBIgZ1X7le286R1R7ZIMgrHUvV)
═══════════════════════════════════════════════════════════════

## ESTADO DEL SISTEMA

```
CICLO V3_02: ACTIVO
RELAY_001 a RELAY_016: CERRADOS ✓
RELAY_017: ACTIVO
FUT-12 familia V3_02: 5/5 COMPLETA ✓
Próxima RES disponible: RES.145
```

---

## ENTREGABLES RELAY_016

| Archivo | ID Drive | Carpeta |
|---|---|---|
| INVESTIGACION_FLOWGRPO_OBSERVABILIDAD_V3_02.md | `1_MJ4sdmk0u4Ehcs_UyOrjCYvEC6a4Spm` | investigaciones/ |
| RELAY_NEXT_POINTER_V3_02_R017.md | este archivo | zzz_proximo_relay/ |

**RES generadas:**
- RES.143 — FUT-12-D Flow-GRPO (FlowGRPO en capa_04/flow_grpo.py)
- RES.144 — FUT-12-E OpenInference (OpenInferenceAttributes en capa_10/openinference_spans.py)

**Próxima RES disponible: RES.145**

---

## FUT-12 FAMILIA V3_02 — ESTADO FINAL ✓

```
FUT-12-A  ZeroTrust/mTLS    ✓ CERRADO  RELAY_013  RES.140
FUT-12-B  Double Ratchet    ✓ CERRADO  RELAY_014  RES.141
FUT-12-C  VMAO              ✓ CERRADO  RELAY_015  RES.142
FUT-12-D  Flow-GRPO         ✓ CERRADO  RELAY_016  RES.143
FUT-12-E  OpenInference     ✓ CERRADO  RELAY_016  RES.144
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5/5 COMPLETA
```

---

## RELAY_017 — TAREA ACTIVA

**Responsable:** Primer alumno que lea este pointer
**Carpetas autorizadas:** `investigaciones/` + `zzz_proximo_relay/`
**Carpetas PROHIBIDAS:** capas/, arquitectura/, estado/, informes/, plantillas/, resoluciones/

### Tarea: INVESTIGACION_TEST_SUITE_V3_02.md (DT-2)

Suite de tests de integración cruzada: SubQ-A2A-Unikernel.

Contenido requerido (10 secciones):
1. Contexto: por qué los tests unitarios no detectan fallos de integración cross-capa
2. Escenario 1: SubQ + Budget timeout → verificar INV-12-SUBQ-2 (budget liberado)
3. Escenario 2: A2A cross-tenant con token HDP expirado → verificar INV-12-A2A-1
4. Escenario 3: Unikernel lifecycle + NHP TTL gap → verificar INC-06 (TTL 300s vs 3600s)
5. Escenario 4: VMAO DAG con nodo fallido → verificar INV-DAG.4 (cascade cancel)
6. Escenario 5: Flow-GRPO convergencia + budget ceiling → verificar INV-GRPO.2
7. Fixtures de pytest: mock Redis, mock Critic, mock A2ATenantBridge
8. Integración con OTel + OpenInference: verificar que los spans se generan correctamente
9. Invariante de la suite: todos los tests deben pasar en < 5s sin infraestructura real
10. Trampa educativa: "¿Para qué mockear si en producción todo funciona junto?"
11. RES.145 + firma + fecha

**RES a generar:** RES.145

### Leer antes de ejecutar:

| Orden | Archivo | ID |
|---|---|---|
| 1 | Este POINTER | — |
| 2 | INVESTIGACION_FLOWGRPO_OBSERVABILIDAD_V3_02.md | `1_MJ4sdmk0u4Ehcs_UyOrjCYvEC6a4Spm` |
| 3 | INVESTIGACION_VMAO_V3_02.md | `1Fj3oK5vEQzBbNmU0kUtqvUbw2GBxe-Vi` |
| 4 | CAPA_12_MASTER_V3_01.md | `1d9R13issNeUhepI2iUC561XutYUAMKXY` |
| 5 | CAPA_11_MASTER_V3_01.md | buscar en capas/ (SubQ + Unikernel) |

---

## IDs CLAVE — REFERENCIA RÁPIDA V3_02 (ACTUALIZADA)

| Recurso | ID |
|---|---|
| INVESTIGACION_FLOWGRPO_OBSERVABILIDAD_V3_02.md | `1_MJ4sdmk0u4Ehcs_UyOrjCYvEC6a4Spm` |
| INVESTIGACION_VMAO_V3_02.md | `1Fj3oK5vEQzBbNmU0kUtqvUbw2GBxe-Vi` |
| INVESTIGACION_DOUBLERATCHET_V3_02.md | `1Yo2H4MWMCy5gEopGLQ9fDr6cyPrz0kdC` |
| INVESTIGACION_ZEROTRUST_V3_02.md | `1NPNBz2Y_6bja-3aV-qDYgE4lpG37dC3i` |
| RESOLUCIONES_CONSOLIDADAS_V3_02_R013.md | `1ZLdclhRZt6BiJiRVYXnpMhdWo4JyQWMd` |
| ARQUITECTURA_base_V3_02.md | `1XAjf_brtVL4vuChpp5vKK1f7bBQNyE9W` |
| CAPA_04_MASTER_V3_01.md | `1ZIxbvRY-JbqT-CwtDHeY0HARWgUsOxCD` |
| CAPA_10_MASTER_V3_01.md | `1qGVZ1-HYWWTbseRfFewQVPU4xanhWDIu` |
| CAPA_12_MASTER_V3_01.md | `1d9R13issNeUhepI2iUC561XutYUAMKXY` |
| investigaciones/ | `1vZzX0ouJOwPMIRFpX-U6TeBVzxNS5V1G` |
| resoluciones/ | `1IaeQLsxhjoNctFWf3PEP4OeBz4GfFHHZ` |
| zzz_proximo_relay/ | `1oaXdMNDlVL5s7VYLotfL_M4-N8Y6JTFq` |

---

## PENDIENTES MANUALES — Sin cambio

| PM | Estado |
|---|---|
| PM-001 (gdoc en informes/) | PENDIENTE MANUAL |
| SUBQ duplicados x2 | PENDIENTE MANUAL |
| CAPA_05 gdoc | PENDIENTE MANUAL |
| gdocs FUT19/FUT20 (5 archivos) | PENDIENTE MANUAL |

---

### Mensaje al grupo:

```
════════════════════════════════════════════════
 RELAY_016 CERRADO — FUT-12 COMPLETA
════════════════════════════════════════════════
 Alumno: docente_AGT_2026
 Fecha: 2026-05-16

 Entregable:
 INVESTIGACION_FLOWGRPO_OBSERVABILIDAD_V3_02.md
 ID: 1_MJ4sdmk0u4Ehcs_UyOrjCYvEC6a4Spm

 FUT-12-D: Flow-GRPO (RES.143)
   — GRPOSession + FlowGRPO con 7 invariantes
   — Loop SAMPLING→EVALUATING→UPDATING
   — 6 guardas de seguridad (HITL, ASL-3, budget, sync)

 FUT-12-E: OpenInference (RES.144)
   — 7 tipos de spans semánticos integrados en MPAT
   — LLM/Agent/Tool/Retriever/Reranker/Embedding/Chain
   — INV-OI.3: redacción automática con privacy HIGH

 FUT-12 familia V3_02: 5/5 CERRADA ✓
 Próxima RES: RES.145
 Próximo: RELAY_017 — Suite tests DT-2
════════════════════════════════════════════════
```

---

*RELAY_NEXT_POINTER_V3_02_R017.md · MPAT V3_02 · 2026-05-16*
*docente_AGT_2026 — RELAY_016 CERRADO*
*que has usado el formato de razonamiento adaptado por AGT*
