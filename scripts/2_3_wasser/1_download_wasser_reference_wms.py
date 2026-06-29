"""
Download water-specific WMS reference rasters for one municipality.

The hydropower and flood-hazard services used here are WMS services. They are
therefore stored as georeferenced PNG reference rasters for QGIS exploration,
not as editable vector layers. Water protection areas are handled separately
from official SHP downloads in ``2_build_wasser_protection_layers.py``.
"""

from pathlib import Path
import argparse
import json
import math
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
from urllib.request import urlopen

from qgis.PyQt.QtGui import QImage
from qgis.core import QgsApplication, QgsVectorLayer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "utils"))
from utils import ColoredArgumentParser, log_error, log_info, log_success, log_warning


BASE_DIR = Path(__file__).resolve().parent.parent.parent

BOUNDARY_DIR = BASE_DIR / "data/processed/1_base_boundaries"
OUTPUT_DIR = BASE_DIR / "data/processed/2_technology_wasser/reference"
LEGEND_OUTPUT_DIR = OUTPUT_DIR / "legends"

WMS_VERSION = "1.3.0"
WMS_CRS = "EPSG:25832"

WMS_SERVICES = {
    "wasserkraft": {
        "url": "https://www.lfu.bayern.de/gdi/wms/energieatlas/wasserkraftanlagen",
        "layers": [
            {
                "name": "wasserkraftanlagen_zv04b14",
                "title": "Wasserkraftanlagen - Zoomstufen 4 bis 14 des Energie-Atlas Bayern",
                "stub": "wasserkraftanlagen",
                "role": "Bestandsanlagen",
                "pixel_scale": 0.38,
                "download_legend": True,
                "legend_icon_indices": [0, 4, 8],
            },
            {
                "name": "neubaupotenzial_querbauwerke",
                "title": "Neubaupotenzial an bestehenden Querbauwerken",
                "stub": "neubaupotenzial_querbauwerke",
                "role": "Potenzial an Querbauwerken",
                "pixel_scale": 0.38,
                "download_legend": True,
                "legend_icon_indices": [0, 2, 4],
            },
            {
                "name": "modernisierung_nachruestung",
                "title": "Modernisierungs- und Nachrüstungspotenzial",
                "stub": "modernisierung_nachruestung",
                "role": "Modernisierung und Nachrüstung",
                "pixel_scale": 0.38,
                "download_legend": True,
                "legend_icon_indices": [0, 1, 2],
            },
        ],
    },
    "ueberschwemmungsgebiete": {
        "url": "https://www.lfu.bayern.de/gdi/wms/wasser/ueberschwemmungsgebiete",
        "layers": [
            {
                "name": "festsetzung",
                "title": "Festgesetzte Überschwemmungsgebiete",
                "stub": "ueberschwemmungsgebiete_festgesetzt_hart",
                "role": "harte wasserrechtliche Restriktion",
            },
            {
                "name": "sicherung",
                "title": "Vorläufig gesicherte Überschwemmungsgebiete",
                "stub": "ueberschwemmungsgebiete_vorlaeufig_hart",
                "role": "harte wasserrechtliche Restriktion",
            },
            {
                "name": "hwgf_hq100",
                "title": "Hochwassergefahrenflächen HQ100",
                "stub": "hochwassergefahren_hq100_weich",
                "role": "weicher Hochwasser-Konfliktbereich",
            },
            {
                "name": "hwgf_hqextrem",
                "title": "Hochwassergefahrenflächen HQextrem",
                "stub": "hochwassergefahren_hqextrem_weich",
                "role": "weicher Hochwasser-Risikokontext",
            },
        ],
    },
}


def safe_filename(name: str) -> str:
    """Create the same filename format as the other scripts."""

    return name.lower().replace(" ", "_")


def display_path(path: Path) -> str:
    """Return a compact path for log messages."""

    try:
        return str(path.resolve().relative_to(BASE_DIR))
    except ValueError:
        return str(path)


