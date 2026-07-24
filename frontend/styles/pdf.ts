/** PDF export style constants — mirrors the dark theme from the web UI. */

export const PDF_COLORS = {
  background: "#111112",
  card: "#1a1b1e",
  cardHover: "#25262b",
  primary: "#f1f3f5",
  muted: "#909296",
  faint: "#5c5f66",
  accent: "#a855f7",   // purple accent (gradient start)
  accentEnd: "#ec4899", // pink accent (gradient end)
  border: "#2e2f34",
  tier: {
    strong: "#22c55e",
    good: "#84cc16",
    moderate: "#eab308",
    stretch: "#f97316",
    low: "#ef4444",
  },
  criticality: {
    blocking: "#ef4444",
    important: "#eab308",
    niceToHave: "#22c55e",
  },
} as const;

export const PDF_FONTS = {
  display: "Helvetica-Bold",
  body: "Helvetica",
  mono: "Courier",
} as const;

export const PDF_SPACING = {
  section: 16,
  item: 10,
  gutter: 6,
} as const;
