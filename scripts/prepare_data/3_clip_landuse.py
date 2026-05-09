"""
Script 3: Clip official landuse data.

Workflow:
1. Read the official landuse (landnutzung.gpkg) GeoPackage downloaded by script 0.
2. Read the municipality boundary created by script 1.
3. Use the municipality bounding box as a fast pre-filter for reading landuse data.
4. Clip each polygon landuse layer exactly with the municipality boundary.
5. Merge the clipped layers into one municipality landuse dataset.
   Output: landnutzung_<municipality>.gpkg
"""

from pathlib import Path
import argparse
import re
import sys

import geopandas as gpd
import pandas as pd
from pyogrio.errors import DataSourceError

sys.path.append(str(Path(__file__).resolve().parent.parent / "utils"))
from utils import ColoredArgumentParser, log_error, log_info, log_success, log_warning


BASE_DIR = Path(__file__).resolve().parent.parent.parent

# -----------------------------------------------------------------------------
# 0. Define input and output paths
# -----------------------------------------------------------------------------
BOUNDARY_DIR = BASE_DIR / "data/processed/boundaries"
LANDUSE_FILE = BASE_DIR / "data/raw/landuse/landnutzung.gpkg"
OUTPUT_DIR = BASE_DIR / "data/processed/landuse"

# Expected layer names in the official landuse GeoPackage.
EXPECTED_LANDUSE_LAYERS = {
    "ln_abbau",
    "ln_aquakulturundfischereiwirtschaft",
    "ln_bahnverkehr",
    "ln_bestattung",
    "ln_flugverkehr",
    "ln_forstwirtschaft",
    "ln_freiluftundnaherholung",
    "ln_freizeitanlage",
    "ln_gewerblichedienstleistungen",
    "ln_industrieundverarbeitendesgewerbe",
    "ln_kulturundunterhaltung",
    "ln_lagerung",
    "ln_landwirtschaft",
    "ln_oeffentlicheeinrichtungen",
    "ln_ohnenutzung",
    "ln_schiffsverkehr",
    "ln_sportanlage",
    "ln_strassenundwegeverkehr",
    "ln_versorgungundentsorgung",
    "ln_wasserwirtschaft",
    "ln_wohnnutzung",
}

# -----------------------------------------------------------------------------
# Helper functions
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


def list_layers(vector_file: Path) -> list[str | None]:
    """List layers for a vector file, or return None for single-layer files."""

    if vector_file.suffix.lower() != ".gpkg":
        return [None]

    try:
        import pyogrio
    except ImportError:
        return [None]

    try:
        return [layer[0] for layer in pyogrio.list_layers(vector_file)]
    except DataSourceError:
        log_warning(f"Skipping unreadable vector file: {display_path(vector_file)}")
        return []


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


def read_vector_layer(
    vector_file: Path,
    layer: str | None,
    bbox: tuple[float, float, float, float] | None = None,
) -> gpd.GeoDataFrame:
    """Read one vector layer, optionally limited to a bounding box."""

    if layer is None:
        return gpd.read_file(vector_file, bbox=bbox)

    return gpd.read_file(vector_file, layer=layer, bbox=bbox)


def remove_existing_output(output_file: Path) -> None:
    """Remove an old output file before writing a fresh GeoPackage."""

    if not output_file.exists():
        return

    try:
        output_file.unlink()
    except PermissionError as error:
        # Stop with a clear message if the GeoPackage is still open in QGIS.
        log_error("Output GeoPackage is locked and cannot be overwritten.")
        log_error(f"Locked file: {display_path(output_file)}")
        log_info("Close the file in QGIS or remove the layer from the QGIS project.")
        log_info("Then run the pipeline again.")
        raise SystemExit(
            "Script 3 stopped because an output GeoPackage is still open."
        ) from error


