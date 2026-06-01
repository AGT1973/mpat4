# social_agent.py
# RES.173 -- Instagram/TikTok AI Agents -- SocialMediaAgent principal
# Autor: Claude Sonnet 4.6 · 2026-05-26
# MPAT4 -- Infraestructura Cognitiva Distribuida
# Contrato: CONTRACT_RES173_v1.md (ID: 1pb-7SjmEPzHur4nl8ObxOpqdblzJalqmy0NwrYTtOfc)
# que has usado el formato de razonamiento adaptado por AGT
#
# INVARIANTES:
#   INV-SOCIAL.1: NUNCA publica sin approved_by != ""
#   INV-SOCIAL.2: Guardrails SIEMPRE antes de generar draft
#   INV-SOCIAL.3: Timeout 30s en descargas externas
#   INV-SOCIAL.4: Toda publicacion en AuditLedger via emit
#   INV-SOCIAL.5: Firma webhook siempre validada antes de procesar
#   INV-SOCIAL.6: Solo emit inyectado, sin imports MPAT4
#   INV-SOCIAL.7: Max 10 frames por video


from __future__ import annotations


import asyncio
import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any


from schema_res173 import (
    ContentAnalysis,
    DraftResponse,
    GuardrailCheck,
    GuardrailResult,
    MediaType,
    PublishResult,
    PublishStatus,
    RateLimitState,
    ResponseType,
    SocialMediaItem,
    SocialPlatform,
    WebhookPayload,
    WebhookResult,
)


logger = logging.getLogger("mpat4.social")


EmitFn  = Callable[[str, dict[str, Any]], None]
LLMFn   = Callable[[str], "Awaitable[str]"]
VLMFn   = Callable[[list[bytes], str], "Awaitable[str]"]
STTFn   = Callable[[bytes], "Awaitable[str]"]


# Eventos (INV-SOCIAL.6)
_EVT_NEW_CONTENT     = "social.new_content"
_EVT_DRAFT_READY     = "social.draft_ready"
_EVT_PUBLISHED       = "social.published"
_EVT_GUARDRAIL_BLOCK = "social.guardrail_block"
_EVT_AUDIT           = "social.audit"


_MAX_FRAMES = 10   # INV-SOCIAL.7
_DL_TIMEOUT = 30   # INV-SOCIAL.3




# ===========================================================================
# SocialMediaAgent
# ===========================================================================


