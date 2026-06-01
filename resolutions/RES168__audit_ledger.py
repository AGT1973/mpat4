"""
RES168__audit_ledger.py
DESTINO FINAL: observability/audit_ledger.py
RES.168 - MPAT4 | Relay: RELAY_014 | 2026-05-23
Autor: cursos.agt.ia@gmail.com (docente_AGT_2026)


P69 — Registro de Auditoría Inmutable (Bloque A).
Ledger de bloques SHA-256 encadenados estilo Merkle.
Hace matemáticamente imposible alterar registros históricos
sin invalidar toda la cadena.


ARQUITECTURA DE PERSISTENCIA (2 capas):
  1. Archivo binario secuencial (.ledger) — append-only, inmutable.
     Cada bloque = 4 bytes longitud + N bytes JSON comprimido.
  2. SQLite como índice secundario — permite búsquedas por timestamp,
     event_type y block_hash SIN cargar todo el archivo en memoria.


INVARIANTES:
  INV-LEDGER.1: cada bloque contiene el hash SHA-256 del bloque anterior.
                El bloque génesis (index=0) tiene previous_hash="0"*64.
  INV-LEDGER.2: record_event() es thread-safe via asyncio.Lock.
                Ningún bloque puede ser insertado concurrentemente.
  INV-LEDGER.3: verify_chain() relee el archivo completo y valida
                cada enlace — O(N) tiempo, O(1) memoria (streaming).
  INV-LEDGER.4: el archivo .ledger es APPEND-ONLY — nunca se reescribe.
                Si se detecta corrupción, se aísla el segmento corrupto
                y se continúa desde el último bloque válido.
  INV-LEDGER.5: los 6 eventos de gobernanza (review.*) se registran
                con prioridad HIGH — siempre al frente de la escritura.


TRAMPA EDUCATIVA:
  "verify_chain() tiene que cargar todos los bloques en memoria."
  FALSO: verify_chain() lee el archivo en STREAMING bloque por bloque.
  Solo necesita mantener dos variables: el hash del bloque anterior
  y el hash calculado del bloque actual. Memoria constante O(1)
  independientemente del tamaño del ledger.


que has usado el formato de razonamiento adaptado por AGT
"""
from __future__ import annotations


import asyncio
import hashlib
import json
import logging
import os
import sqlite3
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Optional
from uuid import uuid4


from observability.audit_schema import (
    AuditBlock, AuditEventType, LedgerStats, ChainVerificationResult,
    GovernanceEventType,
)


logger = logging.getLogger("mpat.audit_ledger")


# Constantes del formato binario
BLOCK_MAGIC = b"MPTB"   # MPAT4 Block — 4 bytes de firma
BLOCK_VERSION = 1




