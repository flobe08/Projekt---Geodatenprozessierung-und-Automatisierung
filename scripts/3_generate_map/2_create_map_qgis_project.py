"""
Script 2: Create a QGIS map project.

Workflow:
1. Load an OpenStreetMap web basemap.
2. Load the official municipality boundary from script 2.
3. Load the prepared technology layers for the selected workflow.
4. Apply basic symbology for QGIS inspection and PDF export.
5. Save everything as a QGIS project for manual map layout work.
"""

from pathlib import Path
import argparse
import sys

from qgis.PyQt.QtGui import QImage
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsFillSymbol,
    QgsLinePatternFillSymbolLayer,
    QgsLayerTreeLayer,
    QgsLineSymbol,
    QgsProject,
    QgsRasterLayer,
    QgsReferencedRectangle,
    QgsSimpleFillSymbolLayer,
    QgsSingleSymbolRenderer,
    QgsVectorLayer,
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "scripts/utils"))

from utils import ColoredArgumentParser, log_warning


# =============================================================================
# 0. Input and output paths
# =============================================================================
# input
BOUNDARY_DIR = BASE_DIR / "data/processed/1_base_boundaries"
WIND_DIR = BASE_DIR / "data/processed/2_technology_wind"
PROTECTION_DIR = BASE_DIR / "data/processed/1_base_protection_areas"
SOLAR_DIR = BASE_DIR / "data/processed/2_technology_solar"
SOLAR_REFERENCE_DIR = SOLAR_DIR / "reference"
WASSER_DIR = BASE_DIR / "data/processed/2_technology_wasser"
WASSER_REFERENCE_DIR = WASSER_DIR / "reference"

# output
OUTPUT_DIR = BASE_DIR / "data/processed/3_qgis_projects"

SOLAR_WMS_ZOOM_1 = "PV-Freiflächenkulisse - Zoomstufe 1"
SOLAR_WMS_ZOOM_2 = "PV-Freiflächenkulisse - Zoomstufe 2"


# =============================================================================
# General layer name helpers
# =============================================================================
def safe_filename(name: str) -> str:
    """Create a safe file name from a municipality name."""

    return name.lower().replace(" ", "_")


def vorrang_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for wind vorrang areas."""

    return f"wind_vorranggebiete_{safe_filename(municipality_name)}"


def vorbehalt_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for wind vorbehalt areas."""

    return f"wind_vorbehaltsgebiete_{safe_filename(municipality_name)}"


def naturschutz_hart_file_name(municipality_name: str) -> str:
    """Create the municipality-specific file name for hard protection areas."""

    return f"{safe_filename(municipality_name)}_naturschutz_allgemein_hart.gpkg"


def naturschutz_weich_file_name(municipality_name: str) -> str:
    """Create the municipality-specific file name for soft protection areas."""

    return f"{safe_filename(municipality_name)}_naturschutz_allgemein_weich.gpkg"


def naturschutz_wind_file_name(municipality_name: str) -> str:
    """Create the municipality-specific file name for wind-specific protection areas."""

    return f"{safe_filename(municipality_name)}_naturschutz_wind.gpkg"


def naturschutz_hart_layer_name() -> str:
    """Return the merged layer name for hard protection areas."""

    return "naturschutz_allgemein_hart_merged"


def naturschutz_weich_layer_name() -> str:
    """Return the merged layer name for soft protection areas."""

    return "naturschutz_allgemein_weich_merged"


def naturschutz_wind_layer_name() -> str:
    """Return the merged layer name for wind-specific protection areas."""

    return "naturschutz_wind_merged"


def wasserschutz_hart_file_name(municipality_name: str) -> str:
    """Create the municipality-specific file name for hard water protection areas."""

    return f"{safe_filename(municipality_name)}_wasserschutz_hart.gpkg"


def wasserschutz_hart_layer_name() -> str:
    """Return the merged layer name for hard water protection areas."""

    return "wasserschutz_hart_merged"


NATURSCHUTZ_HART_DETAIL_LAYERS = [
    "naturschutzgebiete",
    "nationalparke",
    "nationale_naturmonumente",
    "naturdenkmale_flaechen",
    "geschuetzte_landschaftsbestandteile_flaechen",
    "ramsar_gebiete",
    "natura2000_ffh",
    "natura2000_vogelschutz",
    "naturdenkmale_punkte",
    "geschuetzte_landschaftsbestandteile_punkte",
]


NATURSCHUTZ_WEICH_DETAIL_LAYERS = [
    "biosphaerenreservate",
    "landschaftsschutzgebiete",
    "naturparke",
]


NATURSCHUTZ_WIND_DETAIL_LAYERS = [
    "vogelkulissen_2024",
]


WASSERSCHUTZ_HART_DETAIL_LAYERS = [
    "trinkwasserschutzgebiete",
    "heilquellenschutzgebiete",
]


def solar_transport_axis_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for the 500 m solar transport basis."""

    return f"pv_verkehrsachsen_500m_{safe_filename(municipality_name)}"


def solar_eeg_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for the 500 m EEG buffer."""

    return f"pv_förderkulisse_500m_{safe_filename(municipality_name)}"


