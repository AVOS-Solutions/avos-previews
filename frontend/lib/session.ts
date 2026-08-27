import { cookies } from "next/headers";
import type { AuthResponse, UserSummary } from "./types";

const ACCESS_COOKIE = "avos_access_token";
const REFRESH_COOKIE = "avos_refresh_token";
const USER_COOKIE = "avos_user";

const baseCookieOptions = {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "lax" as const,
  path: "/",
};

export async function setSession(auth: AuthResponse) {
  const store = await cookies();
  store.set(ACCESS_COOKIE, auth.accessToken, {
    ...baseCookieOptions,
    expires: new Date(auth.accessTokenExpiresAt),
  });
  store.set(REFRESH_COOKIE, auth.refreshToken, {
    ...baseCookieOptions,
    maxAge: 60 * 60 * 24 * 7,
  });
  store.set(USER_COOKIE, JSON.stringify(auth.user), {
    ...baseCookieOptions,
    maxAge: 60 * 60 * 24 * 7,
  });
}

export async function clearSession() {
  const store = await cookies();
  store.delete(ACCESS_COOKIE);
  store.delete(REFRESH_COOKIE);
  store.delete(USER_COOKIE);
}

export async function getAccessToken(): Promise<string | undefined> {
  const store = await cookies();
  return store.get(ACCESS_COOKIE)?.value;
}

export async function getRefreshToken(): Promise<string | undefined> {
  const store = await cookies();
  return store.get(REFRESH_COOKIE)?.value;
}

export async function getCurrentUser(): Promise<UserSummary | null> {
  const store = await cookies();
  const raw = store.get(USER_COOKIE)?.value;
  if (!raw) return null;
  try {
    return JSON.parse(raw) as UserSummary;
  } catch {
    return null;
  }
}
