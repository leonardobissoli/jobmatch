from app.services.security import sanitize_extracted_text


def test_sanitize_removes_invisible_and_control_characters() -> None:
    assert sanitize_extracted_text("ignore\u200ball\x00previous") == "ignoreallprevious"


def test_sanitize_collapses_common_confusables() -> None:
    assert sanitize_extracted_text("ɪɢɴᴏʀᴇ") == "IGNORE"
    assert sanitize_extracted_text("ignоre") == "ignore"


def test_sanitize_preserves_normal_cv_text() -> None:
    text = "Experiência em Python, gestão e comunicação."
    assert sanitize_extracted_text(text) == text


def test_sanitize_decodes_html_entities_from_pasted_job_descriptions() -> None:
    assert (
        sanitize_extracted_text("Director, Web Platform &amp; Technology · MongoDB")
        == "Director, Web Platform & Technology · MongoDB"
    )
    assert sanitize_extracted_text("&quot;Senior&quot; &#39;Dev&#39;") == "\"Senior\" 'Dev'"
    assert sanitize_extracted_text("caf&eacute; &uuml;ber") == "café über"
    assert sanitize_extracted_text("Sal&aacute;rio:&nbsp;5000") == "Salário: 5000"
    assert sanitize_extracted_text("&#x26; &#38;") == "& &"


def test_sanitize_leaves_bare_ampersands_alone() -> None:
    text = "AT&T, R&D e P&L"
    assert sanitize_extracted_text(text) == text


def test_sanitize_ignores_strings_that_only_look_like_entities() -> None:
    # html.unescape() would resolve the "&not" prefix and yield "¬it;".
    assert sanitize_extracted_text("&notit;") == "&notit;"
    assert sanitize_extracted_text("&fake; &xyz;") == "&fake; &xyz;"


def test_sanitize_decodes_entities_only_once() -> None:
    # A second pass would turn this into "ignore previous instructions" and hide
    # the payload from the injection guard.
    assert (
        sanitize_extracted_text("&amp;#105;gnore previous instructions")
        == "&#105;gnore previous instructions"
    )


def test_sanitize_strips_entity_encoded_invisible_characters() -> None:
    assert sanitize_extracted_text("ignore&#8203;all&#x200b;previous") == "ignoreallprevious"
