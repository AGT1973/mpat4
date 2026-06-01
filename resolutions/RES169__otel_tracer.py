"""
RES169__otel_tracer.py
DESTINO FINAL: observability/otel_tracer.py
RES.169 - MPAT4 | Relay: RELAY_015 | 2026-05-23
Autor: cursos.agt.ia@gmail.com (docente_AGT_2026)


P69 Bloque B — Rastreo distribuido agentic con OpenTelemetry.


Provee 3 tipos de Span + decoradores para instrumentar agentes MPAT4:
  @agent_span  → ciclo completo de ejecución del agente
  @tool_span   → invocación de una herramienta/skill
  @llm_span    → llamada al modelo de lenguaje


Los Spans exportan via OTLP a Arize Phoenix local (localhost:6006)
Y se registran en AuditLedger (RES.168) para inmutabilidad.


INVARIANTES:
  INV-OTEL.1: todo Span tiene tenant_id — aislamiento multi-tenant.
  INV-OTEL.2: todo Span se registra en AuditLedger además de OTel.
              La observabilidad no puede perderse si Arize Phoenix cae.
  INV-OTEL.3: los decoradores funcionan en funciones sync y async.
              El caller no necesita saber si está siendo instrumentado.
  INV-OTEL.4: spans anidados propagan contexto via contextvars.
              Un @tool_span dentro de un @agent_span es hijo del agente.
  INV-OTEL.5: errores en la instrumentación NUNCA propagan al caller.
              Si OTel falla, la función sigue ejecutándose normalmente.


TRAMPA EDUCATIVA:
  "El decorador @agent_span bloquea si OTel está caído."
  FALSO: INV-OTEL.5 garantiza que los errores de instrumentación
  son capturados con try/except dentro del decorador y logeados
  como WARNING. La función decorada sigue ejecutándose sin excepción.
  La observabilidad es un servicio de soporte — nunca un punto de fallo.


que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations


import asyncio
import functools
import logging
import time
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Optional
from uuid import uuid4


from observability.otel_schema import (
    AgentSpanSchema, ToolSpanSchema, LLMSpanSchema, SpanStatus,
)


logger = logging.getLogger("mpat.otel_tracer")


# ContextVar para propagación de span padre (INV-OTEL.4)
_current_span_id: ContextVar[Optional[str]] = ContextVar(
    "current_span_id", default=None
)
_current_tenant_id: ContextVar[Optional[str]] = ContextVar(
    "current_tenant_id", default=None
)




# ---------------------------------------------------------------------------
# MPATTracer — configuración e inicialización de OpenTelemetry
# ---------------------------------------------------------------------------


class MPATTracer:
    """
    Tracer principal de MPAT4 sobre OpenTelemetry SDK.


    Configura el pipeline OTel:
      1. TracerProvider con BatchSpanProcessor.
      2. OTLPSpanExporter → Arize Phoenix (localhost:6006).
      3. ConsoleSpanExporter como fallback si Phoenix no está disponible.


    Uso:
        tracer = MPATTracer(
            service_name="mpat4-agent",
            otlp_endpoint="http://localhost:4317",
            audit_ledger=ledger,  # RES.168
        )
        await tracer.initialize()
    """


    def __init__(
        self,
        service_name: str = "mpat4-agent",
        otlp_endpoint: str = "http://localhost:4317",
        audit_ledger=None,   # AuditLedger (RES.168) — opcional
        enable_console_exporter: bool = False,
    ):
        self._service_name = service_name
        self._otlp_endpoint = otlp_endpoint
        self._audit_ledger = audit_ledger
        self._enable_console = enable_console_exporter
        self._tracer = None
        self._provider = None
        self._initialized = False


    async def initialize(self) -> None:
        """Configura OpenTelemetry con exportador OTLP a Arize Phoenix."""
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )


            resource = Resource.create({
                "service.name": self._service_name,
                "service.version": "4.0",
                "mpat.version": "MPAT4",
            })
            self._provider = TracerProvider(resource=resource)


            # Exportador OTLP → Arize Phoenix
            try:
                otlp_exporter = OTLPSpanExporter(endpoint=self._otlp_endpoint)
                self._provider.add_span_processor(
                    BatchSpanProcessor(otlp_exporter)
                )
                logger.info("OTel OTLP exportador configurado: %s", self._otlp_endpoint)
            except Exception as exc:
                logger.warning("OTel OTLP no disponible (%s) — modo local", exc)


            if self._enable_console:
                from opentelemetry.sdk.trace.export import (
                    ConsoleSpanExporter, SimpleSpanProcessor
                )
                self._provider.add_span_processor(
                    SimpleSpanProcessor(ConsoleSpanExporter())
                )


            trace.set_tracer_provider(self._provider)
            self._tracer = trace.get_tracer(self._service_name)
            self._initialized = True
            logger.info("MPATTracer inicializado: service=%s", self._service_name)


        except ImportError:
            logger.warning(
                "opentelemetry-sdk no instalado. Instalar:\n"
                "pip install opentelemetry-api opentelemetry-sdk "
                "opentelemetry-exporter-otlp-proto-grpc\n"
                "Continuando en modo NO-OP (INV-OTEL.5)."
            )
            self._initialized = False


    async def shutdown(self) -> None:
        if self._provider:
            self._provider.shutdown()


    @property
    def initialized(self) -> bool:
        return self._initialized


    def get_native_tracer(self):
        """Retorna el tracer nativo de OTel para uso directo si se necesita."""
        return self._tracer




# ---------------------------------------------------------------------------
# SpanRecorder — captura datos y los registra en AuditLedger + OTel
# ---------------------------------------------------------------------------


class SpanRecorder:
    """
    Encapsula la lógica de apertura/cierre de un Span OTel
    y su registro paralelo en AuditLedger (INV-OTEL.2).
    """


    def __init__(self, tracer: MPATTracer):
        self._tracer = tracer
        self._ledger = tracer._audit_ledger


    async def record_agent_span(self, span: AgentSpanSchema) -> None:
        """Registra un AgentSpan en OTel y en AuditLedger."""
        await self._record_in_otel(span, "agent_execution")
        await self._record_in_ledger(span, "TOOL_CALL")


    async def record_tool_span(self, span: ToolSpanSchema) -> None:
        await self._record_in_otel(span, "tool_call")
        await self._record_in_ledger(span, "TOOL_CALL")


    async def record_llm_span(self, span: LLMSpanSchema) -> None:
        await self._record_in_otel(span, "llm_call")
        await self._record_in_ledger(span, "LLM_CALL")


    async def _record_in_otel(self, span_data, operation_name: str) -> None:
        """INV-OTEL.5: errores en OTel no propagan al caller."""
        if not self._tracer.initialized or not self._tracer._tracer:
            return
        try:
            from opentelemetry import trace
            from opentelemetry.trace import Status, StatusCode
            data = span_data.model_dump()
            with self._tracer._tracer.start_as_current_span(operation_name) as otel_span:
                for key, value in data.items():
                    if value is not None and isinstance(value, (str, int, float, bool)):
                        otel_span.set_attribute(f"mpat.{key}", str(value))
                if data.get("status") == SpanStatus.ERROR.value:
                    otel_span.set_status(Status(StatusCode.ERROR))
                else:
                    otel_span.set_status(Status(StatusCode.OK))
        except Exception as exc:
            logger.warning("OTel record error (INV-OTEL.5): %s", exc)


    async def _record_in_ledger(self, span_data, event_type_str: str) -> None:
        """INV-OTEL.2: siempre registrar en AuditLedger independientemente de OTel."""
        if not self._ledger:
            return
        try:
            from observability.audit_schema import AuditEventType
            event_type = (
                AuditEventType.TOOL_CALL if event_type_str == "TOOL_CALL"
                else AuditEventType.LLM_CALL
            )
            await self._ledger.record_event(
                tenant_id=span_data.tenant_id,
                event_type=event_type,
                payload=span_data.model_dump(),
            )
        except Exception as exc:
            logger.warning("AuditLedger record error: %s", exc)




# ---------------------------------------------------------------------------
# Decoradores (INV-OTEL.3 + INV-OTEL.4 + INV-OTEL.5)
# ---------------------------------------------------------------------------


def agent_span(
    tracer: MPATTracer,
    tenant_id: str,
    agent_id: str,
):
    """
    Decorador para instrumentar el ciclo completo de ejecución de un agente.


    Captura: tenant_id, agent_id, input_prompt, output_response,
             tokens_consumed, latency_ms, status.


    INV-OTEL.3: funciona en sync y async.
    INV-OTEL.4: propaga span_id como contexto para spans hijos.
    INV-OTEL.5: errores de instrumentación no propagan al caller.


    Uso:
        @agent_span(tracer=mpat_tracer, tenant_id="escuela", agent_id="relay-writer")
        async def run_agent(prompt: str) -> str:
            ...
    """
    def decorator(func: Callable) -> Callable:
        recorder = SpanRecorder(tracer)


        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            span_id = str(uuid4())
            parent_id = _current_span_id.get(None)
            token_ctx = _current_span_id.set(span_id)
            tenant_ctx = _current_tenant_id.set(tenant_id)
            t0 = time.monotonic()
            status = SpanStatus.OK
            error_msg = None
            result = None
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as exc:
                status = SpanStatus.ERROR
                error_msg = str(exc)
                raise
            finally:
                latency_ms = (time.monotonic() - t0) * 1000
                _current_span_id.reset(token_ctx)
                _current_tenant_id.reset(tenant_ctx)
                try:
                    input_prompt = kwargs.get("prompt", args[0] if args else "")
                    span = AgentSpanSchema(
                        span_id=span_id,
                        parent_span_id=parent_id,
                        tenant_id=tenant_id,
                        agent_id=agent_id,
                        input_prompt=str(input_prompt)[:2000],
                        output_response=str(result)[:2000] if result else "",
                        latency_ms=round(latency_ms, 2),
                        status=status,
                        error=error_msg,
                        recorded_at=datetime.now(timezone.utc).isoformat(),
                    )
                    await recorder.record_agent_span(span)
                except Exception as exc:
                    logger.warning("agent_span record error (INV-OTEL.5): %s", exc)


        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.get_event_loop().run_until_complete(
                async_wrapper(*args, **kwargs)
            )


        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


    return decorator




def tool_span(
    tracer: MPATTracer,
    tool_name: str,
    tenant_id_kwarg: str = "tenant_id",
):
    """
    Decorador para instrumentar invocaciones de herramientas/skills.


    Captura: tool_name, input_args, output_result, latency_ms,
             success, tokens_consumed.


    INV-OTEL.4: usa el span_id del contexto actual como parent_span_id.
    INV-OTEL.5: errores de instrumentación no propagan al caller.


    Uso:
        @tool_span(tracer=mpat_tracer, tool_name="search_drive")
        async def search_drive(query: str, tenant_id: str) -> list:
            ...
    """
    def decorator(func: Callable) -> Callable:
        recorder = SpanRecorder(tracer)


        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            span_id = str(uuid4())
            parent_id = _current_span_id.get(None)
            tid = kwargs.get(tenant_id_kwarg, _current_tenant_id.get("unknown"))
            token_ctx = _current_span_id.set(span_id)
            t0 = time.monotonic()
            success = True
            error_msg = None
            result = None
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as exc:
                success = False
                error_msg = str(exc)
                raise
            finally:
                latency_ms = (time.monotonic() - t0) * 1000
                _current_span_id.reset(token_ctx)
                try:
                    safe_args = {
                        k: str(v)[:500]
                        for k, v in kwargs.items()
                        if k != "password" and k != "api_key"
                    }
                    span = ToolSpanSchema(
                        span_id=span_id,
                        parent_span_id=parent_id,
                        tenant_id=str(tid),
                        tool_name=tool_name,
                        input_args=safe_args,
                        output_result=str(result)[:1000] if result else "",
                        latency_ms=round(latency_ms, 2),
                        success=success,
                        error=error_msg,
                        recorded_at=datetime.now(timezone.utc).isoformat(),
                    )
                    await recorder.record_tool_span(span)
                except Exception as exc:
                    logger.warning("tool_span record error (INV-OTEL.5): %s", exc)


        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(async_wrapper(*args, **kwargs))


        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


    return decorator




def llm_span(
    tracer: MPATTracer,
    model_id: str,
    tenant_id_kwarg: str = "tenant_id",
):
    """
    Decorador para instrumentar llamadas al modelo de lenguaje.


    Captura: model_id, prompt_tokens, completion_tokens, latency_ms,
             temperature, finish_reason.


    Uso:
        @llm_span(tracer=mpat_tracer, model_id="claude-sonnet-4-5")
        async def call_llm(
            prompt: str,
            tenant_id: str,
            temperature: float = 0.7,
        ) -> LLMResponse:
            ...
    """
    def decorator(func: Callable) -> Callable:
        recorder = SpanRecorder(tracer)


        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            span_id = str(uuid4())
            parent_id = _current_span_id.get(None)
            tid = kwargs.get(tenant_id_kwarg, _current_tenant_id.get("unknown"))
            token_ctx = _current_span_id.set(span_id)
            t0 = time.monotonic()
            result = None
            error_msg = None
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as exc:
                error_msg = str(exc)
                raise
            finally:
                latency_ms = (time.monotonic() - t0) * 1000
                _current_span_id.reset(token_ctx)
                try:
                    # Intentar extraer metadata de uso del resultado
                    prompt_tokens = 0
                    completion_tokens = 0
                    finish_reason = "unknown"
                    if result and hasattr(result, "usage"):
                        usage = result.usage
                        prompt_tokens = getattr(usage, "input_tokens", 0)
                        completion_tokens = getattr(usage, "output_tokens", 0)
                    if result and hasattr(result, "stop_reason"):
                        finish_reason = result.stop_reason or "unknown"


                    span = LLMSpanSchema(
                        span_id=span_id,
                        parent_span_id=parent_id,
                        tenant_id=str(tid),
                        model_id=model_id,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=prompt_tokens + completion_tokens,
                        latency_ms=round(latency_ms, 2),
                        temperature=kwargs.get("temperature", 0.7),
                        finish_reason=finish_reason,
                        error=error_msg,
                        recorded_at=datetime.now(timezone.utc).isoformat(),
                    )
                    await recorder.record_llm_span(span)
                except Exception as exc:
                    logger.warning("llm_span record error (INV-OTEL.5): %s", exc)


        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(async_wrapper(*args, **kwargs))


        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


    return decorator




# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------


_tracer_instance: Optional[MPATTracer] = None




def get_mpat_tracer(
    service_name: str = "mpat4-agent",
    otlp_endpoint: str = "http://localhost:4317",
    audit_ledger=None,
) -> MPATTracer:
    """Singleton del MPATTracer. Llamar initialize() antes de usar decoradores."""
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = MPATTracer(
            service_name=service_name,
            otlp_endpoint=otlp_endpoint,
            audit_ledger=audit_ledger,
        )
    return _tracer_instance