# RESOLUTION_QUEUE_MPAT4.md
## Cola completa de resoluciones pendientes — MPAT4
## Autor: cursos.agt.ia@gmail.com (docente_AGT_2026) · 2026-05-23
## Base: RELAY_RESEARCH_INDEX.md + relays anteriores + T-008 activo

*que has usado el formato de razonamiento adaptado por AGT*

---

## REGLAS DE LA COLA

- Un alumno toma UNA resolución por sesión.
- Verificar en Drive que el artefacto no exista antes de crear.
- Al terminar: actualizar RELAY_POINTER con nueva RES usada.
- Prioridad A: bloqueante para otros. Prioridad B: independiente. Prioridad C: investigación pura.
- Los RELAY_RESEARCH correspondientes dan el contexto completo.

---

## BLOQUE 0 — ACTIVO AHORA (RES.163)

| RES | Tarea | Prioridad | Alumno | Estado |
|---|---|---|---|---|
| **RES.163** | T-008 Session Scheduler V4 (warm pool + hydration) | **A** | RELAY_009 activo | **EN CURSO** |

Artefactos generados en RELAY_009 (relay/ con prefijo T008__):
- `T008__session_scheduler_v4.py` → mover a `session_scheduler/`
- `T008__hydration_loader.py` → mover a `session_scheduler/`
- `T008__session_scheduler_schema_v4.py` → mover a `schemas/`

---

## BLOQUE 1 — PRIORIDAD A (RES.164–170) — Bloqueantes para el resto

| RES | Item | Descripción | Carpeta destino | RELAY_RESEARCH fuente |
|---|---|---|---|---|
| **RES.164** | P01 Cognitive Event Mesh | CognitiveEventMesh + MeshRouter — routing semántico, topología distribuida, garantías causales. Extiende event_bus_v4.py SIN sobreescribir. Hub máximo: 9 referencias. | `event_bus/` | RELAY_RESEARCH_P01_P75 |
| **RES.165** | P31 AI Native OS | Abstracciones cognitivas sobre el Cognitive Kernel: CognitiveProcess, CognitiveThread, CognitiveIPC. Redefine el SO para agentes. | `core/` | RELAY_RESEARCH_VOL1 item 31 |
| **RES.166** | Item 02 A2A Economy | A2AEconomyEngine: propose_contract, accept_contract, escrow_budget, settle_transaction. Schema A2AContractSchema. | `ecosystem/a2a_economy/` | RELAY_RESEARCH_VOL1 item 02 |
| **RES.167** | Item 03 Persistent Cognitive Memory Graph | CognitiveMemoryGraph con FalkorDB/Neo4j local. Nodos Entity+Concept, relaciones RELATED_TO/OWNED_BY. Query Cypher + hybrid_search. | `core/memory_fabric/graph/` | RELAY_RESEARCH_VOL1 item 03 |
| **RES.168** | P69 Audit Ledger | AuditLedger SHA-256 encadenado. record_event() + verify_chain(). Persistencia binaria indexada. Thread-safe async. | `observability/` | RELAY_RESEARCH_P69 |
| **RES.169** | P69 OTel Tracer | AgentSpan + ToolSpan + LLMSpan. Decoradores @agent_span @tool_span @llm_span. Exportador OLTP a Arize Phoenix local. | `observability/` | RELAY_RESEARCH_P69 |
| **RES.170** | Item 44 MCP 2.0 Providers | Servidores MCP independientes en stdio JSON-RPC. Manifiesto de herramientas. Inyección dinámica en runtime. | `providers/mcp/` | RELAY_RESEARCH_VOL2 item 44 |

---

## BLOQUE 2 — PRIORIDAD B (RES.171–185) — Independientes entre sí

