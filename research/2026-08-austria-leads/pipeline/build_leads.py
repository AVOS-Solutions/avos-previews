#!/usr/bin/env python3
"""Merge herold candidates+details+audits and existing 84 into leads.json,
with value estimation and badges. Usage: build_leads.py <mode>
mode=jobs  -> emit jobs_new.json (sites to audit)
mode=final -> build leads_full.json
"""
import json, os, re, sys, unicodedata

SC = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/user/avos-previews"

def slugify(s):
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:60]

def host_of(u):
    return re.sub(r"^https?://(www\.)?", "", (u or "").lower()).split("/")[0]

BLACKLIST_RE = re.compile(r"mcdonalds|hofer|spar|billa|rewe|obi|hornbach|palmers|hervis|aida\.at|cafe-central|mandarinoriental|expert\.at|felber|stroeck|anker(brot)?\.at|oebb|raiffeisen|sparkasse|bipa|dm-drogerie|libro|thalia|pearle|hartlauer|fielmann|fussl|nkd|takko|deichmann|vapiano|nordsee\.|burgerking|kfc|subway|starbucks|testsieger|marriott|hilton|accor|ibis|motel-one|jufa|austria-trend")

# category value tiers (base low, base high in EUR for a SotA relaunch)
TIERS = {
    "Imkerei": (2200, 3800), "Drechslerei": (2200, 3800), "Schuhmacher": (2200, 3600),
    "Schneiderei": (2400, 3900), "Fußpflege": (2400, 4000), "Privatzimmer / Pension": (3000, 5200),
    "Weinstube / Vinothek": (3200, 5400), "Heuriger / Buschenschank": (3400, 5800),
    "Friseur": (3200, 5200), "Kosmetikinstitut": (3400, 5600), "Blumenhandel": (3200, 5200),
    "Buchhandlung": (3600, 6000), "Textilreinigung": (3000, 5000), "Fotostudio": (3400, 5600),
    "Uhrmacher / Juwelier": (3800, 6400), "Fahrradwerkstatt": (3400, 5600),
    "Bar / Café": (3600, 6000), "Kaffeehaus / Café": (3800, 6400), "Konditorei / Café": (4000, 6800),
    "Bäckerei": (4200, 7200), "Fleischerei": (4200, 7200), "Gasthaus / Gasthof": (4400, 7600),
    "Restaurant": (4600, 8000), "Gärtnerei": (4200, 7000), "Glaserei": (4200, 7000),
    "Schneiderei ": (2400, 3900), "Steinmetz": (4400, 7400), "Hafner / Kachelöfen": (4400, 7400),
    "Sattlerei": (3600, 6000), "Tapezierer / Raumausstattung": (3800, 6400),
    "Schlosserei / Metallbau": (4600, 7800), "Malerei": (4400, 7400), "Spenglerei": (4600, 7800),
    "Dachdeckerei": (5000, 8600), "Zimmerei / Holzbau": (5200, 9000), "Tischlerei": (5000, 8600),
    "Installateur (HKLS)": (5200, 9000), "Elektrotechnik": (5200, 9000),
    "Physiotherapie": (4400, 7600), "Fahrschule": (5000, 8600), "Optiker": (4600, 7800),
    "KFZ-Werkstätte": (5000, 8600), "Weinbau / Winzer": (5400, 9400),
    "Pension": (5400, 9400), "Hotel / Gasthof": (7500, 14000),
}
DEFAULT_TIER = (3800, 6400)

def estimate(cat, audit, name=""):
    lo, hi = TIERS.get(cat, DEFAULT_TIER)
    sig = audit.get("signals", [])
    txt_ind = " ".join(audit.get("events", [])) + " " + (audit.get("title") or "")
    mult = 1.0
    rationale = []
    if "spam-injected" in sig:
        mult += 0.12; rationale.append("Akutfall: Website mit SEO-Spam kompromittiert — Sicherheits-Cleanup + Relaunch dringend")
    if audit.get("events"):
        mult += 0.10; rationale.append("Aktiver Veranstaltungsbetrieb — Event-Modul/Kalender als Mehrwert")
    if re.search(r"zimmer|übernacht|apartment|ferienwohnung", txt_ind, re.I):
        mult += 0.15; rationale.append("Beherbergung — Booking-Strecke möglich")
    if re.search(r"shop|bestell|online kaufen|versand", txt_ind, re.I):
        mult += 0.12; rationale.append("Shop-/Bestell-Potenzial")
    if "frameset" in sig or "flash" in sig:
        rationale.append("Technischer Totalstand (Frames/Flash) — kompletter Neubau nötig")
    sc = audit.get("outdated_score", 0)
    if sc >= 7:
        mult += 0.05
    lo2, hi2 = int(round(lo * mult, -2)), int(round(hi * mult, -2))
    mid = int(round((lo2 + hi2) / 2, -2))
    return lo2, hi2, mid, rationale

