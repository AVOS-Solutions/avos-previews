#!/usr/bin/env python3
"""Phase A: crawl herold.at branch listings for Wien/NÖ/OÖ/Steiermark,
collect business detail pages incl. website, phone, email, address."""
import json, os, re, random, sys, time, html
import requests

OUT = os.path.dirname(os.path.abspath(__file__))
S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "de-AT,de;q=0.9",
})
S.verify = "/root/.ccr/ca-bundle.crt"

REGIONS = {
    "Wien": "wien",
    "Niederösterreich": "nieder%C3%B6sterreich",
    "Oberösterreich": "ober%C3%B6sterreich",
    "Steiermark": "steiermark",
}

# slug -> human category
BRANCHES = {
    "gasthaus-u-gasthof": "Gasthaus / Gasthof",
    "restaurant": "Restaurant",
    "kaffeehaus": "Kaffeehaus / Café",
    "kaffeekonditorei": "Konditorei / Café",
    "heuriger-buschenschank": "Heuriger / Buschenschank",
    "weinbau": "Weinbau / Winzer",
    "weinstuben": "Weinstube / Vinothek",
    "fleischhauereien": "Fleischerei",
    "hotel": "Hotel / Gasthof",
    "friseur": "Friseur",
    "kosmetikinstitut": "Kosmetikinstitut",
    "tischlerei": "Tischlerei",
    "installateur": "Installateur (HKLS)",
    "elektriker": "Elektrotechnik",
    "maler-anstreicher-u-lackierer": "Malerei",
    "dachdecker": "Dachdeckerei",
    "spenglerei": "Spenglerei",
    "schlosserei": "Schlosserei / Metallbau",
    "zimmereien": "Zimmerei / Holzbau",
    "steinmetz": "Steinmetz",
    "hafnereien": "Hafner / Kachelöfen",
    "glaserei": "Glaserei",
    "schneidereien": "Schneiderei",
    "textilreinigung": "Textilreinigung",
    "fahrschule": "Fahrschule",
    "physiotherapie": "Physiotherapie",
    "optiker": "Optiker",
    "uhrmacher": "Uhrmacher / Juwelier",
    "fotograf": "Fotostudio",
    "buchhandlungen": "Buchhandlung",
    "imkerei": "Imkerei",
    "fahrradreparatur": "Fahrradwerkstatt",
    "drechslereien": "Drechslerei",
    "bar-cafe": "Bar / Café",
    "b%C3%A4ckereien": "Bäckerei",
    "baeckereien": "Bäckerei",
    "schuhreparatur": "Schuhmacher",
    "blumenhandel": "Blumenhandel",
    "g%C3%A4rtnerei": "Gärtnerei",
    "kfz-werkst%C3%A4tten": "KFZ-Werkstätte",
    "pension": "Pension",
    "privatzimmervermietung": "Privatzimmer / Pension",
    "fu%C3%9Fpflegeinstitute": "Fußpflege",
    "sattlerei": "Sattlerei",
    "tapezierer-u-dekorateure": "Tapezierer / Raumausstattung",
    "kfz-reparatur": "KFZ-Werkstätte",
    "massage": "Massage-Institut",
    "heilmassage": "Heilmassage",
    "pension-privatzimmer": "Pension",
    "reiseb%C3%BCro": "Reisebüro",
    "steuerberater": "Steuerberatung",
    "eisenwaren": "Eisenwaren / Fachhandel",
    "catering": "Catering / Partyservice",
    "partyservice": "Catering / Partyservice",
    "nagelstudio": "Nagelstudio",
    "restaurant-italienisch": "Restaurant",
    "restaurant-griechisch": "Restaurant",
    "restaurant-chinesisch": "Restaurant",
    "restaurant-asiatisch": "Restaurant",
    "restaurant-balkan": "Restaurant",
    "autohandel": "Autohaus / KFZ-Handel",
    "baumschulen": "Baumschule / Gärtnerei",
    "fischzucht": "Fischzucht / Direktvermarktung",
    "ab-hof-verkauf": "Ab-Hof-Verkauf / Hofladen",
}

MAX_PAGES = 8          # listing pages per branch x region
DETAIL_QUOTA = 100000  # detail fetches per branch x region (all)
DELAY = (0.45, 0.9)

def get(url, tries=5):
    for i in range(tries):
        try:
            r = S.get(url, timeout=30)
            if r.status_code == 200:
                return r.text
            if r.status_code == 404:
                return None
            if r.status_code in (429, 403, 503):
                time.sleep(4 * (i + 1))
                continue
            return None
        except requests.RequestException:
            time.sleep(1.5 * (i + 1) + random.random())
    return None

DETAIL_RE = re.compile(r'href="(/gelbe-seiten/([^"/]+)/([A-Za-z0-9]{4,8})/([^"/]+)/)"\s+aria-label="([^"]+?)\s*anzeigen"')

def crawl_listings():
    cands = {}
    n_req = 0
    for slug, cat in BRANCHES.items():
        for region, rslug in REGIONS.items():
            found_before = len(cands)
            for page in range(1, MAX_PAGES + 1):
                url = f"https://www.herold.at/gelbe-seiten/{rslug}/{slug}/"
                if page > 1:
                    url += f"seite/{page}/"
                t = get(url)
                n_req += 1
                if t is None:
                    break
                hits = DETAIL_RE.findall(t)
                for path, ort, bid, bslug, label in hits:
                    if bid not in cands:
                        cands[bid] = {
                            "id": bid, "detail": "https://www.herold.at" + path,
                            "ort_slug": ort, "name": html.unescape(label).strip(),
                            "category": cat, "region": region, "branch": slug,
                        }
                if len(hits) < 25:
                    break
                time.sleep(random.uniform(*DELAY))
            print(f"[list] {slug} {region}: +{len(cands)-found_before} (total {len(cands)}, req {n_req})", flush=True)
            time.sleep(random.uniform(*DELAY))
    return list(cands.values())

