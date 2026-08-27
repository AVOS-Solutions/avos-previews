import { redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/session";
import { BrandMark, BrandWord } from "@/components/BrandMark";
import { LoginForm } from "./LoginForm";

const DEV_LOGIN = process.env.NODE_ENV !== "production" && !!process.env.DEV_LOGIN_ENABLED;

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string; next?: string }>;
}) {
  const user = await getCurrentUser();
  if (user) redirect("/dashboard");
  const { error, next } = await searchParams;

  return (
    <main className="flex flex-1 items-center justify-center px-4 py-10">
      <div className="w-full max-w-sm rounded-lg border border-line bg-white/60 p-6 shadow-sm">
        <div className="mb-5 flex items-center gap-2.5">
          <BrandMark />
          <BrandWord />
        </div>
        <h1 className="text-xl">Anmeldung</h1>
        <p className="mb-5 mt-1 text-sm text-slate">Zugang für das AVOS-Team über AVOS Licensing.</p>
        {error ? (
          <div className="mb-4 rounded-md border border-brass/30 bg-brass/10 px-3 py-2 text-sm text-brass">
            {error}
          </div>
        ) : null}
        <a
          href={`/auth/sso/start${next ? `?next=${encodeURIComponent(next)}` : ""}`}
          className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-ink px-4 py-2 text-sm font-medium text-paper transition-colors hover:bg-signal-dim"
        >
          Mit AVOS Licensing anmelden
        </a>
        {DEV_LOGIN ? <LoginForm /> : null}
      </div>
    </main>
  );
}
