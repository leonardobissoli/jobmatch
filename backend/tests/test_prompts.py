"""ADR-013 — Prompt regression guard.

PT-BR rendering of the match prompt must be byte-identical (modulo the
runtime substitutions) to the original pre-i18n behavior. This protects
existing scoring quality while we add the en-US locale.
"""
from app.i18n import DEFAULT_LOCALE
from app.services.minimax_client import (
    _PROMPT_PARAMS,
    MATCH_PROMPT_TPL,
    _localize_market,
)


def test_pt_br_params_present() -> None:
    assert DEFAULT_LOCALE in _PROMPT_PARAMS
    p = _PROMPT_PARAMS[DEFAULT_LOCALE]
    assert p["locale_name"].startswith("Brazilian Portuguese")
    assert "á" in p["diacritics_rule"]
    assert "Resumo profissional" in p["canonical_sections_json"]
    assert "Match Forte" in p["tier_labels_json"]
    assert p["unknown_job_title"] == "Vaga não identificada"


def test_en_params_present() -> None:
    assert "en" in _PROMPT_PARAMS
    p = _PROMPT_PARAMS["en"]
    assert p["locale_name"].startswith("American English")
    assert p["diacritics_rule"] == ""
    assert "Professional Summary" in p["canonical_sections_json"]
    assert "Strong Match" in p["tier_labels_json"]
    assert p["unknown_job_title"] == "Job title not identified"


def test_match_prompt_template_has_all_locale_placeholders() -> None:
    required = [
        "{{LOCALE_NAME}}",
        "{{LOCALE_CODE}}",
        "{{DIACRITICS_RULE}}",
        "{{CANONICAL_SECTIONS_JSON}}",
        "{{TIER_LABELS_JSON}}",
        "{{UNKNOWN_JOB_TITLE}}",
    ]
    for placeholder in required:
        assert placeholder in MATCH_PROMPT_TPL, f"missing in match_prompt.md: {placeholder}"


def test_system_prompt_has_locale_placeholders() -> None:
    """Regression: the system prompt body must NOT hard-anchor PT-BR.

    The original rule 2 said "Output language is always Brazilian Portuguese
    (PT-BR)" which won over any appended override. Now rule 2 uses
    placeholders that minimax_client substitutes per locale.
    """
    from app.services.minimax_client import SYSTEM_PROMPT

    required = ["{{LOCALE_NAME}}", "{{LOCALE_CODE}}", "{{DIACRITICS_RULE}}"]
    for placeholder in required:
        assert placeholder in SYSTEM_PROMPT, f"missing in system_prompt.md: {placeholder}"
    # The old hardcoded PT-BR rule must be gone.
    assert "Output language is always Brazilian Portuguese" not in SYSTEM_PROMPT, (
        "system_prompt.md still has hardcoded PT-BR rule — engine can't override it"
    )


def test_system_prompt_substitutes_for_en() -> None:
    """End-to-end: placeholders resolve cleanly for en-US."""
    from app.services.minimax_client import SYSTEM_PROMPT

    params = _PROMPT_PARAMS["en"]
    rendered = (
        SYSTEM_PROMPT
        .replace("{{LOCALE_NAME}}", params["locale_name"])
        .replace("{{LOCALE_CODE}}", params["locale_code"])
        .replace("{{DIACRITICS_RULE}}", params["diacritics_rule"])
    )
    assert "{{" not in rendered
    assert "American English" in rendered
    # The old rule 2 hardcoded "Brazilian Portuguese" must be gone.
    assert "Output language is always Brazilian Portuguese" not in rendered


def test_system_prompt_pt_br_regression() -> None:
    """PT-BR rendered system prompt must still instruct Brazilian Portuguese output."""
    from app.services.minimax_client import SYSTEM_PROMPT

    params = _PROMPT_PARAMS[DEFAULT_LOCALE]
    rendered = (
        SYSTEM_PROMPT
        .replace("{{LOCALE_NAME}}", params["locale_name"])
        .replace("{{LOCALE_CODE}}", params["locale_code"])
        .replace("{{DIACRITICS_RULE}}", params["diacritics_rule"])
    )
    assert "Brazilian Portuguese" in rendered
    assert "pt-BR" in rendered
    # Diacritics rule present for PT-BR
    assert "á" in rendered and "ç" in rendered


def test_localize_market_keys() -> None:
    assert _localize_market("", "pt-BR") == ""
    assert _localize_market("NONE", "pt-BR") == ""
    assert _localize_market("BR", "pt-BR") == "Brasil"
    assert _localize_market("US", "pt-BR") == "EUA / Canadá"
    assert _localize_market("BR", "en") == "Brazil"
    assert _localize_market("US", "en") == "United States / Canada"


def test_match_substitution_round_trip_pt_br() -> None:
    """End-to-end: every placeholder resolves cleanly for PT-BR.

    If a new placeholder is added to match_prompt.md but not handled by
    the engine, this will leave `{{...}}` in the output and fail.
    """
    params = _PROMPT_PARAMS[DEFAULT_LOCALE]
    rendered = (
        MATCH_PROMPT_TPL
        .replace("{{CV_CONTENT}}", "X")
        .replace("{{JOB_CONTENT}}", "Y")
        .replace("{{TARGET_MARKET}}", "Brasil")
        .replace("{{LOCALE_NAME}}", params["locale_name"])
        .replace("{{LOCALE_CODE}}", params["locale_code"])
        .replace("{{DIACRITICS_RULE}}", params["diacritics_rule"])
        .replace("{{CANONICAL_SECTIONS_JSON}}", params["canonical_sections_json"])
        .replace("{{TIER_LABELS_JSON}}", params["tier_labels_json"])
        .replace("{{UNKNOWN_JOB_TITLE}}", params["unknown_job_title"])
    )
    assert "{{" not in rendered, "unresolved placeholder in PT-BR match prompt"
    assert "X" in rendered and "Y" in rendered