def solar_baugb_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for the 200 m BauGB buffer."""

    return f"pv_privilegierung_200m_{safe_filename(municipality_name)}"


def wind_landuse_ausschluss_file_name(municipality_name: str) -> str:
    """Create the municipality-specific file name for wind landuse exclusions."""

    return f"{safe_filename(municipality_name)}_landuse_wind_ausschluss.gpkg"


def solar_landuse_ausschluss_file_name(municipality_name: str) -> str:
    """Create the municipality-specific file name for solar landuse exclusions."""

    return f"{safe_filename(municipality_name)}_landuse_solar_ausschluss.gpkg"


def solar_pv_freiflaechen_naehung_file_name(municipality_name: str) -> str:
    """Create the municipality-specific file name for the solar PV vector approximation."""

    return (
        f"{safe_filename(municipality_name)}"
        "_landuse_solar_pv_freiflaechen_naehung_vektorlayer.gpkg"
    )


def wind_landuse_ausschluss_layer_name() -> str:
    """Return the layer name for wind landuse exclusions."""

    return "landuse_wind_ausschluss"


def solar_landuse_ausschluss_layer_name() -> str:
    """Return the layer name for solar landuse exclusions."""

    return "landuse_solar_ausschluss"


def solar_pv_freiflaechen_naehung_layer_name() -> str:
    """Return the layer name for the solar PV vector approximation."""

    return "landuse_solar_pv_freiflaechen_naehung_vektorlayer"


def osm_wind_ausschluss_layer_name() -> str:
    """Return the prepared OSM exclusion layer name for wind."""

    return "osm_streets_wind_ausschluss"


def wind_ausschluss_gesamt_file_name(municipality_name: str) -> str:
    """Create the municipality-specific file name for combined wind exclusions."""

    return f"{safe_filename(municipality_name)}_wind_ausschluss_gesamt.gpkg"


def wind_ausschluss_gesamt_layer_name() -> str:
    """Return the combined wind exclusion layer name."""

    return "wind_ausschluss_gesamt"


def wind_ausschluss_landuse_layer_name() -> str:
    """Return the wind exclusion validation layer for landuse buffers."""

    return "wind_ausschluss_landuse_puffer"


def wind_ausschluss_osm_buffer_layer_name() -> str:
    """Return the wind exclusion validation layer for active OSM street buffers."""

    return "wind_ausschluss_osm_streets_puffer"


def osm_solar_ausschluss_layer_name() -> str:
    """Return the prepared OSM exclusion layer name for solar."""

    return "osm_streets_solar_ausschluss"


def qgis_project_file_name(municipality_name: str, technology: str) -> str:
    """Create the technology-specific QGIS project file name."""

    return f"{safe_filename(municipality_name)}_map_{technology}.qgz"


def solar_reference_raster_name(municipality_name: str, zoom_level: int) -> str:
    """Create the file name of one downloaded solar WMS reference raster."""

    return (
        f"{safe_filename(municipality_name)}_"
        f"pv_freiflaechenkulisse_zoomstufe_{zoom_level}.png"
    )


# =============================================================================
# General file and layer helpers
# =============================================================================
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


def load_vector_layer(path: Path, layer_name: str, display_name: str) -> QgsVectorLayer:
    """Load one GeoPackage layer as a QGIS vector layer."""

    uri = f"{path}|layername={layer_name}"
    layer = QgsVectorLayer(uri, display_name, "ogr")

    if not layer.isValid():
        raise RuntimeError(f"Layer could not be loaded: {display_name}")

    return layer


def load_optional_vector_layer(
    path: Path,
    layer_name: str,
    display_name: str,
) -> QgsVectorLayer | None:
    """Load one optional GeoPackage layer or return None when it is missing."""

    uri = f"{path}|layername={layer_name}"
    layer = QgsVectorLayer(uri, display_name, "ogr")

    if not layer.isValid():
        return None

    return layer

#TODO
def load_optional_raster_layer(
    raster_file: Path,
    display_name: str,
) -> QgsRasterLayer | None:
    """Load one optional local solar reference raster for the QGIS project."""

    if not raster_file.exists():
        log_warning(f"Solar reference raster not found: {display_path(raster_file)}")
        log_warning(
            "Run Step 3.1 first through scripts/3_generate_map.py, or run: "
            "python3 scripts/2_2_solar/3_download_solar_reference_wms.py --municipality <name>"
        )
        return None

    image = QImage(str(raster_file))

    if image.isNull():
        log_warning(
            f"Solar reference raster could not be read as image: {display_name}"
        )
        return None

    if image.hasAlphaChannel():
        has_visible_pixels = False

        for x in range(image.width()):
            for y in range(image.height()):
                if image.pixelColor(x, y).alpha() > 0:
                    has_visible_pixels = True
                    break
            if has_visible_pixels:
                break

        if not has_visible_pixels:
            log_warning(
                f"Solar reference raster is fully transparent and will be skipped: {display_name}"
            )
            return None

    layer = QgsRasterLayer(str(raster_file), display_name)

    if not layer.isValid():
        log_warning(
            f"Amtlicher Solar-Referenzlayer konnte nicht geladen werden: {display_name}"
        )
        log_warning(
            "Die Kartenerstellung läuft weiter. Der Referenzlayer kann bei Bedarf manuell in QGIS ergänzt werden."
        )
        return None

    return layer


def layer_has_features(layer: QgsVectorLayer | None) -> bool:
    """Return True only if the optional layer exists and contains features."""

    if layer is None:
        return False

    return layer.featureCount() > 0


def move_layer_to_top(project: QgsProject, layer: QgsVectorLayer) -> None:
    """Move a layer to the top of the QGIS layer tree."""

    root = project.layerTreeRoot()
    layer_node = root.findLayer(layer.id())

    if isinstance(layer_node, QgsLayerTreeLayer):
        clone = layer_node.clone()
        parent = layer_node.parent()
        parent.insertChildNode(0, clone)
        parent.removeChildNode(layer_node)


def set_layer_visibility(
    project: QgsProject,
    layer: QgsVectorLayer | QgsRasterLayer,
    visible: bool,
) -> None:
    """Set layer visibility in the QGIS layer tree."""

    layer_node = project.layerTreeRoot().findLayer(layer.id())

    if isinstance(layer_node, QgsLayerTreeLayer):
        layer_node.setItemVisibilityChecked(visible)


def add_layer_to_group(
    project: QgsProject,
    group_name: str,
    layer: QgsVectorLayer | QgsRasterLayer,
    *,
    visible: bool,
) -> None:
    """Add a layer to a named QGIS group and set its default visibility."""

    root = project.layerTreeRoot()
    group = root.findGroup(group_name)

    if group is None:
        # Put validation groups above the OSM basemap. They are hidden by
        # default, but appear immediately above the basemap when enabled.
        group = root.insertGroup(0, group_name)

    project.addMapLayer(layer, False)
    layer_node = group.addLayer(layer)
    layer_node.setItemVisibilityChecked(visible)


def add_optional_layers_to_group(
    project: QgsProject,
    group_name: str,
    source_file: Path,
    layer_names: list[str],
    municipality_name: str,
) -> None:
    """Add optional source layers to a hidden detail and attribute group.

    Detail and attribute layers are loaded when the GeoPackage layer exists,
    even if it currently has zero features for the municipality. This keeps the
    QGIS project structure complete and makes it clear which source datasets
    were checked.
    """

    for layer_name in layer_names:
        detail_layer = load_optional_vector_layer(
            source_file,
            layer_name,
            f"{safe_filename(municipality_name)} - {layer_name}",
        )

        if detail_layer is not None:
            add_layer_to_group(
                project,
                group_name,
                detail_layer,
                visible=False,
            )


def apply_symbol(layer: QgsVectorLayer, symbol: QgsFillSymbol | QgsLineSymbol) -> None:
    """Apply one symbol safely, even if QGIS did not create a default renderer."""

    renderer = layer.renderer()

    if renderer is None:
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        return

    renderer.setSymbol(symbol)


def color_from_rgba_string(rgba: str) -> QColor:
    """Convert a QGIS-style RGBA string into a QColor."""

    red, green, blue, alpha = [int(value) for value in rgba.split(",")]
    return QColor(red, green, blue, alpha)


def build_hatched_fill_symbol(
    outline_rgba: str,
    hatch_rgba: str,
    *,
    outline_width: float,
    hatch_width: float,
    hatch_distance: float,
    hatch_angle: float = 45.0,
) -> QgsFillSymbol:
    """Build a polygon symbol with outline plus one-direction line hatch."""

    base_fill = QgsSimpleFillSymbolLayer.create(
        {
            "color": "255,255,255,0",
            "outline_color": outline_rgba,
            "outline_width": str(outline_width),
        }
    )

    hatch_fill = QgsLinePatternFillSymbolLayer()
    hatch_fill.setColor(color_from_rgba_string(hatch_rgba))
    hatch_fill.setLineWidth(hatch_width)
    hatch_fill.setDistance(hatch_distance)
    hatch_fill.setAngle(hatch_angle)

    symbol = QgsFillSymbol()
    symbol.changeSymbolLayer(0, base_fill)
    symbol.appendSymbolLayer(hatch_fill)
    return symbol


# =============================================================================
# General styling
# =============================================================================
def style_boundary(layer: QgsVectorLayer) -> None:
    """Style the municipality boundary with transparent fill and dark outline."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "40,40,40,0",
            "outline_color": "45,45,45,255",
            "outline_width": "0.4",
        }
    )
    apply_symbol(layer, symbol)


