from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services import local_llm
from app.services.minimax_client import JSON_MODE_OBJECT, JSON_MODE_SCHEMA


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("http://localhost:11434", "http://localhost:11434"),
        ("http://127.0.0.1:1234/v1", "http://127.0.0.1:1234"),
        ("http://[::1]:11434/", "http://[::1]:11434"),
    ],
)
def test_validate_base_url_accepts_loopback(raw: str, expected: str) -> None:
    assert local_llm.validate_base_url(raw) == expected


@pytest.mark.parametrize(
    "raw",
    [
        "http://example.com:11434",
        "http://host.docker.internal:11434",
        "http://10.0.0.5:11434",
        "file:///tmp/model",
        "http://user:pass@localhost:11434",
    ],
)
def test_validate_base_url_rejects_non_loopback(raw: str) -> None:
    with pytest.raises(local_llm.LocalLLMConfigError):
        local_llm.validate_base_url(raw)


def test_transport_maps_loopback_to_docker_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        local_llm,
        "get_settings",
        lambda: SimpleNamespace(local_llm_host="host.docker.internal"),
    )
    assert local_llm._transport_base_url("http://localhost:11434") == "http://host.docker.internal:11434"


def test_build_client_uses_provider_json_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = SimpleNamespace(
        local_llm_host="localhost",
        local_llm_timeout_seconds=300,
        minimax_base_url="https://api.minimax.io/v1",
        minimax_api_key="",
        minimax_model="MiniMax-M2.7",
        minimax_timeout_seconds=180,
    )
    monkeypatch.setattr(local_llm, "get_settings", lambda: settings)
    monkeypatch.setattr("app.services.minimax_client.get_settings", lambda: settings)
    assert local_llm.build_client("ollama", "http://localhost:11434", "model").json_mode == JSON_MODE_OBJECT
    assert local_llm.build_client("lmstudio", "http://localhost:1234", "model").json_mode == JSON_MODE_SCHEMA


@pytest.mark.asyncio
async def test_local_config_lists_both_providers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(local_llm, "is_enabled", lambda: True)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/local/config")
    assert response.status_code == 200
    assert {item["id"] for item in response.json()["providers"]} == {"ollama", "lmstudio"}


@pytest.mark.asyncio
async def test_local_models_rejects_remote_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(local_llm, "is_enabled", lambda: True)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/local/models",
            json={"provider": "ollama", "base_url": "http://example.com:11434"},
        )
    assert response.status_code == 400
