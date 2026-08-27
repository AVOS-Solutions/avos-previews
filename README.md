# avos-previews

Interne Plattform für die Website-Relaunch-Vorschauen aus der Recherche
„Website-Relaunch Leads Österreich" (84 Betriebe, Stand 27.08.2026) — im
AVOS-Theme, hinter AVOS-Licensing-Login, mit steuerbaren Share-Links.

## Was die App kann

- **Dashboard** (Next.js, AVOS-Design-System): alle 84 Betriebe nach Bundesland,
  Suche + Filter, Vorschau-Ansicht für eingeloggte Teammitglieder.
- **Login über avos-licensing** (SSO-Flow `/api/sso/authorize` → Code-Exchange):
  Licensing-Admins immer, andere Konten nur mit aktiver AVOS-Previews-Lizenz.
- **Share-Links** pro Betrieb (`https://<domain>/s/<token>`), einzeln steuerbar:
  - optionales **Passwort** (PBKDF2-gehasht, Abfrage-Seite im AVOS-Theme)
  - optionales **View-Limit** (Zählung pro Besuch, 30-Minuten-Debounce gegen Reloads)
  - optionaler **Ablauf** (7/14/30/90 Tage oder Datum)
  - Widerrufen/Löschen jederzeit, Statistik (Aufrufe, zuletzt geöffnet)

## Struktur

```
backend/src/Avos.Previews.Api/   .NET 10 Minimal API (JWT + Refresh-Rotation wie avos-erp,
                                 EF Core: Postgres, SQLite-Fallback für lokale Entwicklung)
frontend/                        Next.js 16 App Router (Tailwind v4, ERP-Theme-Tokens,
                                 httpOnly-Cookie-Sessions, proxy.ts-Refresh wie avos-erp)
previews/<nr>-<slug>/            84 statische Vorschau-Websites (je 6 Seiten, bespoke Design)
businesses.json                  Betriebskatalog (aus der Lead-Recherche generiert)
index.html                       Alte statische Übersicht (durch das Dashboard abgelöst,
                                 als Referenz behalten)
docker-compose[.prod].yml        Dev-Stack bzw. avos-edge-Produktionsstack mit TLS-Sidecars
Caddyfile                        Referenz-Routing für die gemeinsame Edge-Caddy
```

Deployment und Licensing-Registrierung: siehe `DEPLOY.md`.

## Hinweise

- Jede Vorschau-Seite trägt weiterhin die Kennzeichnung „Unverbindliche
  Gestaltungs-Vorschau" — es sind unabhängig erstellte Konzepte, keine offiziellen
  Websites der Betriebe; Impressum/Datenschutz darin sind Muster-Platzhalter.
- Nichts wird indexiert: `X-Robots-Tag: noindex` auf allen API-Antworten,
  `robots.txt` Disallow im Frontend, noindex-Metas auf den Gate-Seiten.
- Share-Tokens (160 bit) stehen im Klartext in der DB, damit Links später erneut
  kopiert werden können; Passwörter sind ausschließlich gehasht.
