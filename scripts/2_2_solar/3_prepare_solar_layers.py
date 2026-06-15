"""
Script 3: Prepare solar buffer layers.

Workflow:
1. Read the municipality boundary from script 2.
2. Read the OSM motorway and railway layers from prepare-data script 5.
3. Build one broad 500 m EEG transport basis.
4. Build one stricter 200 m BauGB transport basis.
5. Clip both buffer layers exactly to the municipality.
6. Write one clean GeoPackage without unnecessary raw buffer layers.
"""

from pathlib import Path
import re
import sys

import geopandas as gpd
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent / "utils"))
from utils import ColoredArgumentParser, log_error, log_info, log_success, log_warning


BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =============================================================================
# 0. Input and output paths
# =============================================================================
BOUNDARY_DIR = BASE_DIR / "data/processed/boundaries"
OSM_DIR = BASE_DIR / "data/processed/osm_transport"
OUTPUT_DIR = BASE_DIR / "data/processed/solar"


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


def motorway_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for motorways."""

    return f"osm_autobahnen_{safe_filename(municipality_name)}"


def railway_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for railways."""

    return f"osm_schienenwege_{safe_filename(municipality_name)}"


def eeg_transport_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for the 500 m transport basis."""

    return f"pv_verkehrsachsen_500m_{safe_filename(municipality_name)}"


def baugb_transport_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for the 200 m transport basis."""

    return f"pv_verkehrsachsen_200m_{safe_filename(municipality_name)}"


def eeg_buffer_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for the 500 m EEG buffer."""

    return f"pv_förderkulisse_500m_{safe_filename(municipality_name)}"


def baugb_buffer_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for the 200 m BauGB buffer."""

    return f"pv_privilegierung_200m_{safe_filename(municipality_name)}"


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


def empty_polygon_gdf(crs: str = "EPSG:25832") -> gpd.GeoDataFrame:
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
            "Solar script 3 stopped because the output GeoPackage is still open."
        ) from error


def read_layer(vector_file: Path, layer_name: str) -> gpd.GeoDataFrame:
    """Read one layer from a GeoPackage."""

    return gpd.read_file(vector_file, layer=layer_name)


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
            "Solar script 3 stopped because the GeoPackage could not be written."
        ) from error

    if data.empty:
        log_warning(f"Written empty layer: {layer_name} (0 features)")
    else:
        log_success(f"Written {layer_name}: {len(data)} features")


