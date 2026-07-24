import asyncio
import io
import re

import pdfplumber
from loguru import logger

from app.services.security import sanitize_extracted_text


class PdfParseError(Exception):
    pass


# SEC-057 — Dangerous PDF object-level keywords. pdfplumber only renders text
# and does not execute these features, but their presence is a strong signal
# of a crafted/weaponized PDF (auto-actions, JavaScript, embedded files,
# external launches, XFA). Reject before parsing.
#
# Patterns are anchored on the `/` PDF name-token marker with a negative
# lookahead so we don't match longer names (e.g. `/JavaScriptFoo`, `/AAPL`
# would never appear with a leading `/` in real CV text anyway, but the
# lookahead keeps the rule precise). `/URI` is intentionally NOT here — legit
# CVs link to LinkedIn/GitHub/portfolios.
_DANGEROUS_PDF_KEYWORDS: list[re.Pattern[bytes]] = [
    re.compile(rb"/JavaScript(?![A-Za-z0-9_])"),
    re.compile(rb"/JS(?![A-Za-z0-9_])"),
    re.compile(rb"/Launch(?![A-Za-z0-9_])"),
    re.compile(rb"/OpenAction(?![A-Za-z0-9_])"),
    re.compile(rb"/AA(?![A-Za-z0-9_])"),
    re.compile(rb"/EmbeddedFile(?![A-Za-z0-9_])"),
    re.compile(rb"/EmbeddedFiles(?![A-Za-z0-9_])"),
    re.compile(rb"/SubmitForm(?![A-Za-z0-9_])"),
    re.compile(rb"/RichMedia(?![A-Za-z0-9_])"),
    re.compile(rb"/XFA(?![A-Za-z0-9_])"),
    re.compile(rb"/GoToR(?![A-Za-z0-9_])"),
    re.compile(rb"/GoToE(?![A-Za-z0-9_])"),
    re.compile(rb"/Encrypt(?![A-Za-z0-9_])"),
]


def _scan_dangerous_keywords(data: bytes) -> str | None:
    for pat in _DANGEROUS_PDF_KEYWORDS:
        m = pat.search(data)
        if m:
            return m.group(0).decode("ascii", errors="replace")
    return None


def _extract_sync(data: bytes) -> str:
    # SEC-021 (revised): RLIMIT_AS would apply to the whole process, not just
    # the parsing thread, and crashes the worker. Rely on max_cv_bytes (5 MB
    # input) + pdfplumber's own structural checks.
    try:
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
            return "\n".join(pages).strip()
    except MemoryError as e:
        raise PdfParseError("pdf too large to parse") from e
    except Exception as e:
        raise PdfParseError(f"pdfplumber failed: {e}") from e


async def extract_pdf_text(data: bytes, timeout: float = 10.0) -> str:
    if not data.startswith(b"%PDF-"):
        raise PdfParseError("invalid PDF magic bytes")
    hit = _scan_dangerous_keywords(data)
    if hit is not None:
        logger.warning("pdf rejected by keyword scan: {}", hit)
        raise PdfParseError(f"dangerous pdf feature: {hit}")
    try:
        text = await asyncio.wait_for(asyncio.to_thread(_extract_sync, data), timeout=timeout)
    except TimeoutError as e:
        raise PdfParseError("pdf extraction timeout") from e
    if not text or len(text) < 50:
        logger.warning("pdf extracted text too short len={}", len(text) if text else 0)
        raise PdfParseError("pdf has insufficient text content")
    # SEC-065 — defang invisible / control / lookalike characters before the
    # text reaches the injection guard or the LLM.
    return sanitize_extracted_text(text)
