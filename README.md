# Reproducible Pipeline for One Municipality

This project contains a reproducible geodata workflow for one selected
municipality in Bavaria. The workflow prepares official geodata and
OpenStreetMap highways for QGIS and can generate a basic QGIS project and PDF
map.

The workflow is split into two entry points:

- `scripts/prepare_data.py`: downloads and prepares data in the normal WSL
  Python environment.
- `scripts/generate_map.py`: creates a QGIS project and PDF map with the
  system QGIS Python environment.

This split is intentional because PyQGIS is not part of the normal Python
virtual environment.

## Project Structure

```text
scripts/
  prepare_data.py
  generate_map.py
  utils/
    utils.py
  prepare_data/
    0_download_data.py
    1_grenzen.py
    2_download_overpass_data.py
    3_clip_landuse.py
  generate_map/
    4_create_map_qgis_project.py
    5_generate_map_pdf.py
```

## Prepare Environment

The recommended setup on Windows is WSL with Ubuntu. This keeps the geodata
workflow reproducible and avoids Windows path issues.

## Quick Start for a New Machine

Clone the repository first:

```bash
git clone <repository-url>
cd Projekt---Geodatenprozessierung-und-Automatisierung
```

Start Ubuntu/WSL from PowerShell:

```powershell
wsl -d Ubuntu
```

If the repository is stored on a Windows drive, move to the project folder from
inside WSL. Windows drives are mounted under `/mnt/<drive-letter>`:

```bash
cd "/mnt/e/path/to/Projekt---Geodatenprozessierung-und-Automatisierung"
```