def merge_transport_layers(
    motorways: gpd.GeoDataFrame,
    railways: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Merge motorway and railway lines into one transport axis dataset."""

    layers = []

    if not motorways.empty:
        layers.append(motorways.copy())

    if not railways.empty:
        layers.append(railways.copy())

    if not layers:
        return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:25832")

    return gpd.GeoDataFrame(
        pd.concat(layers, ignore_index=True),
        geometry="geometry",
        crs="EPSG:25832",
    )


def to_int_series(data: gpd.GeoDataFrame, column_name: str) -> pd.Series:
    """Convert one optional text column to integers where possible."""

    if column_name not in data.columns:
        return pd.Series(pd.NA, index=data.index, dtype="Int64")

    numeric_values = pd.to_numeric(data[column_name], errors="coerce")
    return numeric_values.astype("Int64")


def filter_baugb_relevant_railways(railways: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Keep only railways that match the simplified BauGB approximation."""

    if railways.empty:
        return railways

    tracks = to_int_series(railways, "tracks")

    # Vereinfachte BauGB-Näherung:
    # Es bleiben nur railway=rail-Features mit explizitem tracks>=2 erhalten.
    railway_mask = tracks.ge(2).fillna(False)
    filtered = railways[railway_mask].copy()

    if filtered.empty:
        log_warning(
            "No railways matched the BauGB railway filter with tracks>=2. "
            "The 200 m buffer may then be based on motorways only."
        )

    return filtered


def build_buffer_layer(
    transport_axes: gpd.GeoDataFrame,
    distance_meters: int,
    layer_label: str,
) -> gpd.GeoDataFrame:
    """Create one dissolved buffer layer from merged transport axes."""

    if transport_axes.empty:
        log_warning(f"No transport axes available for: {layer_label}")
        return empty_polygon_gdf()

    dissolved_axes = transport_axes[["geometry"]].dissolve()
    buffered = dissolved_axes.buffer(distance_meters)

    return gpd.GeoDataFrame(
        {"distance_m": [distance_meters]},
        geometry=buffered,
        crs="EPSG:25832",
    )


def clip_buffer_to_boundary(
    buffer_layer: gpd.GeoDataFrame,
    boundary_for_clip: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """Clip one buffer layer exactly to the municipality boundary."""

    if buffer_layer.empty:
        return empty_polygon_gdf()

    clipped = gpd.clip(buffer_layer, boundary_for_clip)

    if clipped.empty:
        return empty_polygon_gdf()

    return clipped


# =============================================================================
# 1. Prepare solar transport and buffer layers for one municipality
# =============================================================================
def prepare_solar_layers(municipality_name: str) -> None:
    """Prepare the OSM-based solar transport and buffer layers."""

    safe_name = safe_filename(municipality_name)
    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    osm_file = OSM_DIR / f"{safe_name}_osm_transport.gpkg"
    output_file = OUTPUT_DIR / f"{safe_name}_solar_layers.gpkg"

    if not boundary_file.exists():
        raise FileNotFoundError(
            f"Boundary file not found: {boundary_file}. Run script 2 first."
        )

    if not osm_file.exists():
        raise FileNotFoundError(
            f"OSM transport file not found: {osm_file}. Run prepare-data script 5 first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(output_file)

    boundary = gpd.read_file(boundary_file).to_crs(epsg=25832)
    boundary_for_clip = boundary[["geometry"]].dissolve()

    log_info(f"Preparing solar layers for: {municipality_name}")
    log_info(f"Boundary: {display_path(boundary_file)}")
    log_info(f"OSM transport input: {display_path(osm_file)}")
    log_info(f"Output: {display_path(output_file)}")

    motorways = read_layer(
        osm_file,
        motorway_layer_name(municipality_name),
    ).to_crs(epsg=25832)
    railways = read_layer(
        osm_file,
        railway_layer_name(municipality_name),
    ).to_crs(epsg=25832)

    # EEG 500 m:
    # Breiter Suchraum entlang von Autobahnen und Schienenwegen.
    eeg_transport_axes = merge_transport_layers(motorways, railways)

    # BauGB 200 m:
    # Strengere Schienen-Auswahl nur mit tracks>=2.
    baugb_railways = filter_baugb_relevant_railways(railways)
    baugb_transport_axes = merge_transport_layers(motorways, baugb_railways)

    eeg_buffer = build_buffer_layer(
        eeg_transport_axes,
        500,
        "PV-Förderkulisse 500 m",
    )
    eeg_buffer["legal_basis"] = "EEG 2023 Paragraf 37 Abs. 1 Nr. 2 Buchstabe c"
    eeg_buffer["method_note"] = (
        "OSM-Näherung aus motorway, motorway_link und railway=rail."
    )
    eeg_buffer = clip_buffer_to_boundary(eeg_buffer, boundary_for_clip)
    if not eeg_buffer.empty:
        eeg_buffer["legal_basis"] = "EEG 2023 Paragraf 37 Abs. 1 Nr. 2 Buchstabe c"
        eeg_buffer["method_note"] = (
            "OSM-Näherung aus motorway, motorway_link und railway=rail."
        )

    baugb_buffer = build_buffer_layer(
        baugb_transport_axes,
        200,
        "PV-Privilegierung 200 m",
    )
    baugb_buffer["legal_basis"] = "BauGB Paragraf 35 Abs. 1 Nr. 8 Buchstabe b"
    baugb_buffer["method_note"] = (
        "OSM-Näherung aus motorway, motorway_link und railway=rail mit tracks>=2."
    )
    baugb_buffer = clip_buffer_to_boundary(baugb_buffer, boundary_for_clip)
    if not baugb_buffer.empty:
        baugb_buffer["legal_basis"] = "BauGB Paragraf 35 Abs. 1 Nr. 8 Buchstabe b"
        baugb_buffer["method_note"] = (
            "OSM-Näherung aus motorway, motorway_link und railway=rail mit tracks>=2."
        )

    write_layer(output_file, motorway_layer_name(municipality_name), motorways)
    write_layer(output_file, railway_layer_name(municipality_name), railways)
    write_layer(output_file, eeg_transport_layer_name(municipality_name), eeg_transport_axes)
    write_layer(output_file, baugb_transport_layer_name(municipality_name), baugb_transport_axes)
    write_layer(output_file, eeg_buffer_layer_name(municipality_name), eeg_buffer)
    write_layer(output_file, baugb_buffer_layer_name(municipality_name), baugb_buffer)

    log_success("Solar layer preparation finished.")


def main() -> None:
    """Run the solar layer preparation for one municipality."""

    parser = ColoredArgumentParser(
        description="Prepare solar motorway, railway and buffer layers for one municipality."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()
    prepare_solar_layers(args.municipality)


if __name__ == "__main__":
    main()
