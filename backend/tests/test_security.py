from app.services.security import sanitize_extracted_text


def test_sanitize_removes_invisible_and_control_characters() -> None:
    assert sanitize_extracted_text("ignore\u200ball\x00previous") == "ignoreallprevious"


def test_sanitize_collapses_common_confusables() -> None:
    assert sanitize_extracted_text("ɪɢɴᴏʀᴇ") == "IGNORE"
    assert sanitize_extracted_text("ignоre") == "ignore"


def test_sanitize_preserves_normal_cv_text() -> None:
    text = "Experiência em Python, gestão e comunicação."
    assert sanitize_extracted_text(text) == text