# =============================================================================
# Wind styling
# =============================================================================
def style_wind_vorrang(layer: QgsVectorLayer) -> None:
    """Style wind vorrang areas with an opaque blue fill."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "31,60,160,180",
            "outline_color": "18,40,120,255",
            "outline_width": "0.15",
        }
    )
    apply_symbol(layer, symbol)


def style_wind_vorbehalt(layer: QgsVectorLayer) -> None:
    """Style wind vorbehalt areas with a distinct violet fill."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "142,108,185,175",
            "outline_color": "94,64,140,255",
            "outline_width": "0.15",
        }
    )
    apply_symbol(layer, symbol)


def style_naturschutz_hart(layer: QgsVectorLayer) -> None:
    """Style hard protection areas with a QGIS-style red line-pattern hatch."""

    symbol = build_hatched_fill_symbol(
        "255,0,0,255",
        "255,0,0,255",
        outline_width=0.25,
        hatch_width=0.28,
        hatch_distance=2.0,
    )
    apply_symbol(layer, symbol)


def style_naturschutz_weich(layer: QgsVectorLayer) -> None:
    """Style soft protection areas as a subtle transparent yellow context fill."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "245,210,80,55",
            "outline_color": "196,150,35,150",
            "outline_width": "0.10",
        }
    )
    apply_symbol(layer, symbol)


def style_naturschutz_wind(layer: QgsVectorLayer) -> None:
    """Style wind-specific protection areas with orange-red diagonal stripes."""

    symbol = build_hatched_fill_symbol(
        "196,108,0,255",
        "232,136,20,255",
        outline_width=0.22,
        hatch_width=0.24,
        hatch_distance=2.0,
    )
    apply_symbol(layer, symbol)


def style_wasserschutz_hart(layer: QgsVectorLayer) -> None:
    """Style hard water protection areas with a teal transparent fill."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "79,184,166,125",
            "outline_color": "0,118,110,220",
            "outline_width": "0.16",
        }
    )
    apply_symbol(layer, symbol)


