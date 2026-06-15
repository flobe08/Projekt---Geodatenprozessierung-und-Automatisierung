"""
Script 1: Prepare all raw datasets.

Workflow:
1. Download general datasets used by several technologies.
2. Download wind-specific datasets if the selected technology is wind.
3. Download solar-specific datasets if the selected technology is solar.
4. Download water-specific datasets if the selected technology is wasser.
"""

from pathlib import Path
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


BASE_DIR = Path(__file__).resolve().parent.parent.parent


# =============================================================================
# General datasets
# =============================================================================

# -----------------------------------------------------------------------------
# Administrative boundaries
# -----------------------------------------------------------------------------
ALKIS_VERWALTUNG_URL = "https://geodaten.bayern.de/odd/m/4/verwaltung/alkis-verwaltung.zip"
ALKIS_VERWALTUNG_FILE = BASE_DIR / "data/raw/Verwaltungsgebiet_Bayern/alkis_verwaltungsgebiete.zip"
ALKIS_EXTRACT_DIR = BASE_DIR / "data/raw/Verwaltungsgebiet_Bayern"


# -----------------------------------------------------------------------------
# Official landuse
# -----------------------------------------------------------------------------
LANDUSE_URL = "https://geodaten.bayern.de/odd/m/3/daten/ln/landnutzung.gpkg"
LANDUSE_FILE = BASE_DIR / "data/raw/landuse/landnutzung.gpkg"


# -----------------------------------------------------------------------------
# Official protection areas
# -----------------------------------------------------------------------------
SCHUTZGEBIETE_RAW_DIR = BASE_DIR / "data/raw/schutzgebiete"

BIOSPHAERENRESERVATE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/biosphaerenreservate_epsg25832_shp.zip"
BIOSPHAERENRESERVATE_FILE = SCHUTZGEBIETE_RAW_DIR / "biosphaerenreservate.zip"

LANDSCHAFTSSCHUTZGEBIETE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/lsg_epsg25832_shp.zip"
LANDSCHAFTSSCHUTZGEBIETE_FILE = SCHUTZGEBIETE_RAW_DIR / "landschaftsschutzgebiete.zip"

NATIONALPARKE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/nlp_epsg25832_shp.zip"
NATIONALPARKE_FILE = SCHUTZGEBIETE_RAW_DIR / "nationalparke.zip"

NATURPARKE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/naturparke_epsg25832_shp.zip"
NATURPARKE_FILE = SCHUTZGEBIETE_RAW_DIR / "naturparke.zip"

NATURSCHUTZGEBIETE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/nsg_epsg25832_shp.zip"
NATURSCHUTZGEBIETE_FILE = SCHUTZGEBIETE_RAW_DIR / "naturschutzgebiete.zip"

NATIONALE_NATURMONUMENTE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/nationale_naturmonumente_epsg25832_shp.zip"
NATIONALE_NATURMONUMENTE_FILE = SCHUTZGEBIETE_RAW_DIR / "nationale_naturmonumente.zip"

GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_PUNKTE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/landschaftsbestandteil_punktfoermig_epsg25832_shp.zip"
GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_PUNKTE_FILE = SCHUTZGEBIETE_RAW_DIR / "geschuetzte_landschaftsbestandteile_punkte.zip"

GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_FLAECHEN_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/landschaftsbestandteil_flaechig_epsg25832_shp.zip"
GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_FLAECHEN_FILE = SCHUTZGEBIETE_RAW_DIR / "geschuetzte_landschaftsbestandteile_flaechen.zip"

NATURDENKMALE_PUNKTE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/naturdenkmal_punktfoermig_epsg25832_shp.zip"
NATURDENKMALE_PUNKTE_FILE = SCHUTZGEBIETE_RAW_DIR / "naturdenkmale_punkte.zip"

