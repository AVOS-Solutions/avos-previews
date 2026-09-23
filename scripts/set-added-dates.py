#!/usr/bin/env python3
"""Schreibt je Katalogeintrag das Datum, an dem der Preview-Ordner angelegt wurde.

Warum ueberhaupt ein Feld im Katalog: Das API-Image kopiert nur previews/,
previews-neubau/ und die beiden JSON-Kataloge (siehe Dockerfile) -- kein .git. Alle
Dateien tragen dort die COPY-Zeit des Builds, sind also als Datumsquelle wertlos, und
git steht zur Laufzeit nicht zur Verfuegung. Das Datum muss daher aus der Historie in
den Katalog gebacken werden.

Als "hinzugefuegt" gilt der Autor-Zeitpunkt des aeltesten Commits, der eine Datei
unterhalb des Ordners angelegt hat (--diff-filter=A). Spaetere Umbauten desselben
Ordners aendern das Datum nicht.

Aufruf nach dem Anlegen neuer Previews:

    python3 scripts/set-added-dates.py           # nur fehlende Felder ergaenzen
    python3 scripts/set-added-dates.py --force   # alle neu aus der Historie setzen
    python3 scripts/set-added-dates.py --check   # nichts schreiben, nur Luecken melden

--check endet mit Rueckgabewert 1, wenn Eintraege ohne Datum uebrig sind; damit laesst
es sich in eine Pruefung haengen. Ein Eintrag, dessen Ordner noch nicht committet ist,
bekommt kein Datum -- geraten wird hier nichts.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# Katalogdatei -> zugehoeriger Ordner mit den Preview-Sites
KATALOGE = [("businesses.json", "previews"), ("businesses-neubau.json", "previews-neubau")]


def erstanlage_je_ordner() -> dict[tuple[str, str], str]:
    """(wurzel, slug) -> ISO-Datum des aeltesten Commits, der dort etwas angelegt hat.

    Ein einziger git-Aufruf ueber die ganze Historie; --reverse liefert die Commits
    aelteste zuerst, der erste Treffer je Ordner ist damit die Erstanlage.
    """
    roots = [r for _, r in KATALOGE]
    out = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=C %aI", "--name-only", "--reverse", "--", *roots],
        cwd=REPO, capture_output=True, text=True, check=True).stdout
    muster = re.compile(r"(%s)/([^/]+)/" % "|".join(re.escape(r) for r in roots))
    datum = None
    erst: dict[tuple[str, str], str] = {}
    for zeile in out.splitlines():
        if zeile.startswith("C "):
            datum = zeile[2:12]
            continue
        treffer = muster.match(zeile)
        if treffer:
            erst.setdefault((treffer.group(1), treffer.group(2)), datum)
    return erst


def format_wie_vorgefunden(text: str) -> tuple[int, bool]:
    """Einrueckung und abschliessender Zeilenumbruch der vorhandenen Datei.

    Die beiden Kataloge sind unterschiedlich formatiert (ein bzw. zwei Leerzeichen);
    wer das nicht uebernimmt, schreibt die ganze Datei um und macht den Diff unlesbar.
    """
    zeilen = text.split("\n")
    einzug = 2
    for zeile in zeilen[1:]:
        if zeile.strip():
            einzug = len(zeile) - len(zeile.lstrip(" "))
            break
    return einzug, text.endswith("\n")


def main() -> int:
    force = "--force" in sys.argv
    check = "--check" in sys.argv
    erst = erstanlage_je_ordner()

    gesetzt = geaendert = fehlend = 0
    for datei, wurzel in KATALOGE:
        pfad = REPO / datei
        roh = pfad.read_text(encoding="utf-8")
        einzug, endet_mit_umbruch = format_wie_vorgefunden(roh)
        eintraege = json.loads(roh)
        schreiben = False
        for e in eintraege:
            datum = erst.get((wurzel, e["slug"]))
            if datum is None:
                fehlend += 1
                print(f"  ohne Datum: {wurzel}/{e['slug']} (Ordner noch nicht committet?)")
                continue
            alt = e.get("addedOn")
            if alt == datum:
                continue
            if alt is not None and not force:
                continue
            if check:
                fehlend += 1
                print(f"  fehlt: {wurzel}/{e['slug']} -> {datum}")
                continue
            e["addedOn"] = datum
            schreiben = True
            if alt is None:
                gesetzt += 1
            else:
                geaendert += 1
                print(f"  korrigiert: {e['slug']} {alt} -> {datum}")
        if schreiben and not check:
            text = json.dumps(eintraege, ensure_ascii=False, indent=einzug)
            pfad.write_text(text + ("\n" if endet_mit_umbruch else ""), encoding="utf-8")
            print(f"{datei}: geschrieben")

    print(f"neu gesetzt: {gesetzt} | korrigiert: {geaendert} | ohne Datum: {fehlend}")
    return 1 if (check and fehlend) else 0


if __name__ == "__main__":
    raise SystemExit(main())
