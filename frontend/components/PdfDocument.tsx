"use client";

import {
  Circle,
  Document,
  Page,
  Svg,
  Text,
  View,
} from "@react-pdf/renderer";
import { StyleSheet } from "@react-pdf/renderer";

import type { MatchResult } from "@/lib/schemas";
import {
  DIMENSION_LABEL,
  EFFORT_LABEL,
  type Locale,
  TIER_COLOR,
} from "@/lib/schemas";

import { PDF_COLORS, PDF_FONTS, PDF_SPACING } from "@/styles/pdf";

const styles = StyleSheet.create({
  page: {
    backgroundColor: PDF_COLORS.background,
    color: PDF_COLORS.primary,
    fontFamily: PDF_FONTS.body,
    fontSize: 10,
    padding: 32,
    lineHeight: 1.45,
  },
  // ---- header ----
  headerRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 20,
    marginBottom: PDF_SPACING.section,
    padding: 16,
    backgroundColor: PDF_COLORS.card,
    borderRadius: 8,
  },
  scoreContainer: {
    width: 120,
    height: 120,
    position: "relative",
  },
  scoreText: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: "center",
    alignItems: "center",
    fontFamily: PDF_FONTS.display,
    fontSize: 32,
  },
  scoreLabel: {
    fontSize: 8,
    color: PDF_COLORS.faint,
    textAlign: "center",
    marginTop: -4,
  },
  headerInfo: {
    flex: 1,
    gap: 6,
  },
  headerLabel: {
    fontSize: 8,
    color: PDF_COLORS.muted,
    letterSpacing: 1,
  },
  jobTitle: {
    fontFamily: PDF_FONTS.display,
    fontSize: 18,
    color: PDF_COLORS.primary,
  },
  candidateName: {
    fontSize: 9,
    color: PDF_COLORS.muted,
  },
  tierLabel: {
    fontSize: 14,
    fontFamily: PDF_FONTS.display,
  },
  // ---- section ----
  sectionTitle: {
    fontFamily: PDF_FONTS.display,
    fontSize: 13,
    color: PDF_COLORS.primary,
    marginBottom: 8,
  },
  card: {
    backgroundColor: PDF_COLORS.card,
    padding: 12,
    borderRadius: 6,
    marginBottom: 8,
  },
  cardRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  // ---- dimension bars ----
  dimGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: PDF_SPACING.section,
  },
  dimCard: {
    width: "48%",
    backgroundColor: PDF_COLORS.card,
    padding: 10,
    borderRadius: 6,
  },
  dimLabelRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 4,
  },
  dimLabel: {
    fontSize: 9,
    color: PDF_COLORS.muted,
  },
  dimScore: {
    fontFamily: PDF_FONTS.mono,
    fontSize: 9,
    color: PDF_COLORS.primary,
  },
  barBg: {
    height: 6,
    backgroundColor: PDF_COLORS.cardHover,
    borderRadius: 3,
    overflow: "hidden",
  },
  barFill: {
    height: "100%",
    backgroundColor: PDF_COLORS.accent,
    borderRadius: 3,
  },
  // ---- sub-analysis cards ----
  subGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: PDF_SPACING.section,
  },
  subCard: {
    width: "48%",
    backgroundColor: PDF_COLORS.card,
    padding: 10,
    borderRadius: 6,
  },
  subTitle: {
    fontSize: 7,
    color: PDF_COLORS.faint,
    letterSpacing: 1,
    textTransform: "uppercase",
    marginBottom: 4,
  },
  subLabel: {
    fontFamily: PDF_FONTS.display,
    fontSize: 11,
    marginBottom: 4,
  },
  subText: {
    fontSize: 9,
    color: PDF_COLORS.muted,
  },
  subRow: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 2,
  },
  subVal: {
    fontSize: 9,
    color: PDF_COLORS.primary,
  },
  // ---- strengths ----
  strengthItem: {
    backgroundColor: PDF_COLORS.card,
    padding: 10,
    borderRadius: 6,
    marginBottom: 6,
    borderLeftWidth: 3,
    borderLeftColor: PDF_COLORS.tier.strong,
  },
  strengthText: {
    fontSize: 10,
    color: PDF_COLORS.primary,
    marginBottom: 2,
  },
  strengthEvidence: {
    fontSize: 8,
    color: PDF_COLORS.muted,
    fontStyle: "italic",
  },
  // ---- gaps ----
  gapCard: {
    backgroundColor: PDF_COLORS.card,
    padding: 10,
    borderRadius: 6,
    marginBottom: 6,
  },
  gapHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 4,
  },
  gapCriticality: {
    fontFamily: PDF_FONTS.display,
    fontSize: 10,
  },
  gapCategory: {
    fontSize: 8,
    color: PDF_COLORS.faint,
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  gapText: {
    fontSize: 10,
    color: PDF_COLORS.primary,
    marginBottom: 4,
  },
  gapAction: {
    fontSize: 9,
    color: PDF_COLORS.muted,
  },
  gapActionLabel: {
    fontFamily: PDF_FONTS.display,
    fontSize: 9,
    color: PDF_COLORS.primary,
  },
  // ---- action plan ----
  actionCard: {
    flexDirection: "row",
    gap: 10,
    backgroundColor: PDF_COLORS.card,
    padding: 10,
    borderRadius: 6,
    marginBottom: 6,
    alignItems: "flex-start",
  },
  actionNumber: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: PDF_COLORS.accent,
    justifyContent: "center",
    alignItems: "center",
    fontFamily: PDF_FONTS.display,
    fontSize: 12,
    color: PDF_COLORS.background,
  },
  actionBody: {
    flex: 1,
    gap: 4,
  },
  actionDesc: {
    fontSize: 10,
    color: PDF_COLORS.primary,
  },
  actionMeta: {
    flexDirection: "row",
    gap: 8,
    fontSize: 8,
    color: PDF_COLORS.muted,
  },
  actionScore: {
    color: PDF_COLORS.tier.good,
  },
  // ---- footer ----
  footer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: PDF_COLORS.border,
    marginTop: PDF_SPACING.section,
  },
  footerText: {
    fontSize: 7,
    fontFamily: PDF_FONTS.mono,
    color: PDF_COLORS.faint,
  },
  brandText: {
    fontSize: 7,
    color: PDF_COLORS.muted,
    textAlign: "right",
  },
});

