import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BACKEND = process.env.INTERNAL_BACKEND_URL || "http://127.0.0.1:8001";

/**
 * Local edition: the only person reaching this route is whoever is running the
 * stack, so the backend body is surfaced as-is. There is no token gate here —
 * the hosted edition's owner/public split does not apply to a local run.
 */
export async function GET() {
  try {
    const r = await fetch(`${BACKEND}/api/v1/health`, { cache: "no-store" });
    const data = await r.json().catch(() => ({}));
    return NextResponse.json(data, { status: r.status });
  } catch {
    return NextResponse.json({ status: "degraded" }, { status: 503 });
  }
}
