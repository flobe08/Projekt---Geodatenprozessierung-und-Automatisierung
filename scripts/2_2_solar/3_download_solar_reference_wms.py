"""
Script 3: Download solar WMS reference rasters for one municipality.

Workflow:
1. Read the municipality boundary from shared prepare-data script 2.
2. Build one municipality bounding box in EPSG:25832.
3. Request the official solar WMS layers for that bounding box.
4. Save the WMS images as georeferenced PNG reference rasters.
5. Keep these rasters as visual comparison layers in the QGIS project.
"""

from pathlib import Path
import argparse
import json
import math
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
from urllib.request import urlopen

from qgis.core import QgsApplication, QgsVectorLayer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "utils"))
from utils import ColoredArgumentParser, log_error, log_info, log_success, log_warning


BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =============================================================================
# 0. Input and output paths
# =============================================================================
# input
BOUNDARY_DIR = BASE_DIR / "data/processed/1_base_boundaries"

# output
OUTPUT_DIR = BASE_DIR / "data/processed/2_technology_solar/reference"

WMS_BASE_URL = "https://www.lfu.bayern.de/gdi/wms/energieatlas/planungsgrundlagen_solar"
WMS_VERSION = "1.3.0"
WMS_CRS = "EPSG:25832"

WMS_LAYERS = {
    "pv_freiflaechenkulisse_zoomstufe_1": "PV-Freiflächenkulisse - Zoomstufe 1",
    "pv_freiflaechenkulisse_zoomstufe_2": "PV-Freiflächenkulisse - Zoomstufe 2",
}


# =============================================================================
# Helper functions
# =============================================================================
def safe_filename(name: str) -> str:
    """Create the same filename format as the other scripts."""

    return name.lower().replace(" ", "_")


def display_path(path: Path) -> str:
    """Return a compact path for log messages."""

    try:
        return str(path.resolve().relative_to(BASE_DIR))
    except ValueError:
        return str(path)


def remove_old_outputs(base_path: Path) -> None:
    """Remove older PNG, world file and PRJ outputs for the same layer base name."""

    for suffix in [".png", ".pgw", ".prj", ".json"]:
        output_file = base_path.with_suffix(suffix)

        if not output_file.exists():
            continue

        try:
            output_file.unlink()
        except PermissionError as error:
            log_error("One solar WMS reference file is locked and cannot be overwritten.")
            log_error(f"Locked file: {display_path(output_file)}")
            log_info("Close the file in QGIS and run the script again.")
            raise SystemExit(
                "Solar script 2 stopped because a WMS reference output file is still open."
            ) from error


def calculate_image_size(bounds: tuple[float, float, float, float]) -> tuple[int, int]:
    """Choose a stable WMS image size from the municipality bounding box."""

    minx, miny, maxx, maxy = bounds
    width_m = maxx - minx
    height_m = maxy - miny

    if width_m <= 0 or height_m <= 0:
        return 1200, 1200

    max_pixels = 1800

    if width_m >= height_m:
        width_px = max_pixels
        height_px = max(600, int(math.ceil(max_pixels * (height_m / width_m))))
    else:
        height_px = max_pixels
        width_px = max(600, int(math.ceil(max_pixels * (width_m / height_m))))

    return width_px, height_px


def build_wms_params(
    layer_name: str,
    bounds: tuple[float, float, float, float],
    width_px: int,
    height_px: int,
) -> dict:
    """Build one WMS GetMap request."""

    minx, miny, maxx, maxy = bounds

    return {
        "service": "WMS",
        "version": WMS_VERSION,
        "request": "GetMap",
        "layers": layer_name,
        "styles": "",
        "crs": WMS_CRS,
        "bbox": f"{minx},{miny},{maxx},{maxy}",
        "width": str(width_px),
        "height": str(height_px),
        "format": "image/png",
        "transparent": "TRUE",
    }


def fetch_wms_capabilities() -> bytes:
    """Request the WMS GetCapabilities document."""

    params = {
        "service": "WMS",
        "request": "GetCapabilities",
        "version": WMS_VERSION,
    }
    request_url = f"{WMS_BASE_URL}?{urlencode(params)}"

    with urlopen(request_url, timeout=180) as response:
        return response.read()


def local_tag_name(tag: str) -> str:
    """Return one XML tag name without namespace prefix."""

    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def resolve_wms_layer_name(layer_title: str) -> str:
    """Resolve a visible WMS layer title to the internal service layer name."""

    capabilities_xml = fetch_wms_capabilities()
    root = ET.fromstring(capabilities_xml)

    for layer in root.iter():
        if local_tag_name(layer.tag) != "Layer":
            continue

        layer_name = None
        layer_title_value = None

        for child in layer:
            child_name = local_tag_name(child.tag)

            if child_name == "Name" and child.text:
                layer_name = child.text.strip()
            elif child_name == "Title" and child.text:
                layer_title_value = child.text.strip()

        if layer_title_value == layer_title and layer_name:
            return layer_name

    raise RuntimeError(
        f"Could not resolve WMS layer title to an internal layer name: {layer_title}"
    )


def read_boundary_extent(boundary_file: Path) -> tuple[tuple[float, float, float, float], str]:
    """Read the municipality bounding box and CRS WKT with QGIS only."""

    boundary_layer = QgsVectorLayer(str(boundary_file), "boundary", "ogr")

    if not boundary_layer.isValid():
        raise RuntimeError(
            f"Boundary layer could not be loaded: {display_path(boundary_file)}"
        )

    extent = boundary_layer.extent()
    bounds = (extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum())
    crs_wkt = boundary_layer.crs().toWkt()
    return bounds, crs_wkt