NATURDENKMALE_FLAECHEN_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/naturdenkmal_flaechig_epsg25832_shp.zip"
NATURDENKMALE_FLAECHEN_FILE = SCHUTZGEBIETE_RAW_DIR / "naturdenkmale_flaechen.zip"

RAMSAR_GEBIETE_URL = "https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/ramsar_epsg25832_shp.zip"
RAMSAR_GEBIETE_FILE = SCHUTZGEBIETE_RAW_DIR / "ramsar_gebiete.zip"

SCHUTZGEBIETE_DATASETS = [
    (BIOSPHAERENRESERVATE_URL, BIOSPHAERENRESERVATE_FILE, "biosphaerenreservate"),
    (LANDSCHAFTSSCHUTZGEBIETE_URL, LANDSCHAFTSSCHUTZGEBIETE_FILE, "landschaftsschutzgebiete"),
    (NATIONALPARKE_URL, NATIONALPARKE_FILE, "nationalparke"),
    (NATURPARKE_URL, NATURPARKE_FILE, "naturparke"),
    (NATURSCHUTZGEBIETE_URL, NATURSCHUTZGEBIETE_FILE, "naturschutzgebiete"),
    (NATIONALE_NATURMONUMENTE_URL, NATIONALE_NATURMONUMENTE_FILE, "nationale_naturmonumente"),
    (
        GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_PUNKTE_URL,
        GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_PUNKTE_FILE,
        "geschuetzte_landschaftsbestandteile_punkte",
    ),
    (
        GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_FLAECHEN_URL,
        GESCHUETZTE_LANDSCHAFTSBESTANDTEILE_FLAECHEN_FILE,
        "geschuetzte_landschaftsbestandteile_flaechen",
    ),
    (NATURDENKMALE_PUNKTE_URL, NATURDENKMALE_PUNKTE_FILE, "naturdenkmale_punkte"),
    (NATURDENKMALE_FLAECHEN_URL, NATURDENKMALE_FLAECHEN_FILE, "naturdenkmale_flaechen"),
    (RAMSAR_GEBIETE_URL, RAMSAR_GEBIETE_FILE, "ramsar_gebiete"),
]


# -----------------------------------------------------------------------------
# Official Natura 2000 areas
# -----------------------------------------------------------------------------
NATURA2000_RAW_DIR = SCHUTZGEBIETE_RAW_DIR / "natura2000"

NATURA2000_FFH_URL = "https://www.lfu.bayern.de/gdi/dls/daten/natura2000/ffh_epsg25832_shp.zip"
NATURA2000_FFH_FILE = NATURA2000_RAW_DIR / "natura2000_ffh_utm32.zip"

NATURA2000_VOGELSCHUTZ_URL = "https://www.lfu.bayern.de/gdi/dls/daten/natura2000/vogelschutz_epsg25832_shp.zip"
NATURA2000_VOGELSCHUTZ_FILE = NATURA2000_RAW_DIR / "natura2000_vogelschutz_utm32.zip"

NATURA2000_DATASETS = [
    (NATURA2000_FFH_URL, NATURA2000_FFH_FILE, "ffh"),
    (NATURA2000_VOGELSCHUTZ_URL, NATURA2000_VOGELSCHUTZ_FILE, "vogelschutz"),
]


# =============================================================================
# Wind datasets
# =============================================================================

WIND_RAW_DIR = BASE_DIR / "data/raw/wind"
WIND_VORRANG_FILE = WIND_RAW_DIR / "wind_vorranggebiete.gpkg"
WIND_VORBEHALT_FILE = WIND_RAW_DIR / "wind_vorbehaltsgebiete.gpkg"

WFS_REGIONALPLANUNG_URL = "https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung"
WFS_VERSION = "2.0.0"
WFS_OUTPUT_FORMAT = "Geopackage"
WIND_VORRANG_TYPENAME = "WFS_Regionalplanung:Vorranggebiet_Windenergienutzung"
WIND_VORBEHALT_TYPENAME = "WFS_Regionalplanung:Vorbehaltsgebiet_Windenergienutzung"

