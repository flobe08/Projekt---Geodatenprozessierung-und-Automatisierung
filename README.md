# Reproducible Pipeline for One Municipality

This project contains a reproducible geodata pipeline for one selected
municipality in Bavaria. The pipeline downloads the required raw datasets,
extracts the selected municipality boundary, and cuts the Bavaria
OpenStreetMap dataset to this boundary.

The workflow is designed so that another municipality and another energy
technology can be processed with command line arguments. Currently, the
technology-specific download workflow is implemented for wind energy.

## Prepare Environment

The recommended setup on Windows is WSL with Ubuntu. This is useful because
the pipeline needs the Linux command line tool `osmium` to cut an `.osm.pbf`
file and write a new `.osm.pbf` file.

Open PowerShell and start Ubuntu:

```powershell
wsl -d Ubuntu
```

In Ubuntu, go to the project folder. Windows drives are available under
`/mnt/<drive-letter>`. For example, a project on drive `E:` can be reached
under `/mnt/e`.

```bash
cd "/mnt/e/path/to/your/project"
```

Install the required system packages:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip osmium-tool
```

Create and activate a Python environment for WSL:

```bash
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
pip install -r requirements.txt
```

Check that `osmium` is available:

```bash
osmium --version
```

## Python Dependencies

`requirements.txt` is used in the setup step above and installs only the
Python dependencies. It does not install `osmium-tool`, because `osmium` is
not a Python package and must be installed as a system tool.

## Usage

Example for Drachselsried:

```bash
python pipeline.py --municipality Drachselsried --technology wind
```

## Usage (without pipeline)

```bash
python scripts/0_download_data.py --technology wind
python scripts/1_grenzen.py --municipality Drachselsried
python scripts/2_extract_osm.py --municipality Drachselsried
```

## Workflow

1. `scripts/0_download_data.py`
   Downloads the Bavaria OSM extract from Geofabrik and the Bavarian
   administrative boundary dataset.
2. `scripts/1_grenzen.py`
   Extracts the selected municipality from the administrative boundaries and
   writes it as a GeoPackage.
3. `scripts/2_extract_osm.py`
   Uses the municipality boundary from step 1 to cut the Bavaria OSM PBF file
   and writes a municipality-specific OSM PBF file.

## Input Data

Raw data is downloaded automatically and stored in `data/raw`:

- `data/raw/osm/bayern-latest.osm.pbf`
- `data/raw/Verwaltungsgebiet_Bayern/alkis_verwaltungsgebiete.zip`
- `data/raw/Verwaltungsgebiet_Bayern/ALKIS-Vereinfacht/VerwaltungsEinheit.shp`
- `data/raw/Verwaltungsgebiet_Bayern/ALKIS-Vereinfacht/VerwaltungsEinheit.shx`
- `data/raw/Verwaltungsgebiet_Bayern/ALKIS-Vereinfacht/VerwaltungsEinheit.dbf`
- `data/raw/Verwaltungsgebiet_Bayern/ALKIS-Vereinfacht/VerwaltungsEinheit.prj`
- `data/raw/Verwaltungsgebiet_Bayern/ALKIS-Vereinfacht/VerwaltungsEinheit.cpg`
- `data/raw/schutzgebiete/biosphaerenreservate`
- `data/raw/schutzgebiete/landschaftsschutzgebiete`
- `data/raw/schutzgebiete/nationalparke`
- `data/raw/schutzgebiete/naturparke`
- `data/raw/schutzgebiete/naturschutzgebiete`
- `data/raw/schutzgebiete/nationale_naturmonumente`
- `data/raw/schutzgebiete/geschuetzte_landschaftsbestandteile_punkte`
- `data/raw/schutzgebiete/geschuetzte_landschaftsbestandteile_flaechen`
- `data/raw/schutzgebiete/naturdenkmale_punkte`
- `data/raw/schutzgebiete/naturdenkmale_flaechen`
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
- `data/processed/osm/<municipality>_osm.pbf`

The boundary GeoPackage can be opened directly in QGIS. The resulting OSM PBF
can also be loaded into QGIS or converted in later processing steps.

## Reproducibility

The full workflow can be rerun with:

```bash
python pipeline.py --municipality <municipality-name> --technology wind
```

For another municipality, only the `--municipality` value has to be changed.
The pipeline then downloads missing input data, recreates the municipality
boundary, and cuts the OSM dataset again. With `--technology wind`, additional
wind-relevant raw datasets are downloaded.


## Submission Context

This pipeline is part of the topic "Reproducible pipeline for one
municipality". Further project steps can add official open datasets relevant
to energy infrastructure and spatial planning, such as protected areas,
distance buffers, restricted zones, power lines, substations, generators, and
large consumers. These layers should be cleaned, harmonized, reprojected, and
stored in a structured geospatial format for exploration in QGIS.

## Alternative: Miniconda

Instead of WSL, Miniconda can be used to install Python packages and
`osmium-tool` in one Conda environment:

```powershell
conda env create -f environment.yml
conda activate geodata-pipeline
```

This requires Miniconda to be installed first:

https://docs.conda.io/en/latest/miniconda.html
