"use client";

import { z } from "zod";

/**
 * ADR-026 — "run local" mode.
 *
 * The user can point the match at an Ollama / LM Studio server running on the
 * same machine as the backend. The choice lives in localStorage (per browser),
 * and is sent along with the match FormData as `llm_provider` / `llm_base_url`
 * / `llm_model`.
 *
 * The backend ignores these fields entirely unless `LOCAL_LLM_ENABLED` is on,
 * and restricts the base URL to loopback hosts.
 */

export const LLM_PROVIDERS = ["minimax", "ollama", "lmstudio"] as const;
export type LlmProvider = (typeof LLM_PROVIDERS)[number];

export const LOCAL_PROVIDERS = ["ollama", "lmstudio"] as const;
export type LocalProvider = (typeof LOCAL_PROVIDERS)[number];

export const PROVIDER_DEFAULT_BASE_URL: Record<LocalProvider, string> = {
  ollama: "http://localhost:11434",
  lmstudio: "http://localhost:1234",
};

const LlmConfigSchema = z.object({
  provider: z.enum(LLM_PROVIDERS),
  baseUrl: z.string().max(200),
  model: z.string().max(120),
});

export type LlmConfig = z.infer<typeof LlmConfigSchema>;

export const DEFAULT_LLM_CONFIG: LlmConfig = {
  provider: "minimax",
  baseUrl: "",
  model: "",
};

const STORAGE_KEY = "jm.llm";

export function isLocalProvider(provider: LlmProvider): provider is LocalProvider {
  return provider !== "minimax";
}

/** A local run needs both a base URL and a model before it can be submitted. */
export function isLlmConfigReady(config: LlmConfig): boolean {
  if (!isLocalProvider(config.provider)) return true;
  return config.baseUrl.trim().length > 0 && config.model.trim().length > 0;
}

export function readLlmConfig(): LlmConfig {
  if (typeof window === "undefined") return DEFAULT_LLM_CONFIG;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_LLM_CONFIG;
    const parsed = LlmConfigSchema.safeParse(JSON.parse(raw));
    return parsed.success ? parsed.data : DEFAULT_LLM_CONFIG;
  } catch {
    // Private mode / disabled storage / corrupt value — fall back to MiniMax.
    return DEFAULT_LLM_CONFIG;
  }
}

export function writeLlmConfig(config: LlmConfig): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
  } catch {
    // Non-fatal: the config still applies for the current session.
  }
}
