import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BACKEND = process.env.INTERNAL_BACKEND_URL || "http://127.0.0.1:8001";

/**
 * ADR-026 — backs the "test connection" button. The backend probes the local
 * Ollama / LM Studio server and returns the installed models. Base URL is
 * validated against a loopback allowlist server-side (SSRF).
 */
export async function POST(req: NextRequest) {
  const body = await req.text();

  const headers: Record<string, string> = { "content-type": "application/json" };
  const lang = req.headers.get("accept-language");
  if (lang) headers["accept-language"] = lang;

  try {
    const resp = await fetch(`${BACKEND}/api/v1/local/models`, {
      method: "POST",
      body,
      headers,
    });
    const text = await resp.text();
    return new NextResponse(text, {
      status: resp.status,
      headers: { "content-type": resp.headers.get("content-type") || "application/json" },
    });
  } catch (err) {
    console.error("proxy local models failed", err);
    return NextResponse.json(
      { error: "internal_error", message: "Backend indisponível. Tente novamente." },
      { status: 502 },
    );
  }
}
