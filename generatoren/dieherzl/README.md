# Generator: Die Herzl (Varianten 207–209)

Die drei Herzl-Vorschauen sind nicht von Hand geschrieben, sondern gerendert:
`content.py` hält den Inhalt einmal, `themes.py` die drei Gestaltungen,
`build.py` setzt beides zusammen und schreibt nach `previews/<slug>/`.
Der Generator liegt bewusst ausserhalb von `previews/`, damit er nicht selbst
als Vorschau ausgeliefert wird.

```
python3 build.py          # schreibt 207-dieherzl-stube, 208-…-altstadt, 209-…-gewoelbe
```

## Warum überhaupt ein Generator

Die erste Herzl-Vorschau zeigte neben dem Absatz über das Backhendl ein Dessert.
Ursache war nicht der Text, sondern die Bildablage: die alte Website liefert
`alt="Stacks Image 12096"`, also keine Beschreibung. Wer die Seite baut, ohne die
Fotos gesehen zu haben, verteilt sie zwangsläufig blind.

Deshalb sind die Bilder hier **über Slugs** referenziert (`img('backhenderlsalat')`),
nie über eine Nummer. Der Slug und die Bildunterschrift stehen in `bildliste.txt`
(Kopie von `img/index.txt`) und wurden durch Ansehen jedes einzelnen Fotos
vergeben, Speisenamen gegen die echte Karte abgeglichen. Ein Motiv kann damit
nicht mehr unter einem Text landen, der etwas anderes beschreibt — und ein
falscher Slug bricht den Build, statt still das falsche Bild zu setzen.

## Farben

Abgenommen von dieherzl.at: Logo-Grün `#006e33`, Navigationsbraun `#542112`,
Sandgelb `#e7cd73`. Alle drei Varianten bleiben darin.

## Nicht vorhanden

Die Website hat **kein brauchbares Foto eines ganzen Backhenderls**. Das
nächstliegende Motiv ist der Steirische Backhenderlsalat; die Galerie
„Backhenderlschmaus 2015“ enthält nur private Partyaufnahmen erkennbarer Gäste
und ist dafür nicht verwendbar. Für den Relaunch wäre ein Foto nachzuschießen.
