#!/usr/bin/env python3
"""Fetch street addresses for final herold leads whose details lack one,
and derive addresses for bestand leads from impressum text.
Writes herold_addresses.json {candidate_id: {street, zip, city}}."""
import json, os, re, sys, time, random, html
import requests

SC = os.path.dirname(os.path.abspath(__file__))
S = requests.Session()
S.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"})
S.verify = "/root/.ccr/ca-bundle.crt"

ST_RE = re.compile(r'streetAddress"(?:\s+content=|\s*:\s*)"([^"]{3,80})"')
ZIP_RE = re.compile(r'postalCode"(?:\s+content=|\s*:\s*)"(\d{4})"')
CITY_RE = re.compile(r'addressLocality"(?:\s+content=|\s*:\s*)"([^"]{2,60})"')

def get(url, tries=4):
    for i in range(tries):
        try:
            r = S.get(url, timeout=25)
            if r.status_code == 200:
                return r.text
            if r.status_code in (429, 503):
                time.sleep(3 * (i + 1)); continue
            return None
        except requests.RequestException:
            time.sleep(1.5 * (i + 1))
    return None

def main():
    leads = json.load(open(os.path.join(SC, "leads_full.json")))
    cands = {c["id"]: c for c in json.load(open(os.path.join(SC, "herold_candidates.json")))}
    v1p = os.path.join(SC, "herold_candidates_v1.json")
    if os.path.exists(v1p):
        for c in json.load(open(v1p)):
            cands.setdefault(c["id"], c)
    outf = os.path.join(SC, "herold_addresses.json")
    addr = json.load(open(outf)) if os.path.exists(outf) else {}
    todo = []
    for l in leads:
        if l["source"] != "herold":
            continue
        cid = l["slug"].split("-")[1]
        if cid in addr:
            continue
        if l.get("address") and re.search(r"[a-zäöü]\s*\d", (l["address"] or "").lower()):
            continue  # already has street-number style address
        if cid in cands:
            todo.append((cid, cands[cid]["detail"]))
    print(f"{len(todo)} detail pages to re-fetch for addresses", flush=True)
    for i, (cid, url) in enumerate(todo):
        t = get(url)
        if t:
            d = {}
            m = ST_RE.search(t)
            if m: d["street"] = html.unescape(m.group(1)).strip()
            m = ZIP_RE.search(t)
            if m: d["zip"] = m.group(1)
            m = CITY_RE.search(t)
            if m: d["city"] = html.unescape(m.group(1)).strip()
            addr[cid] = d
        else:
            addr[cid] = {}
        if (i + 1) % 50 == 0:
            json.dump(addr, open(outf, "w"), ensure_ascii=False)
            print(f"[{i+1}/{len(todo)}]", flush=True)
        time.sleep(random.uniform(0.35, 0.7))
    json.dump(addr, open(outf, "w"), ensure_ascii=False)
    got = sum(1 for v in addr.values() if v.get("street"))
    print(f"DONE: {len(addr)} fetched, {got} with street", flush=True)

if __name__ == "__main__":
    main()
