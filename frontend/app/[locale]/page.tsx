"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useLocale, useTranslations } from "next-intl";
import { useState } from "react";

import { LocaleSwitcher } from "@/components/LocaleSwitcher";
import { MatchForm } from "@/components/MatchForm";
import { MatchReport } from "@/components/MatchReport";
import { ModelSwitcher } from "@/components/ModelSwitcher";
import { BRAND } from "@/lib/brand";
import { DEFAULT_LLM_CONFIG, type LlmConfig } from "@/lib/llm-config";
import { type Locale, type MatchResult, MatchResultSchema } from "@/lib/schemas";

export default function Page() {
  const locale = useLocale() as Locale;
  const t = useTranslations("landing");
  const tCommon = useTranslations("common");
  const [result, setResult] = useState<MatchResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  // ADR-026 — MiniMax unless the user opts into a local model. ModelSwitcher
  // hydrates this from localStorage after its feature probe succeeds.
  const [llmConfig, setLlmConfig] = useState<LlmConfig>(DEFAULT_LLM_CONFIG);

  return (
    <main className="min-h-screen px-4 py-12 md:py-20">
      <div className="mx-auto max-w-[1100px]">
        <motion.header
          initial={false}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-12 md:mb-16 text-center"
        >
          {/* flex-wrap so the local-model panel (w-full) drops to its own row */}
          <div className="flex flex-wrap items-center justify-center gap-4 mb-3">
            <p className="text-sm uppercase tracking-widest text-fg-muted">
              {BRAND.taglineSuffix}
            </p>
            <LocaleSwitcher />
            <ModelSwitcher value={llmConfig} onChange={setLlmConfig} />
          </div>
          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold mb-4 md:whitespace-nowrap">
            {t("heroTitle")}{" "}
            <span className="text-gradient">{t("heroTitleHighlight")}</span>
            {t("heroTitleSuffix")}
          </h1>
          <p className="text-fg-muted max-w-2xl mx-auto">{t("heroSubtitle")}</p>
        </motion.header>

        {!result ? (
          <motion.div
            initial={false}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="bg-card rounded-card p-6 md:p-10"
          >
            <MatchForm
              locale={locale}
              llmConfig={llmConfig}
              onResult={(data) => {
                const parsed = MatchResultSchema.safeParse(data);
                if (parsed.success) {
                  setResult(parsed.data);
                  setError(null);
                  window.scrollTo({ top: 0, behavior: "smooth" });
                } else {
                  console.error("invalid result", parsed.error);
                  setError(t("serverError"));
                }
              }}
              onError={setError}
            />
            {error && (
              <p className="mt-4 text-sm text-tier-low" role="alert">
                {error}
              </p>
            )}
          </motion.div>
        ) : (
          <MatchReport
            locale={locale}
            result={result}
            onReset={() => {
              setResult(null);
              setError(null);
            }}
          />
        )}

        <footer className="mt-16 text-center space-y-3">
          <p className="text-xs text-fg-faint space-x-3">
            <span>{BRAND.ownerLine}</span>
            <span aria-hidden="true">·</span>
            <Link href="/privacy" className="hover:text-fg-muted underline">
              {t("footerPrivacy")}
            </Link>
            <span aria-hidden="true">·</span>
            <Link href="/terms" className="hover:text-fg-muted underline">
              {t("footerTerms")}
            </Link>
          </p>
        </footer>
      </div>
    </main>
  );
}
