# Match Prompt — Job Match Engine

> Prompt principal que gera o relatório. Combinado com `system_prompt.md` na chamada ao MiniMax.

---

## Prompt Template

```
TASK: Calculate a Job Match Score (0-100) by comparing the candidate's CV against the job description.

OUTPUT LANGUAGE: All text values inside the JSON response MUST be written in {{LOCALE_NAME}} ({{LOCALE_CODE}}). {{DIACRITICS_RULE}}

INPUTS:

<cv>
{{CV_CONTENT}}
</cv>

<job>
{{JOB_CONTENT}}
</job>

<target_market>
{{TARGET_MARKET}}
</target_market>

---

PROCEDURE:

1. Extract from CV: skills, total years of experience, years in target role/area, education level, certifications, languages with levels (CEFR if possible), location, declared seniority.

2. Extract from job: title, company (if mentioned), must-have requirements, nice-to-have requirements, language requirements with levels, modality (remote/hybrid/onsite), location, seniority level.

3. Identify the job's area/sector (Software Engineering / Data / DevOps / Product / Design / Sales / Marketing / Finance / etc.). This affects which hard skills are critical.

3b. **Target market adaptation (R-006).** If `<target_market>` is non-empty, calibrate the recommendations to the CV conventions of that market — length, which personal data is customary or discouraged, date format, and how achievements are expected to be phrased. If the value is "Not specified" / "Não especificado" / empty, skip this step. Do not invent market requirements the job does not mention — use this only to refine `gaps[].how_to_close` and `action_plan[].description`.

4. Apply the rubric below to score each of the 6 dimensions (each 0-100, integer):

| Dimension | Weight |
|-----------|--------|
| Hard Skills (Stack) | 30% |
| Experience | 25% |
| Education & Certifications | 15% |
| Languages | 10% |
| Soft Skills & Cultural Fit | 10% |
| Location & Logistics | 10% |

5. Compute the final score:
   score = round(
     hard_skills * 0.30 +
     experience  * 0.25 +
     education   * 0.15 +
     languages   * 0.10 +
     soft_skills * 0.10 +
     location    * 0.10
   )

6. Map score to tier using the labels below in {{LOCALE_CODE}}:
   {{TIER_LABELS_JSON}}
   - 85-100 → strong_match (first label)
   - 70-84  → good_match    (second label)
   - 55-69  → moderate_match (third label)
   - 40-54  → stretch_match  (fourth label)
   - 0-39   → low_match      (fifth label)

7. List **3 to 5 Match Strengths**: each ties a CV element directly to a job requirement, with cited evidence. Write in {{LOCALE_CODE}}.

8. List **all identified Gaps** (no fixed count, max 20): each is one of:
   - category: hard_skill | experience | education | language | soft_skill | logistics
   - criticality: blocking | important | nice_to_have
   - text: what the gap is (one sentence in {{LOCALE_CODE}})
   - how_to_close: concrete action (course, certification, project, role) in {{LOCALE_CODE}}

9. Build **Action Plan** of 3 to 7 prioritized actions. Write in {{LOCALE_CODE}}:
   - description: one sentence, concrete
   - estimated_duration: e.g. "2 weeks", "3 months" (use the locale's natural phrasing)
   - effort: low | medium | high
   - estimated_score_impact: integer (estimated points the score would gain)

10. **Date formatting consistency (R-002).** Scan all date occurrences in the CV (experience, education, certifications). Output `date_formatting.consistent: true` only if every date follows the same format. If multiple formats coexist (e.g. "05/2020" + "May 2020" + "2020-05"), set `consistent: false` and list 1-3 descriptions of the inconsistencies in {{LOCALE_CODE}} under `issues`. Each issue should reference the variant formats found.

11. **Standard headings check (R-003).** Detect which of these canonical CV sections are present (any common variant counts). Use ONLY the canonical names from the list below in {{LOCALE_CODE}}:
   {{CANONICAL_SECTIONS_JSON}}
   Output `standard_headings.found` with the canonical names detected (in {{LOCALE_CODE}}) and `standard_headings.missing` with the ones absent.

12. **Job title match (R-004).** Extract the candidate's most recent / current role title from the CV (`cv_title`) and the job's title from the posting (`target_title`). Set `aligned: true` only if they refer to the same role family at compatible seniority. Provide a one-sentence `note` in {{LOCALE_CODE}} explaining the alignment or the gap. If the CV has no clear current role, set `cv_title: null` and `aligned: false`. If the job title cannot be identified, use the fallback string "{{UNKNOWN_JOB_TITLE}}".

---

OUTPUT FORMAT:

Respond with ONLY this JSON object, nothing else (no markdown, no text before or after):

{
  "score": <int 0-100>,
  "tier": "<strong_match|good_match|moderate_match|stretch_match|low_match>",
  "tier_label": "<one of the labels in {{LOCALE_CODE}} from step 6>",
  "candidate_name": "<extracted from CV or null>",
  "job_title": "<extracted from job or '{{UNKNOWN_JOB_TITLE}}'>",
  "company": "<extracted from job or null>",
  "dimensions": {
    "hard_skills": <int 0-100>,
    "experience": <int 0-100>,
    "education": <int 0-100>,
    "languages": <int 0-100>,
    "soft_skills": <int 0-100>,
    "location": <int 0-100>
  },
  "strengths": [
    {
      "text": "<one sentence in {{LOCALE_CODE}} describing the strength>",
      "evidence": "<exact phrase from job + matching CV element>"
    }
  ],
  "gaps": [
    {
      "category": "<category>",
      "criticality": "<criticality>",
      "text": "<what's missing, one sentence in {{LOCALE_CODE}}>",
      "how_to_close": "<concrete action in {{LOCALE_CODE}}>"
    }
  ],
  "action_plan": [
    {
      "description": "<one sentence in {{LOCALE_CODE}}>",
      "estimated_duration": "<duration in {{LOCALE_CODE}}>",
      "effort": "<low|medium|high>",
      "estimated_score_impact": <int>
    }
  ],
  "date_formatting": {
    "consistent": <bool>,
    "issues": ["<one sentence in {{LOCALE_CODE}}>", ...]
  },
  "standard_headings": {
    "found": ["<canonical name in {{LOCALE_CODE}}>", ...],
    "missing": ["<canonical name in {{LOCALE_CODE}}>", ...]
  },
  "job_title_match": {
    "cv_title": "<most recent CV role or null>",
    "target_title": "<job posting title or null>",
    "aligned": <bool>,
    "note": "<one sentence in {{LOCALE_CODE}}>"
  }
}

---

REMEMBER:

- Output is JSON only. No markdown code blocks. No explanation text.
- All text values are in {{LOCALE_CODE}}. {{DIACRITICS_RULE}}
- All integer scores are rounded to integers, never decimals.
- Be honest. Don't inflate to please. Follow the rubric strictly.
- If the CV or job description has insufficient data to score (e.g., only a job title with no requirements), return:
  {"error": "insufficient_data", "missing_fields": ["job.requirements", ...]}
```

---

## Notes for the engine implementation

Assembled in `services/minimax_client.py`, method `MinimaxClient.match()`:

- `{{CV_CONTENT}}` and `{{JOB_CONTENT}}` receive the extracted text, already
  normalized by `services/security.py` and screened by `injection_guard`.
- `{{TARGET_MARKET}}` receives the localized market label (empty when unset).
- `{{LOCALE_NAME}}`, `{{LOCALE_CODE}}`, `{{DIACRITICS_RULE}}`,
  `{{CANONICAL_SECTIONS_JSON}}`, `{{TIER_LABELS_JSON}}` and
  `{{UNKNOWN_JOB_TITLE}}` come from `_PROMPT_PARAMS[locale]`.
- The system message is `system_prompt.md` (locale-substituted) followed by
  `scoring_rubric.md` and the output constraint.
- Request: `response_format` per provider (`json_object`, or `json_schema` for
  LM Studio), `temperature: 0`, no `max_tokens` cap (a tight cap starves a
  reasoning model before it emits any JSON), timeout from settings, one retry
  with exponential backoff on 5xx or timeout.
