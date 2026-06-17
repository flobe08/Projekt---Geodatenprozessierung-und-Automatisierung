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
- Solar: `scripts/2_2_solar/1_download_solar_reference_wms.py`
- Solar: `scripts/2_2_solar/2_prepare_solar_corridor_layers.py`
- Solar: `scripts/2_2_solar/3_prepare_solar_landuse.py`
- Solar: `scripts/2_2_solar/4_prepare_solar_osm_streets.py`
- Wasser: `scripts/2_3_wasser/1_prepare_water_landuse.py`
- Wasser: `scripts/2_3_wasser/2_prepare_water_osm_streets.py`

### 3. Kartenerzeugung

- `scripts/3_generate_map.py`
- `scripts/3_generate_map/1_create_map_qgis_project.py`
- `scripts/3_generate_map/2_generate_map_pdf.py`

## Automatischer Workflow

Hinweis vor dem Start:

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

### Solar

```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data.py --municipality Drachselsried --technology solar
deactivate
python3 scripts/3_generate_map.py --municipality Drachselsried --technology solar
```

### Alles zusammen

```bash
bash run_workflow.sh Drachselsried wind
```

Der Workflow ruft intern diese beiden Einstiegsskripte auf:

- `scripts/1_prepare_data.py`
- `scripts/3_generate_map.py`

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

11. QGIS-Projekt erzeugen:

```bash
python3 scripts/3_generate_map/1_create_map_qgis_project.py --municipality Drachselsried --technology wind
```

12. PDF-Karte erzeugen:

```bash
python3 scripts/3_generate_map/2_generate_map_pdf.py --municipality Drachselsried --technology wind
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

6. OSM-Straßen für Solar filtern:

```bash
python3 scripts/2_2_solar/4_prepare_solar_osm_streets.py --municipality Drachselsried
```

7. Solarpuffer erzeugen:

```bash
python3 scripts/2_2_solar/2_prepare_solar_corridor_layers.py --municipality Drachselsried
```

8. Solarspezifische Landnutzung ableiten:

```bash
python3 scripts/2_2_solar/3_prepare_solar_landuse.py --municipality Drachselsried
deactivate
```

9. Amtliche Solar-WMS-Referenzbilder lokal laden:

```bash
python3 scripts/2_2_solar/1_download_solar_reference_wms.py --municipality Drachselsried
```

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

10. QGIS-Projekt erzeugen:

```bash
python3 scripts/3_generate_map/1_create_map_qgis_project.py --municipality Drachselsried --technology solar
```

11. PDF-Karte erzeugen:

```bash
python3 scripts/3_generate_map/2_generate_map_pdf.py --municipality Drachselsried --technology solar
```

## Schutzgebietslayer

`scripts/1_prepare_data/3_build_protection_layers.py` erzeugt aktuell drei
separate GeoPackages:

```text
data/processed/schutzgebiete/<gemeinde>_naturschutz_allgemein_hart.gpkg
data/processed/schutzgebiete/<gemeinde>_naturschutz_allgemein_weich.gpkg
data/processed/schutzgebiete/<gemeinde>_naturschutz_wind.gpkg
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
data/processed/landuse/landnutzung_drachselsried.gpkg
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
data/processed/wind/<gemeinde>_landuse_wind_ausschluss.gpkg
data/processed/wind/<gemeinde>_landuse_wind_potenzial.gpkg
data/processed/wind/<gemeinde>_landuse_wind_geeignet.gpkg
data/processed/wind/<gemeinde>_landuse_wind_unused.gpkg
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
data/processed/osm_streets/<gemeinde>_osm_streets.gpkg
data/processed/osm_streets/<gemeinde>_osm_streets_raw.json
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
data/processed/wind/<gemeinde>_osm_wind_streets.gpkg
data/processed/wind/<gemeinde>_osm_wind_streets_puffer.gpkg
```

Layer:

```text
osm_streets_wind_ausschluss
osm_streets_wind_ausschluss_puffer
```

### Solar

Für die allgemeinen Solar-Straßenausschlüsse:

```text
data/processed/solar/<gemeinde>_osm_solar_streets.gpkg
data/processed/solar/<gemeinde>_osm_solar_streets_puffer.gpkg
```

Layer:

```text
osm_streets_solar_ausschluss
osm_streets_solar_ausschluss_puffer
```

Für die 200-m- und 500-m-Solarpuffer entsteht zusätzlich eine eigene
Korridorgrundlage:

```text
data/processed/solar/<gemeinde>_solar_corridor_basis.gpkg
data/processed/solar/<gemeinde>_solar_corridor_basis_raw.json
```

Layer:

```text
analysekontext_<gemeinde>
solar_corridor_autobahnen_<gemeinde>
solar_corridor_schienenwege_<gemeinde>
```

### Wasser

```text
data/processed/wasser/<gemeinde>_osm_wasser_streets.gpkg
data/processed/wasser/<gemeinde>_osm_wasser_streets_puffer.gpkg
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
