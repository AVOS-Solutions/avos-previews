# -*- coding: utf-8 -*-
"""Drei eigenstaendige Gestaltungen. Die Farben sind von dieherzl.at abgenommen:
Logo-Gruen #006e33, Navigationsbraun #542112, Sandgelb #e7cd73."""

BASE = """
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:var(--ff-t);font-size:clamp(1rem,.96rem + .2vw,1.09rem);
  line-height:1.65;color:var(--ink);background:var(--bg);overflow-wrap:break-word}
img{max-width:100%;height:auto;display:block}
h1,h2,h3{font-family:var(--ff-h);line-height:1.15;margin:0 0 .5em;font-weight:var(--hw)}
h1{font-size:clamp(2.1rem,1.4rem + 3.1vw,3.7rem)}
h2{font-size:clamp(1.55rem,1.15rem + 1.8vw,2.45rem)}
h3{font-size:clamp(1.12rem,1rem + .5vw,1.35rem)}
p{margin:0 0 1em}
a{color:var(--link)}
a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,summary:focus-visible
  {outline:3px solid var(--fokus);outline-offset:3px;border-radius:2px}
.wrap{width:min(1180px,100% - 2.5rem);margin-inline:auto}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
.skip{position:absolute;left:-9999px;top:0;background:var(--ink);color:var(--bg);padding:.7rem 1rem;z-index:50}
.skip:focus{left:.5rem;top:.5rem}

/* Vorschau-Kennzeichnung */
.vorschau{margin:0;padding:.5rem 1rem;text-align:center;font-size:.79rem;letter-spacing:.03em;
  background:var(--warn-bg);color:var(--warn-fg)}

/* Kopf + Navigation */
.top{background:var(--top-bg);border-bottom:1px solid var(--top-li);position:sticky;top:0;z-index:40}
.top__in{display:flex;align-items:center;gap:1rem;flex-wrap:wrap;padding:.85rem 0}
.marke{display:flex;flex-direction:column;text-decoration:none;color:var(--top-fg);min-width:0}
.marke__n{font-family:var(--ff-h);font-size:1.5rem;line-height:1.1;color:var(--marke)}
.marke__s{font-size:.74rem;letter-spacing:.14em;text-transform:uppercase;color:var(--top-mut)}
.burger{margin-left:auto;background:none;border:1px solid var(--top-li);color:var(--top-fg);
  padding:.45rem .8rem;border-radius:var(--r);font:inherit;font-size:.9rem;cursor:pointer}
#nav{flex-basis:100%}
#nav ul{display:none;margin:.6rem 0 0;padding:0;list-style:none;flex-direction:column;gap:.15rem}
#nav.offen ul{display:flex}
#nav a{display:block;padding:.55rem .2rem;text-decoration:none;color:var(--top-fg);
  border-bottom:1px solid var(--top-li);font-size:.95rem}
#nav a[aria-current]{color:var(--marke);font-weight:700}
@media (min-width:62rem){
  .burger{display:none}
  #nav{flex-basis:auto;margin-left:auto}
  #nav ul{display:flex;flex-direction:row;gap:1.35rem;margin:0}
  #nav a{border:0;padding:.2rem 0;border-bottom:2px solid transparent}
  #nav a:hover{border-bottom-color:var(--marke)}
}

/* Abschnitte */
.s{padding:clamp(2.6rem,1.6rem + 4vw,5rem) 0}
.kopf{max-width:46rem;margin-bottom:2.2rem}
.kopf--breit{max-width:54rem}
.kicker{font-size:.76rem;letter-spacing:.2em;text-transform:uppercase;color:var(--kicker);
  margin:0 0 .6rem;font-weight:700}
.lead{font-size:1.1em;color:var(--lead)}
.muster{font-size:.92rem;color:var(--lead);border-left:3px solid var(--marke);padding-left:.9rem}

.zwei{display:grid;gap:clamp(1.5rem,1rem + 2.4vw,3.2rem);align-items:center}
.zwei>*{min-width:0}
@media (min-width:56rem){
  .zwei{grid-template-columns:1fr 1fr}
  .zwei--kehr .zwei__b{order:-1}
}
.raster{display:grid;gap:1.4rem}
.raster>*{min-width:0}
@media (min-width:38rem){.raster--3,.raster--4{grid-template-columns:repeat(2,1fr)}}
@media (min-width:64rem){.raster--3{grid-template-columns:repeat(3,1fr)}
  .raster--4{grid-template-columns:repeat(4,1fr)}}

/* Bilder mit Bildunterschrift */
.shot{margin:0}
.shot + .shot{margin-top:1.1rem}
.gang__bild{display:grid;gap:1.1rem}
.gang__bild>*{min-width:0}
.shot__f{overflow:hidden;border-radius:var(--r);background:var(--flaeche);box-shadow:var(--sh)}
.shot img{width:100%;aspect-ratio:3/2;object-fit:cover}
.shot figcaption,.beleg figcaption{font-size:.83rem;color:var(--lead);margin-top:.55rem;line-height:1.45}
.beleg{margin:0}
.beleg img{width:100%;aspect-ratio:3/2;object-fit:cover;border-radius:var(--r);background:var(--flaeche);
  box-shadow:var(--sh)}

.kachel,.karte{background:var(--flaeche);border-radius:var(--r);overflow:hidden;box-shadow:var(--sh);
  display:flex;flex-direction:column}
.kachel img,.karte img{width:100%;aspect-ratio:3/2;object-fit:cover}
.kachel__t,.karte__t{padding:1.1rem 1.15rem 1.35rem}
.kachel__t h3,.karte__t h3{margin-bottom:.3rem}
.kachel__t p,.karte__t p{margin:0;font-size:.94rem;color:var(--lead)}

/* Knoepfe */
.btns{display:flex;flex-wrap:wrap;gap:.7rem;margin:1.3rem 0 0}
.btn{display:inline-block;padding:.72rem 1.3rem;border-radius:var(--r);text-decoration:none;
  font-weight:700;font-size:.95rem;border:2px solid transparent;cursor:pointer;font-family:inherit}
a.btn--p,.btn--p{background:var(--btn-p-bg);color:var(--btn-p-fg);border-color:var(--btn-p-bg)}
a.btn--p:hover,.btn--p:hover{background:var(--btn-p-hb);border-color:var(--btn-p-hb);color:var(--btn-p-fg)}
a.btn--s,.btn--s{background:transparent;color:var(--btn-s-fg);border-color:var(--btn-s-bd)}
a.btn--s:hover,.btn--s:hover{background:var(--btn-s-hb);color:var(--btn-s-hf);border-color:var(--btn-s-bd)}

/* Speisekarte */
.sprung{display:flex;flex-wrap:wrap;gap:.5rem}
.sprung a{font-size:.87rem;padding:.4rem .8rem;border:1px solid var(--top-li);border-radius:999px;
  text-decoration:none;color:var(--ink);background:var(--flaeche)}
.sprung a:hover{background:var(--marke);color:var(--btn-p-fg);border-color:var(--marke)}
.gang{padding:clamp(1.4rem,1rem + 1.6vw,2.4rem) 0;border-top:1px solid var(--top-li)}
.gang:first-child{border-top:0;padding-top:0}
.gang__kopf{margin-bottom:1.1rem}
.gang__kopf h3{font-size:clamp(1.35rem,1.1rem + 1vw,1.9rem);margin-bottom:.2rem;color:var(--marke)}
.gang__u{margin:0;font-size:.9rem;color:var(--lead);font-style:italic}
.gang__body{display:grid;gap:1.6rem;align-items:start}
.gang__body>*{min-width:0}
@media (min-width:60rem){.gang__body{grid-template-columns:1fr minmax(15rem,21rem)}}
.gerichte{list-style:none;margin:0;padding:0}
.gerichte li{display:flex;gap:1rem;align-items:baseline;padding:.6rem 0;border-bottom:1px dotted var(--top-li)}
.gerichte li>*{min-width:0}
.ger{flex:1 1 auto}
.ger__n{margin:0;font-weight:700}
.ger__b{margin:.15rem 0 0;font-size:.88rem;color:var(--lead)}
.ger__p{margin:0;font-weight:700;color:var(--marke);white-space:nowrap;flex:0 0 auto}
.preisliste{list-style:none;margin:1rem 0 0;padding:0}
.preisliste li{display:flex;justify-content:space-between;gap:1rem;padding:.5rem 0;
  border-bottom:1px dotted var(--top-li)}
.preisliste li>*{min-width:0}

/* Lieferanten */
.liefer{display:grid;gap:0;margin:2rem 0 0;padding:0}
@media (min-width:48rem){.liefer{grid-template-columns:repeat(2,1fr);column-gap:2.5rem}}
.lief{display:flex;flex-wrap:wrap;gap:.2rem 1rem;padding:.65rem 0;border-bottom:1px dotted var(--top-li);
  min-width:0}
.lief dt{font-weight:700;margin:0;flex:1 1 11rem;min-width:0}
.lief dd{margin:0;flex:1 1 12rem;color:var(--lead);font-size:.93rem;min-width:0}

/* Gutscheine */
.gut{background:var(--flaeche);border-radius:var(--r);overflow:hidden;box-shadow:var(--sh);
  display:flex;flex-direction:column}
.gut img{width:100%;aspect-ratio:3/2;object-fit:cover}
.gut__ziffer{font-family:var(--ff-h);font-size:3.4rem;line-height:1;padding:1.6rem 1.15rem .4rem;
  color:var(--marke)}
.gut__t{padding:1.1rem 1.15rem 1.4rem}
.gut__t h3{margin-bottom:.15rem}
.gut__u{margin:0 0 .5rem;font-size:.88rem;color:var(--lead)}
.gut__p{margin:0;font-weight:700;font-size:1.15rem;color:var(--marke)}
.schritte{margin:1rem 0;padding-left:1.25rem}
.schritte li{margin-bottom:.5rem}

/* Formulare */
.form{margin-top:1.2rem}
.form fieldset{border:0;margin:0;padding:0;min-inline-size:0}
.felder{display:grid;gap:.9rem}
.felder>*{min-width:0}
@media (min-width:34rem){.felder{grid-template-columns:repeat(2,1fr)}}
.feld{margin:0;display:flex;flex-direction:column;gap:.3rem;min-width:0}
.feld--voll{margin-top:.9rem}
.feld label{font-size:.86rem;font-weight:700}
.feld input,.feld textarea{width:100%;max-width:100%;font:inherit;font-size:.95rem;padding:.6rem .7rem;
  border:1px solid var(--feld-bd);border-radius:var(--r);background:var(--feld-bg);color:var(--ink)}
.demo-hinweis{margin:1rem 0 0;padding:.8rem .95rem;border-radius:var(--r);font-size:.9rem;
  background:var(--warn-bg);color:var(--warn-fg)}
.notiz{background:var(--flaeche);border-radius:var(--r);padding:clamp(1.3rem,1rem + 1.5vw,2.4rem);
  box-shadow:var(--sh)}
.zeiten{margin-top:1.4rem;background:var(--flaeche);border-radius:var(--r);padding:1.2rem 1.3rem;
  box-shadow:var(--sh)}
.zeiten h3{margin:.9rem 0 .2rem;font-size:1rem}
.zeiten h3:first-child{margin-top:0}
.zeiten p{margin:0;font-size:.95rem}
.karten{display:grid;gap:1rem;margin-bottom:1.8rem}
.karten>*{min-width:0}
@media (min-width:34rem){.karten{grid-template-columns:repeat(2,1fr)}}
.kart{background:var(--flaeche);border-radius:var(--r);padding:1rem 1.1rem;box-shadow:var(--sh)}
.kart h2{font-size:.82rem;letter-spacing:.14em;text-transform:uppercase;color:var(--kicker);margin-bottom:.35rem}
.kart p{margin:0;font-size:.97rem}
.fliess{max-width:44rem}
.fliess h2{margin-top:1.8rem}

/* Fuss */
.fuss{background:var(--fuss-bg);color:var(--fuss-fg);padding:3rem 0 1.5rem;margin-top:2rem}
.fuss a:not(.btn){color:var(--fuss-link)}
.fuss__g{display:grid;gap:1.8rem}
.fuss__g>*{min-width:0}
@media (min-width:48rem){.fuss__g{grid-template-columns:repeat(3,1fr)}}
.fuss__n{font-family:var(--ff-h);font-size:1.15rem;margin-bottom:.45rem;color:var(--fuss-h)}
.fuss p{margin:0 0 .6rem;font-size:.94rem}
.fuss__l{list-style:none;margin:0;padding:0;font-size:.94rem}
.fuss__l li{margin-bottom:.3rem}
.fuss__k{margin-top:2rem;padding-top:1.2rem;border-top:1px solid var(--fuss-li)}
.fuss__k p{font-size:.82rem;color:var(--fuss-mut);margin:0}

/* Hero */
.hero{position:relative;overflow:hidden}
.hero__in{position:relative;z-index:2}
.hero h1{margin:0 0 .4rem}
.hero__sub{font-size:clamp(1.02rem,.95rem + .5vw,1.25rem);margin:0 0 1.4rem}
table{border-collapse:collapse}
"""

