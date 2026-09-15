# -*- coding: utf-8 -*-
"""Inhaltsmodell Die Herzl — alle Angaben aus dieherzl.at (Crawl 15.09.2026).
Nichts erfunden. Bilder sind über ihren Slug referenziert, nie über eine Nummer,
damit Text und Motiv nicht auseinanderlaufen koennen."""

BIZ = dict(
    name="Die Herzl",
    lang="Die Herzl — Altsteirisches Wirtshaus und Weinstube",
    strasse="Prokopigasse 12 / Mehlplatz",
    plz="8010", ort="Graz",
    tel="+43 316 824 300", tel_href="tel:+43316824300",
    mail="office@dieherzl.at",
    web="https://dieherzl.at/",
    zeiten="Montag bis Sonntag und an Feiertagen, 10:00–24:00 Uhr",
    kueche="Küche 10:00–22:00 Uhr",
    mittag="Montag bis Freitag, 11:00–15:00 Uhr",
    chef="Marius Sandu",
    inhaberin="Edith Seitinger",
    gegruendet="1934",
    gruender="Robert Herzl",
)

# --- Speisekarte (Preise woertlich von der bestehenden Seite) ---------------
KARTE = [
 ("Suppen & Eintopf", "Die Herzl trinkt dazu: ein Glas Schilcher vom Langmann", [
   ("Schwammerlsuppe mit Heidensterz", "zubereitet mit Grammeln", "5,80"),
   ("Frittatensuppe", "", "4,80"),
   ("Herzl Festtagssuppe", "Leberknödel, Fleischstrudel und Frittaten mit frischem Gemüse in kräftiger Rindsuppe, frischer Schnittlauch", "5,40"),
   ("Kürbiscremesuppe", "vom Hokkaidokürbis mit Sahnehäubchen, einem Schuss Kernöl und gerösteten Brotwürfeln, Kürbiskerne", "5,60"),
 ], ["kuerbiscremesuppe"]),

 ("Herzhaftes Salatvergnügen", "Wir marinieren unsere Salate mit Apfelessig und Kernöl der Ölmühle Esterer", [
   ("Vogerlsalat", "mit Ei, Speck und Kernöl auf lauwarmem Erdäpfelsalat", "9,90"),
   ("Herzlsalat 2025", "24 Stunden Rind vom Simmentaler Fleckvieh und Avocado in Pankopanade auf Vogerlsalat und Käferbohnen, Wasabi-Kernölmayonnaise", "15,90"),
   ("Vegetarischer Schmankerlsalat", "knusprig gebackene Avocado und Schafskäse in Pankopanade mit Wasabi-Kernölmayonnaise auf Vogerlsalat und Käferbohnen", "15,90"),
   ("Steirischer Backhenderlsalat", "gebackene Hühnerstreifen auf bunten Blattsalaten und Erdäpfelsalat", "15,50"),
   ("Käferbohnensalat", "mit Rettich und Kernöl", "7,90"),
   ("Krautsalat mit Speck", "", "6,90"),
   ("Grüner Salat, Erdäpfelsalat oder Rahmgurkensalat", "", "4,90"),
   ("Gemischter Salat", "", "5,90"),
 ], ["backhenderlsalat"]),

 ("Zur Vorspeise oder nur so zum Achterl", "", [
   ("Zweierlei Aufstrich deftig", "mit Hausbrot, Leberaufstrich und Verhackert", "7,90"),
   ("Zweierlei Aufstrich", "mit Hausbrot, Aufstrich und Käferbohnenaufstrich", "7,90"),
 ], ["brettljause"]),

 ("Die Altbewährten", "", [
   ("½ steirisches Backhenderl", "immer wieder ein Genuss — wir verwenden ausschließlich maisgefütterte Bauernhühner von Kicker", "13,90"),
   ("Rindsgulasch mit Semmel", "Die Herzl trinkt dazu: ein Hausbier", "14,90"),
   ("Rindsgulasch serviert mit Knödel", "Die Herzl trinkt dazu: alternativ ein ZWEITES Glas Hausbier", "17,90"),
   ("Altsteirisches Kalbsbeuschel", "Die Herzl trinkt dazu: ein Puntigamer", "12,90"),
   ("Wiener Schnitzel mit Preiselbeeren", "Die Herzl trinkt dazu: ein Glas Gewürztraminer, Winkler Hermaden", "10,90"),
   ("Steirerschnitzel", "vom Maishenderl. Die Herzl trinkt dazu: einen Spritzer", "11,90"),
   ("Herzhaftes Cordon bleu", "Die Herzl trinkt dazu: einen Schilcherspritzer", "13,90"),
 ], ["roestzwiebeln"]),

 ("Steirische Hauptgerichte", "", [
   ("Lachsforellenfilet vom Grill", "Die Herzl trinkt dazu: ein Glas Sauvignon blanc Jakobi von Gross", "22,90"),
   ("Bauernbratl serviert im Pfandl", "Die Herzl trinkt dazu: ein Glas Blaufränkisch Ried Gfanger von Paul Lehrner", "18,90"),
   ("Herzlpfandl", "Die Herzl trinkt dazu: ein Glas Zweigelt Red Rock", "19,90"),
   ("Burger auf steirisch", "nicht Steirerburger! Die Herzl trinkt dazu: ein großes Mischbier von Gösser", "16,90"),
   ("24 Stunden Rinder-Rippe", "Die Herzl trinkt dazu: ein Glas Blaufränkisch reserve, J. Igler", "20,90"),
   ("Geröstete Leber", "mit Rösterdäpfeln", "12,90"),
   ("Geröstete Kalbsleber", "manchmal röstet unser Küchenchef lieber eine Kalbsleber", "21,90"),
 ], ["rippchen-brett", "nudelpfandl"]),

 ("Steirisch vegetarisch", "", [
   ("Gschmackige Käsespätzle", "Die Herzl trinkt dazu: ein Glas Refugium, Aumann", "14,90"),
   ("Fabians hausgemachte Nudeltaschen", "mit Rucola, frische Parmesanspäne, serviert mit steirischem Rohschinken", "14,90"),
   ("Steirisches Vegichili", "Die Herzl trinkt dazu: ein Glas Rosé, Der Aichinger", "14,90"),
 ], ["kaesespaetzle"]),

 ("Beilagen und Saucen", "", [
   ("Bauernerdäpfel, Süßkartoffeln, Rösterdäpfel, Grillgemüse, Knödel oder Spätzle", "", "4,60"),
   ("Preiselbeeren, Kren, Wasabi-Kernölcreme, Sauerrahm-Knoblauchdip oder Paprikadip", "", "2,60"),
   ("Ketchup, Mayo", "", "0,80"),
 ], []),

 ("Zum Schluß", "Die Herzl trinkt dazu: einen cremigen Cappuccino", [
   ("Steirisches Tiramisu", "mit Äpfeln, Vanille und Zimt, Kürbiskernöl", "7,90"),
   ("Hausgemachter Kaiserschmarren", "natürlich sind auch unsere Zwetschkenröster hausgemacht", "12,90"),
   ("Vanillepudding mit Himbeerröster", "unsere süße Kindheitserinnerung", "6,90"),
   ("Apfelstrudel", "mit Vanillesauce", "6,90"),
   ("Schokoherzen", "", "9,90"),
   ("Arzberger Stollenkäse", "Teller mit Hausbrot — für Käsefreunde", "12,90"),
 ], ["kaiserschmarrn", "kaeseplatte"]),

 ("Edelbrände aus Leitringen", "von Günther Peer", [
   ("Marille, Quitte, Traubenbrand, Williams oder Zwetschke", "2 cl", "4,20"),
   ("Vogelbeer", "2 cl", "5,20"),
   ("Alter Apfel, alte Birne, alte Zwetschke", "2 cl", "5,60"),
   ("Zirbe oder Kräuterzirbe", "2 cl", "3,90"),
 ], []),
]

