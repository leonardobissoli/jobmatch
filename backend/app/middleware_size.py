"""SEC-046 (re-implementação) — ASGI middleware que aborta uploads antes do
parser do FastAPI. O middleware roda ANTES de qualquer endpoint dispatcher,
então o multipart nunca é totalmente lido se exceder o cap.

Comportamento:
- POST com Content-Length acima do cap → 413 imediato (sem ler body).
- POST sem Content-Length: ASGI receive() é decorado pra contar bytes;
  ao ultrapassar o cap, próximo receive devolve 413 e fecha o ciclo.
- Outros métodos passam direto.
"""
import json

from app.config import get_settings
from app.i18n import resolve_locale, t


def _max_total_bytes() -> int:
    s = get_settings()
    return s.max_cv_bytes + s.max_job_bytes + 64 * 1024  # 64KB form overhead


def _payload_too_large_bytes(locale: str) -> bytes:
    return json.dumps(
        {
            "error": "payload_too_large",
            "message": t(locale, "errors.payload_too_large_combined"),
        },
        ensure_ascii=False,
    ).encode()


def _negotiate_locale(scope: dict) -> str:
    # Accept-Language comes through scope headers in raw bytes.
    for name, value in scope.get("headers", []):
        if name == b"accept-language":
            try:
                return resolve_locale(value.decode("latin-1", errors="ignore"))
            except Exception:
                return resolve_locale(None)
    return resolve_locale(None)


async def _send_413(send, locale: str) -> None:
    body = _payload_too_large_bytes(locale)
    await send(
        {
            "type": "http.response.start",
            "status": 413,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body, "more_body": False})


class MaxBodySizeMiddleware:
    """Pure ASGI middleware to cap request body size.

    Must be added BEFORE the FastAPI/Starlette routing layer so it runs
    before multipart parsing.
    """

    def __init__(self, app, max_bytes_callable=None):
        self.app = app
        self._cap_fn = max_bytes_callable or _max_total_bytes

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "").upper()
        if method not in ("POST", "PUT", "PATCH"):
            await self.app(scope, receive, send)
            return

        cap = self._cap_fn()
        locale = _negotiate_locale(scope)

        # 1. Cheap: Content-Length header
        for name, value in scope.get("headers", []):
            if name == b"content-length":
                try:
                    if int(value) > cap:
                        await _send_413(send, locale)
                        return
                except ValueError:
                    pass
                break

        # 2. Streaming: count bytes as the app pulls them
        received = 0
        rejected = False

        async def capped_receive():
            nonlocal received, rejected
            if rejected:
                return {"type": "http.disconnect"}
            message = await receive()
            if message.get("type") == "http.request":
                body = message.get("body", b"") or b""
                received += len(body)
                if received > cap:
                    rejected = True
                    return {"type": "http.disconnect"}
            return message

        sent_response = False

        async def gated_send(message):
            nonlocal sent_response
            if rejected and not sent_response:
                sent_response = True
                await _send_413(send, locale)
                return
            if not sent_response:
                await send(message)

        await self.app(scope, capped_receive, gated_send)

        if rejected and not sent_response:
            sent_response = True
            await _send_413(send, locale)
