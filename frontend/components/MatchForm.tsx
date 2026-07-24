"use client";

import { motion } from "framer-motion";
import { FileText, Loader2, Upload } from "lucide-react";
import { useTranslations } from "next-intl";
import { useRef, useState } from "react";

import {
  DEFAULT_LLM_CONFIG,
  isLlmConfigReady,
  isLocalProvider,
  type LlmConfig,
} from "@/lib/llm-config";
import { DEFAULT_LOCALE, TARGET_MARKET_OPTIONS, type Locale } from "@/lib/schemas";
import { cn } from "@/lib/utils";

type Props = {
  locale: Locale;
  /** ADR-026 — MiniMax by default; a local provider when the user opts in. */
  llmConfig?: LlmConfig;
  onResult: (data: unknown) => void;
  onError: (msg: string) => void;
};

const MAX_CV_BYTES = 5 * 1024 * 1024;
const MAX_JOB_BYTES = 100 * 1024;
const MIN_JOB_CHARS = 50;

type JobMode = "file" | "text";

const jobTextBytes = (s: string) => new TextEncoder().encode(s).length;

export function MatchForm({
  locale,
  llmConfig = DEFAULT_LLM_CONFIG,
  onResult,
  onError,
}: Props) {
  const t = useTranslations("form");
  const tErrors = useTranslations("form.errors");
  const tMarkets = useTranslations("targetMarket");

  const loadingMessages = t.raw("loadingMessages") as string[];
  const [cv, setCv] = useState<File | null>(null);
  const [job, setJob] = useState<File | null>(null);
  const [jobMode, setJobMode] = useState<JobMode>("file");
  const [jobText, setJobText] = useState("");
  const [targetMarket, setTargetMarket] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState(loadingMessages[0]);
  const [elapsed, setElapsed] = useState(0);

  const jobTextBytesNow = jobTextBytes(jobText);
  const jobReady =
    jobMode === "file"
      ? !!job
      : jobText.trim().length >= MIN_JOB_CHARS && jobTextBytesNow <= MAX_JOB_BYTES;
  // A local run needs its address and model filled in before it can be sent.
  const canSubmit =
    !!cv && jobReady && !submitting && isLlmConfigReady(llmConfig);

  function overLimitMsg(kb: number): string {
    return tErrors("txtTooLarge", { kb });
  }

  function handleCvChange(f: File | null) {
    if (f && f.size > MAX_CV_BYTES) {
      const sizeMb = (f.size / 1024 / 1024).toFixed(1);
      onError(tErrors("pdfTooLarge", { size: sizeMb }));
      setCv(null);
      return;
    }
    onError("");
    setCv(f);
  }

  function handleJobChange(f: File | null) {
    if (f && f.size > MAX_JOB_BYTES) {
      onError(overLimitMsg(Math.round(f.size / 1024)));
      setJob(null);
      return;
    }
    onError("");
    setJob(f);
  }

  function handleJobTextChange(value: string) {
    const bytes = jobTextBytes(value);
    if (bytes > MAX_JOB_BYTES) {
      onError(overLimitMsg(Math.round(bytes / 1024)));
    } else {
      onError("");
    }
    setJobText(value);
  }

  function handleJobModeChange(mode: JobMode) {
    if (mode === jobMode) return;
    onError("");
    setJobMode(mode);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!cv || !jobReady) return;
    setSubmitting(true);
    setElapsed(0);
    onError("");

    let i = 0;
    const tick = setInterval(() => {
      i = (i + 1) % loadingMessages.length;
      setLoadingMsg(loadingMessages[i]);
    }, 2200);
    const startedAt = Date.now();
    const elapsedTick = setInterval(() => {
      setElapsed((Date.now() - startedAt) / 1000);
    }, 200);

    try {
      const fd = new FormData();
      fd.append("cv", cv);
      if (jobMode === "file" && job) {
        fd.append("job", job);
      } else {
        fd.append("job_text", jobText.trim());
      }
      fd.append("target_market", targetMarket);
      fd.append("locale", locale);
      // ADR-026 — only sent when the user picked a local provider. The backend
      // ignores these unless LOCAL_LLM_ENABLED is on.
      if (isLocalProvider(llmConfig.provider)) {
        fd.append("llm_provider", llmConfig.provider);
        fd.append("llm_base_url", llmConfig.baseUrl.trim());
        fd.append("llm_model", llmConfig.model.trim());
      }

      const res = await fetch("/api/match", { method: "POST", body: fd });
      const json = await res.json().catch(() => ({}));
      if (!res.ok) {
        onError(json?.message || tErrors("generic"));
        return;
      }
      onResult(json);
    } catch {
      onError(tErrors("network"));
    } finally {
      clearInterval(tick);
      clearInterval(elapsedTick);
      setSubmitting(false);
    }
  }

  const progressPct = Math.min(95, (elapsed / 90) * 95);

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2">
        <FileDrop
          label={t("cvLabel")}
          hint={t("cvDropHint")}
          accept="application/pdf"
          file={cv}
          onChange={handleCvChange}
        />
        <JobInput
          mode={jobMode}
          onModeChange={handleJobModeChange}
          file={job}
          onFileChange={handleJobChange}
          text={jobText}
          onTextChange={handleJobTextChange}
          textBytes={jobTextBytesNow}
          label={t("jobLabel")}
          fileLabel={t("jobTabFile")}
          textLabel={t("jobTabText")}
          fileHint={t("jobDropHint")}
          placeholder={t("jobPlaceholder")}
          minCharsLabel={t("jobMinChars")}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-fg-muted mb-2">
          {t("marketLabel")}{" "}
          <span className="text-fg-faint font-normal">{t("marketOptional")}</span>
        </label>
        <select
          value={targetMarket}
          onChange={(e) => setTargetMarket(e.target.value)}
          className="w-full bg-bg-card border border-border-subtle rounded-lg px-4 py-3 text-fg-primary focus:outline-none focus:border-border-emphasis transition"
        >
          {TARGET_MARKET_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {tMarkets(opt.labelKey)}
            </option>
          ))}
        </select>
        <p className="text-xs text-fg-faint mt-1">{t("marketHelp")}</p>
      </div>

      <div className="space-y-3">
        <button type="submit" disabled={!canSubmit} className="btn-primary w-full md:w-auto">
          {submitting ? (
            <span className="flex items-center justify-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <motion.span
                key={loadingMsg}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                {loadingMsg}
              </motion.span>
            </span>
          ) : (
            t("submit")
          )}
        </button>
        {submitting && (
          <div className="space-y-2">
            <div className="h-2 w-full rounded-full bg-bg-cardHover overflow-hidden">
              <div
                className="h-full bg-gradient-purple transition-[width] duration-200 ease-out"
                style={{ width: `${progressPct}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-fg-faint font-mono">
              <span>{t("progress", { seconds: elapsed.toFixed(0) })}</span>
              <span>{t("progressHint")}</span>
            </div>
          </div>
        )}
      </div>
    </form>
  );
}

function FileDrop({
  label,
  hint,
  accept,
  file,
  onChange,
}: {
  label: string;
  hint: string;
  accept: string;
  file: File | null;
  onChange: (f: File | null) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  return (
    <div>
      <label className="block text-sm font-medium text-fg-muted mb-2">{label}</label>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          const f = e.dataTransfer.files?.[0];
          if (f) onChange(f);
        }}
        onClick={() => inputRef.current?.click()}
        className={cn(
          "cursor-pointer rounded-card border-2 border-dashed p-6 text-center transition",
          dragging
            ? "border-purple-500 bg-purple-500/10"
            : "border-border-subtle bg-bg-card hover:border-border-emphasis",
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          className="hidden"
          onChange={(e) => onChange(e.target.files?.[0] || null)}
        />
        {file ? (
          <div className="flex items-center justify-center gap-2 text-fg-primary">
            <FileText className="h-5 w-5 text-purple-400" />
            <span className="truncate max-w-[220px]">{file.name}</span>
            <span className="text-xs text-fg-faint">
              {(file.size / 1024).toFixed(0)} KB
            </span>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2 text-fg-muted">
            <Upload className="h-6 w-6" />
            <span className="text-sm">{hint}</span>
          </div>
        )}
      </div>
    </div>
  );
}

function JobInput({
  mode,
  onModeChange,
  file,
  onFileChange,
  text,
  onTextChange,
  textBytes,
  label,
  fileLabel,
  textLabel,
  fileHint,
  placeholder,
  minCharsLabel,
}: {
  mode: JobMode;
  onModeChange: (m: JobMode) => void;
  file: File | null;
  onFileChange: (f: File | null) => void;
  text: string;
  onTextChange: (v: string) => void;
  textBytes: number;
  label: string;
  fileLabel: string;
  textLabel: string;
  fileHint: string;
  placeholder: string;
  minCharsLabel: string;
}) {
  const kb = Math.round(textBytes / 1024);
  const overLimit = textBytes > MAX_JOB_BYTES;
  const nearLimit = textBytes > MAX_JOB_BYTES * 0.8 && !overLimit;

  return (
    <div>
      <div className="flex items-center justify-between gap-3 mb-2 flex-wrap">
        <label className="text-sm font-medium text-fg-muted">{label}</label>
        <div className="flex gap-1 rounded-lg bg-bg-card border border-border-subtle p-1">
          <button
            type="button"
            onClick={() => onModeChange("file")}
            className={cn(
              "px-3 py-1 text-xs font-medium rounded-md transition",
              mode === "file"
                ? "bg-purple-500/20 text-purple-300"
                : "text-fg-muted hover:text-fg-primary",
            )}
          >
            {fileLabel}
          </button>
          <button
            type="button"
            onClick={() => onModeChange("text")}
            className={cn(
              "px-3 py-1 text-xs font-medium rounded-md transition",
              mode === "text"
                ? "bg-purple-500/20 text-purple-300"
                : "text-fg-muted hover:text-fg-primary",
            )}
          >
            {textLabel}
          </button>
        </div>
      </div>
      {mode === "file" ? (
        <FileDropInner
          accept=".txt,text/plain"
          file={file}
          onChange={onFileChange}
          hint={fileHint}
        />
      ) : (
        <div>
          <textarea
            value={text}
            onChange={(e) => onTextChange(e.target.value)}
            placeholder={placeholder}
            rows={10}
            className={cn(
              "w-full bg-bg-card border rounded-lg px-4 py-3 text-sm text-fg-primary placeholder-fg-faint focus:outline-none transition resize-y",
              overLimit
                ? "border-red-500/60 focus:border-red-500"
                : "border-border-subtle focus:border-border-emphasis",
            )}
          />
          <div className="flex justify-between text-xs mt-1 font-mono">
            <span className="text-fg-faint">{minCharsLabel}</span>
            <span
              className={cn(
                overLimit
                  ? "text-red-400"
                  : nearLimit
                    ? "text-yellow-400"
                    : "text-fg-faint",
              )}
            >
              {kb}KB / 100KB
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

function FileDropInner({
  accept,
  file,
  onChange,
  hint,
}: {
  accept: string;
  file: File | null;
  onChange: (f: File | null) => void;
  hint: string;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        const f = e.dataTransfer.files?.[0];
        if (f) onChange(f);
      }}
      onClick={() => inputRef.current?.click()}
      className={cn(
        "cursor-pointer rounded-card border-2 border-dashed p-6 text-center transition",
        dragging
          ? "border-purple-500 bg-purple-500/10"
          : "border-border-subtle bg-bg-card hover:border-border-emphasis",
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => onChange(e.target.files?.[0] || null)}
      />
      {file ? (
        <div className="flex items-center justify-center gap-2 text-fg-primary">
          <FileText className="h-5 w-5 text-purple-400" />
          <span className="truncate max-w-[220px]">{file.name}</span>
          <span className="text-xs text-fg-faint">
            {(file.size / 1024).toFixed(0)} KB
          </span>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-2 text-fg-muted">
          <Upload className="h-6 w-6" />
          <span className="text-sm">{hint}</span>
        </div>
      )}
    </div>
  );
}
