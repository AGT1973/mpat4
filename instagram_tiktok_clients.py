# instagram_client.py + tiktok_client.py
# RES.173 -- Social Platform Clients
# Autor: Claude Sonnet 4.6 · 2026-05-26
# MPAT4 -- Infraestructura Cognitiva Distribuida
# que has usado el formato de razonamiento adaptado por AGT
#
# DT-RES173-01: Integracion real con Meta Graph API v20 (requiere app aprobada)
# DT-RES173-02: TikTok API -- acceso aun restringido para developers en 2026


from __future__ import annotations


import hashlib
import hmac
import logging
from typing import Any


logger = logging.getLogger("mpat4.social.clients")




# ===========================================================================
# BaseSocialClient
# ===========================================================================


class BaseSocialClient:
    """Interfaz base para clientes de plataformas sociales."""


    async def post_comment(self, media_id: str, text: str) -> str:
        raise NotImplementedError


    async def send_dm(self, user_id: str, text: str) -> str:
        raise NotImplementedError


    async def reply_story(self, story_id: str, text: str) -> str:
        raise NotImplementedError


    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        raise NotImplementedError




# ===========================================================================
# InstagramClient
# ===========================================================================


class InstagramClient(BaseSocialClient):
    """
    Cliente para Instagram Graph API v20+.


    DT-RES173-01: Esta implementacion usa httpx pero requiere una app Meta
    aprobada con permisos instagram_basic, instagram_manage_comments,
    instagram_manage_messages para funcionar en produccion.


    En tests se usa MockInstagramClient (abajo).


    Referencia API:
      POST /{media-id}/comments     -- publicar comentario
      POST /me/messages             -- enviar DM (Instagram Messaging API)
      POST /{comment-id}/replies    -- reply a story reply
    """


    _API_BASE = "https://graph.instagram.com/v20.0"


    def __init__(self, access_token: str, app_secret: str) -> None:
        self._token      = access_token
        self._app_secret = app_secret


    async def post_comment(self, media_id: str, text: str) -> str:
        """Publica un comentario en un media de Instagram."""
        import httpx
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._API_BASE}/{media_id}/comments",
                params={"access_token": self._token},
                json={"message": text},
            )
            resp.raise_for_status()
            data = resp.json()
            comment_id = data.get("id", "")
            logger.info("InstagramClient: comentario publicado id=%s", comment_id)
            return comment_id


    async def send_dm(self, user_id: str, text: str) -> str:
        """Envia un DM via Instagram Messaging API."""
        import httpx
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._API_BASE}/me/messages",
                params={"access_token": self._token},
                json={
                    "recipient": {"id": user_id},
                    "message":   {"text": text},
                },
            )
            resp.raise_for_status()
            data = resp.json()
            msg_id = data.get("message_id", "")
            logger.info("InstagramClient: DM enviado id=%s", msg_id)
            return msg_id


    async def reply_story(self, story_id: str, text: str) -> str:
        """Responde a una Story reply (comentario en story)."""
        # Stories replies usan el mismo endpoint que comentarios
        return await self.post_comment(story_id, text)


    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Valida X-Hub-Signature-256 de Meta Graph API.
        INV-SOCIAL.5: debe llamarse antes de procesar cualquier webhook.
        """
        if not signature.startswith("sha256="):
            return False
        expected = hmac.new(
            self._app_secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        provided = signature.removeprefix("sha256=")
        return hmac.compare_digest(expected, provided)


    async def get_media(self, media_id: str) -> dict[str, Any]:
        """Obtiene metadata de un media item."""
        import httpx
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{self._API_BASE}/{media_id}",
                params={
                    "access_token": self._token,
                    "fields": "id,media_type,media_url,caption,timestamp,username",
                },
            )
            resp.raise_for_status()
            return resp.json()




# ===========================================================================
# TikTokClient
# ===========================================================================


class TikTokClient(BaseSocialClient):
    """
    Cliente para TikTok Graph API Webhooks v2.


    DT-RES173-02: TikTok Graph API aun tiene acceso restringido para developers
    independientes en 2026. Esta implementacion esta lista para cuando se apruebe.


    Endpoints relevantes:
      POST /v2/comment/publish/      -- publicar comentario en video
      POST /v2/dm/send/              -- enviar DM
    """


    _API_BASE = "https://open.tiktokapis.com/v2"


    def __init__(self, access_token: str, app_secret: str) -> None:
        self._token      = access_token
        self._app_secret = app_secret


    async def post_comment(self, video_id: str, text: str) -> str:
        """Publica un comentario en un video de TikTok."""
        import httpx
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._API_BASE}/comment/publish/",
                headers={"Authorization": f"Bearer {self._token}"},
                json={"video_id": video_id, "text": text},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("comment_id", "")


    async def send_dm(self, user_id: str, text: str) -> str:
        """Envia un DM en TikTok."""
        import httpx
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{self._API_BASE}/dm/send/",
                headers={"Authorization": f"Bearer {self._token}"},
                json={"recipient_user_id": user_id, "message": {"text": text}},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("message_id", "")


    async def reply_story(self, story_id: str, text: str) -> str:
        """TikTok no tiene Stories en el sentido de Instagram -- usa post_comment."""
        return await self.post_comment(story_id, text)


    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Valida firma HMAC-SHA256 de TikTok Webhooks.
        INV-SOCIAL.5.
        """
        expected = hmac.new(
            self._app_secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)




# ===========================================================================
# Mock clients para tests
# ===========================================================================


class MockInstagramClient(BaseSocialClient):
    """Cliente mock para tests. Registra llamadas sin hacer requests HTTP."""


    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []


    async def post_comment(self, media_id: str, text: str) -> str:
        self.calls.append({"method": "post_comment", "media_id": media_id, "text": text})
        return f"mock_comment_{media_id}"


    async def send_dm(self, user_id: str, text: str) -> str:
        self.calls.append({"method": "send_dm", "user_id": user_id, "text": text})
        return f"mock_dm_{user_id}"


    async def reply_story(self, story_id: str, text: str) -> str:
        self.calls.append({"method": "reply_story", "story_id": story_id, "text": text})
        return f"mock_reply_{story_id}"


    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        return True   # siempre valido en tests




class MockTikTokClient(MockInstagramClient):
    """Mock para TikTok -- misma logica que Instagram mock."""
    pass