"""
Script 0: Prepare all raw datasets.

Workflow:
1. Download the common Bavarian administrative boundary dataset.
2. Download the required official wind WFS exports for the workflow.
3. Optionally download municipality-based OSM context roads.
4. Stop with clear source hints when required inputs are still missing.
"""

from pathlib import Path
import argparse
import json
import os
import re
import requests
import sys
import zipfile

import geopandas as gpd
from shapely.geometry import LineString

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


# -----------------------------------------------------------------------------
# 2. Optional OSM context data
# -----------------------------------------------------------------------------
BOUNDARY_DIR = BASE_DIR / "data/processed/boundaries"
OSM_CONTEXT_DIR = BASE_DIR / "data/processed/osm_context"

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

ROAD_HIGHWAY_VALUES = {
    "motorway",
    "motorway_link",
    "trunk",
    "trunk_link",
    "primary",
    "primary_link",
    "secondary",
    "secondary_link",
    "tertiary",
    "tertiary_link",
    "unclassified",
    "residential",
    "living_street",
    "service",
    "track",
    "road",
}


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


def safe_filename(name: str) -> str:
    """Create the same filename format as the municipality scripts."""

    return name.lower().replace(" ", "_")


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


def boundary_to_overpass_bbox(boundary: gpd.GeoDataFrame) -> str:
    """Convert the municipality boundary to an Overpass bounding box."""

    min_lon, min_lat, max_lon, max_lat = boundary.to_crs(epsg=4326).total_bounds
    return f"{min_lat},{min_lon},{max_lat},{max_lon}"


def build_roads_query(overpass_bbox: str) -> str:
    """Build a focused Overpass query for road context data."""

    return f"""
[out:json][timeout:120];
(
  way["highway"]({overpass_bbox});
);
out tags geom;
"""


def clean_column_name(column: str, used_names: set[str]) -> str:
    """Create a GeoPackage-safe column name."""

    if column == "geometry":
        return column

    clean_name = re.sub(r"[^0-9a-zA-Z_]+", "_", column.lower()).strip("_")

    if not clean_name:
        clean_name = "field"

    if clean_name[0].isdigit():
        clean_name = f"field_{clean_name}"

    if clean_name in {"fid", "geom", "geometry"}:
        clean_name = f"attr_{clean_name}"

    clean_name = clean_name[:58]
    unique_name = clean_name
    counter = 1

    while unique_name in used_names:
        suffix = f"_{counter}"
        unique_name = f"{clean_name[:58 - len(suffix)]}{suffix}"
        counter += 1

    used_names.add(unique_name)
    return unique_name


