"""SEC-005 / SEC-052 / SEC-064 — first-line regex filter for prompt-injection
attempts inside CV or job description text.

False positives are acceptable here: the only legitimate user input is a CV
and a job description. Neither should contain phrases like
"ignore previous instructions" or pseudo-system tags ([INTERNAL_NOTE],
<system>, etc.). If a real CV/vaga happens to trip a pattern, the user can
rephrase. Better to reject one borderline case than to leak the system
prompt.

SEC-064: text is NFKC-normalized and stripped of zero-width / RTL-override
characters before the regex runs. Without this step an attacker can write
"ɪɢɴᴏʀᴇ ᴀʟʟ ɪɴꜱᴛʀᴜᴄᴛɪᴏɴꜱ" (Unicode small-caps) or
"ignore​all​previous" (zero-width joiners) and bypass the
case-insensitive ASCII patterns.
"""
import re

from app.services.security import sanitize_extracted_text


def _normalize_for_scan(text: str) -> str:
    """SEC-064 / SEC-069 — delegate to the shared boundary sanitizer so the
    regex sees the same canonical form that the LLM eventually sees:
    NFKC normalization, zero-width / RTL-override / BOM stripped, C0 controls
    stripped, IPA / Cyrillic / Greek confusables folded to ASCII look-alikes.
    """
    return sanitize_extracted_text(text) if text else text

