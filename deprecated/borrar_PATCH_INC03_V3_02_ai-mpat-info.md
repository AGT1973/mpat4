# ARQUITECTURA_base_V3_02_PATCH_INC03.md
## Patch INC-03 — Documentar NHP/ASL/ZTS en descripcion CAPA_9

**Alumno:**     ai.mpat.info@gmail.com
**Fecha:**      2026-05-16
**RELAY:**      RELAY_014 Parte D
**INC:**        INC-03 (Alto) — CERRADA en esta sesion
**Aplica sobre:** ARQUITECTURA_base_V3_02.md (ID: 1XAjf_brtVL4vuChpp5vKK1f7bBQNyE9W)

---

## Naturaleza del patch

INC-03 detecta que ARQUITECTURA_base CAPA_9 solo menciona componentes genericos
("Zero-Trust", "Critic Agent", "HITL", "Semantic Firewall") pero NO nombra
explicitamente los tres protocolos centrales introducidos en V3_01:
- NHP Protocol (New Handshake Protocol — authenticate-before-connect)
- ASL-3 (Autonomy Safety Level 3)
- ZeroTrustSession (ZTS — gestion de sesion distribuida)

Esto genera INC cuando los informes de CAPA_09 (agt1973) referencian estos
componentes por nombre y la base no los registra.

---

## Cambio 1 — INDICE: descripcion de CAPA_9

**ANTES:**
```
CAPA 9 — Seguridad y Validacion (Zero-Trust, Critic Agent, HITL, Semantic Firewall)
```

**DESPUES:**
```
CAPA 9 — Seguridad y Validacion (NHP Protocol, ASL-3, Zero Trust Session,
          Critic Agent, HITL, Semantic Firewall)
```

---

## Cambio 2 — Diagrama de flujo: entrada CAPA_9

**ANTES:**
```
[CAPA 9] Critic/Security — Zero-Trust, HITL, Semantic Firewall
```

**DESPUES:**
```
[CAPA 9] Critic/Security — NHP Protocol, ASL-3, ZTS, HITL,
                            Critic Agent, Semantic Firewall
```

---

## Cambio 3 — Seccion CAPA_9 (bloque descriptivo)

Agregar al bloque de CAPA_9 en ARQUITECTURA_base los siguientes componentes
como parte del stack de seguridad canonico:

```
Componentes principales CAPA_9 (V3_02):
- NHP Protocol (New Handshake Protocol): authenticate-before-connect.
  Invariante INV-NHP-1. TTL sesion: nhp.session_ttl_seconds (default 300s).
  used_nonces: Redis mpat:nhp:nonces (INV-NHP-PERSIST — RES.144).
- ASL-3 (Autonomy Safety Level 3): nivel de autonomia maxima con controles
  obligatorios. Inversion ASL: mayor autonomia = mas controles activos.
- ZeroTrustSession (ZTS): gestion de sesion distribuida. Renovacion automatica
  NHP para unikernels activos (INV-NHP-UK.1 — RES.143).
- Critic Agent: evaluacion critica de outputs antes de entrega.
- HITL (Human-In-The-Loop): gate obligatorio para acciones de alto impacto.
- Semantic Firewall: filtro semantico de requests maliciosos.
```

---

## Invariantes nuevos a agregar en seccion de invariantes CAPA_9

```
INV-NHP-UK.1: TTL unikernel <= TTL sesion NHP,
              O ZTS emite renovacion automatica si unikernel RUNNING + SubQ activa.
              (RES.143 — RELAY_014)

INV-NHP-PERSIST: used_nonces DEBE usar Redis mpat:nhp:nonces con TTL = nonce_max_age_seconds.
                 Prohibido almacenamiento en memoria exclusivamente.
                 (RES.144 — RELAY_014)
```

---

## Nota de aplicacion

Este archivo es un PATCH descriptivo. El archivo canonico a modificar es
`ARQUITECTURA_base_V3_02.md` (ID: 1XAjf_brtVL4vuChpp5vKK1f7bBQNyE9W).
La aplicacion fisica debe realizarse en sesion autorizada por el docente
o en el siguiente RELAY que tenga acceso de escritura a arquitectura/.

---

*ARQUITECTURA_base_V3_02_PATCH_INC03.md*
*ai.mpat.info@gmail.com — 2026-05-16*
*INC-03 CERRADA via PATCH*
*que has usado el formato de razonamiento adaptado por AGT*
