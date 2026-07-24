"""ADR-026 — "run local" mode: Ollama / LM Studio on the same machine.

Both providers speak the OpenAI-compatible `/v1/chat/completions` contract
(including `response_format: {"type": "json_object"}`), so the whole prompt
pipeline in `minimax_client.py` is reused as-is. Only the transport target
changes.

Security model — the base URL originates from the client, which would be a
textbook SSRF vector against whatever network the backend can reach. Two
independent layers:

1. `LOCAL_LLM_ENABLED`. When it is off the routes 404 and `routes/match.py`
   ignores the form fields entirely.
2. `validate_base_url()` — a *literal* host allowlist. Deliberately NOT a
   DNS resolution check: resolving means an attacker-controlled name that
   points at 127.0.0.1 would pass, and rebinding could flip it afterwards.
   Comparing the literal hostname makes both impossible.
"""
from __future__ import annotations

from typing import TypedDict
from urllib.parse import urlparse

import httpx
from loguru import logger

from app.config import get_settings
from app.services.minimax_client import JSON_MODE_OBJECT, JSON_MODE_SCHEMA, MinimaxClient


class ProviderSpec(TypedDict):
    default_base_url: str
    models_path: str
    json_mode: str


PROVIDERS: dict[str, ProviderSpec] = {
    "ollama": {
        "default_base_url": "http://localhost:11434",
        "models_path": "/api/tags",
        # Ollama's OpenAI-compat layer accepts json_object, same as MiniMax.
        "json_mode": JSON_MODE_OBJECT,
    },
    "lmstudio": {
        "default_base_url": "http://localhost:1234",
        "models_path": "/v1/models",
        # LM Studio rejects json_object outright:
        #   "'response_format.type' must be 'json_schema' or 'text'"
        "json_mode": JSON_MODE_SCHEMA,
    },
}

# Literal loopback hosts only. See module docstring for why this is not a
# DNS-resolution check.
_ALLOWED_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})

_ALLOWED_SCHEMES = frozenset({"http", "https"})

# Probing the model list must stay cheap — it runs on a button press.
_PROBE_TIMEOUT_SECONDS = 5.0

MAX_MODEL_NAME_LEN = 120


class LocalLLMError(Exception):
    """The local server could not be reached or answered with garbage."""


class LocalLLMConfigError(LocalLLMError):
    """The provider / base URL / model supplied by the client is invalid.

    Separate type so callers can answer 400 (bad config) vs 502 (config fine,
    server down) without string-matching the message.
    """


def is_enabled() -> bool:
    return get_settings().local_llm_enabled


def validate_provider(provider: str) -> str:
    key = (provider or "").strip().lower()
    if key not in PROVIDERS:
        raise LocalLLMConfigError(f"unknown provider: {key[:30]!r}")
    return key


def validate_base_url(url: str) -> str:
    """Return a normalized loopback base URL, or raise LocalLLMError.

    Normalization strips trailing slashes and a trailing `/v1` so callers can
    append provider-specific paths without doubling the segment.
    """
    raw = (url or "").strip()
    if not raw or len(raw) > 200:
        raise LocalLLMConfigError("base_url missing or too long")

    parsed = urlparse(raw)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise LocalLLMConfigError(f"scheme not allowed: {parsed.scheme[:20]!r}")
    if parsed.username or parsed.password:
        raise LocalLLMConfigError("userinfo not allowed in base_url")
    if parsed.query or parsed.fragment:
        raise LocalLLMConfigError("query/fragment not allowed in base_url")

    # urlparse strips the brackets from an IPv6 literal, so "::1" is what we
    # compare against; `_ALLOWED_HOSTS` holds the unbracketed form.
    hostname = (parsed.hostname or "").lower()
    if hostname not in _ALLOWED_HOSTS:
        raise LocalLLMConfigError(f"host not allowed: {hostname[:60]!r}")

    try:
        port = parsed.port
    except ValueError as e:  # malformed port, e.g. "http://localhost:abc"
        raise LocalLLMConfigError("invalid port") from e
    if port is not None and not (1 <= port <= 65535):
        raise LocalLLMConfigError("port out of range")

    path = parsed.path.rstrip("/")
    if path.endswith("/v1"):
        path = path[: -len("/v1")]
    if path and not path.startswith("/"):
        raise LocalLLMConfigError("invalid path")

    netloc = f"[{hostname}]" if ":" in hostname else hostname
    if port is not None:
        netloc = f"{netloc}:{port}"
    return f"{parsed.scheme}://{netloc}{path}"


def validate_model(model: str) -> str:
    name = (model or "").strip()
    if not name:
        raise LocalLLMConfigError("model is required")
    if len(name) > MAX_MODEL_NAME_LEN:
        raise LocalLLMConfigError("model name too long")
    return name


def _transport_base_url(base_url: str) -> str:
    """Map loopback URLs to the Docker host without trusting client hosts."""
    parsed = urlparse(base_url)
    transport_host = get_settings().local_llm_host.strip().lower()
    if transport_host not in {"localhost", "host.docker.internal"}:
        raise LocalLLMConfigError("invalid LOCAL_LLM_HOST")
    host = f"[{transport_host}]" if ":" in transport_host else transport_host
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"
    return f"{parsed.scheme}://{host}{parsed.path.rstrip('/')}"


async def list_models(provider: str, base_url: str) -> list[str]:
    """Probe the local server for installed models.

    Ollama exposes `/api/tags` (`{"models": [{"name": ...}]}`); LM Studio
    exposes the OpenAI-shaped `/v1/models` (`{"data": [{"id": ...}]}`).
    """
    key = validate_provider(provider)
    base = validate_base_url(base_url)
    url = f"{_transport_base_url(base)}{PROVIDERS[key]['models_path']}"

    try:
        async with httpx.AsyncClient(timeout=_PROBE_TIMEOUT_SECONDS) as client:
            resp = await client.get(url)
    except httpx.HTTPError as e:
        logger.info("local llm probe failed provider={} err={}", key, type(e).__name__)
        raise LocalLLMError("unreachable") from e

    if resp.status_code != 200:
        logger.info("local llm probe non-200 provider={} status={}", key, resp.status_code)
        raise LocalLLMError(f"http {resp.status_code}")

    try:
        data = resp.json()
    except ValueError as e:
        raise LocalLLMError("invalid JSON from local server") from e

    if key == "ollama":
        entries = data.get("models") or []
        names = [m.get("name") for m in entries if isinstance(m, dict)]
    else:
        entries = data.get("data") or []
        names = [m.get("id") for m in entries if isinstance(m, dict)]

    models = [n for n in names if isinstance(n, str) and n.strip()]
    if not models:
        raise LocalLLMError("no models installed")
    return sorted(models)


def build_client(provider: str, base_url: str, model: str) -> MinimaxClient:
    """OpenAI-compatible client pointed at the local server.

    No API key: a local run costs nothing and the server does not authenticate.
    """
    key = validate_provider(provider)
    base = validate_base_url(base_url)
    name = validate_model(model)
    s = get_settings()
    logger.info("local llm client provider={} model={}", key, name)
    return MinimaxClient(
        base_url=f"{_transport_base_url(base)}/v1",
        api_key="",
        model=name,
        timeout=s.local_llm_timeout_seconds,
        require_api_key=False,
        json_mode=PROVIDERS[key]["json_mode"],
    )


def llm_tag(provider: str, model: str) -> str:
    """Cache-key discriminator so a MiniMax result is never served for a local
    run (and vice versa). See job_match_engine.process_match."""
    return f"{provider}:{model}"
