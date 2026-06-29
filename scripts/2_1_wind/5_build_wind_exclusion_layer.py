"""
Script 5: Build one combined wind exclusion layer.

Workflow:
1. Read the buffered wind landuse exclusion layer from wind script 3.
2. Read wind OSM street outputs from wind script 4.
3. Clip polygon inputs exactly to the municipality boundary.
4. Keep OSM street classes with 0 m buffer as line context layers.
5. Write validation layers and one combined polygon exclusion layer.
"""

from pathlib import Path
import argparse
import sys

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "utils"))
from landuse_utils import (
    BASE_DIR,
    display_path,
    remove_existing_output,
    safe_filename,
    write_layer,
)
from utils import ColoredArgumentParser, log_info, log_success, log_warning


# -----------------------------------------------------------------------------
# 0. Input and output paths
# -----------------------------------------------------------------------------
# input
BOUNDARY_DIR = BASE_DIR / "data/processed/1_base_boundaries"

# input/output
WIND_OUTPUT_DIR = BASE_DIR / "data/processed/2_technology_wind"


# =============================================================================
# 1. Layer and file helpers
# =============================================================================
def boundary_file(municipality_name: str) -> Path:
    """Return the municipality boundary GeoPackage."""

    safe_name = safe_filename(municipality_name)
    return BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"


def wind_landuse_buffer_file(municipality_name: str) -> Path:
    """Return the buffered wind landuse exclusion GeoPackage."""

    safe_name = safe_filename(municipality_name)
    return WIND_OUTPUT_DIR / f"{safe_name}_landuse_wind_ausschluss_puffer.gpkg"


def wind_osm_buffer_file(municipality_name: str) -> Path:
    """Return the buffered wind OSM street exclusion GeoPackage."""

    safe_name = safe_filename(municipality_name)
    return WIND_OUTPUT_DIR / f"{safe_name}_osm_wind_streets_puffer.gpkg"


def wind_osm_street_file(municipality_name: str) -> Path:
    """Return the wind-specific OSM street line GeoPackage."""

    safe_name = safe_filename(municipality_name)
    return WIND_OUTPUT_DIR / f"{safe_name}_osm_wind_streets.gpkg"


def wind_exclusion_output_file(municipality_name: str) -> Path:
    """Return the combined wind exclusion GeoPackage."""

    safe_name = safe_filename(municipality_name)
    return WIND_OUTPUT_DIR / f"{safe_name}_wind_ausschluss_gesamt.gpkg"


def landuse_buffer_layer_name() -> str:
    """Return the merged landuse buffer layer name."""

    return "landuse_wind_ausschluss_puffer"


def osm_buffer_layer_name() -> str:
    """Return the merged OSM street buffer layer name."""

    return "osm_streets_wind_ausschluss_puffer"


def osm_without_buffer_layer_name() -> str:
    """Return the OSM street line layer for classes with 0 m buffer."""

    return "osm_streets_wind_ohne_puffer"


# =============================================================================
# 2. Processing helpers
# =============================================================================
def read_layer(input_file: Path, layer_name: str, label: str) -> gpd.GeoDataFrame:
    """Read one required GeoPackage layer."""

    if not input_file.exists():
        raise FileNotFoundError(f"{label} not found: {display_path(input_file)}")

    data = gpd.read_file(input_file, layer=layer_name)

    if data.empty:
        log_warning(f"{label} is empty: {layer_name}")

    return data.to_crs(epsg=25832)


def read_optional_layer(
    input_file: Path,
    layer_name: str,
    label: str,
) -> gpd.GeoDataFrame:
    """Read one optional GeoPackage layer, or return an empty layer."""

    if not input_file.exists():
        log_warning(f"{label} not found: {display_path(input_file)}")
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:25832")

    data = gpd.read_file(input_file, layer=layer_name)

    if data.empty:
        log_warning(f"{label} is empty: {layer_name}")

    return data.to_crs(epsg=25832)


def read_boundary(input_file: Path) -> gpd.GeoDataFrame:
    """Read the municipality boundary."""

    if not input_file.exists():
        raise FileNotFoundError(
            "Municipality boundary file not found. "
            f"Run prepare-data script 2 first: {display_path(input_file)}"
        )

    return gpd.read_file(input_file).to_crs(epsg=25832)


def empty_exclusion_gdf(crs: str = "EPSG:25832") -> gpd.GeoDataFrame:
    """Create an empty polygon GeoDataFrame for stable output layers."""

    return gpd.GeoDataFrame(
        {"source_type": [], "exclusion_category": [], "geometry": []},
        geometry="geometry",
        crs=crs,
    )


def empty_line_gdf(crs: str = "EPSG:25832") -> gpd.GeoDataFrame:
    """Create an empty line GeoDataFrame for stable output layers."""

    return gpd.GeoDataFrame(
        {"source_type": [], "exclusion_category": [], "geometry": []},
        geometry="geometry",
        crs=crs,
    )


