# Skript-Output-Übersicht

Diese Datei ordnet die wichtigsten Skripte ihren Eingabe- und Ausgabedaten zu.
Damit kann später jeder erzeugte Output wieder dem passenden Verarbeitungsschritt
zugeordnet werden.

Platzhalter:

- `<gemeinde>` steht z. B. für `drachselsried`
- `<technologie>` steht z. B. für `wind` oder `solar`

## Ordnerlogik unter `data/processed`

Die Ergebnisordner sind bewusst nummeriert, damit die Outputs direkt einer
Verarbeitungsebene zugeordnet werden können:

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

Für Solar werden zwei Unterordner verwendet:

```text
data/processed/2_technology_solar/corridor/
data/processed/2_technology_solar/reference/
```

`corridor/` enthält die OSM-basierte Grundlage für die EEG-/BauGB-Korridore.
`reference/` enthält die WMS-Referenzbilder aus dem Energie-Atlas Bayern.

## 1. Gemeinsame Datenvorbereitung

| Skriptname | Inputfiles / Quellen | Outputfiles |
| --- | --- | --- |
| `scripts/1_prepare_data/1_download_data.py` | Offizielle Downloadquellen für Verwaltungsgrenzen, Landnutzung, Schutzgebiete, Natura-2000-Daten und technologieabhängige Rohdaten | `data/raw/Verwaltungsgebiet_Bayern/alkis_verwaltungsgebiete.zip`, `data/raw/Verwaltungsgebiet_Bayern/`, `data/raw/landuse/landnutzung.gpkg`, `data/raw/schutzgebiete/`, `data/raw/wind/` |
| `scripts/1_prepare_data/2_extract_municipality_boundary.py` | `data/raw/Verwaltungsgebiet_Bayern/` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg` |
| `scripts/1_prepare_data/3_build_protection_layers.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, `data/raw/schutzgebiete/`, `data/raw/wind/vogelkulissen_2024/` | `data/processed/1_base_protection_areas/<gemeinde>_naturschutz_allgemein_hart.gpkg`, `data/processed/1_base_protection_areas/<gemeinde>_naturschutz_allgemein_weich.gpkg`, `data/processed/1_base_protection_areas/<gemeinde>_naturschutz_wind.gpkg` |
| `scripts/1_prepare_data/4_clip_landuse.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, `data/raw/landuse/landnutzung.gpkg` | `data/processed/1_base_landuse/landnutzung_<gemeinde>.gpkg` |
| `scripts/1_prepare_data/5_download_osm_network_data.py --technology wind` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, Overpass API | `data/processed/1_base_osm_streets/<gemeinde>_osm_streets.gpkg`, `data/processed/1_base_osm_streets/<gemeinde>_osm_streets_raw.json` |
| `scripts/1_prepare_data/5_download_osm_network_data.py --technology solar` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, Overpass API | `data/processed/1_base_osm_streets/<gemeinde>_osm_streets.gpkg`, `data/processed/1_base_osm_streets/<gemeinde>_osm_streets_raw.json`, `data/processed/2_technology_solar/corridor/<gemeinde>_solar_corridor_basis.gpkg`, `data/processed/2_technology_solar/corridor/<gemeinde>_solar_corridor_basis_raw.json` |
| `scripts/1_prepare_data/5_download_osm_network_data.py --technology wasser` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, Overpass API | `data/processed/1_base_osm_streets/<gemeinde>_osm_streets.gpkg`, `data/processed/1_base_osm_streets/<gemeinde>_osm_streets_raw.json` |

## 2. Wind

| Skriptname | Inputfiles | Outputfiles |
| --- | --- | --- |
| `scripts/2_1_wind/1_clip_wind_planning_areas.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, `data/raw/wind/wind_vorranggebiete.gpkg`, `data/raw/wind/wind_vorbehaltsgebiete.gpkg` | `data/processed/2_technology_wind/<gemeinde>_wind_layers.gpkg` |
| `scripts/2_1_wind/2_prepare_wind_landuse.py` | `data/processed/1_base_landuse/landnutzung_<gemeinde>.gpkg` | `data/processed/2_technology_wind/<gemeinde>_landuse_wind_ausschluss.gpkg`, `data/processed/2_technology_wind/<gemeinde>_landuse_wind_potenzial.gpkg`, `data/processed/2_technology_wind/<gemeinde>_landuse_wind_geeignet.gpkg`, `data/processed/2_technology_wind/<gemeinde>_landuse_wind_unused.gpkg` |
| `scripts/2_1_wind/3_build_wind_landuse_buffers.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, `data/processed/2_technology_wind/<gemeinde>_landuse_wind_ausschluss.gpkg` | `data/processed/2_technology_wind/<gemeinde>_landuse_wind_ausschluss_puffer.gpkg` |
| `scripts/2_1_wind/4_prepare_wind_osm_streets.py` | `data/processed/1_base_osm_streets/<gemeinde>_osm_streets.gpkg` | `data/processed/2_technology_wind/<gemeinde>_osm_wind_streets.gpkg`, `data/processed/2_technology_wind/<gemeinde>_osm_wind_streets_puffer.gpkg` |
| `scripts/2_1_wind/5_build_wind_exclusion_layer.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, `data/processed/2_technology_wind/<gemeinde>_landuse_wind_ausschluss_puffer.gpkg`, `data/processed/2_technology_wind/<gemeinde>_osm_wind_streets_puffer.gpkg` | `data/processed/2_technology_wind/<gemeinde>_wind_ausschluss_gesamt.gpkg` |

