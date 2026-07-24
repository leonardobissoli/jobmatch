"""SEC-063 — output-field length caps on LLM-produced match payloads."""
from datetime import UTC, datetime

from app.schemas.match import MatchResult
from app.services.job_match_engine import _clean_str, _sanitize_match_payload


def _base_payload(**overrides) -> dict:
    base: dict = {
        "match_id": "00000000-0000-0000-0000-000000000000",
        "score": 80,
        "tier": "good_match",
        "tier_label": "Bom Match",
        "candidate_name": "Fulano",
        "job_title": "Engineer",
        "company": "Acme",
        "dimensions": {
            "hard_skills": 80, "experience": 80, "education": 80,
            "languages": 80, "soft_skills": 80, "location": 80,
        },
        "strengths": [],
        "gaps": [],
        "action_plan": [],
        "generated_at": datetime.now(UTC).isoformat(),
    }
    base.update(overrides)
    return base


class TestCleanStr:
    def test_truncates_with_ellipsis(self) -> None:
        out = _clean_str("a" * 1000, max_len=50)
        assert len(out) == 50
        assert out.endswith("…")

    def test_no_truncation_when_under_cap(self) -> None:
        assert _clean_str("hello", max_len=50) == "hello"

    def test_strips_html(self) -> None:
        assert _clean_str("<script>x</script>safe", max_len=100) == "xsafe"

    def test_non_string_passthrough(self) -> None:
        assert _clean_str(42) == 42
        assert _clean_str(None) is None


class TestSanitizeMatchPayload:
    def test_runaway_action_plan_truncated(self) -> None:
        raw = _base_payload(
            action_plan=[
                {
                    "description": "x" * 10_000,
                    "estimated_duration": "y" * 500,
                    "effort": "medium",
                    "estimated_score_impact": 5,
                }
            ],
        )
        _sanitize_match_payload(raw)
        desc = raw["action_plan"][0]["description"]
        dur = raw["action_plan"][0]["estimated_duration"]
        assert len(desc) <= 400 and desc.endswith("…")
        assert len(dur) <= 60 and dur.endswith("…")
        # And critically: the payload now validates through Pydantic.
        MatchResult.model_validate(raw)

    def test_long_gap_fields_truncated(self) -> None:
        raw = _base_payload(
            gaps=[
                {
                    "category": "hard_skill",
                    "criticality": "important",
                    "text": "g" * 1000,
                    "how_to_close": "h" * 5000,
                }
            ],
        )
        _sanitize_match_payload(raw)
        g = raw["gaps"][0]
        assert len(g["text"]) <= 300 and g["text"].endswith("…")
        assert len(g["how_to_close"]) <= 500 and g["how_to_close"].endswith("…")
        MatchResult.model_validate(raw)

    def test_long_strength_fields_truncated(self) -> None:
        raw = _base_payload(
            strengths=[{"text": "s" * 1000, "evidence": "e" * 1000}],
        )
        _sanitize_match_payload(raw)
        s = raw["strengths"][0]
        assert len(s["text"]) <= 300
        assert len(s["evidence"]) <= 600
        MatchResult.model_validate(raw)

    def test_long_top_level_fields_truncated(self) -> None:
        raw = _base_payload(
            candidate_name="c" * 1000,
            job_title="j" * 1000,
            company="x" * 1000,
            tier_label="t" * 1000,
        )
        _sanitize_match_payload(raw)
        assert len(raw["candidate_name"]) <= 120
        assert len(raw["job_title"]) <= 200
        assert len(raw["company"]) <= 120
        assert len(raw["tier_label"]) <= 60
        MatchResult.model_validate(raw)