| RES | Item | Descripción breve | Carpeta | Fuente |
|---|---|---|---|---|
| **RES.171** | AESP Engine | AESPEngine 4 triggers biométricos + ReviewManager cola HITL. Integración con OPAEngine. | `governance_engine/aesp/` | RELAY_RESEARCH_AESP |
| **RES.172** | AESP Cognitive Drift | CognitiveDriftDetector 5 mecanismos + Emergency Freeze. Integración con EventBusV4. | `governance_engine/aesp/` | RELAY_RESEARCH_AESP |
| **RES.173** | Item 45 Router Cognitivo | Clasificador BERT ligero SLM/LLM. Router dinámico por complejidad. Circuit breaker ante caída de agente. | `core/cognitive_router/` | RELAY_RESEARCH_VOL2 item 45 |
| **RES.174** | Item 51 Tiered Memory | CognitiveMemoryManager 3 capas: RAM / Redis-SQLite / disco vectorial. LRU semántico. | `core/memory_fabric/` | RELAY_RESEARCH_VOL2 item 51 |
| **RES.175** | Item 52 Guardrails LlamaGuard | Hook interceptor streaming tokens. Clasificador lineal local. AbortController ante contenido dañino. | `governance_engine/guardrails/` | RELAY_RESEARCH_VOL2 item 52 |
| **RES.176** | Item 42 LanceDB Vectorial | LanceDB embebido en ~/.mpat/vectors. Query híbrida FTS+HNSW. RRF fusion. | `core/vector_runtime/` | RELAY_RESEARCH_VOL2 item 42 |
| **RES.177** | Item 43 GraphRAG | Pipeline extracción entidades → Cypher → búsqueda paralela vector+grafo. | `core/memory_fabric/graphrag/` | RELAY_RESEARCH_VOL2 item 43 |
| **RES.178** | Item 41 DSPy Optimizer | Sustitución prompts estáticos por dspy.Signature + BootstrapFewShot/MIPRO local. | `core/prompt_evolution/` | RELAY_RESEARCH_VOL2 item 41 |
| **RES.179** | P19 Long-Term Identity | Ed25519 por agente + DID Documents + historial HMAC encadenado. | `agent_registry/identity/` | RELAY_RESEARCH_VOL1 item 19 |
| **RES.180** | Item 64 HITL Telegram/WA | Pausa ejecución + token único + botones Aprobar/Rechazar + workflow.signal(). | `governance_engine/hitl/` | RELAY_RESEARCH_VOL2 item 64 |
| **RES.181** | Item 57 Temporal.io Workflows | Workflows de larga duración tolerantes a fallos. Decoradores Temporal Python. | `core/workflow_engine/` | RELAY_RESEARCH_VOL2 item 57 |
| **RES.182** | Item 58 MCTS Planner | MCTSPlanner: árbol de decisión cognitivo. Value network simulada. Retropropagación semántica. | `core/planner/` | RELAY_RESEARCH_VOL2 item 58 |
| **RES.183** | Item 07 WhatsApp Runtime | WhatsAppRuntime + WhatsAppSession. Webhook Meta Graph API v20+. X-Hub-Signature-256. | `providers/omnichannel/whatsapp/` | RELAY_RESEARCH_VOL1 item 07 |
| **RES.184** | Item 08 Telegram Agents | TelegramFederatedRuntime. Comandos /status /approve /delegate /freeze. Integración HITL. | `providers/omnichannel/telegram/` | RELAY_RESEARCH_VOL1 item 08 |
| **RES.185** | Item 09 Voice Layer | VoiceCognitiveLayer STT+LLM+TTS <400ms. VAD Silero. Manejo interrupciones. | `providers/voice/` | RELAY_RESEARCH_VOL1 item 09 |

---

## BLOQUE 3 — PRIORIDAD B2 (RES.186–200) — Investigación + implementación