def style_wind_ausschluss_gesamt(layer: QgsVectorLayer) -> None:
    """Style the combined wind exclusion layer as a distinct purple area."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "125,72,165,105",
            "outline_color": "92,47,128,220",
            "outline_width": "0.16",
        }
    )
    apply_symbol(layer, symbol)


def style_wind_osm_context_lines(layer: QgsVectorLayer) -> None:
    """Style OSM street lines that have no active wind buffer."""

    symbol = QgsLineSymbol.createSimple(
        {
            "color": "110,110,110,220",
            "width": "0.36",
        }
    )
    apply_symbol(layer, symbol)


# =============================================================================
# Solar styling
# =============================================================================
def style_solar_eeg(layer: QgsVectorLayer) -> None:
    """Style the 500 m EEG buffer with a warm yellow transparent fill."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "242,186,33,130",
            "outline_color": "189,136,0,255",
            "outline_width": "0.15",
        }
    )
    apply_symbol(layer, symbol)


def style_solar_baugb(layer: QgsVectorLayer) -> None:
    """Style the 200 m BauGB buffer with a blue transparent fill."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "31,60,160,150",
            "outline_color": "18,40,120,255",
            "outline_width": "0.15",
        }
    )
    apply_symbol(layer, symbol)


def style_solar_transport_axes(layer: QgsVectorLayer) -> None:
    """Style motorway and railway axes with a dark line."""

    symbol = QgsLineSymbol.createSimple(
        {
            "color": "60,60,60,255",
            "width": "0.55",
        }
    )
    apply_symbol(layer, symbol)


def style_solar_landuse_ausschluss(layer: QgsVectorLayer) -> None:
    """Style solar landuse exclusions as a distinct purple context layer."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "125,72,165,95",
            "outline_color": "92,47,128,210",
            "outline_width": "0.14",
        }
    )
    apply_symbol(layer, symbol)


# =============================================================================
# Shared project setup
# =============================================================================
def create_empty_project() -> QgsProject:
    """Create a clean QGIS project with EPSG:25832 and OSM basemap."""

    project = QgsProject.instance()
    project.clear()
    project.setCrs(QgsCoordinateReferenceSystem("EPSG:25832"))

    osm_url = "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    osm_layer = QgsRasterLayer(osm_url, "OSM Standard", "wms")

    if not osm_layer.isValid():
        raise RuntimeError("OSM Standard layer could not be loaded.")

    project.addMapLayer(osm_layer)
    return project


def set_project_extent_from_boundary(
    project: QgsProject,
    boundary_layer: QgsVectorLayer,
) -> None:
    """Set the default project view to a slightly padded boundary extent."""

    extent = boundary_layer.extent()
    extent.scale(1.15)
    project.viewSettings().setDefaultViewExtent(
        QgsReferencedRectangle(extent, boundary_layer.crs())
    )


