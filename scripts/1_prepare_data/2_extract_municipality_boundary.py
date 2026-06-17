"""
Script 2: Extract municipality boundary.

This script reads the Bavarian administrative boundary dataset and extracts
one selected municipality as a GeoPackage for all following processing steps.
"""

from pathlib import Path
import geopandas as gpd
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent / "utils"))
from utils import ColoredArgumentParser, log_error, log_info, log_success


BASE_DIR = Path(__file__).resolve().parent.parent.parent

# -----------------------------------------------------------------------------
# 0. Input and output paths
# -----------------------------------------------------------------------------
# input
INPUT_FILE = (
    BASE_DIR
    / "data/raw/Verwaltungsgebiet_Bayern/ALKIS-Vereinfacht/VerwaltungsEinheit.shp"
)

# output
OUTPUT_DIR = BASE_DIR / "data/processed/boundaries"


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
def display_path(path: Path) -> str:
    """Return a compact path for log messages."""

    try:
        return str(path.resolve().relative_to(BASE_DIR))
    except ValueError:
        return str(path)


def write_boundary(output_file: Path, municipality: gpd.GeoDataFrame) -> None:
    """Write the municipality boundary to a GeoPackage."""

    try:
        municipality.to_file(output_file, driver="GPKG")
    except Exception as error:
        # Writing can fail when QGIS or another program keeps the GeoPackage open.
        log_error("Could not write municipality boundary.")
        log_error(f"Output file: {display_path(output_file)}")
        log_info("Close the file in QGIS or remove the layer from the QGIS project.")
        log_info("Then run the pipeline again.")
        raise SystemExit(
            "Script 2 stopped because the boundary GeoPackage could not be written."
        ) from error


# -----------------------------------------------------------------------------
# 1. Extract one municipality from the Bavarian boundary dataset
# -----------------------------------------------------------------------------
def extract_municipality(municipality_name: str) -> None:
    """Extract one municipality boundary from the Bavarian administrative dataset."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    boundaries = gpd.read_file(INPUT_FILE)

    required_columns = ["name", "art", "geometry"]
    for column in required_columns:
        if column not in boundaries.columns:
            raise ValueError(f"Required column missing: {column}")

    municipalities = boundaries[boundaries["art"].str.lower() == "gemeinde"]

    municipality = municipalities[
        municipalities["name"].str.lower() == municipality_name.lower()
    ]

    if municipality.empty:
        print(f"No exact match found for: {municipality_name}")

        similar = municipalities[
            municipalities["name"].str.contains(municipality_name, case=False, na=False)
        ]

        if not similar.empty:
            print("\nSimilar municipalities found:")
            print(similar[["name", "art", "ags"]])
        else:
            print("\nNo similar municipalities found.")

        raise ValueError(f"Municipality not found: {municipality_name}")

    safe_name = municipality_name.lower().replace(" ", "_")
    output_file = OUTPUT_DIR / f"{safe_name}_boundary.gpkg"

    write_boundary(output_file, municipality)

    minx, miny, maxx, maxy = municipality.total_bounds

    print(f"Municipality extracted: {municipality_name}")
    print(f"Output written to: {output_file}")
    print("Bounding box:")
    print(f"{minx},{miny},{maxx},{maxy}")
    log_success("Municipality boundary extraction finished.")


if __name__ == "__main__":
    parser = ColoredArgumentParser(
        description="Extract a municipality boundary from the Bavarian administrative dataset."
    )

    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()
    extract_municipality(args.municipality)
