import { apiFetch } from "@/lib/api";
import type { BusinessSummary } from "@/lib/types";
import { DashboardClient } from "./DashboardClient";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const businesses = await apiFetch<BusinessSummary[]>("/api/businesses");
  return <DashboardClient initialBusinesses={businesses} />;
}
