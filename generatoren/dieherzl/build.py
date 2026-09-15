# -*- coding: utf-8 -*-
"""Rendert drei gestalterisch eigenstaendige Vorschauen fuer dieherzl.at.

Der Inhalt liegt einmal in content.py, die Bildzuordnung laeuft ausschliesslich
ueber Slugs aus img/index.txt — ein Motiv kann deshalb nie unter einem Text
landen, der etwas anderes beschreibt.
"""
import os, shutil, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import BIZ, KARTE, MITTAG, LIEFERANTEN, GUTSCHEINE, RAEUME, PRESSE, GRAZ

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = f"{HERE}/assets/img"
OUTROOT = "/home/user/avosed/avos-previews/previews"

IMG = {}
for ln in open(f"{ASSETS}/index.txt", encoding="utf-8"):
    f, wh, slug, cap = ln.rstrip("\n").split("\t")
    w, h = wh.split("x")
    IMG[slug] = dict(file=f, w=int(w), h=int(h), cap=cap)

def e(s): return html.escape(s, quote=True)

def img(slug, cls="", eager=False, cap=False):
    """<img> mit echtem Alt-Text aus der geprueften Bildliste."""
    m = IMG[slug]
    a = (f'<img src="img/{m["file"]}" alt="{e(m["cap"])}" width="{m["w"]}" height="{m["h"]}"'
         f'{" " + cls if cls else ""}'
         + (' fetchpriority="high" decoding="async">' if eager else ' loading="lazy" decoding="async">'))
    if cls:
        a = a.replace(f' {cls}', f' class="{cls}"')
    if cap:
        return f'<figure class="shot"><div class="shot__f">{a}</div><figcaption>{e(m["cap"])}</figcaption></figure>'
    return a

NAV = [("index.html", "Start"), ("speisekarte.html", "Speisekarte"),
       ("unser-haus.html", "Unser Haus"), ("feiern.html", "Feiern"),
       ("gutscheine.html", "Gutscheine"), ("reservierung.html", "Reservierung"),
       ("kontakt.html", "Kontakt")]

JSONLD = """{
 "@context":"https://schema.org","@type":"Restaurant",
 "name":"Die Herzl \\u2014 Altsteirisches Wirtshaus und Weinstube",
 "servesCuisine":"Steirisch",
 "address":{"@type":"PostalAddress","streetAddress":"Prokopigasse 12","postalCode":"8010",
            "addressLocality":"Graz","addressRegion":"Steiermark","addressCountry":"AT"},
 "telephone":"+43 316 824 300","email":"office@dieherzl.at","url":"https://dieherzl.at/",
 "openingHours":"Mo-Su 10:00-24:00","priceRange":"\\u20ac\\u20ac"
}"""


