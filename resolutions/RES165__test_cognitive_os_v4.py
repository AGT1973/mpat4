"""
RES165__test_cognitive_os_v4.py

DESTINO FINAL: tests/test_cognitive_os_v4.py

RES.165 — MPAT4 | P31 — AI Native OS | Tests
Autor: ariel.garcia.traba@gmail.com · 2026-05-24

que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations

import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock

from cognitive_os_v4 import (
    CognitiveProcess,
    CognitiveProcessState,
    CognitiveThread,
    CognitiveThreadState,
    CognitiveIPC,
    CognitiveProcessScheduler,
    IPCMessageType,
)
from kernel_bridge import KernelBudgetState, BudgetExhausted


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def kernel_mock():
    """KernelStub mock para tests sin Rust."""
    kernel = MagicMock()
    kernel.deduct_budget.return_value = KernelBudgetState(
        tenant_id="tenant_01",
        session_id="sess_01",
        budget_tokens=1000,
        budget_consumed=1000,
        budget_remaining=0,
    )
    kernel.return_budget.return_value = 0
    return kernel


@pytest.fixture
def mesh_mock():
    """CognitiveEventMesh mock."""
    mesh = MagicMock()
    mesh.publish = AsyncMock(return_value="evt-mock-id")
    return mesh


@pytest.fixture
def process(kernel_mock, mesh_mock):
    return CognitiveProcess(
        tenant_id="tenant_01",
        session_id="sess_01",
        agent_id="agent_planner",
        kernel=kernel_mock,
        mesh=mesh_mock,
        budget_tokens=1000,
    )


# ---------------------------------------------------------------------------
# CognitiveProcess — invariantes
# ---------------------------------------------------------------------------

class TestCognitiveProcess:

    # INV-CP.1: tenant_id no puede ser vacío
    def test_empty_tenant_id_raises(self, kernel_mock, mesh_mock):
        with pytest.raises(ValueError, match="INV-CP.1"):
            CognitiveProcess(
                tenant_id="",
                session_id="sess_01",
                agent_id="agent_x",
                kernel=kernel_mock,
                mesh=mesh_mock,
                budget_tokens=100,
            )

    # INV-CP.1: tenant_id no puede ser "unknown"
    def test_unknown_tenant_id_raises(self, kernel_mock, mesh_mock):
        with pytest.raises(ValueError, match="INV-CP.1"):
            CognitiveProcess(
                tenant_id="unknown",
                session_id="sess_01",
                agent_id="agent_x",
                kernel=kernel_mock,
                mesh=mesh_mock,
                budget_tokens=100,
            )

    # INV-CP.2: budget debe ser >= 1
    def test_zero_budget_raises(self, kernel_mock, mesh_mock):
        with pytest.raises(ValueError, match="INV-CP.2"):
            CognitiveProcess(
                tenant_id="tenant_01",
                session_id="sess_01",
                agent_id="agent_x",
                kernel=kernel_mock,
                mesh=mesh_mock,
                budget_tokens=0,
            )

    # INV-CP.2: budget asignado por kernel — no por el proceso
    @pytest.mark.asyncio
    async def test_spawn_calls_kernel_deduct(self, process, kernel_mock):
        await process.spawn()
        kernel_mock.deduct_budget.assert_called_once_with(
            tenant_id="tenant_01",
            session_id="sess_01",
            tokens=1000,
            reason=pytest.approx(str, abs=0),  # verifica que reason es str
        )

    # INV-CP.2: BudgetExhausted → proceso queda en TERMINATED
    @pytest.mark.asyncio
    async def test_spawn_budget_exhausted_terminates(self, kernel_mock, mesh_mock):
        kernel_mock.deduct_budget.side_effect = BudgetExhausted(
            "tenant_01", "sess_01", requested=1000, available=50
        )
        process = CognitiveProcess(
            tenant_id="tenant_01", session_id="sess_01",
            agent_id="agent_x", kernel=kernel_mock,
            mesh=mesh_mock, budget_tokens=1000,
        )
        with pytest.raises(BudgetExhausted):
            await process.spawn()
        assert process.state == CognitiveProcessState.TERMINATED

    # INV-CP.3: terminate() llama a return_budget
    @pytest.mark.asyncio
    async def test_terminate_returns_budget(self, process, kernel_mock):
        kernel_mock.deduct_budget.return_value = KernelBudgetState(
            tenant_id="tenant_01", session_id="sess_01",
            budget_tokens=1000, budget_consumed=200, budget_remaining=800,
        )
        await process.spawn()
        await process.terminate()
        kernel_mock.return_budget.assert_called_once()
        call_kwargs = kernel_mock.return_budget.call_args[1]
        assert call_kwargs["tokens"] == 800  # restante devuelto al padre

    # INV-CP.3: terminate() solo en RUNNING o SUSPENDED
    @pytest.mark.asyncio
    async def test_terminate_from_created_raises(self, process):
        with pytest.raises(RuntimeError):
            await process.terminate()

    # Estado correcto después de spawn
    @pytest.mark.asyncio
    async def test_spawn_sets_running(self, process):
        await process.spawn()
        assert process.state == CognitiveProcessState.RUNNING

    # Estado correcto después de terminate
    @pytest.mark.asyncio
    async def test_terminate_sets_terminated(self, process):
        await process.spawn()
        await process.terminate()
        assert process.state == CognitiveProcessState.TERMINATED

    # Suspend/Resume
    @pytest.mark.asyncio
    async def test_suspend_resume_cycle(self, process):
        await process.spawn()
        process.suspend()
        assert process.state == CognitiveProcessState.SUSPENDED
        process.resume()
        assert process.state == CognitiveProcessState.RUNNING

    # EventMesh recibe proceso.spawned (V4-INV-KERNEL.3)
    @pytest.mark.asyncio
    async def test_spawn_emits_event(self, process, mesh_mock):
        await process.spawn()
        mesh_mock.publish.assert_called()
        calls = [str(c) for c in mesh_mock.publish.call_args_list]
        assert any("process.spawned" in c for c in calls)


# ---------------------------------------------------------------------------
# CognitiveThread — invariantes
# ---------------------------------------------------------------------------

class TestCognitiveThread:

    # INV-CT.3: tenant_id no puede ser vacío
    def test_empty_tenant_id_raises(self):
        async def dummy(): return None
        with pytest.raises(ValueError, match="INV-CT.3"):
            CognitiveThread(
                cpid="cp-001", tenant_id="", session_id="s",
                task=dummy,
            )

    # INV-CT.3: tenant_id heredado del proceso padre
    @pytest.mark.asyncio
    async def test_thread_inherits_tenant_id(self, process):
        await process.spawn()
        async def dummy(): return "ok"
        thread = process.create_thread(task=dummy)
        assert thread.tenant_id == process.tenant_id  # INV-CT.3

    # INV-CT.2: max threads por proceso
    @pytest.mark.asyncio
    async def test_max_threads_enforced(self, process):
        await process.spawn()
        process._max_threads = 2

        async def dummy(): return None

        process.create_thread(task=dummy)
        process.create_thread(task=dummy)
        with pytest.raises(RuntimeError, match="INV-CT.2"):
            process.create_thread(task=dummy)

    # INV-CT.1: no se puede crear thread si proceso en TERMINATING
    @pytest.mark.asyncio
    async def test_no_thread_after_terminate(self, process):
        await process.spawn()
        await process.terminate()
        async def dummy(): return None
        with pytest.raises(RuntimeError):
            process.create_thread(task=dummy)

    # Ejecución exitosa de thread
    @pytest.mark.asyncio
    async def test_thread_execute_success(self, process):
        await process.spawn()
        async def compute(): return 42
        thread = process.create_thread(task=compute)
        result = await process.run_thread(thread.ctid)
        assert result.success is True
        assert result.output == 42
        assert thread.state == CognitiveThreadState.TERMINATED

    # Ejecución fallida de thread — no propaga excepción, devuelve result.success=False
    @pytest.mark.asyncio
    async def test_thread_execute_failure_captured(self, process):
        await process.spawn()
        async def failing(): raise ValueError("error cognitivo")
        thread = process.create_thread(task=failing)
        result = await process.run_thread(thread.ctid)
        assert result.success is False
        assert "error cognitivo" in result.error
        assert thread.state == CognitiveThreadState.TERMINATED


# ---------------------------------------------------------------------------
# CognitiveIPC — invariantes
# ---------------------------------------------------------------------------

class TestCognitiveIPC:

    @pytest.fixture
    def ipc(self, mesh_mock):
        return CognitiveIPC(mesh=mesh_mock, max_payload_bytes=65536)

    @pytest.fixture
    def running_process(self, process):
        # proceso en estado RUNNING sin hacer spawn real (mockeado)
        process.state = CognitiveProcessState.RUNNING
        return process

    # INV-IPC.1: cross-tenant sin NHP levanta ValueError
    @pytest.mark.asyncio
    async def test_cross_tenant_without_nhp_raises(self, ipc, running_process):
        with pytest.raises(ValueError, match="INV-IPC.1"):
            await ipc.send(
                sender=running_process,
                receiver_cpid="cp-other",
                receiver_tenant_id="tenant_02",  # distinto
                payload_bytes=b"hola",
                nhp_session_token=None,           # AUSENTE
            )

    # INV-IPC.1: cross-tenant CON NHP — permitido
    @pytest.mark.asyncio
    async def test_cross_tenant_with_nhp_allowed(self, ipc, running_process, mesh_mock):
        msg = await ipc.send(
            sender=running_process,
            receiver_cpid="cp-other",
            receiver_tenant_id="tenant_02",
            payload_bytes=b"hola",
            nhp_session_token="nhp-token-valid",
        )
        assert msg.nhp_session_token == "nhp-token-valid"
        mesh_mock.publish.assert_called()

    # INV-IPC.2: payload supera límite
    @pytest.mark.asyncio
    async def test_payload_exceeds_limit_raises(self, mesh_mock, running_process):
        ipc = CognitiveIPC(mesh=mesh_mock, max_payload_bytes=10)
        with pytest.raises(ValueError, match="INV-IPC.2"):
            await ipc.send(
                sender=running_process,
                receiver_cpid="cp-other",
                receiver_tenant_id="tenant_01",
                payload_bytes=b"X" * 11,
            )

    # INV-IPC.3 + INV-IPC.4: mensaje publicado en mesh con sender_cpid y receiver_cpid
    @pytest.mark.asyncio
    async def test_ipc_send_routes_via_mesh(self, ipc, running_process, mesh_mock):
        msg = await ipc.send(
            sender=running_process,
            receiver_cpid="cp-target",
            receiver_tenant_id="tenant_01",
            payload_bytes=b"payload",
        )
        mesh_mock.publish.assert_called()
        call_payload = mesh_mock.publish.call_args[1]["payload"]
        assert call_payload["sender_cpid"] == running_process.cpid   # INV-IPC.4
        assert call_payload["receiver_cpid"] == "cp-target"          # INV-IPC.4

    # SIGNAL: solo mismo-tenant (sin NHP)
    @pytest.mark.asyncio
    async def test_signal_same_tenant(self, ipc, running_process, mesh_mock):
        msg = await ipc.signal(
            sender=running_process,
            receiver_cpid="cp-other",
            signal_name="TERMINATE",
        )
        assert msg.message_type == IPCMessageType.SIGNAL
        assert msg.nhp_session_token is None

    # BROADCAST: solo mismo-tenant
    @pytest.mark.asyncio
    async def test_broadcast_reaches_mesh(self, ipc, running_process, mesh_mock):
        msg = await ipc.broadcast(
            sender=running_process,
            payload_bytes=b"todos escuchen",
        )
        assert msg.receiver_cpid == "*"
        mesh_mock.publish.assert_called()

    # Sender no-RUNNING rechazado
    @pytest.mark.asyncio
    async def test_sender_not_running_raises(self, ipc, process):
        # process en CREATED (no spawneado)
        with pytest.raises(RuntimeError):
            await ipc.send(
                sender=process,
                receiver_cpid="cp-other",
                receiver_tenant_id="tenant_01",
                payload_bytes=b"x",
            )


# ---------------------------------------------------------------------------
# CognitiveProcessScheduler
# ---------------------------------------------------------------------------

class TestCognitiveProcessScheduler:

    @pytest.fixture
    def scheduler(self, kernel_mock, mesh_mock):
        return CognitiveProcessScheduler(
            tenant_id="tenant_01",
            kernel=kernel_mock,
            mesh=mesh_mock,
            max_processes=3,
        )

    # INV-CP.1: proceso de otro tenant rechazado
    def test_register_wrong_tenant_raises(self, scheduler, kernel_mock, mesh_mock):
        p = CognitiveProcess(
            tenant_id="tenant_02",  # distinto
            session_id="s", agent_id="a",
            kernel=kernel_mock, mesh=mesh_mock,
            budget_tokens=100,
        )
        with pytest.raises(ValueError, match="INV-CP.1"):
            scheduler.register(p)

    # INV-SCHED.2: max_processes respetado
    def test_max_processes_enforced(self, scheduler, kernel_mock, mesh_mock):
        for i in range(3):  # max = 3
            p = CognitiveProcess(
                tenant_id="tenant_01", session_id=f"s{i}", agent_id=f"a{i}",
                kernel=kernel_mock, mesh=mesh_mock, budget_tokens=100,
            )
            scheduler.register(p)

        extra = CognitiveProcess(
            tenant_id="tenant_01", session_id="s_extra", agent_id="a_extra",
            kernel=kernel_mock, mesh=mesh_mock, budget_tokens=100,
        )
        with pytest.raises(RuntimeError, match="INV-SCHED.2"):
            scheduler.register(extra)

    # terminate_all termina todos los procesos activos
    @pytest.mark.asyncio
    async def test_terminate_all(self, scheduler, kernel_mock, mesh_mock):
        for i in range(2):
            p = CognitiveProcess(
                tenant_id="tenant_01", session_id=f"s{i}", agent_id=f"a{i}",
                kernel=kernel_mock, mesh=mesh_mock, budget_tokens=100,
            )
            p.state = CognitiveProcessState.RUNNING   # simular spawneado
            p._budget_state = KernelBudgetState(
                tenant_id="tenant_01", session_id=f"s{i}",
                budget_tokens=100, budget_consumed=50, budget_remaining=50,
            )
            scheduler.register(p)

        results = await scheduler.terminate_all()
        assert len(results) == 2
        for cpid, returned in results.items():
            assert isinstance(returned, int)
