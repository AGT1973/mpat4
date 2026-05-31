---
migrado_desde: MPAT3/arquitectura/ (diagrama ASCII referenciado en ARQUITECTURA_base_V3_02_INC03 como ARQUITECTURA_systema_V3_03.md — archivo no existía, generado desde el contenido de la base)
id_fuente: generado en LOTE_001 desde ARQUITECTURA_base_V4_00.md
autor_migracion: agt1973@gmail.com
fecha_migracion: 2026-05-23
lote: LOTE_001
estado: MIGRADO_ADAPTADO
cambios: |
  - Diagrama expandido con stack V4
  - Docker → unikernel en todos los nodos
  - SubQ explicitado en CAPA_11
  - Python 3.14 No-GIL + Rust en stack
destino_mpat4: docs/public/
---

# ARQUITECTURA_systema_V4.md
## Diagrama completo del sistema MPAT V4

*que has usado el formato de razonamiento adaptado por AGT*

---

## FLUJO PRINCIPAL — DIAGRAMA ASCII

```
═══════════════════════════════════════════════════════════════
                    MPAT V4 — SISTEMA COMPLETO
═══════════════════════════════════════════════════════════════

CANALES EXTERNOS
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ Browser  │ Telegram │ WhatsApp │ API REST │   A2A    │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘
     └──────────┴──────────┴──────────┴──────────┘
                           │
                    ┌──────▼──────┐
                    │   CAPA_00   │
                    │  Canal +    │
                    │PlatformDet. │
                    └──────┬──────┘
                           │ UnifiedInput (frozen)
                    ┌──────▼──────┐
                    │   CAPA_01   │
                    │  QUIC GW    │  ← TLS 1.3 + JWT
                    │  + eBPF RL  │  ← rate limiting kernel
                    └──────┬──────┘
                           │ ValidatedRequest
                    ┌──────▼──────┐
                    │   CAPA_02   │
                    │  FastAPI    │  ← SSE / WebSocket
                    │  Transport  │  ← TenantContextInjector
                    └──────┬──────┘
                           │ ECS con tenant_id
         ┌─────────────────▼─────────────────┐
         │              CAPA_03              │
         │   Orchestrator / CognitiveScheduler│
         │   EntropyCalc · K_BROKEN · ZeroTrust│
         │   SwarmOrchestrator MAS            │
         │   Python 3.14 No-GIL               │
         └──┬──────────────┬────────────────┬─┘
            │              │                │
     ┌──────▼───┐   ┌──────▼──────┐  ┌─────▼──────┐
     │  CAPA_04 │   │   CAPA_06   │  │  CAPA_08   │
     │  Motor   │   │    ECS /    │  │  Memoria   │
     │ Agentes  │   │CognitiveState│  │ KnowledgeG.│
     │AgentCard │   │  Schema     │  │ DreamCycle │
     │ Handoffs │   │  Redis      │  │ ChromaDB   │
     └──────┬───┘   └─────────────┘  └────────────┘
            │
     ┌──────▼──────┐
     │   CAPA_05   │
     │  ModelRouter│  ← phi4→qwen3→gemini→claude
     │  Speculative│  ← EAGLE-3 / SSD
     │  XGrammar-2 │  ← sintaxis garantizada
     │  ShadowRadix│  ← KV cache tiered
     │  NVFP4/INT8 │  ← Blackwell only
     └──────┬──────┘
            │
     ┌──────▼──────┐
     │   CAPA_07   │
     │  MCP 2.0    │  ← ToolRegistry semántico
     │  A2A v1.0   │  ← Skills Tier 0-3
     │  SkillVal.  │  ← P13 AI Specifiers Rule
     └──────┬──────┘
            │
     ┌──────▼──────┐
     │   CAPA_09   │
     │  Seguridad  │  ← NHP Protocol (authenticate-before-connect)
     │  NHP · ASL  │  ← ASL-3 (más autonomía = más controles)
     │  ZTS · Crit.│  ← ZTS (never trust, always verify por operación)
     │  SemanticFW │  ← cada chunk SSE pasa por aquí
     └──────┬──────┘
            │
     ┌──────▼──────┐
     │   CAPA_13   │
     │  Delivery   │  ← UnikerGuard (verify tenant_id + session_id)
     │  A2ADeliv.  │  ← A2A / SubQ / Sync
     │  SubQDeliv. │
     └──────┬──────┘
            │
CANALES DE SALIDA
┌──────────┬──────────┬──────────┐
│ Usuario  │ Agente   │ SubQ    │
│ (SSE)    │ externo  │ async   │
└──────────┴──────────┴──────────┘

═══════════════════════════════════════════════════════════════
                    CAPAS TRANSVERSALES
═══════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────┐
│  CAPA_10 — Observabilidad                                    │
│  OpenTelemetry · Logger · AlertManager · MetricsRecorder     │
│  QUICSpanExporter (post-RES.157) · cognitive_metrics SQL     │
│  INV: NUNCA interrumpe el pipeline · fail silencioso         │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  CAPA_11 — Workers / SubQ                                    │
│  Redis Streams · SubQBroker · SubQProducer · SubQConsumer    │
│  ToolCallDispatcher (RES.160) · GRPOTriggerConsumer          │
│  at-least-once · dedup por message_id · TTL 24h              │
│  INV-SUBQ.5: NUNCA time.sleep() — siempre asyncio.sleep()   │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  CAPA_12 — Multi-tenancy / Budget / VMAO                     │
│  BudgetManager · P7 Conservation Law · CostTracker          │
│  A2ATenantBridge · SubQBudgetOrchestrator                    │
│  UniKernelTenantLifecycle · DAGVerifier (7 checks)           │
│  PATRÓN: RESERVE → EXECUTE → RELEASE (atómico)               │
│  destroy_at_budget_pct: 95% (NO al 100%)                     │
│  Ref: incidente COINE 2026 — $47.000 USD en 11 días         │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  CAPA_14 — Config Global                                     │
│  policy.yaml · env vars · feature flags · inference_profiles │
│  INV: NADA hardcodeado — todo configurable                   │
└──────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════
                    STACK TECNOLÓGICO V4
═══════════════════════════════════════════════════════════════

Runtime principal:   Python 3.14 No-GIL (Free-Threaded)
Hot paths:           Rust via PyO3 (SubQ broker, schema parser, eBPF)
Aislamiento:         unikernel por tenant (NanoVMs / Firecracker / Unikraft)
Validación:          Pydantic V3
Estado:              Redis + Redis Streams
Memoria:             ChromaDB + FAISS + Context Buffer
Observabilidad:      OpenTelemetry + structured logging
API:                 FastAPI + WebSocket + SSE
Transporte:          QUIC + eBPF (CAPA_01)
Canales:             WhatsApp Business, Telegram, A2A v1.0
Modelos:             phi4-mini → qwen3:8b → gemini-2.5-flash → claude-sonnet-4
Inferencia:          EAGLE-3 speculative · XGrammar-2 · ShadowRadix
Hardware:            Blackwell (B100/B200) para NVFP4 · H100 para INT8
Config:              YAML + env vars (P4: nada hardcodeado)
```

