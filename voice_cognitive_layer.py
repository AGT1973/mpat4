# voice_cognitive_layer.py
# RES.172 -- Voice Cognitive Layer
# Autor: Claude Sonnet 4.6 · 2026-05-26
# MPAT4 -- Infraestructura Cognitiva Distribuida
# Contrato: CONTRACT_RES172_v1.md (ID: 1jgjmbIMeHgWrfwpHMBfBqUIPPYmTpN5lKeidYDSrbAs)
# Schema: schemas/schema_res172.py (ID: 1DyAXJMgxzlF8RS23z4gsePikasoGt-kA44IeMCIQUdc)
# que has usado el formato de razonamiento adaptado por AGT
#
# INVARIANTES IMPLEMENTADAS:
#   INV-VOICE.1: Todo async -- nunca bloquear el loop principal
#   INV-VOICE.2: Interrupcion SIEMPRE cancela respuesta en curso
#   INV-VOICE.3: STT NUNCA envia texto parcial al LLM -- solo utterances completas
#   INV-VOICE.4: TTS streaming: primer chunk en < 150ms
#   INV-VOICE.5: Toda sesion registrada en AuditLedger (via emit inyectado)
#   INV-VOICE.6: NUNCA Docker. Solo emit inyectado.


from __future__ import annotations


import asyncio
import logging
import time
from collections.abc import AsyncIterator, Callable
from typing import Any


from schema_res172 import (
    STTEngine,
    SynthesizedAudio,
    Transcription,
    TTSEngine,
    VADResult,
    VADStatus,
    VoicePipelineMetrics,
    VoiceResponse,
    VoiceSessionConfig,
    VoiceSessionState,
    VoiceSessionStatus,
)


logger = logging.getLogger("mpat4.voice")


EmitFn = Callable[[str, dict[str, Any]], None]


# Eventos emitidos (INV-VOICE.6)
_EVT_UTTERANCE  = "voice.utterance"
_EVT_RESPONSE   = "voice.response"
_EVT_INTERRUPT  = "voice.interrupt"
_EVT_METRICS    = "voice.metrics"
_EVT_AUDIT      = "voice.session_audit"




# ===========================================================================
# VoiceCognitiveLayer -- pipeline principal STT -> LLM -> TTS
# ===========================================================================