BADGE_MAP = [
    ("no-viewport", "KEIN MOBILE"), ("frameset", "FRAMES"), ("flash", "FLASH"),
    ("no-https", "KEIN HTTPS"), ("spam-injected", "SPAM-BEFALL"),
    ("legacy-generator", "UALT-CMS"), ("jquery1.x", "ALTE TECHNIK"),
    ("table-layout", "TABELLEN-LAYOUT"), ("browser-era-note", "IE-ÄRA"),
    ("old-wordpress", "ALTES WORDPRESS"), ("marquee", "MARQUEE"),
]

def badges_for(audit, cat):
    b = []
    sig = audit.get("signals", [])
    for s, lab in BADGE_MAP:
        if s in sig and len(b) < 4:
            b.append(lab)
    cy = audit.get("copyright_year")
    if cy and cy <= 2019 and "COPYRIGHT ALT" not in b:
        b.append(f"© {cy}")
    if audit.get("events"):
        b.append("EVENTS AKTIV")
    if audit.get("socials"):
        b.append("SOCIAL AKTIV")
    return b[:6]

def mode_jobs():
    cands = json.load(open(os.path.join(SC, "herold_candidates.json")))
    v1p = os.path.join(SC, "herold_candidates_v1.json")
    if os.path.exists(v1p):
        _seen = {c["id"] for c in cands}
        cands += [c for c in json.load(open(v1p)) if c["id"] not in _seen]
    details = json.load(open(os.path.join(SC, "herold_details.json")))
    existing = json.load(open(os.path.join(REPO, "businesses.json")))
    known_hosts = {host_of(b["oldWebsite"]) for b in existing}
    jobs, seen = [], set()
    for c in cands:
        d = details.get(c["id"])
        if not d or not d.get("website"):
            continue
        h = host_of(d["website"])
        if h in known_hosts or h in seen or not h:
            continue
        # skip obvious chains/portals
        if re.search(r"mcdonalds|hofer|spar|billa|rewe|obi|hornbach|palmers|hervis|aida\.at|cafe-central|mandarinoriental|expert\.at|felber|stroeck|anker(brot)?\.at|oebb|raiffeisen|sparkasse|bipa|dm-drogerie|libro|thalia|pearle|hartlauer|fielmann|fussl|nkd|takko|deichmann|vapiano|nordsee\.|burgerking|kfc|subway|starbucks|testsieger|marriott|hilton|accor|ibis|motel-one|jufa|austria-trend", h):
            continue
        if re.search(r"/standorte?/|/filiale|/betrieb/|/branch/", d["website"]):
            continue
        seen.add(h)
        jobs.append({"key": c["id"], "url": d["website"]})
    json.dump(jobs, open(os.path.join(SC, "jobs_new.json"), "w"))
    print(f"{len(jobs)} new sites to audit")

# --- recurring revenue model -------------------------------------------------
# monthly care retainer (hosting, wartung, updates, seo-light) and
# AI assistant (chat client on the site, monthly saas fee) per canonical category
HORIZON_MONTHS = 36