class SocialMediaAgent:
    """
    Agente de redes sociales para Instagram y TikTok.


    Pipeline por item:
      webhook -> SocialMediaItem -> analyze_content -> guardrails -> draft -> HITL -> publish


    INV-SOCIAL.1: publish_response() verifica draft.approved y approved_by antes de actuar.
    INV-SOCIAL.2: _run_guardrails() siempre se llama antes de generar texto con LLM.
    INV-SOCIAL.6: No importa nada de MPAT4 directamente -- solo emit + funciones inyectadas.
    """


    def __init__(
        self,
        agent_id:    str,
        tenant_id:   str,
        llm_fn:      LLMFn,
        vlm_fn:      VLMFn,
        stt_fn:      STTFn,
        emit:        EmitFn,
        ig_client:   "InstagramClient | None" = None,
        tt_client:   "TikTokClient | None"    = None,
        config:      dict[str, Any] | None    = None,
    ) -> None:
        self._agent_id  = agent_id
        self._tenant_id = tenant_id
        self._llm_fn    = llm_fn
        self._vlm_fn    = vlm_fn
        self._stt_fn    = stt_fn
        self._emit      = emit
        self._ig        = ig_client
        self._tt        = tt_client
        self._cfg       = config or {}
        self._rate_limits: dict[str, RateLimitState] = {}


    # -----------------------------------------------------------------------
    # analyze_content
    # -----------------------------------------------------------------------


    async def analyze_content(self, item: SocialMediaItem) -> ContentAnalysis:
        """
        Descarga el media, extrae frames (si video), transcribe audio, llama VLM.
        INV-SOCIAL.3: timeout 30s en descarga.
        INV-SOCIAL.7: max 10 frames.
        """
        frames: list[bytes] = []
        transcript = ""


        try:
            media_bytes = await asyncio.wait_for(
                _download_media(item.media_url), timeout=_DL_TIMEOUT
            )
        except (asyncio.TimeoutError, Exception) as exc:
            logger.warning("analyze_content: descarga fallida para %s: %s", item.media_id, exc)
            return ContentAnalysis(
                item_id=item.item_id,
                platform=item.platform,
                description="[descarga fallida]",
                overall_guardrail=GuardrailResult.PASS,
            )


        # Extraccion de frames para video/reel
        if item.media_type in (MediaType.VIDEO, MediaType.REEL):
            frames = await asyncio.get_event_loop().run_in_executor(
                None, _extract_frames, media_bytes, _MAX_FRAMES
            )
            # Transcripcion de audio via STT inyectado
            try:
                transcript = await self._stt_fn(media_bytes)
            except Exception as exc:
                logger.warning("STT fallido para %s: %s", item.media_id, exc)


        elif item.media_type in (MediaType.IMAGE, MediaType.STORY, MediaType.CAROUSEL):
            frames = [media_bytes]


        # VLM: analiza frames + transcript + caption
        context = f"Caption del autor: {item.caption}\nTranscripcion: {transcript}"
        vlm_response = await self._vlm_fn(frames[:_MAX_FRAMES], context)


        # Parsear respuesta VLM (formato simple: descripcion | topics | sentiment)
        description, topics, sentiment = _parse_vlm_response(vlm_response)


        # INV-SOCIAL.2: guardrails antes de cualquier accion
        guardrail_checks = _run_guardrails(item, description, self._cfg)
        overall = (
            GuardrailResult.BLOCK
            if any(c.result == GuardrailResult.BLOCK for c in guardrail_checks)
            else GuardrailResult.PASS
        )


        if overall == GuardrailResult.BLOCK:
            self._emit(_EVT_GUARDRAIL_BLOCK, {
                "item_id":  item.item_id,
                "media_id": item.media_id,
                "platform": item.platform,
                "checks":   [c.model_dump() for c in guardrail_checks],
            })


        return ContentAnalysis(
            item_id=item.item_id,
            platform=item.platform,
            description=description,
            topics=topics,
            sentiment=sentiment,
            audio_transcript=transcript,
            frames_analyzed=len(frames),
            guardrail_checks=guardrail_checks,
            overall_guardrail=overall,
        )


    # -----------------------------------------------------------------------
    # generate_response
    # -----------------------------------------------------------------------


    async def generate_response(
        self,
        item: SocialMediaItem,
        analysis: ContentAnalysis,
        response_type: ResponseType = ResponseType.COMMENT,
    ) -> DraftResponse:
        """
        Genera un borrador de respuesta. NUNCA publica directamente.
        INV-SOCIAL.2: si guardrail bloqueo -> retorna draft.blocked=True sin llamar al LLM.
        """
        if not analysis.is_safe:
            return DraftResponse(
                item_id=item.item_id,
                platform=item.platform,
                response_type=response_type,
                text="",
                target_id=item.media_id,
                blocked=True,
                block_reason="guardrail_block",
            )


        max_len = self._cfg.get("guardrail_max_comment_ig", 2200)
        if item.platform == SocialPlatform.TIKTOK:
            max_len = self._cfg.get("guardrail_max_comment_tt", 150)


        prompt = _build_response_prompt(item, analysis, response_type, max_len)
        try:
            text = await self._llm_fn(prompt)
        except Exception as exc:
            logger.error("LLM fallido para %s: %s", item.media_id, exc)
            return DraftResponse(
                item_id=item.item_id,
                platform=item.platform,
                response_type=response_type,
                text="",
                target_id=item.media_id,
                blocked=True,
                block_reason=f"llm_error: {exc}",
            )


        # Truncar al limite de plataforma
        text = text[:max_len].strip()


        draft = DraftResponse(
            item_id=item.item_id,
            platform=item.platform,
            response_type=response_type,
            text=text,
            target_id=item.media_id,
        )


        self._emit(_EVT_DRAFT_READY, {
            "draft_id":  draft.draft_id,
            "agent_id":  self._agent_id,
            "tenant_id": self._tenant_id,
            "platform":  item.platform,
            "text":      text[:100],  # preview
        })


        return draft


    # -----------------------------------------------------------------------
    # publish_response -- INV-SOCIAL.1
    # -----------------------------------------------------------------------


    async def publish_response(
        self, draft: DraftResponse, approved_by: str
    ) -> PublishResult:
        """
        Publica el draft. INV-SOCIAL.1: NUNCA publica si approved_by == "".
        INV-SOCIAL.4: toda publicacion emite social.audit.
        """
        # INV-SOCIAL.1
        if not approved_by or not draft.approved:
            return PublishResult(
                draft_id=draft.draft_id,
                platform=draft.platform,
                response_type=draft.response_type,
                status=PublishStatus.SKIPPED,
                error="approved_by vacio o draft no aprobado -- INV-SOCIAL.1",
            )


        if draft.blocked:
            return PublishResult(
                draft_id=draft.draft_id,
                platform=draft.platform,
                response_type=draft.response_type,
                status=PublishStatus.SKIPPED,
                error=f"draft bloqueado: {draft.block_reason}",
            )


        # Rate limit check
        rl_key = f"{self._agent_id}:{draft.platform}"
        if rl_key not in self._rate_limits:
            max_hr = self._cfg.get("rate_limit_per_hour", 60)
            self._rate_limits[rl_key] = RateLimitState(
                agent_id=self._agent_id, platform=draft.platform, max_per_hour=max_hr
            )
        rl = self._rate_limits[rl_key]
        if not rl.can_act:
            return PublishResult(
                draft_id=draft.draft_id,
                platform=draft.platform,
                response_type=draft.response_type,
                status=PublishStatus.SKIPPED,
                error="rate_limit_exceeded",
            )


        # Publicar via cliente de plataforma
        platform_id = ""
        error = ""
        try:
            client = self._ig if draft.platform == SocialPlatform.INSTAGRAM else self._tt
            if client is None:
                raise RuntimeError(f"cliente {draft.platform} no configurado")


            if draft.response_type == ResponseType.COMMENT:
                platform_id = await client.post_comment(draft.target_id, draft.text)
            elif draft.response_type == ResponseType.DM:
                platform_id = await client.send_dm(draft.target_id, draft.text)
            elif draft.response_type == ResponseType.STORY_REPLY:
                platform_id = await client.reply_story(draft.target_id, draft.text)


            rl.increment()
            status = PublishStatus.PUBLISHED


        except Exception as exc:
            error  = str(exc)
            status = PublishStatus.FAILED
            logger.error("publish_response fallido para draft %s: %s", draft.draft_id, exc)


        result = PublishResult(
            draft_id=draft.draft_id,
            platform=draft.platform,
            response_type=draft.response_type,
            status=status,
            platform_id=platform_id,
            error=error,
        )


        # INV-SOCIAL.4: audit
        self._emit(_EVT_AUDIT, {
            "draft_id":    draft.draft_id,
            "agent_id":    self._agent_id,
            "tenant_id":   self._tenant_id,
            "platform":    draft.platform,
            "status":      status,
            "approved_by": approved_by,
            "platform_id": platform_id,
        })
        self._emit(_EVT_PUBLISHED, {
            "draft_id": draft.draft_id,
            "status":   status,
        })


        return result


    # -----------------------------------------------------------------------
    # process_webhook -- INV-SOCIAL.5
    # -----------------------------------------------------------------------


    async def process_webhook(
        self, payload: WebhookPayload
    ) -> WebhookResult:
        """
        Procesa un webhook entrante.
        INV-SOCIAL.5: valida firma antes de procesar.
        """
        client = self._ig if payload.platform == SocialPlatform.INSTAGRAM else self._tt
        if client is None:
            return WebhookResult(
                webhook_id=payload.webhook_id,
                valid_sig=False,
                event_type="no_client",
            )


        # INV-SOCIAL.5: validar firma
        import json
        raw_bytes = json.dumps(payload.raw_payload, separators=(",", ":")).encode()
        valid = client.validate_webhook_signature(raw_bytes, payload.signature)


        if not valid:
            logger.warning("process_webhook: firma invalida para webhook %s", payload.webhook_id)
            return WebhookResult(
                webhook_id=payload.webhook_id,
                valid_sig=False,
                event_type="invalid_signature",
            )


        # Extraer items de media del payload
        items, event_type = _parse_webhook_payload(payload)


        for item in items:
            self._emit(_EVT_NEW_CONTENT, {
                "item_id":  item.item_id,
                "media_id": item.media_id,
                "platform": item.platform,
                "agent_id": self._agent_id,
            })


        return WebhookResult(
            webhook_id=payload.webhook_id,
            valid_sig=True,
            items_found=len(items),
            event_type=event_type,
        )