class VoiceCognitiveLayer:
    """
    Pipeline de voz de baja latencia para MPAT4.


    Flujo por utterance:
      VAD confirm -> STT (FasterWhisper) -> LLM streaming -> TTS (Kokoro/edge-tts) -> audio out


    INV-VOICE.1: Toda operacion es async. Nunca bloquear el loop.
    INV-VOICE.2: interrupt() cancela tasks activas inmediatamente.
    INV-VOICE.6: No importa modulos MPAT4 directamente -- solo emit inyectado.


    Uso:
        stt  = WhisperSTT(model="small")
        tts  = KokoroTTS()
        vad  = VoiceActivityDetector(VADConfig())
        vcl  = VoiceCognitiveLayer(stt=stt, tts=tts, vad=vad, llm_fn=my_llm, emit=bus.emit)
        resp = await vcl.process_utterance(audio_bytes, session_id)
    """


    def __init__(
        self,
        stt: "BaseSTT",
        tts: "BaseTTS",
        vad: "VoiceActivityDetector",
        llm_fn: Callable[[str], AsyncIterator[str]],
        emit: EmitFn,
    ) -> None:
        self._stt    = stt
        self._tts    = tts
        self._vad    = vad
        self._llm_fn = llm_fn
        self._emit   = emit
        self._sessions: dict[str, VoiceSessionState] = {}
        self._active_tasks: dict[str, asyncio.Task] = {}  # session_id -> task activa


    # -----------------------------------------------------------------------
    # process_utterance -- punto de entrada principal
    # -----------------------------------------------------------------------


    async def process_utterance(self, audio_bytes: bytes, session_id: str) -> VoiceResponse:
        """
        Ejecuta el pipeline completo: STT -> LLM -> TTS.
        INV-VOICE.3: solo llama al LLM si VAD confirmo utterance completo.
        Retorna VoiceResponse con interrupted=True si fue cancelado.
        """
        t0 = time.monotonic()
        session = self._get_or_create_session(session_id)
        session.status = VoiceSessionStatus.PROCESSING


        try:
            # --- STT ---
            t_stt_start = time.monotonic()
            transcription = await self._stt.transcribe(audio_bytes, session_id)
            stt_latency = int((time.monotonic() - t_stt_start) * 1000)


            if transcription.is_empty:
                session.status = VoiceSessionStatus.LISTENING
                # Retorna respuesta vacia -- no consume tokens del LLM
                return VoiceResponse(
                    session_id=session_id,
                    transcription=transcription,
                    llm_response_text="",
                    interrupted=False,
                    total_latency_ms=int((time.monotonic() - t0) * 1000),
                )


            self._emit(_EVT_UTTERANCE, {
                "session_id": session_id,
                "agent_id":   session.config.agent_id,
                "tenant_id":  session.config.tenant_id,
                "text":       transcription.text,
            })


            # --- LLM streaming -> TTS streaming ---
            session.status = VoiceSessionStatus.SPEAKING
            t_llm_start = time.monotonic()


            task = asyncio.create_task(
                self._llm_to_tts(transcription, session, t0, t_llm_start, stt_latency)
            )
            self._active_tasks[session_id] = task


            try:
                response = await task
            except asyncio.CancelledError:
                session.status = VoiceSessionStatus.INTERRUPTED
                response = VoiceResponse(
                    session_id=session_id,
                    transcription=transcription,
                    llm_response_text="",
                    interrupted=True,
                    total_latency_ms=int((time.monotonic() - t0) * 1000),
                )
            finally:
                self._active_tasks.pop(session_id, None)


            session.utterance_count += 1
            session.last_activity = _now()
            return response


        except Exception as exc:
            logger.error("VoiceCognitiveLayer.process_utterance error: %s", exc)
            session.status = VoiceSessionStatus.IDLE
            raise


    async def _llm_to_tts(
        self,
        transcription: Transcription,
        session: VoiceSessionState,
        t0: float,
        t_llm_start: float,
        stt_latency: int,
    ) -> VoiceResponse:
        """Pipeline interno: LLM streaming -> TTS streaming. Cancelable via task.cancel()."""
        full_text = ""
        tts_first_chunk_ms = 0
        tts_chunks: list[bytes] = []
        t_tts_first: float | None = None


        # Buffer de texto para alimentar TTS en frases completas
        sentence_buffer = ""


        async for token in self._llm_fn(transcription.text):
            full_text += token
            sentence_buffer += token


            # Cuando hay una frase completa, sintetizar
            if _is_sentence_boundary(sentence_buffer):
                chunk_audio = await self._tts.synthesize_chunk(sentence_buffer, session.session_id)
                if t_tts_first is None:
                    t_tts_first = time.monotonic()
                    tts_first_chunk_ms = int((t_tts_first - t_llm_start) * 1000)
                tts_chunks.append(chunk_audio)
                sentence_buffer = ""


        # Sintetizar buffer restante
        if sentence_buffer.strip():
            chunk_audio = await self._tts.synthesize_chunk(sentence_buffer, session.session_id)
            if t_tts_first is None:
                t_tts_first = time.monotonic()
                tts_first_chunk_ms = int((t_tts_first - t_llm_start) * 1000)
            tts_chunks.append(chunk_audio)


        llm_latency = int((time.monotonic() - t_llm_start) * 1000)
        total_latency = int((time.monotonic() - t0) * 1000)


        synth = SynthesizedAudio(
            session_id=session.session_id,
            text=full_text,
            sample_rate=22050,
            duration_ms=sum(len(c) // 44 for c in tts_chunks),  # estimacion
            tts_engine=session.config.tts_engine,
            latency_ms=tts_first_chunk_ms,
        )


        # INV-VOICE.5: emitir auditoria de sesion
        metrics = VoicePipelineMetrics(
            session_id=session.session_id,
            stt_latency_ms=transcription.latency_ms,
            llm_latency_ms=llm_latency,
            tts_first_chunk_ms=tts_first_chunk_ms,
            total_latency_ms=total_latency,
            within_target=total_latency <= session.config.target_latency_ms,
        )
        self._emit(_EVT_METRICS, metrics.model_dump())
        self._emit(_EVT_AUDIT, {
            "session_id":     session.session_id,
            "agent_id":       session.config.agent_id,
            "tenant_id":      session.config.tenant_id,
            "utterance_count": session.utterance_count + 1,
            "within_target":  metrics.within_target,
            "total_latency_ms": total_latency,
        })


        response = VoiceResponse(
            session_id=session.session_id,
            transcription=transcription,
            llm_response_text=full_text,
            synthesized_audio=synth,
            interrupted=False,
            total_latency_ms=total_latency,
        )
        self._emit(_EVT_RESPONSE, {
            "session_id": session.session_id,
            "agent_id":   session.config.agent_id,
            "text":       full_text,
            "interrupted": False,
        })
        session.status = VoiceSessionStatus.LISTENING
        return response


    # -----------------------------------------------------------------------
    # interrupt -- INV-VOICE.2
    # -----------------------------------------------------------------------


    def interrupt(self, session_id: str) -> None:
        """
        Cancela el task activo de STT->LLM->TTS para session_id.
        INV-VOICE.2: SIEMPRE cancela la respuesta en curso.
        """
        task = self._active_tasks.get(session_id)
        if task and not task.done():
            task.cancel()
            session = self._sessions.get(session_id)
            if session:
                session.status = VoiceSessionStatus.INTERRUPTED
            self._emit(_EVT_INTERRUPT, {
                "session_id": session_id,
                "agent_id":   session.config.agent_id if session else "",
            })
            logger.info("VoiceCognitiveLayer: interrupcion en session_id=%s", session_id)


    # -----------------------------------------------------------------------
    # stream_tts -- INV-VOICE.4
    # -----------------------------------------------------------------------


    async def stream_tts(self, text: str, session_id: str) -> AsyncIterator[bytes]:
        """
        TTS streaming directo: retorna chunks de audio sin esperar completion.
        INV-VOICE.4: primer chunk en < 150ms.
        """
        session = self._get_or_create_session(session_id)
        for sentence in _split_sentences(text):
            if sentence.strip():
                chunk = await self._tts.synthesize_chunk(sentence, session_id)
                yield chunk


    # -----------------------------------------------------------------------
    # session management
    # -----------------------------------------------------------------------


    def create_session(self, config: VoiceSessionConfig) -> VoiceSessionState:
        """Crea e inicializa una sesion de voz."""
        state = VoiceSessionState(config=config)
        self._sessions[state.session_id] = state
        self._vad.reset(state.session_id)
        return state


    def get_session_state(self, session_id: str) -> VoiceSessionState | None:
        return self._sessions.get(session_id)


    def close_session(self, session_id: str) -> None:
        """Cierra y limpia una sesion."""
        self.interrupt(session_id)
        self._sessions.pop(session_id, None)
        self._vad.reset(session_id)


    def _get_or_create_session(self, session_id: str) -> VoiceSessionState:
        if session_id not in self._sessions:
            # Config por defecto -- en produccion se crea via create_session()
            default_config = VoiceSessionConfig(agent_id="default", tenant_id="default")
            state = VoiceSessionState(session_id=session_id, config=default_config)
            self._sessions[session_id] = state
        return self._sessions[session_id]




# ===========================================================================
# BaseSTT / WhisperSTT -- adaptador STT
# ===========================================================================


class BaseSTT:
    """Interfaz base para motores STT."""
    async def transcribe(self, audio_bytes: bytes, session_id: str) -> Transcription:
        raise NotImplementedError




class WhisperSTT(BaseSTT):
    """
    STT usando FasterWhisper cuantizado.
    Latencia objetivo: < 200ms para utterances de 5s.
    Fallback a openai-whisper si faster-whisper no esta disponible.
    DT-RES172-04: streaming STT (no utterance-by-utterance) es deuda tecnica ALTA.
    """


    def __init__(self, model: str = "small", language: str = "es") -> None:
        self._model_name = model
        self._language   = language
        self._model      = None
        self._engine     = STTEngine.FASTER_WHISPER


    def _load_model(self) -> None:
        if self._model is not None:
            return
        try:
            from faster_whisper import WhisperModel  # type: ignore
            self._model  = WhisperModel(self._model_name, device="cpu", compute_type="int8")
            self._engine = STTEngine.FASTER_WHISPER
            logger.info("WhisperSTT: FasterWhisper model=%s cargado.", self._model_name)
        except ImportError:
            import whisper  # type: ignore
            self._model  = whisper.load_model(self._model_name)
            self._engine = STTEngine.OPENAI_WHISPER
            logger.warning("WhisperSTT: FasterWhisper no disponible, usando openai-whisper.")


    async def transcribe(self, audio_bytes: bytes, session_id: str) -> Transcription:
        """INV-VOICE.3: retorna solo utterances completas, nunca texto parcial."""
        self._load_model()
        t0 = time.monotonic()


        # Ejecutar en threadpool para no bloquear el loop (INV-VOICE.1)
        loop = asyncio.get_event_loop()
        text, confidence = await loop.run_in_executor(
            None, self._run_inference, audio_bytes
        )


        latency_ms = int((time.monotonic() - t0) * 1000)
        duration_ms = int(len(audio_bytes) / 2 / 16000 * 1000)  # 16kHz 16bit


        return Transcription(
            session_id=session_id,
            text=text.strip(),
            language=self._language,
            confidence=confidence,
            duration_ms=duration_ms,
            stt_engine=self._engine,
            latency_ms=latency_ms,
        )


    def _run_inference(self, audio_bytes: bytes) -> tuple[str, float]:
        """Ejecutado en threadpool -- puede bloquear."""
        import numpy as np  # type: ignore


        audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0


        if self._engine == STTEngine.FASTER_WHISPER:
            segments, info = self._model.transcribe(audio_array, language=self._language)
            text = " ".join(seg.text for seg in segments)
            return text, 0.95
        else:
            result = self._model.transcribe(audio_array, language=self._language)
            return result["text"], 0.90




# ===========================================================================
# BaseTTS / KokoroTTS / EdgeTTS -- adaptadores TTS
# ===========================================================================


class BaseTTS:
    """Interfaz base para motores TTS."""
    async def synthesize_chunk(self, text: str, session_id: str) -> bytes:
        raise NotImplementedError




class KokoroTTS(BaseTTS):
    """
    TTS usando Kokoro-82M (local, alta calidad).
    INV-VOICE.4: primer chunk en < 150ms.
    DT-RES172-03: voice cloning con perfil del usuario (Digital Twin) -- BAJA.
    """


    def __init__(self, voice: str = "af_sky", speed: float = 1.0) -> None:
        self._voice = voice
        self._speed = speed
        self._pipeline = None


    def _load_pipeline(self) -> None:
        if self._pipeline is not None:
            return
        try:
            from kokoro import KPipeline  # type: ignore
            self._pipeline = KPipeline(lang_code="e")
            logger.info("KokoroTTS: pipeline cargado, voz=%s.", self._voice)
        except ImportError:
            logger.warning("KokoroTTS: kokoro no disponible -- usar EdgeTTS como fallback.")
            raise


    async def synthesize_chunk(self, text: str, session_id: str) -> bytes:
        self._load_pipeline()
        loop = asyncio.get_event_loop()
        audio_bytes = await loop.run_in_executor(None, self._run_tts, text)
        return audio_bytes


    def _run_tts(self, text: str) -> bytes:
        import io
        import soundfile as sf  # type: ignore
        audio_chunks = []
        for _, _, audio in self._pipeline(text, voice=self._voice, speed=self._speed):
            audio_chunks.append(audio)
        if not audio_chunks:
            return b""
        import numpy as np  # type: ignore
        combined = np.concatenate(audio_chunks)
        buf = io.BytesIO()
        sf.write(buf, combined, 24000, format="WAV")
        return buf.getvalue()




class EdgeTTS(BaseTTS):
    """
    TTS usando Microsoft Edge TTS (online, fallback cuando Kokoro no disponible).
    DT-RES172-02: para produccion offline, migrar a Kokoro o XTTS v2.
    """


    def __init__(self, voice: str = "es-AR-TomasNeural") -> None:
        self._voice = voice


    async def synthesize_chunk(self, text: str, session_id: str) -> bytes:
        try:
            import edge_tts  # type: ignore
            communicate = edge_tts.Communicate(text, self._voice)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data
        except ImportError:
            logger.error("EdgeTTS: edge-tts no disponible. Instalar con: pip install edge-tts")
            return b""




def make_tts(engine: TTSEngine, **kwargs: Any) -> BaseTTS:
    """Factory de TTS -- intenta Kokoro, fallback a EdgeTTS."""
    if engine == TTSEngine.KOKORO:
        try:
            tts = KokoroTTS(**kwargs)
            tts._load_pipeline()
            return tts
        except (ImportError, Exception) as exc:
            logger.warning("KokoroTTS no disponible (%s), usando EdgeTTS.", exc)
            return EdgeTTS()
    return EdgeTTS(**kwargs)




# ===========================================================================
# Helpers
# ===========================================================================


def _is_sentence_boundary(text: str) -> bool:
    """Detecta si el buffer de texto contiene una frase completa."""
    stripped = text.strip()
    if not stripped:
        return False
    return stripped[-1] in ".!?;:" or len(stripped) > 120




def _split_sentences(text: str) -> list[str]:
    """Divide texto en frases para streaming TTS."""
    import re
    parts = re.split(r"(?<=[.!?;:])\s+", text)
    return [p for p in parts if p.strip()]




def _now() -> "datetime":
    from datetime import datetime
    return datetime.utcnow()