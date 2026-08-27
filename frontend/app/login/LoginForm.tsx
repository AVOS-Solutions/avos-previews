"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button, Input, Label } from "@/components/ui";

export function LoginForm() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    setBusy(false);
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      setError(body.message ?? "Anmeldung fehlgeschlagen.");
      return;
    }
    router.push("/dashboard");
    router.refresh();
  }

  return (
    <form onSubmit={submit} className="mt-5 border-t border-line pt-5">
      <Label htmlFor="dev-password">Dev-Login (nur Entwicklung)</Label>
      <div className="mb-3">
        <Input
          id="dev-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Dev-Passwort"
          required
        />
      </div>
      {error ? (
        <div className="mb-3 rounded-md border border-brass/30 bg-brass/10 px-3 py-2 text-sm text-brass">
          {error}
        </div>
      ) : null}
      <Button type="submit" variant="secondary" className="w-full" disabled={busy}>
        {busy ? "Anmelden …" : "Anmelden"}
      </Button>
    </form>
  );
}
