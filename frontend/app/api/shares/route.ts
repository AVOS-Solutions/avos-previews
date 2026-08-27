import { NextRequest, NextResponse } from "next/server";
import { ApiError, apiFetch } from "@/lib/api";
import type { ShareLinkDto } from "@/lib/types";

export async function GET(request: NextRequest) {
  const slug = request.nextUrl.searchParams.get("slug");
  try {
    const shares = await apiFetch<ShareLinkDto[]>(
      `/api/shares${slug ? `?slug=${encodeURIComponent(slug)}` : ""}`,
    );
    return NextResponse.json(shares);
  } catch (error) {
    return toErrorResponse(error);
  }
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  try {
    const share = await apiFetch<ShareLinkDto>("/api/shares", {
      method: "POST",
      body: JSON.stringify(body),
    });
    return NextResponse.json(share);
  } catch (error) {
    return toErrorResponse(error);
  }
}

function toErrorResponse(error: unknown) {
  if (error instanceof ApiError) {
    return NextResponse.json({ message: error.message }, { status: error.status });
  }
  return NextResponse.json({ message: "Unerwarteter Fehler." }, { status: 500 });
}
