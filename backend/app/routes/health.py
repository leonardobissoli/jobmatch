from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "minimax": "configured" if settings.minimax_api_key else "not_configured",
        "local_llm": "enabled" if settings.local_llm_enabled else "disabled",
    }
