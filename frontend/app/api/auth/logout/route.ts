import { NextResponse } from "next/server";
import { API_URL, internalApiDispatcher } from "@/lib/config";
import { clearSession, getRefreshToken } from "@/lib/session";

export async function POST() {
  const refreshToken = await getRefreshToken();
  if (refreshToken) {
    // Best-effort server-side revocation; the cookies are cleared regardless.
    await fetch(`${API_URL}/api/public/auth/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refreshToken }),
      cache: "no-store",
      // @ts-expect-error -- dispatcher is an undici/Node fetch extension
      dispatcher: internalApiDispatcher,
    }).catch(() => {});
  }
  await clearSession();
  return NextResponse.json({ ok: true });
}
