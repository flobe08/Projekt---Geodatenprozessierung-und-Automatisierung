# Anleitung

Diese Datei beschreibt den aktuellen Projektaufbau, die Reihenfolge der
Skripte und die manuelle Ausführung.

## Skriptstruktur

### 1. Gemeinsame Datenvorbereitung

- `scripts/1_prepare_data.py`
- `scripts/1_prepare_data/1_download_data.py`
- `scripts/1_prepare_data/2_extract_municipality_boundary.py`
- `scripts/1_prepare_data/3_build_protection_layers.py`
- `scripts/1_prepare_data/4_clip_landuse.py`
- `scripts/1_prepare_data/5_download_osm_network_data.py`

### 2. Technologiespezifische Verarbeitung

- Wind: `scripts/2_1_wind/1_clip_wind_planning_areas.py`
- Wind: `scripts/2_1_wind/2_prepare_wind_landuse.py`
- Wind: `scripts/2_1_wind/3_build_wind_landuse_buffers.py`
- Wind: `scripts/2_1_wind/4_prepare_wind_osm_streets.py`
- Wind: `scripts/2_1_wind/5_build_wind_exclusion_layer.py`
- Solar: `scripts/2_2_solar/1_prepare_solar_corridor_layers.py`
- Solar: `scripts/2_2_solar/2_prepare_solar_landuse.py`
- Solar: `scripts/2_2_solar/3_download_solar_reference_wms.py`
- Wasser: TODO/TBD, aktuell nur als Platzhalter vorbereitet

Hinweis:

- `scripts/2_2_solar/unused_prepare_solar_osm_streets.py` bleibt als
  Reserve im Codebestand, wird aber im aktiven Solar-Workflow nicht
  ausgeführt.

### 3. Kartenerzeugung

- `scripts/3_generate_map.py`
- `scripts/3_generate_map/1_prepare_overview_layers.py`
- `scripts/3_generate_map/2_create_map_qgis_project.py`
- `scripts/3_generate_map/3_generate_map_pdf.py`

## Ergebnisstruktur

Die Ergebnisse unter `data/processed/` sind nach Verarbeitungsebene getrennt:

```text
data/processed/
  1_base_boundaries/
  1_base_landuse/
  1_base_osm_streets/
  1_base_overview/
  1_base_protection_areas/

  2_technology_wind/
  2_technology_solar/

  3_qgis_projects/
  3_maps/
```

Die `1_base_*`-Ordner enthalten gemeinsame Grundlagen wie Gemeindegrenzen,
Landnutzung, OSM-Straßen, Schutzgebiete und Locator-Layer. Die
`2_technology_*`-Ordner enthalten daraus abgeleitete Fachlayer für Wind bzw.
Solar. Die finalen QGIS-Projekte und PDF-Karten liegen in den `3_output_*`-
Ordnern.

Für Solar wird zusätzlich innerhalb des Solar-Ordners getrennt:

```text
data/processed/2_technology_solar/corridor/
data/processed/2_technology_solar/reference/
```

`corridor/` enthält die OSM-basierte Grundlage für die 200-m- und
500-m-Korridore. `reference/` enthält die aus dem amtlichen WMS geladenen
PV-Freiflächenkulissen als georeferenzierte Rasterbilder.

## Automatischer Workflow

Hinweis vor dem Start:

- Verwendete QGIS-Version im Projekt: **QGIS 4.0 Norrköping**
- Der erste vollständige Durchlauf kann spürbar länger dauern.
- Im Workflow werden mehrere große Bayern-Datensätze verarbeitet.
- Vor allem der offizielle Landnutzungsdatensatz ist ungefähr 5 bis 6 GB groß
  und braucht beim ersten lokalen Download entsprechend länger.

### Wind

```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data.py --municipality Drachselsried --technology wind
deactivate
python3 scripts/3_generate_map.py --municipality Drachselsried --technology wind
```

