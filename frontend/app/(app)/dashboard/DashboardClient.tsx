"use client";

import { useMemo, useState } from "react";
import type { BusinessSummary, ShareLinkDto } from "@/lib/types";
import { Badge, Button, Card, Input, Label, PageHeader, Select, cx } from "@/components/ui";
import { ShareModal } from "./ShareModal";

const REGIONS = ["Wien", "Niederösterreich", "Oberösterreich", "Steiermark"];

export function DashboardClient({ initialBusinesses }: { initialBusinesses: BusinessSummary[] }) {
  const [businesses, setBusinesses] = useState(initialBusinesses);
  const [region, setRegion] = useState("");
  const [query, setQuery] = useState("");
  const [shareSlug, setShareSlug] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return businesses.filter(
      (b) =>
        (!region || b.region === region) &&
        (!q || `${b.name} ${b.category} ${b.location}`.toLowerCase().includes(q)),
    );
  }, [businesses, region, query]);

  const totals = useMemo(
    () => ({
      links: businesses.reduce((a, b) => a + b.activeLinks, 0),
      views: businesses.reduce((a, b) => a + b.totalViews, 0),
    }),
    [businesses],
  );

  async function refreshBusinesses() {
    const res = await fetch("/api/businesses-summary", { cache: "no-store" });
    if (res.ok) setBusinesses(await res.json());
  }

  const shareBusiness = businesses.find((b) => b.slug === shareSlug) ?? null;

  return (
    <>
      <PageHeader
        eyebrow="Website-Relaunch · Österreich"
        title="Design-Vorschauen"
        action={
          <div className="mono text-[0.8rem] text-slate">
            {filtered.length} von {businesses.length} Betrieben · {totals.links} aktive Links · {totals.views} Aufrufe
          </div>
        }
      />

      <div className="mb-6 flex flex-wrap items-center gap-2">
        <Input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Suchen: Name, Ort, Kategorie …"
          className="max-w-xs"
        />
        <FilterButton active={region === ""} onClick={() => setRegion("")}>
          Alle <span className="mono text-[0.72rem] opacity-70">{businesses.length}</span>
        </FilterButton>
        {REGIONS.map((r) => (
          <FilterButton key={r} active={region === r} onClick={() => setRegion(r)}>
            {r}{" "}
            <span className="mono text-[0.72rem] opacity-70">
              {businesses.filter((b) => b.region === r).length}
            </span>
          </FilterButton>
        ))}
      </div>

      {REGIONS.filter((r) => (!region || r === region) && filtered.some((b) => b.region === r)).map(
        (r) => (
          <section key={r} className="mb-10">
            <div className="mb-4 flex items-baseline gap-3">
              <h2 className="text-xl">{r}</h2>
              <span className="mono text-[0.78rem] text-slate">
                {filtered.filter((b) => b.region === r).length} Betriebe
              </span>
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filtered
                .filter((b) => b.region === r)
                .map((b) => (
                  <Card key={b.slug} className="flex flex-col gap-2 p-4 sm:p-5">
                    <div className="flex items-baseline justify-between gap-2">
                      <span className="mono text-[0.8rem] text-slate">
                        {String(b.num).padStart(2, "0")}
                      </span>
                      <span className="mono text-right text-[0.68rem] uppercase tracking-[0.08em] text-signal-dim">
                        {b.category}
                      </span>
                    </div>
                    <h3 className="text-[1.02rem] leading-snug">{b.name}</h3>
                    <p className="m-0 text-[0.82rem] text-slate">{b.location}</p>
                    <p className="m-0 text-[0.85rem] text-ink-soft">{b.description}</p>
                    <div className="mt-auto flex flex-wrap gap-2 pt-3">
                      <a
                        href={`/previews/${b.slug}/index.html`}
                        target="_blank"
                        rel="noopener"
                        className="inline-flex items-center justify-center rounded-md bg-ink px-2.5 py-1 text-[0.8rem] font-medium text-paper transition-colors hover:bg-signal-dim"
                      >
                        Vorschau
                      </a>
                      {b.oldWebsite ? (
                        <a
                          href={b.oldWebsite}
                          target="_blank"
                          rel="noopener"
                          className="inline-flex items-center justify-center rounded-md border border-line px-2.5 py-1 text-[0.8rem] font-medium text-ink transition-colors hover:bg-paper-dim"
                        >
                          Alte Website ↗
                        </a>
                      ) : null}
                      <button
                        onClick={() => setShareSlug(b.slug)}
                        className="inline-flex items-center justify-center gap-1.5 rounded-md border border-line px-2.5 py-1 text-[0.8rem] font-medium text-ink transition-colors hover:bg-paper-dim"
                      >
                        Teilen
                        {b.activeLinks > 0 ? <Badge kind="aktiv">{b.activeLinks}</Badge> : null}
                      </button>
                    </div>
                  </Card>
                ))}
            </div>
          </section>
        ),
      )}

      {shareBusiness ? (
        <ShareModal
          business={shareBusiness}
          onClose={() => setShareSlug(null)}
          onChanged={refreshBusinesses}
        />
      ) : null}
    </>
  );
}

function FilterButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={cx(
        "rounded-full border px-3.5 py-1 text-[0.82rem] transition-colors",
        active
          ? "border-ink bg-ink text-paper"
          : "border-line bg-transparent text-ink-soft hover:bg-paper-dim",
      )}
    >
      {children}
    </button>
  );
}
