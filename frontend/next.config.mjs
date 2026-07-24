import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./i18n/request.ts");

/** @type {import('next').NextConfig} */
// Content-Security-Policy is set dynamically in `middleware.ts` so each
// request gets a fresh nonce (M-1, M-3). The Reporting-Endpoints header is
// also set there alongside the CSP. Static headers below are stable per
// response and live here.
const SECURITY_HEADERS = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), interest-cohort=()" },
];

const nextConfig = {
  output: "standalone",
  outputFileTracingRoot: process.cwd(),
  reactStrictMode: true,
  poweredByHeader: false,
  experimental: {
    serverActions: {
      bodySizeLimit: "10mb",
    },
    // SEC-061 — Subresource Integrity on all Next-emitted script tags. Next
    // computes sha384 hashes at build time and injects `integrity=` +
    // `crossOrigin="anonymous"` into both framework and app chunks. App Router
    // only (we're on it). Defends against tampering of JS chunks in transit
    // or via a compromised CDN/proxy.
    sri: {
      algorithm: "sha384",
    },
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: SECURITY_HEADERS,
      },
    ];
  },
};

export default withNextIntl(nextConfig);