def recurring_for(cat):
    """returns (care_lo, care_hi, ai_lo, ai_hi, ai_use) per month in EUR"""
    C = canon_cat(cat)
    T = {
        "Hotel / Gasthof": (120, 250, 150, 300, "KI-Concierge: beantwortet Buchungsanfragen, Zimmer-/Preisfragen und FAQ mehrsprachig rund um die Uhr, übergibt an die Rezeption"),
        "Pension": (80, 150, 80, 150, "KI-Buchungsassistent: Verfügbarkeit, Anreise, Frühstückszeiten — entlastet die private Vermietung"),
        "Privatzimmer / Pension": (60, 120, 60, 120, "KI-Buchungsassistent für Anfragen & Belegung"),
        "Restaurant": (90, 180, 60, 120, "KI-Reservierungs- & FAQ-Chat: Tischreservierung, Öffnungszeiten, Karte, Allergene"),
        "Gasthaus / Gasthof": (90, 180, 60, 120, "KI-Reservierungs-Chat: Tische, Feiern, Menüfragen"),
        "Kaffeehaus / Café": (80, 150, 50, 100, "KI-Gäste-Chat: Öffnungszeiten, Reservierung, Events"),
        "Konditorei / Café": (80, 150, 50, 110, "KI-Bestellassistent: Tortenanfragen (Anlass, Größe, Abholtermin)"),
        "Bar / Café": (80, 150, 50, 100, "KI-Gäste-Chat: Events, Reservierung"),
        "Weinstube / Vinothek": (80, 150, 50, 110, "KI-Wein-Berater: Sortiment, Verkostungen, Click&Collect"),
        "Heuriger / Buschenschank": (80, 150, 50, 110, "KI-Ausg'steckt-Auskunft: Termine, Reservierung, Buschenschank-Kalender"),
        "Weinbau / Winzer": (90, 180, 50, 110, "KI-Sommelier: Weinempfehlung, Lagen/Jahrgänge, Shop-Beratung, Verkostungstermine"),
        "Bäckerei": (80, 160, 40, 90, "KI-Vorbestell-Assistent: Sortiment, Filialen, Großbestellungen"),
        "Fleischerei": (80, 160, 40, 90, "KI-Bestellassistent: Platten/Catering-Anfragen, Wochenangebot"),
        "Ab-Hof-Verkauf / Hofladen": (60, 120, 30, 70, "KI-Hofladen-FAQ: Abholzeiten, Saisonware, Vorbestellung"),
        "Imkerei": (60, 120, 30, 70, "KI-Produkt-FAQ: Sorten, Versand, Ab-Hof-Zeiten"),
        "Fischzucht / Direktvermarktung": (60, 120, 30, 70, "KI-FAQ: Frischfisch-Vorbestellung, Abholung"),
        "Friseur": (70, 140, 50, 100, "KI-Terminassistent: Buchung, Preisliste, Erinnerungen — spart Telefonzeit im Salon"),
        "Kosmetikinstitut": (70, 140, 50, 100, "KI-Terminassistent: Behandlungen, Buchung, Gutscheine"),
        "Nagelstudio": (60, 120, 40, 90, "KI-Terminassistent: Buchung & Preisliste"),
        "Fußpflege": (60, 120, 40, 90, "KI-Terminassistent: Buchung & Hausbesuchs-Anfragen"),
        "Massage-Institut": (70, 140, 50, 100, "KI-Terminassistent: Behandlungsarten, Buchung"),
        "Heilmassage": (70, 140, 50, 100, "KI-Terminassistent inkl. Kassen-/Zuweisungsfragen"),
        "Physiotherapie": (80, 150, 60, 120, "KI-Praxis-Assistent: Termin, Kassen-/Wahltherapeut-Fragen, Erstinfo"),
        "Fahrschule": (90, 180, 80, 150, "KI-Kursberater: Führerscheinklassen, Kurstermine, Preise, Online-Anmeldung — Zielgruppe chattet lieber als sie anruft"),
        "Optiker": (80, 160, 50, 100, "KI-Berater: Sehtest-Termin, Marken, Kontaktlinsen-Nachbestellung"),
        "Uhrmacher / Juwelier": (80, 160, 50, 100, "KI-Berater: Reparaturanfragen, Ankauf, Anlassgeschenke"),
        "Buchhandlung": (80, 160, 50, 100, "KI-Buchberater: Empfehlungen, Verfügbarkeit, Abholservice"),
        "Eisenwaren / Fachhandel": (80, 160, 50, 100, "KI-Produktfinder: Verfügbarkeit, Alternativen, Beratung"),
        "Autohaus / KFZ-Handel": (90, 180, 80, 150, "KI-Verkaufsassistent: Fahrzeugbestand, Probefahrt-Termine, Finanzierungsfragen"),
        "KFZ-Werkstätte": (80, 160, 60, 120, "KI-Werkstatt-Assistent: §57a-Pickerl-Termine, Reifenwechsel, Kostenschätzung"),
        "Steuerberatung": (100, 200, 100, 200, "KI-Mandanten-Assistent: Unterlagen-Checklisten, Fristen, Terminvereinbarung, Erstfragen"),
        "Reisebüro": (90, 170, 80, 160, "KI-Reiseberater: Zielgebiets-FAQ, Angebotsanfragen, Reisedokumente"),
        "Catering / Partyservice": (80, 160, 60, 120, "KI-Angebotsassistent: Menüs, Personenzahl, Termin — qualifiziert Anfragen vor"),
        "Fotostudio": (60, 120, 40, 80, "KI-Buchungs-Chat: Pakete, Preise, Termin"),
        "Schneiderei": (60, 120, 30, 70, "KI-FAQ: Preise, Abholzeiten"),
        "Textilreinigung": (60, 120, 30, 70, "KI-FAQ: Preisliste, Abhol-/Lieferservice"),
        "Blumenhandel": (70, 140, 40, 90, "KI-Bestellassistent: Sträuße, Hochzeits-/Trauerfloristik-Anfragen"),
        "Gärtnerei": (80, 150, 50, 100, "KI-Pflanzenberater: Sortiment, Saison, Pflegetipps, Projektanfragen"),
        "Baumschule / Gärtnerei": (80, 150, 50, 100, "KI-Pflanzenberater: Sortiment & Projektanfragen"),
    }
    if C in T:
        return T[C]
    TRADES = {"Tischlerei", "Installateur (HKLS)", "Elektrotechnik", "Malerei", "Dachdeckerei",
              "Spenglerei", "Schlosserei / Metallbau", "Zimmerei / Holzbau", "Steinmetz",
              "Hafner / Kachelöfen", "Glaserei", "Sattlerei", "Tapezierer / Raumausstattung",
              "Fahrradwerkstatt", "Drechslerei", "Schuhmacher"}
    if C in TRADES:
        return (80, 160, 60, 120, "KI-Anfrage-Qualifizierer: nimmt Projektanfragen strukturiert auf (Art, Maße, Fotos, Wunschtermin) und liefert vorqualifizierte Leads")
    return (80, 150, 50, 100, "KI-Anfrage-Assistent: FAQ, Öffnungszeiten, strukturierte Kontaktaufnahme")