def local_tag_name(tag: str) -> str:
    """Return one XML tag name without namespace prefix."""

    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def fetch_capabilities(service_url: str) -> ET.Element:
    """Fetch and parse one WMS capabilities document."""

    params = {
        "service": "WMS",
        "request": "GetCapabilities",
        "version": WMS_VERSION,
    }
    request_url = f"{service_url}?{urlencode(params)}"

    with urlopen(request_url, timeout=180) as response:
        return ET.fromstring(response.read())


def collect_service_layer_names(service_url: str) -> set[str]:
    """Return all named layers advertised by one WMS service."""

    root = fetch_capabilities(service_url)
    layer_names = set()

    for layer in root.iter():
        if local_tag_name(layer.tag) != "Layer":
            continue

        for child in layer:
            if local_tag_name(child.tag) == "Name" and child.text:
                layer_names.add(child.text.strip())

    return layer_names


def validate_layer_name(service_label: str, service_url: str, layer_name: str) -> None:
    """Ensure that a configured WMS layer still exists in the service."""

    layer_names = collect_service_layer_names(service_url)

    if layer_name not in layer_names:
        raise RuntimeError(
            f"WMS layer not found in {service_label}: {layer_name}. "
            f"Available layers: {', '.join(sorted(layer_names))}"
        )


def calculate_image_size(
    bounds: tuple[float, float, float, float],
    pixel_scale: float = 1.0,
) -> tuple[int, int]:
    """Choose a stable WMS image size from the municipality bounding box."""

    minx, miny, maxx, maxy = bounds
    width_m = maxx - minx
    height_m = maxy - miny

    if width_m <= 0 or height_m <= 0:
        return 1200, 1200

    max_pixels = max(700, int(1800 * pixel_scale))
    min_pixels = max(300, int(600 * pixel_scale))

    if width_m >= height_m:
        width_px = max_pixels
        height_px = max(min_pixels, int(math.ceil(max_pixels * (height_m / width_m))))
    else:
        height_px = max_pixels
        width_px = max(min_pixels, int(math.ceil(max_pixels * (width_m / height_m))))

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


def build_wms_legend_params(layer_name: str) -> dict:
    """Build one WMS GetLegendGraphic request."""

    return {
        "service": "WMS",
        "version": WMS_VERSION,
        "request": "GetLegendGraphic",
        "layer": layer_name,
        "format": "image/png",
    }


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


def remove_old_outputs(base_path: Path) -> None:
    """Remove older PNG, world file and metadata outputs for one layer."""

    for suffix in [".png", ".pgw", ".prj"]:
        output_file = base_path.with_suffix(suffix)

        if not output_file.exists():
            continue

        try:
            output_file.unlink()
        except PermissionError as error:
            log_error("One water WMS reference file is locked and cannot be overwritten.")
            log_error(f"Locked file: {display_path(output_file)}")
            log_info("Close the file in QGIS and run the script again.")
            raise SystemExit(
                "Water WMS download stopped because an output file is still open."
            ) from error


def download_wms_image(
    service_url: str,
    layer_name: str,
    bounds: tuple[float, float, float, float],
    pixel_scale: float = 1.0,
) -> tuple[bytes, int, int]:
    """Download one WMS map image for the municipality bounding box."""

    width_px, height_px = calculate_image_size(bounds, pixel_scale)
    params = build_wms_params(layer_name, bounds, width_px, height_px)
    request_url = f"{service_url}?{urlencode(params)}"

    with urlopen(request_url, timeout=180) as response:
        content_type = response.headers.get("Content-Type", "")
        image_bytes = response.read()

    if "image" not in content_type.lower():
        preview = image_bytes[:500].decode("utf-8", errors="replace")
        log_error(f"WMS response for layer '{layer_name}' is not an image.")
        log_error(preview)
        raise RuntimeError(f"WMS GetMap did not return an image for layer: {layer_name}")

    return image_bytes, width_px, height_px