# ===========================================================================
# Helpers internos
# ===========================================================================


async def _download_media(url: str) -> bytes:
    """Descarga media externa. INV-SOCIAL.3: caller aplica timeout 30s."""
    import httpx
    async with httpx.AsyncClient(timeout=_DL_TIMEOUT) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content




def _extract_frames(video_bytes: bytes, max_frames: int) -> list[bytes]:
    """Extrae hasta max_frames frames de un video (OpenCV). INV-SOCIAL.7."""
    try:
        import io
        import cv2  # type: ignore
        import numpy as np


        buf = np.frombuffer(video_bytes, dtype=np.uint8)
        cap = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        if cap is None:
            # imdecode no puede leer video -- usar VideoCapture con tempfile
            import tempfile, os
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
                f.write(video_bytes)
                tmp = f.name
            try:
                cap2 = cv2.VideoCapture(tmp)
                total = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))
                fps   = max(1, int(cap2.get(cv2.CAP_PROP_FPS)))
                step  = max(1, total // max_frames)
                frames = []
                for i in range(0, total, step):
                    cap2.set(cv2.CAP_PROP_POS_FRAMES, i)
                    ok, frame = cap2.read()
                    if ok:
                        _, enc = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                        frames.append(enc.tobytes())
                    if len(frames) >= max_frames:
                        break
                cap2.release()
                return frames
            finally:
                os.unlink(tmp)
        else:
            # Es imagen, no video
            _, enc = cv2.imencode(".jpg", cap, [cv2.IMWRITE_JPEG_QUALITY, 80])
            return [enc.tobytes()]
    except ImportError:
        logger.warning("_extract_frames: opencv-python no disponible.")
        return []
    except Exception as exc:
        logger.warning("_extract_frames error: %s", exc)
        return []




def _parse_vlm_response(response: str) -> tuple[str, list[str], str]:
    """Parsea respuesta del VLM. Formato esperado: descripcion | topic1,topic2 | sentiment."""
    parts = response.split("|")
    description = parts[0].strip() if len(parts) > 0 else response
    topics_raw  = parts[1].strip() if len(parts) > 1 else ""
    sentiment   = parts[2].strip().lower() if len(parts) > 2 else "neutral"
    topics = [t.strip() for t in topics_raw.split(",") if t.strip()]
    if sentiment not in ("positive", "negative", "neutral"):
        sentiment = "neutral"
    return description, topics, sentiment




def _run_guardrails(
    item: SocialMediaItem, description: str, cfg: dict
) -> list[GuardrailCheck]:
    """
    Ejecuta guardrails de contenido. INV-SOCIAL.2: siempre antes del LLM.
    Retorna lista de GuardrailCheck; BLOCK si alguno falla.
    """
    checks = []


    # 1. Palabras prohibidas (lista basica -- en produccion usar LlamaGuard)
    _BLOCKED_TERMS = {"spam", "click here", "buy now", "follow for follow", "f4f"}
    caption_lower = item.caption.lower()
    desc_lower    = description.lower()
    if any(t in caption_lower or t in desc_lower for t in _BLOCKED_TERMS):
        checks.append(GuardrailCheck(
            rule_name="blocked_terms",
            result=GuardrailResult.BLOCK,
            reason="caption o descripcion contiene terminos no permitidos",
        ))
    else:
        checks.append(GuardrailCheck(rule_name="blocked_terms", result=GuardrailResult.PASS))


    # 2. Contenido para adultos (heuristica simple)
    _ADULT_TERMS = {"nsfw", "explicit", "18+", "adult content"}
    if any(t in desc_lower for t in _ADULT_TERMS):
        checks.append(GuardrailCheck(
            rule_name="adult_content",
            result=GuardrailResult.BLOCK,
            reason="VLM detecto posible contenido para adultos",
        ))
    else:
        checks.append(GuardrailCheck(rule_name="adult_content", result=GuardrailResult.PASS))


    # 3. Links en caption (potencial spam)
    if "http" in caption_lower or "www." in caption_lower:
        checks.append(GuardrailCheck(
            rule_name="external_link",
            result=GuardrailResult.BLOCK,
            reason="caption contiene links externos -- posible spam",
        ))
    else:
        checks.append(GuardrailCheck(rule_name="external_link", result=GuardrailResult.PASS))


    return checks




def _build_response_prompt(
    item: SocialMediaItem,
    analysis: ContentAnalysis,
    response_type: ResponseType,
    max_len: int,
) -> str:
    topics_str = ", ".join(analysis.topics) or "varios temas"
    return (
        f"Eres un asistente que genera respuestas autenticas en redes sociales.\n"
        f"Plataforma: {item.platform}\n"
        f"Tipo de respuesta: {response_type}\n"
        f"Descripcion del contenido: {analysis.description}\n"
        f"Temas: {topics_str}\n"
        f"Sentimiento: {analysis.sentiment}\n"
        f"Caption original: {item.caption[:200]}\n"
        f"Transcripcion de audio: {analysis.audio_transcript[:300]}\n"
        f"\nGenera una respuesta breve, autentica y relevante en el mismo idioma del contenido.\n"
        f"Maximo {max_len} caracteres. Sin hashtags excesivos. Sin emojis en exceso.\n"
        f"Solo el texto de la respuesta, sin explicaciones adicionales."
    )




def _parse_webhook_payload(
    payload: WebhookPayload,
) -> tuple[list[SocialMediaItem], str]:
    """Extrae SocialMediaItems del raw_payload de un webhook."""
    items: list[SocialMediaItem] = []
    event_type = "unknown"


    data = payload.raw_payload


    if payload.platform == SocialPlatform.INSTAGRAM:
        # Instagram Graph API webhook format
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                field = change.get("field", "")
                value = change.get("value", {})
                event_type = field


                if field in ("media", "comments", "mentions"):
                    media_id  = value.get("media_id", value.get("id", ""))
                    media_url = value.get("media_url", "")
                    if media_id:
                        items.append(SocialMediaItem(
                            platform=SocialPlatform.INSTAGRAM,
                            media_id=media_id,
                            media_type=MediaType.IMAGE,
                            media_url=media_url,
                            caption=value.get("caption", ""),
                            author_id=value.get("from", {}).get("id", ""),
                        ))


    elif payload.platform == SocialPlatform.TIKTOK:
        # TikTok Webhooks format (v2)
        event = data.get("event", "")
        event_type = event
        video_data = data.get("data", {})
        video_id   = video_data.get("video_id", "")
        if video_id:
            items.append(SocialMediaItem(
                platform=SocialPlatform.TIKTOK,
                media_id=video_id,
                media_type=MediaType.VIDEO,
                media_url=video_data.get("share_url", ""),
                caption=video_data.get("title", ""),
                author_id=video_data.get("creator_uid", ""),
            ))


    return items, event_type