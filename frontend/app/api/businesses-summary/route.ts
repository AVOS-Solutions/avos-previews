import { NextResponse } from "next/server";
import { ApiError, apiFetch } from "@/lib/api";
import type { BusinessSummary } from "@/lib/types";

export async function GET() {
  try {
    const businesses = await apiFetch<BusinessSummary[]>("/api/businesses");
    return NextResponse.json(businesses);
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json({ message: error.message }, { status: error.status });
    }
    return NextResponse.json({ message: "Unerwarteter Fehler." }, { status: 500 });
  }
}
