"""
Script 6: Test export only the map from the QGIS project.

Workflow:
1. Open the QGIS project created by script 4.
2. Create one A4 landscape print layout.
3. Add only one map item.
4. Export the layout as PDF.
"""

from pathlib import Path
import argparse
import sys

from qgis.core import (
    QgsApplication,
    QgsLayerTreeLayer,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsLayoutItemMap,
    QgsLayoutItemPage,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsPrintLayout,
    QgsProject,
    QgsUnitTypes,
    QgsVectorLayer,
)
from qgis.PyQt.QtGui import QFont


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "scripts/utils"))

from utils import ColoredArgumentParser, log_success


# -----------------------------------------------------------------------------
# 0. Configuration: input and output paths
# -----------------------------------------------------------------------------
PROJECT_DIR = BASE_DIR / "data/processed/qgis_projects"
OUTPUT_DIR = BASE_DIR / "data/processed/maps"


# -----------------------------------------------------------------------------
# Helper functions
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


def find_boundary_layer(
    project: QgsProject,
    municipality_name: str,
) -> QgsVectorLayer:
    """Find the municipality boundary layer in the QGIS project."""
    matching_layers = project.mapLayersByName(municipality_name)

    if not matching_layers:
        raise RuntimeError(f"Boundary layer not found in project: {municipality_name}")

    layer = matching_layers[0]

    if not isinstance(layer, QgsVectorLayer):
        raise RuntimeError(f"Boundary layer is not a vector layer: {municipality_name}")

    return layer


def ordered_project_layers(project: QgsProject) -> list:
    """Return project layers in the same order as the layer tree."""
    layers = []
    root = project.layerTreeRoot()

    for node in root.findLayers():
        if isinstance(node, QgsLayerTreeLayer):
            layer = node.layer()

            if layer is not None:
                layers.append(layer)

    return layers


def add_label(
    layout: QgsPrintLayout,
    text: str,
    x: float,
    y: float,
    font_size: int = 12,
    bold: bool = False,
) -> QgsLayoutItemLabel:
    """Add one text label to the layout."""
    label = QgsLayoutItemLabel(layout)
    label.setText(text)

    font = QFont("Arial", font_size)
    font.setBold(bold)
    label.setFont(font)

    layout.addLayoutItem(label)
    label.adjustSizeToText()
    label.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))

    return label


# -----------------------------------------------------------------------------
# 1. Create test PDF layout
# -----------------------------------------------------------------------------
def create_test_layout(
    project: QgsProject,
    municipality_name: str,
) -> QgsPrintLayout:
    """Create a simple A4 landscape map-only layout."""

    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(f"{municipality_name} Test Map Only")

    layout.pageCollection().page(0).setPageSize(
        "A4",
        QgsLayoutItemPage.Landscape,
    )

    boundary_layer = find_boundary_layer(project, municipality_name)
    main_extent = boundary_layer.extent()
    main_extent.scale(1.35)

    add_label(
        layout,
        f"Testkarte: {municipality_name}",
        16,
        10,
        14,
        True,
    )

    # Change only these four values while testing the map position and size.
    map_x = 16
    map_y = 24
    map_width = 210
    map_height = 80

    map_item = QgsLayoutItemMap(layout)
    map_item.setLayers(ordered_project_layers(project))

    # Set map item position and size before adding it to the layout.
    map_item.attemptMove(
        QgsLayoutPoint(map_x, map_y, QgsUnitTypes.LayoutMillimeters)
    )

    map_item.attemptResize(
        QgsLayoutSize(map_width, map_height, QgsUnitTypes.LayoutMillimeters)
    )

    # Use zoomToExtent instead of setExtent.
    map_item.zoomToExtent(main_extent)

    map_item.setFrameEnabled(True)

    # Add the configured map item to the layout at the end.
    layout.addLayoutItem(map_item)

    map_item.refresh()

    return layout


# -----------------------------------------------------------------------------
# 2. Export test PDF
# -----------------------------------------------------------------------------
def generate_test_map_pdf(municipality_name: str) -> None:
    """Open the QGIS project and export only the map as a PDF."""

    safe_name = safe_filename(municipality_name)

    project_file = PROJECT_DIR / f"{safe_name}_map.qgz"
    output_file = OUTPUT_DIR / f"{safe_name}_test_map_only.pdf"

    require_file(project_file, "QGIS project not found. Run script 4 first")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    project = QgsProject.instance()
    project.clear()

    if not project.read(str(project_file)):
        raise RuntimeError(f"QGIS project could not be opened: {display_path(project_file)}")

    layout = create_test_layout(project, municipality_name)

    exporter = QgsLayoutExporter(layout)
    settings = QgsLayoutExporter.PdfExportSettings()

    result = exporter.exportToPdf(str(output_file), settings)

    if result != QgsLayoutExporter.Success:
        raise RuntimeError("PDF export failed.")

    log_success(f"Test map PDF created: {display_path(output_file)}")


def main() -> None:
    parser = ColoredArgumentParser(
        description="Generate a test PDF with only the map."
    )

    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()
    generate_test_map_pdf(args.municipality)


if __name__ == "__main__":
    qgs = QgsApplication([], False)
    qgs.initQgis()

    try:
        main()
    finally:
        qgs.exitQgis()