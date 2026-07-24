"""SEC-055 / SEC-056 / SEC-057 — file-type and content validation.

Unit-level coverage of:
- TXT binary-signature blacklist (SEC-056)
- PDF dangerous-keyword scan (SEC-057)

Route-level enforcement (SEC-055 Content-Type) is exercised via manual
smoke against a running stack. The unit tests below exercise the underlying
logic deterministically without needing the full ASGI stack.
"""
import pytest

from app.services.pdf_parser import (
    PdfParseError,
    _scan_dangerous_keywords,
    extract_pdf_text,
)
from app.services.txt_parser import TxtParseError, parse_txt

# ---------------------------------------------------------------------------
# SEC-056 — TXT binary signatures (unit)
# ---------------------------------------------------------------------------


def _legit_job_text() -> bytes:
    return (
        b"Senior Data Analyst at FinTech Dublin. Requirements: 4+ years SQL, "
        b"Python, Power BI. Nice to have: dbt, Airflow, AWS Glue. Salary "
        b"65k-80k EUR. Hybrid Dublin."
    )


def test_clean_txt_passes() -> None:
    text = parse_txt(_legit_job_text())
    assert "Senior Data Analyst" in text


def test_pdf_as_txt_rejected() -> None:
    with pytest.raises(TxtParseError, match="binary"):
        parse_txt(b"%PDF-1.4\n%fake pdf as text job")


def test_zip_as_txt_rejected() -> None:
    with pytest.raises(TxtParseError, match="binary"):
        parse_txt(b"PK\x03\x04" + b"x" * 200)


def test_exe_as_txt_rejected() -> None:
    with pytest.raises(TxtParseError, match="binary"):
        parse_txt(b"MZ" + b"\x90" * 200)


def test_elf_as_txt_rejected() -> None:
    with pytest.raises(TxtParseError, match="binary"):
        parse_txt(b"\x7fELF" + b"\x02" * 200)


def test_gzip_as_txt_rejected() -> None:
    with pytest.raises(TxtParseError, match="binary"):
        parse_txt(b"\x1f\x8b" + b"x" * 200)


def test_rtf_as_txt_rejected() -> None:
    with pytest.raises(TxtParseError, match="binary"):
        parse_txt(b"{\\rtf1\\ansi this is rtf content with enough body bytes")


def test_ole_as_txt_rejected() -> None:
    with pytest.raises(TxtParseError, match="binary"):
        parse_txt(b"\xd0\xcf\x11\xe0" + b"x" * 200)


def test_utf16_bom_as_txt_rejected() -> None:
    """UTF-16 has alternating null bytes → caught by null-byte rule."""
    payload = b"\xff\xfeS\x00e\x00n\x00i\x00o\x00r\x00 \x00D\x00a\x00t\x00a\x00"
    with pytest.raises(TxtParseError, match="binary|null"):
        parse_txt(payload)


def test_high_nonprintable_ratio_rejected() -> None:
    """Random control bytes (no recognizable signature) still get rejected."""
    payload = bytes([0x01, 0x02, 0x03, 0x04] * 100) + b"some text after"
    with pytest.raises(TxtParseError, match="binary|non-printable"):
        parse_txt(payload)


def test_ptbr_accents_pass() -> None:
    """UTF-8 accented chars are >= 0x80; must not trigger non-printable rule."""
    text = (
        "Analista de Dados Sênior em Lisboa. Requisitos: experiência em "
        "Python, gestão de pipelines, comunicação em inglês. Conhecimento "
        "em análise estatística e aprendizado de máquina é diferencial."
    ).encode()
    out = parse_txt(text)
    assert "Sênior" in out
    assert "experiência" in out


def test_short_txt_rejected() -> None:
    with pytest.raises(TxtParseError, match="too short"):
        parse_txt(b"hi")


# SEC-066 — strict decoding


def test_strict_decode_falls_back_to_latin1() -> None:
    # Latin-1 encoded text with bytes invalid under UTF-8 should still parse
    # via the latin-1 fallback path rather than corrupting with U+FFFD.
    text = (
        "Analista de Dados Sênior em Portugal com experiência em Python. "
        "Conhecimento profundo de pipelines, observabilidade, e tradução "
        "de requisitos de negócio para soluções técnicas concretas."
    )
    data = text.encode("latin-1")
    out = parse_txt(data)
    assert "Sênior" in out and "experiência" in out
    assert "�" not in out  # no replacement chars leaked