Wenn die Zwischenergebnisse bereits erzeugt wurden, kann der erneute Lauf
beschleunigt werden:

```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data.py --municipality Drachselsried --technology wind --skip-existing
deactivate
python3 scripts/3_generate_map.py --municipality Drachselsried --technology wind
```

`--skip-existing` überspringt aktuell insbesondere den bereits vorhandenen
zugeschnittenen Landnutzungsdatensatz. Das ist sinnvoll, wenn nur die Karte,
das QGIS-Projekt oder spätere Folgeschritte erneut getestet werden sollen.


### Solar

```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data.py --municipality Drachselsried --technology solar
deactivate
python3 scripts/3_generate_map.py --municipality Drachselsried --technology solar
```

### beides:
```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data.py --municipality Drachselsried --technology wind
python3 scripts/1_prepare_data.py --municipality Drachselsried --technology solar
deactivate

python3 scripts/3_generate_map.py --municipality Drachselsried --technology wind
python3 scripts/3_generate_map.py --municipality Drachselsried --technology solar
```

### Alles zusammen

```bash
bash run_workflow.sh Drachselsried wind
```

Der Workflow ruft intern diese beiden Einstiegsskripte auf:

- `scripts/1_prepare_data.py`
- `scripts/3_generate_map.py`

Die Mermaid-Diagramme mit den exakten Log-Step-Namen stehen in:

- `description/WORKFLOW_DIAGRAMME.md`

## Manuelle Ausführung Schritt für Schritt

### Wind

1. Rohdaten herunterladen:

```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data/1_download_data.py --technology wind
```

2. Gemeindegrenze extrahieren:

```bash
python3 scripts/1_prepare_data/2_extract_municipality_boundary.py --municipality Drachselsried
```

3. Allgemeine Schutzgebiete und windspezifische Vogelkulissen aufbereiten:

```bash
python3 scripts/1_prepare_data/3_build_protection_layers.py --municipality Drachselsried
```

4. Landnutzung auf Gemeinde clippen:

```bash
python3 scripts/1_prepare_data/4_clip_landuse.py --municipality Drachselsried
```

5. OSM-Netzdaten laden:

```bash
python3 scripts/1_prepare_data/5_download_osm_network_data.py --municipality Drachselsried --technology wind
```

6. OSM-Straßen für Wind filtern:

```bash
python3 scripts/2_1_wind/4_prepare_wind_osm_streets.py --municipality Drachselsried
```

7. Windflächen clippen:

```bash
python3 scripts/2_1_wind/1_clip_wind_planning_areas.py --municipality Drachselsried
```

8. Windspezifische Landnutzung ableiten:

```bash
python3 scripts/2_1_wind/2_prepare_wind_landuse.py --municipality Drachselsried
```

9. Windspezifische Landnutzungspuffer erzeugen:

```bash
python3 scripts/2_1_wind/3_build_wind_landuse_buffers.py --municipality Drachselsried
```

10. Gesamten Wind-Ausschlusslayer aus Landnutzungspuffer und OSM-Puffer bauen:

```bash
python3 scripts/2_1_wind/5_build_wind_exclusion_layer.py --municipality Drachselsried
deactivate
```

11. Übersichtskarten-Layer vorbereiten:

```bash
python3 scripts/3_generate_map/1_prepare_overview_layers.py --municipality Drachselsried
```

12. QGIS-Projekt erzeugen:

```bash
python3 scripts/3_generate_map/2_create_map_qgis_project.py --municipality Drachselsried --technology wind
```

13. PDF-Karte erzeugen:

```bash
python3 scripts/3_generate_map/3_generate_map_pdf.py --municipality Drachselsried --technology wind
```

### Solar

1. Gemeinsame Rohdaten laden:

```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data/1_download_data.py --technology solar
```

2. Gemeindegrenze extrahieren:

