from pathlib import Path
import argparse
import geopandas as gpd


INPUT_FILE = Path(
    "data/raw/Verwaltungsgebiet_Bayern/ALKIS-Vereinfacht/VerwaltungsEinheit.shp"
)

OUTPUT_DIR = Path("data/processed/boundaries")


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

        return

    safe_name = municipality_name.lower().replace(" ", "_")
    output_file = OUTPUT_DIR / f"{safe_name}_boundary.gpkg"

    municipality.to_file(output_file, driver="GPKG")

    minx, miny, maxx, maxy = municipality.total_bounds

    print(f"Municipality extracted: {municipality_name}")
    print(f"Output written to: {output_file}")
    print("Bounding box:")
    print(f"{minx},{miny},{maxx},{maxy}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract a municipality boundary from the Bavarian administrative dataset."
    )

    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()
    extract_municipality(args.municipality)