def shell(v, fname, title, desc, body, hero=""):
    AKT = ' aria-current="page"'
    nav = "".join(
        f'<li><a href="{h}"{AKT if h == fname else ""}>{t}</a></li>'
        for h, t in NAV)
    return f"""<!doctype html>
<html lang="de-AT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="https://dieherzl.at/">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:locale" content="de_AT">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{v['fonts']}">
<link rel="stylesheet" href="style.css">
<script type="application/ld+json">{JSONLD}</script>
</head>
<body>
<a class="skip" href="#main">Zum Inhalt springen</a>
<p class="vorschau">Unverbindliche Gestaltungs-Vorschau · keine offizielle Website der Herzl Weinstube · erstellt von AVOS Solutions</p>
<header class="top">
  <div class="wrap top__in">
    <a class="marke" href="index.html"><span class="marke__n">Die Herzl</span><span class="marke__s">{v['claim']}</span></a>
    <button class="burger" type="button" aria-expanded="false" aria-controls="nav">Menü</button>
    <nav id="nav" aria-label="Hauptnavigation"><ul>{nav}</ul></nav>
  </div>
</header>
{hero}
<main id="main">
{body}
</main>
<footer class="fuss">
  <div class="wrap fuss__g">
    <div>
      <p class="fuss__n">Die Herzl</p>
      <p>{BIZ['strasse']}<br>{BIZ['plz']} {BIZ['ort']}</p>
      <p><a href="{BIZ['tel_href']}">{BIZ['tel']}</a><br><a href="mailto:{BIZ['mail']}">{BIZ['mail']}</a></p>
    </div>
    <div>
      <p class="fuss__n">Geöffnet</p>
      <p>{BIZ['zeiten']}<br>{BIZ['kueche']}</p>
      <p>Mittagsmenü {BIZ['mittag']}</p>
    </div>
    <div>
      <p class="fuss__n">Seiten</p>
      <ul class="fuss__l">{"".join(f'<li><a href="{h}">{t}</a></li>' for h, t in NAV)}
      <li><a href="impressum.html">Impressum</a></li><li><a href="datenschutz.html">Datenschutz</a></li></ul>
    </div>
  </div>
  <div class="wrap fuss__k">
    <p>Das Bildmaterial dieser Vorschau stammt von der bestehenden Website der Herzl Weinstube.
       Alle Speisen, Preise und Angaben sind von dort übernommen.</p>
  </div>
</footer>
<script>
(function(){{
  var b=document.querySelector('.burger'), n=document.getElementById('nav');
  if(b&&n){{b.addEventListener('click',function(){{
    var o=b.getAttribute('aria-expanded')==='true';
    b.setAttribute('aria-expanded',String(!o)); n.classList.toggle('offen',!o);}});}}
  document.querySelectorAll('form[data-demo]').forEach(function(f){{
    f.addEventListener('submit',function(ev){{ev.preventDefault();
      var m=f.querySelector('.demo-hinweis');
      if(m){{m.hidden=false; m.focus();}}
    }});
  }});
}})();
</script>
</body>
</html>"""


# ---------------------------------------------------------------- Seiteninhalt
def sec(cls, inner, wrap=True):
    o, c = ('<div class="wrap">', '</div>') if wrap else ('', '')
    return f'<section class="{cls}">{o}{inner}{c}</section>'


def anker(t):
    """ASCII-Sprungmarke aus einem Gang-Titel."""
    for a, b in (("ä","ae"),("ö","oe"),("ü","ue"),("ß","ss"),("&","und"),(" ","-")):
        t = t.lower().replace(a, b) if a != " " else t.replace(a, b)
    return "".join(c for c in t.lower() if c.isalnum() or c == "-").strip("-")


def karte_html(v):
    out = []
    for titel, unter, zeilen, bild in KARTE:
        rows = "".join(
            f'<li><div class="ger"><p class="ger__n">{e(n)}</p>'
            + (f'<p class="ger__b">{e(b)}</p>' if b else "")
            + f'</div><p class="ger__p">€&nbsp;{p}</p></li>'
            for n, b, p in zeilen)
        bildteil = ("<div class=\"gang__bild\">"
                    + "".join(img(b, cap=True) for b in bild) + "</div>") if bild else ""
        out.append(f"""<article class="gang" id="{anker(titel)}">
  <div class="gang__kopf"><h3>{e(titel)}</h3>{f'<p class="gang__u">{e(unter)}</p>' if unter else ''}</div>
  <div class="gang__body"><ul class="gerichte">{rows}</ul>{bildteil}</div>
</article>""")
    return "\n".join(out)