```bash
python3 scripts/1_prepare_data/2_extract_municipality_boundary.py --municipality Drachselsried
```

3. Allgemeine Schutzgebiete aufbereiten:

```bash
python3 scripts/1_prepare_data/3_build_protection_layers.py --municipality Drachselsried
```

4. Landnutzung auf Gemeinde clippen:

```bash
python3 scripts/1_prepare_data/4_clip_landuse.py --municipality Drachselsried
```

5. OSM-Netzdaten laden:

```bash
python3 scripts/1_prepare_data/5_download_osm_network_data.py --municipality Drachselsried --technology solar
```

6. Solarpuffer erzeugen:

```bash
python3 scripts/2_2_solar/1_prepare_solar_corridor_layers.py --municipality Drachselsried
```

7. Solarspezifische Landnutzung ableiten:

```bash
python3 scripts/2_2_solar/2_prepare_solar_landuse.py --municipality Drachselsried
deactivate
```

8. Amtliche Solar-WMS-Referenzbilder lokal laden:

```bash
python3 scripts/2_2_solar/3_download_solar_reference_wms.py --municipality Drachselsried
```

Hinweis: Dieser Schritt nutzt PyQGIS und wird deshalb außerhalb der
`.venv-wsl` mit dem QGIS-/System-Python ausgeführt.

Zusätzliche manuelle Referenz in QGIS:

1. `WMS/WMTS` öffnen
2. Dienst registrieren:

```text
https://www.lfu.bayern.de/gdi/wms/energieatlas/planungsgrundlagen_solar
```

3. Danach diese amtlichen Referenzlayer laden:

- `PV-Freiflächenkulisse - Zoomstufe 1`
- `PV-Freiflächenkulisse - Zoomstufe 2`

Hinweis:

- Im automatisch erzeugten Solar-QGIS-Projekt werden diese beiden
  WMS-Referenzlayer bereits direkt eingebunden.

9. Übersichtskarten-Layer vorbereiten:

```bash
python3 scripts/3_generate_map/1_prepare_overview_layers.py --municipality Drachselsried
```

10. QGIS-Projekt erzeugen:

```bash
python3 scripts/3_generate_map/2_create_map_qgis_project.py --municipality Drachselsried --technology solar
```

11. PDF-Karte erzeugen:

```bash
python3 scripts/3_generate_map/3_generate_map_pdf.py --municipality Drachselsried --technology solar
```

## Schutzgebietslayer

`scripts/1_prepare_data/3_build_protection_layers.py` erzeugt aktuell drei
separate GeoPackages:

```text
data/processed/1_base_protection_areas/<gemeinde>_naturschutz_allgemein_hart.gpkg
data/processed/1_base_protection_areas/<gemeinde>_naturschutz_allgemein_weich.gpkg
data/processed/1_base_protection_areas/<gemeinde>_naturschutz_wind.gpkg
```

Jede dieser Dateien enthält:

- die einzeln zugeschnittenen Ursprungslayer
- einen zusammengeführten Layer für die jeweilige Kategorie

Typische zusammengeführte Layernamen:

- `naturschutz_allgemein_hart_merged`
- `naturschutz_allgemein_weich_merged`
- `naturschutz_wind_merged`

Hinweis:

- `naturschutz_wind` wird nur dann sinnvoll befüllt, wenn vorher
  `1_download_data.py --technology wind` ausgeführt wurde, weil dabei die
  Vogelkulissen 2024 mitgeladen werden.
- Punktförmige Naturdenkmale und punktförmige geschützte
  Landschaftsbestandteile werden als eigene geclippte Punktlayer mit
  ausgegeben.
- Sie werden aktuell aber noch nicht in den zusammengeführten harten
  Flächenausschlusslayer `naturschutz_allgemein_hart_merged` übernommen, weil
  dafür erst eine fachlich begründete Pufferregel festgelegt werden müsste.

## QGIS-Projekt, Detail- und Attributlayer

