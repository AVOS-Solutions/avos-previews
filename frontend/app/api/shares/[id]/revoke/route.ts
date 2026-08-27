import { NextResponse } from "next/server";
import { ApiError, apiFetch } from "@/lib/api";

export async function POST(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  try {
    await apiFetch(`/api/shares/${id}/revoke`, { method: "POST" });
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ message: error.message }, { status: error.status });
    }
    return NextResponse.json({ message: "Unerwarteter Fehler." }, { status: 500 });
  }
}
