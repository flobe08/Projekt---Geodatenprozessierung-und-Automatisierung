# Highway-Klassen

Diese Datei dokumentiert die gemeinsame Verwendung von OpenStreetMap-Daten in
der Pipeline.

Gemeint sind hier vor allem:

- `highway=*` für Straßen und Wege
- `railway=*` für Schienenwege
- später bei Bedarf auch `waterway=*` für Wasser

Die Einordnung orientiert sich am OpenStreetMap-Wiki.

Quellen:

```text
https://wiki.openstreetmap.org/wiki/DE:Key:highway
https://wiki.openstreetmap.org/wiki/Key:highway
https://wiki.openstreetmap.org/wiki/DE:Key:railway
https://wiki.openstreetmap.org/wiki/Key:railway
```


## Allgemein

### Warum OSM im Projekt verwendet wird

OSM wird in der Pipeline genutzt, weil viele Verkehrs- und Infrastrukturobjekte
dort als Linien mit Attributen vorliegen. Genau diese Linienstruktur ist für
Abstandspuffer, Erschließungsfragen und räumliche Näherungen hilfreich.

Der offizielle Landnutzungsdatensatz enthält zwar ebenfalls Verkehrsflächen,
beschreibt diese aber vor allem als Flächenobjekte. Für einige Analyseschritte
ist OSM deshalb die flexiblere Ergänzung.

### Unterschied zwischen `highway=*` und `railway=*`

- `highway=*` beschreibt Straßen, Wege und andere Landverkehrswege
- `railway=*` beschreibt Schienenwege und Bahn-Infrastruktur

Für Solar sind beide relevant.
Für Wind spielen vor allem Straßen- und Wegeklassen eine Rolle.

### OSM ist eine fachliche Näherung

Wichtig für die Doku:

- OSM ist **kein amtlicher Rechtsdatensatz**
- OSM dient in diesem Projekt als **räumliche Näherung**
- amtliche Planungs- und Schutzdatensätze bleiben die wichtigere
  Entscheidungsgrundlage

Das gilt besonders bei Solar:

- `200 m` nach BauGB
- `500 m` nach EEG

Diese Flächen werden technisch aus OSM-Achsen angenähert, ersetzen aber keine
rechtsverbindliche Einzelfallprüfung.

### Gemeinsames OSM-Skript

Der allgemeine OSM-Download läuft aktuell über:

```text
scripts/1_prepare_data/5_download_osm_network_data.py
```

Das Skript arbeitet mit einem Technologie-Parameter:

- `--technology wind`
- `--technology solar`
- `--technology wasser`

Der Download erfolgt bewusst nicht direkt nur auf die Gemeindegrenze, sondern
mit einem erweiterten Analysekontext.

Aktuell:

```text
1000 m Analysekontext-Buffer
```

Dadurch gehen Verkehrsachsen knapp außerhalb der Gemeinde nicht verloren, wenn
ihre Puffer später innerhalb der Gemeinde wirksam werden.


## Wind

### Warum Straßenklassen bei Wind relevant sind

Für den Wind-Workflow sind OSM-Straßen vor allem für diese Fragen interessant:

- Erschließung
- Straßenpuffer
- Kontext großer Verkehrsachsen
- spätere Unterscheidung zwischen wichtigen Straßen und kleinen Wegen

Gerade deshalb wird `ln_strassenundwegeverkehr` aus der amtlichen Landnutzung
nicht einfach pauschal als Ausschluss behandelt. OSM ist hier feiner, weil
wichtige Straßenklassen getrennt von kleineren Wegen betrachtet werden können.

### Verwendete Straßenklassen für Wind

Aktuell lädt das gemeinsame OSM-Skript für Wind breit alle allgemeinen
Straßen- und Wegeklassen als Rohlayer.

| OSM-Wert | Bedeutung im Wind-Workflow |
| --- | --- |
| `motorway` | sehr wichtige Straßeninfrastruktur |
| `motorway_link` | Anschluss an sehr wichtige Straßen |
| `trunk` | wichtige überregionale Straße |
| `trunk_link` | Anschluss an trunk |
| `primary` | wichtige regionale Straße |
| `primary_link` | Anschluss an primary |
| `secondary` | regionale Straße |
| `secondary_link` | Anschluss an secondary |
| `tertiary` | lokale Verbindungsstraße |
| `tertiary_link` | Anschluss an tertiary |
| `unclassified` | kleinere öffentliche Straße |
| `residential` | Straße im Siedlungsbereich |
| `living_street` | verkehrsberuhigter Bereich |
| `service` | Betriebsweg / Zufahrt |
| `track` | land- oder forstwirtschaftlicher Weg |
| `road` | Straße mit unklarer Klassifikation |

### Welche Klassen im Wind-Ausschlusslayer landen

Für den späteren Wind-Ausschlusslayer werden aktuell vor allem diese größeren
oder fachlich stärkeren Straßenklassen verwendet:

- `motorway`
- `motorway_link`
- `trunk`
- `trunk_link`
- `primary`
- `primary_link`
- `secondary`
- `secondary_link`
- `tertiary`
- `tertiary_link`
- `unclassified`
- `residential`
- `living_street`