Das automatisch erzeugte QGIS-Projekt enthält zwei Ebenen:

1. sichtbare Kartenlayer für die eigentliche Karte
2. ausgeblendete Detail- und Attributlayer für Kontrolle und Dokumentation

Die sichtbaren Naturschutzlayer bleiben bewusst zusammengefasst:

- `Harte Naturschutz-Restriktionen`
- `Weiche Naturschutz-Konfliktflächen`
- `Windspezifische Restriktionen`

Zusätzlich werden im QGIS-Projekt ausgeblendete Gruppen angelegt:

- `Detail- und Attributlayer Naturschutz hart`
- `Detail- und Attributlayer Naturschutz weich`
- `Detail- und Attributlayer Naturschutz Wind`
- `Detail- und Attributlayer Wind-Ausschluss`
- `Detail- und Attributlayer OSM`

Diese Detail- und Attributlayer dienen dazu, einzelne Ursprungslayer und ihre
Attribute nachvollziehen zu können. Sie werden nicht automatisch als
zusätzliche Hauptlayer in der PDF-Karte dargestellt, damit die Karte lesbar
bleibt.

Die PDF-Legende enthält für die Windkarte zusätzlich:

- `Straßen`
- `Nutzungsausschluss`

Der Nordpfeil wird in der Wind-PDF unten rechts innerhalb der Karte platziert.
Dadurch bleibt im rechten Layoutbereich mehr Platz für Legende, Maßstab,
Autor und Datum. Zusätzlich wird eine kleine Übersichtskarte mit dem Titel
`Lage in Bayern` eingebunden. Diese Übersichtskarte nutzt einen dezenten
OSM-Hintergrund, die Bayern-Grenze aus dem amtlichen Verwaltungsdatensatz und
die ausgewählte Gemeinde als rote Fläche.

## Landnutzung

Die Landnutzung wird im Workflow als offizieller Bayern-Gesamtdatensatz lokal
heruntergeladen und anschließend in Script 4 auf die Gemeinde zugeschnitten.

Die separate manuelle Verarbeitung ist weiterhin möglich:

```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data/4_clip_landuse.py --municipality Drachselsried
```

Dabei gilt:

- zuerst Gemeindegrenze lesen
- dann den bereits lokal vorhandenen offiziellen Bayern-Datensatz verwenden
- danach nur den relevanten Bereich per Bounding-Box lesen
- anschließend exakt auf die Gemeinde clippen
- anschließend ein `landnutzung_<gemeinde>.gpkg` schreiben
- darin bleiben die zugeschnittenen `ln_*`-Layer einzeln erhalten

Beispiel:

```text
data/processed/1_base_landuse/landnutzung_drachselsried.gpkg
```

Damit bleibt der Originaldatensatz unangetastet und die technologiespezifischen
Skripte können später alle denselben kleineren Gemeinde-Datensatz verwenden.

Methodischer Hinweis:

- Die offizielle Quelle wird als großes GeoPackage für ganz Bayern bereitgestellt.
- Ein echter kleiner Teil-Download nur für eine einzelne Gemeinde ist über
  dieses Format nicht zuverlässig möglich.
- Deshalb wird der vollständige Datensatz einmal lokal vorgehalten und danach
  automatisiert per Bounding-Box und exaktem Gemeindezuschnitt verarbeitet.

Die technologiespezifischen Landnutzungs-Skripte schreiben danach jeweils
separate GeoPackages, zum Beispiel für Wind:

```text
data/processed/2_technology_wind/<gemeinde>_landuse_wind_ausschluss.gpkg
data/processed/2_technology_wind/<gemeinde>_landuse_wind_potenzial.gpkg
data/processed/2_technology_wind/<gemeinde>_landuse_wind_geeignet.gpkg
data/processed/2_technology_wind/<gemeinde>_landuse_wind_unused.gpkg
```

Hinweis zur Wind-Klasse `unused`:

