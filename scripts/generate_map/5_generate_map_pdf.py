"""
Script 5: Generate a map PDF from the QGIS project.

Workflow:
1. Open the QGIS project created by script 4.
2. Create one A4 landscape print layout.
3. Add one map, a compact information panel and a scale bar.
4. Export the layout as PDF.
"""

from pathlib import Path
import argparse
import textwrap
import sys
from datetime import date

# PyQGIS imports. Main references: Python apps, projects, layouts and PDF export.
# (Docs: 1.4, 3.3, 10)
from qgis.core import (
    QgsApplication,
    QgsFillSymbol,
    QgsLayerTreeLayer,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsLayoutItemMap,
    QgsLayoutItemPage,
    QgsLayoutItemScaleBar,
    QgsLayoutItemShape,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsPrintLayout,
    QgsProject,
    QgsUnitTypes,
    QgsVectorLayer,
)
from qgis.PyQt.QtGui import QColor, QFont


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "scripts/utils"))

from utils import ColoredArgumentParser, log_error, log_info, log_success


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


def remove_existing_output(output_file: Path) -> None:
    """Remove an old PDF before writing a fresh export."""

    if not output_file.exists():
        return

    try:
        output_file.unlink()
    except PermissionError as error:
        # Stop with a clear message if the PDF is still open in a PDF viewer.
        log_error("Output PDF is locked and cannot be overwritten.")
        log_error(f"Locked file: {display_path(output_file)}")
        log_info("Close the PDF viewer and run the script again.")
        raise SystemExit(
            "Script 5 stopped because the output PDF is still open. "
            f"Close it first: {display_path(output_file)}"
        ) from error


# -----------------------------------------------------------------------------
# 1. Create map layout helpers
# -----------------------------------------------------------------------------
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
    font_size: int = 9,
    bold: bool = False,
    width: float | None = None,
    height: float | None = None,
) -> QgsLayoutItemLabel:
    """Add one text label to the layout."""

    label = QgsLayoutItemLabel(layout)
    label.setText(text)
    font = QFont("Arial", font_size)
    font.setBold(bold)
    label.setFont(font)
    label.adjustSizeToText()
    layout.addLayoutItem(label)
    label.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))

    if width is not None and height is not None:
        label.attemptResize(QgsLayoutSize(width, height, QgsUnitTypes.LayoutMillimeters))

    return label


def add_box(
    layout: QgsPrintLayout,
    x: float,
    y: float,
    width: float,
    height: float,
    color: str,
    outline_color: str = "80,80,80,255",
) -> QgsLayoutItemShape:
    """Add a simple colored rectangle to the layout."""

    box = QgsLayoutItemShape(layout)
    box.setShapeType(QgsLayoutItemShape.Rectangle)
    box.setSymbol(
        QgsFillSymbol.createSimple(
            {
                "color": color,
                "outline_color": outline_color,
                "outline_width": "0.2",
            }
        )
    )
    layout.addLayoutItem(box)
    box.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    box.attemptResize(QgsLayoutSize(width, height, QgsUnitTypes.LayoutMillimeters))
    return box


def add_legend_row(
    layout: QgsPrintLayout,
    x: float,
    y: float,
    color: str,
    label: str,
) -> None:
    """Add one compact legend row to the information panel."""

    add_box(layout, x, y + 1.2, 7, 2.2, color, color)
    add_label(layout, label, x + 10, y, 8)


def technology_label(technology: str) -> str:
    """Return the German display name for one energy technology."""

    labels = {
        "wind": "Windkraftanlagen",
        "solar": "Solaranlagen",
        "wasser": "Wasserkraftanlagen",
    }
    return labels[technology]


def placeholder_text(line_width: int = 64) -> str:
    """Return placeholder text for the map description and sources."""

    text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed eiusmod "
        "tempor incidunt ut labore et dolore magna aliqua. Ut enim ad minim "
        "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquid ex "
        "ea commodi consequat. Quis aute iure reprehenderit in voluptate velit "
        "esse cillum dolore eu fugiat nulla pariatur. Excepteur sint obcaecat "
        "cupiditat non proident, sunt in culpa qui officia deserunt mollit "
        "anim id est laborum."
    )
    return textwrap.fill(text, width=line_width)


def add_map_grid(map_item: QgsLayoutItemMap) -> None:
    """Add a light coordinate grid to the map frame."""

    grid = map_item.grid()
    grid.setEnabled(True)
    grid.setIntervalX(1000)
    grid.setIntervalY(1000)
    grid.setGridLineColor(QColor(80, 80, 80, 120))
    grid.setGridLineWidth(0.15)
    grid.setAnnotationEnabled(False)
    grid.setAnnotationPrecision(0)
    grid.setAnnotationFont(QFont("Arial", 6))


