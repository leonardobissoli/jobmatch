import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BACKEND = process.env.INTERNAL_BACKEND_URL || "http://127.0.0.1:8001";

export async function POST(req: NextRequest) {
  const formData = await req.formData();

  const headers: Record<string, string> = {};

  try {
    const resp = await fetch(`${BACKEND}/api/v1/match`, {
      method: "POST",
      body: formData,
      headers,
    });
    const text = await resp.text();
    return new NextResponse(text, {
      status: resp.status,
      headers: { "content-type": resp.headers.get("content-type") || "application/json" },
    });
  } catch (err) {
    console.error("proxy match failed", err);
    return NextResponse.json(
      { error: "internal_error", message: "Backend indisponível. Tente novamente." },
      { status: 502 },
    );
  }
}
