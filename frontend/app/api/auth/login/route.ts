import { NextRequest, NextResponse } from "next/server";
import { API_URL, internalApiDispatcher } from "@/lib/config";
import { setSession } from "@/lib/session";
import type { AuthResponse } from "@/lib/types";

/** Dev-only password login relay. In production the SSO flow (/auth/sso/start) is the only
 *  way in — the API only exposes dev-login in its Development environment. */
export async function POST(request: NextRequest) {
  const body = await request.json();
  const response = await fetch(`${API_URL}/api/public/auth/dev-login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
    // @ts-expect-error -- dispatcher is an undici/Node fetch extension
    dispatcher: internalApiDispatcher,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "Anmeldung fehlgeschlagen." }));
    return NextResponse.json(error, { status: response.status });
  }

  const auth = (await response.json()) as AuthResponse;
  await setSession(auth);
  return NextResponse.json({ user: auth.user });
}