# -----------------------------------------------------------------------------
# 1. Read landuse layers with bounding-box filter
# -----------------------------------------------------------------------------
def clip_and_merge_landuse_layers(boundary: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Read, clip and merge all official landuse polygon layers."""

    if not LANDUSE_FILE.exists() or LANDUSE_FILE.stat().st_size == 0:
        log_error("Official landuse data is missing.")
        log_error(f"Expected file: {display_path(LANDUSE_FILE)}")
        log_info("Run this first:")
        log_info("python scripts/prepare_data/0_download_data.py --technology wind")
        raise SystemExit(
            "Script 3 stopped because the official landuse dataset is missing."
        )

    boundary_25832 = boundary.to_crs(epsg=25832)

    # The bbox reduces the amount of Bavaria-wide data read from each layer.
    landuse_bbox = tuple(boundary_25832.total_bounds)
    clipped_layers = []

    for layer in list_layers(LANDUSE_FILE):
        source_name = layer or LANDUSE_FILE.stem

        if source_name not in EXPECTED_LANDUSE_LAYERS:
            log_warning(f"Unexpected landuse layer, still checking: {source_name}")

        log_info(f"Reading landuse layer: {source_name}")

        try:
            # Read only features near the municipality to avoid loading all Bavaria.
            data = read_vector_layer(LANDUSE_FILE, layer, bbox=landuse_bbox)
        except DataSourceError:
            log_warning(f"Skipping unreadable layer: {source_name}")
            continue

        if data.empty or data.geometry.is_empty.all():
            continue

        data = data[data.geometry.notna()]
        geometry_types = set(data.geometry.geom_type.dropna().unique())

        # clip only (Multi)Polygon
        if not geometry_types.intersection({"Polygon", "MultiPolygon"}):
            log_warning(f"Skipping non-polygon layer: {source_name}")
            continue

        data = data[data.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]
        data = data.to_crs(epsg=25832)

        # The exact municipality boundary is used after the fast bbox pre-filter.
        # keep_geom_type keeps the landuse output as polygons only.
        # Point or line fragments from boundary intersections are intentionally removed.
        clipped = gpd.clip(data, boundary_25832, keep_geom_type=True)

        if clipped.empty:
            continue

        clipped = clipped[
            clipped.geometry.geom_type.isin(["Polygon", "MultiPolygon"])
        ]

        if clipped.empty:
            continue

        clipped["source_layer"] = source_name
        clipped_layers.append(clipped)

    if not clipped_layers:
        log_warning("No matching official landuse features found for the municipality.")
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:25832")

    return gpd.GeoDataFrame(
        pd.concat(clipped_layers, ignore_index=True),
        geometry="geometry",
        crs="EPSG:25832",
    )


# -----------------------------------------------------------------------------
# 2. Write the municipality landuse GeoPackage
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
            "Script 3 stopped because the GeoPackage could not be written."
        ) from error

    log_success(f"Written {layer_name}: {len(data)} features")


# -----------------------------------------------------------------------------
# 3. Run landuse processing for one municipality
# -----------------------------------------------------------------------------
def clip_landuse_for_municipality(municipality_name: str) -> None:
    """Clip official landuse data for one municipality."""

    safe_name = safe_filename(municipality_name)

    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    output_file = OUTPUT_DIR / f"landnutzung_{safe_name}.gpkg"

    if not boundary_file.exists():
        raise FileNotFoundError(
            f"Boundary file not found: {boundary_file}. Run script 1 first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(output_file)

    boundary = gpd.read_file(boundary_file).to_crs(epsg=25832)

    log_info(f"Clipping official landuse for: {municipality_name}")
    log_info(f"Boundary: {display_path(boundary_file)}")
    log_info(f"Output: {display_path(output_file)}")

    log_info("Reading, clipping and merging official landuse layers.")
    landuse = clip_and_merge_landuse_layers(boundary)

    write_layer(output_file, "official_landuse", landuse)

    log_success("Official landuse clipping finished.")


def main() -> None:
    parser = ColoredArgumentParser(
        description="Clip official landuse data to one municipality."
    )

    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()
    clip_landuse_for_municipality(args.municipality)


if __name__ == "__main__":
    main()