# Wind-specific bird-area dataset used for the naturschutz_wind output.
VOGELKULISSEN_2024_URL = (
    "https://www.lfu.bayern.de/natur/artenhilfsprogramme_voegel/wiesenbrueter/vogelkulissen_2024/doc/vogelkulissen24.zip"
)
VOGELKULISSEN_2024_FILE = WIND_RAW_DIR / "vogelkulissen_2024.zip"
VOGELKULISSEN_2024_EXTRACT_DIR = WIND_RAW_DIR / "vogelkulissen_2024"


# =============================================================================
# Solar datasets
# =============================================================================

# TODO: no raw solar download is configured here yet.
# Solar currently creates its OSM transport data and WMS reference rasters in
# the solar-specific scripts because those inputs need the municipality
# boundary or the final map extent.


# =============================================================================
# Wasser datasets
# =============================================================================

# TODO: no raw water download is configured here yet.
# Later candidates are Gewässer, Wasserschutzgebiete, Überschwemmungsgebiete
# and Hochwasserschutzflächen.


# =============================================================================
# General helper functions
# =============================================================================

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


def download_file(url: str, output_file: Path) -> None:
    """Download a file if it does not already exist."""

    output_file.parent.mkdir(parents=True, exist_ok=True)

    if output_file.exists():
        log_warning(f"Download skipped: {display_path(output_file)}")
        return

    log_info(f"Downloading: {url}")
    log_info(f"Saving to: {display_path(output_file)}")

    response = requests.get(url, stream=True, timeout=180)
    response.raise_for_status()

    with open(output_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)

    log_success(f"Saved: {display_path(output_file)}")


def download_wfs_layer(
    dataset_label: str,
    type_name: str,
    output_file: Path,
) -> None:
    """Download one WFS layer directly as GeoPackage."""

    output_file.parent.mkdir(parents=True, exist_ok=True)
    log_dataset(f"Dataset: {dataset_label}")

    if output_file.exists() and output_file.stat().st_size > 0:
        log_warning(f"Download skipped: {display_path(output_file)}")
        return

    log_info(f"WFS layer: {type_name}")
    log_info(f"Source: {WFS_REGIONALPLANUNG_URL}")
    log_info(f"Saving to: {display_path(output_file)}")

    response = requests.get(
        WFS_REGIONALPLANUNG_URL,
        params={
            "service": "WFS",
            "version": WFS_VERSION,
            "request": "GetFeature",
            "typeNames": type_name,
            "outputFormat": WFS_OUTPUT_FORMAT,
        },
        stream=True,
        timeout=300,
    )
    response.raise_for_status()

    with open(output_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)

    if output_file.stat().st_size == 0:
        raise RuntimeError(f"Downloaded file is empty: {output_file}")

    log_success(f"Saved: {display_path(output_file)}")


def has_extracted_geodata(extract_dir: Path) -> bool:
    """Check whether an extraction folder already contains geodata files."""

    geodata_suffixes = {".shp", ".gpkg", ".geojson"}

    return extract_dir.exists() and any(
        file.is_file()
        and file.stat().st_size > 0
        and file.suffix.lower() in geodata_suffixes
        for file in extract_dir.rglob("*")
    )


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


# =============================================================================
# General download steps
# =============================================================================

def download_administrative_boundaries() -> None:
    """Download and extract the common administrative boundary dataset."""

    log_section("General datasets")
    log_dataset("Dataset: alkis_verwaltungsgebiet")
    download_file(ALKIS_VERWALTUNG_URL, ALKIS_VERWALTUNG_FILE)
    unzip_file(ALKIS_VERWALTUNG_FILE, ALKIS_EXTRACT_DIR)


