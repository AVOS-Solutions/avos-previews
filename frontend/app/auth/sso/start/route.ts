import { NextRequest, NextResponse } from "next/server";
import { API_URL, internalApiDispatcher } from "@/lib/config";

/** Begins the avos-licensing SSO flow: asks the API for the authorize URL (the API holds
 *  client_id), stores the CSRF state in a short-lived cookie and redirects the browser to
 *  the licensing login. */
export async function GET(request: NextRequest) {
  const state = crypto.randomUUID().replaceAll("-", "");
  const publicUrl = process.env.APP_PUBLIC_URL ?? request.nextUrl.origin;
  const redirectUri = `${publicUrl.replace(/\/$/, "")}/auth/callback`;

  const response = await fetch(
    `${API_URL}/api/public/auth/sso/authorize-url?redirectUri=${encodeURIComponent(redirectUri)}&state=${state}`,
    {
      cache: "no-store",
      // @ts-expect-error -- dispatcher is an undici/Node fetch extension
      dispatcher: internalApiDispatcher,
    },
  );

  if (!response.ok) {
    const login = request.nextUrl.clone();
    login.pathname = "/login";
    login.search = "";
    login.searchParams.set("error", "AVOS Licensing ist nicht konfiguriert oder nicht erreichbar.");
    return NextResponse.redirect(login);
  }

  const { url } = (await response.json()) as { url: string };
  const redirect = NextResponse.redirect(url);
  redirect.cookies.set("avos_previews_sso_state", state, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 600,
  });
  const next = request.nextUrl.searchParams.get("next");
  if (next && next.startsWith("/")) {
    redirect.cookies.set("avos_previews_sso_next", next, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 600,
    });
  }
  return redirect;
}
