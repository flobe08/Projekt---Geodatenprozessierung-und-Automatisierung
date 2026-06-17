# Skript-Output-Übersicht

Diese Datei ordnet die wichtigsten Skripte ihren Eingabe- und Ausgabedaten zu.
Damit kann später jeder erzeugte Output wieder dem passenden Verarbeitungsschritt
zugeordnet werden.

Platzhalter:

- `<gemeinde>` steht z. B. für `drachselsried`
- `<technologie>` steht z. B. für `wind` oder `solar`

## 1. Gemeinsame Datenvorbereitung

| Skriptname | Inputfiles / Quellen | Outputfiles |
| --- | --- | --- |
| `scripts/1_prepare_data/1_download_data.py` | Offizielle Downloadquellen für Verwaltungsgrenzen, Landnutzung, Schutzgebiete, Natura-2000-Daten und technologieabhängige Rohdaten | `data/raw/Verwaltungsgebiet_Bayern/alkis_verwaltungsgebiete.zip`, `data/raw/Verwaltungsgebiet_Bayern/`, `data/raw/landuse/landnutzung.gpkg`, `data/raw/schutzgebiete/`, `data/raw/wind/` |
| `scripts/1_prepare_data/2_extract_municipality_boundary.py` | `data/raw/Verwaltungsgebiet_Bayern/` | `data/processed/boundaries/<gemeinde>_boundary.gpkg` |
| `scripts/1_prepare_data/3_build_protection_layers.py` | `data/processed/boundaries/<gemeinde>_boundary.gpkg`, `data/raw/schutzgebiete/`, `data/raw/wind/vogelkulissen_2024/` | `data/processed/schutzgebiete/<gemeinde>_naturschutz_allgemein_hart.gpkg`, `data/processed/schutzgebiete/<gemeinde>_naturschutz_allgemein_weich.gpkg`, `data/processed/schutzgebiete/<gemeinde>_naturschutz_wind.gpkg` |
| `scripts/1_prepare_data/4_clip_landuse.py` | `data/processed/boundaries/<gemeinde>_boundary.gpkg`, `data/raw/landuse/landnutzung.gpkg` | `data/processed/landuse/landnutzung_<gemeinde>.gpkg` |
| `scripts/1_prepare_data/5_download_osm_network_data.py --technology wind` | `data/processed/boundaries/<gemeinde>_boundary.gpkg`, Overpass API | `data/processed/osm_streets/<gemeinde>_osm_streets.gpkg`, `data/processed/osm_streets/<gemeinde>_osm_streets_raw.json` |
| `scripts/1_prepare_data/5_download_osm_network_data.py --technology solar` | `data/processed/boundaries/<gemeinde>_boundary.gpkg`, Overpass API | `data/processed/osm_streets/<gemeinde>_osm_streets.gpkg`, `data/processed/osm_streets/<gemeinde>_osm_streets_raw.json`, `data/processed/solar/<gemeinde>_solar_corridor_basis.gpkg`, `data/processed/solar/<gemeinde>_solar_corridor_basis_raw.json` |
| `scripts/1_prepare_data/5_download_osm_network_data.py --technology wasser` | `data/processed/boundaries/<gemeinde>_boundary.gpkg`, Overpass API | `data/processed/osm_streets/<gemeinde>_osm_streets.gpkg`, `data/processed/osm_streets/<gemeinde>_osm_streets_raw.json` |

## 2. Wind

| Skriptname | Inputfiles | Outputfiles |
| --- | --- | --- |
| `scripts/2_1_wind/1_clip_wind_planning_areas.py` | `data/processed/boundaries/<gemeinde>_boundary.gpkg`, `data/raw/wind/wind_vorranggebiete.gpkg`, `data/raw/wind/wind_vorbehaltsgebiete.gpkg` | `data/processed/wind/<gemeinde>_wind_layers.gpkg` |
| `scripts/2_1_wind/2_prepare_wind_landuse.py` | `data/processed/landuse/landnutzung_<gemeinde>.gpkg` | `data/processed/wind/<gemeinde>_landuse_wind_ausschluss.gpkg`, `data/processed/wind/<gemeinde>_landuse_wind_potenzial.gpkg`, `data/processed/wind/<gemeinde>_landuse_wind_geeignet.gpkg`, `data/processed/wind/<gemeinde>_landuse_wind_unused.gpkg` |
| `scripts/2_1_wind/3_build_wind_landuse_buffers.py` | `data/processed/boundaries/<gemeinde>_boundary.gpkg`, `data/processed/wind/<gemeinde>_landuse_wind_ausschluss.gpkg` | `data/processed/wind/<gemeinde>_landuse_wind_ausschluss_puffer.gpkg` |
| `scripts/2_1_wind/4_prepare_wind_osm_streets.py` | `data/processed/osm_streets/<gemeinde>_osm_streets.gpkg` | `data/processed/wind/<gemeinde>_osm_wind_streets.gpkg`, `data/processed/wind/<gemeinde>_osm_wind_streets_puffer.gpkg` |
| `scripts/2_1_wind/5_build_wind_exclusion_layer.py` | `data/processed/boundaries/<gemeinde>_boundary.gpkg`, `data/processed/wind/<gemeinde>_landuse_wind_ausschluss_puffer.gpkg`, `data/processed/wind/<gemeinde>_osm_wind_streets_puffer.gpkg` | `data/processed/wind/<gemeinde>_wind_ausschluss_gesamt.gpkg` |

