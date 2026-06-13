"""
Script 0: Download raw datasets.

This script downloads all raw input datasets needed by the pipeline. ZIP files
are extracted after download. The official landuse dataset is downloaded
directly as a GeoPackage file.
The datasets include administrative boundaries, official landuse data, nature
conservation data, and technology-specific datasets.
"""

from pathlib import Path
import argparse
import os
import requests
import sys
import zipfile

sys.path.append(str(Path(__file__).resolve().parent.parent / "utils"))
from utils import (
    ColoredArgumentParser,
    log_dataset,
    log_info,
    log_section,
    log_success,
    log_warning,
)

# Project root directory.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


def windows_long_path(path: Path) -> str:
    """Return a Windows-safe path string for long file paths."""

    resolved_path = str(path.resolve())

    if os.name == "nt" and not resolved_path.startswith("\\\\?\\"):
        return f"\\\\?\\{resolved_path}"

    return resolved_path


def display_path(path: Path) -> str:
    """Return a compact path for log messages."""

    try:
        return str(path.resolve().relative_to(BASE_DIR))
    except ValueError:
        return str(path)

# -----------------------------------------------------------------------------
# General base datasets used for every pipeline run.
# -----------------------------------------------------------------------------

# Geofabrik is only needed for the old osmium-based PBF cutting workflow.
# BAYERN_OSM_URL = "https://download.geofabrik.de/europe/germany/bayern-latest.osm.pbf"
ALKIS_VERWALTUNG_URL = "https://geodaten.bayern.de/odd/m/4/verwaltung/alkis-verwaltung.zip"
LANDUSE_URL = "https://geodaten.bayern.de/odd/m/3/daten/ln/landnutzung.gpkg"

# BAYERN_OSM_FILE = BASE_DIR / "data/raw/osm/bayern-latest.osm.pbf"
ALKIS_VERWALTUNG_FILE = BASE_DIR / "data/raw/Verwaltungsgebiet_Bayern/alkis_verwaltungsgebiete.zip"
ALKIS_EXTRACT_DIR = BASE_DIR / "data/raw/Verwaltungsgebiet_Bayern"
LANDUSE_FILE = BASE_DIR / "data/raw/landuse/landnutzung.gpkg"


# -----------------------------------------------------------------------------
# Schutzgebiete des Naturschutzes.
# Add the official LfU download links here.
# -----------------------------------------------------------------------------

BIOSPHAERENRESERVATE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/biosphaerenreservate_epsg25832_shp.zip"
LANDSCHAFTSSCHUTZGEBIETE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/lsg_epsg25832_shp.zip"
NATIONALPARKE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/nlp_epsg25832_shp.zip"
NATURPARKE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/naturparke_epsg25832_shp.zip"
NATURSCHUTZGEBIETE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/nsg_epsg25832_shp.zip"
NATIONALE_NATURMONUMENTE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/nationale_naturmonumente_epsg25832_shp.zip"
GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_PUNKTE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/landschaftsbestandteil_punktfoermig_epsg25832_shp.zip"
GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_FLAECHEN_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/landschaftsbestandteil_flaechig_epsg25832_shp.zip"
NATURDENKMALE_PUNKTE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/naturdenkmal_punktfoermig_epsg25832_shp.zip"
NATURDENKMALE_FLAECHEN_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/naturdenkmal_flaechig_epsg25832_shp.zip"

SCHUTZGEBIETE_RAW_DIR = BASE_DIR / "data/raw/schutzgebiete"

BIOSPHAERENRESERVATE_FILE = SCHUTZGEBIETE_RAW_DIR / "biosphaerenreservate.zip"
LANDSCHAFTSSCHUTZGEBIETE_FILE = SCHUTZGEBIETE_RAW_DIR / "landschaftsschutzgebiete.zip"
NATIONALPARKE_FILE = SCHUTZGEBIETE_RAW_DIR / "nationalparke.zip"
NATURPARKE_FILE = SCHUTZGEBIETE_RAW_DIR / "naturparke.zip"
NATURSCHUTZGEBIETE_FILE = SCHUTZGEBIETE_RAW_DIR / "naturschutzgebiete.zip"
NATIONALE_NATURMONUMENTE_FILE = SCHUTZGEBIETE_RAW_DIR / "nationale_naturmonumente.zip"
GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_PUNKTE_FILE = (SCHUTZGEBIETE_RAW_DIR / "geschuetzte_landschaftsbestandteile_punkte.zip")
GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_FLAECHEN_FILE = (SCHUTZGEBIETE_RAW_DIR / "geschuetzte_landschaftsbestandteile_flaechen.zip")
NATURDENKMALE_PUNKTE_FILE = SCHUTZGEBIETE_RAW_DIR / "naturdenkmale_punkte.zip"
NATURDENKMALE_FLAECHEN_FILE = SCHUTZGEBIETE_RAW_DIR / "naturdenkmale_flaechen.zip"