# --------------------------------------------------------------- Variante A
A_CSS = BASE + """
:root{
  --ff-h:'Zilla Slab',Rockwell,'Bitter',Georgia,serif;
  --ff-t:'Lato','Helvetica Neue',Arial,sans-serif;
  --hw:600; --r:6px;
  --ink:#2a1c12; --lead:#5b4632; --bg:#fbf7ea; --flaeche:#fff;
  --marke:#006e33; --kicker:#8a5a1e; --link:#00592a; --fokus:#8a5a1e;
  --sh:0 1px 2px rgba(84,33,24,.09),0 8px 22px rgba(84,33,24,.07);
  --top-bg:#fffdf4; --top-fg:#42301f; --top-mut:#7a6145; --top-li:#e3d6b6;
  --btn-p-bg:#006e33; --btn-p-fg:#fff; --btn-p-hb:#005426;
  --btn-s-fg:#542112; --btn-s-bd:#542112; --btn-s-hb:#542112; --btn-s-hf:#fff;
  --feld-bd:#cfbd93; --feld-bg:#fff;
  --warn-bg:#542112; --warn-fg:#f7e6c4;
  --fuss-bg:#542112; --fuss-fg:#efdfc4; --fuss-h:#f4e7c9; --fuss-link:#f0d79a;
  --fuss-li:#7a3a26; --fuss-mut:#d0b895;
}
.s--band,.s--mittag{background:#f2e7c6}
.s--raeume{background:#efe6d0}
.hero{background:#e7cd73;border-bottom:4px solid #542112}
.hero__in{display:grid;gap:2rem;align-items:center;padding:clamp(2.4rem,1.6rem + 3vw,4.2rem) 0}
.hero__in>*{min-width:0}
@media (min-width:58rem){.hero__in{grid-template-columns:1.05fr .95fr}}
.hero h1{color:#3d1a0f;font-size:clamp(2.2rem,1.3rem + 3.6vw,4rem)}
.hero__sub{color:#4b2916}
.hero__k{font-size:.78rem;letter-spacing:.22em;text-transform:uppercase;color:#6b3a1c;
  font-weight:700;margin:0 0 .7rem}
.hero__b img{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:6px;
  box-shadow:0 10px 30px rgba(61,26,15,.28);border:5px solid #fffdf4}
.gang__kopf{border-left:4px solid #e7cd73;padding-left:.9rem}
"""