// ---------------------------------------------------------------------------
// Radial score ring (SVG)
// ---------------------------------------------------------------------------
function ScoreRadialPdf({ score, color }: { score: number; color: string }) {
  const size = 120;
  const stroke = 10;
  const radius = (size - stroke) / 2;
  // Draw the progress arc via strokeDasharray (supported by @react-pdf v4)
  // instead of strokeDashoffset (absent from v4 types). rotate(-90) starts the
  // arc at 12 o'clock so it reads as a gauge proportional to the score.
  const circumference = 2 * Math.PI * radius;
  const pct = Math.max(0, Math.min(100, score)) / 100;
  const arc = circumference * pct;

  return (
    <View style={styles.scoreContainer}>
      <Svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={PDF_COLORS.cardHover}
          strokeWidth={stroke}
          fill="none"
        />
        <Circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={stroke}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={`${arc} ${circumference}`}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </Svg>
      <View style={styles.scoreText}>
        <Text style={{ fontSize: 28, fontFamily: PDF_FONTS.display, color }}>
          {score}
        </Text>
        <Text style={styles.scoreLabel}>/ 100</Text>
      </View>
    </View>
  );
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------
type Props = {
  result: MatchResult;
  locale: Locale;
};

// Standard PDF fonts (Helvetica/Courier) can't render emoji. A raw 🟢/🟡 in
// tier_label (or any emoji in LLM text) corrupts the glyph + ToUnicode layer:
// garbled visual (shows "=") and broken copy-paste ("Match" -> "Máatch"). The
// web report keeps the emoji on purpose; here we strip it from every string.
const EMOJI_RE =
  /[\u{1F000}-\u{1FFFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{FE00}-\u{FE0F}\u{200D}]/gu;

function stripEmojiDeep<T>(value: T): T {
  if (typeof value === "string") {
    return value.replace(EMOJI_RE, "").replace(/\s{2,}/g, " ").trim() as unknown as T;
  }
  if (Array.isArray(value)) {
    return value.map((v) => stripEmojiDeep(v)) as unknown as T;
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([k, v]) => [k, stripEmojiDeep(v)]),
    ) as T;
  }
  return value;
}