# =============================================================================
# Wind workflow
# =============================================================================
def create_wind_map_project(municipality_name: str) -> None:
    """Create a QGIS project for the wind workflow."""

    safe_name = safe_filename(municipality_name)

    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    wind_file = WIND_DIR / f"{safe_name}_wind_layers.gpkg"
    protection_hard_file = PROTECTION_DIR / naturschutz_hart_file_name(municipality_name)
    protection_weich_file = PROTECTION_DIR / naturschutz_weich_file_name(municipality_name)
    protection_wind_file = PROTECTION_DIR / naturschutz_wind_file_name(municipality_name)
    wind_ausschluss_file = WIND_DIR / wind_ausschluss_gesamt_file_name(municipality_name)
    output_file = OUTPUT_DIR / qgis_project_file_name(municipality_name, "wind")

    require_file(boundary_file, "Boundary file not found. Run script 2 first")
    require_file(wind_file, "Wind planning file not found. Run wind script 1 first")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    project = create_empty_project()

    # -------------------------------------------------------------------------
    # Wind planning layers
    # Official planning result layers from the regional planning workflow.
    # -------------------------------------------------------------------------
    vorrang_layer = load_vector_layer(
        wind_file,
        vorrang_layer_name(municipality_name),
        f"Wind Vorranggebiete {municipality_name}",
    )
    vorbehalt_layer = load_optional_vector_layer(
        wind_file,
        vorbehalt_layer_name(municipality_name),
        f"Wind Vorbehaltsgebiete {municipality_name}",
    )

    # -------------------------------------------------------------------------
    # General and wind-specific protection layers
    # These layers summarize hard restrictions, soft conflict areas and
    # wind-specific bird/sensitivity datasets for map display.
    # -------------------------------------------------------------------------
    naturschutz_hart_layer = load_optional_vector_layer(
        protection_hard_file,
        naturschutz_hart_layer_name(),
        f"Harte Naturschutz-Restriktionen {municipality_name}",
    )
    naturschutz_weich_layer = load_optional_vector_layer(
        protection_weich_file,
        naturschutz_weich_layer_name(),
        f"Weiche Naturschutz-Konfliktflächen {municipality_name}",
    )
    naturschutz_wind_layer = load_optional_vector_layer(
        protection_wind_file,
        naturschutz_wind_layer_name(),
        f"Windspezifische Restriktionen {municipality_name}",
    )

    # -------------------------------------------------------------------------
    # Optional combined exclusion layer for QGIS inspection
    # This layer combines buffered landuse and OSM street exclusions. It is
    # loaded into the QGIS project but hidden by default, so the PDF map is not
    # changed until the layer is intentionally enabled.
    # -------------------------------------------------------------------------
    wind_ausschluss_layer = load_optional_vector_layer(
        wind_ausschluss_file,
        wind_ausschluss_gesamt_layer_name(),
        f"Wind Ausschlussflächen gesamt {municipality_name}",
    )
    wind_ausschluss_landuse_layer = load_optional_vector_layer(
        wind_ausschluss_file,
        wind_ausschluss_landuse_layer_name(),
        f"{safe_name}_wind_ausschluss_gesamt - wind_ausschluss_landuse_puffer",
    )
    wind_ausschluss_osm_buffer_layer = load_optional_vector_layer(
        wind_ausschluss_file,
        wind_ausschluss_osm_buffer_layer_name(),
        f"{safe_name}_wind_ausschluss_gesamt - wind_ausschluss_osm_streets_puffer",
    )
    # -------------------------------------------------------------------------
    # TODO: Future wind exclusion layers
    # These prepared exclusion layers already exist as processing outputs.
    # They are intentionally kept commented out until the final exclusion
    # design for the wind map is fixed and cartographically tested.
    # -------------------------------------------------------------------------
    # wind_landuse_file = WIND_DIR / wind_landuse_ausschluss_file_name(municipality_name)
    # wind_osm_file = WIND_DIR / f"{safe_name}_osm_wind_streets.gpkg"
    # wind_landuse_layer = load_optional_vector_layer(
    #     wind_landuse_file,
    #     wind_landuse_ausschluss_layer_name(),
    #     f"Landnutzung Ausschluss Wind {municipality_name}",
    # )
    # wind_osm_layer = load_optional_vector_layer(
    #     wind_osm_file,
    #     osm_wind_ausschluss_layer_name(),
    #     f"OSM Straßen Ausschluss Wind {municipality_name}",
    # )

    # -------------------------------------------------------------------------
    # Administrative boundary
    # The municipality boundary is always added last and moved to the top.
    # -------------------------------------------------------------------------
    boundary_layer = QgsVectorLayer(str(boundary_file), municipality_name, "ogr")

    if not boundary_layer.isValid():
        raise RuntimeError(f"Boundary layer could not be loaded: {boundary_file}")

    style_wind_vorrang(vorrang_layer)
    style_boundary(boundary_layer)

    if layer_has_features(naturschutz_weich_layer):
        style_naturschutz_weich(naturschutz_weich_layer)
        project.addMapLayer(naturschutz_weich_layer)

    if layer_has_features(naturschutz_hart_layer):
        style_naturschutz_hart(naturschutz_hart_layer)
        project.addMapLayer(naturschutz_hart_layer)

    if layer_has_features(naturschutz_wind_layer):
        style_naturschutz_wind(naturschutz_wind_layer)
        project.addMapLayer(naturschutz_wind_layer)

    if layer_has_features(wind_ausschluss_layer):
        style_wind_ausschluss_gesamt(wind_ausschluss_layer)
        project.addMapLayer(wind_ausschluss_layer)

    # Validation layers from the same GeoPackage are loaded but hidden by
    # default. They make the QGIS project explorable without changing the PDF.
    # OSM street lines without active buffer are not duplicated here because
    # they are loaded once as the visible main map layer "Straßen und Wege".
    validation_group_name = "Detail- und Attributlayer Wind-Ausschluss"

    if layer_has_features(wind_ausschluss_landuse_layer):
        style_wind_ausschluss_gesamt(wind_ausschluss_landuse_layer)
        add_layer_to_group(
            project,
            validation_group_name,
            wind_ausschluss_landuse_layer,
            visible=False,
        )

    if layer_has_features(wind_ausschluss_osm_buffer_layer):
        style_wind_ausschluss_gesamt(wind_ausschluss_osm_buffer_layer)
        add_layer_to_group(
            project,
            validation_group_name,
            wind_ausschluss_osm_buffer_layer,
            visible=False,
        )

    add_optional_layers_to_group(
        project,
        "Detail- und Attributlayer Naturschutz hart",
        protection_hard_file,
        NATURSCHUTZ_HART_DETAIL_LAYERS,
        municipality_name,
    )
    add_optional_layers_to_group(
        project,
        "Detail- und Attributlayer Naturschutz weich",
        protection_weich_file,
        NATURSCHUTZ_WEICH_DETAIL_LAYERS,
        municipality_name,
    )
    add_optional_layers_to_group(
        project,
        "Detail- und Attributlayer Naturschutz Wind",
        protection_wind_file,
        NATURSCHUTZ_WIND_DETAIL_LAYERS,
        municipality_name,
    )

    wind_osm_context_file = WIND_DIR / f"{safe_name}_osm_wind_streets.gpkg"
    wind_osm_context_layer = load_optional_vector_layer(
        wind_osm_context_file,
        osm_wind_ausschluss_layer_name(),
        f"Straßen und Wege {municipality_name}",
    )

    if layer_has_features(wind_osm_context_layer):
        style_wind_osm_context_lines(wind_osm_context_layer)
        project.addMapLayer(wind_osm_context_layer)

    # Empty optional layers stay in the GeoPackage for a stable data structure,
    # but are skipped in the QGIS project to avoid visual clutter.
    if layer_has_features(vorbehalt_layer):
        style_wind_vorbehalt(vorbehalt_layer)
        project.addMapLayer(vorbehalt_layer)

    project.addMapLayer(vorrang_layer)
    project.addMapLayer(boundary_layer)

    set_project_extent_from_boundary(project, boundary_layer)

    if layer_has_features(naturschutz_weich_layer):
        move_layer_to_top(project, naturschutz_weich_layer)
    if layer_has_features(vorbehalt_layer):
        move_layer_to_top(project, vorbehalt_layer)
    move_layer_to_top(project, vorrang_layer)
    if layer_has_features(wind_ausschluss_layer):
        move_layer_to_top(project, wind_ausschluss_layer)
    if layer_has_features(wind_osm_context_layer):
        move_layer_to_top(project, wind_osm_context_layer)
    if layer_has_features(naturschutz_wind_layer):
        move_layer_to_top(project, naturschutz_wind_layer)
    if layer_has_features(naturschutz_hart_layer):
        move_layer_to_top(project, naturschutz_hart_layer)
    move_layer_to_top(project, boundary_layer)

    project.write(str(output_file))
    print(f"QGIS map project created: {display_path(output_file)}")