def p_index(v):
    hero = v["hero"]()
    body = sec("s s--intro", f"""
<div class="zwei">
  <div class="zwei__t">
    <p class="kicker">Hereinspaziert seit {BIZ['gegruendet']}</p>
    <h2>Das altsteirische Gasthaus im Herzen von Graz</h2>
    <p class="lead">{BIZ['gruender']} eröffnete hier {BIZ['gegruendet']} seine Weinstube, in einem Haus aus dem
       17. Jahrhundert am Mehlplatz. Gekocht wird bis heute steirisch und bodenständig — aus Zutaten,
       die zum allergrößten Teil aus der Umgebung kommen.</p>
    <p>Wir haben Montag bis Sonntag und an Feiertagen geöffnet. Die Räumlichkeiten bieten in ihren
       unterschiedlichen Größen den Rahmen für Zweisamkeit ebenso wie für Familienfeste und Firmenfeiern.</p>
    <p class="btns"><a class="btn btn--p" href="reservierung.html">Tisch reservieren</a>
       <a class="btn btn--s" href="speisekarte.html">Zur Speisekarte</a></p>
  </div>
  <div class="zwei__b">{img('stube-tafel', cap=True)}</div>
</div>""")

    body += sec("s s--band", f"""
<div class="zwei zwei--kehr">
  <div class="zwei__b">{img('backhenderlsalat', cap=True)}</div>
  <div class="zwei__t">
    <p class="kicker">Wofür man herkommt</p>
    <h2>Das steirische Backhenderl</h2>
    <p class="lead">Für unser Backhenderl verwenden wir ausschließlich maisgefütterte Bauernhühner
       von Kicker. Ein halbes steirisches Backhenderl steht mit € 13,90 auf der Karte, der
       Steirische Backhenderlsalat mit gebackenen Hühnerstreifen auf bunten Blattsalaten mit € 15,50.</p>
    <p>Für größere Runden gibt es das Backhenderlbuffet ab sechs Personen — als Gutschein
       ab € 85,20 auch zum Verschenken.</p>
    <p class="btns"><a class="btn btn--p" href="speisekarte.html">Die ganze Karte</a></p>
  </div>
</div>""")

    kacheln = "".join(f"""<article class="kachel">{img(s)}
  <div class="kachel__t"><h3>{e(t)}</h3><p>{e(txt)}</p></div></article>""" for t, s, txt in RAEUME)
    body += sec("s s--raeume", f"""
<div class="kopf"><p class="kicker">Vier Räume</p><h2>Wo Sie bei uns sitzen</h2>
<p class="lead">Stube, Stammtisch, Gewölbe und Gastgarten — jeder Raum hat seine eigene Größe
   und seinen eigenen Ton.</p></div>
<div class="raster raster--4">{kacheln}</div>""")

    mittag = "".join(f'<li><span>{e(n)}</span><span class="ger__p">€&nbsp;{p}</span></li>' for n, p in MITTAG)
    body += sec("s s--mittag", f"""
<div class="zwei">
  <div class="zwei__t">
    <p class="kicker">{BIZ['mittag']}</p>
    <h2>Mittagsmenü zum Selbstzusammenstellen</h2>
    <p>Sie wählen, was Sie brauchen — Gericht, Suppe, Salat und Dessert einzeln kombinierbar.
       Die Zutaten stammen von heimischen Lieferanten, und es ist immer etwas Vegetarisches dabei.</p>
    <ul class="preisliste">{mittag}</ul>
    <p class="btns"><a class="btn btn--s" href="speisekarte.html">Wochenkarte ansehen</a></p>
  </div>
  <div class="zwei__b">{img('kueche-anrichten', cap=True)}</div>
</div>""")

    body += sec("s s--wein", f"""
<div class="zwei zwei--kehr">
  <div class="zwei__b">{img('wein-einschenken', cap=True)}</div>
  <div class="zwei__t">
    <p class="kicker">Weinstube</p>
    <h2>Steirisch im Glas</h2>
    <p>Unsere Weißweine kommen aus der Steiermark und aus Niederösterreich, die Rotweine aus dem
       Burgenland. Zu jedem Gericht auf der Karte steht, was die Herzl dazu trinkt. Die Edelbrände
       brennt Günther Peer in Leitring.</p>
    <p class="btns"><a class="btn btn--p" href="reservierung.html">Platz sichern</a></p>
  </div>
</div>""")
    return shell(v, "index.html",
                 f"Die Herzl — Altsteirisches Wirtshaus und Weinstube in Graz",
                 "Steirische Küche am Grazer Mehlplatz seit 1934: Backhenderl, Mittagsmenüs, "
                 "Stube, Gewölbe und Gastgarten. Prokopigasse 12, 8010 Graz.",
                 body, hero)


