"""
Script 4: Clip official landuse data.

Workflow:
1. Read the municipality boundary created by script 2.
2. Prefer a local landuse GeoPackage if it already exists.
3. Otherwise read the official remote GeoPackage directly with a bounding-box
   filter instead of downloading all of Bavaria first.
4. Clip each polygon landuse layer exactly with the municipality boundary.
5. Write one municipality-specific GeoPackage that keeps the clipped ``ln_*``
   layers as separate layers.

Hinweis:
Das Original unter ``data/raw/landuse/landnutzung.gpkg`` bleibt unangetastet.
Dieses Skript erzeugt nur einen kleineren Arbeitsdatensatz für die jeweilige
Gemeinde, damit Wind-, Solar- und Wasser-Skripte später schneller damit
weiterarbeiten können.
"""

from pathlib import Path
import argparse
import re
import sqlite3
import sys

import geopandas as gpd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "utils"))
from utils import ColoredArgumentParser, log_error, log_info, log_success, log_warning


BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =============================================================================
# 0. Input and output paths
# =============================================================================
# input
BOUNDARY_DIR = BASE_DIR / "data/processed/1_base_boundaries"
LANDUSE_URL = "https://geodaten.bayern.de/odd/m/3/daten/ln/landnutzung.gpkg"
LANDUSE_FILE = BASE_DIR / "data/raw/landuse/landnutzung.gpkg"

# output
OUTPUT_DIR = BASE_DIR / "data/processed/1_base_landuse"

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


def display_source(vector_source: Path | str) -> str:
    """Return a compact name for a local or remote vector source."""

    if isinstance(vector_source, Path):
        return display_path(vector_source)

    return vector_source


def remote_landuse_source() -> str:
    """Return a GDAL virtual path for reading the remote GeoPackage."""

    return f"/vsicurl/{LANDUSE_URL}"


def get_landuse_source() -> Path:
    """Use only the local official landuse GeoPackage."""

    if LANDUSE_FILE.exists() and LANDUSE_FILE.stat().st_size > 0:
        log_info(f"Using local landuse source: {display_path(LANDUSE_FILE)}")
        return LANDUSE_FILE

    log_error("Local landuse GeoPackage not found.")
    log_error(f"Expected file: {display_path(LANDUSE_FILE)}")
    log_info("Download the official Bavaria landuse GeoPackage once and place it here.")
    log_info(f"Official source: {LANDUSE_URL}")
    raise SystemExit(
        "Script 4 stopped because the local official landuse GeoPackage is missing."
    )


def is_geopackage_source(vector_source: Path | str) -> bool:
    """Check whether the source points to a GeoPackage."""

    return str(vector_source).lower().endswith(".gpkg")


def list_layers(vector_source: Path | str) -> list[str | None]:
    """List layers of a local GeoPackage via SQLite metadata."""

    if not is_geopackage_source(vector_source):
        return [None]

    if not isinstance(vector_source, Path):
        log_warning(f"Layer metadata could not be inspected: {display_source(vector_source)}")
        log_info("Falling back to the expected official landuse layer names.")
        return sorted(EXPECTED_LANDUSE_LAYERS)

    try:
        with sqlite3.connect(vector_source) as connection:
            rows = connection.execute(
                """
                SELECT table_name
                FROM gpkg_contents
                WHERE data_type = 'features'
                ORDER BY table_name
                """
            ).fetchall()
    except sqlite3.Error:
        log_warning(f"Layer metadata could not be read: {display_source(vector_source)}")
        log_info("Falling back to the expected official landuse layer names.")
        return sorted(EXPECTED_LANDUSE_LAYERS)

    layers = [row[0] for row in rows if isinstance(row[0], str)]

    if not layers:
        log_warning(f"No feature layers found in: {display_source(vector_source)}")
        log_info("Falling back to the expected official landuse layer names.")
        return sorted(EXPECTED_LANDUSE_LAYERS)

    return layers


def layer_matches_expected_name(layer_name: str) -> bool:
    """Check whether a layer name contains one of the expected ln_* names."""

    return any(expected in layer_name for expected in EXPECTED_LANDUSE_LAYERS)


def normalize_source_layer_name(layer_name: str) -> str:
    """Extract the canonical ln_* name from the actual layer name."""

    for expected in sorted(EXPECTED_LANDUSE_LAYERS):
        if expected in layer_name:
            return expected

    return layer_name


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
    vector_source: Path | str,
    layer: str | None,
    bbox: tuple[float, float, float, float] | None = None,
) -> gpd.GeoDataFrame:
    """Read one vector layer, optionally limited to a bounding box."""

    if layer is None:
        return gpd.read_file(vector_source, bbox=bbox)

    return gpd.read_file(vector_source, layer=layer, bbox=bbox)


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
            "Script 4 stopped because an output GeoPackage is still open."
        ) from error