| RES | Item | Descripción breve | Carpeta | Fuente |
|---|---|---|---|---|
| **RES.186** | Item 53 Diarización Voz | Whisper + PyAnnote. Separación por locutor. Transcripciones atribuidas. | `providers/voice/diarization/` | VOL2 item 53 |
| **RES.187** | Item 54 TTS Neuronal | Kokoro-82M o XTTS v2. Chunks semánticos. Streaming audio. | `providers/voice/tts/` | VOL2 item 54 |
| **RES.188** | Item 36 Audio WebRTC | aiortc + FastAPI. Buffers PCM. clear_buffer ante interrupciones. <400ms. | `providers/voice/` | VOL2 item 36 |
| **RES.189** | Item 37 Webhooks Omnicanal | Ingress Controller. Meta Graph API. X-Hub-Signature-256. Formato unificado MPAT. | `providers/omnichannel/` | VOL2 item 37 |
| **RES.190** | Item 60 SecretManager | AES-GCM + PBKDF2. Inyección efímera en sandbox. Limpieza inmediata post-ejecución. | `core/secrets/` | VOL2 item 60 |
| **RES.191** | Item 47 Self-Healing | Bucle while-try-except N intentos. Captura stack trace. Prompt reflexión crítica. | `core/self_healing/` | VOL2 item 47 |
| **RES.192** | Item 63 Hot-Reload | importlib.invalidate_caches + import_module. Watcher de ~/.mpat/skills. Reemplazo en caliente. | `core/hot_reload/` | VOL2 item 63 |
| **RES.193** | Item 55 Streaming Tool Calls | Parser JSON parcial en streaming tokens. Arranque skill antes de fin de generación. | `core/tool_streaming/` | VOL2 item 55 |
| **RES.194** | Item 62 DAG Runtime Mutation | NetworkX DAG. add_node/modify_edge en runtime. Re-planificación adaptativa. | `core/planner/dag_runtime/` | VOL2 item 62 |
| **RES.195** | Item 61 LongLLMLingua | Compresión semántica de contexto. Perplejidad + poda quirúrgica de tokens. 4x más info. | `core/context_optimizer/` | VOL2 item 61 |
| **RES.196** | Item 04 Runtime Optimizer | RuntimeOptimizer métricas: latencia, cache hit rate, pool miss rate. Auto-tune. | `core/runtime_optimizer/` | VOL1 item 04 |
| **RES.197** | Item 12 Recursive Planner | RecursivePlanningAgent HTN. Pool sub-agentes especializados. Delegación A2A con presupuesto. | `core/planner/recursive/` | VOL1 item 12 |
| **RES.198** | Item 17 Skill Discovery | Detección de gap. Búsqueda catálogo MCP 2.0. Generación autónoma. Validación sandbox. | `core/skill_discovery/` | VOL1 item 17 |
| **RES.199** | Item 65 Self-Rewarding | Agente Ejecutor + Agente Evaluador. Rúbrica numérica. Reescritura iterativa. | `core/self_rewarding/` | VOL2 item 65 |
| **RES.200** | Item 48 Datos Sintéticos | Extracción de logs exitosos. Mutación evolutiva. JSONL para Unsloth/LLaMA-Factory. | `core/synthetic_data/` | VOL2 item 48 |

---

## BLOQUE 4 — PRIORIDAD C (RES.201–220) — Frontera avanzada

| RES | Item | Descripción breve | Carpeta | Fuente |
|---|---|---|---|---|
| **RES.201** | Item 49 A2A Consensus | Protocolo Raft adaptado. Sincronización de estado entre agentes distribuidos. | `ecosystem/federation/` | VOL2 item 49 |
| **RES.202** | Item 50 Reputación Ed25519 | Libro contable local. Score de confianza. Firma por agente en cabeceras. | `ecosystem/reputation/` | VOL2 item 50 |
| **RES.203** | Item 39 Firecracker ampliado | Subsistema Rust/Go socket UNIX. MicroVM <10ms. Ampliación de RES.159. | `runtimes/firecracker/` | VOL2 item 39 |
| **RES.204** | Item 40 WASM Runtime | Compilador JIT wasm32-wasi. Wasmtime SDK Python. Restricción WASI de disco/red. | `runtimes/wasm/` | VOL2 item 40 |
| **RES.205** | Item 56 Tensor Parallelism | ExLlamaV2/vLLM local cluster. Fragmentación pesos entre nodos LAN. torch.distributed. | `providers/distributed_inference/` | VOL2 item 56 |
| **RES.206** | Item 66 Speculative Decoding | Draft Model (0.5B) + Target Model (7B). Verificación paralela. 2-3x tokens/s. | `core/inference/speculative/` | VOL2 item 66 |
| **RES.207** | Item 59 Cifrado Homomórfico | TenSEAL + Paillier. Embeddings cifrados. Similitud coseno sobre datos cifrados. | `ecosystem/federation/crypto/` | VOL2 item 59 |
| **RES.208** | Item 67 Libp2p P2P | libp2p Python/Go. DHT descubrimiento nodos. STUN/TURN relay. Payloads cifrados. | `ecosystem/p2p/` | VOL2 item 67 |
| **RES.209** | Item 22 Federated Mesh | Red MPAT instancias P2P. A2A Consensus + Cifrado Homomórfico + Tensor Parallelism. | `ecosystem/federation/mesh/` | VOL1 item 22 |
| **RES.210** | Item 13 Synthetic Teams | SyntheticTeam: roles PM/ARCH/DEV/QA/DOCS. Workflow PRD→Arch→Impl→Test→Docs. Git integration. | `core/synthetic_teams/` | VOL1 item 13 |
| **RES.211** | Item 23 Browser Operators | Playwright async. VLM Set-of-Mark prompting. MCTS navegación multi-paso. | `providers/browser/` | VOL1 item 23 |
| **RES.212** | Item 68 GUI Agent OS | VLM + PyAutoGUI. Set-of-Mark coordenadas. Automatización interfaces sin API. | `providers/gui_agent/` | VOL2 item 68 |
| **RES.213** | Item 38 Visión Social | OpenCV 1FPS. Embeddings visuales + audio. VLM contexto largo. TikTok/Instagram. | `providers/vision/` | VOL2 item 38 |
| **RES.214** | Item 70 Mirror Agents | Suite stress testing. Agentes espejo con perfiles de comportamiento. Ataques controlados. | `tests/stress/` | VOL2 item 70 |
| **RES.215** | Item 35 Synthetic Orgs | Organizaciones de agentes autónomos. A2A Economy + A2A Consensus + Audit. | `ecosystem/synthetic_orgs/` | VOL1 item 35 |

