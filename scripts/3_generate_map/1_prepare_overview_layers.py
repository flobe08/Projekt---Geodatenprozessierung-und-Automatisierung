"""
Script 1: Prepare overview map layers.

Workflow:
1. Read the official Bavarian administrative boundary dataset.
2. Create a simplified Bavaria outline once and reuse it for all maps.
3. Read the selected municipality boundary.
4. Create municipality locator layers for the PDF overview map.
5. Write all overview layers to GeoPackage files.
"""

from pathlib import Path
import argparse
import sys

from qgis.core import (
    QgsApplication,
    QgsFeature,
    QgsGeometry,
    QgsVectorFileWriter,
    QgsVectorLayer,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "scripts/utils"))

from utils import ColoredArgumentParser, log_info, log_success, log_warning


# -----------------------------------------------------------------------------
# 0. Input and output paths
# -----------------------------------------------------------------------------
# input
ADMIN_BOUNDARY_FILE = (
    BASE_DIR
    / "data/raw/Verwaltungsgebiet_Bayern/ALKIS-Vereinfacht/VerwaltungsEinheit.shp"
)
BOUNDARY_DIR = BASE_DIR / "data/processed/1_base_boundaries"

# output
OUTPUT_DIR = BASE_DIR / "data/processed/1_base_overview"
BAVARIA_OUTLINE_FILE = OUTPUT_DIR / "bayern_outline.gpkg"


# -----------------------------------------------------------------------------
# 1. Helper functions
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


def require_file(path: Path, message: str) -> None:
    """Stop if an expected input file is missing."""

    if not path.exists():
        raise FileNotFoundError(f"{message}: {display_path(path)}")


def write_layer(layer: QgsVectorLayer, output_file: Path, layer_name: str) -> None:
    """Write one memory layer to a GeoPackage layer."""

    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "GPKG"
    options.layerName = layer_name
    options.fileEncoding = "UTF-8"

    if output_file.exists():
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
    else:
        options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile

    writer_result = QgsVectorFileWriter.writeAsVectorFormatV3(
        layer,
        str(output_file),
        layer.transformContext(),
        options,
    )
    result = writer_result[0]
    error_message = writer_result[1] if len(writer_result) > 1 else ""

    if result != QgsVectorFileWriter.NoError:
        raise RuntimeError(
            f"Could not write layer {layer_name} to {display_path(output_file)}: "
            f"{error_message}"
        )


def memory_layer(geometry_type: str, crs_authid: str, layer_name: str) -> QgsVectorLayer:
    """Create one empty memory layer."""

    layer = QgsVectorLayer(f"{geometry_type}?crs={crs_authid}", layer_name, "memory")

    if not layer.isValid():
        raise RuntimeError(f"Could not create memory layer: {layer_name}")

    return layer


def add_geometry(layer: QgsVectorLayer, geometry: QgsGeometry) -> None:
    """Add one geometry feature to a memory layer."""

    feature = QgsFeature(layer.fields())
    feature.setGeometry(geometry)
    layer.dataProvider().addFeatures([feature])
    layer.updateExtents()


def dissolve_layer(layer: QgsVectorLayer) -> QgsGeometry | None:
    """Dissolve all features of one vector layer into one geometry."""

    geometries = [
        feature.geometry()
        for feature in layer.getFeatures()
        if feature.geometry() is not None and not feature.geometry().isEmpty()
    ]

    if not geometries:
        return None

    return QgsGeometry.unaryUnion(geometries)


def overview_file_name(municipality_name: str) -> str:
    """Create the municipality-specific overview GeoPackage file name."""

    return f"{safe_filename(municipality_name)}_overview.gpkg"