# -----------------------------------------------------------------------------
# 2. Create the PDF layout
# -----------------------------------------------------------------------------
def create_pdf_layout(
    project: QgsProject,
    municipality_name: str,
    technology: str,
) -> QgsPrintLayout:
    """Create a print layout similar to a manual QGIS map sheet."""

    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(f"{municipality_name} Map PDF")
    layout.pageCollection().page(0).setPageSize(
        "A4",
        QgsLayoutItemPage.Landscape,
    )

    boundary_layer = find_boundary_layer(project, municipality_name)
    main_extent = boundary_layer.extent()
    main_extent.scale(1.02)

    add_label(
        layout,
        f"Potenzielle Standorte für {technology_label(technology)} in {municipality_name}",
        20,
        10,
        13,
        True,
        210,
        8,
    )

    # Main map on the left, following the layout style of a QGIS print map.
    map_item = QgsLayoutItemMap(layout)
    map_item.setLayers(ordered_project_layers(project))
    layout.addLayoutItem(map_item)
    map_item.attemptMove(QgsLayoutPoint(16, 24, QgsUnitTypes.LayoutMillimeters))
    map_item.attemptResize(QgsLayoutSize(208, 158, QgsUnitTypes.LayoutMillimeters))
    map_item.setExtent(main_extent)
    map_item.setFrameEnabled(True)
    add_map_grid(map_item)

    # Right-side description block.
    add_label(
        layout,
        placeholder_text(32),
        236,
        24,
        8,
        False,
        48,
        42,
    )

    # Legend block on the right.
    add_box(layout, 236, 68, 48, 74, "255,255,255,235")
    add_label(layout, "Legende", 239, 72, 12, True)
    add_label(layout, "Standortinformationen", 239, 85, 9, True)
    add_legend_row(layout, 239, 95, "255,0,0,255", "Gemeindegrenze")
    add_legend_row(layout, 239, 105, "90,118,145,255", "Landnutzung")
    add_legend_row(layout, 239, 115, "255,170,0,255", "OSM-Straßen")
    add_label(layout, "Gitternetz", 239, 127, 9, True)
    add_legend_row(layout, 239, 136, "80,80,80,120", "Abstand: 1.000 m")

    # North arrow placeholder and scale bar.
    add_label(layout, "N\n▲", 247, 146, 18, True)

    scale_bar = QgsLayoutItemScaleBar(layout)
    scale_bar.setStyle("Single Box")
    scale_bar.setLinkedMap(map_item)
    scale_bar.applyDefaultSize()
    layout.addLayoutItem(scale_bar)
    scale_bar.attemptMove(QgsLayoutPoint(236, 166, QgsUnitTypes.LayoutMillimeters))

    # Footer with sources and metadata.
    add_label(layout, "Datenquellen", 16, 185, 7, True)
    add_label(layout, placeholder_text(145), 16, 190, 5, False, 208, 10)
    add_label(
        layout,
        f"Koordinatensystem: EPSG:25832 | Erstellt am: {date.today().isoformat()}",
        236,
        185,
        7,
    )

    return layout


# -----------------------------------------------------------------------------
# 3. Export QGIS project as PDF
# -----------------------------------------------------------------------------
def generate_map_pdf(municipality_name: str, technology: str) -> None:
    """Open the QGIS project and export a simple PDF map."""

    safe_name = safe_filename(municipality_name)

    project_file = PROJECT_DIR / f"{safe_name}_map.qgz"
    output_file = OUTPUT_DIR / f"{safe_name}_map.pdf"

    require_file(project_file, "QGIS project not found. Run script 4 first")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(output_file)

    project = QgsProject.instance()
    project.clear()

    if not project.read(str(project_file)):
        raise RuntimeError(f"QGIS project could not be opened: {display_path(project_file)}")

    layout = create_pdf_layout(project, municipality_name, technology)
    exporter = QgsLayoutExporter(layout)
    settings = QgsLayoutExporter.PdfExportSettings()

    result = exporter.exportToPdf(str(output_file), settings)

    if result != QgsLayoutExporter.Success:
        raise RuntimeError(
            "PDF export failed. Close the existing PDF if it is open and try again."
        )

    log_success(f"QGIS map PDF created: {display_path(output_file)}")


def main() -> None:
    parser = ColoredArgumentParser(
        description="Generate a simple PDF map from the QGIS project."
    )

    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )
    parser.add_argument(
        "--technology",
        required=True,
        choices=["wind", "solar", "wasser"],
        help="Energy technology used for the map title.",
    )

    args = parser.parse_args()
    generate_map_pdf(args.municipality, args.technology)


if __name__ == "__main__":
    # QgsApplication is required when PyQGIS is used outside the QGIS GUI. (Doc: 1.4)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    try:
        main()
    finally:
        qgs.exitQgis()
