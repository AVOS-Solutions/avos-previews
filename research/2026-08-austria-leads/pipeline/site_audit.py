#!/usr/bin/env python3
"""Phase B+C: audit business websites for outdatedness, extract impressum
contacts, phones, emails, event/activity hints.
Usage: site_audit.py <jobs.json> <out.json> [workers]
jobs.json: [{"key":..., "url":...}, ...]
"""
import json, os, re, sys, time, html
from concurrent.futures import ThreadPoolExecutor
import requests, urllib3
urllib3.disable_warnings()

CA = "/root/.ccr/ca-bundle.crt"
PROXIES_HTTPS = {"https": "http://127.0.0.1:43137"}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
      "Accept-Language": "de-AT,de;q=0.9,en;q=0.5",
      "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"}

def fetch(url, timeout=22):
    """Fetch URL; https via proxy, http direct. Returns (final_url, resp) or raises."""
    s = requests.Session()
    s.headers.update(UA)
    s.max_redirects = 8
    if url.startswith("https:"):
        return s.get(url, timeout=timeout, proxies=PROXIES_HTTPS, verify=CA, allow_redirects=True)
    # http: go direct, but a redirect to https must go through proxy -> handle manually
    u = url
    for _ in range(8):
        if u.startswith("https:"):
            return s.get(u, timeout=timeout, proxies=PROXIES_HTTPS, verify=CA, allow_redirects=True)
        r = s.get(u, timeout=timeout, allow_redirects=False)
        if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("location"):
            from urllib.parse import urljoin
            u = urljoin(u, r.headers["location"])
            continue
        return r
    raise requests.TooManyRedirects()

PARKED = re.compile(r"domain (is )?(for sale|kaufen)|sedoparking|parkingcrew|diese domain|domain-parking|website wird erstellt|under construction|baustelle.*seite|this domain has been registered|namecheap parking|godaddy", re.I)
YEAR_RE = re.compile(r"(?:©|&copy;|&#169;|copyright|\(c\))[^0-9]{0,40}((?:19|20)\d{2})(?:\s*[-–/]\s*((?:19|20)\d{2}))?", re.I)
GEN_RE = re.compile(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)', re.I)
MAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
MAILTO_RE = re.compile(r'mailto:([^"\'\s?]+)', re.I)
TEL_RE = re.compile(r'(?:tel:|callto:)([+0-9()\/\s.-]{6,20})', re.I)
PHONE_TXT_RE = re.compile(r"(?:Tel(?:efon)?\.?:?\s*|Fon:?\s*|☎\s*|\bT:?\s+)((?:\+43|0043|0)\s?[0-9][0-9()\/\s.-]{5,18}[0-9])")
NAME_CTX_RE = re.compile(
    r"(Inhaber(?:in)?|Gesch\w*ftsf\w*hrer(?:in)?|Firmeninhaber(?:in)?|Betreiber(?:in)?|Eigent\w*mer(?:in)?|"
    r"Ansprechpartner(?:in)?|Kontaktperson|Ihr\s+Team|Familie|Fam\.|Obmann|Obfrau|Meister(?:in)?|"
    r"Medieninhaber(?:in)?|Unternehmer(?:in)?|Herausgeber(?:in)?|K\w*chenchef(?:in)?|Chef(?:in)?|Kontakt)"
    r"[^A-Za-zÄÖÜäöüß]{0,20}"
    r"((?:(?:Mag|Dr|Ing|DI|Dipl|Prof|Komm|KommR|Bmst|Bäckermeister|med)\.?\s+){0,3}"
    r"[A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+){1,2})")
