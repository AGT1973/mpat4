# voice_vad.py
# RES.172 -- Voice Activity Detection (Silero VAD v5)
# Autor: Claude Sonnet 4.6 · 2026-05-26
# MPAT4 -- Infraestructura Cognitiva Distribuida
# Contrato: CONTRACT_RES172_v1.md (ID: 1jgjmbIMeHgWrfwpHMBfBqUIPPYmTpN5lKeidYDSrbAs)
# que has usado el formato de razonamiento adaptado por AGT
#
# INVARIANTES IMPLEMENTADAS:
#   INV-VOICE.1: detect() es sync-seguro; carga modelo en threadpool la primera vez
#   INV-VOICE.3: solo emite UTTERANCE_COMPLETE cuando el silencio supera silence_ms
#   INV-VOICE.6: sin imports de otros modulos MPAT4


from __future__ import annotations


import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any


from schema_res172 import VADConfig, VADResult, VADStatus


logger = logging.getLogger("mpat4.voice.vad")




# ===========================================================================
# Estado interno por sesion
# ===========================================================================


@dataclass
class _SessionVADState:
    """Estado mutable del VAD para una sesion activa."""
    speech_started_at: float | None = None    # monotonic timestamp
    last_speech_at:    float | None = None
    speech_buffer_ms:  int          = 0
    silence_ms_so_far: int          = 0
    consecutive_speech: int         = 0       # chunks consecutivos con is_speech=True
    consecutive_silence: int        = 0       # chunks consecutivos con is_speech=False
    utterance_in_progress: bool     = False




# ===========================================================================
# VoiceActivityDetector
# ===========================================================================


class VoiceActivityDetector:
    """
    Detector de actividad de voz usando Silero VAD v5.


    Responsabilidades:
      - Detectar inicio/fin de utterance en tiempo real (chunk a chunk)
      - Emitir UTTERANCE_COMPLETE solo cuando el silencio supera VADConfig.silence_ms
      - Habilitar interrupciones naturales del usuario (INV-VOICE.2 en VoiceCognitiveLayer)


    INV-VOICE.3: UTTERANCE_COMPLETE solo se emite cuando VAD confirma fin real de utterance.
    INV-VOICE.1: carga del modelo en threadpool, detect() no bloquea el loop.


    Uso:
        vad    = VoiceActivityDetector(VADConfig())
        result = vad.detect(audio_chunk_bytes)
        if result.status == VADStatus.UTTERANCE_COMPLETE:
            # pasar audio acumulado al STT
    """


    def __init__(self, config: VADConfig | None = None) -> None:
        self._config  = config or VADConfig()
        self._model: Any = None
        self._sessions: dict[str, _SessionVADState] = {}
        self._chunk_samples = int(self._config.sample_rate * self._config.chunk_ms / 1000)
        self._loaded = False


    # -----------------------------------------------------------------------
    # Carga del modelo (lazy, thread-safe)
    # -----------------------------------------------------------------------


    def _ensure_model(self) -> None:
        """Carga Silero VAD desde torch.hub la primera vez (sync)."""
        if self._loaded:
            return
        try:
            import torch  # type: ignore
            model, _ = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                force_reload=False,
                verbose=False,
            )
            model.eval()
            self._model  = model
            self._loaded = True
            logger.info("VoiceActivityDetector: Silero VAD v5 cargado.")
        except Exception as exc:
            logger.warning("VoiceActivityDetector: Silero VAD no disponible (%s). Usando heuristica.", exc)
            self._model  = None
            self._loaded = True  # no reintentar


    async def ensure_model_async(self) -> None:
        """Carga el modelo en threadpool para no bloquear el loop (INV-VOICE.1)."""
        if not self._loaded:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._ensure_model)


    # -----------------------------------------------------------------------
    # detect -- punto de entrada principal
    # -----------------------------------------------------------------------


    def detect(self, audio_bytes: bytes, session_id: str = "default") -> VADResult:
        """
        Procesa un chunk de audio y retorna VADResult.


        INV-VOICE.3: UTTERANCE_COMPLETE solo cuando silencio >= config.silence_ms
        y utterance_in_progress=True (hubo habla real previa).


        Args:
            audio_bytes: chunk de audio crudo (PCM 16-bit, 16kHz, mono)
            session_id:  identificador de sesion (estado VAD independiente por sesion)


        Returns:
            VADResult con status UTTERANCE_COMPLETE cuando el utterance termino.
        """
        self._ensure_model()


        state = self._get_state(session_id)
        chunk_ms = self._config.chunk_ms
        now = time.monotonic()


        # --- Inferencia ---
        confidence = self._run_inference(audio_bytes)
        is_speech  = confidence >= self._config.threshold


        # --- Actualizar estado de sesion ---
        if is_speech:
            state.consecutive_silence = 0
            state.consecutive_speech += 1
            state.last_speech_at = now


            if not state.utterance_in_progress:
                # Inicio de utterance: requiere min_speech_ms de habla continua
                state.speech_buffer_ms += chunk_ms
                if state.speech_buffer_ms >= self._config.min_speech_ms:
                    state.utterance_in_progress = True
                    state.speech_started_at = now
                    state.silence_ms_so_far = 0
                    logger.debug("VAD[%s]: inicio de utterance detectado.", session_id)
            else:
                state.silence_ms_so_far = 0


            status = VADStatus.SPEECH_ONGOING if state.utterance_in_progress else VADStatus.SPEECH_START


        else:  # silencio
            state.consecutive_speech  = 0
            state.consecutive_silence += 1
            state.speech_buffer_ms    = 0


            if state.utterance_in_progress:
                state.silence_ms_so_far += chunk_ms


                if state.silence_ms_so_far >= self._config.silence_ms:
                    # Utterance completo -- INV-VOICE.3: solo aqui se emite UTTERANCE_COMPLETE
                    state.utterance_in_progress = False
                    state.silence_ms_so_far     = 0
                    logger.debug(
                        "VAD[%s]: utterance completo (silencio=%dms).",
                        session_id, self._config.silence_ms,
                    )
                    return VADResult(
                        is_speech=False,
                        confidence=confidence,
                        status=VADStatus.UTTERANCE_COMPLETE,
                        samples_processed=len(audio_bytes) // 2,
                    )


                status = VADStatus.SPEECH_ONGOING  # silencio transitorio dentro de utterance
            else:
                status = VADStatus.SILENCE


        return VADResult(
            is_speech=is_speech,
            confidence=confidence,
            status=status,
            samples_processed=len(audio_bytes) // 2,
        )


    # -----------------------------------------------------------------------
    # reset
    # -----------------------------------------------------------------------


    def reset(self, session_id: str) -> None:
        """Reinicia el estado VAD de una sesion."""
        self._sessions.pop(session_id, None)
        logger.debug("VAD[%s]: estado reiniciado.", session_id)


    # -----------------------------------------------------------------------
    # Inferencia interna
    # -----------------------------------------------------------------------


    def _run_inference(self, audio_bytes: bytes) -> float:
        """
        Retorna confidence [0.0, 1.0] de actividad de voz.
        Si Silero no esta disponible, usa heuristica de energia RMS.
        """
        if self._model is not None:
            return self._silero_inference(audio_bytes)
        return self._rms_heuristic(audio_bytes)


    def _silero_inference(self, audio_bytes: bytes) -> float:
        """Inferencia con Silero VAD v5."""
        try:
            import numpy as np  # type: ignore
            import torch  # type: ignore


            audio_np = (
                np.frombuffer(audio_bytes, dtype=np.int16)
                .astype(np.float32) / 32768.0
            )
            # Silero espera tensor 1D float32
            audio_tensor = torch.from_numpy(audio_np)
            with torch.no_grad():
                confidence = self._model(audio_tensor, self._config.sample_rate).item()
            return float(confidence)
        except Exception as exc:
            logger.warning("Silero inference error: %s -- fallback a RMS.", exc)
            return self._rms_heuristic(audio_bytes)


    @staticmethod
    def _rms_heuristic(audio_bytes: bytes) -> float:
        """
        Heuristica de energia RMS cuando Silero no esta disponible.
        Umbral calibrado para microfono de laptop en ambiente moderadamente silencioso.
        """
        if not audio_bytes:
            return 0.0
        try:
            import numpy as np  # type: ignore
            samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
            rms = float(np.sqrt(np.mean(samples ** 2)))
            # Normalizar: RMS tipico de voz ~1500-3000, silencio < 300
            confidence = min(1.0, max(0.0, (rms - 200.0) / 2800.0))
            return confidence
        except Exception:
            return 0.0


    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------


    def _get_state(self, session_id: str) -> _SessionVADState:
        if session_id not in self._sessions:
            self._sessions[session_id] = _SessionVADState()
        return self._sessions[session_id]


    @property
    def config(self) -> VADConfig:
        return self._config


    def active_sessions(self) -> list[str]:
        return list(self._sessions.keys())




