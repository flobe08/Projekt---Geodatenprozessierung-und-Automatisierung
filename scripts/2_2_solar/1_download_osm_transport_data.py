"""
Script 1: Download OSM transport data with an expanded analysis context.

Workflow:
1. Read the municipality boundary from script 2.
2. Build one buffered analysis context around the municipality.
3. Request motorway and railway data from Overpass for that context area.
4. Clip the OSM lines to the analysis context, not directly to the municipality.
5. Write the clipped transport layers to a GeoPackage.

Hinweis:
Dieser ältere Solar-Einstieg bleibt vorerst im Repository erhalten.
Im aktuellen Hauptworkflow wird stattdessen das gemeinsame Skript
`scripts/1_prepare_data/5_download_osm_network_data.py --technology solar`
verwendet.
"""

from pathlib import Path
import json
import re
import sys

import geopandas as gpd
import requests
from shapely.geometry import LineString

sys.path.append(str(Path(__file__).resolve().parent.parent / "utils"))
from utils import ColoredArgumentParser, log_error, log_info, log_success, log_warning
from spatial_context import area_to_overpass_bbox, build_analysis_context


BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =============================================================================
# 0. Input and output paths
# =============================================================================
BOUNDARY_DIR = BASE_DIR / "data/processed/boundaries"
OUTPUT_DIR = BASE_DIR / "data/processed/osm_transport"

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

# Allgemeiner Analysekontext für OSM-Daten:
# Wenn später Buffer oder Distanzanalysen berechnet werden, darf das OSM-Netz
# nicht schon an der Gemeindegrenze enden.
ANALYSIS_CONTEXT_BUFFER_METERS = 1000

MOTORWAY_VALUES = {"motorway", "motorway_link"}
RAILWAY_VALUES = {"rail"}


# =============================================================================
# Helper functions
# =============================================================================
def safe_filename(name: str) -> str:
    """Create the same filename format as the other scripts."""

    return name.lower().replace(" ", "_")


def display_path(path: Path) -> str:
    """Return a compact path for log messages."""

    try:
        return str(path.resolve().relative_to(BASE_DIR))
    except ValueError:
        return str(path)


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


def empty_lines_gdf(crs: str = "EPSG:4326") -> gpd.GeoDataFrame:
    """Create an empty line GeoDataFrame with a valid geometry column."""

    return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs=crs)


def remove_existing_output(output_file: Path) -> None:
    """Remove an old output file before writing a fresh GeoPackage."""

    if not output_file.exists():
        return

    try:
        output_file.unlink()
    except PermissionError as error:
        log_error("Output GeoPackage is locked and cannot be overwritten.")
        log_error(f"Locked file: {display_path(output_file)}")
        log_info("Close the file in QGIS or remove the layer from the QGIS project.")
        log_info("Then run the script again.")
        raise SystemExit(
            "Solar script 1 stopped because the OSM transport GeoPackage is still open."
        ) from error


def build_transport_query(overpass_bbox: str) -> str:
    """Build a focused Overpass query for motorway and railway data."""

    return f"""
[out:json][timeout:180];
(
  way["highway"~"^(motorway|motorway_link)$"]({overpass_bbox});
  way["railway"="rail"]({overpass_bbox});
);
out tags geom;
"""


def request_overpass(query: str) -> dict:
    """Request raw Overpass JSON data, trying a fallback endpoint if needed."""

    headers = {
        "Accept": "application/json",
        "User-Agent": "geodata-pipeline-student-project/1.0",
    }

    last_error = None

    for url in OVERPASS_URLS:
        log_info(f"Requesting solar OSM transport data from: {url}")

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
    raise RuntimeError("Could not download OSM transport data.") from last_error


