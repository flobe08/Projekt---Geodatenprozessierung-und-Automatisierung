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
  2_technology_wasser/

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

## Kennzeichnung der Verwendung

Die Spalten `In finaler PDF` und `Im QGIS-Projekt als Detail-/Attributlayer`
zeigen, wie ein Output später genutzt wird.

| Wert | Bedeutung |
| --- | --- |
| `ja` | Der Output wird direkt verwendet. |
| `teilweise` | Nur einzelne Layer, abgeleitete Layer oder optionale Teile werden verwendet. |
| `nein` | Der Output wird dort nicht direkt verwendet. |

Die QGIS-Projekte enthalten bewusst mehr Layer als die PDF-Karten. Die sichtbare
PDF bleibt kartografisch reduziert, während Detail- und Attributlayer im
QGIS-Projekt für Prüfung, Attributtabellen und Dokumentation verfügbar bleiben.

Für Wasser werden die amtlichen WMS-Referenzbilder getrennt abgelegt:

```text
data/processed/2_technology_wasser/reference/
```

## 1. Gemeinsame Datenvorbereitung

| Skriptname | Inputfiles / Quellen | Outputfiles | In finaler PDF | Im QGIS-Projekt als Detail-/Attributlayer |
| --- | --- | --- | --- | --- |
| `scripts/1_prepare_data/1_download_data.py` | Offizielle Downloadquellen für Verwaltungsgrenzen, Landnutzung, Schutzgebiete, Natura-2000-Daten und technologieabhängige Rohdaten | `data/raw/Verwaltungsgebiet_Bayern/alkis_verwaltungsgebiete.zip`, `data/raw/Verwaltungsgebiet_Bayern/`, `data/raw/landuse/landnutzung.gpkg`, `data/raw/schutzgebiete/`, `data/raw/wind/` | nein | nein |
| `scripts/1_prepare_data/2_extract_municipality_boundary.py` | `data/raw/Verwaltungsgebiet_Bayern/` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg` | ja | ja |
| `scripts/1_prepare_data/3_build_protection_layers.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, `data/raw/schutzgebiete/`, `data/raw/wind/vogelkulissen_2024/` | `data/processed/1_base_protection_areas/<gemeinde>_naturschutz_allgemein_hart.gpkg`, `data/processed/1_base_protection_areas/<gemeinde>_naturschutz_allgemein_weich.gpkg`, `data/processed/1_base_protection_areas/<gemeinde>_naturschutz_wind.gpkg` | ja | ja |
| `scripts/1_prepare_data/4_clip_landuse.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, `data/raw/landuse/landnutzung.gpkg` | `data/processed/1_base_landuse/landnutzung_<gemeinde>.gpkg` | nein | ja |
| `scripts/1_prepare_data/5_download_osm_network_data.py --technology wind` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, Overpass API | `data/processed/1_base_osm_streets/<gemeinde>_osm_streets.gpkg`, `data/processed/1_base_osm_streets/<gemeinde>_osm_streets_raw.json` | teilweise | ja |
| `scripts/1_prepare_data/5_download_osm_network_data.py --technology solar` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, Overpass API | `data/processed/1_base_osm_streets/<gemeinde>_osm_streets.gpkg`, `data/processed/1_base_osm_streets/<gemeinde>_osm_streets_raw.json`, `data/processed/2_technology_solar/corridor/<gemeinde>_solar_corridor_basis.gpkg`, `data/processed/2_technology_solar/corridor/<gemeinde>_solar_corridor_basis_raw.json` | ja | ja |
| `scripts/1_prepare_data/5_download_osm_network_data.py --technology wasser` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, Overpass API | `data/processed/1_base_osm_streets/<gemeinde>_osm_streets.gpkg`, `data/processed/1_base_osm_streets/<gemeinde>_osm_streets_raw.json` | nein | nein |

## 2. Wind

| Skriptname | Inputfiles | Outputfiles | In finaler PDF | Im QGIS-Projekt als Detail-/Attributlayer |
| --- | --- | --- | --- | --- |
| `scripts/2_1_wind/1_clip_wind_planning_areas.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, `data/raw/wind/wind_vorranggebiete.gpkg`, `data/raw/wind/wind_vorbehaltsgebiete.gpkg` | `data/processed/2_technology_wind/<gemeinde>_wind_layers.gpkg` | ja | ja |
| `scripts/2_1_wind/2_prepare_wind_landuse.py` | `data/processed/1_base_landuse/landnutzung_<gemeinde>.gpkg` | `data/processed/2_technology_wind/<gemeinde>_landuse_wind_ausschluss.gpkg`, `data/processed/2_technology_wind/<gemeinde>_landuse_wind_potenzial.gpkg`, `data/processed/2_technology_wind/<gemeinde>_landuse_wind_geeignet.gpkg`, `data/processed/2_technology_wind/<gemeinde>_landuse_wind_unused.gpkg` | nein | ja |
| `scripts/2_1_wind/3_build_wind_landuse_buffers.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, `data/processed/2_technology_wind/<gemeinde>_landuse_wind_ausschluss.gpkg` | `data/processed/2_technology_wind/<gemeinde>_landuse_wind_ausschluss_puffer.gpkg` | teilweise | ja |
| `scripts/2_1_wind/4_prepare_wind_osm_streets.py` | `data/processed/1_base_osm_streets/<gemeinde>_osm_streets.gpkg` | `data/processed/2_technology_wind/<gemeinde>_osm_wind_streets.gpkg`, `data/processed/2_technology_wind/<gemeinde>_osm_wind_streets_puffer.gpkg` | ja | ja |
| `scripts/2_1_wind/5_build_wind_exclusion_layer.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, `data/processed/2_technology_wind/<gemeinde>_landuse_wind_ausschluss_puffer.gpkg`, `data/processed/2_technology_wind/<gemeinde>_osm_wind_streets_puffer.gpkg` | `data/processed/2_technology_wind/<gemeinde>_wind_ausschluss_gesamt.gpkg` | ja | ja |

