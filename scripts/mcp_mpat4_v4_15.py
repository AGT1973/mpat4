"""
MCP MPAT4 — Router de Infraestructura
## Autor: MPAT4 Team
## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida
## Versión: V4_15

Decorador del MCP Google Drive para MPAT4.
El alumno dice "guardar en contracts/" y este MCP:
1. Resuelve el nombre semántico → folder_id real
2. Determina el contentMimeType correcto según extensión
3. Devuelve el payload completo listo para Google Drive:create_file
4. Aplica todas las reglas MPAT4 automáticamente

El alumno NUNCA maneja IDs ni parámetros de Drive directamente.
Si el docente reorganiza carpetas, solo edita FOLDER_IDS — el skill no cambia.

Stack V4_15: Python · Rust · Node.js (investigación) · PyO3 (FFI)
"""

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent


FOLDER_IDS: dict[str, str] = {
    "mpat/":                                                    "1iLTAT03K0eOjGJr0MtZN57hhGp4Ztyks",
    "mpat/tools/":                                              "1bj3eHn0CSuE_CTGjJ3pG0lGtcVXYmtPg",
    "mpat/tools/skills/":                                       "1rrDNblne6P_IwpCnDfmAHKen4KUuua4f",
    "mpat/tools/mcps/":                                         "1kNWfVtJ2MSLyG7pgYXeIP-oipOCVdC-b",
    "mpat/mpat3/":                                              "1vy_pTgB1UIfDQd3UMpO-XwYvZyt2KAoM",
    "mpat/mpat4/":                                              "1gQNxSlp92RpVIfzvyU66czHxLv1sqSqI",

    # Core Infrastructure & Standards
    "mpat/mpat4/contracts/":                                    "1589CC4tPfBkCUndlsVQeT9c9aYTSeaM0",
    "mpat/mpat4/schemas/":                                      "1N_u01JXjeMlMkNbk7GvV6snQTtnpOipG",
    "mpat/mpat4/resolutions/":                                  "1hRfjnUkOyfnfqxLEfBM0CWLLnDBi3GQU",
    "mpat/mpat4/artifacts/":                                    "1Artfcts4x8F-Ej84bN1yyJSzmr7zDCTVArt",
    "mpat/mpat4/deprecated/":                                   "14b47yd91-ebxV_rp_HVkndp0JKKthF2m",

    # Relay System
    "mpat/mpat4/relay/":                                        "1c3CP8dM19BGyjOlI8TadmyL1KtV_Tlte",
    "mpat/mpat4/relay/active/":                                 "PENDIENTE_CREAR",
    "mpat/mpat4/relay/temporal/":                               "1QehAmh2U7brtnHMDYRuR-SQUDCJyPJVu",
    "mpat/mpat4/relay/pointer/":                                "1GbQjZVtsISEYvTe7KiYw9DCwVF3ZU7pW",
    "mpat/mpat4/relay/docs/":                                   "1D8ze2AqZxf8Hx-CYtaI1FnQxiL9niPiq",
    "mpat/mpat4/relay/governance/":                             "1Qj9tA37vnJaoOcdCEttTierjR0-GZxOn",
    "mpat/mpat4/relay/memory/":                                 "145Frw-lSTmf-JxBvaXdXlpwXqD7swZfb",
    "mpat/mpat4/relay/protocol/":                               "1Cyv8eGdyBCwLgc-kCgUvjMP6QVfBwN8j",
    "mpat/mpat4/relay/runtime/":                                "1kpq7zKUlkSaCEhuYCi-V4-5Zqw62w4IU",

    # Docs
    "mpat/mpat4/docs/":                                         "1FlL7ACOo7o-KANItFWIBuJ62ULIHF_Oz",
    "mpat/mpat4/docs/public/":                                  "1Dv_zPx2NLe0lbZvIodIdZsM_2U0uxn7C",
    "mpat/mpat4/docs/internal/":                                "1GQ1Em8NmWO7F55lj3gp4OSqAke6iczFw",
    "mpat/mpat4/docs/business/":                                "1f5ysH7sUMCCtZQr2Mzr9PhXpfsf-41os",
    "mpat/mpat4/docs/architecture/":                            "1k0cHRbenqkDCPcJrcV01ofNtXMNqNSy8",

    # Research
    "mpat/mpat4/research/":                                     "1lrgXcd_s3CxF766lYkTwdoRIeJeUqsHk",
    "mpat/mpat4/research/papers/":                              "1Yi5Erc1drlLqqQe9gID2mmOMSYyrC9EV",
    "mpat/mpat4/research/benchmarks/":                          "1R0grNq4D42LeNtigOFiu-QHkElaWQ8-_",
    "mpat/mpat4/research/experiments/":                         "1ooeCILfKqnavAi6aeEkkKHoF2LdStLRn",
    "mpat/mpat4/research/futures/":                             "1E4i5Dc_JqMGZfF2LsVFPtxL2WIAqURw",
    "mpat/mpat4/research/tech_radar/":                          "PENDIENTE_CREAR",

    # Core Engine
    "mpat/mpat4/core/":                                         "1yvrUM4x8F-Ej84bN1yyJSzmr7zDCTVUC",

    # Core > Cognition
    "mpat/mpat4/core/cognition/":                               "1rexYAfWICisZs4B51V3nmh3gOStK6rWJ",
    "mpat/mpat4/core/cognition/kernel/":                        "1x4y8ijc6bybDOQlU1KwyXNevjLODax5g",
    "mpat/mpat4/core/cognition/agents/":                        "1FoQYxO9aBhpRGh8PEbiPG1Tblm1HbFTU",
    "mpat/mpat4/core/cognition/reasoning/":                     "1yIN_cbk2xOcNzhDJFySleJ-9VPYNkGdy",
    "mpat/mpat4/core/cognition/planning/":                      "1dzhGpyFfc6OBAcyZfJV9min3pZQsu718",
    "mpat/mpat4/core/cognition/context/":                       "1jh50caSvu7M2iSgrvw50oliPWBb-S7yN",
    "mpat/mpat4/core/cognition/orchestration/":                 "16Xis4pxNxLj30bMmqj-oOc2j7zFio1g2",
    "mpat/mpat4/core/cognition/cognition_runtime/":             "1mY4iE6lE6ZtN6ZlA6K9bHX__IXeL9aT",

    # Core > Event Bus
    "mpat/mpat4/core/event_bus/":                               "1lsaMPtDRFcXPGdBrZ8fAilsCNhpXZZiG",
    "mpat/mpat4/core/event_bus/brokers/":                       "1hJb0JSH_nmuaICohq3vOzfzRrbW67tlG",
    "mpat/mpat4/core/event_bus/streams/":                       "1vx-Kf63RxodTGMxgJHFhk-Fz1CUDC5ux",
    "mpat/mpat4/core/event_bus/subscriptions/":                 "1ZNbcafLl7DJPmHz5X6uyxC7dPt-GR6Or",
    "mpat/mpat4/core/event_bus/dead_letter/":                   "1rJiJAeVq_GJSoXJjJJRoNlymXgNYS6xS",
    "mpat/mpat4/core/event_bus/event_sourcing/":                "1dZ6ZlEjkYS5b6CDq7OzGnFHt03tw4OYX",
    "mpat/mpat4/core/event_bus/event_replay/":                  "1XbqroO_uFxfhSseBhDgtNwD8JHgedGMz",
    "mpat/mpat4/core/event_bus/persistence/":                   "1vfDSRAPMuV1Fx2c-CXNqETjAyE--W7Au",

    # Core > Governance
    "mpat/mpat4/core/governance/":                              "1nK9zcVKHoMx_qe16B_Lu4SyKZZPkS06S",
    "mpat/mpat4/core/governance/trust/":                        "1lgrbDbOodTtwj6xo-VwS5PS_KNJBbZP1",
    "mpat/mpat4/core/governance/permissions/":                  "1lyYWh3MqHHB9LBFGXZ3wS6e_vCLaOOw8",
    "mpat/mpat4/core/governance/policies/":                     "11plGvhc8XVpbBBp3aQfgcxUPn9hThL0x",
    "mpat/mpat4/core/governance/compliance/":                   "1YUORTymLRXppzdiLmtDBQN4NuPqa4mdp",
    "mpat/mpat4/core/governance/audit/":                        "1i4NwWGiZ4S2chV66YLt38EfLUX-lLCRy",
    "mpat/mpat4/core/governance/budget_engine/":                "1TDa4cUP4uNIDvZWJU181OKKE_g-4Qz-z",
    "mpat/mpat4/core/governance/runtime_limits/":               "1te_YxTo9iNXjQRbYEFcHbhossL3PMAqa",
    "mpat/mpat4/core/governance/tenant_isolation/":             "1K3WB9dGGF41OuVqVsP4Y0OmsQlRQZhmM",
    "mpat/mpat4/core/governance/economics/":                    "1nVwcG4cjnGcOaPkPKr00GpzSW0BpJqtx",

    # Core > Memory
    "mpat/mpat4/core/memory/":                                  "1CtYQRsZGh6r8UZPySpoHcnXbp0rLWgks",
    "mpat/mpat4/core/memory/indexes/":                          "PENDIENTE_CREAR",
    "mpat/mpat4/core/memory/episodic/":                         "1Jc9b7mH45q1q-YDROwGL7VzgULdDnBoN",
    "mpat/mpat4/core/memory/semantic/":                         "1nSa2FDsRBUXFjNDf-Jrjj1xWZ_kI8dId",
    "mpat/mpat4/core/memory/operational/":                      "1x90B5gm0EKWQ5u_ixOqw2ER4te3kiCmp",
    "mpat/mpat4/core/memory/graph_memory/":                     "1JyjVTJRtFKIhXY-Zkh9HtYWkv-hDCe9S",
    "mpat/mpat4/core/memory/relay_memory/":                     "19yKOls6ynSnk4pEbsvIYngB_DSv9CrX0",
    "mpat/mpat4/core/memory/retrieval/":                        "1VtvILIsXJ0qKG9xgTHyQ9qbPQ0F0Bt0K",
    "mpat/mpat4/core/memory/consolidation/":                    "1-pVc5U5qet2hXKdGh8iYPxgKJe_hXncx",
    "mpat/mpat4/core/memory/embedding_pipeline/":               "19I1Al5dHXGYVk1eaKShQ-6x_s_7d1p7I",
    "mpat/mpat4/core/memory/governance_memory/":                "17sqF5G-NpfkQPL9Mhe73iZ1ikLqVZXkP",

    # Core > Observability
    "mpat/mpat4/core/observability/":                           "1r_cyX_YHtvLwzQZU59jZmkFh4e3MDjqf",
    "mpat/mpat4/core/observability/telemetry/":                 "1gO3UR89Gmfm4Yc9eEHnrvD015aSesTij",
    "mpat/mpat4/core/observability/tracing/":                   "12zkXBc4IDcZHmJuhRPNwORlE1LL1pCJo",
    "mpat/mpat4/core/observability/thought_trace/":             "1s9iPm9p-Ku-O6vItMK3zg6yVPbUCfZTf",
    "mpat/mpat4/core/observability/cognitive_metrics/":         "1EC5SXG-I6c5OZTwXo7D79UkONzQhf08_",
    "mpat/mpat4/core/observability/explainability/":            "11_-8eJ9BT62OD4EXSrx7926KuIBLKerY",
    "mpat/mpat4/core/observability/compliance_views/":          "13HEV0yRxhLiRebEe_TJsmiqYM1QjxmRe",
    "mpat/mpat4/core/observability/session_replay/":            "1cm1I971TCBwAPizjWePEDZnED37Vz1MK",

    # Core > Federation
    "mpat/mpat4/core/federation/":                              "1XZ_M7ShjoVYTAS-5foL6-dElFTzJywW7",
    "mpat/mpat4/core/federation/peer_discovery/":               "1cXCL9qb2vKbDlgZ0i0wxU_Z-2qA0T56O",
    "mpat/mpat4/core/federation/trust_exchange/":               "1ihVF_pp2c4__S8yrjuawBXIgUAg2PcdZ",
    "mpat/mpat4/core/federation/relay_exchange/":               "1y_40zCXjU_O-afmXH-Rci2qmh0LILV2n",
    "mpat/mpat4/core/federation/federated_memory/":             "1K64_2Yam1HjPH7h6SOI25V-3AYSaCtkZ",
    "mpat/mpat4/core/federation/cluster_sync/":                 "1yaD23F6npWM3G--HEFM87znQusfsbUH7",
    "mpat/mpat4/core/federation/remote_execution/":             "1td9JiwWfZqL1q9_lWpdRTlq6sMfItJhd",

    # Core > Execution Graph
    "mpat/mpat4/core/execution_graph/":                         "1XY8JEOFPc-scoUCGgBkwEpVann64MvA3",
    "mpat/mpat4/core/execution_graph/dag_engine/":              "1JbDnhKG7uSAMEZRxH74thpHvZSj10WGZ",
    "mpat/mpat4/core/execution_graph/task_router/":             "1ME1GLPJwor15zAAlbvx5T_9sm_Xy7ahr",
    "mpat/mpat4/core/execution_graph/distributed_execution/":   "1871jKeVGkb44O6moUpR7WCPJ1pTA2ymk",
    "mpat/mpat4/core/execution_graph/planner/":                 "1nK5nLdIY8YZUVU2soomq6qA5ikh0X7Qk",

    # Core > Runtime
    "mpat/mpat4/core/runtime/":                                 "14tSLEH9_Ekt2VkXM8e-UDnej_WX1a80f",
    "mpat/mpat4/core/runtime/hypervisor/":                      "11h8exsjcf-FGdJn1rwc1P47wCoDyyD51",
    "mpat/mpat4/core/runtime/microvm/":                         "1mDD0-Ctsi8tJEdloNDIq8pstyr1hyB4g",
    "mpat/mpat4/core/runtime/unikernel/":                       "1QTiUeExLZIXg8aJw0ggv0T8Z1Fo26fw0",
    "mpat/mpat4/core/runtime/hydration/":                       "1AD62Y5_pSG8hi1Q5H365dElEqF0Zr5yS",
    "mpat/mpat4/core/runtime/scheduler/":                       "1CGdFxf0HfoRNqQ0ZtYVIkq-GYnjjM_rz",
    "mpat/mpat4/core/runtime/migration/":                       "1LNOoIaEn14XQF81eU08YtC4w3XC7mEu0",
    "mpat/mpat4/core/runtime/sandbox/":                         "1gUZ_da4ue7RXc_ahpyEgIBRQeSoI_GGt",
    "mpat/mpat4/core/runtime/runtime_state/":                   "1-erBNudRUxhTmn6J_FSFZsqg6gotkmdW",

    # Core > Sandboxing
    "mpat/mpat4/core/sandboxing/":                              "1Vw4UP8u6SgXh_fAG8CeEWKfmotV4lBpL",
    "mpat/mpat4/core/sandboxing/firecracker/":                  "1QNV_4orKoXKa9ElbLKxDeMcLFN-DXY5p",
    "mpat/mpat4/core/sandboxing/gvisor/":                       "11fZXrIaBhRLGhW7sauLMXsWx8m4bF73V",
    "mpat/mpat4/core/sandboxing/libkrun/":                      "1Xh1vMmRH8_9GF8hCaafJKD9USBlY6Iij",
    "mpat/mpat4/core/sandboxing/seccomp/":                      "14hDKdWPRPE1P1uxuUfwsxPSJJmL4Qq3D",
    "mpat/mpat4/core/sandboxing/network_policies/":             "1OZA4Q8cta6cTIrM38KRyPjCHb-bvv3w3",
    "mpat/mpat4/core/sandboxing/filesystem_policies/":          "1ptUQDpRA21o1yKIa-KaZO8REg6UcDoaE",

    # Core > Rust & Node Paths
    "mpat/mpat4/core/rust/":                                    "PENDIENTE_CREAR",
    "mpat/mpat4/core/rust/parsers/":                            "PENDIENTE_CREAR",
    "mpat/mpat4/core/rust/codecs/":                             "PENDIENTE_CREAR",
    "mpat/mpat4/core/rust/hot_paths/":                          "PENDIENTE_CREAR",
    "mpat/mpat4/core/rust/ffi_bridges/":                        "PENDIENTE_CREAR",
    "mpat/mpat4/core/rust/types/":                              "PENDIENTE_CREAR",
    "mpat/mpat4/core/node_research/":                           "PENDIENTE_CREAR",

    # Providers
    "mpat/mpat4/providers/":                                    "17LCBYsOzjqnCYvru38FnytqH3E8h6Okl",
    "mpat/mpat4/providers/ollama/":                             "1NTMYJoRNrO2iERWTwpfa9Xv7kPEW7poc",
    "mpat/mpat4/providers/openai/":                             "1s0aT0JUiTyOyj8FwYdaZb09bHX__IXeL",
    "mpat/mpat4/providers/anthropic/":                          "PENDIENTE_CREAR",
    "mpat/mpat4/providers/gemini/":                             "1EXfRF-NVAecktdQ-dulkJ58n7mSkyb57",
    "mpat/mpat4/providers/deepseek/":                           "1lAE-pPJVYSzVPXjgLETlQ8bT5SsCWM21",
    "mpat/mpat4/providers/nanobanana/":                         "1DO8AcIj49dm4VLYzJBOWhk4PyFJ0O72I",
    "mpat/mpat4/providers/stability/":                          "1YmaXGpY9x3fYij7FRfUKCq0CY09l7s3e",
    "mpat/mpat4/providers/local_models/":                       "11HhIfWWl8y6iyo-VazBcFysTFw42sIc4",
    "mpat/mpat4/providers/provider_routing/":                   "1IPIxRxkNzWxHnRK8l11ji44YBKOvF2_u",
    "mpat/mpat4/providers/provider_health/":                    "1huEJnticCS8ePftJjWKwqRRash91iVOF",
    "mpat/mpat4/providers/cost_engine/":                        "1LWhd8higxbunCM2fY1sF1fqCJTh6gJJB",

    # Ecosystem
    "mpat/mpat4/ecosystem/":                                    "170be8bj51aAvByQO-fc7GYDkIKKAwPrM",
    "mpat/mpat4/ecosystem/skills/":                             "1-iKL2tvyEuv_TL6YGWsRtuQBQKuI0iLb",
    "mpat/mpat4/ecosystem/skills/personal/":                    "18V76mmCcLu1xySE2-y4Za3_4KmQ74_ye",
    "mpat/mpat4/ecosystem/skills/team/":                        "1kdp45-NR-_nZh9x1pGEKpDPdLHkf-wMR",
    "mpat/mpat4/ecosystem/skills/enterprise/":                  "1KFznnjqaE5C8lYT85USUzktYwZ-S4pR6",
    "mpat/mpat4/ecosystem/skills/shared/":                      "1OMcHvFj5miF2f0qxVwnGwelieV9AjI2s",
    "mpat/mpat4/ecosystem/skills/sandboxed/":                   "1KAEdqYnzFdHCEdPP7z8TG3R7YZgIUmAU",
    "mpat/mpat4/ecosystem/capabilities/":                       "1XCHU8Kxv87G0oGpOrOiUmcTzOUYhFiO_",
    "mpat/mpat4/ecosystem/connectors/":                         "1yfQYyKEiUszfow0vAIYdJ-mN7yY6mmyI",
    "mpat/mpat4/ecosystem/manifests/":                          "1CG_j3KRQrWAtvfhCGVDNkyStGUqPpfCX",
    "mpat/mpat4/ecosystem/registries/":                         "1kzdcLP3wsCZqzdaZcdy5wl32p6FlxNYa",
    "mpat/mpat4/ecosystem/registries/agent_registry/":          "1tixEUJvuGRr_G39cqa6RUswG5_EbycOb",
    "mpat/mpat4/ecosystem/registries/skill_registry/":          "1rSQM2Ut9GQqcTiZGAsjm2YdlxY48c3hX",
    "mpat/mpat4/ecosystem/registries/tenant_registry/":         "1zQr_Zzw__S3sd5hVpdIm4J09hUFT8HjW",
    "mpat/mpat4/ecosystem/cards/":                              "1tcCx7DfhqFg5bYcMi3Y2VdD5x9aVymS1",
    "mpat/mpat4/ecosystem/cards/agent_cards/":                  "1w2vmbb5o0fzGq4ag83PVium6XHyaTAId",
    "mpat/mpat4/ecosystem/cards/skill_cards/":                  "1E2hPYFUWR9Taekl39AAYWYsVTJqYmHnM",
    "mpat/mpat4/ecosystem/cards/tenant_cards/":                 "1aRDJA0-Eoq2mRjqAf63XzJotwHF5AmHe",
    "mpat/mpat4/ecosystem/discovery/":                          "1HFm51PBnzGGlKTtc1URU1q9SQ_hYC_PB",

    # Education
    "mpat/mpat4/education/":                                    "1wSoBpZi8pl22n9a4oisFp5vjCXGTcNab",
    "mpat/mpat4/education/student_relays/":                     "1SiT9S3vUYR6TlFvsryXKTEiSyg7LaT_u",
    "mpat/mpat4/education/lab_guides/":                         "1C4efPjp5LoMqNCzzW6HRr42Mh1tzW4rs",
    "mpat/mpat4/education/teaching_material/":                  "1pWgHvn8oPV3pfkQ1A7vKUFxY-R1ytYy0",
    "mpat/mpat4/education/research_tracks/":                    "1YZzoMjXoTLuTRoRdXqtrSweEdkwy3HPj",
    "mpat/mpat4/education/investigation_gaps/":                 "1dA11Af77qVeEA3r3khv9ua6lzv3S5Ln8",
    "mpat/mpat4/education/evaluation/":                         "1cAThYUCyh4M_XDlLsHdBvOndOO1HbpxA",

    # Tests
    "mpat/mpat4/tests/":                                        "1WjhY2Ch5YHsKlmVNFczFyownqOkfbnRO",
    "mpat/mpat4/tests/unit/":                                   "1Ngc-824Is0PUEFuJV6v9PoHgzNa7ONKO",
    "mpat/mpat4/tests/integration/":                            "1R_OFbcKlKy2TNueWTnl3hJATfsVaFWx8",
    "mpat/mpat4/tests/runtime/":                                "1jEzcWCoVB3gDXnHF_kcwMq1CM2zGAnt5",
    "mpat/mpat4/tests/security/":                               "1uRHb04rAUZ6oN3SeswBNv3vbzL8_pezd",

    # Deployment
    "mpat/mpat4/deployment/":                                   "1l4-fIdx2UAYbRDcIV5a23-bDYfdET8Hs",
    "mpat/mpat4/deployment/edge/":                              "1iV9G8gfxN6WNcumh1ZpwXzJnRE5n3NqK",
    "mpat/mpat4/deployment/lab/":                               "1yE8bQ9OC6BaeAZPcS1BGqsfBKpJOgZlG",
    "mpat/mpat4/deployment/single_node/":                       "12bnnclV7Xi4WhoyYSLuSQ6TxZbcsNB01",
    "mpat/mpat4/deployment/cluster/":                           "1aHNfbWu-pklclZPhXBp3YkvtAdtb4jG1",
    "mpat/mpat4/deployment/bare_metal/":                        "1d9zo6hZcJhUwKVbx13UL6pe_dRvTOi1d",
    "mpat/mpat4/deployment/latam_low_resource/":                "1FWlJPS5f976Qsum6d4Qox44L4VfAZCdj",
    "mpat/mpat4/deployment/university/":                        "17qYRFeP8g17L3flcoimevjSrfR24VZUK",

    # System State
    "mpat/mpat4/system_state/":                                 "1RaDO7KViCevZXlw0rEwdCaTlt17aMUgx",
    "mpat/mpat4/system_state/runtime/":                         "1ZSBCHfImS6PZCuSWvI8_DLea54zZhjJp",
    "mpat/mpat4/system_state/governance/":                      "1nNqqXPo32NsQqFSgprQh-E9yDxjMmNch",
    "mpat/mpat4/system_state/relay/":                           "1SiT9S3vUYR6TlFvsryXKTEiSyg7LaT_u",
    "mpat/mpat4/system_state/cluster/":                         "19ZMDwbP9vEdZQHyH4jkbDbEqfwQfXuWY",
    "mpat/mpat4/system_state/tenants/":                         "15OkOAVrUQaJMapImCYcYv62QmGnFXxqA",

    # Scripts
    "mpat/mpat4/scripts/":                                      "17Fy3Ya8TQWh2uzhSHkusRh577InU_Bvl",
    "mpat/mpat4/scripts/bootstrap/":                            "1r8Jt9H5nkO5HdqKE219ZOIFQtn_nJAlI",
    "mpat/mpat4/scripts/migration/":                            "1WNkBmzJvV1p655zCWJrTC8O9REE8GOvF",
    "mpat/mpat4/scripts/maintenance/":                          "13qOUCKM_TQqiXsRjv4-0rzyn-sxbuefA",
}