def download_wms_image(
    layer_title: str,
    bounds: tuple[float, float, float, float],
) -> tuple[bytes, int, int]:
    """Download one WMS map image for the municipality bounding box."""

    width_px, height_px = calculate_image_size(bounds)
    service_layer_name = resolve_wms_layer_name(layer_title)
    log_info(f"Interner WMS-Layername: {service_layer_name}")
    params = build_wms_params(service_layer_name, bounds, width_px, height_px)

    request_url = f"{WMS_BASE_URL}?{urlencode(params)}"

    with urlopen(request_url, timeout=180) as response:
        content_type = response.headers.get("Content-Type", "")
        image_bytes = response.read()

    if "image" not in content_type.lower():
        preview = image_bytes[:500].decode("utf-8", errors="replace")
        log_error(f"WMS response for layer '{layer_title}' is not an image.")
        log_error(preview)
        raise RuntimeError(f"WMS GetMap did not return an image for layer: {layer_title}")

    return image_bytes, width_px, height_px


def write_world_file(
    world_file: Path,
    bounds: tuple[float, float, float, float],
    width_px: int,
    height_px: int,
) -> None:
    """Write the PNG world file so QGIS can place the raster correctly."""

    minx, miny, maxx, maxy = bounds
    pixel_size_x = (maxx - minx) / width_px
    pixel_size_y = -((maxy - miny) / height_px)
    upper_left_center_x = minx + (pixel_size_x / 2)
    upper_left_center_y = maxy + (pixel_size_y / 2)

    world_file.write_text(
        "\n".join(
            [
                str(pixel_size_x),
                "0.0",
                "0.0",
                str(pixel_size_y),
                str(upper_left_center_x),
                str(upper_left_center_y),
            ]
        ),
        encoding="utf-8",
    )


def write_prj_file(prj_file: Path, crs_wkt: str) -> None:
    """Write a matching CRS file next to the PNG world file."""

    prj_file.write_text(crs_wkt, encoding="utf-8")


def metadata_output_name(municipality_name: str) -> str:
    """Create the metadata file name for one municipality."""

    return f"{safe_filename(municipality_name)}_solar_wms_reference"


# =============================================================================
# 1. Download WMS reference rasters for one municipality
# =============================================================================
def download_solar_reference_wms(municipality_name: str) -> None:
    """Download official solar WMS layers as georeferenced municipality rasters."""

    safe_name = safe_filename(municipality_name)
    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"

    if not boundary_file.exists():
        raise FileNotFoundError(
            f"Boundary file not found: {boundary_file}. Run script 2 first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    bounds, boundary_crs_wkt = read_boundary_extent(boundary_file)

    log_info(f"Downloading solar WMS reference layers for: {municipality_name}")
    log_info(f"Boundary: {display_path(boundary_file)}")
    log_info(f"Output directory: {display_path(OUTPUT_DIR)}")
    log_info("Hinweis: Der WMS wird auf die Bounding-Box der Gemeinde geladen.")
    log_info("Der exakte harte Zuschnitt an der Gemeindegrenze bleibt ein visueller Vergleichslayer.")

    metadata = {
        "municipality": municipality_name,
        "boundary_file": display_path(boundary_file),
        "wms_url": WMS_BASE_URL,
        "wms_version": WMS_VERSION,
        "crs": WMS_CRS,
        "bbox_25832": list(bounds),
        "layers": [],
        "note": (
            "Die Referenzbilder sind WMS-Raster im Ausschnitt der Gemeinde-Bounding-Box. "
            "Sie dienen als visueller Vergleich vor den Pufferschritten und sind "
            "kein bearbeitbarer Vektor-Datensatz."
        ),
    }

    for output_stub, wms_layer_name in WMS_LAYERS.items():
        base_path = OUTPUT_DIR / f"{safe_name}_{output_stub}"
        remove_old_outputs(base_path)

        log_info(f"WMS-Layer: {wms_layer_name}")
        image_bytes, width_px, height_px = download_wms_image(wms_layer_name, bounds)

        png_file = base_path.with_suffix(".png")
        world_file = base_path.with_suffix(".pgw")
        prj_file = base_path.with_suffix(".prj")

        png_file.write_bytes(image_bytes)
        write_world_file(world_file, bounds, width_px, height_px)
        write_prj_file(prj_file, boundary_crs_wkt)

        metadata["layers"].append(
            {
                "wms_layer_name": wms_layer_name,
                "png_file": display_path(png_file),
                "world_file": display_path(world_file),
                "prj_file": display_path(prj_file),
                "width_px": width_px,
                "height_px": height_px,
            }
        )

        log_success(f"Written WMS reference raster: {display_path(png_file)}")

    metadata_file = OUTPUT_DIR / f"{metadata_output_name(municipality_name)}.json"
    remove_old_outputs(metadata_file.with_suffix(""))
    metadata_file.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    log_success("Solar WMS reference download finished.")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = ColoredArgumentParser(
        description="Download official solar WMS reference rasters for one municipality."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    return parser.parse_args()


def main() -> None:
    """Run the WMS reference download for one municipality."""

    args = parse_arguments()
    download_solar_reference_wms(args.municipality)


if __name__ == "__main__":
    qgs = QgsApplication([], False)
    qgs.initQgis()

    try:
        main()
    finally:
        qgs.exitQgis()