# =============================================================================
# Solar workflow
# =============================================================================
def create_solar_map_project(municipality_name: str) -> None:
    """Create a QGIS project for the solar workflow."""

    safe_name = safe_filename(municipality_name)

    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    solar_file = SOLAR_DIR / f"{safe_name}_solar_layers.gpkg"
    solar_landuse_file = SOLAR_DIR / solar_landuse_ausschluss_file_name(municipality_name)
    solar_pv_naehung_file = (
        SOLAR_DIR / solar_pv_freiflaechen_naehung_file_name(municipality_name)
    )
    protection_hard_file = PROTECTION_DIR / naturschutz_hart_file_name(municipality_name)
    protection_weich_file = PROTECTION_DIR / naturschutz_weich_file_name(municipality_name)
    solar_reference_zoom_1 = (
        SOLAR_REFERENCE_DIR / solar_reference_raster_name(municipality_name, 1)
    )
    solar_reference_zoom_2 = (
        SOLAR_REFERENCE_DIR / solar_reference_raster_name(municipality_name, 2)
    )
    output_file = OUTPUT_DIR / qgis_project_file_name(municipality_name, "solar")

    require_file(boundary_file, "Boundary file not found. Run script 2 first")
    require_file(
        solar_file,
        "Solar layer file not found. Run the solar prepare-data workflow first",
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    project = create_empty_project()

    # -------------------------------------------------------------------------
    # Official solar reference rasters
    # These locally downloaded WMS images are visual comparison layers from
    # the Energie-Atlas Bayern and do not replace the vector analysis layers.
    # -------------------------------------------------------------------------
    # Die amtlichen Solar-Referenzlayer werden als lokale Raster geladen.
    # damit die manuelle Registrierung in QGIS nicht jedes Mal nötig ist.
    solar_wms_zoom_2 = load_optional_raster_layer(
        solar_reference_zoom_2,
        "PV-Freiflächenkulisse Zoomstufe 2",
    )
    solar_wms_zoom_1 = load_optional_raster_layer(
        solar_reference_zoom_1,
        "PV-Freiflächenkulisse Zoomstufe 1",
    )

    # -------------------------------------------------------------------------
    # Solar analysis layers
    # EEG 500 m, BauGB 200 m and the shared transport axis layer from the
    # solar prepare workflow.
    # -------------------------------------------------------------------------
    eeg_layer = load_vector_layer(
        solar_file,
        solar_eeg_layer_name(municipality_name),
        f"PV Förderkulisse 500 m {municipality_name}",
    )
    baugb_layer = load_vector_layer(
        solar_file,
        solar_baugb_layer_name(municipality_name),
        f"PV Privilegierung 200 m {municipality_name}",
    )
    transport_layer = load_optional_vector_layer(
        solar_file,
        solar_transport_axis_layer_name(municipality_name),
        f"Autobahnen und Schienenwege {municipality_name}",
    )

    # -------------------------------------------------------------------------
    # General protection layers
    # Shared hard and soft protection areas are reused in the solar map as
    # contextual restriction layers.
    # -------------------------------------------------------------------------
    naturschutz_hart_layer = load_optional_vector_layer(
        protection_hard_file,
        naturschutz_hart_layer_name(),
        f"Harte Naturschutz-Restriktionen {municipality_name}",
    )
    naturschutz_weich_layer = load_optional_vector_layer(
        protection_weich_file,
        naturschutz_weich_layer_name(),
        f"Weiche Naturschutz-Konfliktflächen {municipality_name}",
    )

    # -------------------------------------------------------------------------
    # Administrative boundary
    # The municipality outline frames all solar reference and analysis layers.
    # -------------------------------------------------------------------------
    boundary_layer = QgsVectorLayer(str(boundary_file), municipality_name, "ogr")

    if not boundary_layer.isValid():
        raise RuntimeError(f"Boundary layer could not be loaded: {boundary_file}")

    style_solar_eeg(eeg_layer)
    style_solar_baugb(baugb_layer)
    style_boundary(boundary_layer)

    if layer_has_features(naturschutz_weich_layer):
        style_naturschutz_weich(naturschutz_weich_layer)
        project.addMapLayer(naturschutz_weich_layer)

    if layer_has_features(naturschutz_hart_layer):
        style_naturschutz_hart(naturschutz_hart_layer)
        project.addMapLayer(naturschutz_hart_layer)

    add_optional_layers_to_group(
        project,
        "Detail- und Attributlayer Naturschutz hart",
        protection_hard_file,
        NATURSCHUTZ_HART_DETAIL_LAYERS,
        municipality_name,
    )
    add_optional_layers_to_group(
        project,
        "Detail- und Attributlayer Naturschutz weich",
        protection_weich_file,
        NATURSCHUTZ_WEICH_DETAIL_LAYERS,
        municipality_name,
    )
    add_optional_layers_to_group(
        project,
        "Detail- und Attributlayer Solar-Landnutzung",
        solar_landuse_file,
        [solar_landuse_ausschluss_layer_name()],
        municipality_name,
    )
    add_optional_layers_to_group(
        project,
        "Detail- und Attributlayer Solar-Landnutzung",
        solar_pv_naehung_file,
        [solar_pv_freiflaechen_naehung_layer_name()],
        municipality_name,
    )

    if solar_wms_zoom_2 is not None:
        project.addMapLayer(solar_wms_zoom_2)
    if solar_wms_zoom_1 is not None:
        project.addMapLayer(solar_wms_zoom_1)
    project.addMapLayer(eeg_layer)
    project.addMapLayer(baugb_layer)

    if layer_has_features(transport_layer):
        style_solar_transport_axes(transport_layer)
        project.addMapLayer(transport_layer)

    project.addMapLayer(boundary_layer)

    set_project_extent_from_boundary(project, boundary_layer)

    if layer_has_features(naturschutz_hart_layer):
        move_layer_to_top(project, naturschutz_hart_layer)
    if layer_has_features(naturschutz_weich_layer):
        move_layer_to_top(project, naturschutz_weich_layer)
    move_layer_to_top(project, eeg_layer)
    move_layer_to_top(project, baugb_layer)
    if layer_has_features(transport_layer):
        move_layer_to_top(project, transport_layer)
    move_layer_to_top(project, boundary_layer)

    project.write(str(output_file))
    print(f"QGIS map project created: {display_path(output_file)}")

# =============================================================================
# Wasser workflow
# =============================================================================
def create_wasser_map_project(municipality_name: str) -> None:
    """Create a QGIS project for the water workflow."""

    safe_name = safe_filename(municipality_name)

    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    protection_hard_file = PROTECTION_DIR / naturschutz_hart_file_name(municipality_name)
    protection_weich_file = PROTECTION_DIR / naturschutz_weich_file_name(municipality_name)
    wasser_protection_file = WASSER_DIR / wasserschutz_hart_file_name(municipality_name)

    output_file = OUTPUT_DIR / qgis_project_file_name(municipality_name, "wasser")

    require_file(boundary_file, "Boundary file not found. Run script 2 first")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    project = create_empty_project()

    # -------------------------------------------------------------------------
    # Water WMS reference rasters
    # -------------------------------------------------------------------------
    water_reference_rasters = [
        (
            WASSER_REFERENCE_DIR / f"{safe_name}_wasserkraftanlagen.png",
            f"Wasserkraftanlagen {municipality_name}",
        ),
        (
            WASSER_REFERENCE_DIR / f"{safe_name}_neubaupotenzial_querbauwerke.png",
            f"Neubaupotenzial Querbauwerke {municipality_name}",
        ),
        (
            WASSER_REFERENCE_DIR / f"{safe_name}_modernisierung_nachruestung.png",
            f"Modernisierungs- und Nachrüstungspotenzial {municipality_name}",
        ),
        (
            WASSER_REFERENCE_DIR / f"{safe_name}_ueberschwemmungsgebiete_festgesetzt_hart.png",
            f"Festgesetzte Überschwemmungsgebiete {municipality_name}",
        ),
        (
            WASSER_REFERENCE_DIR / f"{safe_name}_ueberschwemmungsgebiete_vorlaeufig_hart.png",
            f"Vorläufig gesicherte Überschwemmungsgebiete {municipality_name}",
        ),
        (
            WASSER_REFERENCE_DIR / f"{safe_name}_hochwassergefahren_hq100_weich.png",
            f"Hochwassergefahren HQ100 {municipality_name}",
        ),
        (
            WASSER_REFERENCE_DIR / f"{safe_name}_hochwassergefahren_hqextrem_weich.png",
            f"Hochwassergefahren HQextrem {municipality_name}",
        ),
    ]

    # -------------------------------------------------------------------------
    # General protection layers
    # -------------------------------------------------------------------------
    naturschutz_hart_layer = load_optional_vector_layer(
        protection_hard_file,
        naturschutz_hart_layer_name(),
        f"Harte Naturschutz-Restriktionen {municipality_name}",
    )
    naturschutz_weich_layer = load_optional_vector_layer(
        protection_weich_file,
        naturschutz_weich_layer_name(),
        f"Weiche Naturschutz-Konfliktflächen {municipality_name}",
    )
    wasserschutz_hart_layer = load_optional_vector_layer(
        wasser_protection_file,
        wasserschutz_hart_layer_name(),
        f"Wasserschutz hart {municipality_name}",
    )

    boundary_layer = QgsVectorLayer(str(boundary_file), municipality_name, "ogr")

    if not boundary_layer.isValid():
        raise RuntimeError(f"Boundary layer could not be loaded: {boundary_file}")

    style_boundary(boundary_layer)

    # Protection layers first
    if layer_has_features(naturschutz_weich_layer):
        style_naturschutz_weich(naturschutz_weich_layer)
        project.addMapLayer(naturschutz_weich_layer)

    if layer_has_features(naturschutz_hart_layer):
        style_naturschutz_hart(naturschutz_hart_layer)
        project.addMapLayer(naturschutz_hart_layer)

    if layer_has_features(wasserschutz_hart_layer):
        style_wasserschutz_hart(wasserschutz_hart_layer)
        project.addMapLayer(wasserschutz_hart_layer)

    add_optional_layers_to_group(
        project,
        "Detail- und Attributlayer Naturschutz hart",
        protection_hard_file,
        NATURSCHUTZ_HART_DETAIL_LAYERS,
        municipality_name,
    )
    add_optional_layers_to_group(
        project,
        "Detail- und Attributlayer Naturschutz weich",
        protection_weich_file,
        NATURSCHUTZ_WEICH_DETAIL_LAYERS,
        municipality_name,
    )
    add_optional_layers_to_group(
        project,
        "Detail- und Attributlayer Wasserschutz hart",
        wasser_protection_file,
        WASSERSCHUTZ_HART_DETAIL_LAYERS,
        municipality_name,
    )

    # WMS rasters
    for raster_file, display_name in water_reference_rasters:
        raster_layer = load_optional_raster_layer(raster_file, display_name)

        if raster_layer is not None:
            project.addMapLayer(raster_layer)

    project.addMapLayer(boundary_layer)

    set_project_extent_from_boundary(project, boundary_layer)

    if layer_has_features(naturschutz_weich_layer):
        move_layer_to_top(project, naturschutz_weich_layer)
    if layer_has_features(naturschutz_hart_layer):
        move_layer_to_top(project, naturschutz_hart_layer)
    if layer_has_features(wasserschutz_hart_layer):
        move_layer_to_top(project, wasserschutz_hart_layer)

    move_layer_to_top(project, boundary_layer)

    project.write(str(output_file))
    print(f"QGIS map project created: {display_path(output_file)}")


# =============================================================================
# Main entry point
# =============================================================================
def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = ColoredArgumentParser(
        description="Create a QGIS map project for one municipality."
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
        help="Energy technology used for the layer setup.",
    )

    return parser.parse_args()


def main() -> None:
    """Create the requested technology project."""

    args = parse_arguments()

    match args.technology:
        case "wind":
            create_wind_map_project(args.municipality)
        case "solar":
            create_solar_map_project(args.municipality)
        case "wasser":
            create_wasser_map_project(args.municipality)
        case _:
            raise SystemExit(
                f"Map script 1 currently supports only wind and solar, not: {args.technology}"
            )


# =============================================================================
# QGIS application bootstrap
# =============================================================================
if __name__ == "__main__":
    qgs = QgsApplication([], False)
    qgs.initQgis()

    try:
        main()
    finally:
        qgs.exitQgis()
