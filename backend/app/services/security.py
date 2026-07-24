"""Text normalization helpers for untrusted CV and job-description content."""

import re
import unicodedata

_INVISIBLE_RE = re.compile("[​‌‍‎‏‪‫‬‭‮⁠﻿]")
_CONTROL_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")

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


def sanitize_extracted_text(text: str) -> str:
    if not text:
        return text
    normalized = unicodedata.normalize("NFKC", text)
    normalized = _INVISIBLE_RE.sub("", normalized)
    normalized = _CONTROL_RE.sub("", normalized)
    return _CONFUSABLES_RE.sub(lambda match: _CONFUSABLES_MAP[match.group(0)], normalized)