def clean_for_geopackage(data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Clean column names before writing data to GeoPackage."""

    used_names = set()
    rename_map = {
        column: clean_column_name(str(column), used_names)
        for column in data.columns
    }

    return data.rename(columns=rename_map)


def remove_existing_output(output_file: Path, script_label: str) -> None:
    """Remove an old output file before writing a fresh result."""

    if not output_file.exists():
        return

    try:
        output_file.unlink()
    except PermissionError as error:
        log_error("Output file is locked and cannot be overwritten.")
        log_error(f"Locked file: {display_path(output_file)}")
        log_info("Close the file in QGIS or remove the layer from the QGIS project.")
        log_info("Then run the workflow again.")
        raise SystemExit(
            f"{script_label} stopped because an output file is still open."
        ) from error


def request_overpass(query: str) -> dict:
    """Request raw Overpass JSON data, trying a fallback endpoint if needed."""

    headers = {
        "Accept": "application/json",
        "User-Agent": "geodata-pipeline-student-project/1.0",
    }

    last_error = None

    for url in OVERPASS_URLS:
        log_info(f"Requesting OSM context roads from: {url}")

        try:
            response = requests.post(
                url,
                data={"data": query},
                headers=headers,
                timeout=180,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            last_error = error
            log_warning(f"Overpass endpoint failed: {url}")

            if getattr(error, "response", None) is not None:
                log_warning(error.response.text[:500])

    log_error(f"All Overpass endpoints failed: {last_error}")
    raise RuntimeError("Could not download OSM context roads from Overpass.") from last_error


def roads_to_geodataframe(overpass_data: dict) -> gpd.GeoDataFrame:
    """Convert Overpass highway ways to a road line layer."""

    features = []

    for element in overpass_data.get("elements", []):
        if element.get("type") != "way":
            continue

        highway_value = element.get("tags", {}).get("highway")

        if highway_value not in ROAD_HIGHWAY_VALUES:
            continue

        coordinates = [
            (node["lon"], node["lat"])
            for node in element.get("geometry", [])
            if "lon" in node and "lat" in node
        ]

        if len(coordinates) < 2:
            continue

        properties = {
            "osm_id": str(element["id"]),
            "osm_type": element["type"],
            "geometry": LineString(coordinates),
        }

        for key, value in element.get("tags", {}).items():
            properties[key] = str(value)

        features.append(properties)

    if not features:
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:4326")

    return gpd.GeoDataFrame(features, geometry="geometry", crs="EPSG:4326")


def write_layer(output_file: Path, layer_name: str, data: gpd.GeoDataFrame) -> None:
    """Write one non-empty GeoPackage layer."""

    if data.empty:
        log_warning(f"No features for layer: {layer_name}")
        return

    data = clean_for_geopackage(data)

    try:
        data.to_file(output_file, layer=layer_name, driver="GPKG")
    except Exception as error:
        log_error(f"Could not write layer: {layer_name}")
        log_error(f"Output file: {display_path(output_file)}")
        log_info("Close the file in QGIS or remove the layer from the QGIS project.")
        log_info("Then run the workflow again.")
        raise SystemExit(
            "Script 0 stopped because the OSM context GeoPackage could not be written."
        ) from error

    log_success(f"Written {layer_name}: {len(data)} features")


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


def download_optional_osm_context(municipality_name: str) -> None:
    """Download and clip optional OSM context roads for one municipality."""

    safe_name = safe_filename(municipality_name)
    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    output_file = OSM_CONTEXT_DIR / f"{safe_name}_osm_context.gpkg"
    raw_roads_file = OSM_CONTEXT_DIR / f"{safe_name}_osm_context_raw.json"

    if not boundary_file.exists():
        raise FileNotFoundError(
            f"Boundary file not found: {boundary_file}. Run script 1 first."
        )

    OSM_CONTEXT_DIR.mkdir(parents=True, exist_ok=True)

    boundary = gpd.read_file(boundary_file).to_crs(epsg=25832)
    boundary_for_clip = boundary[["geometry"]].dissolve()

    remove_existing_output(output_file, "Script 0")

    log_section("Optional OSM context")
    log_dataset("Dataset: osm_context_roads")
    log_info(f"Downloading optional OSM context for: {municipality_name}")
    log_info(f"Boundary: {display_path(boundary_file)}")
    log_info(f"Output: {display_path(output_file)}")

    overpass_bbox = boundary_to_overpass_bbox(boundary)
    roads_query = build_roads_query(overpass_bbox)
    overpass_data = request_overpass(roads_query)

    with open(raw_roads_file, "w", encoding="utf-8") as file:
        json.dump(overpass_data, file, ensure_ascii=False)

    roads = roads_to_geodataframe(overpass_data)

    if not roads.empty:
        roads = gpd.clip(roads.to_crs(epsg=25832), boundary_for_clip)

    write_layer(output_file, "osm_context_roads", roads)
    log_success("Optional OSM context download finished.")


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
    parser.add_argument(
        "--municipality",
        help="Municipality name for optional municipality-based downloads.",
    )
    parser.add_argument(
        "--with-osm-context",
        action="store_true",
        help="Also download municipality-based OSM context roads.",
    )
    args = parser.parse_args()

    download_base_data()

    match args.technology:
        case "wind":
            prepare_wind_raw_datasets()
            if args.with_osm_context:
                if not args.municipality:
                    raise SystemExit(
                        "Script 0 needs --municipality when --with-osm-context is used."
                    )
                download_optional_osm_context(args.municipality)
            else:
                log_section("Optional OSM context")
                log_info("OSM context download skipped.")
        case "solar" | "wasser":
            log_info(f"No technology-specific raw download configured yet for: {args.technology}")


if __name__ == "__main__":
    main()
