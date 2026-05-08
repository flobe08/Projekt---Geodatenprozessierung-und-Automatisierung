from pathlib import Path
import argparse
import shutil
import subprocess
import tempfile

import geopandas as gpd

from utils import log_info, log_success

BASE_DIR = Path(__file__).resolve().parent.parent

OSM_INPUT_FILE = BASE_DIR / "data/raw/osm/bayern-latest.osm.pbf"
BOUNDARY_DIR = BASE_DIR / "data/processed/boundaries"
OUTPUT_DIR = BASE_DIR / "data/processed/osm"


def safe_filename(name: str) -> str:
    """Create the same filename format as script 1."""

    return name.lower().replace(" ", "_")


def extract_osm_for_municipality(municipality_name: str) -> None:
    """Cut the Bavaria OSM dataset to the municipality boundary from script 1."""

    safe_name = safe_filename(municipality_name)
    boundary_file = BOUNDARY_DIR / f"{safe_name}_boundary.gpkg"
    output_file = OUTPUT_DIR / f"{safe_name}_osm.pbf"

    if not OSM_INPUT_FILE.exists():
        raise FileNotFoundError(f"OSM input file not found: {OSM_INPUT_FILE}")

    if not boundary_file.exists():
        raise FileNotFoundError(
            f"Boundary file not found: {boundary_file}. Run script 1 first."
        )

    if shutil.which("osmium") is None:
        raise RuntimeError(
            "osmium was not found. Install osmium-tool first, because cutting an "
            "OSM PBF into another OSM PBF needs osmium.\n"
            "Windows/conda: conda install -c conda-forge osmium-tool\n"
            "WSL/Linux: sudo apt install osmium-tool"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    boundary = gpd.read_file(boundary_file).to_crs(epsg=4326)
    boundary = boundary[["geometry"]].dissolve()

    with tempfile.TemporaryDirectory() as temp_dir:
        polygon_file = Path(temp_dir) / f"{safe_name}_boundary.geojson"
        boundary.to_file(polygon_file, driver="GeoJSON")

        command = [
            "osmium",
            "extract",
            "-p",
            str(polygon_file),
            str(OSM_INPUT_FILE),
            "-o",
            str(output_file),
            "--overwrite",
        ]

        log_info(f"Cutting OSM data for: {municipality_name}")
        log_info(f"Boundary: {boundary_file}")
        log_info(f"Input: {OSM_INPUT_FILE}")
        log_info(f"Output: {output_file}")
        log_info(f"Running: {' '.join(command)}")

        subprocess.run(command, check=True)

        log_success("Cut OSM dataset finished.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cut the Bavaria OSM PBF to one municipality boundary."
    )

    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()
    extract_osm_for_municipality(args.municipality)


if __name__ == "__main__":
    main()
