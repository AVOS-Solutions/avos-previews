/** Filtering previews by the day they were added.
 *
 *  Kept free of imports so the rules can be compiled and exercised on their own —
 *  the date arithmetic is the part worth testing, not the chips that call it.
 */

export const ADDED_PRESETS = [
  { key: "today", label: "Heute" },
  { key: "7d", label: "7 Tage" },
  { key: "30d", label: "30 Tage" },
];

export const ISO_DAY = /^\d{4}-\d{2}-\d{2}$/;

/** A calendar day as yyyy-MM-dd, read in the viewer's own timezone. The catalog stores
 *  plain days in the same shape, so days are compared as strings — parsing them into a
 *  Date would reintroduce the timezone drift this avoids. */
export function isoDay(d: Date) {
  return [
    d.getFullYear(),
    String(d.getMonth() + 1).padStart(2, "0"),
    String(d.getDate()).padStart(2, "0"),
  ].join("-");
}

/** The predicate for one "Hinzugefügt" selection: "" passes everything, a preset passes a
 *  trailing window ending today, an exact yyyy-MM-dd passes that single day. A preview
 *  without a date never passes a narrowed filter — its date is unknown, not recent.
 *  `today` is injectable so the windows can be checked against a fixed day. */
export function addedMatcher(added: string, today: Date = new Date()) {
  if (!added) return () => true;
  if (ISO_DAY.test(added)) return (iso?: string | null) => iso === added;
  const back = added === "today" ? 0 : added === "7d" ? 6 : 29;
  const from = new Date(today);
  from.setDate(from.getDate() - back);
  const fromIso = isoDay(from);
  return (iso?: string | null) => !!iso && iso >= fromIso;
}

/** 2026-09-23 -> 23.09.2026 */
export function formatDay(iso: string) {
  const [y, m, d] = iso.split("-");
  return `${d}.${m}.${y}`;
}