MITTAG = [("Tagesgericht", "9,90"), ("Menüsuppe", "2,20"),
          ("Menüsalat", "2,20"), ("Tages-Dessert", "2,60")]

LIEFERANTEN = [
 ("Backhenderl", "maisgefütterte Bauernhühner von Kicker"),
 ("Rind, Kalb und Schwein", "Fleisch aus Österreich"),
 ("Schweinefleisch", "Fleischermeister Ehmann, Ligist"),
 ("Wurst und Räucherwaren", "Fleischerei Lamprecht"),
 ("Wild", "zartes Dammwild vom Wildererhof bei St. Stefan im Rosental"),
 ("Bio-Weideganserl", "Familie Meixner bei Pöllau"),
 ("Käse", "Christoph Leitner, Tulwitz"),
 ("Eier aus Bodenhaltung", "Sulmtaler Frischei, Familie Teissl, Heimschuh"),
 ("Erdäpfel, Kraut, Zwiebel, Karotten, Grazer Krauthäuptl", "Friedrich Schlögl, Vasoldsberg"),
 ("Milch und Milchprodukte", "aus Österreich mit dem AMA-Gütesiegel"),
 ("Edelbrände", "Günther Peer, Leitring"),
 ("Wein", "Weißweine aus der Steiermark und Niederösterreich, Rotweine aus dem Burgenland"),
 ("Fruchtsäfte", "von den Winzern oder aus Schlögels Obstgärten"),
]

