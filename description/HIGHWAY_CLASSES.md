# Highway-Klassen

Diese Datei dokumentiert, wie OpenStreetMap-Verkehrsdaten in der Pipeline
verwendet werden.

Gemeint sind vor allem:

- `highway=*` für Straßen und Wege
- `railway=*` für Schienenwege
- später bei Bedarf auch `waterway=*` für Wasser

Quellen:

```text
https://wiki.openstreetmap.org/wiki/DE:Key:highway
https://wiki.openstreetmap.org/wiki/Key:highway
https://wiki.openstreetmap.org/wiki/DE:Key:railway
https://wiki.openstreetmap.org/wiki/Key:railway
```

## 1. Allgemein

OSM wird in der Pipeline genutzt, weil Verkehrsobjekte dort als Linien mit
Attributen vorliegen. Diese Linienstruktur ist für Abstandspuffer,
Erschließungsfragen und räumliche Näherungen besser geeignet als reine
Flächeninformationen.

Der offizielle Landnutzungsdatensatz enthält zwar ebenfalls Verkehrsflächen,
beschreibt diese aber als Flächen. OSM ergänzt diesen Datensatz deshalb, ersetzt
ihn aber nicht vollständig.

Wichtig:

- OSM ist kein amtlicher Rechtsdatensatz.
- OSM dient hier als räumliche Näherung.
- Amtliche Planungs- und Schutzdatensätze bleiben die wichtigere Grundlage.

## 2. Gemeinsamer OSM-Rohdownload

Der allgemeine OSM-Download läuft über:

```text
scripts/1_prepare_data/5_download_osm_network_data.py
```

Das Skript lädt für alle Technologien zuerst einen gemeinsamen
Straßenbasisdatensatz:

```text
data/processed/1_base_osm_streets/<gemeinde>_osm_streets.gpkg
data/processed/1_base_osm_streets/<gemeinde>_osm_streets_raw.json
```

Layer:

```text
analysekontext_<gemeinde>
osm_streets_raw
```

Der Download erfolgt nicht direkt nur auf die Gemeindegrenze, sondern mit einem
erweiterten Analysekontext:

```text
1000 m Buffer um die Gemeinde
```

Dadurch gehen Straßen oder Schienen knapp außerhalb der Gemeinde nicht verloren,
wenn ihre späteren Puffer oder Wirkbereiche innerhalb der Gemeinde liegen.

### Geladene allgemeine Straßenklassen

Diese Klassen werden im Rohlayer `osm_streets_raw` mitgeführt:

| OSM-Wert | Einordnung |
| --- | --- |
| `motorway` | Autobahn |
| `motorway_link` | Autobahnanschluss |
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

## 3. Wind

Für Wind wird aus dem gemeinsamen Rohlayer ein eigener Ausschluss- bzw.
Kontextlayer abgeleitet:

```text
scripts/2_1_wind/4_prepare_wind_osm_streets.py
```

Output:

```text
data/processed/2_technology_wind/<gemeinde>_osm_wind_streets.gpkg
data/processed/2_technology_wind/<gemeinde>_osm_wind_streets_puffer.gpkg
```

Layer:

```text
osm_streets_wind_ausschluss
osm_streets_wind_ausschluss_puffer
```

Aktuell werden dafür diese Klassen verwendet:

```text
motorway, motorway_link, trunk, trunk_link,
primary, primary_link, secondary, secondary_link,
tertiary, tertiary_link, unclassified,
residential, living_street
```

Nicht automatisch im Ausschlusslayer:

```text
service, track, road
```

Diese kleineren oder unklaren Wege bleiben im Rohlayer erhalten und können
später manuell geprüft oder mit eigenen Puffern verarbeitet werden.

Zus�tzlich wird aus dem gefilterten Linienlayer ein erster Pufferlayer
erzeugt. Die Pufferdistanz steht im Feld `buffer_m`. Die Werte sind
Arbeitsannahmen f�r eine erste Ausschluss- bzw. Konfliktfl�che und k�nnen
sp�ter fachlich angepasst werden.

## 4. Solar

Für Solar wird OSM aktuell für die Korridorbasis nach EEG und BauGB verwendet.
Das frühere Solar-Straßenausschluss-Skript bleibt als Reserve erhalten, ist
aber nicht Teil des aktiven Solar-Workflows:

```text
scripts/2_2_solar/unused_prepare_solar_osm_streets.py
```

### 4.1 Solar-Korridorbasis für EEG und BauGB

Script 5 erzeugt für Solar eine eigene Korridorgrundlage:

```text
data/processed/2_technology_solar/corridor/<gemeinde>_solar_corridor_basis.gpkg
data/processed/2_technology_solar/corridor/<gemeinde>_solar_corridor_basis_raw.json
```

Layer:

```text
analysekontext_<gemeinde>
solar_corridor_autobahnen_<gemeinde>
solar_corridor_schienenwege_<gemeinde>
```

Diese Korridorbasis wird von folgendem Skript weiterverarbeitet:

```text
scripts/2_2_solar/1_prepare_solar_corridor_layers.py
```

Fachlicher Bezug:

- `PV-Förderkulisse 500 m`: EEG 2023, § 37 Abs. 1 Nr. 2 Buchstabe c
- `PV-Privilegierung 200 m`: BauGB, § 35 Abs. 1 Nr. 8 Buchstabe b

Für den 500-m-Buffer werden Autobahnen und `railway=rail` verwendet. Für den
200-m-Buffer werden Autobahnen und Schienenwege mit `tracks >= 2` als
vereinfachte OSM-Näherung verwendet.

Diese Buffer sind keine rechtsverbindliche Einzelfallprüfung.

## 5. Wasser

Für Wasser ist OSM aktuell nur als vorbereitender Kontextlayer vorgesehen.

Script und Output:

```text
TODO: TBD: Wasser-spezifische OSM-Verarbeitung ist noch nicht umgesetzt.
```

Layer:

```text
osm_streets_wasser_ausschluss
osm_streets_wasser_ausschluss_puffer
```

Später können für Wasser zusätzlich `waterway=*`, Brücken, Zugänge oder
wasserbezogene Infrastruktur berücksichtigt werden.

## 6. Prüfung in QGIS

Allgemeine Sichtprüfung:

1. `osm_streets_raw` in QGIS laden.
2. OpenStreetMap-Basiskarte hinzufügen.
3. Gemeindegrenze laden.
4. Auf die Gemeinde und den Analysekontext zoomen.
5. Prüfen, ob die Linien zur Basiskarte passen.
6. Prüfen, ob der Analysekontext fachlich sinnvoll gewählt ist.

Attributprüfung:

1. Attributtabelle öffnen.
2. Felder wie `highway`, `railway`, `tracks` und `name` prüfen.
3. Nach Klassen filtern oder kategorisieren.
4. Danach die technologiespezifischen Layer mit dem Rohlayer vergleichen.