## 3. Solar

| Skriptname | Inputfiles | Outputfiles |
| --- | --- | --- |
| `scripts/2_2_solar/1_download_solar_reference_wms.py` | `data/processed/boundaries/<gemeinde>_boundary.gpkg`, WMS `https://www.lfu.bayern.de/gdi/wms/energieatlas/planungsgrundlagen_solar` | `data/processed/solar_reference/<gemeinde>_pv_freiflaechenkulisse_zoomstufe_1.png`, `data/processed/solar_reference/<gemeinde>_pv_freiflaechenkulisse_zoomstufe_2.png` |
| `scripts/2_2_solar/2_prepare_solar_corridor_layers.py` | `data/processed/boundaries/<gemeinde>_boundary.gpkg`, `data/processed/solar/<gemeinde>_solar_corridor_basis.gpkg` | `data/processed/solar/<gemeinde>_solar_layers.gpkg` |
| `scripts/2_2_solar/3_prepare_solar_landuse.py` | `data/processed/landuse/landnutzung_<gemeinde>.gpkg` | `data/processed/solar/<gemeinde>_landuse_solar_ausschluss.gpkg`, `data/processed/solar/<gemeinde>_landuse_solar_potenzial.gpkg`, `data/processed/solar/<gemeinde>_landuse_solar_geeignet.gpkg`, `data/processed/solar/<gemeinde>_landuse_solar_unused.gpkg` |
| `scripts/2_2_solar/4_prepare_solar_osm_streets.py` | `data/processed/osm_streets/<gemeinde>_osm_streets.gpkg` | `data/processed/solar/<gemeinde>_osm_solar_streets.gpkg`, `data/processed/solar/<gemeinde>_osm_solar_streets_puffer.gpkg` |

## 4. Wasser

| Skriptname | Inputfiles | Outputfiles |
| --- | --- | --- |
| `scripts/2_3_wasser/1_prepare_water_landuse.py` | `data/processed/landuse/landnutzung_<gemeinde>.gpkg` | `data/processed/wasser/<gemeinde>_landuse_wasser_ausschluss.gpkg`, `data/processed/wasser/<gemeinde>_landuse_wasser_kontext.gpkg`, `data/processed/wasser/<gemeinde>_landuse_wasser_geeignet.gpkg`, `data/processed/wasser/<gemeinde>_landuse_wasser_unused.gpkg` |
| `scripts/2_3_wasser/2_prepare_water_osm_streets.py` | `data/processed/osm_streets/<gemeinde>_osm_streets.gpkg` | `data/processed/wasser/<gemeinde>_osm_wasser_streets.gpkg`, `data/processed/wasser/<gemeinde>_osm_wasser_streets_puffer.gpkg` |

## 5. Kartenerzeugung

| Skriptname | Inputfiles | Outputfiles |
| --- | --- | --- |
| `scripts/3_generate_map/1_create_map_qgis_project.py --technology wind` | `data/processed/boundaries/<gemeinde>_boundary.gpkg`, `data/processed/wind/<gemeinde>_wind_layers.gpkg`, `data/processed/wind/<gemeinde>_wind_ausschluss_gesamt.gpkg`, `data/processed/schutzgebiete/<gemeinde>_naturschutz_allgemein_hart.gpkg`, `data/processed/schutzgebiete/<gemeinde>_naturschutz_allgemein_weich.gpkg`, `data/processed/schutzgebiete/<gemeinde>_naturschutz_wind.gpkg` | `data/processed/qgis_projects/<gemeinde>_map_wind.qgz` |
| `scripts/3_generate_map/1_create_map_qgis_project.py --technology solar` | `data/processed/boundaries/<gemeinde>_boundary.gpkg`, `data/processed/solar/<gemeinde>_solar_layers.gpkg`, `data/processed/solar_reference/`, `data/processed/schutzgebiete/<gemeinde>_naturschutz_allgemein_hart.gpkg`, `data/processed/schutzgebiete/<gemeinde>_naturschutz_allgemein_weich.gpkg` | `data/processed/qgis_projects/<gemeinde>_map_solar.qgz` |
| `scripts/3_generate_map/2_generate_map_pdf.py --technology wind` | `data/processed/qgis_projects/<gemeinde>_map_wind.qgz` | `data/processed/maps/<gemeinde>_map_wind.pdf` |
| `scripts/3_generate_map/2_generate_map_pdf.py --technology solar` | `data/processed/qgis_projects/<gemeinde>_map_solar.qgz` | `data/processed/maps/<gemeinde>_map_solar.pdf` |

## Hinweis zu OSM

Das OSM-Skript schreibt zuerst immer den gemeinsamen Rohdatensatz
`osm_streets`. Die fachliche Filterung passiert danach in den
Technologieordnern. Für Solar wird zusätzlich `solar_corridor_basis`
geschrieben, weil die 200-m- und 500-m-Puffer Autobahnen und Schienenwege als
eigene Grundlage brauchen.