def overpass_to_geodataframes(
    overpass_data: dict,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Convert Overpass JSON to motorway and railway GeoDataFrames."""

    motorways = []
    railways = []

    for element in overpass_data.get("elements", []):
        if element.get("type") != "way":
            continue

        coordinates = [
            (node["lon"], node["lat"])
            for node in element.get("geometry", [])
            if "lon" in node and "lat" in node
        ]

        if len(coordinates) < 2:
            continue

        highway_value = element.get("tags", {}).get("highway")
        railway_value = element.get("tags", {}).get("railway")

        properties = {
            "osm_id": str(element["id"]),
            "osm_type": element["type"],
            "geometry": LineString(coordinates),
        }

        for key, value in element.get("tags", {}).items():
            properties[key] = str(value)

        if highway_value in MOTORWAY_VALUES:
            properties["source_type"] = "motorway"
            motorways.append(properties.copy())

        if railway_value in RAILWAY_VALUES:
            properties["source_type"] = "railway"
            railways.append(properties.copy())

    if motorways:
        motorway_gdf = gpd.GeoDataFrame(motorways, geometry="geometry", crs="EPSG:4326")
    else:
        motorway_gdf = empty_lines_gdf()

    if railways:
        railway_gdf = gpd.GeoDataFrame(railways, geometry="geometry", crs="EPSG:4326")
    else:
        railway_gdf = empty_lines_gdf()

    return motorway_gdf, railway_gdf


def write_layer(output_file: Path, layer_name: str, data: gpd.GeoDataFrame) -> None:
    """Write one GeoPackage layer, even when it contains no features."""

    data = clean_for_geopackage(data)

    try:
        data.to_file(output_file, layer=layer_name, driver="GPKG")
    except Exception as error:
        log_error(f"Could not write layer: {layer_name}")
        log_error(f"Output file: {display_path(output_file)}")
        log_info("Close the file in QGIS or remove the layer from the QGIS project.")
        log_info("Then run the script again.")
        raise SystemExit(
            "Solar script 1 stopped because the OSM transport GeoPackage could not be written."
        ) from error

    if data.empty:
        log_warning(f"Written empty layer: {layer_name} (0 features)")
    else:
        log_success(f"Written {layer_name}: {len(data)} features")


def motorway_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for motorways."""

    return f"osm_autobahnen_{safe_filename(municipality_name)}"


def railway_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for railways."""

    return f"osm_schienenwege_{safe_filename(municipality_name)}"


def analysis_context_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for the analysis context area."""

    return f"analysekontext_{safe_filename(municipality_name)}"


# =============================================================================
# 1. Download OSM motorway and railway data for one municipality
# =============================================================================
def download_solar_transport_data(municipality_name: str) -> None:
    """Download motorway and railway data with a buffered analysis context."""

    safe_name = safe_filename(municipality_name)
    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    output_file = OUTPUT_DIR / f"{safe_name}_osm_transport.gpkg"
    raw_file = OUTPUT_DIR / f"{safe_name}_osm_transport_raw.json"

    if not boundary_file.exists():
        raise FileNotFoundError(
            f"Boundary file not found: {boundary_file}. Run script 2 first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(output_file)

    boundary = gpd.read_file(boundary_file).to_crs(epsg=25832)
    analysis_context_area = build_analysis_context(
        boundary,
        ANALYSIS_CONTEXT_BUFFER_METERS,
    )

    log_info(f"Downloading OSM transport data for: {municipality_name}")
    log_info(f"Boundary: {display_path(boundary_file)}")
    log_info(f"Output: {display_path(output_file)}")
    log_info(f"Analysekontext-Buffer: {ANALYSIS_CONTEXT_BUFFER_METERS} m")

    overpass_bbox = area_to_overpass_bbox(analysis_context_area)
    query = build_transport_query(overpass_bbox)
    overpass_data = request_overpass(query)

    with open(raw_file, "w", encoding="utf-8") as file:
        json.dump(overpass_data, file, ensure_ascii=False)

    motorways, railways = overpass_to_geodataframes(overpass_data)

    if not motorways.empty:
        motorways = gpd.clip(motorways.to_crs(epsg=25832), analysis_context_area)

    if not railways.empty:
        railways = gpd.clip(railways.to_crs(epsg=25832), analysis_context_area)

    write_layer(
        output_file,
        analysis_context_layer_name(municipality_name),
        analysis_context_area,
    )
    write_layer(output_file, motorway_layer_name(municipality_name), motorways)
    write_layer(output_file, railway_layer_name(municipality_name), railways)

    log_success("OSM transport download finished.")


def main() -> None:
    """Run the OSM transport download for one municipality."""

    parser = ColoredArgumentParser(
        description="Download OSM motorway and railway data for the solar workflow."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()
    download_solar_transport_data(args.municipality)


if __name__ == "__main__":
    main()