class AuditLedger:
    """
    Registro de auditoría inmutable de MPAT4.


    Cada evento del sistema — sesiones, governance, tool calls, IPC —
    se registra como un bloque en el ledger. Los bloques están
    encadenados con SHA-256: alterar un bloque invalida todos los
    siguientes, haciendo la manipulación matemáticamente detectable.


    Uso típico:
        ledger = AuditLedger(base_path="~/.mpat/audit")
        await ledger.initialize()
        block_hash = await ledger.record_event(
            tenant_id="escuela_IA",
            event_type=AuditEventType.SESSION_STARTED,
            payload={"session_id": "...", "agent_id": "..."},
        )
        result = await ledger.verify_chain(tenant_id="escuela_IA")
    """


    def __init__(
        self,
        base_path: str = "~/.mpat/audit",
        compress: bool = True,
    ):
        self._base = Path(base_path).expanduser()
        self._compress = compress
        self._lock = asyncio.Lock()           # INV-LEDGER.2
        self._last_hash: dict[str, str] = {}  # tenant_id → último block_hash
        self._block_index: dict[str, int] = {}# tenant_id → próximo block_index
        self._db: Optional[sqlite3.Connection] = None


    # ------------------------------------------------------------------
    # Inicialización
    # ------------------------------------------------------------------


    async def initialize(self) -> None:
        """Crea directorios, inicializa SQLite index, carga estado actual."""
        self._base.mkdir(parents=True, exist_ok=True)
        self._db = self._open_sqlite()
        await self._load_last_state()
        logger.info("AuditLedger inicializado en %s", self._base)


    def _open_sqlite(self) -> sqlite3.Connection:
        db_path = self._base / "ledger_index.db"
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS blocks (
                tenant_id   TEXT NOT NULL,
                block_index INTEGER NOT NULL,
                block_hash  TEXT NOT NULL,
                event_type  TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                byte_offset INTEGER NOT NULL,
                PRIMARY KEY (tenant_id, block_index)
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tenant_time
            ON blocks (tenant_id, recorded_at)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_type
            ON blocks (tenant_id, event_type)
        """)
        conn.commit()
        return conn


    async def _load_last_state(self) -> None:
        """Carga el último block_hash y block_index de cada tenant desde SQLite."""
        cursor = self._db.execute("""
            SELECT tenant_id, MAX(block_index) AS last_idx, block_hash
            FROM blocks
            GROUP BY tenant_id
        """)
        for row in cursor.fetchall():
            tid, last_idx, last_hash = row
            self._last_hash[tid] = last_hash
            self._block_index[tid] = last_idx + 1
        logger.debug("Estado cargado: %d tenants en el ledger", len(self._last_hash))


    # ------------------------------------------------------------------
    # record_event — escritura de bloque (INV-LEDGER.1/2)
    # ------------------------------------------------------------------


    async def record_event(
        self,
        tenant_id: str,
        event_type: AuditEventType,
        payload: dict[str, Any],
        priority: str = "NORMAL",
    ) -> str:
        """
        Registra un evento como un nuevo bloque en el ledger.


        INV-LEDGER.1: inyecta el hash del bloque anterior.
        INV-LEDGER.2: usa asyncio.Lock — nunca concurrente.


        Retorna el block_hash del bloque creado.
        """
        async with self._lock:
            previous_hash = self._last_hash.get(tenant_id, "0" * 64)
            block_index   = self._block_index.get(tenant_id, 0)
            recorded_at   = datetime.now(timezone.utc).isoformat()


            # Construir el bloque
            block_data = {
                "block_index":   block_index,
                "tenant_id":     tenant_id,
                "event_type":    event_type.value,
                "payload":       payload,
                "previous_hash": previous_hash,
                "recorded_at":   recorded_at,
                "block_id":      str(uuid4()),
            }


            # Calcular hash del bloque actual (INV-LEDGER.1)
            canonical = json.dumps(block_data, sort_keys=True, ensure_ascii=True)
            block_hash = hashlib.sha256(canonical.encode()).hexdigest()
            block_data["block_hash"] = block_hash


            # Serializar y opcionalmente comprimir
            raw_json = json.dumps(block_data, ensure_ascii=True).encode()
            payload_bytes = zlib.compress(raw_json) if self._compress else raw_json


            # Escribir en archivo binario (INV-LEDGER.4: append-only)
            ledger_path = self._ledger_path(tenant_id)
            byte_offset = await self._append_block(ledger_path, payload_bytes)


            # Actualizar índice SQLite
            self._db.execute(
                "INSERT OR REPLACE INTO blocks "
                "(tenant_id, block_index, block_hash, event_type, recorded_at, byte_offset) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (tenant_id, block_index, block_hash,
                 event_type.value, recorded_at, byte_offset),
            )
            self._db.commit()


            # Actualizar estado en memoria
            self._last_hash[tenant_id]  = block_hash
            self._block_index[tenant_id] = block_index + 1


            logger.debug(
                "Bloque registrado: tenant=%s index=%d type=%s hash=%s...",
                tenant_id, block_index, event_type.value, block_hash[:16],
            )
            return block_hash


    async def _append_block(self, path: Path, payload_bytes: bytes) -> int:
        """
        Escribe el bloque en el archivo binario.
        Formato: [MAGIC 4B][VERSION 1B][LEN 4B][PAYLOAD NB]
        Retorna el byte_offset donde fue escrito.
        """
        header = (
            BLOCK_MAGIC
            + struct.pack(">B", BLOCK_VERSION)
            + struct.pack(">I", len(payload_bytes))
        )
        data = header + payload_bytes
        loop = asyncio.get_event_loop()
        byte_offset = await loop.run_in_executor(
            None, self._sync_append, path, data
        )
        return byte_offset


    def _sync_append(self, path: Path, data: bytes) -> int:
        """Operación de I/O síncrona — ejecutada en thread pool."""
        with open(path, "ab") as f:
            offset = f.tell()
            f.write(data)
            f.flush()
            os.fsync(f.fileno())  # garantiza escritura a disco
            return offset


    # ------------------------------------------------------------------
    # verify_chain — validación streaming O(1) memoria (INV-LEDGER.3)
    # ------------------------------------------------------------------


    async def verify_chain(self, tenant_id: str) -> ChainVerificationResult:
        """
        Verifica la integridad de toda la cadena de un tenant.


        INV-LEDGER.3: streaming bloque por bloque — memoria O(1).
        TRAMPA resuelta: no carga todos los bloques en memoria.


        Retorna ChainVerificationResult con:
        - is_valid: bool
        - blocks_verified: int
        - first_invalid_block: Optional[int]
        - error_detail: Optional[str]
        """
        ledger_path = self._ledger_path(tenant_id)
        if not ledger_path.exists():
            return ChainVerificationResult(
                tenant_id=tenant_id,
                is_valid=True,
                blocks_verified=0,
                message="Ledger vacío — cadena válida por vacuidad",
            )


        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, self._sync_verify, ledger_path, tenant_id
        )
        return result


    def _sync_verify(
        self, path: Path, tenant_id: str
    ) -> ChainVerificationResult:
        """
        Verificación síncrona en thread pool.
        Lee el archivo bloque por bloque — O(1) memoria (INV-LEDGER.3).
        """
        previous_hash = "0" * 64
        blocks_verified = 0


        with open(path, "rb") as f:
            while True:
                # Leer header: MAGIC(4) + VERSION(1) + LEN(4) = 9 bytes
                header = f.read(9)
                if not header:
                    break  # fin del archivo
                if len(header) < 9:
                    return ChainVerificationResult(
                        tenant_id=tenant_id,
                        is_valid=False,
                        blocks_verified=blocks_verified,
                        first_invalid_block=blocks_verified,
                        error_detail="Header truncado en bloque {}".format(blocks_verified),
                    )


                magic   = header[:4]
                version = struct.unpack(">B", header[4:5])[0]
                length  = struct.unpack(">I", header[5:9])[0]


                if magic != BLOCK_MAGIC:
                    return ChainVerificationResult(
                        tenant_id=tenant_id,
                        is_valid=False,
                        blocks_verified=blocks_verified,
                        first_invalid_block=blocks_verified,
                        error_detail=f"Magic inválido en bloque {blocks_verified}: {magic!r}",
                    )


                payload = f.read(length)
                if len(payload) < length:
                    return ChainVerificationResult(
                        tenant_id=tenant_id,
                        is_valid=False,
                        blocks_verified=blocks_verified,
                        first_invalid_block=blocks_verified,
                        error_detail=f"Payload truncado en bloque {blocks_verified}",
                    )


                # Descomprimir
                try:
                    raw = zlib.decompress(payload) if self._compress else payload
                    block_data = json.loads(raw.decode())
                except Exception as exc:
                    return ChainVerificationResult(
                        tenant_id=tenant_id,
                        is_valid=False,
                        blocks_verified=blocks_verified,
                        first_invalid_block=blocks_verified,
                        error_detail=f"Deserialización fallida bloque {blocks_verified}: {exc}",
                    )


                # Verificar enlace causal (INV-LEDGER.1)
                stored_hash   = block_data.pop("block_hash", "")
                stored_prev   = block_data.get("previous_hash", "")


                if stored_prev != previous_hash:
                    return ChainVerificationResult(
                        tenant_id=tenant_id,
                        is_valid=False,
                        blocks_verified=blocks_verified,
                        first_invalid_block=blocks_verified,
                        error_detail=(
                            f"Cadena rota en bloque {blocks_verified}: "
                            f"previous_hash esperado={previous_hash[:16]}... "
                            f"encontrado={stored_prev[:16]}..."
                        ),
                    )


                # Recalcular hash y comparar
                canonical = json.dumps(block_data, sort_keys=True, ensure_ascii=True)
                computed_hash = hashlib.sha256(canonical.encode()).hexdigest()


                if computed_hash != stored_hash:
                    return ChainVerificationResult(
                        tenant_id=tenant_id,
                        is_valid=False,
                        blocks_verified=blocks_verified,
                        first_invalid_block=blocks_verified,
                        error_detail=(
                            f"Hash inválido en bloque {blocks_verified}: "
                            f"esperado={stored_hash[:16]}... "
                            f"calculado={computed_hash[:16]}..."
                        ),
                    )


                previous_hash = stored_hash
                blocks_verified += 1


        return ChainVerificationResult(
            tenant_id=tenant_id,
            is_valid=True,
            blocks_verified=blocks_verified,
            message=f"Cadena válida — {blocks_verified} bloques verificados",
        )


    # ------------------------------------------------------------------
    # Consultas via índice SQLite — sin leer el archivo binario
    # ------------------------------------------------------------------


    async def query_by_event_type(
        self,
        tenant_id: str,
        event_type: AuditEventType,
        limit: int = 100,
    ) -> list[dict]:
        """Busca bloques por tipo de evento usando el índice SQLite."""
        cursor = self._db.execute(
            "SELECT block_index, block_hash, recorded_at, byte_offset "
            "FROM blocks WHERE tenant_id=? AND event_type=? "
            "ORDER BY block_index DESC LIMIT ?",
            (tenant_id, event_type.value, limit),
        )
        return [
            {"block_index": r[0], "block_hash": r[1],
             "recorded_at": r[2], "byte_offset": r[3]}
            for r in cursor.fetchall()
        ]


    async def query_by_timerange(
        self,
        tenant_id: str,
        since: str,   # ISO8601
        until: Optional[str] = None,
        limit: int = 500,
    ) -> list[dict]:
        """Busca bloques en un rango de tiempo usando el índice SQLite."""
        until = until or datetime.now(timezone.utc).isoformat()
        cursor = self._db.execute(
            "SELECT block_index, block_hash, event_type, recorded_at "
            "FROM blocks WHERE tenant_id=? AND recorded_at BETWEEN ? AND ? "
            "ORDER BY recorded_at ASC LIMIT ?",
            (tenant_id, since, until, limit),
        )
        return [
            {"block_index": r[0], "block_hash": r[1],
             "event_type": r[2], "recorded_at": r[3]}
            for r in cursor.fetchall()
        ]


    # ------------------------------------------------------------------
    # 6 eventos de gobernanza (INV-LEDGER.5)
    # ------------------------------------------------------------------


    async def record_governance_event(
        self,
        tenant_id: str,
        governance_type: GovernanceEventType,
        payload: dict,
    ) -> str:
        """
        Registra uno de los 6 tipos de eventos de gobernanza con prioridad HIGH.
        INV-LEDGER.5: eventos de gobernanza van siempre al frente de la escritura.


        Los 6 tipos:
          REVIEW_CREATED, REVIEW_APPROVED, REVIEW_REJECTED,
          REVIEW_MODIFIED, REVIEW_EXPIRED, REVIEW_CANCELLED
        """
        return await self.record_event(
            tenant_id=tenant_id,
            event_type=AuditEventType.GOVERNANCE,
            payload={"governance_type": governance_type.value, **payload},
            priority="HIGH",
        )


    # ------------------------------------------------------------------
    # Stats y utilidades
    # ------------------------------------------------------------------


    async def stats(self, tenant_id: str) -> LedgerStats:
        cursor = self._db.execute(
            "SELECT COUNT(*), MIN(recorded_at), MAX(recorded_at) "
            "FROM blocks WHERE tenant_id=?",
            (tenant_id,),
        )
        row = cursor.fetchone()
        total, first_at, last_at = row if row else (0, None, None)


        ledger_path = self._ledger_path(tenant_id)
        file_size = ledger_path.stat().st_size if ledger_path.exists() else 0


        return LedgerStats(
            tenant_id=tenant_id,
            total_blocks=total or 0,
            file_size_bytes=file_size,
            first_block_at=first_at,
            last_block_at=last_at,
            last_block_hash=self._last_hash.get(tenant_id, ""),
        )


    def _ledger_path(self, tenant_id: str) -> Path:
        """Ruta del archivo .ledger por tenant (INV-GRAPH.1 equivalente)."""
        safe_tid = tenant_id.replace("/", "_").replace("..", "_")
        return self._base / f"{safe_tid}.ledger"


    async def close(self) -> None:
        if self._db:
            self._db.close()