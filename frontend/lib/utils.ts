import clsx, { type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Compact duration label. Output is locale-neutral (e.g. "5min", "1h30min")
 * so it composes with localized wrappers like "há {ago}" / "{ago} ago".
 */
export function formatDistanceShort(diffMs: number): string {
  const totalMin = Math.max(Math.floor(Math.abs(diffMs) / 60000), 1);
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  if (h && m) return `${h}h${m}min`;
  if (h) return `${h}h`;
  return `${m}min`;
}
