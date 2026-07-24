import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as value:
        yield value


@pytest.mark.asyncio
async def test_health_describes_local_runtime(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["local_llm"] == "enabled"


def test_match_contract_has_no_email_or_consent() -> None:
    schema = app.openapi()
    request_schema = schema["paths"]["/api/v1/match"]["post"]["requestBody"]["content"]["multipart/form-data"]["schema"]
    ref = request_schema["$ref"].split("/")[-1]
    properties = schema["components"]["schemas"][ref]["properties"]
    assert "email" not in properties
    assert "consent" not in properties
    assert "consent_text" not in properties
    assert "consent_version" not in properties


@pytest.mark.asyncio
async def test_match_requires_exactly_one_job_input(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/match",
        files={"cv": ("cv.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "validation_error"
