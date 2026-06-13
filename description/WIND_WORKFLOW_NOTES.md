# Wind Workflow Notes

## Core Idea

The current project version uses a simpler and more defensible wind workflow:

1. official municipality boundary
2. official wind planning result layers from the Bavarian regional planning WFS
3. optional OSM roads only as context

That means the project no longer tries to derive wind suitability mainly from
landuse and self-defined buffers.

## Why This Version Is Better

For the course topic, this version is easier to justify because:

- the study area comes from an official administrative dataset
- the wind layer comes from the official regional planning context
- the result can be reproduced for another municipality
- the outputs go directly into QGIS and PDF

## Current Workflow

### 1. Download raw datasets

Script:

- `scripts/prepare_data/0_download_data.py`

What it does:

- downloads the Bavarian ALKIS administrative boundary ZIP
- extracts it locally
- downloads the required wind WFS layers directly as GeoPackages

Expected wind raw files:

- `data/raw/wind/wind_vorranggebiete.gpkg`
- `data/raw/wind/wind_vorbehaltsgebiete.gpkg`

Zusätzliche Verifikation:

- Die automatisch geladenen WFS-Daten wurden manuell in QGIS geöffnet.
- Die WFS-Layer wurden zusätzlich direkt über die QGIS-WFS-Verbindung geprüft.
- Die Windflächen wurden mit der Gemeindegrenze von Drachselsried abgeglichen.

### 2. Extract municipality boundary

Script:

- `scripts/prepare_data/1_grenzen.py`

Output:

- `data/processed/boundaries/<municipality>_boundary.gpkg`

### 3. Clip wind planning datasets

Script:

- `scripts/wind/3_clip_wind_planning_areas.py`

Output:

- `data/processed/wind/<municipality>_wind_layers.gpkg`

Possible output layers:

- `wind_vorranggebiete`
- `wind_vorbehaltsgebiete`

### 4. Optionally add OSM context

Handled in:

- `scripts/prepare_data/0_download_data.py --with-osm-context`

Output:

- `data/processed/osm_context/<municipality>_osm_context.gpkg`
- `data/processed/osm_context/<municipality>_osm_context_raw.json`

This OSM part means:

- optional roads and highways
- only for visual orientation
- not for the official wind planning decision itself

### 5. Create QGIS project

Script:

- `scripts/generate_map/4_create_map_qgis_project.py`

### 6. Export PDF map

Script:

- `scripts/generate_map/5_generate_map_pdf.py`

## What The WFS Datasets Are

The WFS datasets are official regional planning result layers from the Bavaria
regional planning service:

- `Vorranggebiet fuer die Errichtung von Windenergieanlagen`
- `Vorbehaltsgebiet fuer die Errichtung von Windenergieanlagen`

Technical WFS layer names used in the script:

- `WFS_Regionalplanung:Vorranggebiet_Windenergienutzung`
- `WFS_Regionalplanung:Vorbehaltsgebiet_Windenergienutzung`

Useful links:

- WFS service:
  [https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung](https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung)
- GetCapabilities:
  [https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung?service=WFS&request=GetCapabilities](https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung?service=WFS&request=GetCapabilities)
- Regional plan background:
  [https://www.landesentwicklung-bayern.de/instrumente/regionalplaene.html](https://www.landesentwicklung-bayern.de/instrumente/regionalplaene.html)

## What They Consider, And What We Can Safely Claim

This is the important distinction for the report:

- these WFS layers are planning **results**
- they are not a full machine-readable explanation of every criterion
- the WFS itself does not document every single reason per polygon

So we should **not** claim:

- that the workflow independently proves all underlying criteria
- that the WFS alone fully explains species protection, settlement distance,
  military restrictions, or every planning conflict

What we **can** claim:

- the layers are official regional planning designations
- they already reflect a planning and balancing process
- they are more reliable for this project than a self-derived proxy from
  landuse plus buffers
- the exact detailed justifications must be read in the respective regional
  plan texts and explanatory documents

That limitation is not a weakness. It is actually a clean and honest project
statement.

## Why OSM Is Still Included

OSM is still useful, but only in a supporting role:

- roads make the map easier to read
- municipalities are easier to interpret visually
- the user can orient themselves in QGIS and in the PDF

So in the current workflow:

- WFS wind layers = main thematic data
- OSM roads = optional context data

## How To Describe This In The Report

Good wording for the report is:

- The municipality boundary was derived from the Bavarian ALKIS
  administrative dataset.
- The wind layer was derived from official regional planning WFS exports from
  Bavaria.
- OpenStreetMap roads were added optionally as contextual map information.
- The workflow does not derive wind suitability independently from raw
  environmental criteria, but processes official planning result layers into a
  reproducible municipality-level QGIS and PDF workflow.

## Current Limitation

The complete workflow is currently implemented only for:

- `wind`

`solar` and `wasser` still exist only as CLI placeholders for later
extensions.