# --------------------------------------------------------------- Variante B
B_CSS = BASE + """
:root{
  --ff-h:'Cormorant Garamond','Iowan Old Style',Georgia,serif;
  --ff-t:'Jost','Avenir Next','Segoe UI',system-ui,sans-serif;
  --hw:600; --r:0px;
  --ink:#16130f; --lead:#54504a; --bg:#fff; --flaeche:#f6f4f0;
  --marke:#006e33; --kicker:#006e33; --link:#00592a; --fokus:#006e33;
  --sh:none;
  --top-bg:#fff; --top-fg:#16130f; --top-mut:#6d6862; --top-li:#e0ddd6;
  --btn-p-bg:#006e33; --btn-p-fg:#fff; --btn-p-hb:#00441f;
  --btn-s-fg:#16130f; --btn-s-bd:#16130f; --btn-s-hb:#16130f; --btn-s-hf:#fff;
  --feld-bd:#c9c5bd; --feld-bg:#fff;
  --warn-bg:#e9efe9; --warn-fg:#1d3a27;
  --fuss-bg:#16130f; --fuss-fg:#ddd9d1; --fuss-h:#fff; --fuss-link:#8fd7a8;
  --fuss-li:#3a352e; --fuss-mut:#a8a29a;
}
h1,h2{letter-spacing:-.012em}
h1{font-size:clamp(2.4rem,1.4rem + 4.2vw,4.6rem);font-weight:500}
h2{font-weight:500}
.marke__n{letter-spacing:.01em}
.kachel,.karte,.gut,.notiz,.kart,.zeiten{border:1px solid var(--top-li)}
.shot__f,.beleg img{border:1px solid var(--top-li)}
.s--band{background:#f6f4f0}
.s--raeume,.s--gut{background:#fff}
.s--graz{background:#f6f4f0}
.hero{background:#16130f}
.hero__bg{position:absolute;inset:0;z-index:1}
.hero__bg img{width:100%;height:100%;object-fit:cover;opacity:.46}
.hero__in{padding:clamp(4.5rem,3rem + 8vw,9.5rem) 0;max-width:44rem}
.hero h1{color:#fff}
.hero__sub{color:#e8e4dc}
.hero__k{font-size:.76rem;letter-spacing:.26em;text-transform:uppercase;color:#8fd7a8;
  font-weight:600;margin:0 0 1rem}
.hero .btn--s{color:#fff;border-color:#fff}
.hero .btn--s:hover{background:#fff;color:#16130f}
.gang__kopf h3{font-weight:500}
.sprung a{border-radius:0}
"""