- `ln_strassenundwegeverkehr` wird bewusst nicht mehr pauschal als Ausschluss
  behandelt.
- Der offizielle Landnutzungslayer ist dafür zu grob, weil dort auch kleinere
  Wege enthalten sein können.
- Die Fläche bleibt deshalb als eigener Zwischenlayer erhalten und kann später
  gezielt mit OSM-Straßenklassen oder Puffern weiter verfeinert werden.

Analog dazu gibt es dieselbe Grundstruktur auch für Solar und Wasser.

## OSM-Netzdaten

Der allgemeine OSM-Download wird jetzt über ein gemeinsames Skript gesteuert:

```text
scripts/1_prepare_data/5_download_osm_network_data.py
```

Wichtige Parameter:

- `--municipality`
- `--technology wind|solar|wasser`

Der Download arbeitet mit einem gemeinsamen Analysekontext:

```text
1000 m Buffer um die Gemeinde
```

Dadurch werden Straßen oder Schienen knapp außerhalb der Gemeinde nicht zu
früh abgeschnitten.

Zuerst entsteht immer ein gemeinsamer OSM-Straßenbasisdatensatz:

```text
data/processed/1_base_osm_streets/<gemeinde>_osm_streets.gpkg
data/processed/1_base_osm_streets/<gemeinde>_osm_streets_raw.json
```

Layer:

```text
analysekontext_<gemeinde>
osm_streets_raw
```

Dieser Datensatz enthält die breit geladenen Straßenklassen. Die eigentliche
fachliche Auswahl erfolgt danach in den Technologieordnern.

### Wind

```text
data/processed/2_technology_wind/<gemeinde>_osm_wind_streets.gpkg
data/processed/2_technology_wind/<gemeinde>_osm_wind_streets_puffer.gpkg
```

Layer:

```text
osm_streets_wind_ausschluss
osm_streets_wind_ausschluss_puffer
```

### Solar

Für die 200-m- und 500-m-Solarpuffer entsteht eine eigene
Korridorgrundlage:

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

Das frühere Skript `unused_prepare_solar_osm_streets.py` bleibt nur als
Reserve im Codebestand. Im aktiven Solar-Workflow wird es nicht ausgeführt,
weil die EEG-/BauGB-Korridore direkt aus `solar_corridor_basis` abgeleitet
werden.

### Wasser

```text
data/processed/2_technology_wasser/<gemeinde>_osm_wasser_streets.gpkg
data/processed/2_technology_wasser/<gemeinde>_osm_wasser_streets_puffer.gpkg
```

Layer:

```text
osm_streets_wasser_ausschluss
osm_streets_wasser_ausschluss_puffer
```

## Fachliche Logik der Solarpuffer

Der Solar-Workflow trennt bewusst zwei Flächenkategorien:

1. `PV-Förderkulisse 500 m`
   - Orientierung an `EEG 2023 § 37 Abs. 1 Nr. 2 Buchstabe c`
   - räumliche Näherung entlang von Autobahnen und Schienenwegen

2. `PV-Privilegierung 200 m`
   - Orientierung an `BauGB § 35 Abs. 1 Nr. 8 Buchstabe b`
   - ebenfalls entlang von Autobahnen und Schienenwegen

Wichtig:

- Die 500-m-Fläche ist **nicht** automatisch eine Baugenehmigung.
- Die 200-m-Fläche ist ebenfalls **keine** abschließende Einzelfallprüfung.
- Beide Layer sind bewusst als automatisierte, nachvollziehbare Näherung
  umgesetzt.

## Welche OSM-Typen für Solar verwendet werden

Aktuell werden für die Solarpipeline nur diese OSM-Typen verwendet:

- `highway = motorway`
- `highway = motorway_link`
- `railway = rail`

Damit orientiert sich die Pipeline an `Autobahnen + Schienenwegen` und nicht an
allgemeinen Straßen.