SCHUTZGEBIETE_DATASETS = [
    (BIOSPHAERENRESERVATE_URL, BIOSPHAERENRESERVATE_FILE, "biosphaerenreservate"),
    (LANDSCHAFTSSCHUTZGEBIETE_URL, LANDSCHAFTSSCHUTZGEBIETE_FILE, "landschaftsschutzgebiete"),
    (NATIONALPARKE_URL, NATIONALPARKE_FILE, "nationalparke"),
    (NATURPARKE_URL, NATURPARKE_FILE, "naturparke"),
    (NATURSCHUTZGEBIETE_URL, NATURSCHUTZGEBIETE_FILE, "naturschutzgebiete"),
    (NATIONALE_NATURMONUMENTE_URL, NATIONALE_NATURMONUMENTE_FILE, "nationale_naturmonumente"),
    (GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_PUNKTE_URL, GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_PUNKTE_FILE, "geschuetzte_landschaftsbestandteile_punkte",),
    (GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_FLAECHEN_URL, GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_FLAECHEN_FILE, "geschuetzte_landschaftsbestandteile_flaechen",),
    (NATURDENKMALE_PUNKTE_URL, NATURDENKMALE_PUNKTE_FILE, "naturdenkmale_punkte"),
    (NATURDENKMALE_FLAECHEN_URL, NATURDENKMALE_FLAECHEN_FILE, "naturdenkmale_flaechen"),
]


# -----------------------------------------------------------------------------
# Additional official datasets for self created buffers the wind_self-energy workflow.
# -----------------------------------------------------------------------------
NATURA2000_FFH_URL = (
    "https://www.lfu.bayern.de/gdi/dls/daten/natura2000/ffh_epsg25832_shp.zip"
)
NATURA2000_VOGELSCHUTZ_URL = (
    "https://www.lfu.bayern.de/gdi/dls/daten/natura2000/vogelschutz_epsg25832_shp.zip"
)
VOGELKULISSEN_2024_URL = (
    "https://www.lfu.bayern.de/natur/artenhilfsprogramme_voegel/"
    "wiesenbrueter/vogelkulissen_2024/doc/vogelkulissen24.zip"
)

WIND_RAW_DIR = BASE_DIR / "data/raw/wind_self"
NATURA2000_FFH_FILE = WIND_RAW_DIR / "natura2000_ffh_utm32.zip"
NATURA2000_VOGELSCHUTZ_FILE = WIND_RAW_DIR / "natura2000_vogelschutz_utm32.zip"
VOGELKULISSEN_2024_FILE = WIND_RAW_DIR / "vogelkulissen_2024.zip"
NATURA2000_EXTRACT_DIR = WIND_RAW_DIR / "natura2000"
VOGELKULISSEN_EXTRACT_DIR = WIND_RAW_DIR / "vogelkulissen_2024"

# -----------------------------------------------------------------------------
#  official datasets for the buffers for windenergy
# -----------------------------------------------------------------------------

(12)Wind_Donauwald_Url = "https://www.region-donau-wald.de/fileadmin/user_upload/pdfs/Regionalplan/laufende_Fortschreibungen/Windenergie/Beteiligungsverfahren/250714_DW_WindVRG_Exportdatei_Shape.zip"

def download_file(url: str, output_file: Path) -> None:
    """Download a file if it does not already exist."""

    output_file.parent.mkdir(parents=True, exist_ok=True)

    if output_file.exists():
        log_warning(f"Download skipped: {display_path(output_file)}")
        return

    log_info(f"Downloading: {url}")
    log_info(f"Saving to: {display_path(output_file)}")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)

    log_success(f"Saved: {display_path(output_file)}")


def has_extracted_geodata(extract_dir: Path) -> bool:
    """Check whether an extraction folder already contains geodata files."""

    geodata_suffixes = {".shp", ".gpkg", ".geojson", ".pbf"}

    return extract_dir.exists() and any(
        file.is_file()
        and file.stat().st_size > 0
        and file.suffix.lower() in geodata_suffixes
        for file in extract_dir.rglob("*")
    )


