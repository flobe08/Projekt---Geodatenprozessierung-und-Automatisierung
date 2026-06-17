# Wind Workflow Notes

## Core idea

The current wind workflow uses a defensible and reproducible approach:

1. official municipality boundary
2. official wind planning result layers from the Bavarian WFS
3. optional cartographic context only in the final map

The project therefore does **not** derive wind suitability mainly from self-made
buffers or landuse proxies.

## Current script order

1. `scripts/1_prepare_data/1_download_data.py`
2. `scripts/1_prepare_data/2_extract_municipality_boundary.py`
3. `scripts/1_prepare_data/3_build_protection_layers.py`
4. `scripts/1_prepare_data/4_clip_landuse.py`
5. `scripts/1_prepare_data/5_download_osm_network_data.py --technology wind`
6. `scripts/2_1_wind/1_clip_wind_planning_areas.py`
7. `scripts/2_1_wind/2_prepare_wind_landuse.py`
8. `scripts/2_1_wind/3_build_wind_landuse_buffers.py`
9. `scripts/2_1_wind/4_prepare_wind_osm_streets.py`
10. `scripts/2_1_wind/5_build_wind_exclusion_layer.py`
11. `scripts/3_generate_map/1_create_map_qgis_project.py`
12. `scripts/3_generate_map/2_generate_map_pdf.py`

## Main datasets

### Administrative boundary

- Source: Bavarian ALKIS administrative dataset
- Output: `data/processed/boundaries/<municipality>_boundary.gpkg`

### Official wind planning datasets

- `wind_vorranggebiete.gpkg`
- `wind_vorbehaltsgebiete.gpkg`

### Official municipality landuse

- source: `data/raw/landuse/landnutzung.gpkg`
- municipality clip:
  `data/processed/landuse/landnutzung_<municipality>.gpkg`

Additional wind-specific working outputs:

- `data/processed/wind/<municipality>_landuse_wind_ausschluss.gpkg`
- `data/processed/wind/<municipality>_landuse_wind_potenzial.gpkg`
- `data/processed/wind/<municipality>_landuse_wind_geeignet.gpkg`
- `data/processed/wind/<municipality>_landuse_wind_unused.gpkg`
- `data/processed/wind/<municipality>_landuse_wind_ausschluss_puffer.gpkg`
- `data/processed/wind/<municipality>_wind_ausschluss_gesamt.gpkg`

Hinweis:

- Die Landnutzungs-Outputs sind aktuell Arbeits- und Prüflayer.
- Sie sind im QGIS-Projektskript bereits als nächste TODO-Stufe vorbereitet,
  aber noch nicht aktiv in die finale Windkarte eingebunden.

### OSM-Straßendaten

- `data/processed/osm_streets/<municipality>_osm_streets.gpkg`
- `data/processed/wind/<municipality>_osm_wind_streets.gpkg`
- `data/processed/wind/<municipality>_osm_wind_streets_puffer.gpkg`

Wichtige Layer:

- `osm_streets_raw`
- `osm_streets_wind_ausschluss`

Hinweis:

- Der technologiespezifische OSM-Ausschlusslayer ist aktuell ebenfalls nur
  vorbereitet und noch nicht aktiv in die finale Windkarte eingebunden.

### Aktueller Kartenstand

Die aktuelle Windkarte bindet bereits ein:

- offizielle Wind-Vorranggebiete
- offizielle Wind-Vorbehaltsgebiete
- harte allgemeine Naturschutz-Restriktionen
- weiche allgemeine Naturschutz-Konfliktflächen
- windspezifische Naturschutz-Restriktionen

Zusätzlich vorbereitet, aber noch bewusst nicht aktiv eingebunden:

- `landuse_wind_ausschluss_puffer`
- `osm_streets_wind_ausschluss_puffer`
- `wind_ausschluss_gesamt`

Diese beiden Layer stehen im QGIS-Projektskript bereits als `TODO` bereit und
werden später zugeschaltet, sobald die endgültige Ausschlusslogik feststeht.

Aktueller Stand: `wind_ausschluss_gesamt` wird im QGIS-Projekt bereits als
Prüflayer geladen, ist aber standardmäßig ausgeblendet. Dadurch kann der
Layer manuell aktiviert und geprüft werden, ohne die automatisch erzeugte
PDF-Karte direkt zu verändern.

### General protection datasets

- official LfU protection area downloads
- municipality outputs:
  - `data/processed/schutzgebiete/<municipality>_naturschutz_allgemein_hart.gpkg`
  - `data/processed/schutzgebiete/<municipality>_naturschutz_allgemein_weich.gpkg`
  - `data/processed/schutzgebiete/<municipality>_naturschutz_wind.gpkg`

The current protection workflow separates:

- `naturschutz_allgemein_hart`
- `naturschutz_allgemein_weich`

The wind-specific planning result is additionally available as:

- `naturschutz_wind`

Technical WFS layer names:

- `WFS_Regionalplanung:Vorranggebiet_Windenergienutzung`
- `WFS_Regionalplanung:Vorbehaltsgebiet_Windenergienutzung`

Useful links:

- WFS service:
  [https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung](https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung)
- GetCapabilities:
  [https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung?service=WFS&request=GetCapabilities](https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung?service=WFS&request=GetCapabilities)
- Background:
  [https://www.landesentwicklung-bayern.de/instrumente/regionalplaene.html](https://www.landesentwicklung-bayern.de/instrumente/regionalplaene.html)

## What we can claim in the report

These wind layers are official planning **results**. They already reflect a
regional planning process, but the WFS itself does not explain every criterion
per polygon.

So we should not claim:

- that the pipeline independently proves all underlying criteria
- that the WFS fully documents every species, settlement, military or planning
  conflict

What we can safely claim:

- the layers are official regional planning designations
- the workflow reproduces these official designations at municipality level
- the outputs are suitable for QGIS and PDF map production

## Validation

The wind workflow was checked manually in QGIS:

- official WFS layers loaded directly
- municipality boundary loaded separately
- manual clip compared with automated output

The detailed validation steps are documented in:

- [VERIFIKATION.md](VERIFIKATION.md)