GUTSCHEINE = [
 ("Backhenderlbuffet", "ab 6 Personen", "ab € 85,20", "backhenderlsalat"),
 ("5-Gänge-Menü", "ab 2 Personen", "ab € 88,00", "rippchen-brett"),
 ("Kulinarik-Gutschein", "für Feinschmecker", "€ 100,00", None),
 ("Kulinarik-Gutschein", "", "€ 50,00", None),
 ("Kulinarik-Gutschein", "", "€ 10,00", None),
]

RAEUME = [
 ("Die Stube", "stube-tafel",
  "Gedeckte Tafel unter Butzenfenstern und Holzvertäfelung — der Raum, in dem seit 1934 gegessen wird."),
 ("Der Stammtisch", "stube-gruen",
  "Runder Tisch, grüne Vorhänge, Vertäfelung: für Runden, die nicht auf die Uhr schauen."),
 ("Das Gewölbe", "gewoelbe",
  "Ein Gewölbe aus dem 17. Jahrhundert, eingedeckt für größere Gesellschaften."),
 ("Der Gastgarten", "gastgarten",
  "Innenhof unter dem Baum, mitten in der Altstadt und trotzdem aus dem Trubel heraus."),
]

PRESSE = [
 ("presse-80jahre", "„Herzl Weinstube: 80 Jahre sind noch nicht genug“"),
 ("presse-graz", "Die Stadtzeitung über das Haus am Mehlplatz"),
 ("presse-1934", "Pressestimmen zur Eröffnung, Grazer Zeitung 1934"),
 ("presse-eroeffnung", "Eröffnung der Weinstube Robert Herzl"),
 ("presse-kulinarik", "Kulinarik-News mit einem Beitrag über das Haus"),
]

GRAZ = [
 ("graz-glockenspiel", "Der Glockenspielplatz — wenige Schritte vom Mehlplatz."),
 ("graz-rathaus", "Das Rathaus mit dem Erzherzog-Johann-Brunnen am Hauptplatz."),
 ("graz-gasse", "Altstadtgassen mit Blumen und schmiedeeisernen Laternen."),
 ("graz-luftbild", "Die roten Dächer der Grazer Altstadt, UNESCO-Weltkulturerbe."),
 ("graz-kirche", "Gotische Kirchenräume, nur ein paar Gassen weiter."),
]
