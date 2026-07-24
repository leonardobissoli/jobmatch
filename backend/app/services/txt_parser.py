"""SEC-036 (size cap) + SEC-056 (binary signature blacklist).

The job description field is supposed to be plain text. There is no
canonical magic-byte signature for "text", so we work the other way around:
reject anything that LOOKS like a known binary format up front. Combined
with the route-level Content-Type check (SEC-055), this makes it
impractical to smuggle a PDF/ZIP/PE/ELF/etc as a "job description" and
have its raw bytes flow to the LLM.
"""
import chardet

from app.services.security import sanitize_extracted_text


class TxtParseError(Exception):
    pass


# SEC-056 — known binary signatures rejected up-front. A real .txt file
# cannot start with any of these.
_BINARY_SIGNATURES: tuple[bytes, ...] = (
    b"%PDF-",                  # PDF
    b"MZ",                     # PE/COFF (.exe, .dll)
    b"PK\x03\x04",             # ZIP / JAR / DOCX / XLSX / ODT / APK
    b"\x7fELF",                # ELF (Linux/BSD executables)
    b"Rar!\x1a\x07",           # RAR
    b"7z\xbc\xaf\x27\x1c",     # 7-Zip
    b"GIF8",                   # GIF87a / GIF89a
    b"\x89PNG\r\n\x1a\n",      # PNG
    b"\xff\xd8\xff",           # JPEG
    b"BM",                     # BMP
    b"RIFF",                   # WAV / WebP / AVI containers
    b"\x1f\x8b",               # gzip
    b"\xd0\xcf\x11\xe0",       # MS OLE compound (legacy .doc/.xls/.ppt)
    b"{\\rtf",                 # RTF — can embed OLE objects
    b"\xca\xfe\xba\xbe",       # Java class / Mach-O fat binary
    b"\xfe\xed\xfa",           # Mach-O (covers both 32 and 64 bit prefixes)
)

# Non-printable C0 controls (excludes TAB, LF, CR which are valid in text).
_NON_PRINTABLE = (
    set(range(0x00, 0x09))
    | {0x0B, 0x0C}
    | set(range(0x0E, 0x20))
    | {0x7F}
)

_HEAD_SAMPLE = 1024
_NON_PRINTABLE_THRESHOLD = 0.30  # >30% non-printable in head sample → binary


def _looks_binary(data: bytes) -> str | None:
    """Return a short reason if data looks binary, else None."""
    for sig in _BINARY_SIGNATURES:
        if data.startswith(sig):
            return f"binary signature: {sig[:8]!r}"
    head = data[:_HEAD_SAMPLE]
    if b"\x00" in head:
        # UTF-16 files trigger this (alternating nulls) and are intentionally
        # rejected — frontend `accept=".txt,text/plain"` produces UTF-8/Latin-1
        # in practice; UTF-16 is a strong signal of unusual content.
        return "null byte in head"
    if head:
        bad = sum(1 for b in head if b in _NON_PRINTABLE)
        if bad / len(head) > _NON_PRINTABLE_THRESHOLD:
            return f"non-printable ratio {bad}/{len(head)}"
    return None


def parse_txt(data: bytes) -> str:
    if not data:
        raise TxtParseError("empty job description")
    reason = _looks_binary(data)
    if reason is not None:
        raise TxtParseError(f"binary content rejected ({reason})")
    # SEC-066 — strict decode. The previous `errors="replace"` silently
    # substituted U+FFFD for invalid bytes, which let an attacker smuggle
    # an unintended byte sequence past the binary-signature blacklist by
    # mis-tagging encoding. Strict mode rejects anything that isn't cleanly
    # decodable, falling back UTF-8 → Latin-1 (the historical "everything is
    # printable" superset) before giving up.
    detected = chardet.detect(data)
    primary = detected.get("encoding") or "utf-8"
    candidates = [primary, "utf-8", "latin-1"]
    last_err: Exception | None = None
    text: str | None = None
    for enc in candidates:
        try:
            text = data.decode(enc, errors="strict").strip()
            break
        except (UnicodeDecodeError, LookupError) as e:
            last_err = e
            continue
    if text is None:
        raise TxtParseError(f"decode failed: {last_err}") from last_err
    if len(text) < 50:
        raise TxtParseError("job description too short")
    # SEC-065 — defang invisible / control / lookalike characters before the
    # text reaches the injection guard or the LLM.
    return sanitize_extracted_text(text)
