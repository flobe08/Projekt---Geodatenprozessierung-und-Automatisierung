# OSM-Highway-Klassen

Diese Datei dokumentiert, welche OpenStreetMap-Werte aus `highway=*` im
Wind-Workflow verwendet werden.

Die Einordnung orientiert sich am OpenStreetMap-Wiki. Der Schlüssel
`highway=*` beschreibt Straßen, Wege und andere Verkehrswege. Der Wert gibt
die Funktion oder Hauptnutzung des Weges an.

Quellen:

```text
https://wiki.openstreetmap.org/wiki/DE:Key:highway
https://wiki.openstreetmap.org/wiki/Key:highway
```

## Warum OSM-Straßen verwendet werden

Der offizielle Landnutzungsdatensatz enthält bereits Verkehrsflächen. Diese
Daten beschreiben aber vor allem Flächen. Für den Wind-Workflow sind
OSM-Straßen trotzdem wichtig, weil sie als Linienlayer vorliegen und das Feld
`highway` enthalten.

Dadurch können später unterschiedliche Abstandspuffer erzeugt werden:

```text
primary / secondary / tertiary -> größere Puffer
service / track -> kleinere Puffer oder Erschließungsprüfung
```

Der OSM-Straßenlayer ist deshalb nicht nur doppelt zur Landnutzung, sondern
ein eigener Eingangslayer für Straßenpuffer und Erschließungsfragen.

## Prüfung in QGIS

Der erzeugte Straßenlayer liegt hier:

```text
data/processed/osm_highways/<gemeinde>_osm_highways.gpkg
```

Layer:

```text
osm_roads
```

Für Drachselsried:

```text
data/processed/osm_highways/drachselsried_osm_highways.gpkg
```

Sichtprüfung:

1. `osm_roads` in QGIS laden.
2. OpenStreetMap als Basiskarte hinzufügen.
3. Gemeindegrenze aus `data/processed/boundaries/<gemeinde>_boundary.gpkg` laden.
4. Auf die Gemeindegrenze zoomen.
5. Prüfen, ob die Straßen zur Basiskarte passen.
6. Prüfen, ob keine Straßen weit außerhalb der Gemeinde liegen.

Attributprüfung:

1. Attributtabelle von `osm_roads` öffnen.
2. Prüfen, ob das Feld `highway` vorhanden ist.
3. Nach `highway` sortieren oder filtern.
4. Prüfen, welche Straßenklassen vorkommen.

Symbolisierung:

1. Rechtsklick auf `osm_roads`.
2. `Eigenschaften` öffnen.
3. `Symbolisierung` auswählen.
4. `Kategorisiert` auswählen.
5. Als Wert `highway` verwenden.
6. `Klassifizieren` klicken.

So wird sichtbar, ob die wichtigen Straßenklassen korrekt geladen wurden.

## Verwendete Klassen

Diese Klassen werden in `scripts/prepare_data/2_download_overpass_data.py`
behalten und in den Layer `osm_roads` geschrieben.

| OSM-Wert | Verwendung im Wind-Workflow | Grund |
| --- | --- | --- |
| motorway | Straßenpuffer | Sehr wichtige Straßeninfrastruktur |
| motorway_link | Straßenpuffer | Verbindung zu sehr wichtiger Straßeninfrastruktur |
| trunk | Straßenpuffer | Wichtige überregionale Straße |
| trunk_link | Straßenpuffer | Verbindung zu überregionaler Straße |
| primary | Straßenpuffer | Wichtige regionale Straße |
| primary_link | Straßenpuffer | Verbindung zu regionaler Straße |
| secondary | Straßenpuffer | Regionale Straße |
| secondary_link | Straßenpuffer | Verbindung zu regionaler Straße |
| tertiary | Straßenpuffer | Lokale Verbindungsstraße |
| tertiary_link | Straßenpuffer | Verbindung zu lokaler Straße |
| unclassified | Straßenpuffer | Kleinere öffentliche Straße |
| residential | Siedlung / Straßenpuffer | Straße innerhalb von Wohngebieten |
| living_street | Siedlung / Straßenpuffer | Verkehrsberuhigter Bereich |
| service | Kleiner Puffer / Erschließung | Zufahrt, Parkplatzweg oder Betriebsweg |
| track | Erschließung / kleiner Puffer | Land- oder forstwirtschaftlicher Weg |
| road | Manuelle Prüfung | Straße mit unklarer Klassifikation |

## Zunächst nicht verwendete Klassen

Diese Klassen werden im ersten Workflow nicht verwendet, weil sie meist
Fußwege, Radwege oder sehr kleine Wege beschreiben:

| OSM-Wert | Grund |
| --- | --- |
| footway | Fußweg, nicht primäre Straßeninfrastruktur |
| path | Allgemeiner Pfad, für erste Straßenpuffer weniger relevant |
| cycleway | Radweg, nicht primäre Straßeninfrastruktur |
| bridleway | Reitweg |
| steps | Treppen |
| pedestrian | Fußgängerbereich, später eher über Siedlung/Landnutzung prüfbar |

## Hinweise

Für die erste Analyse werden die Straßen vor allem für Abstandspuffer und
Erschließungsprüfungen genutzt. Wenn später eine genauere Erreichbarkeit
modelliert werden soll, können `track`, `service`, `path`, `cycleway` und
Attribute wie `surface` detaillierter geprüft werden.