## 3. Solar

| Skriptname | Inputfiles | Outputfiles | In finaler PDF | Im QGIS-Projekt als Detail-/Attributlayer |
| --- | --- | --- | --- | --- |
| `scripts/2_2_solar/1_prepare_solar_corridor_layers.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, `data/processed/2_technology_solar/corridor/<gemeinde>_solar_corridor_basis.gpkg` | `data/processed/2_technology_solar/<gemeinde>_solar_layers.gpkg` | ja | ja |
| `scripts/2_2_solar/2_prepare_solar_landuse.py` | `data/processed/1_base_landuse/landnutzung_<gemeinde>.gpkg` | `data/processed/2_technology_solar/<gemeinde>_landuse_solar_ausschluss.gpkg`, `data/processed/2_technology_solar/<gemeinde>_landuse_solar_pv_freiflaechen_naehung_vektorlayer.gpkg`, `data/processed/2_technology_solar/<gemeinde>_landuse_solar_unused.gpkg` | nein | ja |
| `scripts/2_2_solar/3_download_solar_reference_wms.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, WMS `https://www.lfu.bayern.de/gdi/wms/energieatlas/planungsgrundlagen_solar` | `data/processed/2_technology_solar/reference/<gemeinde>_pv_freiflaechenkulisse_zoomstufe_1.png`, `data/processed/2_technology_solar/reference/<gemeinde>_pv_freiflaechenkulisse_zoomstufe_2.png` | ja | nein |

Hinweis: `scripts/2_2_solar/unused_prepare_solar_osm_streets.py` bleibt als
Reserve erhalten, ist aber aktuell kein aktiver Schritt im Solar-Workflow. Die
Solar-Korridorlogik nutzt `solar_corridor_basis` aus dem gemeinsamen
OSM-Netzwerkdownload.

## 4. Wasser

| Skriptname | Inputfiles | Outputfiles | In finaler PDF | Im QGIS-Projekt als Detail-/Attributlayer |
| --- | --- | --- | --- | --- |
| `scripts/2_3_wasser/2_build_wasser_protection_layers.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, `data/raw/wasser/wasserschutzgebiete/trinkwasserschutzgebiete/`, `data/raw/wasser/wasserschutzgebiete/heilquellenschutzgebiete/` | `data/processed/2_technology_wasser/<gemeinde>_wasserschutz_hart.gpkg` mit `trinkwasserschutzgebiete`, `heilquellenschutzgebiete`, `wasserschutz_hart_merged` | ja | ja |
| `scripts/2_3_wasser/1_download_wasser_reference_wms.py` | `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg`, WMS `https://www.lfu.bayern.de/gdi/wms/energieatlas/wasserkraftanlagen`, WMS `https://www.lfu.bayern.de/gdi/wms/wasser/ueberschwemmungsgebiete` | `data/processed/2_technology_wasser/reference/<gemeinde>_wasserkraftanlagen.png`, `data/processed/2_technology_wasser/reference/<gemeinde>_neubaupotenzial_querbauwerke.png`, `data/processed/2_technology_wasser/reference/<gemeinde>_modernisierung_nachruestung.png`, `data/processed/2_technology_wasser/reference/<gemeinde>_ueberschwemmungsgebiete_festgesetzt_hart.png`, `data/processed/2_technology_wasser/reference/<gemeinde>_ueberschwemmungsgebiete_vorlaeufig_hart.png`, `data/processed/2_technology_wasser/reference/<gemeinde>_hochwassergefahren_hq100_weich.png`, `data/processed/2_technology_wasser/reference/<gemeinde>_hochwassergefahren_hqextrem_weich.png`, jeweils mit `.pgw` und `.prj`, plus `<gemeinde>_wasser_wms_reference.json` | ja | nein |