PITCH = {
    "Gasthaus / Gasthof": "Wirtshaus mit Stammpublikum, aber Web-Auftritt aus einer anderen Zeit: Ein Relaunch mit aktueller Speisekarte, Reservierungsanfrage, Google-Maps-Anbindung und mobiler Darstellung holt Laufkundschaft und Feiern-Buchungen ab.",
    "Restaurant": "Restaurant mit veralteter Website — mobile Gäste springen ab. SotA-Relaunch mit Speisekarte als strukturierten Daten, Reservierung, Fotos und lokalem SEO bringt direkt messbar mehr Tische.",
    "Kaffeehaus / Café": "Café mit Charme, Website ohne: Relaunch mit Story, Öffnungszeiten, Instagram-Einbindung und mobiler Karte stärkt Tourismus- und Stammgeschäft.",
    "Konditorei / Café": "Konditorei mit Produkt, das sich visuell verkauft — die alte Website tut es nicht. Relaunch mit Produktgalerie, Torten-Anfrageformular und saisonalen Aktionen.",
    "Bäckerei": "Traditionsbäckerei mit veralteter Website: Relaunch mit Filialen/Öffnungszeiten, Produktwelt und Vorbestell-Funktion; starke lokale Suche (\"Bäckerei + Ort\").",
    "Fleischerei": "Fleischerei mit treuer Kundschaft: Relaunch mit Wochenangebot, Catering/Platten-Bestellung und regionaler Herkunftsstory hebt Bestellungen und Feiertagsgeschäft.",
    "Heuriger / Buschenschank": "Buschenschank mit Ausg'steckt-Terminen, die online kaum auffindbar sind: Relaunch mit Kalender, Newsletter und Weinshop-Option monetarisiert die bestehende Nachfrage.",
    "Weinbau / Winzer": "Weingut ohne zeitgemäßen Auftritt: Relaunch mit Weinshop (Direktvertrieb!), Verkostungsterminen und Jahrgangs-Storytelling — höchste Marge aller Maßnahmen.",
    "Weinstube / Vinothek": "Vinothek mit veralteter Seite: Relaunch mit Sortiment, Events und Click&Collect.",
    "Hotel / Gasthof": "Beherbergungsbetrieb ohne moderne Buchungsstrecke verliert an Booking.com-Provisionen: Relaunch mit Direktbuchung, Zimmergalerie und mehrsprachigem Auftritt rechnet sich binnen Monaten.",
    "Pension": "Pension mit veralteter Website: Direktbuchungs-Relaunch senkt OTA-Provisionen und füllt Nebensaison.",
    "Privatzimmer / Pension": "Kleinvermieter: schlanker Relaunch mit Belegungskalender und Anfrage-Funnel.",
    "Friseur": "Salon mit veralteter Website: Relaunch mit Online-Terminbuchung, Preisliste und Team-Seite reduziert Telefonaufwand und bringt Neukundschaft.",
    "Kosmetikinstitut": "Institut mit Behandlungsangebot, das online nicht wirkt: Relaunch mit Buchung, Gutschein-Verkauf und Vorher/Nachher-Galerie.",
    "Fußpflege": "Praxis mit voller Auslastung am Telefon: Online-Terminbuchung entlastet und füllt Lücken.",
    "Tischlerei": "Handwerksbetrieb, dessen Referenzen online nicht sichtbar sind: Relaunch mit Projektgalerie, Materialwelt und Anfrage-Funnel bringt größere Privat- und B2B-Aufträge.",
    "Zimmerei / Holzbau": "Holzbau boomt — der Webauftritt nicht: Referenz-Relaunch mit Projektstrecken und Förder-Infos generiert hochwertige Anfragen.",
    "Installateur (HKLS)": "Installateur ohne modernen Auftritt verliert Heizungstausch-Anfragen (Förderwelle!): Relaunch mit Notdienst-CTA, Förderrechner und Bewertungen.",
    "Elektrotechnik": "Elektrobetrieb: Relaunch mit PV/E-Mobilität-Landingpages trifft die aktuelle Nachfrage; Anfrageformulare ersetzen den Anrufbeantworter.",
    "Malerei": "Malerbetrieb: Vorher/Nachher-Galerie, Farbberatung und schnelle Angebotsanfrage — ein Relaunch macht Qualität sichtbar.",
    "Dachdeckerei": "Dachdecker mit vollem Auftragsbuch, aber ohne digitale Visitenkarte für die Generation Google: Relaunch sichert die nächsten Jahre Anfragen.",
    "Spenglerei": "Spengler: Relaunch mit Leistungsübersicht und Sturmschaden-Notfall-CTA.",
    "Schlosserei / Metallbau": "Metallbau: Referenzgalerie (Geländer, Tore, Stiegen) plus Konfigurator-Anfrage hebt den Auftragswert.",
    "Steinmetz": "Steinmetz: pietätvolle, moderne Präsenz mit Grabmal-Galerie und Küchenplatten-Geschäft als zweitem Standbein.",
    "Hafner / Kachelöfen": "Hafner: Kachelofen-Galerie und Heizkosten-Argumentation — Relaunch trifft die Energiepreis-Sensibilität.",
    "Glaserei": "Glaserei: Notdienst-CTA und Duschverglasungs-Galerie; Relaunch bringt Privatkundschaft.",
    "Schneiderei": "Änderungsschneiderei: Klare Preisliste, Öffnungszeiten und Google-Profil-Anbindung.",
    "Textilreinigung": "Putzerei: schlanker Relaunch mit Preisliste und Abhol-Service-Anfrage.",
    "Fahrschule": "Fahrschule: Kurskalender mit Online-Anmeldung und Preisrechner — die Zielgruppe ist 17 und ausschließlich mobil unterwegs; die alte Website konvertiert nicht.",
    "Physiotherapie": "Praxis: Online-Terminbuchung, Kassen/Wahltherapeut-Info und Leistungsseiten — Relaunch füllt den Kalender planbar.",
    "Optiker": "Optiker: Markenwelt, Sehtest-Terminbuchung und Kontaktlinsen-Abo — Relaunch verteidigt gegen Ketten.",
    "Uhrmacher / Juwelier": "Juwelier: hochwertige Produktfotografie und Service-Storys (Reparatur, Ankauf) — die alte Seite wird dem Sortiment nicht gerecht.",
    "Fotostudio": "Fotostudio: das Schaufenster ist die Website — ein datiertes Portfolio kostet direkt Buchungen. Relaunch mit Galerie-System und Paketpreisen.",
    "Buchhandlung": "Buchhandlung: Veranstaltungen (Lesungen!), Abholservice und Empfehlungs-Blog — Relaunch stärkt das Lokale gegen Amazon.",
    "Imkerei": "Imkerei: kleiner, feiner Shop-Relaunch (Honig-Direktvertrieb, Ab-Hof-Zeiten) mit sehr persönlicher Story.",
    "Fahrradwerkstatt": "Radwerkstatt: Service-Terminbuchung und E-Bike-Kompetenz — Relaunch trifft den Radboom.",
    "Blumenhandel": "Blumengeschäft: Hochzeits/Trauerfloristik-Galerien und Bestell-Hotline — visueller Relaunch verkauft.",
    "Gärtnerei": "Gärtnerei: Saisonkalender, Pflanzen-Sortiment und Gestaltungs-Referenzen — Relaunch bringt Projektaufträge.",
    "KFZ-Werkstätte": "KFZ-Betrieb: Terminbuchung (§57a Pickerl!), Reifen-Service und Gebrauchtwagen-Liste — Relaunch mit klaren CTAs.",
    "Bar / Café": "Bar/Café: Events, Karte und Instagram-Feed — mobiler Relaunch für ein mobiles Publikum.",
    "Drechslerei": "Drechslerei: Manufaktur-Story mit kleinem Shop — Nische mit treuer Kundschaft.",
    "Schuhmacher": "Schuhmacher: Handwerks-Story, Preisliste, Öffnungszeiten — kompakter, würdiger Auftritt.",
    "Sattlerei": "Sattlerei: Nischen-Handwerk mit Liebhaber-Kundschaft — Portfolio-Relaunch.",
    "Tapezierer / Raumausstattung": "Raumausstatter: Stoffwelten und Referenzen — visueller Relaunch verkauft Beratung.",
    "Hotel": "Beherbergungsbetrieb ohne moderne Buchungsstrecke: Relaunch mit Direktbuchung rechnet sich binnen Monaten.",
}
DEFAULT_PITCH = "Aktiver Betrieb mit deutlich veralteter Website: Ein zeitgemäßer Relaunch (mobil, schnell, DSGVO-konform, lokal auffindbar) verwandelt die bestehende Reputation in messbare Anfragen."