# -----------------------------------------------------------------------------
# 2. Build Bavaria outline
# -----------------------------------------------------------------------------
def build_bavaria_outline() -> None:
    """Create the simplified Bavaria outline if it does not already exist."""

    if BAVARIA_OUTLINE_FILE.exists():
        log_info(
            f"Bavaria outline already exists, step skipped: "
            f"{display_path(BAVARIA_OUTLINE_FILE)}"
        )
        return

    require_file(ADMIN_BOUNDARY_FILE, "Administrative boundary dataset not found")

    log_info("Creating Bavaria outline from administrative boundaries.")
    log_info("This is done once and then reused for later PDF exports.")

    admin_layer = QgsVectorLayer(
        str(ADMIN_BOUNDARY_FILE),
        "Bayern Verwaltungsgrenzen",
        "ogr",
    )

    if not admin_layer.isValid():
        raise RuntimeError(
            f"Administrative boundary layer is invalid: {display_path(ADMIN_BOUNDARY_FILE)}"
        )

    bavaria_geometry = dissolve_layer(admin_layer)

    if bavaria_geometry is None or bavaria_geometry.isEmpty():
        raise RuntimeError("Bavaria outline could not be created.")

    # The locator map is small. Simplification keeps the PDF compact while the
    # outline remains clearly recognizable at Bavaria scale.
    simplified_geometry = bavaria_geometry.simplify(250)

    if simplified_geometry is not None and not simplified_geometry.isEmpty():
        bavaria_geometry = simplified_geometry

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    bavaria_layer = memory_layer(
        "MultiPolygon",
        admin_layer.crs().authid(),
        "bayern_outline",
    )
    add_geometry(bavaria_layer, bavaria_geometry)
    write_layer(bavaria_layer, BAVARIA_OUTLINE_FILE, "bayern_outline")

    log_success(f"Bavaria outline written: {display_path(BAVARIA_OUTLINE_FILE)}")


# -----------------------------------------------------------------------------
# 3. Build municipality locator layers
# -----------------------------------------------------------------------------
def build_municipality_overview(municipality_name: str) -> None:
    """Create locator layers for one selected municipality."""

    safe_name = safe_filename(municipality_name)
    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    output_file = OUTPUT_DIR / overview_file_name(municipality_name)

    require_file(boundary_file, "Municipality boundary not found")

    boundary_layer = QgsVectorLayer(
        f"{boundary_file}|layername={safe_name}_boundary",
        f"{municipality_name} Boundary",
        "ogr",
    )

    if not boundary_layer.isValid():
        # Some older outputs use the default GeoPackage layer name.
        boundary_layer = QgsVectorLayer(str(boundary_file), f"{municipality_name} Boundary", "ogr")

    if not boundary_layer.isValid():
        raise RuntimeError(f"Boundary layer is invalid: {display_path(boundary_file)}")

    municipality_geometry = dissolve_layer(boundary_layer)

    if municipality_geometry is None or municipality_geometry.isEmpty():
        raise RuntimeError(f"Municipality geometry is empty: {municipality_name}")

    crs_authid = boundary_layer.crs().authid()
    municipality_layer = memory_layer(
        "MultiPolygon",
        crs_authid,
        "overview_municipality",
    )
    marker_layer = memory_layer("Point", crs_authid, "overview_marker")
    locator_window_layer = memory_layer("Polygon", crs_authid, "overview_search_window")

    municipality_extent = municipality_geometry.boundingBox()
    locator_extent = municipality_extent
    locator_extent.scale(12.0)

    add_geometry(municipality_layer, municipality_geometry)
    add_geometry(marker_layer, municipality_geometry.pointOnSurface())
    add_geometry(locator_window_layer, QgsGeometry.fromRect(locator_extent))

    if output_file.exists():
        output_file.unlink()

    write_layer(municipality_layer, output_file, "overview_municipality")
    write_layer(marker_layer, output_file, "overview_marker")
    write_layer(locator_window_layer, output_file, "overview_search_window")

    log_success(f"Municipality overview layers written: {display_path(output_file)}")


# -----------------------------------------------------------------------------
# 4. Main entry point
# -----------------------------------------------------------------------------
def parse_arguments() -> argparse.Namespace:
    """Read command line arguments."""

    parser = ColoredArgumentParser(
        description="Prepare overview layers for the PDF locator map."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    return parser.parse_args()


def main() -> None:
    """Prepare all locator-map input layers."""

    args = parse_arguments()
    build_bavaria_outline()
    build_municipality_overview(args.municipality)


if __name__ == "__main__":
    qgs = QgsApplication([], False)
    qgs.initQgis()

    try:
        main()
    finally:
        qgs.exitQgis()
