"""
Script 2: Download OSM road data from Overpass.

This script uses the municipality boundary from script 1, requests roads from
OpenStreetMap via Overpass, clips the roads to the official municipality
boundary, and writes the result to a GeoPackage layer named `osm_roads`.
The raw Overpass response is also saved as JSON for transparency and debugging.
"""

from pathlib import Path
import argparse
import json
import re
import sys

import geopandas as gpd
import requests
from shapely.geometry import LineString

sys.path.append(str(Path(__file__).resolve().parent.parent / "utils"))
from utils import ColoredArgumentParser, log_error, log_info, log_success, log_warning


BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Input and output paths.
BOUNDARY_DIR = BASE_DIR / "data/processed/boundaries"
OUTPUT_DIR = BASE_DIR / "data/processed/osm_highways"


# Overpass configuration.
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]



# Road types used for first distance buffers and access checks.
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


# -----------------------------------------------------------------------------
# Helper functions.
# -----------------------------------------------------------------------------
def safe_filename(name: str) -> str:
    """Create the same filename format as script 1."""

    return name.lower().replace(" ", "_")


def display_path(path: Path) -> str:
    """Return a compact path for log messages."""

    try:
        return str(path.resolve().relative_to(BASE_DIR))
    except ValueError:
        return str(path)


def boundary_to_overpass_bbox(boundary: gpd.GeoDataFrame) -> str:
    """Convert the municipality boundary to an Overpass bounding box."""

    min_lon, min_lat, max_lon, max_lat = boundary.to_crs(epsg=4326).total_bounds
    return f"{min_lat},{min_lon},{max_lat},{max_lon}"


def build_roads_query(overpass_bbox: str) -> str:
    """Build a small Overpass query for OSM roads only."""

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


def remove_existing_output(output_file: Path) -> None:
    """Remove an old output file before writing a fresh GeoPackage."""

    if not output_file.exists():
        return

    try:
        output_file.unlink()
    except PermissionError as error:
        # Stop with a clear message if the GeoPackage is still open (in QGIS).
        log_error("Output GeoPackage is locked and cannot be overwritten.")
        log_error(f"Locked file: {display_path(output_file)}")
        log_info("Close the file in QGIS or remove the layer from the QGIS project.")
        log_info("Then run the pipeline again.")
        raise SystemExit(
            "Script 2 stopped because the output GeoPackage is still open."
        ) from error


# -----------------------------------------------------------------------------
# 1. Request OSM roads from Overpass.
# -----------------------------------------------------------------------------
def request_overpass(query: str) -> dict:
    """Request raw Overpass JSON data, trying a fallback endpoint if needed."""

    headers = {
        "Accept": "application/json",
        "User-Agent": "geodata-pipeline-student-project/1.0",
    }

    last_error = None

    for url in OVERPASS_URLS:
        log_info(f"Requesting OSM roads from: {url}")

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
    raise RuntimeError("Could not download OSM roads from Overpass.") from last_error


# -----------------------------------------------------------------------------
# 2. Convert Overpass response to road geometries.
# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
# 3. Write processed output layers.
# -----------------------------------------------------------------------------
def write_layer(output_file: Path, layer_name: str, data: gpd.GeoDataFrame) -> None:
    """Write one non-empty GeoPackage layer."""

    if data.empty:
        log_warning(f"No features for layer: {layer_name}")
        return

    data = clean_for_geopackage(data)
    try:
        data.to_file(output_file, layer=layer_name, driver="GPKG")
    except Exception as error:
        # Writing can fail when QGIS or another program keeps the GeoPackage open.
        log_error(f"Could not write layer: {layer_name}")
        log_error(f"Output file: {display_path(output_file)}")
        log_info("Close the file in QGIS or remove the layer from the QGIS project.")
        log_info("Then run the pipeline again.")
        raise SystemExit(
            "Script 2 stopped because the GeoPackage could not be written."
        ) from error

    log_success(f"Written {layer_name}: {len(data)} features")


# -----------------------------------------------------------------------------
# 4. Run OSM road preparation for one municipality.
# -----------------------------------------------------------------------------
def download_overpass_roads(municipality_name: str) -> None:
    """Download and clip OSM road data for one municipality."""

    safe_name = safe_filename(municipality_name)

    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    output_file = OUTPUT_DIR / f"{safe_name}_osm_highways.gpkg"
    raw_roads_file = OUTPUT_DIR / f"{safe_name}_roads_overpass_raw.json"

    if not boundary_file.exists():
        raise FileNotFoundError(
            f"Boundary file not found: {boundary_file}. Run script 1 first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    boundary = gpd.read_file(boundary_file).to_crs(epsg=25832)
    boundary_for_clip = boundary[["geometry"]].dissolve()

    remove_existing_output(output_file)

    log_info(f"Downloading OSM roads for: {municipality_name}")
    log_info(f"Boundary: {display_path(boundary_file)}")
    log_info(f"Output: {display_path(output_file)}")

    overpass_bbox = boundary_to_overpass_bbox(boundary)
    roads_query = build_roads_query(overpass_bbox)
    overpass_data = request_overpass(roads_query)

    # Save the raw Overpass JSON response as reproducible download evidence.
    with open(raw_roads_file, "w", encoding="utf-8") as file:
        json.dump(overpass_data, file, ensure_ascii=False)

    roads = roads_to_geodataframe(overpass_data)

    if not roads.empty:
        roads = gpd.clip(roads.to_crs(epsg=25832), boundary_for_clip)

    write_layer(output_file, "osm_roads", roads)
    log_success("OSM road download finished.")


def main() -> None:
    parser = ColoredArgumentParser(
        description="Download and clip OSM road data from Overpass."
    )

    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()
    download_overpass_roads(args.municipality)


if __name__ == "__main__":
    main()