def region_from_zip(z):
    if not z or not re.match(r"^\d{4}$", str(z)):
        return None
    z = int(z)
    if 1010 <= z <= 1239: return "Wien"
    if 2000 <= z <= 2899: return "Niederösterreich"
    if 3000 <= z <= 3999: return "Niederösterreich"
    if 4000 <= z <= 4299: return "Oberösterreich"
    if 4300 <= z <= 4303: return "Niederösterreich"
    if 4304 <= z <= 4999: return "Oberösterreich"
    if z in (5230, 5232, 5233, 5251, 5261, 5270, 5280, 5282, 5310, 5311, 5360) or 5211 <= z <= 5283: return "Oberösterreich"
    if 8000 <= z <= 8999: return "Steiermark"
    return "OUT"

def prettify_ort(slug):
    import urllib.parse
    s = urllib.parse.unquote(slug)
    s = s.replace("-", " ")
    small = {"an", "der", "am", "im", "bei", "ob", "und", "unter", "ober", "auf"}
    words = []
    for w in s.split():
        words.append(w if w in small else (w[:1].upper() + w[1:]))
    return " ".join(words)

def compose_activity(det):
    parts = []
    if det.get("review_count"):
        s = f"Herold: {det['review_count']} Bewertung(en)"
        if det.get("last_review_date"):
            s += f", zuletzt {det['last_review_date']}"
        parts.append(s + ".")
    if det.get("review_snippets"):
        parts.append("Stimme: „" + det["review_snippets"][0][:140] + "“")
    return " ".join(parts) or None

