# avos-previews

Interne Plattform für Website-Relaunch-Vorschauen — im AVOS-Theme, hinter
AVOS-Licensing-Login, mit steuerbaren Share-Links.

## Inhalt

**120 individuell gestaltete Vorschau-Websites** für die Top-120 der qualifizierten
Relaunch-Leads (Recherche in `avos-erp/docs/leads/`). Jede Vorschau ist ein eigenständiger
Entwurf, kein Template:

- **7–9 Seiten + eigenes `style.css`** je Betrieb (1.080 Seiten insgesamt), jede mit
  eigener Farbwelt, eigenem Schriftpaar und eigener Layoutidee.
- **Der gesamte Inhalt der alten Website** wurde übernommen: Speisekarten mit Preisen,
  Zimmerkategorien, Öffnungs- und Küchenzeiten, Team, Firmengeschichte, Auszeichnungen,
  Referenzen, Leistungen. Grundlage ist ein vollständiger Crawl der bestehenden Seite
  inklusive der nur als PDF hinterlegten Karten und Preislisten.
- **Darüber hinaus** genau die digitalen Basics, die dem Betrieb fehlen: Online-Reservierung,
  Buchungsanfrage, Gutschein-Bestellung, Karriereseite mit Bewerbungsformular, Galerie,
  FAQ, Newsletter, Konfiguratoren. Formulare sind Demos ohne Backend.
- **Bildmaterial** stammt aus der bestehenden Website des jeweiligen Betriebs; wo keine
  Fotos vorlagen, tragen eigens gezeichnete SVG-Grafiken und Typografie die Seite —
  keine Stockfotos.
- Nichts erfunden: fehlende Preise oder Daten werden offen benannt statt ersetzt.

Jede Seite ist automatisch geprüft auf tote Links, fehlende Bilder, Platzhaltertext,
fehlendes JSON-LD/Viewport, WCAG-AA-Kontrast und horizontales Scrollen bei 390 px.

Aufteilung: 104 A-Leads / 16 B-Leads · Oberösterreich 39, Wien 28, Niederösterreich 27,
Steiermark 26 · Relaunch-Potenzial der abgedeckten Betriebe: € 1,15–2,14 Mio.

## Was die App kann

- **Dashboard** (Next.js, AVOS-Design-System): alle Betriebe nach Bundesland,
  Suche + Filter, Vorschau-Ansicht für eingeloggte Teammitglieder — samt Grade,
  Aufhänger und Richtpreis je Lead.
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
previews/NNN-<slug>/             die 120 aktuellen Vorschauen (7–9 Seiten + style.css + img/)
previews/206-energie-quelle/     Kundenprojekt Energie-Quelle als statischer Next.js-Export
previews/20[789]-dieherzl-*/     drei Gestaltungsvarianten fuer dieselbe Herzl-Recherche
generatoren/<betrieb>/           Renderer, wo mehrere Varianten aus einem Inhalt entstehen
previews/NN-<slug>/              84 ältere Vorschauen der ersten Recherche-Runde (je 6 Seiten,
                                 ohne Bildmaterial); nicht im Katalog gelistet, als Referenz behalten
businesses.json                  Katalog der gelisteten Vorschauen (120 Leads + Energie-Quelle)
index.html                       Alte statische Übersicht (durch das Dashboard abgelöst)
docker-compose[.prod].yml        Dev-Stack bzw. avos-edge-Produktionsstack mit TLS-Sidecars
Caddyfile                        Referenz-Routing für die gemeinsame Edge-Caddy
```

Deployment und Licensing-Registrierung: siehe `DEPLOY.md`.
Die Skripte, mit denen Inhalte gecrawlt, Vorschauen generiert und geprüft werden, liegen in
`avos-erp/docs/leads/playbook/scripts/` (`scrape_site.py`, `pdf_pass.py`, `qa_preview.py`,
`contrast_check.py`).

## Hinweise

- Jede Lead-Vorschau trägt die Kennzeichnung „Unverbindliche Gestaltungs-Vorschau" —
  es sind unabhängig erstellte Konzepte, keine offiziellen Websites der Betriebe;
  Impressum/Datenschutz darin sind Muster-Platzhalter. **Ausgenommen: Energie-Quelle**
  (siehe unten) — ein beauftragter Relaunch, der bewusst ohne diese Leiste ausgeliefert wird.
- Nichts wird indexiert: `X-Robots-Tag: noindex` auf allen API-Antworten,
  `robots.txt` Disallow im Frontend, noindex-Metas auf den Gate-Seiten.
- Keine externen Tracker, keine eingebetteten Fremdkarten; Schriften über Google Fonts
  mit Fallback-Stack.
- Share-Tokens (160 bit) stehen im Klartext in der DB, damit Links später erneut
  kopiert werden können; Passwörter sind ausschließlich gehasht.

## Sonderfall: Energie-Quelle (Kundenprojekt)

`previews/206-energie-quelle/` ist keine Recherche-Vorschau, sondern der fertige
Relaunch von **energie-quelle.at** (Bianca Dürbeck, Bad Mitterndorf) — hier eingebunden,
damit er über dieselben Share-Links zur Abnahme weitergegeben werden kann.

Herkunft: `AVOS-Solutions/energie-quelle.at`, Next.js 16 / React 19 / Tailwind v4,
9 Routen. Gebaut als statischer Export (`EXPORT=1 npm run build`, `output: "export"`,
`trailingSlash: true`, `images.unoptimized`).

Weil dieselbe Vorschau unter zwei verschiedenen Basis-Pfaden ausgeliefert wird
(`/api/previews/<slug>/…` für das Team, `/s/<token>/…` für Share-Links, Token variabel),
kann kein fester `BASE_PATH` gesetzt werden. Der Export wird daher nachbearbeitet:
alle wurzel-absoluten URLs (`/_next/…`, `/images/…`, `href`, `srcset`, `url(…)` in CSS)
werden pro Dateitiefe in relative Pfade umgeschrieben (`./…` auf der Startseite,
`../…` eine Ebene tiefer). Die Navigation läuft dadurch als vollständiger Seitenwechsel
statt über den Client-Router — für eine Vorschau unerheblich, dafür basis-pfad-unabhängig.

Damit die Routen-Ordner (`massage/`, `kontakt/` …) ausgeliefert werden, liefert
`ServePreviewFile` für Verzeichnispfade deren `index.html` aus.

Geprüft unter beiden Basis-Pfaden: alle 9 Routen laden, 94 Bilder vollständig,
CSS aktiv, keine 404er, WCAG-AA-Kontrast sauber, kein horizontales Scrollen bei 390 px.