def p_speisekarte(v):
    body = sec("s s--kopf", f"""
<div class="kopf kopf--breit">
  <p class="kicker">à la carte</p>
  <h1>Die Herzl Speisekarte</h1>
  <p class="lead">Küchenchef {BIZ['chef']} kocht mit Zutaten aus der Region. Alle Preise in Euro,
     wörtlich von der bestehenden Karte übernommen.</p>
</div>
<nav class="sprung" aria-label="Zu den Gängen">
  {"".join(f'<a href="#{anker(t)}">{e(t)}</a>' for t, _, _, _ in KARTE)}
</nav>""")
    body += sec("s s--karte", karte_html(v))
    body += sec("s s--hinweis", f"""
<div class="notiz">
  <h2>Was noch auf dem Tisch steht</h2>
  <p>Fragen Sie bitte nach der Abendempfehlung — jeden Abend gibt es etwas Besonderes.
     Von Mittwoch bis Sonntag kommen die Schmankerl-Tage dazu, dazu die Wochenempfehlungen.</p>
  <p class="btns"><a class="btn btn--p" href="reservierung.html">Tisch reservieren</a></p>
</div>""")
    return shell(v, "speisekarte.html", "Speisekarte — Die Herzl, Graz",
                 "Die vollständige Karte der Herzl Weinstube: Suppen, Salate, die Altbewährten "
                 "mit dem steirischen Backhenderl, Hauptgerichte, Vegetarisches und Desserts.",
                 body)


def p_haus(v):
    presse = "".join(f'<figure class="beleg">{img(s)}<figcaption>{e(t)}</figcaption></figure>' for s, t in PRESSE)
    liefer = "".join(f'<div class="lief"><dt>{e(a)}</dt><dd>{e(b)}</dd></div>' for a, b in LIEFERANTEN)
    graz = "".join(f'<figure class="beleg">{img(s)}<figcaption>{e(t)}</figcaption></figure>' for s, t in GRAZ)
    body = sec("s s--kopf", f"""
<div class="kopf kopf--breit"><p class="kicker">Seit {BIZ['gegruendet']}</p>
<h1>Unser Haus</h1>
<p class="lead">Ein Wirtshaus in der ältesten Ecke von Graz — und die Menschen, Lieferanten und
   Räume, aus denen es besteht.</p></div>""")
    body += sec("s s--intro", f"""
<div class="zwei">
  <div class="zwei__t">
    <h2>Hereinspaziert seit {BIZ['gegruendet']}</h2>
    <p class="lead">{BIZ['gruender']} eröffnete {BIZ['gegruendet']} am Mehlplatz seine Weinstube.
       Das Haus selbst stammt aus dem 17. Jahrhundert; seine Gewölbe und Stuben sind bis heute
       der Grund, warum hier so unterschiedlich große Runden Platz finden.</p>
    <p>Heute führt {BIZ['inhaberin']} das Haus, in der Küche steht {BIZ['chef']}.</p>
  </div>
  <div class="zwei__b">{img('team', cap=True)}</div>
</div>""")
    body += sec("s s--band", f"""
<div class="kopf"><p class="kicker">Aus dem Archiv</p><h2>Was über uns geschrieben wurde</h2></div>
<div class="raster raster--4">{presse}</div>""")
    body += sec("s s--liefer", f"""
<div class="zwei">
  <div class="zwei__t">
    <p class="kicker">Unser Küchengeheimnis</p>
    <h2>Woher die Zutaten kommen</h2>
    <p class="lead">Für die frische Zubereitung und den Einsatz regionaler Rohstoffe wurden wir mit dem
       AMA-Gastrosiegel ausgezeichnet. Das Siegel verlangt, dass auf der Karte steht, woher Fleisch,
       Milchprodukte, Eier, Obst, Gemüse, Erdäpfel und Wild stammen — und es wird kontrolliert.</p>
  </div>
  <div class="zwei__b">{img('auszeichnung', cap=True)}</div>
</div>
<dl class="liefer">{liefer}</dl>""")
    body += sec("s s--graz", f"""
<div class="kopf"><p class="kicker">Rundherum</p><h2>Die Altstadt vor der Tür</h2>
<p class="lead">Der Mehlplatz liegt mitten im UNESCO-Weltkulturerbe. Vieles, wofür Gäste nach Graz
   kommen, ist von hier aus zu Fuß erreichbar.</p></div>
<div class="raster raster--4">{graz}</div>""")
    return shell(v, "unser-haus.html", "Unser Haus — Die Herzl, Graz",
                 "Die Geschichte der Herzl seit 1934, das Haus aus dem 17. Jahrhundert, das "
                 "AMA-Gastrosiegel und die Lieferanten hinter der Karte.", body)