Install the required system packages:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip qgis python3-qgis
```

Create the project environment:

```bash
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
pip install -r requirements.txt
```

Run the complete workflow:

```bash
bash run_workflow.sh Drachselsried wind
```

The script first runs the normal Python data preparation inside `.venv-wsl`.
Afterwards it leaves the virtual environment and runs the QGIS map generation
with the system PyQGIS installation.

## Python Dependencies

`requirements.txt` installs only the Python dependencies. It does not install
QGIS or PyQGIS.

## QGIS / PyQGIS

`scripts/generate_map.py` uses the PyQGIS API to create a QGIS project and a
simple PDF map automatically.

PyQGIS is not part of the normal Python virtual environment and therefore
cannot be installed with `pip install -r requirements.txt`.

The map generation workflow must be executed with the QGIS Python environment,
for example after leaving the virtual environment:

```bash
deactivate
python3 scripts/generate_map.py --municipality Drachselsried --technology wind
```

The implementation is based on the official PyQGIS Developer Cookbook:

https://docs.qgis.org/3.44/de/docs/pyqgis_developer_cookbook/index.html

## Usage

Prepare all data for Drachselsried:

```bash
source .venv-wsl/bin/activate
python3 scripts/prepare_data.py --municipality Drachselsried --technology wind
```

Generate the QGIS project and PDF map afterwards:

```bash
deactivate
python3 scripts/generate_map.py --municipality Drachselsried --technology wind
```

## Usage Without Entry Points

The data preparation scripts can also be executed individually inside the
normal Python virtual environment:

```bash
python3 scripts/prepare_data/0_download_data.py --technology wind
python3 scripts/prepare_data/1_grenzen.py --municipality Drachselsried
python3 scripts/prepare_data/2_download_overpass_data.py --municipality Drachselsried
python3 scripts/prepare_data/3_clip_landuse.py --municipality Drachselsried
```

The map generation scripts require the QGIS Python environment:

```bash
python3 scripts/generate_map/4_create_map_qgis_project.py --municipality Drachselsried
python3 scripts/generate_map/5_generate_map_pdf.py --municipality Drachselsried
```

## Workflow

1. `scripts/prepare_data/0_download_data.py`
   Downloads the required raw datasets, including administrative boundaries,
   official landuse data, nature conservation datasets, and wind datasets.

2. `scripts/prepare_data/1_grenzen.py`
   Extracts the selected municipality from the administrative boundaries and
   writes it as a GeoPackage.

3. `scripts/prepare_data/2_download_overpass_data.py`
   Downloads OSM highways from Overpass, clips them to the municipality
   boundary, and writes the `osm_roads` layer to a GeoPackage.

4. `scripts/prepare_data/3_clip_landuse.py`
   Clips the official landuse dataset to the municipality boundary and writes
   the `official_landuse` layer to a municipality GeoPackage.

5. `scripts/generate_map/4_create_map_qgis_project.py`
   Creates a QGIS project containing an OpenStreetMap background layer,
   municipality boundary, OSM highways and official landuse.

6. `scripts/generate_map/5_generate_map_pdf.py`
   Exports a simple PDF map from the generated QGIS project.

## Input Data

Raw data is downloaded automatically and stored in `data/raw`:

- `data/raw/Verwaltungsgebiet_Bayern/alkis_verwaltungsgebiete.zip`
- `data/raw/landuse/landnutzung.gpkg`
- `data/raw/Verwaltungsgebiet_Bayern/ALKIS-Vereinfacht/VerwaltungsEinheit.shp`
- `data/raw/Verwaltungsgebiet_Bayern/ALKIS-Vereinfacht/VerwaltungsEinheit.shx`
- `data/raw/Verwaltungsgebiet_Bayern/ALKIS-Vereinfacht/VerwaltungsEinheit.dbf`
- `data/raw/Verwaltungsgebiet_Bayern/ALKIS-Vereinfacht/VerwaltungsEinheit.prj`
- `data/raw/Verwaltungsgebiet_Bayern/ALKIS-Vereinfacht/VerwaltungsEinheit.cpg`
- `data/raw/schutzgebiete/*`
- `data/raw/wind/natura2000/ffh`
- `data/raw/wind/natura2000/vogelschutz`
- `data/raw/wind/vogelkulissen_2024`

Raw data is not included in the repository because of file size.

The administrative boundary dataset is delivered as a Shapefile. A Shapefile
is not a single file, but a group of files:

- `.shp`: stores the geometry
- `.shx`: spatial index for the geometry
- `.dbf`: attribute table
- `.prj`: coordinate reference system
- `.cpg`: text encoding information

All of these files belong together and are required to read the Shapefile
correctly.

## Outputs

Processed data is written to `data/processed`:

- `data/processed/boundaries/<municipality>_boundary.gpkg`
- `data/processed/osm_highways/<municipality>_osm_highways.gpkg`
- `data/processed/landuse/landnutzung_<municipality>.gpkg`
- `data/processed/qgis_projects/<municipality>_map.qgz`
- `data/processed/maps/<municipality>_map.pdf`

The OSM highways GeoPackage contains the clipped OSM road layer. The clipped
official landuse is written to a separate municipality GeoPackage and can be
opened directly in QGIS.

## Reproducibility

The full workflow can be rerun with:

```bash
source .venv-wsl/bin/activate
python3 scripts/prepare_data.py --municipality <municipality-name> --technology wind

deactivate
python3 scripts/generate_map.py --municipality <municipality-name> --technology wind
```

For another municipality, only the `--municipality` value has to be changed.
The data preparation workflow then downloads missing input data, recreates the
municipality boundary, downloads OSM roads, and clips official landuse again.
With `--technology wind`, additional wind-relevant raw datasets are downloaded.

## Usage Summary

Recommended full workflow:

Start Ubuntu/WSL first:

```powershell
wsl -d Ubuntu
```

Go to the project folder:

```bash
cd "/mnt/e/path/to/Projekt---Geodatenprozessierung-und-Automatisierung"
```

Install the required system packages:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip qgis python3-qgis
```

Create the Python environment and install the Python requirements:

```bash
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
pip install -r requirements.txt
deactivate
```

Run the automatic workflow:

```bash
bash run_workflow.sh Drachselsried wind
```

For another municipality, replace `Drachselsried` with the municipality name.
For another technology, replace `wind` with `solar` or `wasser`.


## Submission Context

This workflow is part of the topic "Reproducible pipeline for one
municipality". Further project steps can add official open datasets relevant
to energy infrastructure and spatial planning, such as protected areas,
distance buffers, restricted zones, power lines, substations, generators, and
large consumers. These layers should be cleaned, harmonized, reprojected, and
stored in a structured geospatial format for exploration in QGIS.
