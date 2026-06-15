"""
Script 5: Download OSM network data with one shared workflow.

Workflow:
1. Read the municipality boundary from script 2.
2. Build one buffered analysis context around the municipality.
3. Request technology-specific OSM road and optional railway data from Overpass.
4. Clip the OSM lines to the analysis context, not directly to the municipality.
5. Write the clipped network layers to a GeoPackage for later processing.

Hinweis:
Dieses Skript ist bewusst allgemein gehalten. Es lädt je nach Technologie
unterschiedliche OSM-Netzklassen, damit dieselbe technische Basis für Wind,
Solar und später auch Wasser genutzt werden kann. Aus dem breiten Rohdownload
wird zusätzlich ein kleiner technologiespezifischer Ausschlusslayer abgeleitet.
"""

from pathlib import Path
import json
import re
import sys

import geopandas as gpd
import requests
from shapely.geometry import LineString

sys.path.append(str(Path(__file__).resolve().parent.parent / "utils"))
from spatial_context import area_to_overpass_bbox, build_analysis_context
from utils import ColoredArgumentParser, log_error, log_info, log_success, log_warning


BASE_DIR = Path(__file__).resolve().parent.parent.parent


# =============================================================================
# 0. Input and output paths
# =============================================================================
BOUNDARY_DIR = BASE_DIR / "data/processed/boundaries"
OSM_HIGHWAY_DIR = BASE_DIR / "data/processed/osm_highways"
OSM_TRANSPORT_DIR = BASE_DIR / "data/processed/osm_transport"

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

# Allgemeiner Analysekontext für OSM-Daten:
# Wenn später Buffer oder Distanzanalysen berechnet werden, darf das OSM-Netz
# nicht schon an der Gemeindegrenze enden.
ANALYSIS_CONTEXT_BUFFER_METERS = 1000

GENERAL_HIGHWAY_VALUES = [
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
]

# Diese Listen definieren je Technologie, welche Straßenklassen später als
# Ausschluss- oder Konfliktlayer nach außen ausgegeben werden sollen.
# Kleinere Wege wie service, track und road bleiben im Rohdownload erhalten,
# werden aber zunächst nicht automatisch als Ausschluss behandelt.
TECH_HIGHWAY_EXCLUSION_VALUES = {
    "wind": {
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
    },
    "solar": {
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
    },
    "wasser": {
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
    },
}

MOTORWAY_VALUES = {"motorway", "motorway_link"}
RAILWAY_VALUES = {"rail"}


# =============================================================================
# 1. Technology configuration
# =============================================================================
TECH_CONFIG = {
    "wind": {
        "output_dir": OSM_HIGHWAY_DIR,
        "file_suffix": "osm_highways",
        "download_highways": True,
        "download_railways": False,
        "description": "OSM highway data",
    },
    "solar": {
        "output_dir": OSM_TRANSPORT_DIR,
        "file_suffix": "osm_transport",
        "download_highways": True,
        "download_railways": True,
        "description": "OSM transport data",
    },
    "wasser": {
        "output_dir": OSM_HIGHWAY_DIR,
        "file_suffix": "osm_highways",
        "download_highways": True,
        "download_railways": False,
        "description": "OSM highway data",
    },
}


# =============================================================================
# 2. Helper functions
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
            "Script 5 stopped because the OSM GeoPackage is still open."
        ) from error


def build_overpass_query(
    highway_values: list[str],
    include_railways: bool,
    overpass_bbox: str,
) -> str:
    """Build one Overpass query for the configured technology."""

    highway_regex = "|".join(highway_values)
    highway_block = f'  way["highway"~"^({highway_regex})$"]({overpass_bbox});'
    railway_block = '  way["railway"="rail"]({});'.format(overpass_bbox)

    query_parts = [highway_block]
    if include_railways:
        query_parts.append(railway_block)

    query_body = "\n".join(query_parts)
    return f"""
[out:json][timeout:180];
(
{query_body}
);
out tags geom;
"""


def request_overpass(query: str, description: str) -> dict:
    """Request raw Overpass JSON data, trying a fallback endpoint if needed."""

    headers = {
        "Accept": "application/json",
        "User-Agent": "geodata-pipeline-student-project/1.0",
    }

    last_error = None

    for url in OVERPASS_URLS:
        log_info(f"Requesting {description} from: {url}")

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
    raise RuntimeError("Could not download OSM network data.") from last_error