def p_feiern(v):
    raeume = "".join(f"""<article class="karte">{img(s, cap=False)}
<div class="karte__t"><h3>{e(t)}</h3><p>{e(txt)}</p></div></article>""" for t, s, txt in RAEUME)
    body = sec("s s--kopf", f"""
<div class="kopf kopf--breit"><p class="kicker">Für 2 und mehr</p>
<h1>Feiern in der Herzl</h1>
<p class="lead">Die Räumlichkeiten aus dem 17. Jahrhundert bieten mit ihren unterschiedlichen Größen
   den Rahmen für Zweisamkeit, Familienfeste und Firmenfeiern.</p></div>""")
    body += sec("s s--raeume", f'<div class="raster raster--4">{raeume}</div>')
    body += sec("s s--band", f"""
<div class="zwei">
  <div class="zwei__t">
    <p class="kicker">Platten und Buffets</p>
    <h2>Herzhaftes für die Runde</h2>
    <p class="lead">In der altsteirischen Weinstube gibt es die Klassiker: Platten für zwei oder mehr
       Personen und Buffets für eine gemütliche Speisefolge ganz nach Belieben. Dazu reichen wir unsere
       steirischen Weine — und das Schnapserl für „danach“.</p>
    <p>Unser Küchenchef gestaltet Buffet und Menü auf Wunsch nach Ihren Vorlieben. Weil das Vorlauf
       braucht, bitten wir um eine persönliche Anfrage per Telefon oder E-Mail.</p>
    <p class="btns"><a class="btn btn--p" href="{BIZ['tel_href']}">{BIZ['tel']}</a>
       <a class="btn btn--s" href="mailto:{BIZ['mail']}">{BIZ['mail']}</a></p>
  </div>
  <div class="zwei__b">{img('brettljause', cap=True)}{img('pfanne-deftig', cap=True)}</div>
</div>""")
    body += sec("s s--anfrage", f"""
<div class="zwei zwei--kehr">
  <div class="zwei__b">{img('gewoelbe-gaeste', cap=True)}{img('gaeste-fass', cap=True)}</div>
  <div class="zwei__t">
    <h2>Anfrage für Ihre Feier</h2>
    <p>Sagen Sie uns Anlass, Datum und ungefähre Personenzahl — wir melden uns mit einem Vorschlag.</p>
    {formular(v, 'feier', [('Name', 'text', 'name'), ('E-Mail', 'email', 'mail'),
                           ('Telefon', 'tel', 'tel'), ('Datum', 'date', 'datum'),
                           ('Personen', 'number', 'pers')],
              'Anlass und Wünsche', 'Anfrage senden')}
  </div>
</div>""")
    return shell(v, "feiern.html", "Feiern & Buffets — Die Herzl, Graz",
                 "Stube, Stammtisch, Gewölbe und Gastgarten für Familienfeste und Firmenfeiern, "
                 "dazu Platten und Buffets nach Absprache mit dem Küchenchef.", body)


