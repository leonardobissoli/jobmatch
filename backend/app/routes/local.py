from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.i18n import resolve_locale, t
from app.services import local_llm

router = APIRouter()


def _require_enabled() -> None:
    if not local_llm.is_enabled():
        raise HTTPException(status_code=404)


@router.get("/local/config")
async def local_config() -> JSONResponse:
    _require_enabled()
    return JSONResponse(
        {
            "enabled": True,
            "providers": [
                {"id": key, "default_base_url": spec["default_base_url"]}
                for key, spec in local_llm.PROVIDERS.items()
            ],
        }
    )


class ModelsRequest(BaseModel):
    provider: str = Field(max_length=30)
    base_url: str = Field(max_length=200)


@router.post("/local/models")
async def local_models(request: Request, body: ModelsRequest) -> JSONResponse:
    _require_enabled()
    locale = resolve_locale(accept_language=request.headers.get("accept-language"))
    try:
        models = await local_llm.list_models(body.provider, body.base_url)
    except local_llm.LocalLLMConfigError:
        return JSONResponse(
            {"error": "validation_error", "message": t(locale, "errors.local_llm_invalid")},
            status_code=400,
        )
    except local_llm.LocalLLMError:
        return JSONResponse(
            {
                "error": "local_llm_unreachable",
                "message": t(locale, "errors.local_llm_unreachable"),
            },
            status_code=502,
        )
    return JSONResponse({"models": models})
