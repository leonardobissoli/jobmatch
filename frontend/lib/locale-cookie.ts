"use client";

import { routing } from "@/i18n/routing";

const COOKIE_NAME = "NEXT_LOCALE";

export function setLocaleCookie(locale: string): void {
  if (typeof document === "undefined") return;
  if (!routing.locales.includes(locale as (typeof routing.locales)[number])) {
    return;
  }
  const oneYear = 60 * 60 * 24 * 365;
  document.cookie = `${COOKIE_NAME}=${locale}; Max-Age=${oneYear}; Path=/; SameSite=Lax`;
}

export function readLocaleCookie(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${COOKIE_NAME}=`));
  if (!match) return null;
  const value = match.split("=")[1];
  return value && routing.locales.includes(value as (typeof routing.locales)[number])
    ? value
    : null;
}
