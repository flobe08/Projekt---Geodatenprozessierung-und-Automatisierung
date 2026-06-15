"""
Script 3: Build municipality protection layers.

Workflow:
1. Read the municipality boundary from script 2.
2. Read the official general protection datasets downloaded by script 1.
3. Use the municipality bounding box as a fast pre-filter.
4. Clip the polygon protection datasets exactly to the municipality boundary.
5. Write three municipality GeoPackages:
   - naturschutz_allgemein_hart
   - naturschutz_allgemein_weich
   - naturschutz_wind
6. Each GeoPackage contains the clipped source layers and one merged layer.

Hinweis:
Punktförmige Naturdenkmale und punktförmige geschützte Landschaftsbestandteile
werden als eigene geclippte Hinweislayer mit ausgegeben, aber aktuell nicht in
den zusammengeführten harten Flächenlayer übernommen. Für automatische
Ausschlussflächen sind die flächenhaften Datensätze methodisch sauberer.
"""

from pathlib import Path
import re
import sys

import geopandas as gpd
import pandas as pd
from pyogrio.errors import DataSourceError
from shapely.ops import unary_union

sys.path.append(str(Path(__file__).resolve().parent.parent / "utils"))
from utils import ColoredArgumentParser, log_error, log_info, log_success, log_warning


BASE_DIR = Path(__file__).resolve().parent.parent.parent


# -----------------------------------------------------------------------------
# 0. Input and output paths
# -----------------------------------------------------------------------------
BOUNDARY_DIR = BASE_DIR / "data/processed/boundaries"
SCHUTZGEBIETE_RAW_DIR = BASE_DIR / "data/raw/schutzgebiete"
NATURA2000_RAW_DIR = SCHUTZGEBIETE_RAW_DIR / "natura2000"
WIND_RAW_DIR = BASE_DIR / "data/raw/wind"
OUTPUT_DIR = BASE_DIR / "data/processed/schutzgebiete"

HARD_DATASET_DIRS = {
    "naturschutzgebiete": SCHUTZGEBIETE_RAW_DIR / "naturschutzgebiete",
    "nationalparke": SCHUTZGEBIETE_RAW_DIR / "nationalparke",
    "nationale_naturmonumente": SCHUTZGEBIETE_RAW_DIR / "nationale_naturmonumente",
    "naturdenkmale_flaechen": SCHUTZGEBIETE_RAW_DIR / "naturdenkmale_flaechen",
    "geschuetzte_landschaftsbestandteile_flaechen": (
        SCHUTZGEBIETE_RAW_DIR / "geschuetzte_landschaftsbestandteile_flaechen"
    ),
    "ramsar_gebiete": SCHUTZGEBIETE_RAW_DIR / "ramsar_gebiete",
    "natura2000_ffh": NATURA2000_RAW_DIR / "ffh",
    "natura2000_vogelschutz": NATURA2000_RAW_DIR / "vogelschutz",
}

SOFT_DATASET_DIRS = {
    "biosphaerenreservate": SCHUTZGEBIETE_RAW_DIR / "biosphaerenreservate",
    "landschaftsschutzgebiete": SCHUTZGEBIETE_RAW_DIR / "landschaftsschutzgebiete",
    "naturparke": SCHUTZGEBIETE_RAW_DIR / "naturparke",
}

WIND_DATASET_DIRS = {
    # Wind-specific bird and species-sensitivity layer.
    "vogelkulissen_2024": WIND_RAW_DIR / "vogelkulissen_2024",
}

POINT_DATASET_DIRS = {
    "naturdenkmale_punkte": SCHUTZGEBIETE_RAW_DIR / "naturdenkmale_punkte",
    "geschuetzte_landschaftsbestandteile_punkte": (
        SCHUTZGEBIETE_RAW_DIR / "geschuetzte_landschaftsbestandteile_punkte"
    ),
}


# -----------------------------------------------------------------------------
# 1. General helper functions
# -----------------------------------------------------------------------------
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
            "Script 3 stopped because an output GeoPackage is still open."
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


def read_vector_layer(
    vector_file: Path,
    layer: str | None,
    bbox: tuple[float, float, float, float],
) -> gpd.GeoDataFrame:
    """Read one vector layer with a municipality bounding-box pre-filter."""

    if layer is None:
        return gpd.read_file(vector_file, bbox=bbox)

    return gpd.read_file(vector_file, layer=layer, bbox=bbox)


