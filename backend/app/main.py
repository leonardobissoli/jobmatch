from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import get_settings
from app.i18n import resolve_locale
from app.logging_setup import configure_logging
from app.middleware_size import MaxBodySizeMiddleware
from app.routes import health, local, match


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("starting local Job Match backend")
    yield


app = FastAPI(title="Job Match Local API", version="1.0.0", lifespan=lifespan)
settings = get_settings()

app.add_middleware(MaxBodySizeMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def locale_resolver(request: Request, call_next):
    request.state.locale = resolve_locale(
        accept_language=request.headers.get("accept-language"),
    )
    return await call_next(request)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


app.include_router(health.router, prefix="/api/v1")
app.include_router(match.router, prefix="/api/v1")
app.include_router(local.router, prefix="/api/v1")
