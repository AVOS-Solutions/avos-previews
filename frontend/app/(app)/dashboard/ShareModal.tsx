"use client";

import { useCallback, useEffect, useState } from "react";
import type { BusinessSummary, ShareLinkDto } from "@/lib/types";
import { Badge, Button, Input, Label, Select } from "@/components/ui";

function fmtDate(iso: string | null) {
  if (!iso) return "–";
  return new Date(iso).toLocaleString("de-AT", { dateStyle: "medium", timeStyle: "short" });
}

export function ShareModal({
  business,
  onClose,
  onChanged,
}: {
  business: BusinessSummary;
  onClose: () => void;
  onChanged: () => void;
}) {
  const [shares, setShares] = useState<ShareLinkDto[] | null>(null);
  const [label, setLabel] = useState("");
  const [password, setPassword] = useState("");
  const [maxViews, setMaxViews] = useState("");
  const [expiry, setExpiry] = useState("14");
  const [expiryCustom, setExpiryCustom] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [created, setCreated] = useState<ShareLinkDto | null>(null);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    const res = await fetch(`/api/shares?slug=${encodeURIComponent(business.slug)}`, {
      cache: "no-store",
    });
    if (res.ok) setShares(await res.json());
  }, [business.slug]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function create() {
    setError(null);
    setBusy(true);
    const body: Record<string, unknown> = {
      slug: business.slug,
      label: label || null,
      password: password || null,
      maxViews: maxViews ? parseInt(maxViews, 10) : null,
    };
    if (expiry === "custom") {
      if (!expiryCustom) {
        setError("Bitte ein Ablaufdatum wählen.");
        setBusy(false);
        return;
      }
      body.expiresAt = new Date(expiryCustom).toISOString();
    } else if (expiry) {
      body.expiresInDays = parseInt(expiry, 10);
    }
    const res = await fetch("/api/shares", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    setBusy(false);
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      setError(data.message ?? "Fehler beim Erstellen.");
      return;
    }
    const share = (await res.json()) as ShareLinkDto;
    setCreated(share);
    copy(share.url);
    await refresh();
    onChanged();
  }

  async function revoke(id: string) {
    if (!confirm("Diesen Link widerrufen? Er ist danach sofort ungültig.")) return;
    await fetch(`/api/shares/${id}/revoke`, { method: "POST" });
    await refresh();
    onChanged();
  }

  async function remove(id: string) {
    if (!confirm("Diesen Link endgültig löschen (inkl. Statistik)?")) return;
    await fetch(`/api/shares/${id}`, { method: "DELETE" });
    await refresh();
    onChanged();
  }

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-ink/45 p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-lg border border-line bg-paper p-6">
        <div className="mb-4 flex items-baseline justify-between gap-3">
          <h2 className="text-lg">Share-Links · {business.name}</h2>
          <Button variant="secondary" className="px-3 py-1.5 text-[0.8rem]" onClick={onClose}>
            Schließen
          </Button>
        </div>

        <div className="mb-5 rounded-lg border border-line bg-white/60 p-4">
          <div className="eyebrow mb-3">Neuen Share-Link erstellen</div>
          <div className="mb-3">
            <Label htmlFor="share-label">Bezeichnung (intern, optional)</Label>
            <Input
              id="share-label"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              placeholder="z. B. E-Mail an Hrn. Huber, 08/2026"
            />
          </div>
          <div className="mb-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div>
              <Label htmlFor="share-password">Passwort (optional)</Label>
              <Input
                id="share-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="leer = ohne Passwort"
              />
            </div>
            <div>
              <Label htmlFor="share-maxviews">View-Limit (optional)</Label>
              <Input
                id="share-maxviews"
                type="number"
                min={1}
                value={maxViews}
                onChange={(e) => setMaxViews(e.target.value)}
                placeholder="leer = unbegrenzt"
              />
            </div>
          </div>
          <div className="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div>
              <Label htmlFor="share-expiry">Gültigkeit</Label>
              <Select id="share-expiry" value={expiry} onChange={(e) => setExpiry(e.target.value)}>
                <option value="">Unbegrenzt</option>
                <option value="7">7 Tage</option>
                <option value="14">14 Tage</option>
                <option value="30">30 Tage</option>
                <option value="90">90 Tage</option>
                <option value="custom">Datum wählen …</option>
              </Select>
            </div>
            {expiry === "custom" ? (
              <div>
                <Label htmlFor="share-expiry-custom">Ablaufdatum</Label>
                <Input
                  id="share-expiry-custom"
                  type="datetime-local"
                  value={expiryCustom}
                  onChange={(e) => setExpiryCustom(e.target.value)}
                />
              </div>
            ) : null}
          </div>
          {error ? (
            <div className="mb-3 rounded-md border border-brass/30 bg-brass/10 px-3 py-2 text-sm text-brass">
              {error}
            </div>
          ) : null}
          <Button onClick={create} disabled={busy}>
            {busy ? "Erstellen …" : "Link erstellen"}
          </Button>
          {created ? (
            <div className="mt-4">
              <div className="eyebrow mb-1.5">Neuer Link (in Zwischenablage kopiert)</div>
              <div className="flex items-center gap-2">
                <div className="mono flex-1 break-all rounded-md border border-line bg-white px-3 py-2 text-[0.78rem]">
                  {created.url}
                </div>
                <CopyButton text={created.url} />
              </div>
            </div>
          ) : null}
        </div>

        <div className="eyebrow mb-2">Bestehende Links</div>
        {shares === null ? (
          <p className="text-sm text-slate">Laden …</p>
        ) : shares.length === 0 ? (
          <p className="text-sm text-slate">Noch keine Links für diesen Betrieb.</p>
        ) : (
          <div className="flex flex-col gap-3">
            {shares.map((s) => (
              <div key={s.id} className="rounded-lg border border-line bg-white/60 p-3">
                <div className="mb-1.5 flex flex-wrap items-center gap-2">
                  <Badge kind={s.status}>{s.status}</Badge>
                  {s.hasPassword ? <Badge kind="passwort">Passwort</Badge> : <Badge kind="offen">offen</Badge>}
                  <span className="mono text-[0.75rem] text-slate">
                    {s.viewCount}
                    {s.maxViews ? ` / ${s.maxViews}` : ""} Aufrufe
                  </span>
                  <span className="text-[0.78rem] text-slate">
                    · Ablauf: {s.expiresAt ? fmtDate(s.expiresAt) : "unbegrenzt"}
                  </span>
                </div>
                <div className="mono break-all text-[0.72rem] text-ink-soft">{s.url}</div>
                <div className="mt-1 text-[0.75rem] text-slate">
                  {s.label ? `${s.label} · ` : ""}erstellt {fmtDate(s.createdAt)} von {s.createdBy}
                  {s.lastViewedAt ? ` · zuletzt geöffnet ${fmtDate(s.lastViewedAt)}` : ""}
                </div>
                <div className="mt-2 flex gap-2">
                  <CopyButton text={s.url} />
                  {s.status === "aktiv" ? (
                    <Button
                      variant="danger"
                      className="px-2.5 py-1 text-[0.78rem]"
                      onClick={() => revoke(s.id)}
                    >
                      Widerrufen
                    </Button>
                  ) : (
                    <Button
                      variant="secondary"
                      className="px-2.5 py-1 text-[0.78rem]"
                      onClick={() => remove(s.id)}
                    >
                      Löschen
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <Button
      variant="secondary"
      className="px-2.5 py-1 text-[0.78rem]"
      onClick={async () => {
        await copy(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
      }}
    >
      {copied ? "Kopiert ✓" : "Kopieren"}
    </Button>
  );
}

async function copy(text: string) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const ta = document.createElement("textarea");
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    ta.remove();
  }
}