def download_general_base_datasets() -> None:
    """Download the common official base datasets."""

    log_dataset("Dataset: landnutzung")
    log_warning(
        "Hinweis: Die amtliche Landnutzung ist ein großer Bayern-Datensatz "
        "von ungefähr 5 bis 6 GB."
    )
    log_warning(
        "Der erste Download kann deshalb deutlich länger dauern als die "
        "anderen allgemeinen Datensätze."
    )
    # Die Landnutzung wird bewusst einmal vollständig lokal vorgehalten.
    # Der eigentliche Gemeinde-Arbeitsdatensatz wird erst später in Script 4
    # per Bounding-Box-Vorfilter und exaktem Gemeindezuschnitt erzeugt.
    download_file(LANDUSE_URL, LANDUSE_FILE)


def download_general_protection_datasets() -> None:
    """Download and extract the official general protection area datasets."""

    log_section("Nature conservation (general datasets)")

    for url, zip_file, dataset_name in SCHUTZGEBIETE_DATASETS:
        log_dataset(f"Dataset: {dataset_name}")
        download_file(url, zip_file)
        unzip_file(zip_file, SCHUTZGEBIETE_RAW_DIR / dataset_name)


def download_general_natura2000_datasets() -> None:
    """Download and extract the official Natura-2000 datasets."""

    log_section("Nature conservation (Natura 2000)")

    for url, zip_file, dataset_name in NATURA2000_DATASETS:
        log_dataset(f"Dataset: natura2000_{dataset_name}")
        download_file(url, zip_file)
        unzip_file(zip_file, NATURA2000_RAW_DIR / dataset_name)


def download_general_datasets() -> None:
    """Download all general raw datasets."""

    download_administrative_boundaries()
    download_general_base_datasets()
    download_general_protection_datasets()
    download_general_natura2000_datasets()


# =============================================================================
# Wind download steps
# =============================================================================

def prepare_wind_raw_datasets() -> None:
    """Download all required official wind datasets for the workflow."""

    WIND_RAW_DIR.mkdir(parents=True, exist_ok=True)

    log_section("Wind datasets")
    download_wfs_layer(
        "wind_vorranggebiete",
        WIND_VORRANG_TYPENAME,
        WIND_VORRANG_FILE,
    )
    download_wfs_layer(
        "wind_vorbehaltsgebiete",
        WIND_VORBEHALT_TYPENAME,
        WIND_VORBEHALT_FILE,
    )

    log_dataset("Dataset: vogelkulissen_2024")
    download_file(VOGELKULISSEN_2024_URL, VOGELKULISSEN_2024_FILE)
    unzip_file(VOGELKULISSEN_2024_FILE, VOGELKULISSEN_2024_EXTRACT_DIR)


# =============================================================================
# Solar download steps
# =============================================================================

def prepare_solar_raw_datasets() -> None:
    """Placeholder for future raw solar downloads."""

    log_section("Solar datasets")
    log_info("No raw solar download configured in script 1 yet.")
    log_info("Solar-specific OSM and WMS inputs are prepared in the solar scripts.")


# =============================================================================
# Wasser download steps
# =============================================================================

def prepare_wasser_raw_datasets() -> None:
    """Placeholder for future raw water downloads."""

    log_section("Wasser datasets")
    log_info("No raw water download configured yet.")


# =============================================================================
# Command line entry point
# =============================================================================

def main() -> None:
    """Download and validate the raw datasets used by the selected workflow."""

    parser = ColoredArgumentParser(
        description="Download and validate raw datasets for the geodata pipeline."
    )
    parser.add_argument(
        "--technology",
        required=True,
        choices=["wind", "solar", "wasser"],
        help="Selected technology for the current workflow run.",
    )
    args = parser.parse_args()

    download_general_datasets()

    match args.technology:
        case "wind":
            prepare_wind_raw_datasets()
        case "solar":
            prepare_solar_raw_datasets()
        case "wasser":
            prepare_wasser_raw_datasets()


if __name__ == "__main__":
    main()
