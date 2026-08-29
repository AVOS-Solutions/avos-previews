#!/usr/bin/env python3
"""Generate the AVOS lead-research PDF: cover, summary, index, one page per lead.
Usage: gen_pdf.py <leads_full.json> <out.pdf>"""
import json, os, re, sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image

INK = HexColor("#161225")
INK_SOFT = HexColor("#2b2140")
PAPER = HexColor("#f4eee2")
PAPER_DIM = HexColor("#e9ddc9")
GOLD = HexColor("#e0a437")
GOLD_DIM = HexColor("#b8822a")
SLATE = HexColor("#6b6478")
BRASS = HexColor("#c1502e")
LINE = Color(22/255, 18/255, 37/255, alpha=0.15)
GREEN = HexColor("#4a7c59")

W, H = A4
pdfmetrics.registerFont(TTFont("DV", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

def eur(n):
    return "€ " + f"{n:,}".replace(",", ".")

def fit_text(c, text, font, size, maxw, minsize=7):
    while size > minsize and c.stringWidth(text, font, size) > maxw:
        size -= 0.5
    return size

def wrap(c, text, font, size, maxw):
    words = (text or "").split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if c.stringWidth(t, font, size) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def pill(c, x, y, text, bg, fg, size=6.6, h=11):
    tw = c.stringWidth(text, "DVB", size)
    w_ = tw + 10
    c.setFillColor(bg)
    c.roundRect(x, y, w_, h, h / 2, fill=1, stroke=0)
    c.setFillColor(fg)
    c.setFont("DVB", size)
    c.drawString(x + 5, y + h / 2 - size * 0.36, text)
    return w_ + 4

BADGE_COLORS = {
    "SPAM-BEFALL": (BRASS, PAPER), "KEIN MOBILE": (BRASS, PAPER), "FRAMES": (BRASS, PAPER),
    "FLASH": (BRASS, PAPER), "KEIN HTTPS": (GOLD_DIM, PAPER), "UALT-CMS": (GOLD_DIM, PAPER),
    "ALTE TECHNIK": (GOLD_DIM, PAPER), "TABELLEN-LAYOUT": (GOLD_DIM, PAPER),
    "IE-ÄRA": (GOLD_DIM, PAPER), "ALTES WORDPRESS": (GOLD_DIM, PAPER), "MARQUEE": (GOLD_DIM, PAPER),
    "EVENTS AKTIV": (GREEN, PAPER), "SOCIAL AKTIV": (GREEN, PAPER), "OFFLINE": (INK, PAPER),
}

def sec_head(c, x, y, label):
    c.setFillColor(GOLD_DIM)
    c.setFont("DVB", 7.5)
    c.drawString(x, y, label)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(x, y - 3, x + 243, y - 3)
    return y - 14

def footer(c, page_label):
    c.setFillColor(SLATE)
    c.setFont("DV", 7)
    c.drawString(40, 24, "AVOS Solutions · Lead-Research Österreich · Stand 28.08.2026 · vertraulich")
    c.drawRightString(W - 40, 24, page_label)

def lead_page(c, ld, idx, total, shots_dir):
    # header band
    c.setFillColor(INK)
    c.rect(0, H - 92, W, 92, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("DVB", 10)
    c.drawString(40, H - 34, f"LEAD #{idx:03d}")
    c.setFillColor(SLATE)
    c.setFont("DV", 8)
    c.drawString(105, H - 34, f"von {total} · sortiert nach Auftragspotenzial (aufsteigend)")
    name = ld["name"]
    fs = fit_text(c, name, "DVB", 19, W - 80 - 210)
    c.setFillColor(PAPER)
    c.setFont("DVB", fs)
    c.drawString(40, H - 60, name)
    sub = " · ".join(x for x in (ld.get("category"), ld.get("town"), ld.get("region")) if x)
    c.setFillColor(PAPER_DIM)
    sfs = fit_text(c, sub, "DV", 9, W - 80 - 210)
    c.setFont("DV", sfs)
    c.drawString(40, H - 78, sub)
    # estimate top right
    c.setFillColor(GOLD)
    c.setFont("DVB", 15)
    tot = f"{eur(ld.get('tot_lo', ld['est_low']))} – {eur(ld.get('tot_hi', ld['est_high']))}"
    c.drawRightString(W - 40, H - 58, tot)
    c.setFillColor(PAPER_DIM)
    c.setFont("DV", 7.2)
    c.drawRightString(W - 40, H - 70, f"3-Jahres-Potenzial · Projekt {eur(ld['est_low'])}–{eur(ld['est_high'])}")
    mon_lo = ld.get("care_lo", 0) + ld.get("ai_lo", 0)
    mon_hi = ld.get("care_hi", 0) + ld.get("ai_hi", 0)
    c.drawRightString(W - 40, H - 80, f"+ laufend {eur(mon_lo)}–{eur(mon_hi)} / Monat (Betreuung + KI)")

    # badges
    bx, by = 40, H - 112
    for b in ld.get("badges", [])[:7]:
        bg, fg = BADGE_COLORS.get(b, (SLATE, PAPER))
        if b.startswith("©"):
            bg, fg = GOLD_DIM, PAPER
        bx += pill(c, bx, by, b, bg, fg)

    # screenshot
    img_y_top = H - 122
    img_h = 296
    shot = ld.get("screenshot")
    fr_x, fr_w = 40, W - 80
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    if shot and os.path.exists(os.path.join(shots_dir, shot)):
        try:
            import tempfile
            im = Image.open(os.path.join(shots_dir, shot)).convert("RGB")
            if im.width > 1100:
                im = im.resize((1100, int(im.height * 1100 / im.width)), Image.LANCZOS)
            ratio = fr_w / im.width
            crop_h = min(im.height, int(img_h / ratio))
            im2 = im.crop((0, 0, im.width, crop_h))
            tmpdir = os.path.join(tempfile.gettempdir(), "pdfimgs")
            os.makedirs(tmpdir, exist_ok=True)
            tmp = os.path.join(tmpdir, ld["slug"] + ".jpg")
            im2.save(tmp, "JPEG", quality=72)
            iw, ih = fr_w, crop_h * ratio
            c.drawImage(tmp, fr_x, img_y_top - ih, width=iw, height=ih)
            c.rect(fr_x, img_y_top - ih, iw, ih, fill=0, stroke=1)
            cap_y = img_y_top - ih - 11
        except Exception:
            shot = None
            cap_y = img_y_top - 20
    if not shot or not os.path.exists(os.path.join(shots_dir, shot or "")):
        c.setFillColor(PAPER_DIM)
        c.rect(fr_x, img_y_top - 120, fr_w, 120, fill=1, stroke=1)
        c.setFillColor(SLATE)
        c.setFont("DV", 10)
        c.drawCentredString(W / 2, img_y_top - 65, "Kein Screenshot verfügbar (Website nicht erreichbar)")
        cap_y = img_y_top - 131
    c.setFillColor(SLATE)
    c.setFont("DV", 7.5)
    c.drawString(fr_x, cap_y, "IST-Zustand: " + (ld.get("final_url") or ld.get("website") or ""))

    # two columns
    col_y = cap_y - 18
    lx, rx = 40, 312
    colw = 243
    y = sec_head(c, lx, col_y, "KONTAKT")
    c.setFillColor(INK)
    ln_h = 10.5
    def out_line(x, yy, txt, bold=False, color=INK, size=8):
        c.setFillColor(color)
        c.setFont("DVB" if bold else "DV", size)
        c.drawString(x, yy, txt)
        return yy - ln_h
    for cn in ld.get("contact_names", [])[:3]:
        y = out_line(lx, y, "👤 " + cn if False else cn, bold=True)
    if ld.get("address"):
        c.setFillColor(SLATE)
        c.setFont("DVB", 7)
        c.drawString(lx, y, "STANDORT")
        y -= 9.5
        for line in wrap(c, ld["address"], "DV", 8, colw)[:2]:
            y = out_line(lx, y, line)
    for p in ld.get("phones", [])[:2]:
        y = out_line(lx, y, "Tel: " + p)
    for e in ld.get("emails", [])[:2]:
        y = out_line(lx, y, e)
    if not ld.get("phones") and not ld.get("emails") and not ld.get("contact_names"):
        y = out_line(lx, y, "Keine Kontaktdaten auf Website auffindbar", color=SLATE)
    y -= 6
    y = sec_head(c, lx, y, "IMPRESSUM (AUSZUG)")
    imp = ld.get("impressum_text") or "Kein Impressum gefunden — selbst das ist ein Gesprächseinstieg (Impressumspflicht §5 ECG)."
    c.setFillColor(INK_SOFT)
    c.setFont("DV", 6.8)
    for line in wrap(c, imp[:560], "DV", 6.8, colw)[:9]:
        c.drawString(lx, y, line)
        y -= 8.6

    ry = sec_head(c, rx, col_y, "WEBSITE-ZUSTAND")
    sigtxt = ", ".join(ld.get("signals", [])) or "—"
    sc = ld.get("score")
    c.setFillColor(BRASS)
    c.setFont("DVB", 8)
    if sc is not None:
        c.drawString(rx, ry, f"Veraltet-Score: {sc}/10")
    else:
        c.drawString(rx, ry, "Website aktuell nicht/nur teilweise erreichbar")
    ry -= ln_h
    c.setFillColor(INK)
    c.setFont("DV", 7.5)
    for line in wrap(c, "Befunde: " + sigtxt, "DV", 7.5, colw)[:3]:
        c.drawString(rx, ry, line)
        ry -= 9.5
    ry -= 6
    ry = sec_head(c, rx, ry, "AKTIVITÄT & BEWERTUNGEN")
    c.setFont("DV", 8)
    if ld.get("rating"):
        stars = "★" * int(round(ld["rating"])) + "☆" * (5 - int(round(ld["rating"])))
        c.setFillColor(GOLD_DIM)
        c.setFont("DVB", 8)
        rc = f' ({ld["review_count"]} Bewertungen)' if ld.get("review_count") else ""
        c.drawString(rx, ry, f"{stars}  {ld['rating']:.1f}/5{rc} — Herold")
        ry -= ln_h
    act = ld.get("activity_note")
    if act:
        c.setFillColor(INK)
        c.setFont("DV", 7.5)
        for line in wrap(c, act, "DV", 7.5, colw)[:4]:
            c.drawString(rx, ry, line)
            ry -= 9.5
    ev = ld.get("events_note")
    if ev:
        c.setFillColor(GREEN)
        c.setFont("DVB", 7.5)
        for line in wrap(c, "Termine: " + ev, "DVB", 7.5, colw)[:3]:
            c.drawString(rx, ry, line)
            ry -= 9.5
    if not ld.get("rating") and not act and not ev:
        c.setFillColor(SLATE)
        c.setFont("DV", 7.5)
        c.drawString(rx, ry, "Keine öffentlichen Bewertungs-/Eventdaten erhoben")
        ry -= ln_h
    ry -= 6
    ry = sec_head(c, rx, ry, "LAUFENDE ERLÖSE (MONATLICH)")
    c.setFillColor(INK)
    c.setFont("DV", 7.5)
    c.drawString(rx, ry, f"Website-Betreuung (Hosting, Wartung, SEO): {eur(ld.get('care_lo',0))}–{eur(ld.get('care_hi',0))}/Mon.")
    ry -= 10
    c.setFillColor(GOLD_DIM)
    c.setFont("DVB", 7.5)
    c.drawString(rx, ry, f"KI-Assistent: {eur(ld.get('ai_lo',0))}–{eur(ld.get('ai_hi',0))}/Mon.")
    ry -= 10
    c.setFillColor(INK)
    c.setFont("DV", 7.2)
    for line in wrap(c, ld.get("ai_use") or "", "DV", 7.2, colw)[:3]:
        c.drawString(rx, ry, line)
        ry -= 9
    ry -= 6
    ry = sec_head(c, rx, ry, "EINSCHÄTZUNG / PITCH")
    c.setFillColor(INK)
    c.setFont("DV", 7.5)
    pitch = ld.get("pitch") or ""
    for line in wrap(c, pitch, "DV", 7.5, colw)[:7]:
        c.drawString(rx, ry, line)
        ry -= 9.5

    footer(c, f"Lead {idx:03d}/{total}")
    c.showPage()

def cover(c, leads):
    c.setFillColor(INK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("DVB", 13)
    c.drawString(60, H - 120, "AVOS SOLUTIONS")
    c.setFillColor(PAPER)
    c.setFont("DVB", 30)
    c.drawString(60, H - 170, "Website-Relaunch Leads")
    c.drawString(60, H - 205, "Österreich 2026")
    c.setFillColor(PAPER_DIM)
    c.setFont("DV", 12)
    c.drawString(60, H - 245, "Wien · Niederösterreich · Oberösterreich · Steiermark")
    c.setStrokeColor(GOLD_DIM)
    c.setLineWidth(2)
    c.line(60, H - 265, 300, H - 265)
    n = len(leads)
    tot_lo = sum(l.get("tot_lo", l["est_low"]) for l in leads)
    tot_hi = sum(l.get("tot_hi", l["est_high"]) for l in leads)
    stats = [
        (f"{n}", "aktive Betriebe mit veralteter Website"),
        (f"{eur(tot_lo)} – {eur(tot_hi)}", "kumuliertes Auftragspotenzial über 3 Jahre (Projekt + Betreuung + KI-Assistent)"),
        ("1 Seite pro Betrieb", "Screenshot · Kontakte · Impressum · Bewertung · Pitch"),
        ("aufsteigend sortiert", "nach 3-Jahres-Potenzial (Mitte): Projekt + 36 Monate Betreuung & KI"),
    ]
    y = H - 330
    for big, small in stats:
        c.setFillColor(GOLD)
        c.setFont("DVB", 17)
        c.drawString(60, y, big)
        c.setFillColor(PAPER_DIM)
        c.setFont("DV", 10)
        c.drawString(60, y - 16, small)
        y -= 60
    c.setFillColor(SLATE)
    c.setFont("DV", 8)
    c.drawString(60, 60, "Recherche-Stand: 28. August 2026 · Quellen: Websites der Betriebe (Impressum), Herold-Branchenverzeichnis,")
    c.drawString(60, 49, "eigene technische Analyse (Responsivität, HTTPS, CMS-Alter, Copyright-Jahre) · vertraulich, nur für den internen Gebrauch")
    c.showPage()

def summary(c, leads):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("DVB", 16)
    c.drawString(40, H - 60, "Zusammenfassung & Methodik")
    from collections import Counter
    reg = Counter(l["region"] for l in leads)
    cat = Counter(l["category"] for l in leads)
    y = H - 95
    c.setFont("DVB", 10)
    c.setFillColor(GOLD_DIM)
    c.drawString(40, y, "NACH REGION")
    y -= 16
    c.setFillColor(INK)
    c.setFont("DV", 9)
    for r, n in reg.most_common():
        sub_lo = sum(l.get("tot_lo", l["est_low"]) for l in leads if l["region"] == r)
        sub_hi = sum(l.get("tot_hi", l["est_high"]) for l in leads if l["region"] == r)
        c.setFont("DVB", 9)
        c.drawString(48, y, f"{r}: {n} Leads")
        c.setFont("DV", 8)
        c.drawString(48, y - 10, f"Potenzial {eur(sub_lo)} – {eur(sub_hi)}")
        y -= 26
    y -= 10
    c.setFont("DVB", 10)
    c.setFillColor(GOLD_DIM)
    c.drawString(40, y, "TOP-BRANCHEN")
    y -= 16
    c.setFillColor(INK)
    c.setFont("DV", 9)
    for k, n in cat.most_common(18):
        c.drawString(48, y, f"{k}: {n}")
        y -= 12
    # methodology right column
    ry = H - 95
    c.setFont("DVB", 10)
    c.setFillColor(GOLD_DIM)
    c.drawString(310, ry, "METHODIK")
    ry -= 16
    meth = ("Kandidaten aus dem Herold-Branchenverzeichnis (45 Branchen × 4 Bundesländer) und der bestehenden "
            "AVOS-Recherche vom 27.08.2026. Jede Website wurde automatisiert geprüft: fehlendes mobiles Layout "
            "(Viewport), Frames/Flash, Alt-CMS (FrontPage, iWeb, altes WordPress), jQuery 1.x, Copyright-Jahre, "
            "fehlendes HTTPS, Tabellen-Layouts, SEO-Spam-Befall. Nur erreichbare, aktive Betriebe mit klar veralteter "
            "Website (Score ≥ 3) wurden aufgenommen. Kontakte stammen aus Impressum/Kontaktseiten der Websites sowie "
            "dem Herold-Eintrag; Bewertungen aus Herold (Sterne, Anzahl, letzte Bewertung). Termine/Events wurden aus "
            "den Websites extrahiert. Die Projekt-Schätzung folgt marktüblichen österreichischen Agentursätzen je "
            "Branche und Umfang (Brochure-Site bis Booking/Shop), moduliert nach Zustand und Potenzial. Das ausgewiesene Gesamtpotenzial rechnet zusätzlich 36 Monate laufende Website-Betreuung (Hosting, Wartung, SEO-Pflege) sowie einen branchenspezifischen KI-Assistenten (Chat auf der Website: Reservierung, Terminbuchung, Anfrage-Qualifizierung) als monatliche Gebühr ein — beide Positionen sind je Lead getrennt ausgewiesen. "
            "Alle Angaben ohne Gewähr; fehlende Daten sind als solche gekennzeichnet — nichts wurde geschätzt oder erfunden.")
    c.setFillColor(INK)
    c.setFont("DV", 8.5)
    for line in wrap(c, meth, "DV", 8.5, 245):
        c.drawString(310, ry, line)
        ry -= 11
    ry -= 10
    c.setFont("DVB", 10)
    c.setFillColor(GOLD_DIM)
    c.drawString(310, ry, "BADGES")
    ry -= 16
    for b, desc in [("KEIN MOBILE", "kein Viewport/responsives Layout"), ("KEIN HTTPS", "unverschlüsselt"),
                    ("FRAMES / FLASH", "Technik der 90er/2000er"), ("UALT-CMS", "FrontPage, iWeb & Co"),
                    ("SPAM-BEFALL", "gehackt / SEO-Spam — Akutfall"), ("© JAHR", "letztes Copyright-Jahr"),
                    ("EVENTS AKTIV", "Veranstaltungen auf der Website"), ("SOCIAL AKTIV", "Facebook/Instagram verlinkt")]:
        c.setFont("DVB", 8)
        c.setFillColor(INK)
        c.drawString(310, ry, b)
        c.setFont("DV", 8)
        c.setFillColor(SLATE)
        c.drawString(408, ry, desc)
        ry -= 12
    footer(c, "Übersicht")
    c.showPage()

def index_pages(c, leads):
    per = 46
    for start in range(0, len(leads), per):
        chunk = leads[start:start + per]
        c.setFillColor(PAPER)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("DVB", 13)
        c.drawString(40, H - 50, "Index — sortiert nach Auftragspotenzial (aufsteigend)")
        y = H - 78
        c.setFont("DVB", 7)
        c.setFillColor(SLATE)
        for label, x in [("#", 40), ("BETRIEB", 65), ("ORT", 255), ("BRANCHE", 350), ("REGION", 455), ("POTENZIAL 3J", 505)]:
            c.drawString(x, y, label)
        y -= 4
        c.setStrokeColor(LINE)
        c.line(40, y, W - 40, y)
        y -= 11
        for i, l in enumerate(chunk):
            idx = start + i + 1
            c.setFont("DV", 7.2)
            c.setFillColor(INK)
            c.drawString(40, y, f"{idx:03d}")
            c.setFont("DVB", 7.2)
            c.drawString(65, y, l["name"][:42])
            c.setFont("DV", 7.2)
            c.drawString(255, y, (l.get("town") or "")[:20])
            c.drawString(350, y, (l.get("category") or "")[:24])
            c.drawString(455, y, {"Wien": "W", "Niederösterreich": "NÖ", "Oberösterreich": "OÖ", "Steiermark": "STMK"}.get(l["region"], l["region"])[:4])
            c.setFillColor(GOLD_DIM)
            c.drawString(505, y, f"{eur(l.get('tot_mid', l['est_mid']))}")
            c.setFillColor(INK)
            y -= 14.2
        footer(c, "Index")
        c.showPage()

def main():
    leads = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    shots_dir = sys.argv[3] if len(sys.argv) > 3 else "."
    leads.sort(key=lambda l: (l.get("tot_mid", l["est_mid"]), l["est_high"], l["name"]))
    c = canvas.Canvas(out, pagesize=A4)
    c.setTitle("AVOS Solutions — Website-Relaunch Leads Österreich 2026")
    c.setAuthor("AVOS Solutions")
    cover(c, leads)
    summary(c, leads)
    index_pages(c, leads)
    for i, ld in enumerate(leads, 1):
        lead_page(c, ld, i, len(leads), shots_dir)
    c.save()
    print(f"PDF written: {out} ({len(leads)} leads)")

if __name__ == "__main__":
    main()