# -----------------------------------------------------------------------------
# 2. Read and clip protection datasets
# -----------------------------------------------------------------------------
def read_clipped_polygon_features(
    dataset_name: str,
    dataset_dir: Path,
    boundary: gpd.GeoDataFrame,
    restriktionsklasse: str,
) -> gpd.GeoDataFrame:
    """Read one extracted dataset folder and clip all polygon layers."""

    if not dataset_dir.exists():
        log_warning(f"Missing extracted dataset folder: {display_path(dataset_dir)}")
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:25832")

    boundary_25832 = boundary.to_crs(epsg=25832)
    bbox = tuple(boundary_25832.total_bounds)
    clipped_parts = []

    for vector_file in find_vector_files(dataset_dir):
        for layer_name in list_layers(vector_file):
            source_layer_name = layer_name or vector_file.stem

            try:
                data = read_vector_layer(vector_file, layer_name, bbox)
            except DataSourceError:
                log_warning(
                    f"Skipping unreadable layer: {display_path(vector_file)}"
                    f" ({source_layer_name})"
                )
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
            clipped["source_layer"] = source_layer_name
            clipped["restriktionsklasse"] = restriktionsklasse
            clipped_parts.append(clipped)

    if not clipped_parts:
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:25832")

    return gpd.GeoDataFrame(
        pd.concat(clipped_parts, ignore_index=True),
        geometry="geometry",
        crs="EPSG:25832",
    )


