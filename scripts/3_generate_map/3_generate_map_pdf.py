"""
Script 3: Generate a map PDF from the QGIS project.

Workflow:
1. Open the QGIS project created by map script 1.
2. Create one A4 landscape print layout.
3. Add one main map, a compact information panel, optional overview map,
   north arrow and a scale bar.
4. Export the layout as PDF.
"""

from pathlib import Path
import argparse
import html
import math
import sys
import warnings
from datetime import date

# PyQGIS imports. Main references: Python apps, projects, layouts and PDF export.
# (Docs: 1.4, 3.3, 10)
from qgis.core import (
    QgsApplication,
    QgsFillSymbol,
    QgsGeometry,
    QgsLinePatternFillSymbolLayer,
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
    QgsRectangle,
    QgsSimpleFillSymbolLayer,
    QgsSingleSymbolRenderer,
    QgsUnitTypes,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QFont


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts/utils"))
sys.path.insert(0, str(BASE_DIR / "scripts/3_generate_map"))

from map_config import get_map_config
from utils import ColoredArgumentParser, log_error, log_info, log_success


warnings.filterwarnings("ignore", category=DeprecationWarning)


# -----------------------------------------------------------------------------
# 0. Input and output paths
# -----------------------------------------------------------------------------
# input
PROJECT_DIR = BASE_DIR / "data/processed/3_qgis_projects"
OVERVIEW_DIR = BASE_DIR / "data/processed/1_base_overview"
BAVARIA_OUTLINE_FILE = OVERVIEW_DIR / "bayern_outline.gpkg"
WASSER_WMS_LEGEND_DIR = (
    BASE_DIR / "data/processed/2_technology_wasser/reference/legends"
)

# output
OUTPUT_DIR = BASE_DIR / "data/processed/3_maps"

# input
NORTH_ARROW_PATH = BASE_DIR / "assets/svg/NorthArrow_11.svg"


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
def safe_filename(name: str) -> str:
    """Create the same filename format as the other scripts."""

    return name.lower().replace(" ", "_")


def qgis_project_file_name(municipality_name: str, technology: str) -> str:
    """Create the technology-specific QGIS project file name."""

    return f"{safe_filename(municipality_name)}_map_{technology}.qgz"


def map_pdf_file_name(municipality_name: str, technology: str) -> str:
    """Create the technology-specific map PDF file name."""

    return f"{safe_filename(municipality_name)}_map_{technology}.pdf"


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
            "Map script 2 stopped because the output PDF is still open. "
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
    """Return visible project layers in the same order as the layer tree."""

    layers = []
    root = project.layerTreeRoot()

    for node in root.findLayers():
        if isinstance(node, QgsLayerTreeLayer):
            layer = node.layer()

            if layer is not None and node.isVisible():
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


def round_scale_up(scale: float, step: int) -> int:
    """Round a map scale denominator up to a clean configured step."""

    if step <= 0:
        return round(scale)

    return int(math.ceil(scale / step) * step)


def add_label(
    layout: QgsPrintLayout,
    text: str,
    x: float,
    y: float,
    font_size: int = 9,
    bold: bool = False,
    width: float | None = None,
    height: float | None = None,
    html_mode: bool = False,
) -> QgsLayoutItemLabel:
    """Add one text label to the layout."""

    label = QgsLayoutItemLabel(layout)
    label.setText(text)
    if html_mode:
        label.setMode(QgsLayoutItemLabel.ModeHtml)

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


def add_manual_multiline_label(
    layout: QgsPrintLayout,
    text: str,
    x: float,
    y: float,
    font_size: int,
    line_height: float,
    bold_prefixes: tuple[str, ...] = (),
    line_width: float | None = None,
    line_box_height: float | None = None,
) -> None:
    """Add manual text lines without QGIS automatic wrapping."""

    for line_index, line in enumerate(text.splitlines()):
        line_text = html.escape(line)
        html_mode = False

        for prefix in bold_prefixes:
            escaped_prefix = html.escape(prefix)
            if line_text.startswith(escaped_prefix):
                line_text = line_text.replace(
                    escaped_prefix,
                    f"<b>{escaped_prefix}</b>",
                    1,
                )
                html_mode = True
                break

        add_label(
            layout,
            line_text,
            x,
            y + line_index * line_height,
            font_size,
            False,
            line_width,
            line_box_height,
            html_mode,
        )


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


def color_from_rgba_string(rgba: str) -> QColor:
    """Convert a QGIS-style RGBA string into a QColor."""

    red, green, blue, alpha = [int(value) for value in rgba.split(",")]
    return QColor(red, green, blue, alpha)


def add_hatched_box(
    layout: QgsPrintLayout,
    x: float,
    y: float,
    width: float,
    height: float,
    color: str,
    outline_color: str,
) -> QgsLayoutItemShape:
    """Add a small legend box with a real QGIS line-pattern fill."""

    base_fill = QgsSimpleFillSymbolLayer.create(
        {
            "color": "255,255,255,255",
            "outline_color": outline_color,
            "outline_width": "0.3",
        }
    )

    hatch_fill = QgsLinePatternFillSymbolLayer()
    hatch_fill.setColor(color_from_rgba_string(color))
    hatch_fill.setLineWidth(0.22)
    hatch_fill.setDistance(1.45)
    hatch_fill.setAngle(45)

    symbol = QgsFillSymbol()
    symbol.changeSymbolLayer(0, base_fill)
    symbol.appendSymbolLayer(hatch_fill)

    box = QgsLayoutItemShape(layout)
    box.setShapeType(QgsLayoutItemShape.Rectangle)
    box.setSymbol(symbol)

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
    image_path: Path | None = None,
) -> None:
    """Add one legend row with an aligned symbol and label."""

    if outline_color is None:
        outline_color = color

    symbol_width = 8
    symbol_height = 3.6
    symbol_y = y + 1.2
    label_x = x + 12

    if symbol == "image" and image_path is not None and image_path.exists():
        symbol_width = 14
        label_x = x + 16
        picture = QgsLayoutItemPicture(layout)
        picture.setPicturePath(str(image_path))
        picture.attemptMove(
            QgsLayoutPoint(x, y + 0.55, QgsUnitTypes.LayoutMillimeters)
        )
        picture.attemptResize(
            QgsLayoutSize(symbol_width, 4.8, QgsUnitTypes.LayoutMillimeters)
        )
        layout.addLayoutItem(picture)
    elif symbol == "line":
        # Roads are represented as a framed line symbol, not as a filled area.
        add_box(
            layout,
            x,
            symbol_y,
            symbol_width,
            symbol_height,
            "255,255,255,255",
            "0,0,0,255",
            "0.3",
        )
        add_box(
            layout,
            x + 1,
            symbol_y + (symbol_height / 2) - 0.15,
            symbol_width - 2,
            0.3,
            color,
            color,
            "0",
        )
    elif symbol == "stripe_box":
        add_hatched_box(
            layout,
            x,
            symbol_y,
            symbol_width,
            symbol_height,
            color,
            outline_color,
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
            "0.3",
        )

    add_label(layout, label, label_x, y + 1.1, 8)  # Align legend text vertically with the symbol.


