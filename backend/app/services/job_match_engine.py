import asyncio
import re
import uuid
from datetime import UTC, datetime
from typing import Any

import bleach
from loguru import logger

from app.i18n import DEFAULT_LOCALE, t
from app.schemas.match import MatchResult, ResumeLength, ResumeLengthStatus, score_to_tier
from app.services.injection_guard import find_suspicious_patterns
from app.services.minimax_client import MinimaxClient, MinimaxError, get_minimax
from app.services.security import decode_html_entities

_WORD_RE = re.compile(r"\S+")
_RESUME_TOO_SHORT = 300
_RESUME_TOO_LONG = 1000
_WORDS_PER_PAGE = 500


def _resume_length_analysis(cv_text: str, locale: str = DEFAULT_LOCALE) -> ResumeLength:
    word_count = len(_WORD_RE.findall(cv_text or ""))
    pages = round(word_count / _WORDS_PER_PAGE, 1) if word_count else 0.0
    if word_count < _RESUME_TOO_SHORT:
        status = ResumeLengthStatus.too_short
        message = t(locale, "resume_length.short")
    elif word_count > _RESUME_TOO_LONG:
        status = ResumeLengthStatus.too_long
        message = t(locale, "resume_length.long")
    else:
        status = ResumeLengthStatus.ideal
        message = t(locale, "resume_length.ideal")
    return ResumeLength(
        word_count=word_count,
        estimated_pages=pages,
        status=status,
        message=message,
    )


class ContentValidationError(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class LLMUnavailableError(Exception):
    pass


def _clean_str(value: Any, max_len: int | None = None) -> Any:
    if not isinstance(value, str):
        return value
    # bleach.clean() strips tags but also escapes the text it keeps, so a job
    # title like "Web Platform & Technology" came back as "&amp;" and the report
    # rendered the entity verbatim. Decoding undoes exactly that escaping: any
    # markup bleach removed is already gone, and anything the model had written
    # pre-escaped ("&lt;script&gt;") only unwinds one level, so it stays inert
    # text rather than becoming a tag. Frontend rendering escapes again anyway.
    cleaned = decode_html_entities(bleach.clean(value, tags=[], attributes={}, strip=True))
    if max_len is not None and len(cleaned) > max_len:
        return cleaned[: max_len - 1].rstrip() + "…"
    return cleaned


def _sanitize_match_payload(raw: dict) -> None:
    caps = {"candidate_name": 120, "job_title": 200, "company": 120, "tier_label": 60}
    for field, cap in caps.items():
        if field in raw:
            raw[field] = _clean_str(raw[field], cap)
    for strength in raw.get("strengths", []) or []:
        if isinstance(strength, dict):
            strength["text"] = _clean_str(strength.get("text"), 300)
            strength["evidence"] = _clean_str(strength.get("evidence"), 600)
    for gap in raw.get("gaps", []) or []:
        if isinstance(gap, dict):
            gap["text"] = _clean_str(gap.get("text"), 300)
            gap["how_to_close"] = _clean_str(gap.get("how_to_close"), 500)
    for action in raw.get("action_plan", []) or []:
        if isinstance(action, dict):
            action["description"] = _clean_str(action.get("description"), 400)
            action["estimated_duration"] = _clean_str(action.get("estimated_duration"), 60)
    for field in ("date_formatting", "standard_headings", "job_title_match"):
        value = raw.get(field)
        if not isinstance(value, dict):
            continue
        for key, item in list(value.items()):
            if isinstance(item, str):
                value[key] = _clean_str(item, 500)
            elif isinstance(item, list):
                value[key] = [_clean_str(entry, 300) for entry in item if isinstance(entry, str)]


async def process_match(
    *,
    cv_text: str,
    job_text: str,
    target_market: str = "",
    locale: str = DEFAULT_LOCALE,
    llm: MinimaxClient | None = None,
) -> MatchResult:
    resume_length = _resume_length_analysis(cv_text, locale=locale)

    if find_suspicious_patterns(cv_text):
        logger.warning("cv blocked by injection guard")
        raise ContentValidationError("suspicious_content_cv")
    if find_suspicious_patterns(job_text):
        logger.warning("job blocked by injection guard")
        raise ContentValidationError("suspicious_content_job")

    client = llm or get_minimax()
    cv_verdict, job_verdict = await asyncio.gather(
        client.judge(cv_text, kind="cv"),
        client.judge(job_text, kind="job"),
        return_exceptions=True,
    )
    for verdict in (cv_verdict, job_verdict):
        if isinstance(verdict, MinimaxError):
            raise LLMUnavailableError(str(verdict)) from verdict
        if isinstance(verdict, BaseException):
            raise verdict
    if not cv_verdict.get("is_cv") or not cv_verdict.get("is_safe"):
        raise ContentValidationError("cv_validation_failed")
    if not job_verdict.get("is_job_description") or not job_verdict.get("is_safe"):
        raise ContentValidationError("job_validation_failed")

    try:
        raw = await client.match(cv_text, job_text, target_market=target_market, locale=locale)
    except MinimaxError as exc:
        raise LLMUnavailableError(str(exc)) from exc
    if "error" in raw:
        raise ContentValidationError("insufficient_data")

    _sanitize_match_payload(raw)
    raw["match_id"] = str(uuid.uuid4())
    raw["generated_at"] = datetime.now(UTC).isoformat()
    raw["tier"] = score_to_tier(int(raw.get("score", 0))).value
    raw["resume_length"] = resume_length.model_dump(mode="json")
    return MatchResult.model_validate(raw)
