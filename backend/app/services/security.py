"""Text normalization helpers for untrusted CV and job-description content."""

import html
import re
import unicodedata
from html.entities import html5

_INVISIBLE_RE = re.compile("[​‌‍‎‏‪‫‬‭‮⁠﻿]")
_CONTROL_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")

# Job descriptions are routinely copy-pasted out of a rendered web page, which
# drags HTML entities along with them ("Web Platform &amp; Technology"). Nothing
# downstream decodes those, so the raw entity reached the LLM and was echoed back
# into the report verbatim.
#
# Deliberately narrower than a bare html.unescape() call:
#
#   * only well-formed entities (trailing ";" required) are decoded, so a literal
#     "&" survives untouched — "AT&T" and "R&D" stay as written.
#   * the name is checked against the real entity table before decoding. A bare
#     html.unescape() resolves the longest known prefix and leaves the rest, so
#     "&notit;" would become "¬it;"; requiring an exact match keeps it literal.
#   * a single pass, never a loop. Repeated unescaping is its own injection
#     vector: "&amp;#105;" would decode to "&#105;" and then to "i".
#
# This runs FIRST, before the defenses below and before the injection guard sees
# the text — otherwise an entity-encoded payload ("&#105;gnore previous
# instructions", "&#8203;" as a zero-width space) would slip past both.
_ENTITY_RE = re.compile(r"&(?:#[0-9]{1,7}|#[xX][0-9a-fA-F]{1,6}|[A-Za-z][A-Za-z0-9]{1,31});")

_CONFUSABLES_MAP: dict[str, str] = {
    "ᴀ": "A", "ʙ": "B", "ᴄ": "C", "ᴅ": "D", "ᴇ": "E", "ꜰ": "F",
    "ɢ": "G", "ʜ": "H", "ɪ": "I", "ᴊ": "J", "ᴋ": "K", "ʟ": "L",
    "ᴍ": "M", "ɴ": "N", "ᴏ": "O", "ᴘ": "P", "ʀ": "R", "ꜱ": "S",
    "ᴛ": "T", "ᴜ": "U", "ᴠ": "V", "ᴡ": "W", "ʏ": "Y", "ᴢ": "Z",
    "А": "A", "В": "B", "С": "C", "Е": "E", "Н": "H", "К": "K",
    "М": "M", "О": "O", "Р": "P", "Т": "T", "Х": "X", "Ѕ": "S",
    "І": "I", "Ј": "J", "а": "a", "в": "B", "с": "c", "е": "e",
    "о": "o", "р": "p", "у": "y", "х": "x", "ѕ": "s", "і": "i",
    "ј": "j", "Α": "A", "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H",
    "Ι": "I", "Κ": "K", "Μ": "M", "Ν": "N", "Ο": "O", "Ρ": "P",
    "Τ": "T", "Υ": "Y", "Χ": "X", "ο": "o", "ρ": "p",
}
_CONFUSABLES_RE = re.compile("|".join(re.escape(key) for key in _CONFUSABLES_MAP))


def _decode_entity(match: re.Match[str]) -> str:
    token = match.group(0)
    name = token[1:-1]
    if name.startswith("#") or f"{name};" in html5:
        return html.unescape(token)
    return token


def decode_html_entities(text: str) -> str:
    """Resolve well-formed HTML entities to the characters they stand for."""
    if not text:
        return text
    return _ENTITY_RE.sub(_decode_entity, text)


def sanitize_extracted_text(text: str) -> str:
    if not text:
        return text
    normalized = unicodedata.normalize("NFKC", decode_html_entities(text))
    normalized = _INVISIBLE_RE.sub("", normalized)
    normalized = _CONTROL_RE.sub("", normalized)
    return _CONFUSABLES_RE.sub(lambda match: _CONFUSABLES_MAP[match.group(0)], normalized)