def p_gutscheine(v):
    g = "".join(f"""<article class="gut">
  {img(s) if s else '<div class="gut__ziffer" aria-hidden="true">€</div>'}
  <div class="gut__t"><h3>{e(t)}</h3>{f'<p class="gut__u">{e(u)}</p>' if u else ''}
  <p class="gut__p">{e(p)}</p></div></article>""" for t, u, p, s in GUTSCHEINE)
    body = sec("s s--kopf", f"""
<div class="kopf kopf--breit"><p class="kicker">Freude schenken</p>
<h1>Herzl-Gutscheine</h1>
<p class="lead">Kulinarik zum Verschenken — vom Zehner bis zum Backhenderlbuffet für die ganze Runde.
   Alle Preise inklusive Steuern und Abgaben.</p></div>""")
    body += sec("s s--gut", f'<div class="raster raster--3">{g}</div>')
    body += sec("s s--band", f"""
<div class="zwei">
  <div class="zwei__t">
    <p class="kicker">In drei Schritten</p>
    <h2>Vom Kauf zum fertigen Geschenk</h2>
    <ol class="schritte">
      <li>Gutschein bestellen — die Gutscheinnummer kommt per E-Mail.</li>
      <li>Vorlage herunterladen: Gutschein im Format A5 quer, Grußkarte in A4 quer.</li>
      <li>Ausdrucken, Nummer und Widmung eintragen, falten — passt in jedes A5-Kuvert.</li>
    </ol>
    <p>Es gibt den Festtagsgutschein für Muttertag, Geburtstag oder Zeugnis, den Genussgutschein für
       Stunden zu zweit oder mit Freunden und die Schöne-Stunden-Gutscheine zum Muttertag und zum
       Weihnachtsfest.</p>
  </div>
  <div class="zwei__b">{img('topfencreme', cap=True)}</div>
</div>""")
    body += sec("s s--anfrage", f"""
<div class="notiz">
  <h2>Gutschein bestellen</h2>
  <p>Wählen Sie Betrag oder Buffet — wir schicken Ihnen die Gutscheinnummer und die Druckvorlage zu.</p>
  {formular(v, 'gutschein', [('Name', 'text', 'gname'), ('E-Mail', 'email', 'gmail'),
                             ('Gewünschter Gutschein', 'text', 'gwahl')],
            'Widmung (optional)', 'Gutschein anfragen')}
</div>""")
    return shell(v, "gutscheine.html", "Gutscheine — Die Herzl, Graz",
                 "Kulinarik-Gutscheine der Herzl Weinstube von € 10 bis € 100, dazu "
                 "Backhenderlbuffet ab 6 Personen und 5-Gänge-Menü ab 2 Personen.", body)


def formular(v, ident, felder, textarea, knopf):
    f = "".join(f"""<p class="feld"><label for="{ident}-{n}">{e(l)}</label>
<input id="{ident}-{n}" name="{n}" type="{t}"{' required' if t in ('text', 'email') else ''}></p>"""
                for l, t, n in felder)
    return f"""<form class="form" data-demo method="post" action="#">
<fieldset><legend class="vh">{e(knopf)}</legend>
<div class="felder">{f}</div>
<p class="feld feld--voll"><label for="{ident}-txt">{e(textarea)}</label>
<textarea id="{ident}-txt" name="txt" rows="4"></textarea></p>
<p class="btns"><button class="btn btn--p" type="submit">{e(knopf)}</button></p>
<p class="demo-hinweis" hidden tabindex="-1" role="status">Vorschau — im Live-Betrieb geht diese
Anfrage direkt an {BIZ['mail']}. Bitte rufen Sie uns bis dahin unter {BIZ['tel']} an.</p>
</fieldset></form>"""


