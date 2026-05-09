"""
Script 4: Create a QGIS map project.

Workflow:
1. Load an OpenStreetMap web basemap.
2. Load the official municipality boundary from script 1.
3. Load the clipped OSM highway data from script 2.
4. Load the clipped official landuse data from script 3.
5. Save everything as a QGIS project for manual map layout work.
"""

from pathlib import Path
import argparse
import sys

# PyQGIS imports. Main references: Python apps, layer loading, symbology and CRS.
# (Docs: 1.4, 3, 3.2, 3.3, 6.8, 8)
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


# -----------------------------------------------------------------------------
# 0. Configuration: input and output paths
# -----------------------------------------------------------------------------
BOUNDARY_DIR = BASE_DIR / "data/processed/boundaries"
OSM_HIGHWAYS_DIR = BASE_DIR / "data/processed/osm_highways"
LANDUSE_DIR = BASE_DIR / "data/processed/landuse"
OUTPUT_DIR = BASE_DIR / "data/processed/qgis_projects"


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
def safe_filename(name: str) -> str:
    """Create a safe file name from a municipality name."""

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


def load_vector_layer(path: Path, layer_name: str, display_name: str) -> QgsVectorLayer:
    """Load one GeoPackage layer as a QGIS vector layer."""

    uri = f"{path}|layername={layer_name}"
    layer = QgsVectorLayer(uri, display_name, "ogr")

    if not layer.isValid():
        raise RuntimeError(f"Layer could not be loaded: {display_name}")

    return layer


def move_layer_to_top(project: QgsProject, layer: QgsVectorLayer) -> None:
    """Move a layer to the top of the QGIS layer tree."""

    root = project.layerTreeRoot()
    layer_node = root.findLayer(layer.id())

    if isinstance(layer_node, QgsLayerTreeLayer):
        clone = layer_node.clone()
        parent = layer_node.parent()
        parent.insertChildNode(0, clone)
        parent.removeChildNode(layer_node)


# -----------------------------------------------------------------------------
# 1. Style map layers
# -----------------------------------------------------------------------------
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


def style_landuse(layer: QgsVectorLayer) -> None:
    """Style official landuse with an opaque blue-gray fill."""

    symbol = QgsFillSymbol.createSimple(
        {
            "color": "92,118,145,255",
            "outline_color": "50,70,95,255",
            "outline_width": "0.15",
        }
    )
    layer.renderer().setSymbol(symbol)


def style_osm_highways(layer: QgsVectorLayer) -> None:
    """Style OSM highway lines with a visible orange line."""

    symbol = QgsLineSymbol.createSimple(
        {
            "color": "255,170,0,255",
            "width": "0.35",
        }
    )
    layer.renderer().setSymbol(symbol)


# -----------------------------------------------------------------------------
# 2. Create QGIS project for one municipality
# -----------------------------------------------------------------------------
def create_map_project(municipality_name: str) -> None:
    """Create a QGIS project with basemap, boundary, OSM highways and landuse."""

    safe_name = safe_filename(municipality_name)

    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    osm_highways_file = OSM_HIGHWAYS_DIR / f"{safe_name}_osm_highways.gpkg"
    landuse_file = LANDUSE_DIR / f"landnutzung_{safe_name}.gpkg"
    output_file = OUTPUT_DIR / f"{safe_name}_map.qgz"

    require_file(boundary_file, "Boundary file not found. Run script 1 first")
    require_file(osm_highways_file, "OSM highway file not found. Run script 2 first")
    require_file(landuse_file, "Landuse file not found. Run script 3 first")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # A QGIS project stores map layers, CRS and project settings. (Doc: 3.3)
    project = QgsProject.instance()
    project.clear()

    # EPSG:25832 is suitable for metric distance analysis in Bavaria. (Doc: 8)
    project.setCrs(QgsCoordinateReferenceSystem("EPSG:25832"))

    # -------------------------------------------------------------------------
    # 2.1 Add OpenStreetMap web basemap
    # -------------------------------------------------------------------------
    # XYZ tiles are loaded as a raster layer. (Doc: 3.2)
    osm_url = "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    osm_layer = QgsRasterLayer(osm_url, "OSM Standard", "wms")

    if not osm_layer.isValid():
        raise RuntimeError("OSM Standard layer could not be loaded.")

    project.addMapLayer(osm_layer)

    # -------------------------------------------------------------------------
    # 2.2 Add processed vector layers
    # -------------------------------------------------------------------------
    # GeoPackage layers are loaded as vector layers. (Doc: 3)
    landuse_layer = load_vector_layer(landuse_file, "official_landuse", "Landnutzung")
    osm_highways_layer = load_vector_layer(osm_highways_file, "osm_roads", "OSM Highways")
    boundary_layer = QgsVectorLayer(str(boundary_file), municipality_name, "ogr")

    if not boundary_layer.isValid():
        raise RuntimeError(f"Boundary layer could not be loaded: {boundary_file}")

    style_landuse(landuse_layer)
    style_osm_highways(osm_highways_layer)
    style_boundary(boundary_layer)

    project.addMapLayer(landuse_layer)
    project.addMapLayer(osm_highways_layer)
    project.addMapLayer(boundary_layer)

    # -------------------------------------------------------------------------
    # 2.3 Set project extent and layer order
    # -------------------------------------------------------------------------
    extent = boundary_layer.extent()
    extent.scale(1.15)
    project.viewSettings().setDefaultViewExtent(
        QgsReferencedRectangle(extent, boundary_layer.crs())
    )

    move_layer_to_top(project, landuse_layer)
    move_layer_to_top(project, osm_highways_layer)
    move_layer_to_top(project, boundary_layer)

    # -------------------------------------------------------------------------
    # 2.4 Save QGIS project
    # -------------------------------------------------------------------------
    project.write(str(output_file))

    print(f"QGIS map project created: {display_path(output_file)}")


def main() -> None:
    parser = ColoredArgumentParser(
        description="Create a QGIS map project with OSM, boundary, highways and landuse."
    )

    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()
    create_map_project(args.municipality)


if __name__ == "__main__":

    # QgsApplication is required when PyQGIS is used outside the QGIS GUI. (Doc: 1.4)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    try:
        main()
    finally:
        qgs.exitQgis()
