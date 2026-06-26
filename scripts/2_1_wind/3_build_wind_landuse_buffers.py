"""
Script 3: Build wind-specific landuse buffer layers.

Workflow:
1. Read the wind landuse exclusion layer created by wind script 2.
2. Select source layers that need an additional distance buffer.
3. Buffer those source layers in EPSG:25832.
4. Clip the buffered result back to the municipality boundary.
5. Write one GeoPackage for validation and later map integration.
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
from utils import (
    ColoredArgumentParser,
    log_detail,
    log_info,
    log_success,
    log_warning,
)


# -----------------------------------------------------------------------------
# 0. Input and output paths
# -----------------------------------------------------------------------------
# input
BOUNDARY_DIR = BASE_DIR / "data/processed/1_base_boundaries"

# input/output
WIND_OUTPUT_DIR = BASE_DIR / "data/processed/2_technology_wind"


# =============================================================================
# 1. Wind buffer rules
# =============================================================================
# Distances are first working assumptions for the project workflow.
# They should be replaced or adjusted once the exact legal/planning rule is set.
WIND_LANDUSE_BUFFER_RULES_METERS = {
    "ln_wohnnutzung": 500,
    "ln_oeffentlicheeinrichtungen": 300,
    "ln_bestattung": 0,
    "ln_freiluftundnaherholung": 0,
    "ln_freizeitanlage": 0,
    "ln_sportanlage": 0,
    "ln_gewerblichedienstleistungen": 0,
    "ln_industrieundverarbeitendesgewerbe": 0,
    "ln_versorgungundentsorgung": 0,
}


# =============================================================================
# 2. Helper functions
# =============================================================================
def wind_landuse_exclusion_file(municipality_name: str) -> Path:
    """Return the wind landuse exclusion GeoPackage."""

    safe_name = safe_filename(municipality_name)
    return WIND_OUTPUT_DIR / f"{safe_name}_landuse_wind_ausschluss.gpkg"


def wind_landuse_buffer_file(municipality_name: str) -> Path:
    """Return the wind landuse buffer GeoPackage."""

    safe_name = safe_filename(municipality_name)
    return WIND_OUTPUT_DIR / f"{safe_name}_landuse_wind_ausschluss_puffer.gpkg"


def boundary_file(municipality_name: str) -> Path:
    """Return the municipality boundary GeoPackage."""

    safe_name = safe_filename(municipality_name)
    return BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"


def layer_name_for_source(source_layer: str) -> str:
    """Create a GeoPackage layer name for one buffered source layer."""

    return f"puffer_{source_layer}"


def read_wind_landuse_exclusion(input_file: Path) -> gpd.GeoDataFrame:
    """Read the wind landuse exclusion layer."""

    if not input_file.exists():
        raise FileNotFoundError(
            "Wind landuse exclusion file not found. "
            f"Run wind script 2 first: {display_path(input_file)}"
        )

    return gpd.read_file(input_file, layer="landuse_wind_ausschluss")


def read_boundary(input_file: Path) -> gpd.GeoDataFrame:
    """Read the municipality boundary."""

    if not input_file.exists():
        raise FileNotFoundError(
            "Municipality boundary file not found. "
            f"Run prepare-data script 2 first: {display_path(input_file)}"
        )

    return gpd.read_file(input_file).to_crs(epsg=25832)


def build_buffer_for_source_layer(
    landuse: gpd.GeoDataFrame,
    boundary: gpd.GeoDataFrame,
    source_layer: str,
    buffer_meters: float,
) -> gpd.GeoDataFrame:
    """Build one clipped buffer layer for one landuse source layer."""

    source_data = landuse[landuse["source_layer"] == source_layer].copy()

    if source_data.empty:
        log_warning(f"No features found for buffer source layer: {source_layer}")
        return gpd.GeoDataFrame(
            {"source_layer": [], "buffer_m": [], "geometry": []},
            geometry="geometry",
            crs="EPSG:25832",
        )

    source_data = source_data.to_crs(epsg=25832)
    source_data["buffer_m"] = buffer_meters
    source_data["geometry"] = source_data.geometry.buffer(buffer_meters)

    buffered = gpd.clip(source_data, boundary, keep_geom_type=True)

    if buffered.empty:
        return gpd.GeoDataFrame(
            {"source_layer": [], "buffer_m": [], "geometry": []},
            geometry="geometry",
            crs="EPSG:25832",
        )

    buffered = buffered[buffered.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]
    return buffered


def merge_buffer_layers(buffer_layers: list[gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
    """Merge all non-empty buffer layers into one overview layer."""

    non_empty_layers = [layer for layer in buffer_layers if not layer.empty]

    if not non_empty_layers:
        return gpd.GeoDataFrame(
            {"source_layer": [], "buffer_m": [], "geometry": []},
            geometry="geometry",
            crs="EPSG:25832",
        )

    return gpd.GeoDataFrame(
        pd.concat(non_empty_layers, ignore_index=True),
        geometry="geometry",
        crs="EPSG:25832",
    )


# =============================================================================
# 3. Build buffers for one municipality
# =============================================================================
def build_wind_landuse_buffers(municipality_name: str) -> None:
    """Build wind-specific landuse buffers for one municipality."""

    input_file = wind_landuse_exclusion_file(municipality_name)
    output_file = wind_landuse_buffer_file(municipality_name)
    municipality_boundary_file = boundary_file(municipality_name)

    WIND_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(output_file)

    landuse = read_wind_landuse_exclusion(input_file)
    boundary = read_boundary(municipality_boundary_file)

    log_info(f"Building wind landuse buffers for: {municipality_name}")
    log_info(f"Input: {display_path(input_file)}")
    log_info(f"Boundary: {display_path(municipality_boundary_file)}")
    log_info(f"Output: {display_path(output_file)}")

    buffer_layers = []

    for source_layer, buffer_meters in WIND_LANDUSE_BUFFER_RULES_METERS.items():
        log_detail(f"Buffer rule: {source_layer} -> {buffer_meters} m")

        buffered = build_buffer_for_source_layer(
            landuse,
            boundary,
            source_layer,
            buffer_meters,
        )

        buffer_layers.append(buffered)
        write_layer(output_file, layer_name_for_source(source_layer), buffered)

    merged = merge_buffer_layers(buffer_layers)
    write_layer(output_file, "landuse_wind_ausschluss_puffer", merged)

    log_success("Wind landuse buffer preparation finished.")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = ColoredArgumentParser(
        description="Build wind-specific buffers from landuse exclusion layers."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    return parser.parse_args()


def main() -> None:
    """Run wind landuse buffer preparation for one municipality."""

    args = parse_arguments()
    build_wind_landuse_buffers(args.municipality)


if __name__ == "__main__":
    main()
