"use client";

import { useMemo, useState } from "react";
import type { BusinessSummary, ShareLinkDto } from "@/lib/types";
import { Badge, Button, Card, Input, Label, PageHeader, Select, cx } from "@/components/ui";
import { ShareModal } from "./ShareModal";

const REGIONS = ["Wien", "Niederösterreich", "Oberösterreich", "Steiermark"];
const DATASETS = [
  { key: "relaunch", label: "Relaunch" },
  { key: "neubau", label: "Neubau" },
];

/** Known regions first, anything else after — so a preview never falls out of the list
 *  just because its region is new or missing. */
function orderRegions(names: string[]) {
  return [...names].sort((a, b) => {
    const ia = REGIONS.indexOf(a);
    const ib = REGIONS.indexOf(b);
    if (ia !== ib) return (ia < 0 ? REGIONS.length : ia) - (ib < 0 ? REGIONS.length : ib);
    return a.localeCompare(b, "de");
  });
}

export function DashboardClient({ initialBusinesses }: { initialBusinesses: BusinessSummary[] }) {
  const [businesses, setBusinesses] = useState(initialBusinesses);
  const [region, setRegion] = useState("");
  const [dataset, setDataset] = useState("");
  const [query, setQuery] = useState("");
  const [shareSlug, setShareSlug] = useState<string | null>(null);

  const inDataset = useMemo(
    () => businesses.filter((b) => !dataset || b.dataset === dataset),
    [businesses, dataset],
  );

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return inDataset.filter(
      (b) =>
        (!region || (b.region || "") === region) &&
        (!q || `${b.name} ${b.category} ${b.location}`.toLowerCase().includes(q)),
    );
  }, [inDataset, region, query]);

  const regionChips = useMemo(
    () => orderRegions(Array.from(new Set(inDataset.map((b) => b.region || "")))),
    [inDataset],
  );

  const groups = useMemo(
    () =>
      orderRegions(Array.from(new Set(filtered.map((b) => b.region || "")))).map((name) => ({
        name,
        items: filtered.filter((b) => (b.region || "") === name),
      })),
    [filtered],
  );

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
        eyebrow="Relaunch & Neubau · Österreich"
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
          Alle <span className="mono text-[0.72rem] opacity-70">{inDataset.length}</span>
        </FilterButton>
        {regionChips.map((r) => (
          <FilterButton key={r || "none"} active={region === r} onClick={() => setRegion(r)}>
            {r || "Ohne Region"}{" "}
            <span className="mono text-[0.72rem] opacity-70">
              {inDataset.filter((b) => (b.region || "") === r).length}
            </span>
          </FilterButton>
        ))}
      </div>

      <div className="mb-6 flex flex-wrap items-center gap-2">
        <span className="mono text-[0.72rem] uppercase tracking-[0.08em] text-slate">Datensatz</span>
        <FilterButton
          active={dataset === ""}
          onClick={() => {
            setDataset("");
            setRegion("");
          }}
        >
          Alle <span className="mono text-[0.72rem] opacity-70">{businesses.length}</span>
        </FilterButton>
        {DATASETS.map((d) => (
          <FilterButton
            key={d.key}
            active={dataset === d.key}
            onClick={() => {
              setDataset(d.key);
              setRegion("");
            }}
          >
            {d.label}{" "}
            <span className="mono text-[0.72rem] opacity-70">
              {businesses.filter((b) => b.dataset === d.key).length}
            </span>
          </FilterButton>
        ))}
      </div>

      {groups.map(
        ({ name: r, items }) => (
          <section key={r || "none"} className="mb-10">
            <div className="mb-4 flex items-baseline gap-3">
              <h2 className="text-xl">{r || "Ohne Region"}</h2>
              <span className="mono text-[0.78rem] text-slate">
                {items.length} Betriebe
              </span>
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {items
                .map((b) => (
                  <Card key={b.slug} className="flex flex-col gap-2 p-4 sm:p-5">
                    <div className="flex items-baseline justify-between gap-2">
                      <span className="mono text-[0.8rem] text-slate">
                        {String(b.num).padStart(2, "0")}
                        {b.dataset === "neubau" ? (
                          <span className="ml-2 rounded-full border border-line px-1.5 py-0.5 text-[0.62rem] uppercase tracking-[0.08em]">
                            Neubau
                          </span>
                        ) : null}
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