INJECTION_PATTERNS = [
    # Direct overrides of prior instructions
    re.compile(r"(?i)ignore\s+(?:(?:all|previous|above|earlier|prior|the|any|your)\s+)+(instructions|prompts|rules)"),
    re.compile(r"(?i)disregard\s+(your|all|previous|the\s+above|prior)"),
    re.compile(r"(?i)forget\s+(everything|all|previous|prior|your\s+instructions)"),
    re.compile(r"(?i)override\s+(your|the|all)\s+(instructions|prompts|rules|guidelines)"),
    # Role hijack
    re.compile(r"(?i)you\s+are\s+now\s+(a|an)\s+"),
    # SEC-052 follow-up: narrowed to hijack targets / "act as if you". Bare
    # "act as a <noun>" is normal job copy ("act as a liaison/mentor").
    re.compile(r"(?i)act\s+as\s+(?:(?:an?\s+)?(?:dan|jailbroken|jailbreak|unrestricted|unfiltered|uncensored|unlimited|evil|malicious|rogue|hacker|root|sudo|admin|god\s*mode|different\s+(?:ai|assistant|model|persona)|new\s+(?:ai|assistant|persona)|system\s+administrator)\b|if\s+you\b)"),
    re.compile(r"(?i)pretend\s+(you\s+are|to\s+be)\s+"),
    re.compile(r"(?i)from\s+now\s+on\s+(you|respond|act|behave)"),
    # System-prompt exfiltration (verb-agnostic)
    re.compile(
        r"(?i)(reveal|show|print|output|display|reproduce|return|leak|dump|expose)"
        r"\s+(me\s+)?(your|the|this|that|exact)?\s*"
        r"(system|initial|original|raw)?\s*(prompt|instructions|configuration|rules|guidelines|directives)"
    ),
    re.compile(r"(?i)what\s+(are|is|were)\s+your\s+(instructions|prompt|rules|guidelines)"),
    re.compile(r"(?i)repeat\s+(your|the)\s+(system|initial|original)\s+(prompt|message|instructions)"),
    # Pseudo-system / audit / admin tags trying to look authoritative
    re.compile(r"(?i)\[\s*(internal[_\s\-]?note|system|admin|audit|developer|dev|operator|moderator|policy|override|root)"),
    # Tag breakout — closing the prompt wrappers (<cv>, <job>) or fake role tags.
    # SEC-064: allow optional whitespace between `<`, `/`, and the tag name so
    # variants like `< /cv>`, `</ cv>`, `< cv >` are still caught.
    re.compile(r"(?i)<\s*/?\s*(system|user|assistant|sysadmin|operator|policy|cv|job|target_market|instructions?|prompt)\b"),
    re.compile(r"(?i)\[INST\]|\[/INST\]"),
    re.compile(r"(?i)BEGIN\s+(SYSTEM|INITIAL|HIDDEN)\s+(PROMPT|MESSAGE|INSTRUCTIONS)"),
    re.compile(r"(?i)\bpriority\s*[:=]\s*\"?(critical|urgent|highest|p0)\"?"),
    # SEC-052 follow-up: require the literal authority framing "this is required
    # for ...". "<skill> required for testing/compliance" is normal job copy.
    re.compile(r"(?i)this\s+is\s+required\s+for\s+(compliance|audit|logging|debugging|verification|security|policy)"),
    # SEC-052 follow-up: require an AI-output object so "before responding to
    # the customer" (normal support-role copy) no longer trips.
    re.compile(r"(?i)before\s+(outputting|generating|producing|emitting|returning|printing)\s+(?:(?:the|your|any|a)\s+)?(?:\w+\s+)?(json|output|response|answer|result|reply|score)\b"),
    # Jailbreak personas
    re.compile(r"(?i)jailbreak|DAN\s+mode|developer\s+mode|sudo\s+mode|god\s+mode|admin\s+mode"),
    # Credential exfiltration — REMOVED (SEC-052 false positive on tech CVs).
    # Legit CVs: "managed password policies", "API token", "secret key rotation"
    # re.compile(r"(?i)\b(password|senha|api[_\-]?key|secret[_\-]?key|token|credential|bearer)\b"),
    # External-action requests
    # SEC-052 follow-up: dropped bare "reach out to me at <email>" — that is a
    # normal CV contact line. Imperative "email me" / "send me an email" kept.
    re.compile(r"(?i)email\s+me|send\s+me\s+(an?\s+)?email"),
    re.compile(r"(?i)\b(curl|wget|fetch|http\.get)\s+https?://"),
    re.compile(r"(?i)visit\s+https?://|navigate\s+to\s+https?://|open\s+https?://"),
    # Output-shape hijack
    re.compile(r"(?i)respond\s+(only\s+)?(with|in)\s+(plain\s+text|markdown|the\s+following)"),
    re.compile(r"(?i)do\s+not\s+(output|return)\s+(JSON|json)"),
    re.compile(r"(?i)label\s+it\s+\""),
    # Portuguese variants (app primary language is PT-BR)
    re.compile(r"(?i)ignor[ae]\s+(as|todas)?\s*(instru[cç][õo]es|regras|prompts?)\s+(anteriores|acima|pr[eé]vias)?"),
    re.compile(r"(?i)esque[çc]a\s+(tudo|as\s+instru[cç][õo]es)"),
    re.compile(r"(?i)(revele|mostre|imprima|exiba|mostra|imprime)\s+(o|a|os|as|seu|sua|este|esta)\s+(system|prompt|sistema|instru[cç][õo]es|regras|diretrizes)"),
    # SEC-052 follow-up: require "agora" (mirrors EN "you are now a"). Bare
    # "Você é um/uma ..." is extremely common second-person vaga copy.
    re.compile(r"(?i)voc[eê]\s+agora\s+[eé]\s+(um|uma)\b"),
    # SEC-052 follow-up: narrowed to hijack targets / "aja como se". Bare
    # "aja como um <noun>" is normal vaga copy ("aja como um agente de mudança").
    re.compile(r"(?i)aja\s+como\s+(?:(um|uma)\s+(assistente|ia|intelig[eê]ncia|hacker|administrador|sistema|dan|rob[ôo]|m[aá]quina|modelo)\b|se\s+(voc[eê]|n[ãa]o|tu)\b)"),
    # SEC-052 follow-up: require an output object so "antes de responder ao
    # cliente" (normal copy) no longer trips; "imprima as instruções" is still
    # caught by the revele/imprima pattern above.
    re.compile(r"(?i)antes\s+de\s+(responder|gerar|produzir|emitir|fornecer)\s+(?:(o|a|com)\s+)?(?:\w+\s+)?(json|resposta|sa[ií]da|resultado|score|nota|an[aá]lise)\b"),
]


def find_suspicious_patterns(text: str) -> list[str]:
    normalized = _normalize_for_scan(text)
    return [p.pattern for p in INJECTION_PATTERNS if p.search(normalized)]


def has_suspicious_patterns(text: str) -> bool:
    normalized = _normalize_for_scan(text)
    return any(p.search(normalized) for p in INJECTION_PATTERNS)