MIME_TYPES: dict[str, str] = {
    "md":    "text/plain",
    "skill": "text/plain",
    "yaml":  "text/plain",
    "toml":  "text/plain",
    "txt":   "text/plain",
    "py":    "text/x-python",
    "rs":    "text/x-rustsrc",
    "json":  "application/json",
    "html":  "text/html",
    "css":   "text/css",
    "js":    "text/javascript",
}

server = Server("mcp-mpat4")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="prepare_save",
            description=(
                "TOOL PRINCIPAL. El alumno dice 'guardar en docs/' y este tool devuelve "
                "el payload completo listo para llamar a Google Drive:create_file. "
                "Incluye: parentId (folder_id real), contentMimeType correcto, title, "
                "disableConversionToGoogleType:true, y el encabezado MPAT4 obligatorio. "
                "Claude copia el drive_payload y lo pasa directo al MCP Drive. "
                "Acepta rutas cortas ('contracts/') o completas ('mpat/mpat4/contracts/'). "
                "Si la carpeta es PENDIENTE_CREAR: devuelve instrucciones para crearla."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Ruta destino. Ej: 'contracts/', 'relay/temporal/', 'core/memory/'"},
                    "filename": {"type": "string", "description": "Nombre sin extensión. Ej: 'CONTRACT_memory_V1'"},
                    "extension": {
                        "type": "string",
                        "description": "Extensión del archivo",
                        "enum": ["md", "py", "rs", "json", "yaml", "toml", "skill", "txt", "html", "css", "js"]
                    }
                },
                "required": ["path", "filename", "extension"]
            }
        ),
        Tool(
            name="resolve_path",
            description="Resuelve una ruta semántica MPAT4 a su folder_id real de Google Drive.",
            inputSchema={
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        ),
        Tool(
            name="list_paths",
            description="Lista todas las rutas disponibles. Prefijo opcional para filtrar.",
            inputSchema={
                "type": "object",
                "properties": {"prefix": {"type": "string"}}
            }
        ),
        Tool(
            name="get_module_paths",
            description="Retorna todas las rutas relacionadas a un módulo. Ej: 'memory', 'governance'.",
            inputSchema={
                "type": "object",
                "properties": {"module": {"type": "string"}},
                "required": ["module"]
            }
        ),
        Tool(
            name="get_stack_paths",
            description="Retorna rutas por stack: 'python', 'rust', 'ffi', 'node', 'investigacion'.",
            inputSchema={
                "type": "object",
                "properties": {"stack": {"type": "string"}},
                "required": ["stack"]
            }
        ),
        Tool(
            name="update_pending_id",
            description="Registra el ID real de una carpeta PENDIENTE_CREAR. Temporal hasta reinicio — avisar al docente.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "folder_id": {"type": "string"}
                },
                "required": ["path", "folder_id"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:

    def normalize_path(p: str) -> str:
        p = p.strip()
        if not p.endswith("/"):
            p += "/"
        if p in FOLDER_IDS:
            return p
        full = f"mpat/mpat4/{p}"
        if full in FOLDER_IDS:
            return full
        return p

    if name == "prepare_save":
        path = normalize_path(arguments.get("path", ""))
        filename = arguments.get("filename", "").strip()
        extension = arguments.get("extension", "").strip().lower()
        folder_id = FOLDER_IDS.get(path)

        if not folder_id:
            similar = [p for p in FOLDER_IDS if any(part in p for part in path.strip("/").split("/") if part)][:5]
            return [TextContent(type="text", text=json.dumps({
                "ok": False, "error": f"Ruta '{path}' no encontrada.", "similar": similar,
                "accion": "Usar list_paths() para ver rutas disponibles."
            }, indent=2, ensure_ascii=False))]

        if folder_id == "PENDIENTE_CREAR":
            return [TextContent(type="text", text=json.dumps({
                "ok": False, "path": path, "error": "PENDIENTE_CREAR",
                "accion": "1. Crear carpeta en Drive con mimeType application/vnd.google-apps.folder. "
                          "2. Llamar update_pending_id(path, nuevo_id). "
                          "3. Registrar ID en sección 2 del relay. 4. Avisar al docente."
            }, indent=2, ensure_ascii=False))]

        full_filename = filename if "." in filename else f"{filename}.{extension}"
        return [TextContent(type="text", text=json.dumps({
            "ok": True,
            "path": path,
            "filename": full_filename,
            "drive_payload": {
                "parentId": folder_id,
                "title": full_filename,
                "contentMimeType": MIME_TYPES.get(extension, "text/plain"),
                "disableConversionToGoogleType": True
            },
            "instruccion": f"Pasar drive_payload a Google Drive:create_file. "
                           f"Si '{full_filename}' ya existe en '{path}': renombrar original a '{full_filename}.old.{extension}' primero.",
            "encabezado_requerido": f"# {full_filename}\n## Autor: [ALUMNO_ID] · [FECHA]\n"
                                    f"## Módulo: [módulo] · Lenguaje: [{extension.upper()}] · Versión: V4_15\n"
                                    f"## Sistema: MPAT4 — Infraestructura Cognitiva Distribuida"
        }, indent=2, ensure_ascii=False))]

    elif name == "resolve_path":
        path = normalize_path(arguments.get("path", ""))
        folder_id = FOLDER_IDS.get(path)
        if folder_id and folder_id != "PENDIENTE_CREAR":
            return [TextContent(type="text", text=json.dumps({"ok": True, "path": path, "folder_id": folder_id}, indent=2))]
        elif folder_id == "PENDIENTE_CREAR":
            return [TextContent(type="text", text=json.dumps({"ok": False, "path": path, "error": "PENDIENTE_CREAR", "accion": "Crear carpeta y llamar update_pending_id."}, indent=2))]
        else:
            similar = [p for p in FOLDER_IDS if path.rstrip("/") in p][:5]
            return [TextContent(type="text", text=json.dumps({"ok": False, "path": path, "error": "No encontrada", "similar": similar}, indent=2))]

    elif name == "list_paths":
        prefix = arguments.get("prefix", "").strip()
        paths = {p: v for p, v in FOLDER_IDS.items() if p.startswith(prefix)} if prefix else FOLDER_IDS
        pending = [p for p, v in paths.items() if v == "PENDIENTE_CREAR"]
        return [TextContent(type="text", text=json.dumps({"total": len(paths), "pending_count": len(pending), "pending_paths": pending, "paths": paths}, indent=2))]

    elif name == "get_module_paths":
        module = arguments.get("module", "").strip().lower()
        paths = {p: v for p, v in FOLDER_IDS.items() if module in p}
        pending = [p for p, v in paths.items() if v == "PENDIENTE_CREAR"]
        return [TextContent(type="text", text=json.dumps({"module": module, "total": len(paths), "pending_count": len(pending), "paths": paths}, indent=2))]

    elif name == "get_stack_paths":
        stack = arguments.get("stack", "").strip().lower()
        stack_prefixes = {
            "rust": ["mpat/mpat4/core/rust/"],
            "ffi": ["mpat/mpat4/core/rust/ffi_bridges/"],
            "node": ["mpat/mpat4/core/node_research/"],
            "investigacion": ["mpat/mpat4/research/tech_radar/", "mpat/mpat4/research/"],
            "python": ["mpat/mpat4/core/", "mpat/mpat4/schemas/", "mpat/mpat4/contracts/"]
        }
        if stack not in stack_prefixes:
            return [TextContent(type="text", text=json.dumps({"ok": False, "error": f"Stack desconocido: {stack}", "valid": list(stack_prefixes.keys())}, indent=2))]
        paths = {}
        for prefix in stack_prefixes[stack]:
            for p, v in FOLDER_IDS.items():
                if p.startswith(prefix):
                    paths[p] = v
        if stack == "python":
            paths = {p: v for p, v in paths.items() if "rust" not in p and "node" not in p}
        pending = [p for p, v in paths.items() if v == "PENDIENTE_CREAR"]
        return [TextContent(type="text", text=json.dumps({"ok": True, "stack": stack, "total": len(paths), "pending_count": len(pending), "pending_paths": pending, "paths": paths}, indent=2))]

    elif name == "update_pending_id":
        path = normalize_path(arguments.get("path", ""))
        folder_id = arguments.get("folder_id", "").strip()
        if path not in FOLDER_IDS:
            return [TextContent(type="text", text=json.dumps({"ok": False, "error": f"Ruta {path} no existe."}, indent=2))]
        if FOLDER_IDS.get(path) != "PENDIENTE_CREAR":
            return [TextContent(type="text", text=json.dumps({"ok": False, "error": f"Ya tiene ID: {FOLDER_IDS[path]}"}, indent=2))]
        FOLDER_IDS[path] = folder_id
        return [TextContent(type="text", text=json.dumps({
            "ok": True, "path": path, "folder_id": folder_id,
            "advertencia": "TEMPORAL — actualizar FOLDER_IDS en mcp_mpat4.py permanentemente.",
            "accion_docente": f"Editar mcp_mpat4_v4_15.py: '{path}': '{folder_id}'"
        }, indent=2))]

    return [TextContent(type="text", text=json.dumps({"error": f"Tool desconocida: {name}"}))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp_mpat4",
                server_version="V4_15",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    import asyncio
    print("mcp cargando")
    asyncio.run(main())