def p_reservierung(v):
    body = sec("s s--kopf", f"""
<div class="kopf kopf--breit"><p class="kicker">Tischreservierung erbeten</p>
<h1>Einen Tisch reservieren</h1>
<p class="lead">Wir haben Montag bis Sonntag und an Feiertagen von 10:00 bis 24:00 Uhr geöffnet,
   die Küche kocht bis 22:00 Uhr. Kommen Sie nach einer Veranstaltung, die länger dauert?
   Reservieren Sie rechtzeitig — bei Bedarf halten wir die Küche für Sie länger offen.</p></div>""")
    body += sec("s s--anfrage", f"""
<div class="zwei">
  <div class="zwei__t">
    <h2>Ihre Reservierung</h2>
    {formular(v, 'res', [('Name', 'text', 'rname'), ('E-Mail', 'email', 'rmail'),
                         ('Telefon', 'tel', 'rtel'), ('Datum', 'date', 'rdatum'),
                         ('Uhrzeit', 'time', 'rzeit'), ('Personen', 'number', 'rpers')],
              'Wunsch (Stube, Gewölbe, Gastgarten …)', 'Reservierung anfragen')}
  </div>
  <div class="zwei__b">
    {img('gastgarten', cap=True)}
    <div class="zeiten">
      <h3>Geöffnet</h3>
      <p>{BIZ['zeiten']}<br>{BIZ['kueche']}</p>
      <h3>Mittagsmenü</h3>
      <p>{BIZ['mittag']}</p>
      <h3>Lieber anrufen?</h3>
      <p><a href="{BIZ['tel_href']}">{BIZ['tel']}</a></p>
    </div>
  </div>
</div>""")
    return shell(v, "reservierung.html", "Reservierung — Die Herzl, Graz",
                 "Tisch reservieren in der Herzl Weinstube am Grazer Mehlplatz: täglich 10:00–24:00 Uhr, "
                 "Küche bis 22:00 Uhr.", body)


def p_kontakt(v):
    body = sec("s s--kopf", f"""
<div class="kopf kopf--breit"><p class="kicker">Prokopigasse 12 / Mehlplatz</p>
<h1>Kontakt und Anfahrt</h1>
<p class="lead">Mitten in der Grazer Altstadt, wenige Schritte vom Glockenspielplatz und vom Hauptplatz.</p></div>""")
    body += sec("s s--kontakt", f"""
<div class="zwei">
  <div class="zwei__t">
    <div class="karten">
      <div class="kart"><h2>Adresse</h2><p>Die Herzl<br>{BIZ['strasse']}<br>{BIZ['plz']} {BIZ['ort']}</p></div>
      <div class="kart"><h2>Telefon</h2><p><a href="{BIZ['tel_href']}">{BIZ['tel']}</a></p></div>
      <div class="kart"><h2>E-Mail</h2><p><a href="mailto:{BIZ['mail']}">{BIZ['mail']}</a></p></div>
      <div class="kart"><h2>Geöffnet</h2><p>{BIZ['zeiten']}<br>{BIZ['kueche']}</p></div>
    </div>
    <h2>Anfahrt</h2>
    <p>Die Prokopigasse ist Fußgängerzone. Von der Herrengasse und vom Hauptplatz sind es wenige
       Minuten zu Fuß; die Straßenbahn hält am Hauptplatz.</p>
    <p class="btns"><a class="btn btn--s" href="https://www.openstreetmap.org/search?query=Prokopigasse%2012%2C%208010%20Graz"
       rel="noopener noreferrer" target="_blank">Route öffnen</a></p>
  </div>
  <div class="zwei__b">{img('eingang-blumen', cap=True)}{img('graz-gasse', cap=True)}</div>
</div>""")
    return shell(v, "kontakt.html", "Kontakt & Anfahrt — Die Herzl, Graz",
                 "Die Herzl, Prokopigasse 12 / Mehlplatz, 8010 Graz. Telefon +43 316 824 300, "
                 "office@dieherzl.at.", body)


