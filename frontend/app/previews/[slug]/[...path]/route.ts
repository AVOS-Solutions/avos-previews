import { NextResponse } from "next/server";
import { API_URL, internalApiDispatcher } from "@/lib/config";
import { getAccessToken } from "@/lib/session";

/** Streams a preview page/asset from the API for logged-in staff. The browser only ever
 *  talks to the Next.js server (ERP topology); the API validates the bearer token. */
export async function GET(
  _request: Request,
  { params }: { params: Promise<{ slug: string; path: string[] }> },
) {
  const { slug, path } = await params;
  const token = await getAccessToken();
  if (!token) {
    return NextResponse.redirect(new URL("/login", process.env.APP_PUBLIC_URL ?? "http://localhost:3000"));
  }

  const target = `${API_URL}/api/previews/${encodeURIComponent(slug)}/${path.map(encodeURIComponent).join("/")}`;
  const response = await fetch(target, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
    // @ts-expect-error -- dispatcher is an undici/Node fetch extension
    dispatcher: internalApiDispatcher,
  });

  if (!response.ok) {
    return new NextResponse("Nicht gefunden.", { status: response.status });
  }

  return new NextResponse(response.body, {
    status: 200,
    headers: {
      "Content-Type": response.headers.get("Content-Type") ?? "application/octet-stream",
      "Cache-Control": "no-store",
    },
  });
}
