"use client";

import { pdf } from "@react-pdf/renderer";
import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";
import { useFormatter, useTranslations } from "next-intl";
import { useState } from "react";

import PdfDocument from "@/components/PdfDocument";
import {
  CRITICALITY_LABEL,
  type DateFormatting,
  DIMENSION_LABEL,
  EFFORT_LABEL,
  type JobTitleMatch,
  type Locale,
  type MatchResult,
  RESUME_LENGTH_COLOR,
  RESUME_LENGTH_LABEL,
  type ResumeLength,
  type StandardHeadings,
  TIER_COLOR,
} from "@/lib/schemas";

type Props = {
  locale: Locale;
  result: MatchResult;
  onReset: () => void;
};

export function MatchReport({ locale, result, onReset }: Props) {
  const t = useTranslations("report");
  const tGap = useTranslations("report.gap");
  const tAction = useTranslations("report.actionItem");
  const format = useFormatter();
  const tierColor = TIER_COLOR[result.tier];
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  async function handlePdfExport() {
    setExporting(true);
    setExportError(null);
    try {
      const blob = await pdf(
        <PdfDocument result={result} locale={locale} />,
      ).toBlob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `job-match-${result.match_id.slice(0, 8)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setExportError(t("pdfError"));
    } finally {
      setExporting(false);
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-8"
    >
      <div className="bg-card rounded-card p-8 flex flex-col md:flex-row gap-8 items-center">
        <ScoreRadial score={result.score} color={tierColor} />
        <div className="flex-1 space-y-3">
          <p className="text-sm text-fg-muted">{t("jobAnalyzed")}</p>
          <h2 className="text-2xl font-bold text-fg-primary">
            {result.job_title}
            {result.company ? ` · ${result.company}` : ""}
          </h2>
          {result.candidate_name && (
            <p className="text-sm text-fg-muted">
              {t("candidateLabel", { name: result.candidate_name })}
            </p>
          )}
          <p className="text-lg font-semibold" style={{ color: tierColor }}>
            {result.tier_label}
          </p>
        </div>
      </div>

      <Section title={t("breakdownTitle")}>
        <div className="grid gap-4 md:grid-cols-2">
          {(Object.keys(result.dimensions) as Array<keyof typeof result.dimensions>).map((k) => (
            <DimensionBar
              key={k}
              label={DIMENSION_LABEL[k][locale]}
              score={result.dimensions[k]}
            />
          ))}
        </div>
      </Section>

      {result.job_title_match && <JobTitleMatchCard data={result.job_title_match} />}

      {result.resume_length && <ResumeLengthCard data={result.resume_length} locale={locale} />}

      {result.standard_headings && <StandardHeadingsCard data={result.standard_headings} />}

      {result.date_formatting && <DateFormattingCard data={result.date_formatting} />}

      <Section title={t("matchStrengths")}>
        <ul className="space-y-3">
          {result.strengths.map((s, i) => (
            <motion.li
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
              className="bg-card rounded-card p-4 border-l-4 border-tier-strong"
            >
              <p className="text-fg-primary">{s.text}</p>
              <p className="text-xs text-fg-muted mt-2 italic">{s.evidence}</p>
            </motion.li>
          ))}
        </ul>
      </Section>

      {result.gaps.length > 0 && (
        <Section title={t("gaps")}>
          <ul className="space-y-3">
            {result.gaps.map((g, i) => (
              <motion.li
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.06 }}
                className="bg-card rounded-card p-4"
              >
                <div className="flex items-center justify-between mb-2 gap-3">
                  <span className="text-sm font-semibold">
                    {CRITICALITY_LABEL[g.criticality][locale]}
                  </span>
                  <span className="text-xs text-fg-faint uppercase tracking-wide">
                    {g.category.replace("_", " ")}
                  </span>
                </div>
                <p className="text-fg-primary">{g.text}</p>
                <p className="text-sm text-fg-muted mt-2">
                  <strong className="text-fg-primary">{tGap("howToClose")}</strong>{" "}
                  {g.how_to_close}
                </p>
              </motion.li>
            ))}
          </ul>
        </Section>
      )}

      <Section title={t("actionPlan")}>
        <ol className="space-y-3">
          {result.action_plan.map((a, i) => (
            <motion.li
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              className="bg-card rounded-card p-4 flex gap-4"
            >
              <div className="text-2xl font-bold text-gradient">{i + 1}</div>
              <div className="flex-1">
                <p className="text-fg-primary">{a.description}</p>
                <div className="flex flex-wrap gap-3 mt-3 text-xs text-fg-muted">
                  <span>⏱ {a.estimated_duration}</span>
                  <span>{tAction("effort", { level: EFFORT_LABEL[a.effort][locale] })}</span>
                  <span className="text-tier-good">
                    {tAction("scoreImpact", { pts: a.estimated_score_impact })}
                  </span>
                </div>
              </div>
            </motion.li>
          ))}
        </ol>
      </Section>

      {exportError && (
        <div className="rounded-card border border-tier-low/40 bg-tier-low/5 p-3 text-sm text-tier-low">
          {exportError}
        </div>
      )}

      <div className="flex justify-between items-center pt-4 border-t border-border-subtle">
        <div className="flex gap-3">
          <button onClick={onReset} className="text-fg-muted hover:text-fg-primary transition">
            {t("newAnalysis")}
          </button>
          <button
            onClick={handlePdfExport}
            disabled={exporting}
            className="text-purple-400 hover:text-purple-300 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5"
          >
            {exporting ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                {t("pdfGenerating")}
              </>
            ) : (
              t("downloadPdf")
            )}
          </button>
        </div>
        <p className="text-xs text-fg-faint font-mono">
          {t("matchId", { id: result.match_id.slice(0, 8) })}
        </p>
      </div>
    </motion.div>
  );
}

function JobTitleMatchCard({ data }: { data: JobTitleMatch }) {
  const t = useTranslations("report.jobTitleCard");
  const color = data.aligned ? "#22c55e" : "#eab308";
  const label = data.aligned ? t("aligned") : t("misaligned");
  return (
    <Section title={t("title")}>
      <div className="bg-card rounded-card p-4 space-y-3">
        <div className="flex flex-wrap items-baseline gap-x-6 gap-y-2">
          <span className="text-sm font-semibold" style={{ color }}>
            {label}
          </span>
        </div>
        <div className="grid gap-3 md:grid-cols-2 text-sm">
          <div>
            <div className="text-xs uppercase tracking-wide text-fg-faint mb-1">
              {t("currentCv")}
            </div>
            <div className="text-fg-primary">{data.cv_title || t("notIdentified")}</div>
          </div>
          <div>
            <div className="text-xs uppercase tracking-wide text-fg-faint mb-1">
              {t("targetJob")}
            </div>
            <div className="text-fg-primary">{data.target_title || t("notIdentified")}</div>
          </div>
        </div>
        <p className="text-sm text-fg-muted">{data.note}</p>
      </div>
    </Section>
  );
}

function StandardHeadingsCard({ data }: { data: StandardHeadings }) {
  const t = useTranslations("report.standardHeadings");
  if (!data.found.length && !data.missing.length) return null;
  return (
    <Section title={t("title")}>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="bg-card rounded-card p-4">
          <div className="text-xs uppercase tracking-wide text-fg-faint mb-3">
            {t("present", { count: data.found.length })}
          </div>
          {data.found.length ? (
            <ul className="space-y-1 text-sm text-fg-primary">
              {data.found.map((h) => (
                <li key={h}>• {h}</li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-fg-muted">{t("noneFound")}</p>
          )}
        </div>
        <div className="bg-card rounded-card p-4">
          <div className="text-xs uppercase tracking-wide text-fg-faint mb-3">
            {t("missing", { count: data.missing.length })}
          </div>
          {data.missing.length ? (
            <ul className="space-y-1 text-sm text-fg-primary">
              {data.missing.map((h) => (
                <li key={h}>• {h}</li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-fg-muted">{t("noneMissing")}</p>
          )}
        </div>
      </div>
    </Section>
  );
}

function DateFormattingCard({ data }: { data: DateFormatting }) {
  const t = useTranslations("report.dateFormatting");
  const color = data.consistent ? "#22c55e" : "#eab308";
  const label = data.consistent ? t("consistent") : t("inconsistent");
  return (
    <Section title={t("title")}>
      <div className="bg-card rounded-card p-4 space-y-3">
        <span className="text-sm font-semibold" style={{ color }}>
          {label}
        </span>
        {data.issues.length > 0 && (
          <ul className="space-y-1 text-sm text-fg-muted">
            {data.issues.map((issue, i) => (
              <li key={i}>• {issue}</li>
            ))}
          </ul>
        )}
        {data.consistent && data.issues.length === 0 && (
          <p className="text-sm text-fg-muted">{t("okMessage")}</p>
        )}
      </div>
    </Section>
  );
}

function ResumeLengthCard({ data, locale }: { data: ResumeLength; locale: Locale }) {
  const t = useTranslations("report.resumeLength");
  const color = RESUME_LENGTH_COLOR[data.status];
  const label = RESUME_LENGTH_LABEL[data.status][locale];
  return (
    <Section title={t("title")}>
      <div className="bg-card rounded-card p-4 space-y-3">
        <div className="flex flex-wrap items-baseline gap-x-6 gap-y-2">
          <span className="text-sm font-semibold" style={{ color }}>
            {label}
          </span>
          <span className="font-mono text-fg-primary">
            {t("wordCount", { count: data.word_count })}
          </span>
          <span className="text-sm text-fg-muted">
            {t("pageCount", { count: data.estimated_pages })}
          </span>
        </div>
        <p className="text-sm text-fg-muted">{data.message}</p>
      </div>
    </Section>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-4">
      <h3 className="text-xl font-bold text-fg-primary">{title}</h3>
      {children}
    </section>
  );
}

function DimensionBar({ label, score }: { label: string; score: number }) {
  return (
    <div className="bg-card rounded-card p-4">
      <div className="flex justify-between mb-2">
        <span className="text-sm text-fg-muted">{label}</span>
        <span className="font-mono text-fg-primary">{score}</span>
      </div>
      <div className="h-2 rounded-full bg-bg-cardHover overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="h-full rounded-full bg-gradient-purple"
        />
      </div>
    </div>
  );
}

function ScoreRadial({ score, color }: { score: number; color: string }) {
  const size = 160;
  const stroke = 14;
  const radius = (size - stroke) / 2;
  const circ = 2 * Math.PI * radius;
  const offset = circ - (score / 100) * circ;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#1f2937"
          strokeWidth={stroke}
          fill="none"
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={stroke}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: "easeOut" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span
          className="text-5xl font-bold font-mono"
          style={{ color }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          {score}
        </motion.span>
        <span className="text-xs text-fg-faint">/ 100</span>
      </div>
    </div>
  );
}