// ---------------------------------------------------------------------------
// PDF Document
// ---------------------------------------------------------------------------
export default function PdfDocument({ result: rawResult, locale }: Props) {
  const result = stripEmojiDeep(rawResult);
  const tierColor = TIER_COLOR[result.tier];

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* ============ HEADER ============ */}
        <View style={styles.headerRow}>
          <ScoreRadialPdf score={result.score} color={tierColor} />
          <View style={styles.headerInfo}>
            <Text style={styles.headerLabel}>Vaga analisada / Job analyzed</Text>
            <Text style={styles.jobTitle}>
              {result.job_title}
              {result.company ? ` · ${result.company}` : ""}
            </Text>
            {result.candidate_name && (
              <Text style={styles.candidateName}>
                Candidato / Candidate: {result.candidate_name}
              </Text>
            )}
            <Text style={[styles.tierLabel, { color: tierColor }]}>
              {result.tier_label}
            </Text>
          </View>
        </View>

        {/* ============ DIMENSION BARS ============ */}
        <Text style={styles.sectionTitle}>
          {locale === "pt-BR" ? "Breakdown por dimensão" : "Breakdown by dimension"}
        </Text>
        <View style={styles.dimGrid}>
          {(Object.keys(result.dimensions) as Array<keyof typeof result.dimensions>).map((k) => (
            <View key={k} style={styles.dimCard}>
              <View style={styles.dimLabelRow}>
                <Text style={styles.dimLabel}>{DIMENSION_LABEL[k][locale]}</Text>
                <Text style={styles.dimScore}>{result.dimensions[k]}</Text>
              </View>
              <View style={styles.barBg}>
                <View
                  style={[
                    styles.barFill,
                    { width: `${result.dimensions[k]}%` },
                  ]}
                />
              </View>
            </View>
          ))}
        </View>

        {/* ============ SUB-ANALYSIS CARDS ============ */}
        {result.job_title_match && (
          <View style={styles.subGrid}>
            <JobTitleCard data={result.job_title_match} locale={locale} />
            {result.resume_length && (
              <ResumeLengthCard data={result.resume_length} locale={locale} />
            )}
          </View>
        )}

        {result.standard_headings && (
          <View style={styles.subGrid}>
            <StandardHeadingsCard data={result.standard_headings} locale={locale} />
            {result.date_formatting && (
              <DateFormattingCard data={result.date_formatting} locale={locale} />
            )}
          </View>
        )}

        {/* ============ STRENGTHS ============ */}
        <Text style={styles.sectionTitle}>
          {locale === "pt-BR" ? "Pontos fortes" : "Match strengths"}
        </Text>
        {result.strengths.map((s, i) => (
          <View key={i} style={styles.strengthItem}>
            <Text style={styles.strengthText}>{s.text}</Text>
            <Text style={styles.strengthEvidence}>{s.evidence}</Text>
          </View>
        ))}

        {/* ============ GAPS ============ */}
        {result.gaps.length > 0 && (
          <>
            <Text style={styles.sectionTitle}>
              {locale === "pt-BR" ? "Lacunas" : "Gaps"}
            </Text>
            {result.gaps.map((g, i) => (
              <View key={i} style={styles.gapCard}>
                <View style={styles.gapHeader}>
                  <Text
                    style={[
                      styles.gapCriticality,
                      {
                        color:
                          g.criticality === "blocking"
                            ? PDF_COLORS.tier.low
                            : g.criticality === "important"
                              ? PDF_COLORS.tier.moderate
                              : PDF_COLORS.tier.good,
                      },
                    ]}
                  >
                    {g.criticality === "blocking"
                      ? locale === "pt-BR" ? "Bloqueante" : "Blocking"
                      : g.criticality === "important"
                        ? locale === "pt-BR" ? "Importante" : "Important"
                        : locale === "pt-BR" ? "Nice to have" : "Nice to have"}
                  </Text>
                  <Text style={styles.gapCategory}>
                    {g.category.replace(/_/g, " ")}
                  </Text>
                </View>
                <Text style={styles.gapText}>{g.text}</Text>
                <Text style={styles.gapAction}>
                  <Text style={styles.gapActionLabel}>
                    {locale === "pt-BR" ? "Como fechar:" : "How to close:"}{" "}
                  </Text>
                  {g.how_to_close}
                </Text>
              </View>
            ))}
          </>
        )}

        {/* ============ ACTION PLAN ============ */}
        <Text style={styles.sectionTitle}>
          {locale === "pt-BR" ? "Plano de ação" : "Action plan"}
        </Text>
        {result.action_plan.map((a, i) => (
          <View key={i} style={styles.actionCard}>
            <View style={styles.actionNumber}>
              <Text>{i + 1}</Text>
            </View>
            <View style={styles.actionBody}>
              <Text style={styles.actionDesc}>{a.description}</Text>
              <View style={styles.actionMeta}>
                <Text>{a.estimated_duration}</Text>
                <Text>
                  {locale === "pt-BR"
                    ? `esforço: ${EFFORT_LABEL[a.effort][locale]}`
                    : `effort: ${EFFORT_LABEL[a.effort][locale]}`}
                </Text>
                <Text style={styles.actionScore}>
                  +{a.estimated_score_impact} pts
                </Text>
              </View>
            </View>
          </View>
        ))}

        {/* ============ FOOTER ============ */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            id: {result.match_id.slice(0, 8)}
          </Text>
          <Text style={styles.brandText}>
            Gerado por Job Match — Tech Hub
            {result.generated_at
              ? ` · ${new Date(result.generated_at).toLocaleDateString(
                  locale === "pt-BR" ? "pt-BR" : "en-US",
                )}`
              : ""}
          </Text>
        </View>
      </Page>
    </Document>
  );
}

