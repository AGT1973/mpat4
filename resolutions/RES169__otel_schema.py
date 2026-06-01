"""
RES169__otel_schema.py
DESTINO FINAL: observability/otel_schema.py
RES.169 - MPAT4 | Relay: RELAY_015 | 2026-05-23
Autor: cursos.agt.ia@gmail.com (docente_AGT_2026)
que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field




class SpanStatus(str, Enum):
    OK    = "ok"
    ERROR = "error"




class AgentSpanSchema(BaseModel):
    """Ciclo completo de ejecución de un agente."""
    model_config = {"frozen": True}
    span_id: str
    parent_span_id: Optional[str] = None   # INV-OTEL.4: propagación de contexto
    tenant_id: str
    agent_id: str
    input_prompt: str = Field(max_length=2000)
    output_response: str = Field(default="", max_length=2000)
    tokens_consumed: int = 0
    latency_ms: float = 0.0
    status: SpanStatus = SpanStatus.OK
    error: Optional[str] = None
    recorded_at: str
    schema_version: str = "v4.0"




class ToolSpanSchema(BaseModel):
    """Invocación de una herramienta o skill."""
    model_config = {"frozen": True}
    span_id: str
    parent_span_id: Optional[str] = None
    tenant_id: str
    tool_name: str
    input_args: dict[str, Any] = Field(default_factory=dict)
    output_result: str = Field(default="", max_length=1000)
    latency_ms: float = 0.0
    success: bool = True
    tokens_consumed: int = 0
    error: Optional[str] = None
    recorded_at: str
    schema_version: str = "v4.0"




class LLMSpanSchema(BaseModel):
    """Llamada al modelo de lenguaje."""
    model_config = {"frozen": True}
    span_id: str
    parent_span_id: Optional[str] = None
    tenant_id: str
    model_id: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    temperature: float = 0.7
    finish_reason: str = "unknown"
    error: Optional[str] = None
    recorded_at: str
    schema_version: str = "v4.0"




class TracerConfigSchema(BaseModel):
    model_config = {"frozen": True}
    service_name: str = "mpat4-agent"
    otlp_endpoint: str = "http://localhost:4317"
    enable_console_exporter: bool = False
    audit_ledger_enabled: bool = True
    schema_version: str = "v4.0"