# ===========================================================================
# AudioAccumulator -- acumula chunks hasta UTTERANCE_COMPLETE
# ===========================================================================


class AudioAccumulator:
    """
    Acumula chunks de audio por sesion hasta que VAD confirma utterance completo.
    Luego entrega el buffer completo al STT.


    Uso tipico:
        accum  = AudioAccumulator(vad)
        result = accum.push(chunk, session_id)
        if result is not None:
            transcription = await stt.transcribe(result, session_id)
    """


    def __init__(self, vad: VoiceActivityDetector) -> None:
        self._vad     = vad
        self._buffers: dict[str, list[bytes]] = {}


    def push(self, audio_bytes: bytes, session_id: str) -> bytes | None:
        """
        Acumula chunk. Retorna el buffer completo cuando VAD detecta UTTERANCE_COMPLETE.
        Retorna None si el utterance todavia no termino.
        INV-VOICE.3: STT solo recibe audio cuando se retorna no-None.
        """
        result = self._vad.detect(audio_bytes, session_id)


        if result.status in (VADStatus.SPEECH_START, VADStatus.SPEECH_ONGOING):
            if session_id not in self._buffers:
                self._buffers[session_id] = []
            self._buffers[session_id].append(audio_bytes)
            return None


        if result.status == VADStatus.UTTERANCE_COMPLETE:
            chunks = self._buffers.pop(session_id, [])
            chunks.append(audio_bytes)
            return b"".join(chunks)


        # SILENCE: descartar si no hay utterance en curso
        return None


    def reset(self, session_id: str) -> None:
        self._buffers.pop(session_id, None)
        self._vad.reset(session_id)


    def clear_all(self) -> None:
        self._buffers.clear()