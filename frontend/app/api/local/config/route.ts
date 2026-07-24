import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BACKEND = process.env.INTERNAL_BACKEND_URL || "http://127.0.0.1:8001";

/**
 * ADR-026 — feature probe for the model selector. The backend 404s when
 * LOCAL_LLM_ENABLED is off, which the frontend reads as "don't render it".
 */
export async function GET() {
  try {
    const resp = await fetch(`${BACKEND}/api/v1/local/config`, { cache: "no-store" });
    const text = await resp.text();
    return new NextResponse(text, {
      status: resp.status,
      headers: { "content-type": resp.headers.get("content-type") || "application/json" },
    });
  } catch {
    // Backend down — behave exactly like "disabled" so the UI stays quiet.
    return NextResponse.json({ enabled: false }, { status: 404 });
  }
}