// ---------------------------------------------------------------------------
// Sub-cards
// ---------------------------------------------------------------------------
function JobTitleCard({
  data,
  locale,
}: {
  data: NonNullable<MatchResult["job_title_match"]>;
  locale: Locale;
}) {
  const color = data.aligned ? "#22c55e" : "#eab308";
  const label = data.aligned
    ? locale === "pt-BR" ? "Alinhado" : "Aligned"
    : locale === "pt-BR" ? "Desalinhado" : "Misaligned";
  return (
    <View style={styles.subCard}>
      <Text style={styles.subTitle}>
        {locale === "pt-BR" ? "Cargo: CV × vaga" : "Role: CV × job"}
      </Text>
      <Text style={[styles.subLabel, { color }]}>
        {label}
      </Text>
      <View style={styles.subRow}>
        <Text style={styles.subText}>
          {locale === "pt-BR" ? "CV:" : "CV:"}{" "}
          <Text style={styles.subVal}>{data.cv_title || "—"}</Text>
        </Text>
        <Text style={styles.subText}>
          {locale === "pt-BR" ? "Vaga:" : "Job:"}{" "}
          <Text style={styles.subVal}>{data.target_title || "—"}</Text>
        </Text>
      </View>
      <Text style={styles.subText}>{data.note}</Text>
    </View>
  );
}

function ResumeLengthCard({
  data,
  locale,
}: {
  data: NonNullable<MatchResult["resume_length"]>;
  locale: Locale;
}) {
  const color =
    data.status === "ideal" ? PDF_COLORS.tier.good : PDF_COLORS.tier.moderate;
  return (
    <View style={styles.subCard}>
      <Text style={styles.subTitle}>
        {locale === "pt-BR" ? "Tamanho do CV" : "Resume length"}
      </Text>
      <Text style={[styles.subLabel, { color }]}>
        {locale === "pt-BR"
          ? data.status === "too_short" ? "Curto" : data.status === "too_long" ? "Longo" : "Ideal"
          : data.status === "too_short" ? "Short" : data.status === "too_long" ? "Long" : "Ideal"}
      </Text>
      <View style={styles.subRow}>
        <Text style={styles.subText}>
          {data.word_count}{" "}
          {locale === "pt-BR" ? "palavras" : "words"}
        </Text>
        <Text style={styles.subText}>
          ≈ {data.estimated_pages}{" "}
          {locale === "pt-BR" ? "páginas" : "pages"}
        </Text>
      </View>
      <Text style={styles.subText}>{data.message}</Text>
    </View>
  );
}

function StandardHeadingsCard({
  data,
  locale,
}: {
  data: NonNullable<MatchResult["standard_headings"]>;
  locale: Locale;
}) {
  const hasAny = data.found.length > 0 || data.missing.length > 0;
  if (!hasAny) return null;
  return (
    <View style={styles.subCard}>
      <Text style={styles.subTitle}>
        {locale === "pt-BR" ? "Seções do CV" : "CV sections"}
      </Text>
      <View style={{ gap: 4 }}>
        <Text style={[styles.subText, { color: PDF_COLORS.tier.good }]}>
          {locale === "pt-BR" ? "Presentes" : "Present"}: {data.found.join(", ") || "—"}
        </Text>
        <Text style={[styles.subText, { color: PDF_COLORS.tier.moderate }]}>
          {locale === "pt-BR" ? "Ausentes" : "Missing"}: {data.missing.join(", ") || "—"}
        </Text>
      </View>
    </View>
  );
}

function DateFormattingCard({
  data,
  locale,
}: {
  data: NonNullable<MatchResult["date_formatting"]>;
  locale: Locale;
}) {
  const color = data.consistent ? PDF_COLORS.tier.good : PDF_COLORS.tier.moderate;
  const label = data.consistent
    ? locale === "pt-BR" ? "Consistente" : "Consistent"
    : locale === "pt-BR" ? "Inconsistente" : "Inconsistent";
  return (
    <View style={styles.subCard}>
      <Text style={styles.subTitle}>
        {locale === "pt-BR" ? "Formatação de datas" : "Date formatting"}
      </Text>
      <Text style={[styles.subLabel, { color }]}>{label}</Text>
      {data.issues.length > 0 && (
        <Text style={styles.subText}>{data.issues.join("; ")}</Text>
      )}
    </View>
  );
}