def fix_mojibake(s):
    if not isinstance(s, str) or not s:
        return s
    if "Ã" in s or "ï»" in s or "â€" in s:
        try:
            s = s.encode("latin-1", "ignore").decode("utf-8", "ignore")
        except Exception:
            pass
    return s.replace("﻿", "").strip()

def fix_lead_texts(l):
    for k in ("impressum_text", "activity_note", "events_note", "name", "town", "address", "pitch"):
        if l.get(k):
            l[k] = fix_mojibake(l[k])
    for k in ("contact_names", "emails", "phones"):
        if l.get(k):
            l[k] = [fix_mojibake(x) for x in l[k]]
    return l

ADDR_IMP_RE = re.compile(
    r"([A-ZÄÖÜ][\w.ßäöü -]{1,32}?(?:gasse|straße|strasse|weg|platz|allee|markt|zeile|ring|siedlung)\s*\d+[a-zA-Z]?"
    r"(?:\s*[/-]\s*\d+[a-zA-Z]?)*)[,\s]+(?:A-?)?(\d{4})\s+([A-ZÄÖÜ][A-Za-zäöüß.\- ]{2,28})")
ZIP_CITY_RE = re.compile(r"\b([1-9]\d{3})\s+([A-ZÄÖÜ][A-Za-zäöüß.\-]{2,28}(?:\s[A-ZÄÖÜ][A-Za-zäöüß.\-]+){0,2})")

def addr_from_impressum(imp):
    m = ADDR_IMP_RE.search(imp)
    if m:
        street, z, city = m.groups()
        return f"{street.strip()}, {z} {city.strip().rstrip('.,-')}"
    m = ZIP_CITY_RE.search(imp)
    if m:
        return f"{m.group(1)} {m.group(2).strip().rstrip('.,-')}"
    return None

def dedup_phones(phones):
    seen, out = set(), []
    for p in phones:
        d = re.sub(r"\D", "", p)
        d = "43" + d.lstrip("0") if not d.startswith("43") else d
        if d not in seen:
            seen.add(d)
            out.append(p)
    return out

