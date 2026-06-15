"""
Script 1: Create a QGIS map project.

Workflow:
1. Load an OpenStreetMap web basemap.
2. Load the official municipality boundary from script 2.
3. Load the prepared technology layers for the selected workflow.
4. Apply basic symbology for QGIS inspection and PDF export.
5. Save everything as a QGIS project for manual map layout work.
"""

from pathlib import Path
import sys

from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsFillSymbol,
    QgsLayerTreeLayer,
    QgsLineSymbol,
    QgsProject,
    QgsRasterLayer,
    QgsReferencedRectangle,
    QgsSingleSymbolRenderer,
    QgsVectorLayer,
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "scripts/utils"))

from utils import ColoredArgumentParser, log_warning


# =============================================================================
# General paths
# =============================================================================
BOUNDARY_DIR = BASE_DIR / "data/processed/boundaries"
WIND_DIR = BASE_DIR / "data/processed/wind"
PROTECTION_DIR = BASE_DIR / "data/processed/schutzgebiete"
SOLAR_DIR = BASE_DIR / "data/processed/solar"
SOLAR_REFERENCE_DIR = BASE_DIR / "data/processed/solar_reference"
OUTPUT_DIR = BASE_DIR / "data/processed/qgis_projects"

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


def solar_transport_axis_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for the 500 m solar transport basis."""

    return f"pv_verkehrsachsen_500m_{safe_filename(municipality_name)}"


def solar_eeg_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for the 500 m EEG buffer."""

    return f"pv_förderkulisse_500m_{safe_filename(municipality_name)}"


def solar_baugb_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for the 200 m BauGB buffer."""

    return f"pv_privilegierung_200m_{safe_filename(municipality_name)}"


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


def load_optional_raster_layer(
    raster_file: Path,
    display_name: str,
) -> QgsRasterLayer | None:
    """Load one optional local solar reference raster for the QGIS project."""

    if not raster_file.exists():
        log_warning(f"Solar reference raster not found: {display_path(raster_file)}")
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


def apply_symbol(layer: QgsVectorLayer, symbol: QgsFillSymbol | QgsLineSymbol) -> None:
    """Apply one symbol safely, even if QGIS did not create a default renderer."""

    renderer = layer.renderer()

    if renderer is None:
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        return

    renderer.setSymbol(symbol)


# =============================================================================
# General styling
# =============================================================================
def style_boundary(layer: QgsVectorLayer) -> None:
    """Style the municipality boundary with transparent fill and red outline."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "255,0,0,0",
            "outline_color": "255,0,0,255",
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
    """Style hard protection areas with a red hatch pattern."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "255,0,0,255",
            "outline_color": "255,0,0,255",
            "outline_width": "0.18",
            "style": "b_diagonal",
        }
    )
    apply_symbol(layer, symbol)


def style_naturschutz_weich(layer: QgsVectorLayer) -> None:
    """Style soft protection areas so they stay visible on top of the basemap."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "230,155,52,255",
            "outline_color": "190,120,20,255",
            "outline_width": "0.16",
            "style": "f_diagonal",
        }
    )
    apply_symbol(layer, symbol)


def style_naturschutz_wind(layer: QgsVectorLayer) -> None:
    """Style wind-specific protection areas with an orange hatch pattern."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "232,136,20,255",
            "outline_color": "196,108,0,255",
            "outline_width": "0.14",
            "style": "f_diagonal",
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
    output_file = OUTPUT_DIR / qgis_project_file_name(municipality_name, "wind")

    require_file(boundary_file, "Boundary file not found. Run script 2 first")
    require_file(wind_file, "Wind planning file not found. Run wind script 1 first")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    project = create_empty_project()

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

    # Empty optional layers stay in the GeoPackage for a stable data structure,
    # but are skipped in the QGIS project to avoid visual clutter.
    if layer_has_features(vorbehalt_layer):
        style_wind_vorbehalt(vorbehalt_layer)
        project.addMapLayer(vorbehalt_layer)

    project.addMapLayer(vorrang_layer)
    project.addMapLayer(boundary_layer)

    set_project_extent_from_boundary(project, boundary_layer)

    if layer_has_features(naturschutz_hart_layer):
        move_layer_to_top(project, naturschutz_hart_layer)
    if layer_has_features(naturschutz_weich_layer):
        move_layer_to_top(project, naturschutz_weich_layer)
    if layer_has_features(naturschutz_wind_layer):
        move_layer_to_top(project, naturschutz_wind_layer)
    if layer_has_features(vorbehalt_layer):
        move_layer_to_top(project, vorbehalt_layer)
    move_layer_to_top(project, vorrang_layer)
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
    boundary_layer = QgsVectorLayer(str(boundary_file), municipality_name, "ogr")

    if not boundary_layer.isValid():
        raise RuntimeError(f"Boundary layer could not be loaded: {boundary_file}")

    style_solar_eeg(eeg_layer)
    style_solar_baugb(baugb_layer)
    style_boundary(boundary_layer)

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

    move_layer_to_top(project, eeg_layer)
    move_layer_to_top(project, baugb_layer)
    if layer_has_features(transport_layer):
        move_layer_to_top(project, transport_layer)
    move_layer_to_top(project, boundary_layer)

    project.write(str(output_file))
    print(f"QGIS map project created: {display_path(output_file)}")


# =============================================================================
# Main entry point
# =============================================================================
def main() -> None:
    """Parse CLI arguments and create the requested technology project."""

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

    args = parser.parse_args()

    match args.technology:
        case "wind":
            create_wind_map_project(args.municipality)
        case "solar":
            create_solar_map_project(args.municipality)
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
