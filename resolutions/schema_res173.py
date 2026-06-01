# schema_res173.py
# RES.173 -- Instagram/TikTok AI Agents Schemas
# Autor: Claude Sonnet 4.6 · 2026-05-26
# MPAT4 -- Infraestructura Cognitiva Distribuida
# que has usado el formato de razonamiento adaptado por AGT


from __future__ import annotations


import uuid
from datetime import datetime
from enum import Enum
from typing import Any


from pydantic import BaseModel, Field




# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------


class SocialPlatform(str, Enum):
    INSTAGRAM = "instagram"
    TIKTOK    = "tiktok"




class MediaType(str, Enum):
    IMAGE   = "image"
    VIDEO   = "video"
    STORY   = "story"
    REEL    = "reel"
    CAROUSEL = "carousel"




class ResponseType(str, Enum):
    COMMENT      = "comment"
    DM           = "dm"
    STORY_REPLY  = "story_reply"




class GuardrailResult(str, Enum):
    PASS    = "pass"
    BLOCK   = "block"




class PublishStatus(str, Enum):
    PUBLISHED = "published"
    FAILED    = "failed"
    SKIPPED   = "skipped"   # guardrail bloqueo




# ---------------------------------------------------------------------------
# MEDIA
# ---------------------------------------------------------------------------


class SocialMediaItem(BaseModel, frozen=True):
    """Item de contenido de una red social (post, video, story, reel)."""
    item_id:    str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform:   SocialPlatform
    media_id:   str                         # ID nativo de la plataforma
    media_type: MediaType
    media_url:  str                         # URL de descarga (tiempo limitado)
    caption:    str       = ""
    author_id:  str       = ""
    author_name: str      = ""
    timestamp:  datetime  = Field(default_factory=datetime.utcnow)
    metadata:   dict[str, Any] = Field(default_factory=dict)




class VideoFrame(BaseModel, frozen=True):
    """Frame extraido de un video para analisis VLM."""
    frame_id:      str     = Field(default_factory=lambda: str(uuid.uuid4()))
    media_id:      str
    frame_index:   int     = Field(ge=0)
    timestamp_sec: float   = Field(ge=0.0)
    image_bytes:   bytes                    # JPEG/PNG del frame




# ---------------------------------------------------------------------------
# ANALISIS DE CONTENIDO
# ---------------------------------------------------------------------------


class GuardrailCheck(BaseModel, frozen=True):
    """Resultado de una comprobacion de guardrail individual."""
    rule_name:  str
    result:     GuardrailResult
    reason:     str = ""




class ContentAnalysis(BaseModel, frozen=True):
    """Resultado del analisis de un SocialMediaItem por el VLM."""
    analysis_id:         str     = Field(default_factory=lambda: str(uuid.uuid4()))
    item_id:             str
    platform:            SocialPlatform
    description:         str     = ""      # descripcion del VLM
    topics:              list[str] = Field(default_factory=list)
    sentiment:           str     = "neutral"  # positive | negative | neutral
    engagement_potential: float  = Field(ge=0.0, le=1.0, default=0.5)
    audio_transcript:    str     = ""      # de WhisperSTT si hay audio
    frames_analyzed:     int     = 0
    guardrail_checks:    list[GuardrailCheck] = Field(default_factory=list)
    overall_guardrail:   GuardrailResult = GuardrailResult.PASS
    analyzed_at:         datetime = Field(default_factory=datetime.utcnow)


    @property
    def is_safe(self) -> bool:
        return self.overall_guardrail == GuardrailResult.PASS




# ---------------------------------------------------------------------------
# DRAFT Y PUBLICACION
# ---------------------------------------------------------------------------


class DraftResponse(BaseModel):
    """Borrador de respuesta generado por el LLM. Requiere aprobacion antes de publicar."""
    draft_id:    str     = Field(default_factory=lambda: str(uuid.uuid4()))
    item_id:     str
    platform:    SocialPlatform
    response_type: ResponseType
    text:        str
    target_id:   str                        # media_id o user_id segun response_type
    blocked:     bool    = False            # True si guardrail bloqueo
    block_reason: str    = ""
    approved:    bool    = False            # INV-SOCIAL.1: nunca True por defecto
    approved_by: str     = ""
    approved_at: datetime | None = None
    created_at:  datetime = Field(default_factory=datetime.utcnow)




class PublishResult(BaseModel, frozen=True):
    """Resultado de publicar un DraftResponse aprobado."""
    publish_id:   str     = Field(default_factory=lambda: str(uuid.uuid4()))
    draft_id:     str
    platform:     SocialPlatform
    response_type: ResponseType
    status:       PublishStatus
    platform_id:  str     = ""             # ID del comentario/DM publicado
    error:        str     = ""
    published_at: datetime = Field(default_factory=datetime.utcnow)




# ---------------------------------------------------------------------------
# WEBHOOK
# ---------------------------------------------------------------------------


class WebhookPayload(BaseModel, frozen=True):
    """Payload de webhook recibido de Instagram o TikTok."""
    webhook_id:  str     = Field(default_factory=lambda: str(uuid.uuid4()))
    platform:    SocialPlatform
    raw_payload: dict[str, Any]
    signature:   str     = ""
    received_at: datetime = Field(default_factory=datetime.utcnow)




class WebhookResult(BaseModel, frozen=True):
    """Resultado de procesar un WebhookPayload."""
    webhook_id:  str
    valid_sig:   bool
    items_found: int     = 0
    event_type:  str     = ""              # new_media | comment | dm | mention
    processed_at: datetime = Field(default_factory=datetime.utcnow)




# ---------------------------------------------------------------------------
# RATE LIMIT
# ---------------------------------------------------------------------------


class RateLimitState(BaseModel):
    """Estado de rate limit por plataforma y agente. Mutable."""
    agent_id:       str
    platform:       SocialPlatform
    actions_this_hour: int      = 0
    window_start:   datetime    = Field(default_factory=datetime.utcnow)
    max_per_hour:   int         = Field(default=60)


    @property
    def can_act(self) -> bool:
        return self.actions_this_hour < self.max_per_hour


    def increment(self) -> None:
        """Incrementa el contador. Resetea si la ventana expiro."""
        now = datetime.utcnow()
        elapsed = (now - self.window_start).total_seconds()
        if elapsed >= 3600:
            self.actions_this_hour = 0
            self.window_start = now
        self.actions_this_hour += 1