def download_and_unzip_dataset(
    dataset_name: str,
    url: str,
    zip_file: Path,
    extract_dir: Path,
) -> None:
    """Download and extract one dataset with compact status logs."""

    log_dataset(f"Dataset: {dataset_name}")
    download_file(url, zip_file)
    unzip_file(zip_file, extract_dir)


def download_wind_data() -> None:
    """Download official planning and restriction datasets relevant for wind_self."""

    log_section("Wind datasets")

    download_and_unzip_dataset(
        "natura2000_ffh",
        NATURA2000_FFH_URL,
        NATURA2000_FFH_FILE,
        NATURA2000_EXTRACT_DIR / "ffh",
    )
    download_and_unzip_dataset(
        "natura2000_vogelschutz",
        NATURA2000_VOGELSCHUTZ_URL,
        NATURA2000_VOGELSCHUTZ_FILE,
        NATURA2000_EXTRACT_DIR / "vogelschutz",
    )
    download_and_unzip_dataset(
        "vogelkulissen_2024",
        VOGELKULISSEN_2024_URL,
        VOGELKULISSEN_2024_FILE,
        VOGELKULISSEN_EXTRACT_DIR,
    )


def download_schutzgebiete_data() -> None:
    """Download official nature conservation area datasets when URLs are set."""

    log_section("Nature conservation (base datasets)")

    for url, zip_file, dataset_name in SCHUTZGEBIETE_DATASETS:
        if not url:
            log_warning(f"Skipping {dataset_name}: download URL not configured yet.")
            continue

        download_and_unzip_dataset(
            dataset_name,
            url,
            zip_file,
            SCHUTZGEBIETE_RAW_DIR / dataset_name,
        )


def download_base_data() -> None:
    """Download and extract datasets used by every technology workflow."""

    log_section("Base datasets")

    # The current workflow gets roads from Overpass and does not need this file.
    # log_dataset("Dataset: bayern_osm")
    # download_file(BAYERN_OSM_URL, BAYERN_OSM_FILE)

    download_and_unzip_dataset(
        "alkis_verwaltungsgebiet",
        ALKIS_VERWALTUNG_URL,
        ALKIS_VERWALTUNG_FILE,
        ALKIS_EXTRACT_DIR,
    )

    log_dataset("Dataset: landnutzung")
    download_file(LANDUSE_URL, LANDUSE_FILE)

    # download Nature conservation datasets
    download_schutzgebiete_data()


def download_technology_data(technology: str | None) -> None:
    """Download optional datasets for the selected technology."""

    match technology:
        case "wind_self":
            download_wind_data()
        case "solar":
            log_warning("No additional solar datasets configured yet.")
        case "wasser":
            log_warning("No additional wasser datasets configured yet.")
        case _:
            raise ValueError(f"Unknown technology: {technology}")


def unzip_file(zip_file: Path, extract_dir: Path) -> None:
    """Extract a zip file into the given folder."""

    if not zip_file.exists():
        raise FileNotFoundError(f"ZIP file not found: {zip_file}")

    if has_extracted_geodata(extract_dir):
        log_warning(f"Extraction skipped: {display_path(extract_dir)}")
        return

    log_info(f"Extracting: {display_path(zip_file)}")
    log_info(f"Extracting to: {display_path(extract_dir)}")

    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        for member in zip_ref.infolist():
            target_path = extract_dir / member.filename

            if member.is_dir():
                target_path.mkdir(parents=True, exist_ok=True)
                continue

            if target_path.suffix.lower() == ".pdf":
                log_warning(f"Skipping documentation file: {member.filename}")
                continue

            os.makedirs(windows_long_path(target_path.parent), exist_ok=True)

            with zip_ref.open(member) as source, open(
                windows_long_path(target_path), "wb"
            ) as target:
                target.write(source.read())

    log_success("Extraction finished.")


def main() -> None:
    """Download and extract all required raw datasets."""

    # Read selected technology for additional downloads.
    parser = ColoredArgumentParser(
        description="Download raw datasets for the geodata pipeline."
    )
    parser.add_argument(
        "--technology",
        required=True,
        choices=["wind","wind_self", "solar", "wasser"],
        help="Selected technology for additional datasets.",
    )
    args = parser.parse_args()

    # Step 1: Download datasets required for every pipeline run.
    download_base_data()

    # Step 2: Download additional datasets for the selected technology.
    download_technology_data(args.technology)


if __name__ == "__main__":
    main()