WEB_RE = re.compile(r'href="(https?://(?:www\.)?[a-z0-9äöü.-]+\.[a-z]{2,6}(?:/[^"]*)?)"[^>]*>')
TEL_RE = re.compile(r'href="tel:([^"]+)"')
MAIL_RE = re.compile(r'href="mailto:([^"?]+)')
ADDR_RE = re.compile(r'streetAddress"\s+content="([^"]*)".{0,400}?postalCode"\s+content="([^"]*)".{0,200}?addressLocality"\s+content="([^"]*)"', re.S)
ADDR_RE2 = re.compile(r'postalCode"\s+content="([^"]*)"')
BAD_HOSTS = ("herold", "mktgcdn", "ksv.at", "google", "facebook", "instagram", "youtube", "twitter", "linkedin", "tiktok", "arztsuche24", "tailwindcss", "consentmanager", "wko.at", "schema.org", "w3.org", "willhaben", "firmenabc", "justiz", "wkoecg", "apple.com", "yext", "gstatic", "booking.com", "tripadvisor")

RATING_RE = re.compile(r'aria-label="Wurde mit ([0-9,.]+) von 5')
REVCOUNT_RE = re.compile(r'(\d+)\s*Bewertung(?:en)?')
REVIEW_SNIP_RE = re.compile(r'"reviewBody"\s*:\s*"([^"]{10,220})')
REVDATE_RE = re.compile(r'"datePublished"\s*:\s*"([0-9-]{8,10})')

def parse_detail(txt):
    d = {}
    mr = RATING_RE.search(txt)
    if mr:
        try:
            d["rating"] = float(mr.group(1).replace(",", "."))
        except ValueError:
            pass
    mc = REVCOUNT_RE.search(txt)
    if mc:
        d["review_count"] = int(mc.group(1))
    snips = REVIEW_SNIP_RE.findall(txt)
    if snips:
        d["review_snippets"] = [html.unescape(s).replace("\\n", " ").strip()[:200] for s in snips[:2]]
    dates = REVDATE_RE.findall(txt)
    if dates:
        d["last_review_date"] = max(dates)
    webs = []
    for u in WEB_RE.findall(txt):
        low = u.lower()
        if any(b in low for b in BAD_HOSTS):
            continue
        if low.endswith((".jpg", ".png", ".pdf", ".css", ".js")):
            continue
        webs.append(u.split("?")[0].rstrip('"'))
    # keep order, dedup
    seen = set(); ws = []
    for w in webs:
        k = re.sub(r"^https?://(www\.)?", "", w).rstrip("/")
        if k not in seen:
            seen.add(k); ws.append(w)
    if ws:
        d["website"] = ws[0]
        if len(ws) > 1:
            d["website_alt"] = ws[1:3]
    tels = list(dict.fromkeys(TEL_RE.findall(txt)))
    if tels:
        d["phone"] = html.unescape(tels[0]).strip()
    mails = list(dict.fromkeys(MAIL_RE.findall(txt)))
    if mails:
        d["email"] = html.unescape(mails[0]).strip()
    m = ADDR_RE.search(txt)
    if m:
        d["street"], d["zip"], d["city"] = (html.unescape(x).strip() for x in m.groups())
    else:
        m2 = ADDR_RE2.search(txt)
        if m2:
            d["zip"] = m2.group(1)
    return d

def main():
    lf = os.path.join(OUT, "herold_candidates.json")
    if os.path.exists(lf):
        cands = json.load(open(lf))
        print(f"loaded {len(cands)} candidates from cache", flush=True)
    else:
        cands = crawl_listings()
        json.dump(cands, open(lf, "w"), ensure_ascii=False, indent=1)
        print(f"listing crawl done: {len(cands)} candidates", flush=True)

    # detail fetches with per branch x region quota
    detf = os.path.join(OUT, "herold_details.json")
    details = json.load(open(detf)) if os.path.exists(detf) else {}
    random.seed(42)
    by_bucket = {}
    for c in cands:
        by_bucket.setdefault((c["branch"], c["region"]), []).append(c)
    order = []
    for bucket, items in by_bucket.items():
        random.shuffle(items)
        order.extend(items[:DETAIL_QUOTA])
    random.shuffle(order)
    order = [c for c in order if c["id"] not in details]
    print(f"fetching {len(order)} detail pages", flush=True)
    from concurrent.futures import ThreadPoolExecutor
    n = [0]
    def work(c):
        t = get(c["detail"])
        if t is None:
            details[c["id"]] = {"error": "fetch_failed"}
        else:
            details[c["id"]] = parse_detail(t)
        n[0] += 1
        if n[0] % 100 == 0:
            json.dump(dict(details), open(detf, "w"), ensure_ascii=False)
            got = sum(1 for v in details.values() if v.get("website"))
            print(f"[detail] {n[0]}/{len(order)} fetched, {got} with website", flush=True)
        time.sleep(random.uniform(*DELAY))
    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(work, order))
    json.dump(details, open(detf, "w"), ensure_ascii=False)
    got = sum(1 for v in details.values() if v.get("website"))
    print(f"DONE details: {len(details)} fetched, {got} with website", flush=True)

if __name__ == "__main__":
    main()
