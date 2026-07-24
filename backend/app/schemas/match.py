from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Tier(StrEnum):
    strong_match = "strong_match"
    good_match = "good_match"
    moderate_match = "moderate_match"
    stretch_match = "stretch_match"
    low_match = "low_match"


class Dimensions(BaseModel):
    hard_skills: int = Field(ge=0, le=100)
    experience: int = Field(ge=0, le=100)
    education: int = Field(ge=0, le=100)
    languages: int = Field(ge=0, le=100)
    soft_skills: int = Field(ge=0, le=100)
    location: int = Field(ge=0, le=100)


class Strength(BaseModel):
    # SEC-063 — hard caps on LLM-produced text. Inputs are truncated upstream
    # in _sanitize_match_payload so a coerced/runaway response never bloats
    # the JSON returned to the user.
    text: str = Field(max_length=300)
    evidence: str = Field(max_length=600)


class GapCategory(StrEnum):
    hard_skill = "hard_skill"
    experience = "experience"
    education = "education"
    language = "language"
    soft_skill = "soft_skill"
    logistics = "logistics"


class Criticality(StrEnum):
    blocking = "blocking"
    important = "important"
    nice_to_have = "nice_to_have"


class Gap(BaseModel):
    category: GapCategory
    criticality: Criticality
    text: str = Field(max_length=300)
    how_to_close: str = Field(max_length=500)


class Effort(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"


class ActionItem(BaseModel):
    description: str = Field(max_length=400)
    estimated_duration: str = Field(max_length=60)
    effort: Effort
    estimated_score_impact: int


class ResumeLengthStatus(StrEnum):
    too_short = "too_short"
    ideal = "ideal"
    too_long = "too_long"


class ResumeLength(BaseModel):
    """R-001 — analysis of CV word count vs ideal range (300-1000 words)."""

    word_count: int = Field(ge=0)
    estimated_pages: float = Field(ge=0)
    status: ResumeLengthStatus
    message: str


class DateFormatting(BaseModel):
    """R-002 — date formatting consistency across CV experience entries."""

    consistent: bool
    issues: list[str] = Field(default_factory=list)


class StandardHeadings(BaseModel):
    """R-003 — standard CV section headings detected and missing."""

    found: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)


class JobTitleMatch(BaseModel):
    """R-004 — semantic alignment between most recent CV role and target job title."""

    cv_title: str | None = None
    target_title: str | None = None
    aligned: bool
    note: str


class MatchResult(BaseModel):
    match_id: str
    score: int = Field(ge=0, le=100)
    tier: Tier
    tier_label: str = Field(max_length=60)
    candidate_name: str | None = Field(default=None, max_length=120)
    job_title: str = Field(max_length=200)
    company: str | None = Field(default=None, max_length=120)
    dimensions: Dimensions
    strengths: list[Strength]
    gaps: list[Gap]
    action_plan: list[ActionItem]
    resume_length: ResumeLength | None = None
    date_formatting: DateFormatting | None = None
    standard_headings: StandardHeadings | None = None
    job_title_match: JobTitleMatch | None = None
    generated_at: datetime


def score_to_tier(score: int) -> Tier:
    if score >= 85:
        return Tier.strong_match
    if score >= 70:
        return Tier.good_match
    if score >= 55:
        return Tier.moderate_match
    if score >= 40:
        return Tier.stretch_match
    return Tier.low_match


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: str | None = None