Nicht automatisch im Ausschlusslayer:

- `service`
- `track`
- `road`

Diese Klassen bleiben im Rohlayer erhalten, werden aber zunächst nur als
Prüf- oder Kontextinformation verstanden.

### Output für Wind

```text
data/processed/osm_highways/<gemeinde>_osm_highways.gpkg
```

Layer:

```text
analysekontext_<gemeinde>
osm_roads_raw
osm_roads_wind_ausschluss
```


## Solar

### Warum Straßen und Schienen bei Solar relevant sind

Für die Solarpipeline gibt es zwei zentrale räumliche Näherungen:

1. `PV-Förderkulisse 500 m`
   - EEG 2023
   - § 37 Abs. 1 Nr. 2 Buchstabe c

2. `PV-Privilegierung 200 m`
   - BauGB
   - § 35 Abs. 1 Nr. 8 Buchstabe b

Beide beziehen sich auf Flächen entlang von:

- Autobahnen
- Schienenwegen

Zusätzlich werden aber auch weitere Straßenklassen mitgeladen, weil sie für
spätere Sperr- oder Kontextlogik nützlich sein können. Die rechtliche
Pufferlogik nutzt aktuell trotzdem vor allem Autobahnen und Schienen.

### Verwendete Klassen für Solar

Der gemeinsame OSM-Download lädt für Solar ebenfalls breit einen Rohlayer und
zusätzlich die Solar-spezifisch wichtigen Teilmengen.

#### Straßen

- `motorway`
- `motorway_link`
- `trunk`
- `trunk_link`
- `primary`
- `primary_link`
- `secondary`
- `secondary_link`
- `tertiary`
- `tertiary_link`
- `unclassified`
- `residential`
- `living_street`
- `service`
- `track`
- `road`

#### Schiene

- `railway = rail`

### Fachliche Solar-Logik

Für die eigentliche Solar-Pufferlogik sind aktuell besonders wichtig:

- `motorway`
- `motorway_link`
- `railway = rail`

Für einen zusätzlichen Solar-Straßen-Ausschlusslayer werden aktuell vor allem
diese Straßenklassen verwendet:

- `motorway`
- `motorway_link`
- `trunk`
- `trunk_link`
- `primary`
- `primary_link`
- `secondary`
- `secondary_link`
- `tertiary`
- `tertiary_link`
- `unclassified`
- `residential`
- `living_street`

Nicht automatisch im Solar-Ausschlusslayer:

- `service`
- `track`
- `road`

Bezug:

- `500 m` Förderkulisse nach EEG
- `200 m` Privilegierung nach BauGB

Zusätzlich wird im BauGB-Teil später mit dem Attribut `tracks` gearbeitet, um
die strengere Näherung `tracks >= 2` für Schienenwege zu prüfen.

### Wichtiger Hinweis für die Doku

Die Solar-Buffer sind:

- eine **automatisierte räumliche Näherung**
- keine rechtsverbindliche Einzelfallprüfung

### Output für Solar

```text
data/processed/osm_transport/<gemeinde>_osm_transport.gpkg
```

Layer:

```text
analysekontext_<gemeinde>
osm_roads_raw
osm_roads_solar_ausschluss
osm_strassen_<gemeinde>
osm_autobahnen_<gemeinde>
osm_schienenwege_<gemeinde>
```

Hinweis:

- `osm_roads_raw` ist der breite gemeinsame Rohlayer.
- `osm_roads_solar_ausschluss` ist der kleinere technologiebezogene
  Straßen-Ausschlusslayer.
- `osm_strassen_<gemeinde>` ist aktuell vor allem ein zusätzlicher
  Kontext- und Prüflayer.
- Die eigentliche 200-m- und 500-m-Logik arbeitet in der Solarpipeline
  gezielt mit `osm_autobahnen_<gemeinde>` und `osm_schienenwege_<gemeinde>`.


## Wasser

### Aktueller Stand

Für Wasser ist OSM derzeit noch nicht der wichtigste Fachdatenblock.

Später könnten interessant werden:

- Straßen für Erschließung und Zugang
- Brücken
- wasserbezogene Infrastruktur
- eventuell `waterway=*`

Aktuell wird das gemeinsame OSM-Skript für Wasser vor allem als vorbereitender
Kontextlayer verstanden.

Output:

```text
analysekontext_<gemeinde>
osm_roads_raw
osm_roads_wasser_ausschluss
```


## Prüfung in QGIS

Allgemeine Sichtprüfung:

1. OSM-Layer laden
2. OpenStreetMap-Basiskarte hinzufügen
3. Gemeindegrenze laden
4. auf die Gemeinde zoomen
5. prüfen, ob die Linien zur Basiskarte passen
6. prüfen, ob der Analysekontext fachlich sinnvoll gewählt ist

Attributprüfung:

1. Attributtabelle öffnen
2. Felder wie `highway`, `railway`, `tracks`, `name` prüfen
3. nach Klassen filtern oder kategorisieren

So wird sichtbar, ob die wichtigen OSM-Klassen korrekt geladen wurden und ob
sie fachlich zur jeweiligen Technologie passen.
