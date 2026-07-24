import type { Metadata } from "next";
import { NextIntlClientProvider } from "next-intl";
import { getMessages, getTranslations, setRequestLocale } from "next-intl/server";
import Script from "next/script";
import { notFound } from "next/navigation";
import { MotionConfig } from "framer-motion";
import { headers } from "next/headers";
import { routing } from "@/i18n/routing";
import "../globals.css";

type Props = {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
};

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!(routing.locales as readonly string[]).includes(locale)) return {};
  const t = await getTranslations({ locale, namespace: "metadata" });
  const base = "http://localhost:3000";
  const path = locale === routing.defaultLocale ? "" : `/${locale}`;
  return {
    title: t("title"),
    description: t("description"),
    metadataBase: new URL(base),
    alternates: {
      canonical: `${base}${path}`,
      languages: {
        "pt-BR": `${base}`,
        en: `${base}/en`,
      },
    },
    openGraph: {
      title: t("title"),
      description: t("ogDescription"),
      type: "website",
    },
    twitter: {
      card: "summary",
      title: t("title"),
      description: t("ogDescription"),
    },
    robots: { index: false, follow: false },
  };
}

export default async function LocaleLayout({ children, params }: Props) {
  const { locale } = await params;
  if (!(routing.locales as readonly string[]).includes(locale)) {
    notFound();
  }
  setRequestLocale(locale);
  const messages = await getMessages();

  // M-1/M-3 — nonce produced by middleware.ts on every request.
  const nonce = (await headers()).get("x-nonce") ?? "";

  return (
    <html lang={locale}>
      <body>
        {/*
          __webpack_nonce__ must be set BEFORE any chunk loads, otherwise
          Next 15 App Router lazy chunks get blocked by the nonce-only CSP.
        */}
        <Script
          id="webpack-nonce"
          strategy="beforeInteractive"
          nonce={nonce}
          dangerouslySetInnerHTML={{
            __html: `__webpack_nonce__ = ${JSON.stringify(nonce)};`,
          }}
        />
        <NextIntlClientProvider messages={messages}>
          <MotionConfig nonce={nonce}>{children}</MotionConfig>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
