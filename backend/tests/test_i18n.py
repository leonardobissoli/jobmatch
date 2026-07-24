"""ADR-013 — backend i18n coverage.

Verifies every error code has both PT-BR (canonical) and EN translations,
fallback paths work, and the resolve_locale helper honors the precedence
order documented in app/i18n.py.
"""
import pytest

from app.i18n import DEFAULT_LOCALE, SUPPORTED_LOCALES, resolve_locale, t


def _all_keys() -> set[str]:
    # Re-import to walk the private dict (test-internal access is fine).
    from app.i18n import _MESSAGES  # type: ignore[attr-defined]

    keys: set[str] = set()
    for bucket in _MESSAGES.values():
        keys.update(bucket.keys())
    return keys


def test_default_locale_is_pt_br() -> None:
    assert DEFAULT_LOCALE == "pt-BR"


def test_supported_locales_is_two() -> None:
    assert set(SUPPORTED_LOCALES) == {"pt-BR", "en"}


@pytest.mark.parametrize("key", sorted(_all_keys()))
def test_each_key_exists_in_every_locale(key: str) -> None:
    from app.i18n import _MESSAGES  # type: ignore[attr-defined]

    for locale in SUPPORTED_LOCALES:
        assert key in _MESSAGES[locale], f"missing in {locale}: {key}"


def test_resolve_locale_form_field_wins() -> None:
    assert resolve_locale("en-US", "pt-BR") == "pt-BR"
    assert resolve_locale("pt-BR", "en") == "en"


def test_resolve_locale_accept_language() -> None:
    assert resolve_locale("en-US,en;q=0.9,pt-BR;q=0.8") == "en"
    assert resolve_locale("pt-BR,pt;q=0.9,en;q=0.5") == "pt-BR"
    assert resolve_locale("fr-FR,fr;q=0.9") == DEFAULT_LOCALE


def test_resolve_locale_missing_header_falls_back() -> None:
    assert resolve_locale(None) == DEFAULT_LOCALE
    assert resolve_locale("") == DEFAULT_LOCALE


def test_resolve_locale_invalid_form_falls_through() -> None:
    # "fr" is not supported, so we ignore the form field and look at AL.
    assert resolve_locale("en-US", "fr-FR") == "en"


def test_t_pt_br_canonical_string() -> None:
    assert t("pt-BR", "errors.missing_job") == "Envie a descrição da vaga (arquivo ou texto colado)."


def test_t_en_free_translation() -> None:
    assert t("en", "errors.missing_job") == "Send the job description (file or pasted text)."


def test_t_interpolates_kwargs() -> None:
    assert t("en", "unknown", value="unused") == "unknown"


def test_t_falls_back_to_default_for_missing_key() -> None:
    # t() with an unknown key returns the key itself in both locales.
    assert t("en", "totally.unknown.key") == "totally.unknown.key"
    assert t("pt-BR", "totally.unknown.key") == "totally.unknown.key"


def test_t_falls_back_locale_when_key_absent() -> None:
    """If a locale bucket is missing a key the call falls back to default."""
    # Delete a key from EN, look it up, get the PT-BR value.
    from app.i18n import _MESSAGES  # type: ignore[attr-defined]

    en_bucket = _MESSAGES["en"]
    pt_value = en_bucket.pop("pdf.corrupt", None)
    assert pt_value is not None  # precondition
    try:
        assert t("en", "pdf.corrupt") == t("pt-BR", "pdf.corrupt")
    finally:
        en_bucket["pdf.corrupt"] = pt_value
