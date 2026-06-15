"""
Gemeinsame Hilfsfunktionen für technologiespezifische Landnutzungs-Layer.

Die Skripte für Wind, Solar und Wasser lesen alle denselben vorbereiteten
Gemeinde-Datensatz aus script 4. Dort liegen die offiziellen ``ln_*``-Layer
bereits auf die Gemeinde zugeschnitten vor. Erst danach werden sie hier
technologiespezifisch zu Ausschluss-, Potenzial- oder Kontext-Layern
zusammengeführt.
"""

from pathlib import Path
import re
import sqlite3

import geopandas as gpd
import pandas as pd

from utils import log_error, log_info, log_success, log_warning


BASE_DIR = Path(__file__).resolve().parent.parent.parent
LANDUSE_DIR = BASE_DIR / "data/processed/landuse"
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


def safe_filename(name: str) -> str:
    """Create the same filename format as the other scripts."""

    return name.lower().replace(" ", "_")


def display_path(path: Path) -> str:
    """Return a compact path for log messages."""

    try:
        return str(path.resolve().relative_to(BASE_DIR))
    except ValueError:
        return str(path)


def landuse_input_file(municipality_name: str) -> Path:
    """Return the municipality-specific landuse GeoPackage from script 4."""

    return LANDUSE_DIR / f"landnutzung_{safe_filename(municipality_name)}.gpkg"


def list_landuse_layers(input_file: Path) -> list[str]:
    """List all expected municipality landuse layers inside the GeoPackage."""

    try:
        with sqlite3.connect(input_file) as connection:
            rows = connection.execute(
                """
                SELECT table_name
                FROM gpkg_contents
                WHERE data_type = 'features'
                ORDER BY table_name
                """
            ).fetchall()
    except sqlite3.Error:
        log_warning(
            "Layer list of the municipality landuse GeoPackage could not be read."
        )
        log_info("Falling back to the expected official landuse layer names.")
        return sorted(EXPECTED_LANDUSE_LAYERS)

    layers = [row[0] for row in rows if isinstance(row[0], str)]
    return [layer for layer in layers if layer.startswith("ln_")]


def load_official_landuse(municipality_name: str) -> gpd.GeoDataFrame:
    """Read all clipped ``ln_*`` layers and combine them in memory."""

    input_file = landuse_input_file(municipality_name)

    if not input_file.exists():
        raise FileNotFoundError(
            "Municipality landuse file not found. "
            f"Run script 4 first: {display_path(input_file)}"
        )

    layer_names = list_landuse_layers(input_file)

    if not layer_names:
        raise SystemExit(
            "No municipality landuse layers were found. "
            f"Expected clipped ln_* layers in: {display_path(input_file)}"
        )

    loaded_layers = []

    for layer_name in layer_names:
        log_info(f"Reading municipality landuse layer: {layer_name}")
        try:
            layer_data = gpd.read_file(input_file, layer=layer_name)
        except Exception:
            continue

        if layer_data.empty:
            continue

        layer_data["source_layer"] = layer_name
        loaded_layers.append(layer_data)

    if not loaded_layers:
        raise SystemExit(
            "All municipality landuse layers are empty. "
            f"Check the clipped output: {display_path(input_file)}"
        )

    return gpd.GeoDataFrame(
        pd.concat(loaded_layers, ignore_index=True),
        geometry="geometry",
        crs=loaded_layers[0].crs,
    )


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
            "The landuse output GeoPackage is still open and cannot be overwritten."
        ) from error


def filter_landuse_by_source_layers(
    landuse: gpd.GeoDataFrame,
    source_layers: set[str],
    category_name: str,
) -> gpd.GeoDataFrame:
    """Filter the combined municipality landuse by selected ``source_layer`` values."""

    filtered = landuse[landuse["source_layer"].isin(source_layers)].copy()

    if filtered.empty:
        return gpd.GeoDataFrame(
            {"source_layer": [], "landuse_category": [], "geometry": []},
            geometry="geometry",
            crs=landuse.crs,
        )

    filtered["landuse_category"] = category_name
    return filtered


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
            "The technology-specific landuse GeoPackage could not be written."
        ) from error

    if data.empty:
        log_warning(f"Written empty layer: {layer_name} (0 features)")
    else:
        log_success(f"Written {layer_name}: {len(data)} features")