def mode_final():
    cands = {c["id"]: c for c in json.load(open(os.path.join(SC, "herold_candidates.json")))}
    v1p = os.path.join(SC, "herold_candidates_v1.json")
    if os.path.exists(v1p):
        for c in json.load(open(v1p)):
            cands.setdefault(c["id"], c)
    details = json.load(open(os.path.join(SC, "herold_details.json")))
    audits_new = {a["key"]: a for a in json.load(open(os.path.join(SC, "audit_new.json")))}
    audits_old = {a["key"]: a for a in json.load(open(os.path.join(SC, "audit_existing.json")))}
    existing = json.load(open(os.path.join(REPO, "businesses.json")))
    overrides = {}
    ovf = os.path.join(SC, "research_overrides.json")
    if os.path.exists(ovf):
        overrides = json.load(open(ovf))
    cleans = {}
    clf = os.path.join(SC, "contact_cleanup.json")
    if os.path.exists(clf):
        cleans = json.load(open(clf))
    haddr = {}
    hap = os.path.join(SC, "herold_addresses.json")
    if os.path.exists(hap):
        haddr = json.load(open(hap))

    leads = []
    # existing 84 (prior vetted research) — keep all alive ones
    for b in existing:
        a = audits_old.get(b["slug"], {})
        if a.get("status") in ("dead",):
            continue
        cat = b["category"]
        catk = cat
        lo, hi, mid, rat = estimate_cat_lookup(cat, a)
        town = b["location"].split(",")[0].strip()
        reg = b["region"]
        if town == reg:
            town = ""
        leads.append({
            "slug": b["slug"], "name": b["name"], "category": cat, "region": reg, "town": town,
            "website": b["oldWebsite"], "final_url": a.get("final_url"),
            "phones": a.get("phones", []), "emails": a.get("emails", []),
            "contact_names": a.get("contact_names", []),
            "address": addr_from_impressum(a.get("impressum_text") or ""),
            "impressum_text": a.get("impressum_text", ""),
            "screenshot": b["slug"] + ".jpg",
            "score": a.get("outdated_score"), "signals": a.get("signals", []),
            "badges": badges_for(a, cat) + (["OFFLINE"] if a.get("status") == "parked" else []),
            "rating": None, "review_count": None,
            "events_note": "; ".join(a.get("events", [])[:2])[:230] or None,
            "activity_note": b.get("description"),
            "pitch": " ".join(rat + [PITCH.get(base_cat(cat), DEFAULT_PITCH)]),
            "est_low": lo, "est_high": hi, "est_mid": mid,
            "source": "bestand",
        })
    known_hosts = {host_of(l["website"]) for l in leads}

    for key, a in audits_new.items():
        if a.get("status") != "ok" or a.get("outdated_score", 0) < 3:
            continue
        c = cands.get(key)
        d = details.get(key, {})
        if not c:
            continue
        h = host_of(a.get("final_url") or a.get("url"))
        if h in known_hosts or BLACKLIST_RE.search(h):
            continue
        known_hosts.add(h)
        zipc = d.get("zip")
        reg = region_from_zip(zipc) or c["region"]
        if reg == "OUT":
            continue
        cat = c["category"]
        lo, hi, mid, rat = estimate_cat_lookup(cat, a)
        ha = haddr.get(key, {})
        street = ha.get("street") or d.get("street")
        zipc = ha.get("zip") or zipc
        city = ha.get("city") or d.get("city") or prettify_ort(c["ort_slug"])
        town = city
        addr = ", ".join(x for x in (street, " ".join(y for y in (zipc, city) if y)) if x)
        if not addr:
            addr = addr_from_impressum(a.get("impressum_text") or "")
        phones = a.get("phones", []) or ([d["phone"]] if d.get("phone") else [])
        emails = a.get("emails", []) or ([d["email"]] if d.get("email") else [])
        slug = f"h-{key}-{slugify(c['name'])[:40]}"
        leads.append({
            "slug": slug, "name": c["name"], "category": cat, "region": reg, "town": town,
            "website": a.get("url"), "final_url": a.get("final_url"),
            "phones": phones, "emails": emails,
            "contact_names": a.get("contact_names", []), "address": addr or None,
            "impressum_text": a.get("impressum_text", ""),
            "screenshot": slug + ".jpg",
            "score": a.get("outdated_score"), "signals": a.get("signals", []),
            "badges": badges_for(a, cat),
            "rating": d.get("rating"), "review_count": d.get("review_count"),
            "last_review_date": d.get("last_review_date"),
            "events_note": "; ".join(a.get("events", [])[:2])[:230] or None,
            "activity_note": compose_activity(d),
            "pitch": " ".join(rat + [PITCH.get(base_cat(cat), DEFAULT_PITCH)]),
            "est_low": lo, "est_high": hi, "est_mid": mid,
            "source": "herold",
        })
    # apply research overrides + contact cleanup + phone dedup
    for l in leads:
        fix_lead_texts(l)
        l["phones"] = dedup_phones(l.get("phones", []))
        if not l.get("address"):
            l["address"] = ", ".join(x for x in (l.get("town"), l.get("region")) if x) or l.get("region")
        ov = overrides.get(l["slug"])
        if ov:
            if ov.get("activity_note"):
                l["activity_note"] = ov["activity_note"]
            if ov.get("events_note"):
                l["events_note"] = ov["events_note"]
            if ov.get("extra_contact"):
                l["contact_names"] = [ov["extra_contact"]] + l.get("contact_names", [])
        cl = cleans.get(l["slug"])
        if cl and cl.get("remove"):
            l["_remove"] = True
            continue
        if cl is not None:
            l["contact_names"] = cl.get("contact_names", l["contact_names"])
            if cl.get("phones"):
                l["phones"] = cl["phones"]
            if cl.get("emails"):
                l["emails"] = cl["emails"]
        if l["source"] == "bestand" and (l.get("score") or 0) < 3:
            l["signals"] = (l.get("signals") or []) + ["manuell als Relaunch-Kandidat eingestuft (Recherche 27.08.2026)"]
        # recurring revenue: care retainer + AI assistant, 36-month horizon
        care_lo, care_hi, ai_lo, ai_hi, ai_use = recurring_for(l["category"])
        l.update({"care_lo": care_lo, "care_hi": care_hi, "ai_lo": ai_lo, "ai_hi": ai_hi,
                  "ai_use": ai_use, "horizon_months": HORIZON_MONTHS})
        l["tot_lo"] = l["est_low"] + HORIZON_MONTHS * (care_lo + ai_lo)
        l["tot_hi"] = l["est_high"] + HORIZON_MONTHS * (care_hi + ai_hi)
        l["tot_mid"] = int(round((l["tot_lo"] + l["tot_hi"]) / 2, -2))
    leads = [l for l in leads if not l.get("_remove")]
    # cap: keep report usable — bestand always; herold ranked by contact quality + score
    CAP = 1500
    if len(leads) > CAP:
        bestand = [l for l in leads if l["source"] == "bestand"]
        herold = [l for l in leads if l["source"] != "bestand"]
        def qual(l):
            return (bool(l.get("phones")) + bool(l.get("emails")),
                    bool(l.get("contact_names")),
                    l.get("score") or 0,
                    bool(l.get("rating")))
        herold.sort(key=qual, reverse=True)
        keep = bestand + herold[:CAP - len(bestand)]
        dropped = len(leads) - len(keep)
        print(f"capped: kept {len(keep)}, dropped {dropped} lowest-quality herold leads")
        leads = keep
    json.dump(leads, open(os.path.join(SC, "leads_full.json"), "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(len(leads), "leads", Counter(l["region"] for l in leads))

def base_cat(cat):
    return canon_cat(cat)

def estimate_cat_lookup(cat, audit):
    return estimate(canon_cat(cat), audit)

def canon_cat(cat):
    if cat in TIERS:
        return cat
    # fuzzy: match existing-84 categories onto tiers
    MAP = [("Buschenschank", "Heuriger / Buschenschank"), ("Heurig", "Heuriger / Buschenschank"),
           ("Bäckerei", "Bäckerei"), ("Kaffeehaus", "Kaffeehaus / Café"), ("Café", "Konditorei / Café"),
           ("Konditorei", "Konditorei / Café"), ("Fleisch", "Fleischerei"), ("Gasthaus", "Gasthaus / Gasthof"),
           ("Gasthof", "Hotel / Gasthof"), ("Hotel", "Hotel / Gasthof"), ("Pension", "Pension"),
           ("Privatzimmer", "Privatzimmer / Pension"), ("Gästehaus", "Privatzimmer / Pension"),
           ("Gästezimmer", "Pension"), ("Physiotherapie", "Physiotherapie"), ("Fahrschule", "Fahrschule"),
           ("Pizzeria", "Restaurant"), ("Restaurant", "Restaurant"), ("Tischlerei", "Tischlerei"),
           ("Friseur", "Friseur"), ("Winzer", "Weinbau / Winzer"), ("Weinbau", "Weinbau / Winzer"),
           ("Weingut", "Weinbau / Winzer"), ("Installat", "Installateur (HKLS)"), ("Elektro", "Elektrotechnik"),
           ("Imker", "Imkerei"), ("Optiker", "Optiker"), ("Foto", "Fotostudio"), ("Buchhandlung", "Buchhandlung"),
           ("KFZ", "KFZ-Werkstätte"), ("Schuh", "Schuhmacher"), ("Schneider", "Schneiderei"),
           ("Reinigung", "Textilreinigung"), ("Malerei", "Malerei"), ("Maler", "Malerei"),
           ("Dachdeck", "Dachdeckerei"), ("Glaser", "Glaserei"), ("Zimmerei", "Zimmerei / Holzbau"),
           ("Steinmetz", "Steinmetz"), ("Schlosser", "Schlosserei / Metallbau"), ("Kosmetik", "Kosmetikinstitut"),
           ("Blumen", "Blumenhandel"), ("Gärtner", "Gärtnerei"), ("Uhr", "Uhrmacher / Juwelier"),
           ("Juwel", "Uhrmacher / Juwelier"), ("Bar", "Bar / Café"), ("Vinothek", "Weinstube / Vinothek")]
    for k, t in MAP:
        if k.lower() in cat.lower():
            return t
    return cat

if __name__ == "__main__":
    if sys.argv[1] == "jobs":
        mode_jobs()
    elif sys.argv[1] == "final":
        mode_final()
