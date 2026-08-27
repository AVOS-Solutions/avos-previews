import { NextRequest, NextResponse } from "next/server";
import { API_URL, internalApiDispatcher } from "@/lib/config";
import { decodeJwtExpiryMs } from "@/lib/jwt";
import type { AuthResponse } from "@/lib/types";

const PUBLIC_PREFIXES = ["/login", "/auth"];
const REFRESH_SKEW_MS = 30_000;

const cookieOptions = {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax" as const,
  path: "/",
};

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isPublic = PUBLIC_PREFIXES.some((p) => pathname === p || pathname.startsWith(`${p}/`));
  if (isPublic) {
    return NextResponse.next();
  }

  const accessToken = request.cookies.get("avos_access_token")?.value;
  const refreshToken = request.cookies.get("avos_refresh_token")?.value;
  const expiryMs = accessToken ? decodeJwtExpiryMs(accessToken) : null;
  const isExpiringSoon = !expiryMs || expiryMs - Date.now() < REFRESH_SKEW_MS;

  if (accessToken && !isExpiringSoon) {
    return NextResponse.next();
  }

  if (!refreshToken) {
    return redirectToLogin(request);
  }

  const refreshed = await fetch(`${API_URL}/api/public/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refreshToken }),
    cache: "no-store",
    // @ts-expect-error -- dispatcher is an undici/Node fetch extension, not in the standard RequestInit typings
    dispatcher: internalApiDispatcher,
  });

  if (!refreshed.ok) {
    const response = redirectToLogin(request);
    response.cookies.delete("avos_access_token");
    response.cookies.delete("avos_refresh_token");
    response.cookies.delete("avos_user");
    return response;
  }

  const auth = (await refreshed.json()) as AuthResponse;
  const response = NextResponse.next();
  response.cookies.set("avos_access_token", auth.accessToken, {
    ...cookieOptions,
    expires: new Date(auth.accessTokenExpiresAt),
  });
  response.cookies.set("avos_refresh_token", auth.refreshToken, {
    ...cookieOptions,
    maxAge: 60 * 60 * 24 * 7,
  });
  response.cookies.set("avos_user", JSON.stringify(auth.user), {
    ...cookieOptions,
    maxAge: 60 * 60 * 24 * 7,
  });
  return response;
}

function redirectToLogin(request: NextRequest) {
  const url = request.nextUrl.clone();
  url.pathname = "/login";
  url.searchParams.set("next", request.nextUrl.pathname);
  return NextResponse.redirect(url);
}

export const config = {
  matcher: ["/((?!login|auth|api|_next/static|_next/image|favicon.ico).*)"],
};