def p_recht(v, fname, h1, txt):
    body = sec("s s--kopf", f'<div class="kopf kopf--breit"><h1>{e(h1)}</h1>'
                            f'<p class="muster">Muster-Platzhalter dieser Gestaltungs-Vorschau. '
                            f'Die rechtlich verbindlichen Texte der Herzl Weinstube stehen auf dieherzl.at.</p></div>')
    body += sec("s s--recht", f'<div class="fliess">{txt}</div>')
    return shell(v, fname, f"{h1} — Die Herzl, Graz",
                 f"{h1} dieser unverbindlichen Gestaltungs-Vorschau.", body)


IMPRESSUM = f"""
<h2>Angaben zum Betrieb</h2>
<p>Die Herzl — Altsteirisches Wirtshaus und Weinstube<br>
{BIZ['strasse']}<br>{BIZ['plz']} {BIZ['ort']}, Österreich</p>
<p>Telefon: <a href="{BIZ['tel_href']}">{BIZ['tel']}</a><br>
E-Mail: <a href="mailto:{BIZ['mail']}">{BIZ['mail']}</a></p>
<p>Medieninhaberin: {BIZ['inhaberin']}</p>
<h2>Hinweis zu dieser Seite</h2>
<p>Diese Seite ist eine unverbindliche Gestaltungs-Vorschau von AVOS Solutions und keine offizielle
Website der Herzl Weinstube. Firmenbuchnummer, Gerichtsstand, Kammerzugehörigkeit, Gewerbeordnung
und Aufsichtsbehörde sind hier bewusst nicht angeführt — sie gehören in ein echtes Impressum und
werden beim Relaunch vom Betrieb beigestellt.</p>
<h2>Bildmaterial</h2>
<p>Alle Fotos stammen von der bestehenden Website der Herzl Weinstube und werden ausschließlich
für diese Vorschau verwendet.</p>"""

DATENSCHUTZ = """
<h2>Grundsatz</h2>
<p>Diese Gestaltungs-Vorschau setzt keine Cookies, bindet keine Tracker und keine fremden Karten ein.
Es werden keine Zugriffe ausgewertet.</p>
<h2>Formulare</h2>
<p>Reservierung, Feier-Anfrage und Gutschein-Bestellung sind in dieser Vorschau <strong>Demos ohne
Backend</strong>. Eingaben werden nicht übertragen, nicht gespeichert und nicht weitergegeben — beim
Absenden erscheint nur ein Hinweis.</p>
<h2>Schriften</h2>
<p>Die Schriften werden über Google Fonts geladen. Beim Relaunch lassen sie sich lokal ausliefern,
dann verlässt kein Aufruf den eigenen Server.</p>
<h2>Im Live-Betrieb</h2>
<p>Die echte Datenschutzerklärung nennt Verantwortliche, Rechtsgrundlagen, Speicherdauer,
Auftragsverarbeiter und Betroffenenrechte nach DSGVO. Dieser Text ist ein Muster-Platzhalter
und ersetzt sie nicht.</p>"""


def build(v):
    out = f"{OUTROOT}/{v['slug']}"
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(f"{out}/img", exist_ok=True)
    for f in os.listdir(ASSETS):
        shutil.copy2(f"{ASSETS}/{f}", f"{out}/img/{f}")
    seiten = {
        "index.html": p_index(v),
        "speisekarte.html": p_speisekarte(v),
        "unser-haus.html": p_haus(v),
        "feiern.html": p_feiern(v),
        "gutscheine.html": p_gutscheine(v),
        "reservierung.html": p_reservierung(v),
        "kontakt.html": p_kontakt(v),
        "impressum.html": p_recht(v, "impressum.html", "Impressum", IMPRESSUM),
        "datenschutz.html": p_recht(v, "datenschutz.html", "Datenschutz", DATENSCHUTZ),
    }
    for n, t in seiten.items():
        open(f"{out}/{n}", "w", encoding="utf-8").write(t)
    open(f"{out}/style.css", "w", encoding="utf-8").write(v["css"])
    return out, len(seiten)


if __name__ == "__main__":
    from themes import VARIANTEN
    for v in VARIANTEN:
        out, n = build(v)
        print(f"{v['slug']}: {n} Seiten -> {out}")