## 3. Solar

| Skriptname | Inputfiles | Outputfiles |
| --- | --- | --- |
| `scripts/2_2_solar/1_prepare_solar_corridor_layers.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, `data/processed/2_technology_solar/corridor/<gemeinde>_solar_corridor_basis.gpkg` | `data/processed/2_technology_solar/<gemeinde>_solar_layers.gpkg` |
| `scripts/2_2_solar/2_prepare_solar_landuse.py` | `data/processed/1_base_landuse/landnutzung_<gemeinde>.gpkg` | `data/processed/2_technology_solar/<gemeinde>_landuse_solar_ausschluss.gpkg`, `data/processed/2_technology_solar/<gemeinde>_landuse_solar_pv_freiflaechen_naehung_vektorlayer.gpkg`, `data/processed/2_technology_solar/<gemeinde>_landuse_solar_unused.gpkg` |
| `scripts/2_2_solar/3_download_solar_reference_wms.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, WMS `https://www.lfu.bayern.de/gdi/wms/energieatlas/planungsgrundlagen_solar` | `data/processed/2_technology_solar/reference/<gemeinde>_pv_freiflaechenkulisse_zoomstufe_1.png`, `data/processed/2_technology_solar/reference/<gemeinde>_pv_freiflaechenkulisse_zoomstufe_2.png` |

Hinweis: `scripts/2_2_solar/unused_prepare_solar_osm_streets.py` bleibt als
Reserve erhalten, ist aber aktuell kein aktiver Schritt im Solar-Workflow. Die
Solar-Korridorlogik nutzt `solar_corridor_basis` aus dem gemeinsamen
OSM-Netzwerkdownload.

## 4. Wasser

Wasser ist aktuell TODO/TBD. Die wasserbezogenen Skripte und Outputs werden
erst ergänzt, wenn die Wasser-Datengrundlagen und die fachliche Logik festgelegt
sind.

## 5. Kartenerzeugung

