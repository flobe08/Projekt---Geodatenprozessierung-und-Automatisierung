# Reproducible Wind Workflow for One Municipality

This project builds a reproducible wind-planning workflow for one municipality
in Bavaria. The current workflow is intentionally simple and stable:

1. Download the Bavarian administrative boundaries
2. Extract one municipality boundary
3. Clip official wind planning areas to this municipality
   (/4. Optionally download OSM context roads)
5. Store the results as GeoPackages
6. Create a QGIS project
7. Export a PDF map

The workflow is split into two entry points:

- `scripts/prepare_data.py` for normal Python data preparation
- `scripts/generate_map.py` for PyQGIS project and PDF generation

This split is required because PyQGIS is not installed through `pip`.

## Project Structure

```text
scripts/
  prepare_data.py
  generate_map.py
  prepare_data/
    0_download_data.py
    1_grenzen.py
  wind/
    3_clip_wind_planning_areas.py
  generate_map/
    4_create_map_qgis_project.py
    5_generate_map_pdf.py
    map_config.py
  utils/
    utils.py
```

## Recommended Setup

The recommended setup is WSL with Ubuntu on Windows.

Start WSL from PowerShell:

```powershell
wsl -d Ubuntu
```

Move into the project folder:

```bash
cd "/mnt/e/path/to/Projekt---Geodatenprozessierung-und-Automatisierung"
```

