"""
T008__session_scheduler_schema_v4.py
DESTINO FINAL: schemas/session_scheduler_schema_v4.py
RES.163 - MPAT4 | Relay: RELAY_009 | 2026-05-23
Autor: cursos.agt.ia@gmail.com (docente_AGT_2026)
que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field




class SchedulerConfig(BaseModel):
    model_config = {"frozen": True}
    warm_pool_size: int = Field(default=5, ge=1, le=50,
                                 description="INV-WARM.1: tamano del warm pool por tenant")
    idle_ttl_seconds: float = Field(default=300.0, gt=0,
                                     description="INV-WARM.3: TTL de MicroVM ocioso en segundos")
    schema_version: str = "v4.0"




class WarmPoolEntry(BaseModel):
    model_config = {"frozen": True}
    unikernel_id: str
    tenant_id: str
    booted_at: datetime
    schema_version: str = "v4.0"




class WarmPoolState(BaseModel):
    model_config = {"frozen": True}
    tenant_id: str
    schema_version: str = "v4.0"
    available_unikernels: int
    target_pool_size: int
    last_replenished_at: datetime




class HydrationResult(BaseModel):
    model_config = {"frozen": True}
    success: bool
    session_id: str
    tenant_id: str
    schema_version: str = "v4.0"
    episodic_fragments_loaded: int = 0
    semantic_refs_loaded: int = 0
    policies_activated: int = 0
    hydration_ms: float = 0.0
    error: Optional[str] = None




class SessionLifecycleEvent(BaseModel):
    """Schema para eventos session.started y session.teardown en EventBusV4."""
    model_config = {"frozen": True}
    event_type: str  # "session.started" | "session.teardown"
    session_id: str
    tenant_id: str
    agent_id: str
    unikernel_id: str
    hydrated: bool = False
    budget_tokens: int
    reason: Optional[str] = None  # solo en teardown
    relay_export_required: bool = False
    schema_version: str = "v4.0"