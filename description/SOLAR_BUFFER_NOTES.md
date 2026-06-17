# Solar-Buffer-Notizen

## Ziel der Solar-Pipeline

Für die Solar-Pipeline werden zwei räumliche Randstreifen erzeugt:

1. `PV-Förderkulisse 500 m`
2. `PV-Privilegierung 200 m`

Beide Layer sind automatisierte räumliche Näherungen auf Basis von
OpenStreetMap-Daten und stellen keine abschließende Genehmigungsprüfung dar.

## Alternative amtliche Referenz zur Verifikation

Alternativ zu den selbst erzeugten Bufferzonen kann in QGIS auch der amtliche
Solar-Dienst des Energieatlas Bayern als Referenz eingebunden werden:

- [PV-Freiflächenkulissen / Planungsgrundlagen Solar](https://www.lfu.bayern.de/gdi/wms/energieatlas/planungsgrundlagen_solar)

Relevant sind dort unter anderem diese Layer:

- `PV-Förderkulisse 500 m Randstreifen (EEG)`
- `PV-Privilegierung 200 m Randstreifen (BauGB)`

Wichtig für die Methodik:

- Diese amtlichen Layer werden als WMS bereitgestellt.
- WMS-Layer eignen sich vor allem für die Visualisierung.
- Sie lassen sich schlechter als strukturierte Vektordaten automatisiert
  weiterverarbeiten, verschneiden oder attributbasiert analysieren.

Deshalb erzeugt die Pipeline eigene 200-m- und 500-m-Bufferzonen aus
OSM-Verkehrsdaten. Die amtlichen WMS-Layer eignen sich aber gut zur visuellen
Verifikation.

## Rechtlicher Hintergrund

### 1. PV-Privilegierung 200 m

Rechtsgrundlage:

- `Paragraf 35 Abs. 1 Nr. 8 Buchstabe b BauGB`

Inhalt:

Freiflächen-Photovoltaikanlagen können im Außenbereich privilegiert sein,
wenn sie auf einer Fläche längs von Autobahnen oder Schienenwegen des
übergeordneten Netzes mit mindestens zwei Hauptgleisen liegen und höchstens
200 m vom äußeren Rand der Fahrbahn entfernt sind.

### 2. PV-Förderkulisse 500 m

Rechtsgrundlage:

- `Paragraf 37 Abs. 1 Nr. 2 Buchstabe c EEG 2023`

Inhalt:

Die EEG-Förderkulisse umfasst unter anderem Flächen längs von Autobahnen oder
Schienenwegen, wenn die Freiflächenanlage in einer Entfernung von bis zu
500 m vom äußeren Rand der Fahrbahn errichtet werden soll.

## Umgesetzte OSM-Näherung in der Pipeline

### 500 m EEG-Buffer

Für den 500-m-Buffer wird diese breite Näherung verwendet:

```text
highway = motorway
oder
highway = motorway_link
oder
railway = rail
```

### 200 m BauGB-Buffer

Für den 200-m-Buffer wird diese bewusst einfache Näherung verwendet:

```text
highway = motorway
oder
highway = motorway_link
oder (
  railway = rail
  und tracks >= 2
)
```

Das bedeutet:

- Autobahnen werden immer berücksichtigt.
- Schienenwege werden für den 200-m-Buffer nur berücksichtigt, wenn in OSM
  explizit `tracks >= 2` gepflegt ist.

## Wichtige methodische Einschränkung

Die Bedingung

```text
mindestens zwei Hauptgleise
```

kann aus OSM nicht rechtssicher vollständig geprüft werden. Die Pipeline nutzt
daher nur das Attribut `tracks >= 2`.

Geeignete Formulierung für die Arbeit:

> Für Schienenwege konnte die Bedingung "mindestens zwei Hauptgleise" aus
> OSM-Daten nicht vollständig rechtsverbindlich automatisiert geprüft werden.
> In der Pipeline wurde daher eine vereinfachte OSM-Näherung über das Attribut
> `tracks >= 2` verwendet. Der 200-m-Buffer stellt deshalb eine vereinfachte
> räumliche Näherung dar.

## Warum ein Analysekontext nötig ist

Für OSM-basierte Buffer- und Distanzanalysen wäre ein harter Zuschnitt direkt
an der Gemeindegrenze fachlich zu eng.

Beispiel:

- Eine Bahnlinie kann knapp außerhalb von Drachselsried verlaufen.
- Ihr 200-m- oder 500-m-Puffer kann trotzdem in die Gemeinde hineinreichen.
- Würde die Bahnlinie schon beim Download an der Gemeindegrenze abgeschnitten,
  würde dieser relevante Randstreifen verloren gehen.

Deshalb arbeitet die Pipeline mit einem **erweiterten Analysekontext** um die
Gemeinde herum. Erst die finalen 200-m- und 500-m-Buffer werden anschließend
exakt auf die Gemeinde zugeschnitten.

Aktuell wird dafür ein Kontext-Buffer von `1000 m` verwendet.

## Was im Output gespeichert wird

Die Solardatei enthält mehrere Layer, damit die Herleitung nachvollziehbar
bleibt:

- `analysekontext_<gemeinde>`
- `solar_corridor_autobahnen_<gemeinde>`
- `solar_corridor_schienenwege_<gemeinde>`
- `pv_verkehrsachsen_500m_<gemeinde>`
- `pv_verkehrsachsen_200m_<gemeinde>`
- `pv_förderkulisse_500m_<gemeinde>`
- `pv_privilegierung_200m_<gemeinde>`

Damit kann später in QGIS nachvollzogen werden:

- welcher erweiterte Analysekontext für den OSM-Download verwendet wurde
- welche Linien für 500 m benutzt wurden
- welche strengere Teilmenge für 200 m über `tracks >= 2` benutzt wurde
- wie daraus die finalen, auf die Gemeinde zugeschnittenen Pufferzonen
  entstanden sind

## Wie die Solar-Daten sinnvoll validiert werden

Wenn eine Gemeinde selbst keine Autobahn oder Schiene enthält, ist das kein
Problem. Dann wird nicht die reine Gemeindegeometrie geprüft, sondern:

1. `analysekontext_<gemeinde>`
2. `solar_corridor_autobahnen_<gemeinde>` und `solar_corridor_schienenwege_<gemeinde>`
3. `pv_förderkulisse_500m_<gemeinde>` und `pv_privilegierung_200m_<gemeinde>`

So lässt sich kontrollieren:

- ob die Achsen im erweiterten Umfeld korrekt geladen wurden
- ob daraus sinnvolle Buffer entstehen
- ob die finalen Buffer korrekt an der Gemeindegrenze abgeschnitten wurden

Für Drachselsried ist besonders der 500-m-Fall wichtig, weil relevante
Verkehrsachsen außerhalb der Gemeinde liegen können, ihr Buffer aber trotzdem
in die Gemeinde hineinreicht.

## Formulierung für die Arbeit

> Für die Solar-Potenzialanalyse wurden zwei Randstreifen modelliert. Der
> 200-m-Randstreifen orientiert sich an Paragraf 35 Abs. 1 Nr. 8 Buchstabe b
> BauGB und bildet die bauplanungsrechtliche Privilegierung von
> Freiflächen-Photovoltaikanlagen entlang von Autobahnen und bestimmten
> Schienenwegen näherungsweise ab. Für Schienenwege wurde dazu in OSM die
> vereinfachte Bedingung `tracks >= 2` verwendet. Der 500-m-Randstreifen
> orientiert sich an Paragraf 37 Abs. 1 Nr. 2 Buchstabe c EEG 2023 und
> beschreibt eine förderrechtlich relevante Flächenkulisse entlang von
> Autobahnen und Schienenwegen. Beide Randstreifen wurden aus OSM-
> Verkehrsdaten abgeleitet und stellen keine rechtsverbindliche Prüfung dar.