---

## BLOQUE 5 — PRIORIDAD C2 (RES.216–230) — Largo plazo

| RES | Item | Descripción breve | Fuente |
|---|---|---|---|
| **RES.216** | Item 06 Prompt Evolution | DSPy Signatures + MIPRO. A/B testing prompts. Versionado semántico. | VOL1 item 06 |
| **RES.217** | Item 11 Code Refactoring | AST parsing tree-sitter. Métricas ciclomáticas. SWE-agent pattern. | VOL1 item 11 |
| **RES.218** | Item 14 AI DevOps | CI/CD agentic. Deploy+rollback automático. Alertas vía WA/Telegram. | VOL1 item 14 |
| **RES.219** | Item 21 AI Scheduler | Priorización: urgencia × importancia × energía × dependencias. Google Calendar MCP. | VOL1 item 21 |
| **RES.220** | Item 24 Multimodal | Pipeline paralelo texto+imagen+audio asyncio. Fusión embeddings multimodal. | VOL1 item 24 |
| **RES.221** | Item 25 Cognitive Security | OWASP LLM Top10. Input sanitization. Output validation. Red team con Mirror Agents. | VOL1 item 25 |
| **RES.222** | Item 26 Research Agent | Browser Operator + GraphRAG + Multi-source synthesis + Citation tracking. | VOL1 item 26 |
| **RES.223** | Item 29 Digital Twin | CognitiveTwin: perfil cognitivo + Long-term Memory + Self-Rewarding. | VOL1 item 29 |
| **RES.224** | Item 30 Ambient AI | Event-driven triggers. Proactive suggestions. Background idle processing. | VOL1 item 30 |
| **RES.225** | Item 32 Knowledge Distillation | QLoRA + Unsloth. Domain-specific fine-tuning. Quality gating Self-Rewarding. | VOL1 item 32 |
| **RES.226** | Item 33 Edge Federation | GGUF Q4 Raspberry Pi. Federated Learning gradientes. Edge-to-cloud routing. | VOL1 item 33 |
| **RES.227** | Item 34 Workflow Evolution | DAG evolutivo. Tournament selection. A/B testing workflows en paralelo. | VOL1 item 34 |
| **RES.228** | Item 10 Social Agents | SocialMediaAgent Instagram/TikTok. VLM + content moderation guardrails. | VOL1 item 10 |
| **RES.229** | Item 18 Marketplace | Directorio AgentCards + pricing dinámico + integración Reputación (RES.202). | VOL1 item 18 |
| **RES.230** | Item 27 Reputation System | Libro contable local + Ed25519 atribución + integración A2A Consensus. | VOL1 item 27 |

---

## RESUMEN ESTADÍSTICO

| Bloque | Rango RES | Cantidad | Prioridad |
|---|---|---|---|
| 0 — Activo | RES.163 | 1 | AHORA |
| 1 — Bloqueantes | RES.164–170 | 7 | A |
| 2 — Independientes | RES.171–185 | 15 | B |
| 3 — Implementación | RES.186–200 | 15 | B2 |
| 4 — Frontera avanzada | RES.201–215 | 15 | C |
| 5 — Largo plazo | RES.216–230 | 15 | C2 |
| **TOTAL** | **RES.163–230** | **68 items encolados** | — |

---

*RESOLUTION_QUEUE_MPAT4.md · docente_AGT_2026 · 2026-05-23*
*que has usado el formato de razonamiento adaptado por AGT*