## 5. Kartenerzeugung

| Skriptname | Inputfiles | Outputfiles | In finaler PDF | Im QGIS-Projekt als Detail-/Attributlayer |
| --- | --- | --- | --- | --- |
| `scripts/3_generate_map/1_prepare_overview_layers.py` | `data/raw/Verwaltungsgebiet_Bayern/ALKIS-Vereinfacht/VerwaltungsEinheit.shp`, `data/processed/1_base_boundaries/<gemeinde>_boundary.gpkg` | `data/processed/1_base_overview/bayern_outline.gpkg`, `data/processed/1_base_overview/<gemeinde>_overview.gpkg` | teilweise | ja |
| `scripts/3_generate_map/2_create_map_qgis_project.py --technology wind` | Wind-, Naturschutz-, Landnutzungs-, OSM- und Übersichtslayer | `data/processed/3_qgis_projects/<gemeinde>_map_wind.qgz` | nein | ja |
| `scripts/3_generate_map/2_create_map_qgis_project.py --technology solar` | Solar-, Naturschutz-, Landnutzungs-, WMS-Referenz- und Übersichtslayer | `data/processed/3_qgis_projects/<gemeinde>_map_solar.qgz` | nein | ja |
| `scripts/3_generate_map/2_create_map_qgis_project.py --technology wasser` | Wasser-, Naturschutz-, WMS-Referenz- und Übersichtslayer | `data/processed/3_qgis_projects/<gemeinde>_map_wasser.qgz` | nein | ja |
| `scripts/3_generate_map/3_generate_map_pdf.py --technology wind` | `data/processed/3_qgis_projects/<gemeinde>_map_wind.qgz`, Übersichtslayer | `data/processed/3_maps/<gemeinde>_map_wind.pdf` | ja | nein |
| `scripts/3_generate_map/3_generate_map_pdf.py --technology solar` | `data/processed/3_qgis_projects/<gemeinde>_map_solar.qgz`, Übersichtslayer | `data/processed/3_maps/<gemeinde>_map_solar.pdf` | ja | nein |
| `scripts/3_generate_map/3_generate_map_pdf.py --technology wasser` | `data/processed/3_qgis_projects/<gemeinde>_map_wasser.qgz`, Übersichtslayer | `data/processed/3_maps/<gemeinde>_map_wasser.pdf` | ja | nein |

## Hinweis zu OSM

Das OSM-Skript schreibt zuerst immer den gemeinsamen Rohdatensatz
`osm_streets`. Die fachliche Filterung passiert danach in den
Technologieordnern. Für Solar wird zusätzlich `solar_corridor_basis`
geschrieben, weil die 200-m- und 500-m-Korridore Autobahnen und Schienenwege als
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

- der Legendeneintrag `Nutzungsausschluss` fasst Landnutzungs- und
  Straßenausschlüsse kartografisch zusammen
- der Straßeneintrag wird als Legendenkasten mit horizontaler Linie dargestellt
- die Übersichtskarte nutzt vorbereitete Locator-Layer aus
  `data/processed/1_base_overview/`
- der Bayern-Außenumriss wird einmalig erzeugt und danach wiederverwendet
- die gewählte Gemeinde wird in der Übersichtskarte markiert
- die Übersichtskarte wird nur eingefügt, wenn sie im Hauptkartenbild keinen
  relevanten Teil der Gemeinde verdeckt

Diese letzte Regel ist wichtig für Gemeinden mit sehr unterschiedlicher Größe
oder Lage im Kartenrahmen. Die Pipeline bevorzugt in diesem Fall die Lesbarkeit
der Hauptkarte gegenüber einer immer erzwungenen Locator Map.

Die genauere Beschreibung steht in
[WIND_WORKFLOW_NOTES.md](WIND_WORKFLOW_NOTES.md).

