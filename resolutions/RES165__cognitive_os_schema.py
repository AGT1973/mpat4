"""
RES165__cognitive_os_schema.py
DESTINO FINAL: schemas/cognitive_os_schema.py
RES.165 - MPAT4 | Relay: RELAY_011 | 2026-05-23
Autor: cursos.agt.ia@gmail.com (docente_AGT_2026)
que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field




class ProcessState(str, Enum):
    SPAWNING   = "SPAWNING"
    ACTIVE     = "ACTIVE"
    SUSPENDING = "SUSPENDING"
    TERMINATED = "TERMINATED"




class ThreadState(str, Enum):
    READY     = "READY"
    RUNNING   = "RUNNING"
    WAITING   = "WAITING"
    COMPLETED = "COMPLETED"
    FAILED    = "FAILED"




class CognitiveSignal(str, Enum):
    COMPLETE   = "COMPLETE"
    SUSPEND    = "SUSPEND"
    RESUME     = "RESUME"
    FREEZE     = "FREEZE"
    BUDGET_LOW = "BUDGET_LOW"




class SchedulingPolicy(str, Enum):
    FIFO         = "fifo"
    PRIORITY     = "priority"
    ROUND_ROBIN  = "round_robin"
    BUDGET_URGENT = "budget_urgent"




class CognitiveThreadSchema(BaseModel):
    model_config = {"frozen": True}
    thread_id: str
    process_id: str
    tenant_id: str
    name: str
    state: ThreadState = ThreadState.READY
    tokens_consumed: int = 0
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    schema_version: str = "v4.0"




class CognitiveProcessSchema(BaseModel):
    model_config = {"frozen": True}
    pid: str
    tenant_id: str
    agent_id: str
    unikernel_id: str
    budget_tokens: int = Field(ge=0)
    tokens_consumed: int = Field(default=0, ge=0)
    budget_remaining: int = Field(ge=0)
    state: ProcessState = ProcessState.SPAWNING
    soul_md_loaded: bool = False
    thread_count: int = 0
    schema_version: str = "v4.0"




class IPCMessageSchema(BaseModel):
    model_config = {"frozen": True}
    from_pid: str
    to_pid: str
    message_type: str
    payload: dict[str, Any]
    sent_at: datetime
    schema_version: str = "v4.0"




class CognitiveSignalSchema(BaseModel):
    model_config = {"frozen": True}
    signal: CognitiveSignal
    target_pid: str
    sender_pid: Optional[str] = None
    reason: Optional[str] = None
    emitted_at: datetime
    schema_version: str = "v4.0"




class SchedulerStatsSchema(BaseModel):
    model_config = {"frozen": True}
    policy: SchedulingPolicy
    queued_processes: int
    active_processes: int
    total_budget: int
    allocated: int
    schema_version: str = "v4.0"




class OSStatsSchema(BaseModel):
    model_config = {"frozen": True}
    total_processes: int
    active_processes: int
    scheduler: SchedulerStatsSchema
    schema_version: str = "v4.0"




# Eventos emitidos en CognitiveEventMesh por el CognitiveOS
class ProcessSpawnedEventSchema(BaseModel):
    model_config = {"frozen": True}
    pid: str
    agent_id: str
    unikernel_id: str
    budget_tokens: int
    schema_version: str = "v4.0"




class ProcessTerminatedEventSchema(BaseModel):
    model_config = {"frozen": True}
    pid: str
    agent_id: str
    reason: str
    tokens_consumed: int
    schema_version: str = "v4.0"