| Skriptname | Inputfiles | Outputfiles |
| --- | --- | --- |
| `scripts/3_generate_map/1_prepare_overview_layers.py` | `data/raw/Verwaltungsgebiet_Bayern/ALKIS-Vereinfacht/VerwaltungsEinheit.shp`, `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg` | `data/processed/1_base_overview/bayern_outline.gpkg`, `data/processed/1_base_overview/<gemeinde>_overview.gpkg` |
| `scripts/3_generate_map/2_create_map_qgis_project.py --technology wind` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, `data/processed/2_technology_wind/<gemeinde>_wind_layers.gpkg`, `data/processed/2_technology_wind/<gemeinde>_wind_ausschluss_gesamt.gpkg`, `data/processed/1_base_protection_areas/<gemeinde>_naturschutz_allgemein_hart.gpkg`, `data/processed/1_base_protection_areas/<gemeinde>_naturschutz_allgemein_weich.gpkg`, `data/processed/1_base_protection_areas/<gemeinde>_naturschutz_wind.gpkg` | `data/processed/3_qgis_projects/<gemeinde>_map_wind.qgz` mit sichtbaren Sammellayern und ausgeblendeten Detail- und Attributlayern |
| `scripts/3_generate_map/2_create_map_qgis_project.py --technology solar` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, `data/processed/2_technology_solar/<gemeinde>_solar_layers.gpkg`, `data/processed/2_technology_solar/<gemeinde>_landuse_solar_ausschluss.gpkg`, `data/processed/2_technology_solar/<gemeinde>_landuse_solar_pv_freiflaechen_naehung_vektorlayer.gpkg`, `data/processed/2_technology_solar/reference/<gemeinde>_pv_freiflaechenkulisse_zoomstufe_1.png`, `data/processed/2_technology_solar/reference/<gemeinde>_pv_freiflaechenkulisse_zoomstufe_2.png`, `data/processed/1_base_protection_areas/<gemeinde>_naturschutz_allgemein_hart.gpkg`, `data/processed/1_base_protection_areas/<gemeinde>_naturschutz_allgemein_weich.gpkg` | `data/processed/3_qgis_projects/<gemeinde>_map_solar.qgz` |
| `scripts/3_generate_map/3_generate_map_pdf.py --technology wind` | `data/processed/3_qgis_projects/<gemeinde>_map_wind.qgz`, `data/processed/1_base_overview/bayern_outline.gpkg`, `data/processed/1_base_overview/<gemeinde>_overview.gpkg` | `data/processed/3_maps/<gemeinde>_map_wind.pdf` mit erweiterter Legende, Nordpfeil in der Karte und kleiner Übersichtskarte |
| `scripts/3_generate_map/3_generate_map_pdf.py --technology solar` | `data/processed/3_qgis_projects/<gemeinde>_map_solar.qgz`, `data/processed/1_base_overview/bayern_outline.gpkg`, `data/processed/1_base_overview/<gemeinde>_overview.gpkg` | `data/processed/3_maps/<gemeinde>_map_solar.pdf` |
## Hinweis zu OSM

Das OSM-Skript schreibt zuerst immer den gemeinsamen Rohdatensatz
`osm_streets`. Die fachliche Filterung passiert danach in den
Technologieordnern. Für Solar wird zusätzlich `solar_corridor_basis`
geschrieben, weil die 200-m- und 500-m-Puffer Autobahnen und Schienenwege als
eigene Grundlage brauchen.

## Hinweis zu QGIS-Projekt und PDF

Die QGIS-Projekte enthalten bewusst mehr Layer als die PDF-Karten zeigen. Die
sichtbaren Kartenlayer bleiben zusammengefasst, damit die Karte lesbar bleibt.
Zusätzlich werden ausgeblendete Detail- und Attributlayer geladen. Diese
dienen der Analyse, Attributprüfung und Dokumentation, zum Beispiel für:

- einzelne Naturschutz-Ursprungslayer
- einzelne Landnutzungs- und OSM-Ausschlusslayer
- technische Zwischenlayer vor der finalen Aggregation

Die PDF-Karte verwendet nur die sichtbaren Layer des QGIS-Projekts. Dadurch
bleiben Detaildaten im Projekt verfügbar, ohne die finale Karte zu überladen.

Für die Wind-PDF ist zusätzlich eine Layout-Feinabstimmung dokumentiert:

- der Legendeneintrag `Ausschlussflächen durch Landnutzung` soll in der
  finalen PDF auf `Nutzungsausschluss` gekürzt werden
- der Straßeneintrag soll als Legendenkasten mit horizontaler Linie
  dargestellt werden
- die Übersichtskarte nutzt vorbereitete Locator-Layer aus `data/processed/1_base_overview/`
- der Bayern-Außenumriss wird einmalig erzeugt und danach wiederverwendet
- die gewählte Gemeinde wird in der Übersichtskarte als rote Fläche markiert
- die Übersichtskarte wird nur eingefügt, wenn sie im Hauptkartenbild keinen
  relevanten Teil der Gemeinde verdeckt

Diese letzte Regel ist wichtig für Gemeinden mit sehr unterschiedlicher Größe
oder Lage im Kartenrahmen. Die Pipeline bevorzugt in diesem Fall die Lesbarkeit
der Hauptkarte gegenüber einer immer erzwungenen Locator Map.

Die genauere Beschreibung steht in
[WIND_WORKFLOW_NOTES.md](WIND_WORKFLOW_NOTES.md).

