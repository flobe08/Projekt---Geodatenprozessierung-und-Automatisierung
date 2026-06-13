"""
Script 4: Create a QGIS map project.

Workflow:
1. Load an OpenStreetMap web basemap.
2. Load the official municipality boundary from script 1.
3. Load the clipped wind vorrang and vorbehalt layers from script 3.
4. Optionally load clipped OSM context roads from script 4.
5. Save everything as a QGIS project for manual map layout work.
"""

from pathlib import Path
import argparse
import sys

from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsFillSymbol,
    QgsLineSymbol,
    QgsLayerTreeLayer,
    QgsProject,
    QgsReferencedRectangle,
    QgsRasterLayer,
    QgsVectorLayer,
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "scripts/utils"))

from utils import ColoredArgumentParser


BOUNDARY_DIR = BASE_DIR / "data/processed/boundaries"
WIND_DIR = BASE_DIR / "data/processed/wind"
OSM_CONTEXT_DIR = BASE_DIR / "data/processed/osm_context"
OUTPUT_DIR = BASE_DIR / "data/processed/qgis_projects"


def safe_filename(name: str) -> str:
    """Create a safe file name from a municipality name."""

    return name.lower().replace(" ", "_")


def vorrang_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for wind vorrang areas."""

    return f"wind_vorranggebiete_{safe_filename(municipality_name)}"


def vorbehalt_layer_name(municipality_name: str) -> str:
    """Create the municipality-specific layer name for wind vorbehalt areas."""

    return f"wind_vorbehaltsgebiete_{safe_filename(municipality_name)}"


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


def style_boundary(layer: QgsVectorLayer) -> None:
    """Style the municipality boundary with transparent fill and red outline."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "255,0,0,0",
            "outline_color": "255,0,0,255",
            "outline_width": "0.4",
        }
    )
    layer.renderer().setSymbol(symbol)


def style_wind_vorrang(layer: QgsVectorLayer) -> None:
    """Style wind vorrang areas with an opaque blue fill."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "31,60,160,180",
            "outline_color": "18,40,120,255",
            "outline_width": "0.15",
        }
    )
    layer.renderer().setSymbol(symbol)


def style_wind_vorbehalt(layer: QgsVectorLayer) -> None:
    """Style wind vorbehalt areas with a yellow fill."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "232,177,35,190",
            "outline_color": "168,124,10,255",
            "outline_width": "0.15",
        }
    )
    layer.renderer().setSymbol(symbol)


def style_osm_context(layer: QgsVectorLayer) -> None:
    """Style optional OSM context roads with an orange line."""

    symbol = QgsLineSymbol.createSimple(
        {
            "color": "255,170,0,255",
            "width": "0.35",
        }
    )
    layer.renderer().setSymbol(symbol)


def create_wind_map_project(municipality_name: str) -> None:
    """Create a QGIS project for the wind workflow."""

    safe_name = safe_filename(municipality_name)

    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    wind_file = WIND_DIR / f"{safe_name}_wind_layers.gpkg"
    osm_context_file = OSM_CONTEXT_DIR / f"{safe_name}_osm_context.gpkg"
    output_file = OUTPUT_DIR / f"{safe_name}_map.qgz"

    require_file(boundary_file, "Boundary file not found. Run script 1 first")
    require_file(wind_file, "Wind planning file not found. Run script 3 first")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    project = QgsProject.instance()
    project.clear()
    project.setCrs(QgsCoordinateReferenceSystem("EPSG:25832"))

    osm_url = "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    osm_layer = QgsRasterLayer(osm_url, "OSM Standard", "wms")

    if not osm_layer.isValid():
        raise RuntimeError("OSM Standard layer could not be loaded.")

    project.addMapLayer(osm_layer)

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
    boundary_layer = QgsVectorLayer(str(boundary_file), municipality_name, "ogr")

    if not boundary_layer.isValid():
        raise RuntimeError(f"Boundary layer could not be loaded: {boundary_file}")

    style_wind_vorrang(vorrang_layer)
    style_boundary(boundary_layer)

    project.addMapLayer(vorrang_layer)
    # Empty optional layers are kept in the GeoPackage for a stable output
    # structure, but they are skipped in the QGIS project to avoid styling
    # issues and visual clutter.
    if layer_has_features(vorbehalt_layer):
        style_wind_vorbehalt(vorbehalt_layer)
        project.addMapLayer(vorbehalt_layer)
    project.addMapLayer(boundary_layer)

    if osm_context_file.exists():
        osm_context_layer = load_vector_layer(
            osm_context_file,
            "osm_context_roads",
            "OSM Context Roads",
        )
        style_osm_context(osm_context_layer)
        project.addMapLayer(osm_context_layer)
        move_layer_to_top(project, osm_context_layer)

    extent = boundary_layer.extent()
    extent.scale(1.15)
    project.viewSettings().setDefaultViewExtent(
        QgsReferencedRectangle(extent, boundary_layer.crs())
    )

    if layer_has_features(vorbehalt_layer):
        move_layer_to_top(project, vorbehalt_layer)
    move_layer_to_top(project, vorrang_layer)
    move_layer_to_top(project, boundary_layer)

    project.write(str(output_file))
    print(f"QGIS map project created: {display_path(output_file)}")


def main() -> None:
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
        case _:
            raise SystemExit(
                f"Script 4 currently supports only the wind workflow, not: {args.technology}"
            )


if __name__ == "__main__":
    qgs = QgsApplication([], False)
    qgs.initQgis()

    try:
        main()
    finally:
        qgs.exitQgis()
