from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError as PydanticValidationError

from app.config import get_settings
from app.i18n import resolve_locale, t
from app.schemas.match import ErrorResponse, MatchResult
from app.services import local_llm
from app.services.job_match_engine import ContentValidationError, LLMUnavailableError, process_match
from app.services.pdf_parser import PdfParseError, extract_pdf_text
from app.services.txt_parser import TxtParseError, parse_txt

router = APIRouter()
_INTERNAL_MARKETS = {"", "NONE", "BR", "PT", "UK", "EU", "US"}
_CONTENT_VALIDATION_KEYS = {
    "insufficient_data": "errors.content.insufficient_data",
    "cv_validation_failed": "errors.content.cv_validation_failed",
    "job_validation_failed": "errors.content.job_validation_failed",
    "suspicious_content_cv": "errors.content.suspicious_content_cv",
    "suspicious_content_job": "errors.content.suspicious_content_job",
}
_CONTENT_VALIDATION_MESSAGES = {
    code: t("pt-BR", key) for code, key in _CONTENT_VALIDATION_KEYS.items()
}
_CONTENT_VALIDATION_FALLBACK = t("pt-BR", "errors.content.fallback")


def _err(status: int, code: str, message: str, **extra) -> JSONResponse:
    payload = ErrorResponse(error=code, message=message, **extra).model_dump(exclude_none=True)
    return JSONResponse(status_code=status, content=payload)


async def _read_capped(upload: UploadFile, cap: int) -> bytes | None:
    buffer = bytearray()
    while chunk := await upload.read(64 * 1024):
        buffer.extend(chunk)
        if len(buffer) > cap:
            return None
    return bytes(buffer)


def _pdf_message(exc: PdfParseError, locale: str) -> str:
    message = str(exc)
    mapping = {
        "dangerous pdf feature: /Encrypt": "pdf.password_protected",
        "invalid PDF magic bytes": "pdf.invalid_magic",
        "pdf has insufficient text content": "pdf.no_text",
        "pdf extraction timeout": "pdf.timeout",
        "pdf too large to parse": "pdf.too_large",
    }
    if message == "dangerous pdf feature: /Encrypt":
        return t(locale, "pdf.password_protected")
    if message.startswith("dangerous pdf feature:"):
        return t(locale, "pdf.dangerous_feature")
    if message.startswith("pdfplumber failed"):
        return t(locale, "pdf.corrupt")
    return t(locale, mapping.get(message, "pdf.fallback"))


def _txt_message(exc: TxtParseError, locale: str) -> str:
    message = str(exc)
    mapping = {
        "empty job description": "txt.empty",
        "job description too short": "txt.too_short",
    }
    if message.startswith("binary content rejected"):
        return t(locale, "txt.binary")
    if message.startswith("decode failed"):
        return t(locale, "txt.decode")
    return t(locale, mapping.get(message, "txt.fallback"))


def _pdf_user_message(exc: PdfParseError, locale: str = "pt-BR") -> str:
    return _pdf_message(exc, locale)


def _txt_user_message(exc: TxtParseError, locale: str = "pt-BR") -> str:
    return _txt_message(exc, locale)


@router.post("/match", response_model=MatchResult, response_model_exclude_none=True)
async def post_match(
    request: Request,
    cv: UploadFile = File(...),
    job: UploadFile | None = File(None),
    job_text: str = Form(""),
    target_market: str = Form(""),
    locale_form: str = Form("", alias="locale"),
    llm_provider: str = Form(""),
    llm_base_url: str = Form(""),
    llm_model: str = Form(""),
):
    settings = get_settings()
    locale = resolve_locale(
        accept_language=request.headers.get("accept-language"),
        form_locale=locale_form,
    )

    llm = None
    if settings.local_llm_enabled and llm_provider.strip():
        try:
            llm = local_llm.build_client(llm_provider, llm_base_url, llm_model)
        except local_llm.LocalLLMError:
            return _err(400, "validation_error", t(locale, "errors.local_llm_invalid"))

    job_text_input = job_text.strip()
    has_job_file = job is not None and bool((job.filename or "").strip())
    if has_job_file == bool(job_text_input):
        key = "errors.cv_job_conflict" if has_job_file else "errors.missing_job"
        return _err(400, "validation_error", t(locale, key))

    content_length = request.headers.get("content-length", "")
    total_cap = settings.max_cv_bytes + settings.max_job_bytes + 64 * 1024
    if content_length.isdigit() and int(content_length) > total_cap:
        return _err(413, "payload_too_large", t(locale, "errors.payload_too_large_combined"))

    if (cv.content_type or "").lower() != "application/pdf":
        return _err(422, "content_validation_failed", t(locale, "errors.invalid_cv_type"))
    if has_job_file and job is not None:
        content_type = (job.content_type or "").lower()
        if not (content_type.startswith("text/") or content_type == "application/octet-stream"):
            return _err(422, "content_validation_failed", t(locale, "errors.invalid_job_type"))

    cv_bytes = await _read_capped(cv, settings.max_cv_bytes)
    if cv_bytes is None:
        return _err(413, "payload_too_large", t(locale, "errors.cv_too_large"))
    if has_job_file and job is not None:
        job_bytes = await _read_capped(job, settings.max_job_bytes)
        if job_bytes is None:
            return _err(413, "payload_too_large", t(locale, "errors.job_too_large"))
    else:
        job_bytes = job_text_input.encode("utf-8")
        if len(job_bytes) > settings.max_job_bytes:
            return _err(413, "payload_too_large", t(locale, "errors.job_too_large"))

    try:
        cv_text = await extract_pdf_text(cv_bytes)
    except PdfParseError as exc:
        return _err(422, "content_validation_failed", _pdf_message(exc, locale))
    try:
        parsed_job = parse_txt(job_bytes)
    except TxtParseError as exc:
        return _err(422, "content_validation_failed", _txt_message(exc, locale))

    market = target_market.strip()[:60]
    if market not in _INTERNAL_MARKETS:
        market = ""
    try:
        return await process_match(
            cv_text=cv_text,
            job_text=parsed_job,
            target_market=market,
            locale=locale,
            llm=llm,
        )
    except ContentValidationError as exc:
        if exc.code == "insufficient_data" and llm is not None:
            message = t(locale, "errors.local_llm_insufficient_data")
        else:
            message = t(locale, _CONTENT_VALIDATION_KEYS.get(exc.code, "errors.content.fallback"))
        return _err(422, "content_validation_failed", message, details=exc.code)
    except LLMUnavailableError as exc:
        logger.error("llm unavailable: {}", exc)
        return _err(503, "llm_unavailable", t(locale, "errors.llm_unavailable"))
    except PydanticValidationError as exc:
        logger.warning("llm output failed schema validation: {}", str(exc)[:300])
        key = "errors.local_llm_bad_output" if llm is not None else "errors.internal"
        status = 422 if llm is not None else 500
        return _err(status, "content_validation_failed" if llm is not None else "internal_error", t(locale, key))
    except Exception as exc:
        logger.exception("unexpected match error: {}", exc)
        return _err(500, "internal_error", t(locale, "errors.internal"))
