# avos-previews

Website-Relaunch-Vorschauen für 84 österreichische Betriebe mit veralteten Websites,
erstellt als Sales-Material auf Basis der Recherche `Website-Relaunch Leads Österreich`
(Stand 27.08.2026).

## Inhalt

- **`index.html`** — durchsuchbare Übersicht aller 84 Betriebe, gruppiert nach Bundesland
  (Wien, Niederösterreich, Oberösterreich, Steiermark), mit Link zur jeweiligen
  Vorschau-Seite und zur aktuellen (alten) Website des Betriebs.
- **`previews/<nr>-<slug>.html`** — je eine eigenständige, in sich geschlossene
  HTML-Datei pro Betrieb: eine bespoke Redesign-Vorschau, die zeigt, wie eine moderne
  Website für genau diesen Betrieb aussehen könnte. Kein Bau-Kasten-Template — jede
  Seite hat ein eigenes Layout, Typografie-Pairing und eine eigene Farbwelt, passend zur
  Branche.

Jede Vorschau-Seite trägt eine klar sichtbare Kennzeichnung ("Unverbindliche
Gestaltungs-Vorschau … keine offizielle Website von …"), da es sich um unabhängig
erstellte Konzepte zu Demonstrationszwecken handelt, nicht um die echten Websites der
Betriebe.

## Technische Eckpunkte

- Reines, statisches HTML/CSS/Vanilla-JS — kein Build-Step, direkt über GitHub Pages
  oder jeden anderen Static Host deploybar.
- Jede Seite ist self-contained: einzige externe Ressource sind Google Fonts (und, wo
  passend, ein Google-Maps-Link/-Embed ohne API-Key). Keine Bild-CDNs, kein Analytics,
  keine JS-Frameworks — Visuals entstehen ausschließlich aus Typografie, Farbe,
  Verläufen und Inline-SVG.
- Mobile-first und responsiv: fluide Typografie via `clamp()`, kollabierende
  Grids/Hero-Layouts unterhalb von ca. 640–900px, mobile Navigation, Touch-Targets
  ≥ 44px.

## Quelle

Kontaktdaten und Betriebsbeschreibungen stammen aus öffentlich zugänglichen Impressen
der Betriebe (siehe Ursprungsdokument). Interne Recherche-Notizen (Preiskalkulation,
technische Mängel der Altwebsite, Bewertungs-Monitoring) sind bewusst nicht Teil der
Vorschau-Seiten.
