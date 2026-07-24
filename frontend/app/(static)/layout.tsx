import { headers } from "next/headers";
import Script from "next/script";

import "../globals.css";

/**
 * Root layout for static PT-BR-only pages (/privacy, /terms — see ADR-021).
 *
 * Lives in a route group so the URL stays /privacy and /terms (route groups
 * are URL-invisible). The top-level `app/layout.tsx` is intentionally absent:
 * with no top-level layout, each route group owns its own <html>/<body> via
 * the "multiple root layouts" pattern documented for the Next.js App Router.
 *
 * The [locale] route group has its own root layout (app/[locale]/layout.tsx)
 * that wires NextIntlClientProvider, MotionConfig, and per-locale <html lang>.
 * Static pages don't need any of that.
 */
export default async function StaticLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // M-1/M-3 — nonce produced by middleware.ts on every request.
  // Privacy/terms don't ship client JS today, but Next 15 still emits
  // framework chunks for hydration; without the nonce, the strict-dynamic
  // CSP in middleware would block them.
  const nonce = (await headers()).get("x-nonce") ?? "";

  return (
    <html lang="pt-BR">
      <body>
        <Script
          id="webpack-nonce"
          strategy="beforeInteractive"
          nonce={nonce}
          dangerouslySetInnerHTML={{
            __html: `__webpack_nonce__ = ${JSON.stringify(nonce)};`,
          }}
        />
        {children}
      </body>
    </html>
  );
}