Install the required system packages:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip qgis python3-qgis
```

Create the Python environment for the preparation scripts:

```bash
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
pip install -r requirements.txt
deactivate
```

## Usage Summary

Recommended full workflow:

```bash
bash run_workflow.sh Drachselsried wind
```

Run the same workflow with optional OSM context roads:

```bash
bash run_workflow.sh Drachselsried wind --with-osm-context
```

## Step-by-Step Usage

Prepare the data only:

```bash
source .venv-wsl/bin/activate
python3 scripts/prepare_data.py --municipality Drachselsried --technology wind
deactivate
```

Prepare the data and also add optional OSM context roads:

```bash
source .venv-wsl/bin/activate
python3 scripts/prepare_data.py --municipality Drachselsried --technology wind --with-osm-context
deactivate
```

Generate the QGIS project and PDF map:

```bash
python3 scripts/generate_map.py --municipality Drachselsried --technology wind
```

## Run Every Script Manually

Data preparation:

```bash
source .venv-wsl/bin/activate
python3 scripts/prepare_data/0_download_data.py --technology wind
python3 scripts/prepare_data/1_grenzen.py --municipality Drachselsried
python3 scripts/prepare_data/0_download_data.py --technology wind --municipality Drachselsried --with-osm-context
python3 scripts/wind/3_clip_wind_planning_areas.py --municipality Drachselsried
deactivate
```

Map generation:

```bash
python3 scripts/generate_map/4_create_map_qgis_project.py --municipality Drachselsried --technology wind
python3 scripts/generate_map/5_generate_map_pdf.py --municipality Drachselsried --technology wind
```

## Workflow Explanation

### Step 1: Download raw datasets

`scripts/prepare_data/0_download_data.py`

This script:

- downloads the Bavarian administrative boundary ZIP
- extracts the ALKIS boundary dataset
- downloads the required wind GeoPackages directly from the official WFS

The wind data are now downloaded automatically from the official WFS.

### Step 2: Extract municipality boundary

`scripts/prepare_data/1_grenzen.py`

This script extracts one municipality from the Bavarian administrative
boundaries and writes:

- `data/processed/boundaries/<municipality>_boundary.gpkg`

### Step 3: Clip official wind areas to municipality

`scripts/wind/3_clip_wind_planning_areas.py`

This script reads the official wind datasets, clips them to the municipality
boundary, and writes:

- `data/processed/wind/<municipality>_wind_layers.gpkg`

The output can contain these layers:

- `wind_vorranggebiete_<municipality>`
- `wind_vorbehaltsgebiete_<municipality>`

### Step 4: Optionally download OSM context roads

`scripts/prepare_data/0_download_data.py --with-osm-context`

This optional download is handled inside script 0 after the municipality
boundary already exists. In this project, OSM does **not** define the wind
planning result. It is only used for orientation in QGIS and in the PDF map.

The OSM output is written to:

- `data/processed/osm_context/<municipality>_osm_context.gpkg`
- `data/processed/osm_context/<municipality>_osm_context_raw.json`

The GeoPackage contains the processed roads layer:

- `osm_context_roads`

### Step 5: Create QGIS project

`scripts/generate_map/4_create_map_qgis_project.py`

This script builds a QGIS project with:

- OSM web basemap
- municipality boundary
- clipped wind vorrang areas
- clipped wind vorbehalt areas
- optional OSM context roads

### Step 6: Export PDF map

`scripts/generate_map/5_generate_map_pdf.py`

This script exports an A4 landscape PDF map from the generated QGIS project.

## Input Data

### 1. Bavarian administrative boundaries

- downloaded automatically by script 0
- source dataset: ALKIS administrative boundaries for Bavaria

### 2. Official wind WFS exports

These are the key datasets for the wind workflow.

Expected files:

- `data/raw/wind/wind_vorranggebiete.gpkg`
- `data/raw/wind/wind_vorbehaltsgebiete.gpkg`

Recommended source:

- WFS service: [https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung](https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung)
- GetCapabilities: [https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung?service=WFS&request=GetCapabilities](https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung?service=WFS&request=GetCapabilities)
- Regional planning background: [https://www.landesentwicklung-bayern.de/instrumente/regionalplaene.html](https://www.landesentwicklung-bayern.de/instrumente/regionalplaene.html)

Recommended WFS layers:

- `Vorranggebiet fuer die Errichtung von Windenergieanlagen`
- `Vorbehaltsgebiet fuer die Errichtung von Windenergieanlagen`

Technical WFS layer names used in the automated download:

- `WFS_Regionalplanung:Vorranggebiet_Windenergienutzung`
- `WFS_Regionalplanung:Vorbehaltsgebiet_Windenergienutzung`

QGIS WFS connection, if you want to inspect the service manually:

1. `Layer > Layer hinzufügen > WFS/OGC API - Features-Layer hinzufügen`
2. Neue Verbindung anlegen
3. URL einfügen:

```text
https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung
```

4. Verbinden
5. Diese beiden Layer auswählen:
   - `Vorranggebiet für die Errichtung von Windenergieanlagen`
   - `Vorbehaltsgebiet für die Errichtung von Windenergieanlagen`

### 3. Optional OSM context roads

These roads are requested automatically from Overpass when
`--with-osm-context` is used in script 0 or in `scripts/prepare_data.py`.

In this project, "OSM data" means:

- optional road and highway line data
- used as contextual map information
- not used as the official planning basis

## What The WFS Datasets Are

The two WFS layers are official **regional planning result layers** from
Regionalplanung Bayern:

- `Vorranggebiet fuer die Errichtung von Windenergieanlagen`
- `Vorbehaltsgebiet fuer die Errichtung von Windenergieanlagen`

For the project, they are treated as official planning designations that are
already the result of a planning and balancing process.

## What The WFS Datasets Consider

This point is important for the written report:

- the WFS shows the final planning designations
- the WFS itself does **not** fully document every detailed criterion per area
- therefore the workflow should **not** claim that it independently proves or
  reconstructs all underlying criteria such as species protection, settlement
  distances, military constraints, or every planning trade-off

What can be said safely:

- the layers come from the official regional planning context in Bavaria
- they represent official planning outputs, not a self-derived proxy
- the detailed justification can vary by planning region and by planning
  update status
- exact explanations must be read in the responsible regional plan documents
  and explanatory texts, not in the WFS alone

That limitation is completely acceptable and should be stated explicitly in the
report.

## Output Data

Processed outputs are written here:

- `data/processed/boundaries/<municipality>_boundary.gpkg`
- `data/processed/wind/<municipality>_wind_layers.gpkg`
- `data/processed/osm_context/<municipality>_osm_context.gpkg`
- `data/processed/qgis_projects/<municipality>_map.qgz`
- `data/processed/maps/<municipality>_map.pdf`

## Why This Workflow Is Better Than The Older One

The older approach combined landuse and OSM context as the main thematic basis.
That was useful for experimentation, but weaker for a wind-planning topic.

The current workflow is stronger because:

- the municipality boundary comes from an official administrative dataset
- the wind layer comes from the official regional planning context
- OSM stays optional and clearly secondary
- the result is still reproducible and QGIS-ready

## Reproducibility

To rerun the workflow for another municipality, change only:

- `--municipality`
- optionally `--with-osm-context`

Example:

```bash
source .venv-wsl/bin/activate
python3 scripts/prepare_data.py --municipality Bodenmais --technology wind --with-osm-context
deactivate
python3 scripts/generate_map.py --municipality Bodenmais --technology wind
```

## Notes

- `wind` is the currently implemented full workflow.
- `solar` and `wasser` remain CLI placeholders for later extensions.
- PyQGIS scripts must run with the system QGIS Python environment, not inside
  the plain virtual environment.
