import { NextRequest, NextResponse } from "next/server";
import { API_URL, internalApiDispatcher } from "@/lib/config";
import { setSession } from "@/lib/session";
import type { AuthResponse } from "@/lib/types";

/** SSO callback: validates the CSRF state cookie, exchanges the single-use code at the API
 *  (which holds the client secret and enforces the license gate), then stores the issued
 *  token pair in httpOnly cookies — the ERP session pattern. */
export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");
  const state = request.nextUrl.searchParams.get("state");
  const expectedState = request.cookies.get("avos_previews_sso_state")?.value;
  const next = request.cookies.get("avos_previews_sso_next")?.value;

  // Every redirect below must be built from APP_PUBLIC_URL, never request.nextUrl — this
  // server sits behind a Caddy TLS sidecar bound to 127.0.0.1:3000, so request.nextUrl.origin
  // reflects that internal address, not the public domain the browser is actually on.
  const publicUrl = process.env.APP_PUBLIC_URL ?? request.nextUrl.origin;

  const fail = (message: string) => {
    const login = new URL("/login", publicUrl);
    login.searchParams.set("error", message);
    const response = NextResponse.redirect(login);
    response.cookies.delete("avos_previews_sso_state");
    response.cookies.delete("avos_previews_sso_next");
    return response;
  };

  if (!code || !state || !expectedState || state !== expectedState) {
    return fail("SSO-Anmeldung fehlgeschlagen (ungültiger Zustand). Bitte erneut versuchen.");
  }

  const redirectUri = `${publicUrl.replace(/\/$/, "")}/auth/callback`;

  const response = await fetch(`${API_URL}/api/public/auth/sso/exchange`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, redirectUri }),
    cache: "no-store",
    // @ts-expect-error -- dispatcher is an undici/Node fetch extension
    dispatcher: internalApiDispatcher,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    return fail(body.message ?? "SSO-Anmeldung fehlgeschlagen. Bitte erneut versuchen.");
  }

  const auth = (await response.json()) as AuthResponse;
  await setSession(auth);

  const target = new URL(next && next.startsWith("/") ? next : "/dashboard", publicUrl);
  const redirect = NextResponse.redirect(target);
  redirect.cookies.delete("avos_previews_sso_state");
  redirect.cookies.delete("avos_previews_sso_next");
  return redirect;
}
