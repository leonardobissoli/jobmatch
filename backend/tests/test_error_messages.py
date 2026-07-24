"""SEC-058 — Unit tests for the two-tier error-message policy.

Specific messages for benign causes (wrong file format, encrypted PDF,
scanned PDF, etc.) — generic / opaque messages for security-sensitive
rejections (regex injection hits). Tests below exercise the mapping
without touching the ASGI stack.
"""
from app.routes.match import (
    _CONTENT_VALIDATION_FALLBACK,
    _CONTENT_VALIDATION_MESSAGES,
    _pdf_user_message,
    _txt_user_message,
)
from app.services.pdf_parser import PdfParseError
from app.services.txt_parser import TxtParseError

_GENERIC_GLOBAL = "Não conseguimos processar esse arquivo."

# Substrings that must NEVER appear in user-facing copy — they would leak
# detection internals to attackers.
_FORBIDDEN_LEAKS = (
    "/JavaScript",
    "/JS",
    "/Launch",
    "/OpenAction",
    "/AA",
    "/XFA",
    "/EmbeddedFile",
    "/SubmitForm",
    "/RichMedia",
    "/GoToR",
    "/GoToE",
    "regex",
    "injection",
    "judge",
    "LLM",
    "binary signature",
    "%PDF",
    "MZ",
    "PK\\x03",
    "ELF",
)


def _assert_no_leak(msg: str) -> None:
    for token in _FORBIDDEN_LEAKS:
        assert token not in msg, f"leak: {token!r} in message {msg!r}"


# ---------------------------------------------------------------------------
# PDF — specific (benign) messages
# ---------------------------------------------------------------------------


def test_pdf_encrypted_specific_message() -> None:
    msg = _pdf_user_message(PdfParseError("dangerous pdf feature: /Encrypt"))
    assert "protegido por senha" in msg
    _assert_no_leak(msg)


def test_pdf_invalid_magic_specific() -> None:
    msg = _pdf_user_message(PdfParseError("invalid PDF magic bytes"))
    assert "não é um PDF válido" in msg
    _assert_no_leak(msg)


def test_pdf_scanned_specific_message() -> None:
    msg = _pdf_user_message(PdfParseError("pdf has insufficient text content"))
    assert "escaneado" in msg or "imagem" in msg
    _assert_no_leak(msg)


def test_pdf_timeout_specific_message() -> None:
    msg = _pdf_user_message(PdfParseError("pdf extraction timeout"))
    assert "demorou demais" in msg
    _assert_no_leak(msg)


def test_pdf_too_large_specific_message() -> None:
    msg = _pdf_user_message(PdfParseError("pdf too large to parse"))
    assert "muito grande" in msg
    _assert_no_leak(msg)


def test_pdf_corrupted_specific_message() -> None:
    msg = _pdf_user_message(PdfParseError("pdfplumber failed: malformed"))
    assert "corrompido" in msg
    _assert_no_leak(msg)


# ---------------------------------------------------------------------------
# PDF — generic (security-sensitive) messages
# ---------------------------------------------------------------------------


def test_pdf_javascript_stays_generic() -> None:
    msg = _pdf_user_message(PdfParseError("dangerous pdf feature: /JavaScript"))
    assert "padrão" in msg or "recursos especiais" in msg
    _assert_no_leak(msg)


def test_pdf_launch_stays_generic() -> None:
    msg = _pdf_user_message(PdfParseError("dangerous pdf feature: /Launch"))
    _assert_no_leak(msg)
    # Generic /Launch and generic /JavaScript share the same copy.
    assert msg == _pdf_user_message(PdfParseError("dangerous pdf feature: /JavaScript"))


def test_pdf_openaction_stays_generic() -> None:
    msg = _pdf_user_message(PdfParseError("dangerous pdf feature: /OpenAction"))
    _assert_no_leak(msg)


def test_pdf_xfa_stays_generic() -> None:
    msg = _pdf_user_message(PdfParseError("dangerous pdf feature: /XFA"))
    _assert_no_leak(msg)


def test_pdf_unknown_falls_back_generic() -> None:
    msg = _pdf_user_message(PdfParseError("something brand new"))
    assert msg.startswith("Não conseguimos ler o CV")
    _assert_no_leak(msg)


# ---------------------------------------------------------------------------
# TXT — specific (benign) messages
# ---------------------------------------------------------------------------


def test_txt_empty_specific_message() -> None:
    msg = _txt_user_message(TxtParseError("empty job description"))
    assert "vazia" in msg
    _assert_no_leak(msg)


def test_txt_binary_specific_message() -> None:
    msg = _txt_user_message(
        TxtParseError("binary content rejected (binary signature: b'%PDF-')")
    )
    assert "arquivo de texto" in msg or "(.txt)" in msg
    _assert_no_leak(msg)


def test_txt_null_byte_specific_message() -> None:
    msg = _txt_user_message(TxtParseError("binary content rejected (null byte in head)"))
    assert "arquivo de texto" in msg
    _assert_no_leak(msg)


def test_txt_decode_failed_specific_message() -> None:
    msg = _txt_user_message(TxtParseError("decode failed: codec error"))
    assert "UTF-8" in msg
    _assert_no_leak(msg)


def test_txt_too_short_specific_message() -> None:
    msg = _txt_user_message(TxtParseError("job description too short"))
    assert "muito curta" in msg
    _assert_no_leak(msg)


def test_txt_unknown_falls_back_generic() -> None:
    msg = _txt_user_message(TxtParseError("something brand new"))
    assert msg == "Descrição da vaga inválida."
    _assert_no_leak(msg)


# ---------------------------------------------------------------------------
# ContentValidationError mapping
# ---------------------------------------------------------------------------


def test_content_validation_insufficient_data_specific() -> None:
    msg = _CONTENT_VALIDATION_MESSAGES["insufficient_data"]
    assert "dados suficientes" in msg
    _assert_no_leak(msg)


def test_content_validation_cv_judge_specific() -> None:
    msg = _CONTENT_VALIDATION_MESSAGES["cv_validation_failed"]
    assert "currículo" in msg
    _assert_no_leak(msg)
    # Must not say "the judge said so" or hint at the LLM step
    assert "judge" not in msg.lower()


def test_content_validation_job_judge_specific() -> None:
    msg = _CONTENT_VALIDATION_MESSAGES["job_validation_failed"]
    assert "vaga" in msg
    _assert_no_leak(msg)


def test_content_validation_suspicious_cv_stays_generic() -> None:
    assert _CONTENT_VALIDATION_MESSAGES["suspicious_content_cv"] == _GENERIC_GLOBAL


def test_content_validation_suspicious_job_stays_generic() -> None:
    assert _CONTENT_VALIDATION_MESSAGES["suspicious_content_job"] == _GENERIC_GLOBAL


def test_content_validation_unknown_falls_back_generic() -> None:
    msg = _CONTENT_VALIDATION_MESSAGES.get("brand_new_code", _CONTENT_VALIDATION_FALLBACK)
    assert msg == _GENERIC_GLOBAL


# ---------------------------------------------------------------------------
# Global negative — every message in the map and from helpers must be leak-free
# ---------------------------------------------------------------------------


def test_no_internal_token_leaks_anywhere() -> None:
    for code, m in _CONTENT_VALIDATION_MESSAGES.items():
        _assert_no_leak(m)
        assert m, f"empty message for code {code}"
    _assert_no_leak(_CONTENT_VALIDATION_FALLBACK)
