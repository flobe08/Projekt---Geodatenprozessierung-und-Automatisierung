"""
Script 0: Prepare all raw datasets.

Workflow:
1. Download the common Bavarian administrative boundary dataset.
2. Download the required official wind WFS exports for the workflow.
3. Stop with clear source hints when required inputs are still missing.
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
    log_error,
    log_info,
    log_section,
    log_success,
    log_warning,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# -----------------------------------------------------------------------------
# 0. Common administrative boundary dataset
# -----------------------------------------------------------------------------
ALKIS_VERWALTUNG_URL = "https://geodaten.bayern.de/odd/m/4/verwaltung/alkis-verwaltung.zip"
ALKIS_VERWALTUNG_FILE = BASE_DIR / "data/raw/Verwaltungsgebiet_Bayern/alkis_verwaltungsgebiete.zip"
ALKIS_EXTRACT_DIR = BASE_DIR / "data/raw/Verwaltungsgebiet_Bayern"


# -----------------------------------------------------------------------------
# 1. Wind raw datasets
# -----------------------------------------------------------------------------
WIND_RAW_DIR = BASE_DIR / "data/raw/wind"
WIND_VORRANG_FILE = WIND_RAW_DIR / "wind_vorranggebiete.gpkg"
WIND_VORBEHALT_FILE = WIND_RAW_DIR / "wind_vorbehaltsgebiete.gpkg"
WFS_REGIONALPLANUNG_URL = "https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung"
WFS_REGIONALPLANUNG_CAPABILITIES_URL = (
    "https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung"
    "?service=WFS&request=GetCapabilities"
)
WFS_VERSION = "2.0.0"
WFS_OUTPUT_FORMAT = "Geopackage"
WIND_VORRANG_TYPENAME = "WFS_Regionalplanung:Vorranggebiet_Windenergienutzung"
WIND_VORBEHALT_TYPENAME = "WFS_Regionalplanung:Vorbehaltsgebiet_Windenergienutzung"


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


def download_base_data() -> None:
    """Download and extract the common administrative boundary dataset."""

    log_section("Base datasets")
    log_dataset("Dataset: alkis_verwaltungsgebiet")
    download_file(ALKIS_VERWALTUNG_URL, ALKIS_VERWALTUNG_FILE)
    unzip_file(ALKIS_VERWALTUNG_FILE, ALKIS_EXTRACT_DIR)


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

    download_base_data()

    match args.technology:
        case "wind":
            prepare_wind_raw_datasets()
            # Future optional step:
            # OSM context data can be added here later if the workflow needs
            # extra road context for map orientation.
        case "solar" | "wasser":
            log_info(f"No technology-specific raw download configured yet for: {args.technology}")


if __name__ == "__main__":
    main()