---

## INVARIANTES CRÍTICOS DEL SISTEMA (resumen)

| Invariante | Descripción | Capa |
|-----------|-------------|------|
| P3 Zero-Trust | `validated_by_orchestrator=true` solo lo setea el Orchestrator | CAPA_03 |
| P6 Degradación | El sistema entrega algo útil. Nunca excepción vacía | CAPA_05 |
| P7 Conservation | Budget delegado activo ≤ 100% del tenant | CAPA_12 |
| P13 AI Specifiers | Contrato legible por máquina antes de invocar cualquier herramienta | CAPA_07 |
| INV-NHP.1 | Sin NHP exitoso → sin datos operativos | CAPA_09 |
| INV-ZTS.1 | anomaly_score ≥ 0.8 → revocación inmediata | CAPA_09 |
| INV-ASL.3 | ASL-3 activa 6 controles adicionales (más autonomía = más supervisión) | CAPA_09 |
| INV-SUBQ.5 | NUNCA time.sleep() en ToolCallDispatcher | CAPA_11 |
| INV-12-UK-2 | Unikernel se destruye al 95% del consumo, NO al 100% | CAPA_12 |
| INV-13-UG.1 | UnikerGuard en TODOS los paths de salida | CAPA_13 |
| INV-10 | Observabilidad NUNCA interrumpe el pipeline | CAPA_10 |

---

*ARQUITECTURA_systema_V4.md · MPAT4 · docs/public/ · 2026-05-23*
*agt1973@gmail.com · LOTE_001 · Skill B mpat3-to-mpat4*
*que has usado el formato de razonamiento adaptado por AGT*
