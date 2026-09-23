export type UserSummary = {
  id: string;
  email: string;
  fullName: string;
};

export type AuthResponse = {
  accessToken: string;
  accessTokenExpiresAt: string;
  refreshToken: string;
  user: UserSummary;
};

export type BusinessSummary = {
  num: number;
  slug: string;
  name: string;
  category: string;
  region: string;
  location: string;
  description: string;
  oldWebsite: string | null;
  /** "relaunch" for leads with an outdated site, "neubau" for leads with none yet. */
  dataset: string;
  /** ISO date (yyyy-MM-dd) the preview folder was first committed, or null for a preview
   *  the catalog does not list. Seeded by scripts/set-added-dates.py. */
  addedOn?: string | null;
  activeLinks: number;
  totalViews: number;
  grade?: string | null;
  score?: number | null;
  pitchHook?: string | null;
  priceLow?: number | null;
  priceHigh?: number | null;
  phone?: string | null;
  email?: string | null;
  contactPerson?: string | null;
};

export type ShareLinkDto = {
  id: string;
  slug: string;
  label: string | null;
  url: string;
  hasPassword: boolean;
  maxViews: number | null;
  viewCount: number;
  expiresAt: string | null;
  createdAt: string;
  createdBy: string;
  revokedAt: string | null;
  lastViewedAt: string | null;
  status: "aktiv" | "abgelaufen" | "aufgebraucht" | "widerrufen";
};