# =============================================================================
# 2. Read and clip municipality landuse layers
# =============================================================================
def clip_landuse_layers_from_source(
    boundary: gpd.GeoDataFrame,
    landuse_source: Path,
) -> dict[str, gpd.GeoDataFrame]:
    """Read and clip all official polygon landuse layers from one source."""

    boundary_25832 = boundary.to_crs(epsg=25832)
    landuse_bbox = tuple(boundary_25832.total_bounds)
    clipped_layers: dict[str, gpd.GeoDataFrame] = {}
    available_layers = list_layers(landuse_source)
    official_landuse_layers = [
        layer
        for layer in available_layers
        if layer is not None and layer_matches_expected_name(layer)
    ]

    log_warning(
        "Official landuse source contains "
        f"{len(official_landuse_layers)} matching ln_* layers."
    )

    for layer in available_layers:
        if layer is None:
            continue

        source_name = normalize_source_layer_name(layer)

        if not layer_matches_expected_name(layer):
            log_warning(f"Skipping non-landuse layer: {layer}")
            continue

        log_info(f"Reading landuse layer: {layer}")

        try:
            data = read_vector_layer(landuse_source, layer, bbox=landuse_bbox)
        except Exception:
            log_warning(f"Skipping unreadable layer: {layer}")
            continue

        if data.empty or data.geometry.is_empty.all():
            continue

        data = data[data.geometry.notna()]
        geometry_types = set(data.geometry.geom_type.dropna().unique())

        if not geometry_types.intersection({"Polygon", "MultiPolygon"}):
            log_warning(f"Skipping non-polygon layer: {source_name}")
            continue

        data = data[data.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]
        data = data.to_crs(epsg=25832)

        # Der harte Zuschnitt passiert erst nach dem Bounding-Box-Vorfilter.
        clipped = gpd.clip(data, boundary_25832, keep_geom_type=True)

        if clipped.empty:
            continue

        clipped = clipped[clipped.geometry.geom_type.isin(["Polygon", "MultiPolygon"])]

        if clipped.empty:
            continue

        clipped_layers[source_name] = clipped

    return clipped_layers


def clip_landuse_layers(boundary: gpd.GeoDataFrame) -> dict[str, gpd.GeoDataFrame]:
    """Read and clip all official polygon landuse layers for one municipality."""

    landuse_source = get_landuse_source()
    return clip_landuse_layers_from_source(boundary, landuse_source)


# =============================================================================
# 3. Write the municipality landuse GeoPackage
# =============================================================================
def write_layer(output_file: Path, layer_name: str, data: gpd.GeoDataFrame) -> None:
    """Write one non-empty GeoPackage layer."""

    if data.empty:
        log_warning(f"No features for layer: {layer_name}")
        return

    data = clean_for_geopackage(data)

    try:
        data.to_file(output_file, layer=layer_name, driver="GPKG")
    except Exception as error:
        log_error(f"Could not write layer: {layer_name}")
        log_error(f"Output file: {display_path(output_file)}")
        log_info("Close the file in QGIS or remove the layer from the QGIS project.")
        log_info("Then run the script again.")
        raise SystemExit(
            "Script 4 stopped because the GeoPackage could not be written."
        ) from error

    log_success(f"Written {layer_name}: {len(data)} features")


def write_landuse_layers(
    output_file: Path,
    clipped_layers: dict[str, gpd.GeoDataFrame],
) -> None:
    """Write all municipality landuse layers into one GeoPackage."""

    if not clipped_layers:
        raise SystemExit(
            "Script 4 stopped because no matching polygon landuse layers were found."
        )

    missing_layers = sorted(EXPECTED_LANDUSE_LAYERS - set(clipped_layers.keys()))
    written_layers = 0

    for layer_name, data in clipped_layers.items():
        write_layer(output_file, layer_name, data)
        written_layers += 1

    if missing_layers:
        for layer_name in missing_layers:
            log_warning(f"Skipped {layer_name}: 0 features")

        log_warning(
            f"{len(missing_layers)} official ln_* layers had no clipped features for this municipality."
        )

    log_success(f"Municipality landuse GeoPackage written with {written_layers} layers.")


# =============================================================================
# 4. Run landuse processing for one municipality
# =============================================================================
def clip_landuse_for_municipality(municipality_name: str) -> None:
    """Clip official landuse data for one municipality."""

    safe_name = safe_filename(municipality_name)
    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    output_file = OUTPUT_DIR / f"landnutzung_{safe_name}.gpkg"

    if not boundary_file.exists():
        raise FileNotFoundError(
            f"Boundary file not found: {boundary_file}. Run script 2 first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(output_file)

    boundary = gpd.read_file(boundary_file).to_crs(epsg=25832)

    log_info(f"Clipping official landuse for: {municipality_name}")
    log_info(f"Boundary: {display_path(boundary_file)}")
    log_info(f"Output: {display_path(output_file)}")
    log_info("Reading landuse with municipality bounding-box filter.")
    log_info("Then clipping each layer exactly with the municipality boundary.")

    clipped_layers = clip_landuse_layers(boundary)
    write_landuse_layers(output_file, clipped_layers)

    log_success("Official landuse clipping finished.")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = ColoredArgumentParser(
        description="Clip official landuse data to one municipality."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    return parser.parse_args()


def main() -> None:
    """Run the landuse clipping for one municipality."""

    args = parse_arguments()
    clip_landuse_for_municipality(args.municipality)


if __name__ == "__main__":
    main()
