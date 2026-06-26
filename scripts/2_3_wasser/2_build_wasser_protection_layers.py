"""
Build municipality water-specific protection layers from official SHP downloads.

Workflow:
1. Read the municipality boundary from the shared base workflow.
2. Read the official LfU water protection SHP datasets.
3. Clip them to the municipality.
4. Write detail layers and one merged hard water-restriction layer.
"""

from pathlib import Path
import argparse
import re
import sys

import geopandas as gpd
import pandas as pd
from pyogrio.errors import DataSourceError
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "utils"))
from utils import ColoredArgumentParser, log_error, log_info, log_success, log_warning


BASE_DIR = Path(__file__).resolve().parent.parent.parent

BOUNDARY_DIR = BASE_DIR / "data/processed/1_base_boundaries"
WASSERSCHUTZ_RAW_DIR = BASE_DIR / "data/raw/wasser/wasserschutzgebiete"
OUTPUT_DIR = BASE_DIR / "data/processed/2_technology_wasser"

WASSER_HARD_DATASET_DIRS = {
    "trinkwasserschutzgebiete": WASSERSCHUTZ_RAW_DIR / "trinkwasserschutzgebiete",
    "heilquellenschutzgebiete": WASSERSCHUTZ_RAW_DIR / "heilquellenschutzgebiete",
}


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


def empty_polygon_gdf() -> gpd.GeoDataFrame:
    """Create an empty polygon GeoDataFrame with a valid geometry column."""

    return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:25832")


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
            "Water protection processing stopped because the GeoPackage is still open."
        ) from error


def find_vector_files(dataset_dir: Path) -> list[Path]:
    """Find all supported vector files inside one extracted dataset folder."""

    supported_suffixes = {".shp", ".gpkg", ".geojson"}

    if not dataset_dir.exists():
        return []

    return sorted(
        file
        for file in dataset_dir.rglob("*")
        if file.is_file() and file.suffix.lower() in supported_suffixes
    )


def read_clipped_polygon_features(
    dataset_name: str,
    dataset_dir: Path,
    boundary: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Read one extracted dataset folder and clip polygon features."""

    if not dataset_dir.exists():
        log_warning(f"Missing extracted water dataset folder: {display_path(dataset_dir)}")
        return empty_polygon_gdf()

    boundary_25832 = boundary.to_crs(epsg=25832)
    bbox = tuple(boundary_25832.total_bounds)
    clipped_parts = []

    for vector_file in find_vector_files(dataset_dir):
        try:
            data = gpd.read_file(vector_file, bbox=bbox)
        except DataSourceError:
            log_warning(f"Skipping unreadable vector file: {display_path(vector_file)}")
            continue

        if data.empty or data.crs is None:
            continue

        data = data[data.geometry.notna()]

        if data.empty:
            continue

        data = data.to_crs(epsg=25832)
        data = data[data.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]

        if data.empty:
            continue

        clipped = gpd.clip(data, boundary_25832, keep_geom_type=True)
        clipped = clipped[clipped.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]

        if clipped.empty:
            continue

        clipped["source_dataset"] = dataset_name
        clipped["source_file"] = vector_file.name
        clipped["restriktionsklasse"] = "wasser_hart"
        clipped_parts.append(clipped)

    if not clipped_parts:
        return empty_polygon_gdf()

    return gpd.GeoDataFrame(
        pd.concat(clipped_parts, ignore_index=True),
        geometry="geometry",
        crs="EPSG:25832",
    )


def merge_layers(group_layers: dict[str, gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
    """Merge all non-empty water restriction layers and dissolve overlaps."""

    merged_parts = [layer for layer in group_layers.values() if not layer.empty]

    if not merged_parts:
        return empty_polygon_gdf()

    merged_data = gpd.GeoDataFrame(
        pd.concat(merged_parts, ignore_index=True),
        geometry="geometry",
        crs="EPSG:25832",
    )
    dissolved_geometry = unary_union(merged_data.geometry)
    dissolved = gpd.GeoDataFrame(
        {
            "restriktionsklasse": ["wasser_hart"],
            "method_note": [
                "Trinkwasser- und Heilquellenschutzgebiete aus LfU-SHP-Downloads."
            ],
            "geometry": [dissolved_geometry],
        },
        geometry="geometry",
        crs="EPSG:25832",
    )
    dissolved = dissolved.explode(index_parts=False).reset_index(drop=True)
    return dissolved[dissolved.geometry.notna()]


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
            "Water protection processing stopped because the GeoPackage could not be written."
        ) from error

    if data.empty:
        log_warning(f"Written empty layer: {layer_name} (0 features)")
    else:
        log_success(f"Written {layer_name}: {len(data)} features")


def build_wasser_protection_layers(municipality_name: str) -> None:
    """Build clipped water protection GeoPackage for one municipality."""

    safe_name = safe_filename(municipality_name)
    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    output_file = OUTPUT_DIR / f"{safe_name}_wasserschutz_hart.gpkg"

    if not boundary_file.exists():
        raise FileNotFoundError(
            f"Boundary file not found: {boundary_file}. Run script 2 first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(output_file)

    boundary = gpd.read_file(boundary_file).to_crs(epsg=25832)

    log_info(f"Building water protection layers for: {municipality_name}")
    log_info(f"Boundary: {display_path(boundary_file)}")
    log_info(f"Output: {display_path(output_file)}")

    group_layers = {}
    for dataset_name, dataset_dir in WASSER_HARD_DATASET_DIRS.items():
        log_info(f"Reading water protection dataset: {dataset_name}")
        group_layers[dataset_name] = read_clipped_polygon_features(
            dataset_name,
            dataset_dir,
            boundary,
        )

    for dataset_name, data in group_layers.items():
        write_layer(output_file, dataset_name, data)

    merged = merge_layers(group_layers)
    write_layer(output_file, "wasserschutz_hart_merged", merged)

    log_success("Water protection layer processing finished.")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = ColoredArgumentParser(
        description="Build water-specific protection layers for one municipality."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    return parser.parse_args()


def main() -> None:
    """Run the water protection processing."""

    args = parse_arguments()
    build_wasser_protection_layers(args.municipality)


if __name__ == "__main__":
    main()