def test_strict_decode_rejects_garbled_bytes() -> None:
    # A short payload with bytes that decode cleanly under no candidate
    # encoding should hit the decode_failed branch instead of silently
    # smuggling replacement chars through to the LLM.
    # Mix high bytes that violate UTF-8 multibyte rules and aren't a
    # plausible Latin-1 paragraph either, prefixed by enough printable text
    # to clear the 30% non-printable head check.
    payload = b"This looks like a job description, mostly. " + b"\xc3\x28" * 100
    # chardet should fail or pick a weird encoding; if both UTF-8 and
    # Latin-1 succeed (Latin-1 always succeeds on any byte sequence) the
    # output will still be the Latin-1 reading. Strict-mode goal here is
    # to surface a decode failure if NO candidate works.
    try:
        out = parse_txt(payload)
        # Latin-1 always decodes; assert no U+FFFD appears (strict mode).
        assert "�" not in out
    except TxtParseError as e:
        # Acceptable: explicit decode_failed surface.
        assert "decode" in str(e).lower() or "binary" in str(e).lower()


# ---------------------------------------------------------------------------
# SEC-057 — PDF dangerous keywords (unit)
# ---------------------------------------------------------------------------


def test_clean_pdf_passes_keyword_scan() -> None:
    data = b"%PDF-1.4\n%random comment\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"
    assert _scan_dangerous_keywords(data) is None


def test_javascript_caught() -> None:
    assert _scan_dangerous_keywords(b"%PDF-1.4\n/JavaScript (alert(1)) endobj") == "/JavaScript"


def test_js_short_caught() -> None:
    assert _scan_dangerous_keywords(b"%PDF-1.4\n<< /JS (xx) >>") == "/JS"


def test_javascript_with_suffix_not_overmatched() -> None:
    """`/JavaScriptFoo` is a different name token and must NOT match `/JavaScript`."""
    assert _scan_dangerous_keywords(b"%PDF-1.4\n/JavaScriptFoo dummy") is None


def test_aa_with_suffix_not_overmatched() -> None:
    """`/AAPL` (hypothetical user-defined name) must NOT match `/AA`."""
    assert _scan_dangerous_keywords(b"%PDF-1.4\n/AAPL dummy data") is None


def test_aa_in_dict_form_caught() -> None:
    """`/AA<<...>>` is the common form for Additional Actions."""
    assert _scan_dangerous_keywords(b"%PDF-1.4\n/AA<</O 1 0 R>>") == "/AA"


def test_open_action_caught() -> None:
    # Scan order returns the first hit found; pattern below has no /JS / /JavaScript
    # so we get the OpenAction match (which is the keyword we care about here).
    assert _scan_dangerous_keywords(b"%PDF-1.4\n/OpenAction 5 0 R") == "/OpenAction"


def test_launch_caught() -> None:
    assert _scan_dangerous_keywords(b"%PDF-1.4\n/Launch /F (cmd.exe)") == "/Launch"


def test_embedded_file_caught() -> None:
    assert _scan_dangerous_keywords(b"%PDF-1.4\n/EmbeddedFile stuff") == "/EmbeddedFile"


def test_xfa_caught() -> None:
    assert _scan_dangerous_keywords(b"%PDF-1.4\n/XFA [(...)]") == "/XFA"


def test_encrypt_caught() -> None:
    assert _scan_dangerous_keywords(b"%PDF-1.4\n/Encrypt 5 0 R") == "/Encrypt"


def test_gotor_caught() -> None:
    assert _scan_dangerous_keywords(b"%PDF-1.4\n/GoToR (/etc/passwd)") == "/GoToR"


def test_uri_not_rejected() -> None:
    """`/URI` is allowed — legit CVs link to LinkedIn / GitHub."""
    assert _scan_dangerous_keywords(b"%PDF-1.4\n/URI (https://linkedin.com/in/me)") is None


@pytest.mark.asyncio
async def test_extract_pdf_text_rejects_dangerous() -> None:
    with pytest.raises(PdfParseError, match="dangerous"):
        await extract_pdf_text(b"%PDF-1.4\n/JavaScript (alert(1))")


@pytest.mark.asyncio
async def test_extract_pdf_text_rejects_missing_magic() -> None:
    with pytest.raises(PdfParseError, match="magic"):
        await extract_pdf_text(b"NOT_A_PDF" + b"x" * 200)