# --------------------------------------------------------------- Variante C
C_CSS = BASE + """
:root{
  --ff-h:'Playfair Display','Iowan Old Style',Georgia,serif;
  --ff-t:'Source Sans 3','Segoe UI',system-ui,sans-serif;
  --hw:700; --r:3px;
  --ink:#f2e6d3; --lead:#c6b49a; --bg:#17100a; --flaeche:#241811;
  --marke:#e0b15f; --kicker:#5ec17f; --link:#e8c27c; --fokus:#e0b15f;
  --sh:0 2px 4px rgba(0,0,0,.4),0 12px 30px rgba(0,0,0,.35);
  --top-bg:#120c07; --top-fg:#eadcc6; --top-mut:#a4907a; --top-li:#3a2a1c;
  --btn-p-bg:#e0b15f; --btn-p-fg:#1a1009; --btn-p-hb:#f0c67c;
  --btn-s-fg:#e8d9bf; --btn-s-bd:#7d6244; --btn-s-hb:#e0b15f; --btn-s-hf:#1a1009;
  --feld-bd:#4a3726; --feld-bg:#1d1309;
  --warn-bg:#2b1d10; --warn-fg:#ecd6ae;
  --fuss-bg:#0e0905; --fuss-fg:#d8c6aa; --fuss-h:#e0b15f; --fuss-link:#e8c27c;
  --fuss-li:#332417; --fuss-mut:#a08a70;
}
.s--band,.s--mittag,.s--graz{background:#1e150d}
.s--raeume{background:#140d07}
.sprung a{background:#241811;border-color:#4a3726;color:#eadcc6}
.sprung a:hover{background:#e0b15f;color:#1a1009;border-color:#e0b15f}
.gerichte li{border-bottom-color:#33261a}
.preisliste li,.lief{border-bottom-color:#33261a}
.gang{border-top-color:#33261a}
.hero{background:#0e0905}
.hero__bg{position:absolute;inset:0;z-index:1}
.hero__bg img{width:100%;height:100%;object-fit:cover;opacity:.38}
.hero__in{padding:clamp(4rem,2.6rem + 7vw,8.5rem) 0;text-align:center;max-width:46rem;
  margin-inline:auto}
.hero h1{color:#f6e8ce}
.hero__sub{color:#d3c0a2}
.hero__k{font-size:.76rem;letter-spacing:.26em;text-transform:uppercase;color:#5ec17f;
  font-weight:700;margin:0 0 .9rem}
.hero__rule{width:4.5rem;height:2px;background:#e0b15f;margin:1.5rem auto 0}
.hero .btns{justify-content:center}
.shot__f,.beleg img,.kachel img,.karte img,.gut img{filter:saturate(1.02)}
"""


