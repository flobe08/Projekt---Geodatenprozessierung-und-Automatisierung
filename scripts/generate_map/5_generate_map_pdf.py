"""
Script 5: Generate a map PDF from the QGIS project.

Workflow:
1. Open the QGIS project created by script 4.
2. Create one A4 landscape print layout.
3. Add one main map, a compact information panel, a north arrow and a scale bar.
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
    QgsLayoutItemPicture,
    QgsLayoutItemScaleBar,
    QgsLayoutItemShape,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsPrintLayout,
    QgsProject,
    QgsUnitTypes,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QFont


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "scripts/utils"))
sys.path.append(str(BASE_DIR / "scripts/generate_map"))

from map_config import get_map_config
from utils import ColoredArgumentParser, log_error, log_info, log_success


# -----------------------------------------------------------------------------
# 0. Configuration: input and output paths
# -----------------------------------------------------------------------------
PROJECT_DIR = BASE_DIR / "data/processed/qgis_projects"
OUTPUT_DIR = BASE_DIR / "data/processed/maps"

NORTH_ARROW_PATH = BASE_DIR / "assets/svg/NorthArrow_11.svg"


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


def automatic_extent_scale(extent) -> float:
    """Return a map padding factor based on the municipality size."""

    max_size = max(extent.width(), extent.height())

    if max_size < 5_000:
        return 1.45

    if max_size < 10_000:
        return 1.25

    if max_size < 20_000:
        return 1.15

    return 1.08


def scale_map_extent(extent, layout_config: dict) -> None:
    """Scale the map extent with automatic or manually configured padding."""

    scale_setting = layout_config["map_extent_scale"]

    if scale_setting == "auto":
        extent.scale(automatic_extent_scale(extent))
    else:
        extent.scale(float(scale_setting))


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

    layout.addLayoutItem(label)
    label.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))

    if width is not None and height is not None:
        label.attemptResize(QgsLayoutSize(width, height, QgsUnitTypes.LayoutMillimeters))
    else:
        label.adjustSizeToText()

    return label


def add_box(
    layout: QgsPrintLayout,
    x: float,
    y: float,
    width: float,
    height: float,
    color: str,
    outline_color: str = "80,80,80,255",
    outline_width: str = "0.2",
) -> QgsLayoutItemShape:
    """Add a simple colored rectangle to the layout."""

    box = QgsLayoutItemShape(layout)
    box.setShapeType(QgsLayoutItemShape.Rectangle)

    box.setSymbol(
        QgsFillSymbol.createSimple(
            {
                "color": color,
                "outline_color": outline_color,
                "outline_width": outline_width,
            }
        )
    )

    layout.addLayoutItem(box)
    box.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    box.attemptResize(QgsLayoutSize(width, height, QgsUnitTypes.LayoutMillimeters))

    return box


def add_debug_frame(
    layout: QgsPrintLayout,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    """Add a temporary red frame to visualize layout blocks."""

    add_box(
        layout,
        x,
        y,
        width,
        height,
        "255,255,255,0",
        "255,0,0,255",
        "0.2",
    )


def add_legend_row(
    layout: QgsPrintLayout,
    x: float,
    y: float,
    color: str,
    label: str,
    outline_color: str | None = None,
    symbol: str = "box",
) -> None:
    """Add one legend row with an aligned symbol and label."""

    if outline_color is None:
        outline_color = color

    symbol_width = 8
    symbol_height = 3.6
    symbol_y = y + 1.2

    if symbol == "line":
        # Roads are shown as a road-like symbol: white fill, yellow edge,
        # and a yellow center line.
        add_box(
            layout,
            x,
            symbol_y,
            symbol_width,
            symbol_height,
            "255,255,255,255",
            "0,0,0,255",
            "0.25",
        )
        add_box(
            layout,
            x + 1.1,
            symbol_y + 1.55,
            symbol_width - 2.2,
            0.5,
            color,
            color,
            "0",
        )
    else:
        add_box(
            layout,
            x,
            symbol_y,
            symbol_width,
            symbol_height,
            color,
            outline_color,
            "0.25",
        )

    add_label(layout, label, x + 12, y + 1.1, 8) # Align legend text vertically with the symbol.

def add_scale_bar_block(
    layout: QgsPrintLayout,
    map_item: QgsLayoutItemMap,
    x: float,
    y: float,
    width: float,
    units_per_segment: int = 90,
) -> QgsLayoutItemScaleBar:
    """Add the boxed graphical scale bar component."""

    box_height = 13
    padding_x = 2
    padding_y = 1

    # Outer frame around the scale bar component.
    add_box(
        layout,
        x,
        y,
        width,
        box_height,
        "255,255,255,255",
        "0,0,0,255",
        "0.25",
    )

    scale_bar = QgsLayoutItemScaleBar(layout)
    scale_bar.setStyle("Single Box")
    scale_bar.setLinkedMap(map_item)
    scale_bar.setUnits(QgsUnitTypes.DistanceMeters)
    scale_bar.setNumberOfSegments(2)
    scale_bar.setNumberOfSegmentsLeft(0)
    scale_bar.setUnitsPerSegment(units_per_segment)
    scale_bar.setHeight(3)
    scale_bar.setFont(QFont("Arial", 8))
    scale_bar.setFontColor(QColor(0, 0, 0))

    layout.addLayoutItem(scale_bar)

    scale_bar.attemptMove(
        QgsLayoutPoint(x + padding_x, y + padding_y, QgsUnitTypes.LayoutMillimeters)
    )
    scale_bar.attemptResize(
        QgsLayoutSize(width - 2 * padding_x, box_height - 2 * padding_y, QgsUnitTypes.LayoutMillimeters)
    )

    scale_bar.update()

    # QGIS does not always append the unit label to the last scale value in
    # standalone exports, so the unit is added as a separate aligned label.
    add_label(layout, "m", x + width - 13, y + 1.4, 8)

    return scale_bar

def add_map_grid(map_item: QgsLayoutItemMap) -> None:
    """Add a light coordinate grid to the map frame."""

    grid = map_item.grid()
    grid.setEnabled(True)
    grid.setIntervalX(500)
    grid.setIntervalY(500)
    grid.setGridLineColor(QColor(80, 80, 80, 90))
    grid.setGridLineWidth(0.10)
    grid.setAnnotationEnabled(False)


def add_north_arrow(
    layout: QgsPrintLayout,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    """Add the north arrow SVG from the project assets."""

    require_file(NORTH_ARROW_PATH, "North arrow SVG not found")

    north_arrow = QgsLayoutItemPicture(layout)
    north_arrow.setPicturePath(str(NORTH_ARROW_PATH))

    layout.addLayoutItem(north_arrow)
    north_arrow.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    north_arrow.attemptResize(QgsLayoutSize(width, height, QgsUnitTypes.LayoutMillimeters))


# -----------------------------------------------------------------------------
# 2. Create the PDF layout
# -----------------------------------------------------------------------------
def create_pdf_layout(
    project: QgsProject,
    municipality_name: str,
    technology: str,
) -> QgsPrintLayout:
    """Create an A4 landscape map layout without an inset map."""

    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(f"{municipality_name} Map PDF")

    layout.pageCollection().page(0).setPageSize(
        "A4",
        QgsLayoutItemPage.Landscape,
    )

    boundary_layer = find_boundary_layer(project, municipality_name)
    main_extent = boundary_layer.extent()
    map_config = get_map_config(technology)
    layout_config = map_config["layout"]
    scale_map_extent(main_extent, layout_config)

    # -------------------------------------------------------------------------
    # 2.1 Read the shared static layout template
    # -------------------------------------------------------------------------
    map_x = layout_config["map_x"]
    map_y = layout_config["map_y"]
    map_width = layout_config["map_width"]
    map_height = layout_config["map_height"]

    title_y = layout_config["title_y"]
    title_width = layout_config["title_width"]

    footer_y = layout_config["footer_y"]

    panel_x = layout_config["panel_x"]
    panel_width = layout_config["panel_width"]

    description_y = layout_config["description_y"]

    legend_y = layout_config["legend_y"]
    legend_width = layout_config["legend_width"]
    legend_height = layout_config["legend_height"]

    legend_title_y = layout_config["legend_title_y"]
    legend_section_y = layout_config["legend_section_y"]

    legend_row_start_y = layout_config["legend_row_start_y"]
    legend_row_gap = layout_config["legend_row_gap"]

    grid_title_y = layout_config["grid_title_y"]
    grid_row_y = layout_config["grid_row_y"]

    north_arrow_y = layout_config["north_arrow_y"]

    scale_bar_y = layout_config["scale_bar_y"]
    scale_text_y = layout_config["scale_text_y"]

    author_y = layout_config["author_y"]
    date_y = layout_config["date_y"]

    # -------------------------------------------------------------------------
    # 2.2 Add centered map title
    # -------------------------------------------------------------------------
    title_label = add_label(
        layout,
        map_config["title"].format(municipality=municipality_name),
        map_x,
        title_y,
        layout_config["title_font_size"],
        True,
        title_width,
        layout_config["title_height"],
    )
    title_label.setHAlign(Qt.AlignCenter)

    # -------------------------------------------------------------------------
    # 2.3 Add main map item
    # -------------------------------------------------------------------------
    # The map item is configured before it is added to the layout. This follows
    # the QGIS print layout documentation and avoids unwanted square map items.
    map_item = QgsLayoutItemMap(layout)
    map_item.setLayers(ordered_project_layers(project))

    map_item.attemptMove(
        QgsLayoutPoint(map_x, map_y, QgsUnitTypes.LayoutMillimeters)
    )
    map_item.attemptResize(
        QgsLayoutSize(map_width, map_height, QgsUnitTypes.LayoutMillimeters)
    )

    # zoomToExtent is used here instead of setExtent because it respects the
    # configured layout item size more reliably in standalone PyQGIS scripts.
    map_item.zoomToExtent(main_extent)
    map_item.setFrameEnabled(True)

    layout.addLayoutItem(map_item)

    add_map_grid(map_item)
    map_item.refresh()
    add_debug_frame(layout, map_x, map_y, map_width, map_height)  # todo:delte this lione

    # -------------------------------------------------------------------------
    # 2.4 Add right-side description
    # -------------------------------------------------------------------------
    add_debug_frame(
        layout,
        panel_x,
        description_y,
        panel_width,
        layout_config["description_height"],
    )  # todo:delte this lione
    add_label(
        layout,
        textwrap.fill(
            map_config["description"].format(municipality=municipality_name),
            width=layout_config["description_wrap_width"],
        ),
        panel_x,
        description_y,
        layout_config["description_font_size"],
        False,
        panel_width,
        layout_config["description_height"],
    )

    # -------------------------------------------------------------------------
    # 2.5 Add legend
    # -------------------------------------------------------------------------
    add_box(
        layout,
        panel_x,
        legend_y,
        legend_width,
        legend_height,
        "255,255,255,235",
    )
    add_debug_frame(layout, panel_x, legend_y, legend_width, legend_height)  # todo:delte this lione

    add_label(layout, "Legende", panel_x + 2, legend_title_y, 12, True)
    add_label(layout, map_config["legend_section"], panel_x + 2, legend_section_y + 1, 9, True)

    for index, item in enumerate(map_config["legend_items"]):
        add_legend_row(
            layout,
            panel_x + 2,
            legend_row_start_y + index * legend_row_gap,
            item["color"],
            item["label"],
            item["outline_color"],
            item.get("symbol", "box"),
        )

    add_label(layout, "Gitternetz", panel_x + 2, grid_title_y, 9, True)
    add_legend_row(
        layout,
        panel_x + 2,
        grid_row_y,
        "255,255,255,255",
        map_config["grid_distance_label"],
        "120,120,120,160",
    )

    # -------------------------------------------------------------------------
    # 2.6 Add north arrow and scale components
    # -------------------------------------------------------------------------
    add_north_arrow(
        layout,
        panel_x,
        north_arrow_y,
        layout_config["north_arrow_width"],
        layout_config["north_arrow_height"],
    )

    add_scale_bar_block(
        layout,
        map_item,
        panel_x,
        scale_bar_y,
        legend_width,
        units_per_segment=map_config["scale_units_per_segment"],
    )
    add_debug_frame(
        layout,
        panel_x,
        layout_config["panel_y"],
        panel_width,
        185,
    )  # todo:delte this lione

    scale_denominator = round(map_item.scale())

    add_label(
        layout,
        f"1:{scale_denominator:,}".replace(",", "."),
        panel_x,
        scale_text_y,
        8,
    )

    # -------------------------------------------------------------------------
    # 2.7 Add metadata block
    # -------------------------------------------------------------------------
    add_label(
        layout,
        "Autor: Elena Geiger, Florian Hoepfl",
        panel_x,
        author_y,
        layout_config["metadata_font_size"],
    )
    add_label(
        layout,
        f"Datum: {date.today().strftime('%d.%m.%Y')}",
        panel_x,
        date_y,
        layout_config["metadata_font_size"],
    )

    # -------------------------------------------------------------------------
    # 2.8 Add footer information below map
    # -------------------------------------------------------------------------
    add_label(
        layout,
        (
            "Datenquellen: "
            f"{textwrap.fill(map_config['sources'], width=layout_config['footer_wrap_width'])}\n"
            "Koordinatensystem: EPSG:25832 / ETRS89 UTM Zone 32N"
        ),
        map_x,
        footer_y,
        layout_config["footer_font_size"],
        False,
        map_width,
        layout_config["footer_height"],
    )
    add_debug_frame(
        layout,
        map_x,
        footer_y,
        map_width,
        layout_config["footer_height"],
    )  # todo:delte this lione

    return layout


# -----------------------------------------------------------------------------
# 3. Export QGIS project as PDF
# -----------------------------------------------------------------------------
def generate_map_pdf(municipality_name: str, technology: str) -> None:
    """Open the QGIS project and export a PDF map."""

    safe_name = safe_filename(municipality_name)

    project_file = PROJECT_DIR / f"{safe_name}_map.qgz"
    output_file = OUTPUT_DIR / f"{safe_name}_map.pdf"

    require_file(project_file, "QGIS project not found. Run script 4 first")
    require_file(NORTH_ARROW_PATH, "North arrow SVG not found")

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
        description="Generate a PDF map from the QGIS project."
    )

    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Geiersthal",
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
