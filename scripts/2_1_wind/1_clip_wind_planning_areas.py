"""
Script 1: Clip all wind datasets to one municipality.

Workflow:
1. Read the municipality boundary from script 2.
2. Read the official WFS exports for Vorranggebiete and Vorbehaltsgebiete.
3. Clip both datasets exactly to the municipality boundary.
4. Store the municipality result as one GeoPackage with detail layers and one
   combined technology layer:
   - wind_vorranggebiete_<municipality>
   - wind_vorbehaltsgebiete_<municipality>
   - wind_spezifisch
"""

from pathlib import Path
import re
import sys

import geopandas as gpd
import pandas as pd
from pyogrio.errors import DataSourceError

sys.path.append(str(Path(__file__).resolve().parent.parent / "utils"))
from utils import ColoredArgumentParser, log_error, log_info, log_success, log_warning


BASE_DIR = Path(__file__).resolve().parent.parent.parent

BOUNDARY_DIR = BASE_DIR / "data/processed/boundaries"
WIND_RAW_DIR = BASE_DIR / "data/raw/wind"
WIND_PROCESSED_DIR = BASE_DIR / "data/processed/wind"

WIND_VORRANG_FILE = WIND_RAW_DIR / "wind_vorranggebiete.gpkg"
WIND_VORBEHALT_FILE = WIND_RAW_DIR / "wind_vorbehaltsgebiete.gpkg"


def safe_filename(name: str) -> str:
    """Create the same filename format as script 1."""

    return name.lower().replace(" ", "_")


def vorrang_layer_name(municipality_name: str) -> str:
    """Create a municipality-specific layer name for wind vorrang areas."""

    return f"wind_vorranggebiete_{safe_filename(municipality_name)}"


def vorbehalt_layer_name(municipality_name: str) -> str:
    """Create a municipality-specific layer name for wind vorbehalt areas."""

    return f"wind_vorbehaltsgebiete_{safe_filename(municipality_name)}"


def wind_specific_layer_name() -> str:
    """Create the shared layer name for all wind-specific planning areas."""

    return "wind_spezifisch"


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
        log_info("Then run the wind script again.")
        raise SystemExit(
            "Wind script 1 stopped because an output GeoPackage is still open."
        ) from error


def read_single_layer(vector_file: Path, bbox: tuple[float, float, float, float]) -> gpd.GeoDataFrame:
    """Read one vector file with a municipality bounding box pre-filter."""

    try:
        data = gpd.read_file(vector_file, bbox=bbox)
    except DataSourceError as error:
        raise SystemExit(f"Unreadable dataset: {display_path(vector_file)}") from error

    if data.empty:
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:25832")

    data = data[data.geometry.notna()]
    data = data[data.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]

    if data.empty:
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:25832")

    if data.crs is None:
        raise SystemExit(f"Dataset has no CRS: {display_path(vector_file)}")

    return data.to_crs(epsg=25832)


def clip_dataset(
    vector_file: Path,
    boundary: gpd.GeoDataFrame,
    source_name: str,
) -> gpd.GeoDataFrame:
    """Clip one polygon dataset to the municipality boundary."""

    if not vector_file.exists() or vector_file.stat().st_size == 0:
        log_error(f"Missing input dataset: {display_path(vector_file)}")
        raise SystemExit(
            "Wind script 1 stopped because one required wind dataset is missing."
        )

    boundary_25832 = boundary.to_crs(epsg=25832)
    bbox = tuple(boundary_25832.total_bounds)

    log_info(f"Reading dataset: {source_name}")
    data = read_single_layer(vector_file, bbox)

    if data.empty:
        log_warning(f"No polygon features found in: {source_name}")
        return data

    clipped = gpd.clip(data, boundary_25832, keep_geom_type=True)

    if clipped.empty:
        return clipped

    clipped = clipped[clipped.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]

    if clipped.empty:
        return clipped

    clipped["source_dataset"] = source_name
    return clipped


def merge_wind_specific_layers(
    wind_layers: list[gpd.GeoDataFrame],
) -> gpd.GeoDataFrame:
    """Merge all wind-specific layers into one QGIS-friendly overview layer."""

    non_empty_layers = [layer for layer in wind_layers if not layer.empty]

    if not non_empty_layers:
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:25832")

    return gpd.GeoDataFrame(
        pd.concat(non_empty_layers, ignore_index=True),
        geometry="geometry",
        crs="EPSG:25832",
    )


def write_layer(output_file: Path, layer_name: str, data: gpd.GeoDataFrame) -> None:
    """Write one GeoPackage layer, even when it contains no features."""

    data = clean_for_geopackage(data)
    try:
        data.to_file(output_file, layer=layer_name, driver="GPKG")
    except Exception as error:
        log_error(f"Could not write layer: {layer_name}")
        log_error(f"Output file: {display_path(output_file)}")
        log_info("Close the file in QGIS or remove the layer from the QGIS project.")
        log_info("Then run the wind script again.")
        raise SystemExit(
            "Wind script 1 stopped because the GeoPackage could not be written."
        ) from error

    if data.empty:
        log_warning(f"Written empty layer: {layer_name} (0 features)")
    else:
        log_success(f"Written {layer_name}: {len(data)} features")


def clip_wind_datasets_for_municipality(municipality_name: str) -> None:
    """Clip the official wind datasets for one municipality."""

    safe_name = safe_filename(municipality_name)
    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    output_file = WIND_PROCESSED_DIR / f"{safe_name}_wind_layers.gpkg"

    if not boundary_file.exists():
        raise FileNotFoundError(
            f"Boundary file not found: {boundary_file}. Run script 2 first."
        )

    WIND_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(output_file)

    boundary = gpd.read_file(boundary_file).to_crs(epsg=25832)

    log_info(f"Clipping wind datasets for: {municipality_name}")
    log_info(f"Boundary: {display_path(boundary_file)}")
    log_info(f"Output: {display_path(output_file)}")

    vorrang = clip_dataset(WIND_VORRANG_FILE, boundary, "wind_vorranggebiete")
    vorbehalt = clip_dataset(WIND_VORBEHALT_FILE, boundary, "wind_vorbehaltsgebiete")
    wind_spezifisch = merge_wind_specific_layers([vorrang, vorbehalt])

    write_layer(output_file, vorrang_layer_name(municipality_name), vorrang)
    write_layer(output_file, vorbehalt_layer_name(municipality_name), vorbehalt)
    write_layer(output_file, wind_specific_layer_name(), wind_spezifisch)
    log_success("Wind dataset clipping finished.")


def main() -> None:
    parser = ColoredArgumentParser(
        description="Clip all wind datasets to one municipality."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()
    clip_wind_datasets_for_municipality(args.municipality)


if __name__ == "__main__":
    main()
