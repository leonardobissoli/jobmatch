"use client";

import { useLocale, useTranslations } from "next-intl";
import { usePathname, useRouter } from "next/navigation";
import { useTransition } from "react";

import { routing } from "@/i18n/routing";
import { setLocaleCookie } from "@/lib/locale-cookie";

type Props = {
  className?: string;
};

export function LocaleSwitcher({ className }: Props) {
  const t = useTranslations("localeSwitcher");
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();

  function switchTo(target: string) {
    if (target === locale) return;
    setLocaleCookie(target);
    const stripped = stripLocale(pathname, locale);
    const next = target === routing.defaultLocale ? stripped : `/${target}${stripped}`;
    startTransition(() => {
      router.replace(next);
      router.refresh();
    });
  }

  return (
    <div className={className} aria-label={t("label")}>
      <label className="sr-only" htmlFor="locale-switcher">
        {t("label")}
      </label>
      <select
        id="locale-switcher"
        value={locale}
        onChange={(e) => switchTo(e.target.value)}
        disabled={isPending}
        className="bg-bg-card border border-border-subtle rounded-md px-2.5 py-1 text-xs text-fg-muted hover:text-fg-primary focus:outline-none focus:border-border-emphasis transition cursor-pointer"
      >
        {routing.locales.map((loc) => (
          <option key={loc} value={loc}>
            {t(loc)}
          </option>
        ))}
      </select>
    </div>
  );
}

function stripLocale(pathname: string, currentLocale: string): string {
  const prefix = `/${currentLocale}`;
  if (pathname === prefix) return "/";
  if (pathname.startsWith(`${prefix}/`)) return pathname.slice(prefix.length);
  return pathname;
}
