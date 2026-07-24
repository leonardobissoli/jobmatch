import { z } from "zod";

// Canonical locale codes used throughout the app.
export const LOCALES = ["pt-BR", "en"] as const;
export type Locale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: Locale = "pt-BR";

// Internal keys for target market. Wire format is language-neutral.
// Backend maps these to localized labels when building LLM prompts.
export type TargetMarketKey = "NONE" | "BR" | "PT" | "UK" | "EU" | "US";

export const TierSchema = z.enum([
  "strong_match",
  "good_match",
  "moderate_match",
  "stretch_match",
  "low_match",
]);
export type Tier = z.infer<typeof TierSchema>;

export const DimensionsSchema = z.object({
  hard_skills: z.number().int().min(0).max(100),
  experience: z.number().int().min(0).max(100),
  education: z.number().int().min(0).max(100),
  languages: z.number().int().min(0).max(100),
  soft_skills: z.number().int().min(0).max(100),
  location: z.number().int().min(0).max(100),
});

export const StrengthSchema = z.object({
  text: z.string(),
  evidence: z.string(),
});

export const GapSchema = z.object({
  category: z.enum([
    "hard_skill",
    "experience",
    "education",
    "language",
    "soft_skill",
    "logistics",
  ]),
  criticality: z.enum(["blocking", "important", "nice_to_have"]),
  text: z.string(),
  how_to_close: z.string(),
});

export const ActionItemSchema = z.object({
  description: z.string(),
  estimated_duration: z.string(),
  effort: z.enum(["low", "medium", "high"]),
  estimated_score_impact: z.number().int(),
});

export const ResumeLengthStatusSchema = z.enum(["too_short", "ideal", "too_long"]);
export type ResumeLengthStatus = z.infer<typeof ResumeLengthStatusSchema>;

export const ResumeLengthSchema = z.object({
  word_count: z.number().int().nonnegative(),
  estimated_pages: z.number().nonnegative(),
  status: ResumeLengthStatusSchema,
  message: z.string(),
});
export type ResumeLength = z.infer<typeof ResumeLengthSchema>;

export const DateFormattingSchema = z.object({
  consistent: z.boolean(),
  issues: z.array(z.string()).default([]),
});
export type DateFormatting = z.infer<typeof DateFormattingSchema>;

export const StandardHeadingsSchema = z.object({
  found: z.array(z.string()).default([]),
  missing: z.array(z.string()).default([]),
});
export type StandardHeadings = z.infer<typeof StandardHeadingsSchema>;

export const JobTitleMatchSchema = z.object({
  cv_title: z.string().nullable().optional(),
  target_title: z.string().nullable().optional(),
  aligned: z.boolean(),
  note: z.string(),
});
export type JobTitleMatch = z.infer<typeof JobTitleMatchSchema>;

export const MatchResultSchema = z.object({
  match_id: z.string(),
  score: z.number().int().min(0).max(100),
  tier: TierSchema,
  tier_label: z.string(),
  candidate_name: z.string().nullable().optional(),
  job_title: z.string(),
  company: z.string().nullable().optional(),
  dimensions: DimensionsSchema,
  strengths: z.array(StrengthSchema),
  gaps: z.array(GapSchema),
  action_plan: z.array(ActionItemSchema),
  resume_length: ResumeLengthSchema.nullable().optional(),
  date_formatting: DateFormattingSchema.nullable().optional(),
  standard_headings: StandardHeadingsSchema.nullable().optional(),
  job_title_match: JobTitleMatchSchema.nullable().optional(),
  generated_at: z.string(),
});

export type MatchResult = z.infer<typeof MatchResultSchema>;
export type Dimensions = z.infer<typeof DimensionsSchema>;
export type Strength = z.infer<typeof StrengthSchema>;
export type Gap = z.infer<typeof GapSchema>;
export type ActionItem = z.infer<typeof ActionItemSchema>;

export const ErrorResponseSchema = z.object({
  error: z.string(),
  message: z.string(),
  details: z.string().optional(),
  retry_after_seconds: z.number().optional(),
  retry_after_human: z.string().optional(),
});

export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;

export const TIER_COLOR: Record<Tier, string> = {
  strong_match: "#22c55e",
  good_match: "#84cc16",
  moderate_match: "#eab308",
  stretch_match: "#f97316",
  low_match: "#ef4444",
};

// Locale-aware label maps. Indexed by domain key first, locale second so
// `DIMENSION_LABEL[k][locale]` narrows cleanly in TypeScript.
export const DIMENSION_LABEL: Record<keyof Dimensions, Record<Locale, string>> = {
  hard_skills: { "pt-BR": "Hard Skills", en: "Hard Skills" },
  experience: { "pt-BR": "Experiência", en: "Experience" },
  education: { "pt-BR": "Educação", en: "Education" },
  languages: { "pt-BR": "Idiomas", en: "Languages" },
  soft_skills: { "pt-BR": "Soft Skills", en: "Soft Skills" },
  location: { "pt-BR": "Localização", en: "Location" },
};

export const CRITICALITY_LABEL: Record<Gap["criticality"], Record<Locale, string>> = {
  blocking: { "pt-BR": "🔴 Bloqueante", en: "🔴 Blocking" },
  important: { "pt-BR": "🟡 Importante", en: "🟡 Important" },
  nice_to_have: { "pt-BR": "🟢 Nice to have", en: "🟢 Nice to have" },
};

export const EFFORT_LABEL: Record<ActionItem["effort"], Record<Locale, string>> = {
  low: { "pt-BR": "Baixo", en: "Low" },
  medium: { "pt-BR": "Médio", en: "Medium" },
  high: { "pt-BR": "Alto", en: "High" },
};

export const RESUME_LENGTH_LABEL: Record<ResumeLengthStatus, Record<Locale, string>> = {
  too_short: { "pt-BR": "🟡 Curto", en: "🟡 Short" },
  ideal: { "pt-BR": "🟢 Ideal", en: "🟢 Ideal" },
  too_long: { "pt-BR": "🟡 Longo", en: "🟡 Longo" },
};

export const RESUME_LENGTH_COLOR: Record<ResumeLengthStatus, string> = {
  too_short: "#eab308",
  ideal: "#22c55e",
  too_long: "#eab308",
};

// Locale-aware target market options. `value` is the canonical key sent to
// the backend (language-neutral). `labelKey` references the message file.
export const TARGET_MARKET_OPTIONS: ReadonlyArray<{
  value: TargetMarketKey | "";
  labelKey: TargetMarketKey;
}> = [
  { value: "", labelKey: "NONE" },
  { value: "BR", labelKey: "BR" },
  { value: "PT", labelKey: "PT" },
  { value: "UK", labelKey: "UK" },
  { value: "EU", labelKey: "EU" },
  { value: "US", labelKey: "US" },
];