def hero_a():
    from build import img, BIZ
    return f"""<section class="hero"><div class="wrap hero__in">
  <div>
    <p class="hero__k">Prokopigasse 12 · Mehlplatz · Graz</p>
    <h1>Das altsteirische Gasthaus</h1>
    <p class="hero__sub">Seit {BIZ['gegruendet']} wird hier steirisch gekocht — Backhenderl, Bauernbratl
       und Kürbiscremesuppe, mitten in der Grazer Altstadt.</p>
    <p class="btns"><a class="btn btn--p" href="reservierung.html">Tisch reservieren</a>
       <a class="btn btn--s" href="speisekarte.html">Speisekarte</a></p>
  </div>
  <div class="hero__b">{img('stube-gruen', eager=True)}</div>
</div></section>"""


def hero_b():
    from build import img, BIZ
    return f"""<section class="hero">
  <div class="hero__bg" aria-hidden="true">{img('gastgarten', eager=True)}</div>
  <div class="wrap hero__in">
    <p class="hero__k">Seit {BIZ['gegruendet']} am Mehlplatz</p>
    <h1>Steirisch essen,<br>wo Graz am ältesten ist</h1>
    <p class="hero__sub">Wirtshaus und Weinstube in einem Haus aus dem 17. Jahrhundert.
       Täglich geöffnet, Küche bis 22 Uhr.</p>
    <p class="btns"><a class="btn btn--p" href="reservierung.html">Tisch reservieren</a>
       <a class="btn btn--s" href="speisekarte.html">Zur Karte</a></p>
  </div>
</section>"""


