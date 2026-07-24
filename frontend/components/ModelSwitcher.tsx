"use client";

import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";

import {
  DEFAULT_LLM_CONFIG,
  isLocalProvider,
  type LlmConfig,
  type LlmProvider,
  type LocalProvider,
  LOCAL_PROVIDERS,
  PROVIDER_DEFAULT_BASE_URL,
  readLlmConfig,
  writeLlmConfig,
} from "@/lib/llm-config";
import { cn } from "@/lib/utils";

/**
 * ADR-026 — model selector, rendered next to the LocaleSwitcher.
 *
 * Renders nothing at all unless the backend reports LOCAL_LLM_ENABLED, so the
 * public site is unchanged. Picking "run local" reveals the settings the user
 * has to fill in (provider, address, model), with the model list fetched from
 * their own Ollama / LM Studio server.
 */

type Props = {
  value: LlmConfig;
  onChange: (config: LlmConfig) => void;
  className?: string;
};

type TestState =
  | { status: "idle" }
  | { status: "testing" }
  | { status: "ok"; count: number }
  | { status: "error"; message: string };

export function ModelSwitcher({ value, onChange, className }: Props) {
  const t = useTranslations("modelSwitcher");
  const [enabled, setEnabled] = useState(false);
  const [models, setModels] = useState<string[]>([]);
  const [test, setTest] = useState<TestState>({ status: "idle" });

  // Feature probe + localStorage hydration. Both run client-side only so SSR
  // output stays identical to the MiniMax-only page.
  useEffect(() => {
    let active = true;
    fetch("/api/local/config")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!active || !data?.enabled) return;
        setEnabled(true);
        const stored = readLlmConfig();
        if (stored.provider !== DEFAULT_LLM_CONFIG.provider) onChange(stored);
      })
      .catch(() => {
        /* backend down — stay hidden */
      });
    return () => {
      active = false;
    };
    // Intentionally mount-only: re-running on `onChange` identity would refetch.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function update(next: LlmConfig) {
    writeLlmConfig(next);
    onChange(next);
  }

  function handleModeChange(mode: "minimax" | "local") {
    if (mode === "minimax") {
      update(DEFAULT_LLM_CONFIG);
      setModels([]);
      setTest({ status: "idle" });
      return;
    }
    const provider: LocalProvider = "ollama";
    update({ provider, baseUrl: PROVIDER_DEFAULT_BASE_URL[provider], model: "" });
  }

  function handleProviderChange(provider: LocalProvider) {
    // Address and model list belong to the previous provider — reset both.
    setModels([]);
    setTest({ status: "idle" });
    update({ provider, baseUrl: PROVIDER_DEFAULT_BASE_URL[provider], model: "" });
  }

  async function handleTest() {
    if (!isLocalProvider(value.provider)) return;
    setTest({ status: "testing" });
    setModels([]);
    try {
      const res = await fetch("/api/local/models", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ provider: value.provider, base_url: value.baseUrl }),
      });
      const json = await res.json().catch(() => ({}));
      if (!res.ok) {
        setTest({ status: "error", message: json?.message || t("genericFailure") });
        return;
      }
      const found: string[] = Array.isArray(json?.models) ? json.models : [];
      setModels(found);
      setTest({ status: "ok", count: found.length });
      // Auto-select the first model so a successful test leaves the form ready.
      if (found.length > 0 && !found.includes(value.model)) {
        update({ ...value, model: found[0] });
      }
    } catch {
      setTest({ status: "error", message: t("genericFailure") });
    }
  }

  if (!enabled) return null;

  const local = isLocalProvider(value.provider);
  const mode = local ? "local" : "minimax";

  return (
    <>
      <div className={className} aria-label={t("label")}>
        <label className="sr-only" htmlFor="model-switcher">
          {t("label")}
        </label>
        <select
          id="model-switcher"
          value={mode}
          onChange={(e) => handleModeChange(e.target.value as "minimax" | "local")}
          className="bg-bg-card border border-border-subtle rounded-md px-2.5 py-1 text-xs text-fg-muted hover:text-fg-primary focus:outline-none focus:border-border-emphasis transition cursor-pointer"
        >
          <option value="minimax">{t("minimax")}</option>
          <option value="local">{t("local")}</option>
        </select>
      </div>

      {local && (
        <motion.div
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
          className="w-full mt-4 text-left bg-bg-card border border-border-subtle rounded-card p-4 md:p-5 space-y-4"
        >
          <div>
            <p className="text-sm font-medium text-fg-primary">{t("panelTitle")}</p>
            <p className="text-xs text-fg-faint mt-1">{t("panelHelp")}</p>
          </div>

          <div className="grid gap-3 md:grid-cols-3">
            <Field label={t("providerLabel")}>
              <select
                value={value.provider}
                onChange={(e) => handleProviderChange(e.target.value as LocalProvider)}
                className={fieldClass}
              >
                {LOCAL_PROVIDERS.map((p) => (
                  <option key={p} value={p}>
                    {t(p)}
                  </option>
                ))}
              </select>
            </Field>

            <Field label={t("baseUrlLabel")}>
              <input
                type="text"
                inputMode="url"
                spellCheck={false}
                value={value.baseUrl}
                onChange={(e) => {
                  setTest({ status: "idle" });
                  setModels([]);
                  update({ ...value, baseUrl: e.target.value });
                }}
                placeholder={PROVIDER_DEFAULT_BASE_URL[value.provider as LocalProvider]}
                className={fieldClass}
              />
            </Field>

            <Field label={t("modelLabel")}>
              <select
                value={value.model}
                disabled={models.length === 0}
                onChange={(e) => update({ ...value, model: e.target.value })}
                className={cn(fieldClass, models.length === 0 && "opacity-60")}
              >
                {models.length === 0 ? (
                  <option value="">{t("selectModelPlaceholder")}</option>
                ) : (
                  models.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))
                )}
              </select>
            </Field>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={handleTest}
              disabled={test.status === "testing" || !value.baseUrl.trim()}
              className="rounded-lg border border-border-subtle px-3 py-1.5 text-xs font-medium text-fg-muted hover:text-fg-primary hover:border-border-emphasis transition disabled:opacity-50"
            >
              {test.status === "testing" ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="h-3 w-3 animate-spin" />
                  {t("testing")}
                </span>
              ) : (
                t("test")
              )}
            </button>
            {test.status === "ok" && (
              <span className="text-xs text-green-400">
                {t("connected", { count: test.count })}
              </span>
            )}
            {test.status === "error" && (
              <span className="text-xs text-red-400" role="alert">
                {t("failed", { message: test.message })}
              </span>
            )}
          </div>

          <p className="text-xs text-fg-faint">{t("warning")}</p>
        </motion.div>
      )}
    </>
  );
}

const fieldClass =
  "w-full bg-bg-cardHover border border-border-subtle rounded-lg px-3 py-2 text-sm text-fg-primary placeholder-fg-faint focus:outline-none focus:border-border-emphasis transition";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="block text-xs font-medium text-fg-muted mb-1">{label}</span>
      {children}
    </label>
  );
}

export type { LlmProvider };