def download_wms_legend(service_url: str, layer_name: str) -> bytes:
    """Download one official WMS legend graphic as PNG."""

    params = build_wms_legend_params(layer_name)
    request_url = f"{service_url}?{urlencode(params)}"

    with urlopen(request_url, timeout=180) as response:
        content_type = response.headers.get("Content-Type", "")
        legend_bytes = response.read()

    if "image" not in content_type.lower():
        preview = legend_bytes[:500].decode("utf-8", errors="replace")
        log_error(f"WMS legend response for layer '{layer_name}' is not an image.")
        log_error(preview)
        raise RuntimeError(
            f"WMS GetLegendGraphic did not return an image for layer: {layer_name}"
        )

    return legend_bytes


def pixel_is_visible_symbol(pixel) -> bool:
    """Return whether one legend pixel belongs to a visible symbol."""

    if pixel.alpha() < 20:
        return False

    # The LfU hydropower legend symbols are blue, while the labels are
    # dark gray/black. Restricting the crop to blue pixels avoids pulling
    # label fragments into the compact icon.
    return (
        pixel.blue() > 80
        and pixel.blue() > pixel.red() + 10
        and pixel.blue() >= pixel.green() - 5
    )


def write_compact_legend_icons(
    legend_file: Path,
    icon_file: Path,
    selected_indices: list[int] | None = None,
) -> int:
    """Crop left-side WMS legend symbols into one compact icon strip."""

    image = QImage(str(legend_file))

    if image.isNull():
        return 0

    scan_width = min(70, image.width())
    symbol_rows = []

    for y in range(image.height()):
        has_symbol_pixel = False

        for x in range(scan_width):
            if pixel_is_visible_symbol(image.pixelColor(x, y)):
                has_symbol_pixel = True
                break

        if has_symbol_pixel:
            symbol_rows.append(y)

    if not symbol_rows:
        return 0

    groups = []
    start = previous = symbol_rows[0]

    for y in symbol_rows[1:]:
        if y <= previous + 1:
            previous = y
        else:
            groups.append((start, previous))
            start = previous = y

    groups.append((start, previous))
    symbol_groups = [
        (start, end)
        for start, end in groups
        if (end - start) >= 8
    ]

    if not symbol_groups:
        return 0

    cropped_icons = []

    for min_y, max_y in symbol_groups:
        min_x = scan_width
        max_x = 0

        for y in range(min_y, max_y + 1):
            for x in range(scan_width):
                if pixel_is_visible_symbol(image.pixelColor(x, y)):
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)

        if min_x > max_x:
            continue

        margin = 2
        min_x = max(0, min_x - margin)
        min_y = max(0, min_y - margin)
        max_x = min(image.width() - 1, max_x + margin)
        max_y = min(image.height() - 1, max_y + margin)
        cropped_icons.append(
            image.copy(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
        )

    if not cropped_icons:
        return 0

    if selected_indices is not None:
        cropped_icons = [
            cropped_icons[index]
            for index in selected_indices
            if index < len(cropped_icons)
        ]

    if not cropped_icons:
        return 0

    gap = 4
    strip_width = sum(icon.width() for icon in cropped_icons) + gap * (
        len(cropped_icons) - 1
    )
    strip_height = max(icon.height() for icon in cropped_icons)
    strip = QImage(strip_width, strip_height, QImage.Format_ARGB32)
    strip.fill(0)

    offset_x = 0
    for icon in cropped_icons:
        offset_y = int((strip_height - icon.height()) / 2)

        for y in range(icon.height()):
            for x in range(icon.width()):
                strip.setPixelColor(offset_x + x, offset_y + y, icon.pixelColor(x, y))

        offset_x += icon.width() + gap

    if not strip.save(str(icon_file), "PNG"):
        return 0

    return len(cropped_icons)


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


def download_wasser_reference_wms(municipality_name: str) -> None:
    """Download official water WMS layers as georeferenced municipality rasters."""

    safe_name = safe_filename(municipality_name)
    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"

    if not boundary_file.exists():
        raise FileNotFoundError(
            f"Boundary file not found: {boundary_file}. Run script 2 first."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LEGEND_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    bounds, boundary_crs_wkt = read_boundary_extent(boundary_file)

    log_info(f"Downloading water WMS reference layers for: {municipality_name}")
    log_info(f"Boundary: {display_path(boundary_file)}")
    log_info(f"Output directory: {display_path(OUTPUT_DIR)}")
    log_info("Hinweis: WMS-Layer werden auf die Bounding-Box der Gemeinde geladen.")

    metadata = {
        "municipality": municipality_name,
        "boundary_file": display_path(boundary_file),
        "wms_version": WMS_VERSION,
        "crs": WMS_CRS,
        "bbox_25832": list(bounds),
        "layers": [],
        "classification_note": (
            "Wasserschutzgebiete werden separat aus SHP-Downloads als Vektorlayer "
            "gefuehrt. Festsetzung und Sicherung werden als harte "
            "wasserrechtliche Hochwasserrestriktionen im WMS-Kontext gezeigt. "
            "hwgf_hq100 und hwgf_hqextrem dienen als weiche Hochwasser-Konflikt- "
            "bzw. Risikokontextlayer. WMS-Raster ersetzen keine rechtsverbindliche "
            "Einzelfallpruefung."
        ),
    }

    for service_label, service_config in WMS_SERVICES.items():
        service_url = service_config["url"]
        log_info(f"WMS service: {service_label}")

        for layer_config in service_config["layers"]:
            layer_name = layer_config["name"]
            validate_layer_name(service_label, service_url, layer_name)

            base_path = OUTPUT_DIR / f"{safe_name}_{layer_config['stub']}"
            remove_old_outputs(base_path)

            log_info(f"WMS layer: {layer_config['title']} ({layer_name})")
            image_bytes, width_px, height_px = download_wms_image(
                service_url,
                layer_name,
                bounds,
                float(layer_config.get("pixel_scale", 1.0)),
            )

            png_file = base_path.with_suffix(".png")
            world_file = base_path.with_suffix(".pgw")
            prj_file = base_path.with_suffix(".prj")

            png_file.write_bytes(image_bytes)
            write_world_file(world_file, bounds, width_px, height_px)
            write_prj_file(prj_file, boundary_crs_wkt)

            legend_file = None
            icon_file = None
            if layer_config.get("download_legend", False):
                legend_file = LEGEND_OUTPUT_DIR / f"{layer_config['stub']}.png"
                legend_file.write_bytes(download_wms_legend(service_url, layer_name))
                log_success(
                    f"Written WMS legend graphic: {display_path(legend_file)}"
                )
                icon_file = LEGEND_OUTPUT_DIR / f"{layer_config['stub']}_icon.png"

                icon_count = write_compact_legend_icons(
                    legend_file,
                    icon_file,
                    layer_config.get("legend_icon_indices"),
                )

                if icon_count:
                    log_success(
                        "Written compact WMS legend icons: "
                        f"{display_path(icon_file)} ({icon_count})"
                    )
                else:
                    icon_file = None

            layer_metadata = {
                "service": service_label,
                "wms_url": service_url,
                "wms_layer_name": layer_name,
                "title": layer_config["title"],
                "role": layer_config["role"],
                "png_file": display_path(png_file),
                "world_file": display_path(world_file),
                "prj_file": display_path(prj_file),
                "width_px": width_px,
                "height_px": height_px,
            }

            if legend_file is not None:
                layer_metadata["legend_file"] = display_path(legend_file)

            if icon_file is not None:
                layer_metadata["legend_icon_file"] = display_path(icon_file)

            metadata["layers"].append(layer_metadata)

            log_success(f"Written WMS reference raster: {display_path(png_file)}")

    metadata_file = OUTPUT_DIR / f"{safe_name}_wasser_wms_reference.json"
    metadata_file.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    log_success("Water WMS reference download finished.")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = ColoredArgumentParser(
        description="Download official water WMS reference rasters for one municipality."
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
    download_wasser_reference_wms(args.municipality)


if __name__ == "__main__":
    qgs = QgsApplication([], False)
    qgs.initQgis()

    try:
        main()
    finally:
        qgs.exitQgis()