def hero_c():
    from build import img, BIZ
    return f"""<section class="hero">
  <div class="hero__bg" aria-hidden="true">{img('gewoelbe', eager=True)}</div>
  <div class="wrap hero__in">
    <p class="hero__k">Altsteirische Weinstube · Graz</p>
    <h1>Die Herzl</h1>
    <p class="hero__sub">Gewölbe aus dem 17. Jahrhundert, steirische Küche seit {BIZ['gegruendet']}
       und ein Glas dazu, das auf der Karte gleich mitsteht.</p>
    <p class="btns"><a class="btn btn--p" href="reservierung.html">Tisch reservieren</a>
       <a class="btn btn--s" href="speisekarte.html">Speisekarte</a></p>
    <div class="hero__rule" aria-hidden="true"></div>
  </div>
</section>"""


VARIANTEN = [
  dict(slug="207-dieherzl-stube", css=A_CSS, hero=hero_a,
       claim="Altsteirisches Wirtshaus",
       fonts="https://fonts.googleapis.com/css2?family=Zilla+Slab:wght@400;600;700&family=Lato:wght@400;700&display=swap"),
  dict(slug="208-dieherzl-altstadt", css=B_CSS, hero=hero_b,
       claim="Wirtshaus & Weinstube · Graz",
       fonts="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Jost:wght@400;500;700&display=swap"),
  dict(slug="209-dieherzl-gewoelbe", css=C_CSS, hero=hero_c,
       claim="Weinstube am Mehlplatz",
       fonts="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Source+Sans+3:wght@400;600;700&display=swap"),
]