IMPRESSUM_LINK_RE = re.compile(r'href=["\']([^"\']*(?:impressum|imprint|kontakt|contact|ueber-uns|über-uns|about)[^"\']*)["\']', re.I)
EVENTPAGE_LINK_RE = re.compile(r'href=["\']([^"\']*(?:veranstalt|termine|events?|aktuell|news|ausgsteckt|ausgesteckt|kalender)[^"\']*)["\']', re.I)
NAME_STOP = {"Impressum", "Datenschutz", "Kontakt", "Startseite", "Team", "Öffnungszeiten", "Anfahrt",
             "Home", "Willkommen", "Herzlich", "Website", "Webdesign", "Gmbh", "GmbH", "Sitemap", "Links",
             "Galerie", "News", "Aktuelles", "Speisekarte", "Zimmer", "Preise", "Angebot", "Leistungen",
             "Über", "Uns", "Mehr", "Menü", "Menu", "Seite", "Cookie", "Cookies", "Facebook", "Instagram",
             "Google", "Maps", "Login", "Suche", "Datenschutzerklärung", "Offenlegung", "Haftung", "Agb",
             "Besuchen", "Buchen", "Rufen", "Folgen", "Finden", "Jetzt", "Hier", "Unsere", "Unser"}
STREET_SUFFIX = re.compile(r"(gasse\b|stra|weg\b|platz\b|allee\b|markt\b|zeile\b|ring\b|siedlung\b|dorf$)", re.I)
BIZ_WORDS = {"Gasthaus", "Gasthof", "Restaurant", "Hotel", "Café", "Cafe", "Weinstube", "Pension", "Zimmer",
             "Gästehaus", "Stube", "Zentrale", "China", "Pizzeria", "Bäckerei", "Fleischerei", "Tischlerei",
             "Friseur", "Salon", "Studio", "Praxis", "Institut", "Werkstatt", "Fahrschule", "Apotheke",
             "Weingut", "Buschenschank", "Heuriger", "Imkerei", "Kanzlei", "Konditorei", "Beratung",
             "Brauchst", "Gastgeber", "Betrieb", "Firma", "Verein", "Privatzimmer", "Ferienwohnung",
             "Landhaus", "Wirt", "Wirtshaus", "Beisl", "Casa", "Trattoria", "Osteria", "Chinarestaurant",
             "Grössere", "Größere", "Kartenansicht", "Adresse", "Anschrift", "Sitz", "Service", "Beste",
             "Geschäftsführung", "Haarstudio", "Fleischhauerei", "Elektrotechnik", "Asia", "Telefon",
             "Fax", "Mobil", "Email", "Route", "Anfahrtsplan", "Standort", "Qualit", "Qualität",
             "Öffnungszeit", "Reservierung", "Tel", "Mail", "Homepage", "Internet", "Btw", "Uid"}
EVENT_RE = re.compile(r"(Veranstaltung\w*|Termine?\b|Events?\b|Konzert\w*|Fest\b|Feste\b|Heurigenkalender|Ausg'?steckt|Ausgesteckt|Lesung\w*|Verkostung\w*|Weinfest|Kirtag|Markttag\w*)", re.I)
DATE_2026_RE = re.compile(r"\b([0-3]?\d\.\s?[01]?\d\.\s?(?:20)?2[5-9]\b)|((?:J[aä]nner|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s+202[5-9])")
FB_RE = re.compile(r'href=["\']((?:https?:)?//(?:www\.)?(?:facebook|instagram)\.com/[^"\']{2,80})["\']', re.I)

def host_in(href, base):
    m = re.match(r"https?://(?:www\.)?([^/]+)", href)
    b = re.match(r"https?://(?:www\.)?([^/]+)", base)
    return bool(m and b and m.group(1) == b.group(1))

def clean_txt(h):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", h, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return html.unescape(re.sub(r"\s+", " ", t))