def read_clipped_point_features(
    dataset_name: str,
    dataset_dir: Path,
    boundary: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Read one extracted dataset folder and clip all point layers."""

    if not dataset_dir.exists():
        log_warning(f"Missing extracted dataset folder: {display_path(dataset_dir)}")
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:25832")

    boundary_25832 = boundary.to_crs(epsg=25832)
    bbox = tuple(boundary_25832.total_bounds)
    clipped_parts = []

    for vector_file in find_vector_files(dataset_dir):
        for layer_name in list_layers(vector_file):
            source_layer_name = layer_name or vector_file.stem

            try:
                data = read_vector_layer(vector_file, layer_name, bbox)
            except DataSourceError:
                log_warning(
                    f"Skipping unreadable layer: {display_path(vector_file)}"
                    f" ({source_layer_name})"
                )
                continue

            if data.empty or data.crs is None:
                continue

            data = data[data.geometry.notna()]

            if data.empty:
                continue

            data = data.to_crs(epsg=25832)
            data = data[data.geometry.geom_type.isin(["Point", "MultiPoint"])]

            if data.empty:
                continue

            clipped = gpd.clip(data, boundary_25832, keep_geom_type=True)
            clipped = clipped[clipped.geometry.geom_type.isin(["Point", "MultiPoint"])]

            if clipped.empty:
                continue

            clipped["source_dataset"] = dataset_name
            clipped["source_layer"] = source_layer_name
            clipped["restriktionsklasse"] = "allgemein_hart_punkte"
            clipped_parts.append(clipped)

    if not clipped_parts:
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:25832")

    return gpd.GeoDataFrame(
        pd.concat(clipped_parts, ignore_index=True),
        geometry="geometry",
        crs="EPSG:25832",
    )


def build_dataset_group(
    dataset_dirs: dict[str, Path],
    boundary: gpd.GeoDataFrame,
    restriktionsklasse: str,
) -> dict[str, gpd.GeoDataFrame]:
    """Build one clipped layer per source dataset inside a restriction group."""

    group_layers: dict[str, gpd.GeoDataFrame] = {}

    for dataset_name, dataset_dir in dataset_dirs.items():
        log_info(f"Reading protection dataset: {dataset_name}")
        group_layers[dataset_name] = read_clipped_polygon_features(
            dataset_name,
            dataset_dir,
            boundary,
            restriktionsklasse,
        )

    return group_layers


def build_point_group(boundary: gpd.GeoDataFrame) -> dict[str, gpd.GeoDataFrame]:
    """Build one clipped point layer per configured point dataset."""

    point_layers: dict[str, gpd.GeoDataFrame] = {}

    for dataset_name, dataset_dir in POINT_DATASET_DIRS.items():
        log_info(f"Reading point protection dataset: {dataset_name}")
        point_layers[dataset_name] = read_clipped_point_features(
            dataset_name,
            dataset_dir,
            boundary,
        )

    return point_layers


def merge_group_layers(group_layers: dict[str, gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
    """Merge all non-empty clipped source layers and dissolve overlaps."""

    merged_parts = [
        layer
        for layer in group_layers.values()
        if not layer.empty
    ]

    if not merged_parts:
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:25832")

    merged_data = gpd.GeoDataFrame(
        pd.concat(merged_parts, ignore_index=True),
        geometry="geometry",
        crs="EPSG:25832",
    )

    restriction_class = ""

    if "restriktionsklasse" in merged_data.columns and not merged_data.empty:
        restriction_class = str(merged_data["restriktionsklasse"].iloc[0])

    dissolved_geometry = unary_union(merged_data.geometry)
    dissolved = gpd.GeoDataFrame(
        {"restriktionsklasse": [restriction_class], "geometry": [dissolved_geometry]},
        geometry="geometry",
        crs="EPSG:25832",
    )

    dissolved = dissolved.explode(index_parts=False).reset_index(drop=True)
    dissolved = dissolved[dissolved.geometry.notna()]

    return dissolved


# -----------------------------------------------------------------------------
# 3. Write municipality protection layers
# -----------------------------------------------------------------------------
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
            "Script 3 stopped because the GeoPackage could not be written."
        ) from error

    if data.empty:
        log_warning(f"Written empty layer: {layer_name} (0 features)")
    else:
        log_success(f"Written {layer_name}: {len(data)} features")


def write_group_output(
    output_file: Path,
    merged_layer_name: str,
    group_layers: dict[str, gpd.GeoDataFrame],
    extra_layers: dict[str, gpd.GeoDataFrame] | None = None,
) -> None:
    """Write all source layers of one group and one merged layer to one GeoPackage."""

    remove_existing_output(output_file)

    for dataset_name, data in group_layers.items():
        write_layer(output_file, dataset_name, data)

    if extra_layers:
        for dataset_name, data in extra_layers.items():
            write_layer(output_file, dataset_name, data)

    merged_data = merge_group_layers(group_layers)
    write_layer(output_file, merged_layer_name, merged_data)
    log_info(f"Output written to: {display_path(output_file)}")


def build_protection_layers_for_municipality(municipality_name: str) -> None:
    """Build municipality protection GeoPackages for general and wind layers."""

    safe_name = safe_filename(municipality_name)
    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    hard_output_file = OUTPUT_DIR / f"{safe_name}_naturschutz_allgemein_hart.gpkg"
    soft_output_file = OUTPUT_DIR / f"{safe_name}_naturschutz_allgemein_weich.gpkg"
    wind_output_file = OUTPUT_DIR / f"{safe_name}_naturschutz_wind.gpkg"

    if not boundary_file.exists():
        raise FileNotFoundError(
            f"Boundary file not found: {boundary_file}. Run script 2 first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    boundary = gpd.read_file(boundary_file).to_crs(epsg=25832)

    log_info(f"Building protection layers for: {municipality_name}")
    log_info(f"Boundary: {display_path(boundary_file)}")
    log_info(f"Hard output: {display_path(hard_output_file)}")
    log_info(f"Soft output: {display_path(soft_output_file)}")
    log_info(f"Wind output: {display_path(wind_output_file)}")

    hard_layers = build_dataset_group(HARD_DATASET_DIRS, boundary, "allgemein_hart")
    hard_point_layers = build_point_group(boundary)
    soft_layers = build_dataset_group(SOFT_DATASET_DIRS, boundary, "allgemein_weich")
    wind_layers = build_dataset_group(WIND_DATASET_DIRS, boundary, "wind")

    write_group_output(
        hard_output_file,
        "naturschutz_allgemein_hart_merged",
        hard_layers,
        hard_point_layers,
    )
    write_group_output(
        soft_output_file,
        "naturschutz_allgemein_weich_merged",
        soft_layers,
    )
    write_group_output(
        wind_output_file,
        "naturschutz_wind_merged",
        wind_layers,
    )
    log_success("Protection layer processing finished.")


def main() -> None:
    """Run the municipality protection processing."""

    parser = ColoredArgumentParser(
        description="Build hard and soft protection layers for one municipality."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()
    build_protection_layers_for_municipality(args.municipality)


if __name__ == "__main__":
    main()
