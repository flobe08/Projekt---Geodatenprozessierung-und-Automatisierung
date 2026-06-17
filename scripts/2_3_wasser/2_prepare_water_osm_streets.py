"""
Script 2: Prepare water-specific OSM street layers.

Workflow:
1. Read the broad OSM street basis from prepare-data script 5.
2. Filter street classes that may be relevant as access or conflict context.
3. Keep small or unclear paths only in the raw OSM street basis.
4. Buffer the filtered street classes with first working distances.
5. Write water-specific line and buffer GeoPackages for later mapping.
"""

from pathlib import Path
import re
import sys

import geopandas as gpd

sys.path.append(str(Path(__file__).resolve().parent.parent / "utils"))
from utils import ColoredArgumentParser, log_error, log_info, log_success, log_warning


BASE_DIR = Path(__file__).resolve().parent.parent.parent


# =============================================================================
# 0. Input and output paths
# =============================================================================
# input
OSM_STREETS_DIR = BASE_DIR / "data/processed/osm_streets"

# output
OUTPUT_DIR = BASE_DIR / "data/processed/wasser"


WATER_STREET_AUSSCHLUSS = {
    "living_street",
    "motorway",
    "motorway_link",
    "primary",
    "primary_link",
    "residential",
    "secondary",
    "secondary_link",
    "tertiary",
    "tertiary_link",
    "trunk",
    "trunk_link",
    "unclassified",
}

# service, track and road stay in osm_streets_raw. They are too broad or too
# unclear for a first automatic water-related street context.
WATER_OSM_STREET_BUFFER_RULES_METERS = {
    "living_street": 20,
    "motorway": 100,
    "motorway_link": 100,
    "primary": 75,
    "primary_link": 75,
    "residential": 20,
    "secondary": 50,
    "secondary_link": 50,
    "tertiary": 30,
    "tertiary_link": 30,
    "trunk": 100,
    "trunk_link": 100,
    "unclassified": 20,
}


# =============================================================================
# 1. Helper functions
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


def empty_lines_gdf(crs: str = "EPSG:25832") -> gpd.GeoDataFrame:
    """Create an empty line GeoDataFrame with a valid geometry column."""

    return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs=crs)


def empty_polygons_gdf(crs: str = "EPSG:25832") -> gpd.GeoDataFrame:
    """Create an empty polygon GeoDataFrame with a valid geometry column."""

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
            "Water OSM street script stopped because the output file is still open."
        ) from error


def write_layer(output_file: Path, layer_name: str, data: gpd.GeoDataFrame) -> None:
    """Write one GeoPackage layer, even when it contains no features."""

    data = clean_for_geopackage(data)
    data.to_file(output_file, layer=layer_name, driver="GPKG")

    if data.empty:
        log_warning(f"Written empty layer: {layer_name} (0 features)")
    else:
        log_success(f"Written {layer_name}: {len(data)} features")


def build_street_buffer_layer(
    streets: gpd.GeoDataFrame,
    buffer_rules: dict[str, int],
) -> gpd.GeoDataFrame:
    """Create dissolved street buffers grouped by OSM highway class."""

    if streets.empty or "highway" not in streets.columns:
        return empty_polygons_gdf()

    buffer_parts = []

    for highway_value, buffer_distance in sorted(buffer_rules.items()):
        street_subset = streets[streets["highway"] == highway_value].copy()

        if street_subset.empty or buffer_distance <= 0:
            continue

        # Each highway class is buffered separately so the source class and
        # applied distance remain visible in the attribute table.
        buffered_geometry = street_subset.geometry.buffer(buffer_distance).unary_union
        buffer_parts.append(
            {
                "highway": highway_value,
                "buffer_m": buffer_distance,
                "geometry": buffered_geometry,
            }
        )

    if not buffer_parts:
        return empty_polygons_gdf(streets.crs)

    return gpd.GeoDataFrame(buffer_parts, geometry="geometry", crs=streets.crs)


def raw_street_layer_name() -> str:
    """Return the standard raw street layer name."""

    return "osm_streets_raw"


def water_street_layer_name() -> str:
    """Return the water-specific OSM street exclusion layer name."""

    return "osm_streets_wasser_ausschluss"


def water_street_buffer_layer_name() -> str:
    """Return the water-specific OSM street buffer layer name."""

    return "osm_streets_wasser_ausschluss_puffer"


# =============================================================================
# 2. Prepare water OSM street layer
# =============================================================================
def prepare_water_osm_streets(municipality_name: str) -> None:
    """Prepare water-specific OSM street exclusion data."""

    safe_name = safe_filename(municipality_name)
    input_file = OSM_STREETS_DIR / f"{safe_name}_osm_streets.gpkg"
    output_file = OUTPUT_DIR / f"{safe_name}_osm_wasser_streets.gpkg"
    buffer_output_file = OUTPUT_DIR / f"{safe_name}_osm_wasser_streets_puffer.gpkg"

    if not input_file.exists():
        raise FileNotFoundError(
            f"OSM street file not found: {input_file}. Run prepare-data script 5 first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(output_file)
    remove_existing_output(buffer_output_file)

    log_info(f"Preparing water OSM street layer for: {municipality_name}")
    log_info(f"Input: {display_path(input_file)}")
    log_info(f"Output 1: {display_path(output_file)}")
    log_info(f"Output 2: {display_path(buffer_output_file)}")
    log_info(f"Water street exclusion classes: {', '.join(sorted(WATER_STREET_AUSSCHLUSS))}")
    log_info(
        "Water street buffer rules: "
        + ", ".join(
            f"{key}={value}m"
            for key, value in sorted(WATER_OSM_STREET_BUFFER_RULES_METERS.items())
        )
    )

    streets = gpd.read_file(input_file, layer=raw_street_layer_name()).to_crs(epsg=25832)

    if streets.empty or "highway" not in streets.columns:
        water_streets = empty_lines_gdf()
    else:
        water_streets = streets[streets["highway"].isin(WATER_STREET_AUSSCHLUSS)].copy()

    write_layer(output_file, water_street_layer_name(), water_streets)
    water_street_buffers = build_street_buffer_layer(
        water_streets,
        WATER_OSM_STREET_BUFFER_RULES_METERS,
    )
    write_layer(buffer_output_file, water_street_buffer_layer_name(), water_street_buffers)
    log_success("Water OSM street preparation finished.")


def main() -> None:
    """Run the water OSM street preparation for one municipality."""

    parser = ColoredArgumentParser(
        description="Prepare water-specific OSM street exclusion data."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()
    prepare_water_osm_streets(args.municipality)


if __name__ == "__main__":
    main()