def audit_one(job):
    key, url = job["key"], job["url"]
    out = {"key": key, "url": url}
    broken_ssl = False
    try:
        r = fetch(url)
    except requests.exceptions.SSLError:
        # broken/expired cert on their side: try plain http (a lead signal, not a dead site)
        try:
            r = fetch(re.sub(r"^https:", "http:", url))
            broken_ssl = True
        except Exception as e:
            out["status"] = "dead"
            out["error"] = "SSLError+" + type(e).__name__
            return out
    except Exception as e:
        out["status"] = "dead"
        out["error"] = type(e).__name__
        return out
    if r.status_code >= 400:
        out["status"] = "dead"
        out["error"] = f"http_{r.status_code}"
        return out
    body = r.text or ""
    out["final_url"] = str(r.url)
    out["status"] = "ok"
    low = body.lower()
    from urllib.parse import urljoin
    # 90s splash/enter page with only a couple of links -> follow the first one
    splash = False
    if len(clean_txt(body).strip()) < 120 and "<frameset" not in low:
        hrefs = [h for h in re.findall(r'href=["\']([^"\']+)["\']', body, re.I)
                 if not h.startswith(("mailto:", "javascript:", "#", "http")) or host_in(h, out["final_url"])]
        if 1 <= len(hrefs) <= 4:
            try:
                r2 = fetch(urljoin(out["final_url"], html.unescape(hrefs[0])), timeout=15)
                if r2.status_code < 400 and (r2.text or "").strip():
                    body += "\n" + r2.text
                    low = body.lower()
                    splash = True
            except Exception:
                pass
    # frameset sites: pull in frame contents for text/contact analysis
    if "<frameset" in low or "<frame " in low:
        for fsrc in re.findall(r'<i?frame[^>]+src=["\']([^"\']+)["\']', body, re.I)[:4]:
            if fsrc.startswith(("javascript:", "about:")):
                continue
            try:
                rf = fetch(urljoin(out["final_url"], html.unescape(fsrc)), timeout=15)
                if rf.status_code < 400:
                    body += "\n" + (rf.text or "")
            except Exception:
                pass
        low = body.lower()
    txt = clean_txt(body)
    if PARKED.search(txt[:4000]) or len(txt.strip()) < 80:
        out["status"] = "parked"
        return out
    if broken_ssl:
        pass  # scored below

    score = 0.0
    sig = []
    if broken_ssl:
        score += 3; sig.append("broken-ssl")
    if splash:
        score += 1.5; sig.append("splash-entry-page")
    if "<frameset" in low or "<frame " in low:
        score += 4; sig.append("frameset")
    if 'name="viewport"' not in low and "name='viewport'" not in low:
        score += 3; sig.append("no-viewport")
    if ".swf" in low or "shockwave" in low or "macromedia" in low:
        score += 2.5; sig.append("flash")
    if "<font" in low:
        score += 1.5; sig.append("font-tags")
    if "<marquee" in low or "<blink" in low:
        score += 2; sig.append("marquee")
    m = GEN_RE.search(body)
    gen = ""
    if m:
        gen = m.group(1)[:60]
        out["generator"] = gen
        gl = gen.lower()
        if any(x in gl for x in ("frontpage", "iweb", "netobjects", "dreamweaver", "publisher", "word", "golive", "namo", "web to date", "webtodate", "phase 5", "magix", "homepage")):
            score += 3; sig.append("legacy-generator")
        mwp = re.search(r"wordpress ([0-9.]+)", gl)
        if mwp and int(mwp.group(1).split(".")[0]) < 5:
            score += 2; sig.append("old-wordpress")
        if "joomla! 1" in gl or "joomla! 2" in gl:
            score += 2; sig.append("old-joomla")
    if re.search(r"jquery[/.-]1\.[0-9.]+(?:\.min)?\.js", low):
        score += 1.5; sig.append("jquery1.x")
    yrs = YEAR_RE.findall(body)
    cy = 0
    for a, b in yrs:
        cy = max(cy, int(b or a))
    if cy:
        out["copyright_year"] = cy
        if cy <= 2015: score += 3; sig.append(f"copyright-{cy}")
        elif cy <= 2019: score += 2; sig.append(f"copyright-{cy}")
        elif cy <= 2022: score += 1; sig.append(f"copyright-{cy}")
    if out["final_url"].startswith("http://"):
        score += 2; sig.append("no-https")
    if len(body) < 12000:
        score += 0.8; sig.append("tiny-page")
    if low.count("<table") >= 4 and "flex" not in low and "grid" not in low:
        score += 1.2; sig.append("table-layout")
    if re.search(r"optimiert f|best viewed|internet explorer|netscape|aufl\w*sung von 10|800x600|1024x768", low):
        score += 2; sig.append("browser-era-note")
    spam_hits = len(re.findall(r"casino|roulette|spielautomat|slots?\b|bookmaker|sportwetten-bonus|viagra|cialis|payday", low))
    if spam_hits >= 4 and "modern-stack" not in sig and 'name="viewport"' not in low:
        score += 2.5; sig.append("spam-injected")
    # modern signals
    modern = 0
    for pat, lab in (("srcset", "srcset"), ("webp", "webp"), ("elementor", "elementor"),
                     ("wp-block-", "gutenberg"), ("tailwind", "tailwind"), ("_next/", "nextjs"),
                     ("astra-theme", "astra"), ("data-aos", "aos"), ("swiper", "swiper"),
                     ("bootstrap.min.css", "bootstrap")):
        if pat in low:
            modern += 1
    if 'name="viewport"' in low and modern >= 2:
        score -= 2.5; sig.append("modern-stack")
    if "@media" in low:
        score -= 0.5
    out["outdated_score"] = round(score, 1)
    out["signals"] = sig
    out["title"] = (re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I) or [None, ""])[1]
    out["title"] = html.unescape(re.sub(r"\s+", " ", out["title"] or "")).strip()[:140]

    # contacts from homepage
    emails = [e for e in MAILTO_RE.findall(body)] + MAIL_RE.findall(txt)
    phones = TEL_RE.findall(body) + PHONE_TXT_RE.findall(txt)
    names = NAME_CTX_RE.findall(txt)
    socials = FB_RE.findall(body)
    events = []
    if EVENT_RE.search(txt):
        for m2 in DATE_2026_RE.finditer(txt):
            frag = txt[max(0, m2.start() - 90):m2.end() + 60].strip()
            events.append(frag)
            if len(events) >= 3:
                break

    # impressum / kontakt subpages
    from urllib.parse import urljoin
    sub_urls = []
    for href in IMPRESSUM_LINK_RE.findall(body):
        href = html.unescape(href)
        if href.startswith(("mailto:", "javascript:", "#")):
            continue
        full = urljoin(out["final_url"], href)
        if full not in sub_urls and len(sub_urls) < 3:
            sub_urls.append(full)
    if not sub_urls:
        for cand in ("impressum/", "impressum.html", "impressum.php", "kontakt/", "kontakt.html"):
            sub_urls.append(urljoin(out["final_url"], cand))
            if len(sub_urls) >= 3:
                break
    # event/news subpages (up to 2)
    host = re.sub(r"^https?://(www\.)?", "", out["final_url"]).split("/")[0]
    ev_urls = []
    for href in EVENTPAGE_LINK_RE.findall(body):
        href = html.unescape(href)
        if href.startswith(("mailto:", "javascript:", "#")):
            continue
        if href.startswith("http") and host not in href:
            continue
        full = urljoin(out["final_url"], href)
        if full not in ev_urls and full not in sub_urls and len(ev_urls) < 2:
            ev_urls.append(full)
    for eu in ev_urls:
        try:
            r3 = fetch(eu, timeout=15)
            if r3.status_code < 400:
                t3 = clean_txt(r3.text or "")
                for m3 in DATE_2026_RE.finditer(t3):
                    frag = t3[max(0, m3.start() - 90):m3.end() + 60].strip()
                    events.append(frag)
                    if len(events) >= 6:
                        break
        except Exception:
            pass
        time.sleep(0.15)
    imp_txt_all = ""
    for su in sub_urls:
        try:
            r2 = fetch(su, timeout=18)
            if r2.status_code < 400:
                b2 = r2.text or ""
                t2 = clean_txt(b2)
                imp_txt_all += " || " + t2[:6000]
                emails += MAILTO_RE.findall(b2) + MAIL_RE.findall(t2)
                phones += TEL_RE.findall(b2) + PHONE_TXT_RE.findall(t2)
                names += NAME_CTX_RE.findall(t2)
                if EVENT_RE.search(t2):
                    for m2 in DATE_2026_RE.finditer(t2):
                        frag = t2[max(0, m2.start() - 90):m2.end() + 60].strip()
                        events.append(frag)
                        if len(events) >= 5:
                            break
        except Exception:
            pass
        time.sleep(0.2)

    def norm_email(e):
        e = e.strip().strip(".,;:")
        e = re.sub(r"^%20|^mailto:", "", e)
        return e.lower()
    bad_mail = ("example.", "wixpress", "sentry", "@2x", ".png", ".jpg", "webmaster@", "office@herold", "datenschutzbehoerde", "@dsb.gv.at", "@wko.at", "@ecg.at", "rtr.at", "@ris.")
    emails = [norm_email(e) for e in emails]
    emails = [e for e in dict.fromkeys(emails) if "@" in e and not any(b in e for b in bad_mail) and len(e) < 60][:4]
    def norm_phone(p):
        p = re.sub(r"\s+", " ", p.strip())
        return p.strip(" .-")
    phones = [norm_phone(p) for p in phones]
    phones = [p for p in dict.fromkeys(phones) if len(re.sub(r"\D", "", p)) >= 6][:3]
    nm = []
    for role, name in names:
        name = re.sub(r"\s+", " ", name).strip()
        words = name.split()
        if words[0] in ("Der", "Die", "Das", "Unser", "Ihre", "Ihr", "Wir", "Als", "Am", "Im", "Neue", "Alle", "Zum", "Zur", "Bei", "Auf"):
            continue
        # split words into runs of non-stop words; take best run (2-3 words preferred)
        def is_stop(w):
            ws = w.strip(".,")
            return bool(STREET_SUFFIX.search(ws)) or ws in NAME_STOP or ws in BIZ_WORDS
        runs, cur = [], []
        for w in words:
            if is_stop(w):
                if cur:
                    runs.append(cur)
                cur = []
            else:
                cur.append(w)
        if cur:
            runs.append(cur)
        min_len = 1 if role.startswith("Famil") else 2
        best = next((r for r in runs if 2 <= len(r) <= 3), None) or next((r for r in runs if len(r) >= min_len), None)
        if not best:
            continue
        name = " ".join(best)
        pair = f"{role.strip()}: {name}"
        if pair not in nm:
            nm.append(pair)
    out["contact_names"] = nm[:4]
    out["emails"] = emails
    out["phones"] = phones
    out["socials"] = list(dict.fromkeys(socials))[:3]
    out["events"] = list(dict.fromkeys(events))[:4]
    out["impressum_urls"] = sub_urls
    # short impressum snippet: text around "Impressum" or first sub page text
    imp_sn = ""
    mi = re.search(r"(Impressum|Medieninhaber|Offenlegung)", imp_txt_all)
    if mi:
        imp_sn = imp_txt_all[mi.start():mi.start() + 700]
    elif imp_txt_all:
        imp_sn = imp_txt_all[3:700]
    out["impressum_text"] = imp_sn.strip()
    return out

def main():
    jobs = json.load(open(sys.argv[1]))
    outf = sys.argv[2]
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    done = {}
    if os.path.exists(outf):
        done = {d["key"]: d for d in json.load(open(outf))}
    todo = [j for j in jobs if j["key"] not in done]
    print(f"{len(todo)} to audit ({len(done)} cached)", flush=True)
    lock_n = [0]
    def run(j):
        try:
            res = audit_one(j)
        except Exception as e:
            res = {"key": j["key"], "url": j["url"], "status": "error", "error": repr(e)[:120]}
        done[j["key"]] = res
        lock_n[0] += 1
        if lock_n[0] % 20 == 0:
            json.dump(list(done.values()), open(outf, "w"), ensure_ascii=False)
            print(f"[{lock_n[0]}/{len(todo)}] audited", flush=True)
        return res
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(run, todo))
    json.dump(list(done.values()), open(outf, "w"), ensure_ascii=False, indent=0)
    ok = sum(1 for d in done.values() if d.get("status") == "ok")
    old = sum(1 for d in done.values() if d.get("outdated_score", -9) >= 3)
    print(f"DONE {len(done)} audited, {ok} ok, {old} with score>=3", flush=True)

if __name__ == "__main__":
    main()