def resolve_legend_image_path(technology: str, item: dict) -> Path | None:
    """Return an optional local image path for an item-specific legend symbol."""

    image_name = item.get("legend_image")

    if technology == "wasser" and image_name:
        return WASSER_WMS_LEGEND_DIR / image_name

    return None

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


def apply_layer_symbol(layer: QgsVectorLayer, symbol) -> None:
    """Apply a symbol to a temporary overview-map layer."""

    renderer = layer.renderer()

    if renderer is None:
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        return

    renderer.setSymbol(symbol)


def find_osm_base_layer(project: QgsProject):
    """Return the OSM basemap layer used as background for the locator map."""

    fallback_layer = None

    for layer in project.mapLayers().values():
        layer_name = layer.name().lower()

        if "osm standard" in layer_name or "openstreetmap" in layer_name:
            return layer

        if "osm" in layer_name and not any(
            excluded in layer_name
            for excluded in ["straße", "strasse", "street", "transport", "context"]
        ):
            fallback_layer = layer

    return fallback_layer


def create_overview_layers(
    project: QgsProject,
    municipality_name: str,
) -> tuple[list, QgsRectangle] | None:
    """Load prepared Bavaria locator-map layers."""

    safe_name = safe_filename(municipality_name)
    municipality_overview_file = OVERVIEW_DIR / f"{safe_name}_overview.gpkg"

    if not BAVARIA_OUTLINE_FILE.exists():
        log_info(
            "Bavaria overview map skipped because the prepared outline is missing: "
            f"{display_path(BAVARIA_OUTLINE_FILE)}"
        )
        return None

    if not municipality_overview_file.exists():
        log_info(
            "Bavaria overview map skipped because the municipality locator file is missing: "
            f"{display_path(municipality_overview_file)}"
        )
        return None

    bavaria_layer = QgsVectorLayer(
        f"{BAVARIA_OUTLINE_FILE}|layername=bayern_outline",
        "Bayern Außenumriss",
        "ogr",
    )
    municipality_layer = QgsVectorLayer(
        f"{municipality_overview_file}|layername=overview_municipality",
        f"{municipality_name} Zielgemeinde",
        "ogr",
    )
    if not all(
        layer.isValid()
        for layer in [
            bavaria_layer,
            municipality_layer,
        ]
    ):
        log_info("Bavaria overview map skipped because a prepared locator layer is invalid.")
        return None

    bavaria_symbol = QgsFillSymbol.createSimple(
        {
            "color": "245,245,245,60",
            "outline_color": "90,90,90,220",
            "outline_width": "0.18",
        }
    )
    municipality_symbol = QgsFillSymbol.createSimple(
        {
            "color": "255,0,0,120",
            "outline_color": "255,0,0,255",
            "outline_width": "0.9",
        }
    )
    apply_layer_symbol(bavaria_layer, bavaria_symbol)
    apply_layer_symbol(municipality_layer, municipality_symbol)

    overview_extent = bavaria_layer.extent()
    overview_extent.scale(1.05)

    osm_layer = find_osm_base_layer(project)

    # Layer order for this inset map only. QgsLayoutItemMap renders the first
    # layer on top. The marker layer is still prepared by script 1 but
    # intentionally not shown in the PDF because the red municipality fill is
    # calmer.
    overview_layers = [
        municipality_layer,
        bavaria_layer,
    ]

    if osm_layer is not None:
        overview_layers.append(osm_layer)

    for layer in [
        bavaria_layer,
        municipality_layer,
    ]:
        project.addMapLayer(layer, False)

    return overview_layers, overview_extent