def clip_exclusion_layer(
    data: gpd.GeoDataFrame,
    boundary: gpd.GeoDataFrame,
    source_type: str,
) -> gpd.GeoDataFrame:
    """Clip one exclusion input to the municipality and add source metadata."""

    if data.empty:
        return empty_exclusion_gdf()

    clipped = gpd.clip(data, boundary, keep_geom_type=True)

    if clipped.empty:
        return empty_exclusion_gdf()

    clipped = clipped[clipped.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]

    if clipped.empty:
        return empty_exclusion_gdf()

    clipped = clipped.copy()
    clipped["source_type"] = source_type
    clipped["exclusion_category"] = "wind_ausschluss"
    return clipped


def clip_line_context_layer(
    data: gpd.GeoDataFrame,
    boundary: gpd.GeoDataFrame,
    source_type: str,
) -> gpd.GeoDataFrame:
    """Clip OSM context lines with 0 m buffer for validation and display."""

    if data.empty:
        return empty_line_gdf()

    clipped = gpd.clip(data, boundary, keep_geom_type=True)

    if clipped.empty:
        return empty_line_gdf()

    clipped = clipped[clipped.geometry.geom_type.isin(["LineString", "MultiLineString"])]

    if clipped.empty:
        return empty_line_gdf()

    clipped = clipped.copy()
    clipped["source_type"] = source_type
    clipped["exclusion_category"] = "wind_ausschluss_context_without_buffer"
    return clipped


def merge_exclusion_layers(layers: list[gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
    """Merge and dissolve all non-empty exclusion layers into one geometry."""

    non_empty_layers = [layer for layer in layers if not layer.empty]

    if not non_empty_layers:
        return empty_exclusion_gdf()

    merged = gpd.GeoDataFrame(
        pd.concat(non_empty_layers, ignore_index=True),
        geometry="geometry",
        crs="EPSG:25832",
    )

    dissolved_geometry = merged.geometry.unary_union
    return gpd.GeoDataFrame(
        {
            "source_type": ["landuse_osm_combined"],
            "exclusion_category": ["wind_ausschluss_gesamt"],
            "geometry": [dissolved_geometry],
        },
        geometry="geometry",
        crs="EPSG:25832",
    )


# =============================================================================
# 3. Build combined exclusion layer
# =============================================================================
def build_wind_exclusion_layer(municipality_name: str) -> None:
    """Build one combined wind exclusion layer for one municipality."""

    boundary_input = boundary_file(municipality_name)
    landuse_input = wind_landuse_buffer_file(municipality_name)
    osm_buffer_input = wind_osm_buffer_file(municipality_name)
    osm_line_input = wind_osm_street_file(municipality_name)
    output_file = wind_exclusion_output_file(municipality_name)

    WIND_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(output_file)

    log_info(f"Building combined wind exclusion layer for: {municipality_name}")
    log_info(f"Boundary: {display_path(boundary_input)}")
    log_info(f"Input 1: {display_path(landuse_input)}")
    log_info(f"Input 2: {display_path(osm_buffer_input)}")
    log_info(f"Input 3: {display_path(osm_line_input)}")
    log_info(f"Output: {display_path(output_file)}")

    boundary = read_boundary(boundary_input)
    landuse_buffer = read_layer(
        landuse_input,
        landuse_buffer_layer_name(),
        "Wind landuse buffer layer",
    )
    osm_buffer = read_optional_layer(
        osm_buffer_input,
        osm_buffer_layer_name(),
        "Wind OSM street buffer layer",
    )
    osm_lines_without_buffer = read_optional_layer(
        osm_line_input,
        osm_without_buffer_layer_name(),
        "Wind OSM street line layer without buffer",
    )

    landuse_clipped = clip_exclusion_layer(landuse_buffer, boundary, "landuse")
    osm_clipped = clip_exclusion_layer(osm_buffer, boundary, "osm_streets")
    osm_lines_clipped = clip_line_context_layer(
        osm_lines_without_buffer,
        boundary,
        "osm_streets",
    )
    combined = merge_exclusion_layers([landuse_clipped, osm_clipped])

    write_layer(
        output_file,
        "wind_ausschluss_landuse_puffer",
        landuse_clipped,
    )
    write_layer(
        output_file,
        "wind_ausschluss_osm_streets_puffer",
        osm_clipped,
    )
    write_layer(
        output_file,
        "wind_ausschluss_osm_streets_ohne_puffer",
        osm_lines_clipped,
    )
    write_layer(output_file, "wind_ausschluss_gesamt", combined)

    log_success("Combined wind exclusion layer finished.")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = ColoredArgumentParser(
        description="Build one combined wind exclusion layer."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    return parser.parse_args()


def main() -> None:
    """Run wind exclusion layer preparation for one municipality."""

    args = parse_arguments()
    build_wind_exclusion_layer(args.municipality)


if __name__ == "__main__":
    main()