def overpass_to_geodataframes(
    overpass_data: dict,
    include_railways: bool,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Convert Overpass JSON to highway and optional railway GeoDataFrames."""

    roads = []
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

        if highway_value in GENERAL_HIGHWAY_VALUES:
            road_properties = properties.copy()
            road_properties["source_type"] = "road"
            roads.append(road_properties)

        if include_railways and railway_value in RAILWAY_VALUES:
            railway_properties = properties.copy()
            railway_properties["source_type"] = "railway"
            railways.append(railway_properties)

    if roads:
        road_gdf = gpd.GeoDataFrame(roads, geometry="geometry", crs="EPSG:4326")
    else:
        road_gdf = empty_lines_gdf()

    if railways:
        railway_gdf = gpd.GeoDataFrame(railways, geometry="geometry", crs="EPSG:4326")
    else:
        railway_gdf = empty_lines_gdf()

    return road_gdf, railway_gdf


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
            "Script 5 stopped because the OSM GeoPackage could not be written."
        ) from error

    if data.empty:
        log_warning(f"Written empty layer: {layer_name} (0 features)")
    else:
        log_success(f"Written {layer_name}: {len(data)} features")


def raw_road_layer_name() -> str:
    """Return the standard raw road layer name."""

    return "osm_roads_raw"


def exclusion_road_layer_name(technology: str) -> str:
    """Return the technology-specific exclusion road layer name."""

    return f"osm_roads_{technology}_ausschluss"


def solar_road_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for the broader solar road context."""

    return f"osm_strassen_{safe_filename(municipality_name)}"


def motorway_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for motorways."""

    return f"osm_autobahnen_{safe_filename(municipality_name)}"


def railway_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for railways."""

    return f"osm_schienenwege_{safe_filename(municipality_name)}"


def analysis_context_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for the analysis context area."""

    return f"analysekontext_{safe_filename(municipality_name)}"


def split_motorways(roads: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Keep only motorway and motorway_link from the broader road dataset."""

    if roads.empty or "highway" not in roads.columns:
        return empty_lines_gdf(crs=roads.crs if not roads.empty else "EPSG:25832")

    motorway_mask = roads["highway"].isin(MOTORWAY_VALUES)
    return roads[motorway_mask].copy()


def build_exclusion_roads(
    roads: gpd.GeoDataFrame,
    technology: str,
) -> gpd.GeoDataFrame:
    """Filter one broader road dataset down to the technology exclusion classes."""

    if roads.empty or "highway" not in roads.columns:
        return empty_lines_gdf(crs=roads.crs if not roads.empty else "EPSG:25832")

    exclusion_values = TECH_HIGHWAY_EXCLUSION_VALUES[technology]
    mask = roads["highway"].isin(exclusion_values)
    return roads[mask].copy()


# =============================================================================
# 3. Download OSM network data for one municipality
# =============================================================================
def download_osm_network_data(municipality_name: str, technology: str) -> None:
    """Download technology-specific OSM network data with a buffered context."""

    if technology not in TECH_CONFIG:
        raise ValueError(f"Unknown technology: {technology}")

    safe_name = safe_filename(municipality_name)
    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"

    if not boundary_file.exists():
        raise FileNotFoundError(
            f"Boundary file not found: {boundary_file}. Run script 2 first."
        )

    config = TECH_CONFIG[technology]
    output_dir = config["output_dir"]
    output_file = output_dir / f"{safe_name}_{config['file_suffix']}.gpkg"
    raw_file = output_dir / f"{safe_name}_{config['file_suffix']}_raw.json"

    output_dir.mkdir(parents=True, exist_ok=True)
    remove_existing_output(output_file)

    boundary = gpd.read_file(boundary_file).to_crs(epsg=25832)
    analysis_context_area = build_analysis_context(
        boundary,
        ANALYSIS_CONTEXT_BUFFER_METERS,
    )

    log_info(f"Downloading {config['description']} for: {municipality_name}")
    log_info(f"Boundary: {display_path(boundary_file)}")
    log_info(f"Output: {display_path(output_file)}")
    log_info(f"Analysekontext-Buffer: {ANALYSIS_CONTEXT_BUFFER_METERS} m")

    overpass_bbox = area_to_overpass_bbox(analysis_context_area)
    query = build_overpass_query(
        GENERAL_HIGHWAY_VALUES,
        config["download_railways"],
        overpass_bbox,
    )
    overpass_data = request_overpass(query, config["description"])

    with open(raw_file, "w", encoding="utf-8") as file:
        json.dump(overpass_data, file, ensure_ascii=False)

    roads, railways = overpass_to_geodataframes(
        overpass_data,
        include_railways=config["download_railways"],
    )

    if not roads.empty:
        roads = gpd.clip(roads.to_crs(epsg=25832), analysis_context_area)

    if not railways.empty:
        railways = gpd.clip(railways.to_crs(epsg=25832), analysis_context_area)

    exclusion_roads = build_exclusion_roads(roads, technology)

    write_layer(
        output_file,
        analysis_context_layer_name(municipality_name),
        analysis_context_area,
    )

    if technology == "solar":
        motorways = split_motorways(roads)
        write_layer(output_file, raw_road_layer_name(), roads)
        write_layer(
            output_file,
            exclusion_road_layer_name(technology),
            exclusion_roads,
        )
        write_layer(output_file, solar_road_layer_name(municipality_name), roads)
        write_layer(output_file, motorway_layer_name(municipality_name), motorways)
        write_layer(output_file, railway_layer_name(municipality_name), railways)
    else:
        write_layer(output_file, raw_road_layer_name(), roads)
        write_layer(
            output_file,
            exclusion_road_layer_name(technology),
            exclusion_roads,
        )

    log_success("OSM network download finished.")


def main() -> None:
    """Run the OSM network download for one municipality and technology."""

    parser = ColoredArgumentParser(
        description="Download technology-specific OSM road and railway data."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )
    parser.add_argument(
        "--technology",
        required=True,
        choices=["wind", "solar", "wasser"],
        help="Technology that defines the OSM filter.",
    )

    args = parser.parse_args()
    download_osm_network_data(args.municipality, args.technology)


if __name__ == "__main__":
    main()