def add_overview_map(
    layout: QgsPrintLayout,
    project: QgsProject,
    layers: list,
    extent,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    """Add the small Bavaria locator map with the highlighted municipality."""

    overview_map = QgsLayoutItemMap(layout)
    overview_map.setId("Uebersichtskarte")
    overview_map.setLayers(layers)
    overview_map.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    overview_map.attemptResize(QgsLayoutSize(width, height, QgsUnitTypes.LayoutMillimeters))

    overview_map.zoomToExtent(extent)
    overview_map.setFrameEnabled(True)

    layout.addLayoutItem(overview_map)

    # TODO: QGIS-native linked-map overview was tested here, but did not render
    # reliably in the standalone PyQGIS export used by this project.
    # Keep the locator map simple for now: Bavaria + highlighted municipality.
    #
    # extent_indicator = QgsLayoutItemMapOverview("Ausschnitt Hauptkarte", overview_map)
    # extent_indicator.setLinkedMap(linked_map)
    # extent_indicator.setFrameSymbol(...)
    # overview_map.overviews().addOverview(extent_indicator)
    overview_map.refresh()

    title_width = 24
    title_height = 4.5
    title_x = x + width - title_width - 1
    title_y = y + 1

    add_box(
        layout,
        title_x,
        title_y,
        title_width,
        title_height,
        "255,255,255,145",
        "255,255,255,0",
        "0",
    )
    title_label = add_label(
        layout,
        "Lage in Bayern",
        title_x,
        title_y + 1.0,
        7,
        True,
        title_width,
        title_height - 0.2,
    )
    title_label.setHAlign(Qt.AlignCenter)


def overview_map_overlaps_boundary(
    boundary_layer: QgsVectorLayer,
    main_extent: QgsRectangle,
    map_x: float,
    map_y: float,
    map_width: float,
    map_height: float,
    overview_x: float,
    overview_y: float,
    overview_width: float,
    overview_height: float,
) -> bool:
    """Return True if the fixed overview map would cover the municipality."""

    relative_left = (overview_x - map_x) / map_width
    relative_right = (overview_x + overview_width - map_x) / map_width
    relative_top = (overview_y - map_y) / map_height
    relative_bottom = (overview_y + overview_height - map_y) / map_height

    if (
        relative_right <= 0
        or relative_left >= 1
        or relative_bottom <= 0
        or relative_top >= 1
    ):
        return False

    relative_left = max(0, relative_left)
    relative_right = min(1, relative_right)
    relative_top = max(0, relative_top)
    relative_bottom = min(1, relative_bottom)

    extent_width = main_extent.width()
    extent_height = main_extent.height()
    covered_extent = QgsRectangle(
        main_extent.xMinimum() + relative_left * extent_width,
        main_extent.yMaximum() - relative_bottom * extent_height,
        main_extent.xMinimum() + relative_right * extent_width,
        main_extent.yMaximum() - relative_top * extent_height,
    )
    covered_geometry = QgsGeometry.fromRect(covered_extent)

    for feature in boundary_layer.getFeatures():
        geometry = feature.geometry()
        if geometry and geometry.intersects(covered_geometry):
            return True

    return False


# -----------------------------------------------------------------------------
# 2. Create the PDF layout
# -----------------------------------------------------------------------------
def create_pdf_layout(
    project: QgsProject,
    municipality_name: str,
    technology: str,
) -> QgsPrintLayout:
    """Create an A4 landscape map layout with optional overview map."""

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
    debug_frames = layout_config.get("debug_frames", False)
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
    panel_y = layout_config["panel_y"]
    panel_width = layout_config["panel_width"]

    description_y = layout_config["description_y"]

    legend_y = layout_config["legend_y"]
    legend_width = layout_config["legend_width"]
    legend_height = layout_config["legend_height"]

    legend_title_y = legend_y + layout_config["legend_title_offset"]
    legend_section_y = legend_y + layout_config["legend_section_offset"]
    legend_row_start_y = legend_y + layout_config["legend_row_start_offset"]
    legend_row_gap = layout_config["legend_row_gap"]
    legend_note = map_config.get("legend_note")
    legend_note_after_index = map_config.get("legend_note_after_index")
    legend_note_extra_gap = (
        map_config.get("legend_note_extra_gap", 0) if legend_note else 0
    )
    legend_subnote_extra_gap = sum(
        float(item.get("subnote_extra_gap", 0))
        for item in map_config["legend_items"]
        if item.get("subnote")
    )
    legend_gap_after_first_item = float(
        layout_config.get("legend_gap_after_first_item", 0)
    )

    last_legend_row_y = legend_row_start_y + (
        (len(map_config["legend_items"]) - 1) * legend_row_gap
    ) + legend_note_extra_gap + legend_subnote_extra_gap + legend_gap_after_first_item
    grid_title_y = last_legend_row_y + layout_config["grid_title_gap_after_last_row"]
    grid_row_y = grid_title_y + layout_config["grid_row_offset"]

    north_arrow_y = layout_config["north_arrow_y"]

    scale_bar_y = layout_config["scale_bar_y"]
    scale_text_y = layout_config["scale_text_y"]

    panel_height = (map_y + map_height) - panel_y

    # Author and date get their own footer block on the right. This keeps the
    # metadata separate from the scale bar and aligned with the data-source
    # footer below the main map.
    metadata_box_x = panel_x
    metadata_box_y = footer_y
    metadata_box_width = panel_width
    metadata_box_height = layout_config["footer_height"]
    author_y = metadata_box_y + 2.0
    date_y = author_y + 4.2

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
    map_item.setId("Hauptkarte")
    visible_layers = ordered_project_layers(project)
    map_item.setLayers(visible_layers)

    map_item.attemptMove(
        QgsLayoutPoint(map_x, map_y, QgsUnitTypes.LayoutMillimeters)
    )
    map_item.attemptResize(
        QgsLayoutSize(map_width, map_height, QgsUnitTypes.LayoutMillimeters)
    )

    # zoomToExtent is used here instead of setExtent because it respects the
    # configured layout item size more reliably in standalone PyQGIS scripts.
    map_item.zoomToExtent(main_extent)
    map_item.setScale(
        round_scale_up(
            map_item.scale(),
            layout_config.get("main_scale_step", 500),
        )
    )
    map_item.setFrameEnabled(True)

    layout.addLayoutItem(map_item)

    add_map_grid(map_item)
    map_item.refresh()
    if debug_frames:
        add_debug_frame(layout, map_x, map_y, map_width, map_height)

    # -------------------------------------------------------------------------
    # 2.4 Add right-side description
    # -------------------------------------------------------------------------
    add_manual_multiline_label(
        layout,
        map_config["description"].format(municipality=municipality_name),
        panel_x,
        description_y,
        layout_config["description_font_size"],
        3.2,
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
    if debug_frames:
        add_debug_frame(layout, panel_x, legend_y, legend_width, legend_height)
    add_box(
        layout,
        panel_x,
        legend_y,
        legend_width,
        legend_height,
        "255,255,255,0",
        "80,80,80,255",
        "0.2",
    )

    add_label(layout, "Legende", panel_x + 2, legend_title_y, 12, True)
    add_label(
        layout,
        map_config["legend_section"],
        panel_x + 2,
        legend_section_y + 1,
        layout_config.get("legend_section_font_size", 9),
        True,
        width=legend_width - 4,
        height=6,
    )

    current_legend_row_y = legend_row_start_y

    for index, item in enumerate(map_config["legend_items"]):
        add_legend_row(
            layout,
            panel_x + 2,
            current_legend_row_y,
            item["color"],
            item["label"],
            item["outline_color"],
            item.get("symbol", "box"),
            resolve_legend_image_path(technology, item),
        )

        if legend_note and index == legend_note_after_index:
            add_label(
                layout,
                legend_note,
                panel_x + 2,
                current_legend_row_y + legend_row_gap + 1.5,
                6,
                False,
                width=legend_width - 4,
                height=4,
            )
            current_legend_row_y += legend_note_extra_gap

        if item.get("subnote"):
            add_label(
                layout,
                item["subnote"],
                panel_x + 2,
                current_legend_row_y + 6.0,
                5,
                False,
                width=legend_width - 4,
                height=3,
            )
            current_legend_row_y += float(item.get("subnote_extra_gap", 0))

        if index == 0:
            current_legend_row_y += legend_gap_after_first_item

        current_legend_row_y += legend_row_gap

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
    if layout_config.get("overview_map_enabled", False):
        overview = create_overview_layers(
            project,
            municipality_name,
        )

        if overview is None:
            overview_layers = visible_layers
            overview_extent = boundary_layer.extent()
            overview_extent.scale(3.2)
        else:
            overview_layers, overview_extent = overview

        overview_overlaps_boundary = overview_map_overlaps_boundary(
            boundary_layer,
            main_extent,
            map_x,
            map_y,
            map_width,
            map_height,
            layout_config["overview_map_x"],
            layout_config["overview_map_y"],
            layout_config["overview_map_width"],
            layout_config["overview_map_height"],
        )

        if overview_overlaps_boundary:
            log_info(
                "Bavaria overview map skipped because it would cover the municipality "
                "in the main map."
            )
        else:
            add_overview_map(
                layout,
                project,
                overview_layers,
                overview_extent,
                layout_config["overview_map_x"],
                layout_config["overview_map_y"],
                layout_config["overview_map_width"],
                layout_config["overview_map_height"],
            )

    north_arrow_x = panel_x

    if layout_config.get("north_arrow_inside_map", False):
        north_arrow_margin = layout_config.get("north_arrow_map_margin", 3)
        north_arrow_x = (
            map_x
            + map_width
            - layout_config["north_arrow_width"]
            - north_arrow_margin
        )
        north_arrow_y = (
            map_y
            + map_height
            - layout_config["north_arrow_height"]
            - north_arrow_margin
        )

    add_north_arrow(
        layout,
        north_arrow_x,
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
    if debug_frames:
        add_debug_frame(
            layout,
            panel_x,
            panel_y,
            panel_width,
            panel_height,
        )

    scale_denominator = round(map_item.scale())

    add_label(
        layout,
        f"1:{scale_denominator:,}".replace(",", "."),
        panel_x + 2,
        scale_text_y,
        8,
    )

    # -------------------------------------------------------------------------
    # 2.7 Add metadata block
    # -------------------------------------------------------------------------
    if debug_frames:
        add_debug_frame(
            layout,
            metadata_box_x,
            metadata_box_y,
            metadata_box_width,
            metadata_box_height,
        )

    add_label(
        layout,
        "Autor: Elena Geiger, Florian Höpfl",
        metadata_box_x + 2,
        author_y,
        layout_config["metadata_font_size"],
    )
    add_label(
        layout,
        f"Datum: {date.today().strftime('%d.%m.%Y')}",
        metadata_box_x + 2,
        date_y,
        layout_config["metadata_font_size"],
    )

    # 2.8 Add footer information below map
    # -----------------------------------------------------------------------------
    add_label(
        layout,
        "Datenquellen: " + map_config["sources"],
        map_x,
        footer_y,
        layout_config["footer_font_size"],
        False,
        map_width,
        layout_config["footer_height"],
    )

    if debug_frames:
        add_debug_frame(
            layout,
            map_x,
            footer_y,
            map_width,
            layout_config["footer_height"],
        )

    return layout

# -----------------------------------------------------------------------------
# 3. Export QGIS project as PDF
# -----------------------------------------------------------------------------
def generate_map_pdf(municipality_name: str, technology: str) -> None:
    """Open the QGIS project and export a PDF map."""

    safe_name = safe_filename(municipality_name)

    project_file = PROJECT_DIR / qgis_project_file_name(municipality_name, technology)
    output_file = OUTPUT_DIR / map_pdf_file_name(municipality_name, technology)

    require_file(project_file, "QGIS project not found. Run map script 1 first")
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


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""

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

    return parser.parse_args()


def main() -> None:
    """Generate the requested PDF map."""

    args = parse_arguments()
    generate_map_pdf(args.municipality, args.technology)


if __name__ == "__main__":

    # QgsApplication is required when PyQGIS is used outside the QGIS GUI. (Doc: 1.4)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    try:
        main()
    finally:
        qgs.exitQgis()

