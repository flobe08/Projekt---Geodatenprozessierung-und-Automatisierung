"""
Script 2: Prepare wind-specific landuse layers.

Workflow:
1. Read the municipality landuse GeoPackage created by script 4.
2. Filter the official landuse classes via the field ``source_layer``.
3. Build four wind-specific output layers.
4. Save each category as its own GeoPackage for QGIS and manual validation.
"""

from pathlib import Path
import argparse
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent / "utils"))
from landuse_utils import (
    BASE_DIR,
    display_path,
    filter_landuse_by_source_layers,
    load_official_landuse,
    remove_existing_output,
    safe_filename,
    validate_landuse_group_assignment,
    write_layer,
)
from utils import ColoredArgumentParser, log_detail, log_info, log_success


# -----------------------------------------------------------------------------
# 0. Input and output paths
# -----------------------------------------------------------------------------
# input is resolved in landuse_utils.load_official_landuse()

# output
OUTPUT_DIR = BASE_DIR / "data/processed/2_technology_wind"


# =============================================================================
# 1. Wind landuse groups
# =============================================================================
# Ausschluss:
# Residential areas, sensitive uses, recreation and water-related landuse
# classes are excluded in the first wind analysis.
WIND_AUSSCHLUSS = {
    "ln_aquakulturundfischereiwirtschaft",
    "ln_bahnverkehr",
    "ln_bestattung",
    "ln_flugverkehr",
    "ln_freiluftundnaherholung",
    "ln_freizeitanlage",
    "ln_gewerblichedienstleistungen",
    "ln_industrieundverarbeitendesgewerbe",
    "ln_kulturundunterhaltung",
    "ln_oeffentlicheeinrichtungen",
    "ln_schiffsverkehr",
    "ln_sportanlage",
    "ln_versorgungundentsorgung",
    "ln_wasserwirtschaft",
    "ln_wohnnutzung",
}

# Potential:
# This group contains broad search-space classes and case-by-case classes
# that can be checked more closely in later processing steps.
WIND_POTENZIAL = {
    "ln_abbau", # only case-by-case; active extraction sites are not directly suitable
    "ln_forstwirtschaft",
    "ln_lagerung",
    "ln_landwirtschaft",
    "ln_ohnenutzung",
}

# Geeignet:
# This smaller subset contains the clearest core areas, for example
# agricultural land and land with little current use.
WIND_GEEIGNET = {
    "ln_landwirtschaft",
    "ln_ohnenutzung",
}

# Unused:
# Remaining class for layers that are currently not actively used.
# Roads and paths are kept separate because they can later be checked more
# precisely with OSM classes and method-specific buffers.
WIND_UNUSED = {
    "ln_strassenundwegeverkehr",
}


# =============================================================================
# 2. Prepare municipality output
# =============================================================================
def format_source_layers(source_layers: set[str]) -> str:
    """Format one source-layer set for compact log output."""

    return ", ".join(sorted(source_layers))


def prepare_wind_landuse(municipality_name: str) -> None:
    """Create wind-specific landuse layers for one municipality."""

    safe_name = safe_filename(municipality_name)
    ausschluss_file = OUTPUT_DIR / f"{safe_name}_landuse_wind_ausschluss.gpkg"
    # Output is currently not used directly in the final map.
    potenzial_file = OUTPUT_DIR / f"{safe_name}_landuse_wind_potenzial.gpkg"
    # Output is currently not used directly in the final map.
    geeignet_file = OUTPUT_DIR / f"{safe_name}_landuse_wind_geeignet.gpkg"
    # Output is currently not used directly in the final map.
    unused_file = OUTPUT_DIR / f"{safe_name}_landuse_wind_unused.gpkg"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(ausschluss_file)
    remove_existing_output(potenzial_file)
    remove_existing_output(geeignet_file)
    remove_existing_output(unused_file)

    landuse = load_official_landuse(municipality_name)

    log_info(f"Preparing wind landuse for: {municipality_name}")
    log_info("Filtering official landuse classes by source_layer.")
    log_info(f"Output 1: {display_path(ausschluss_file)}")
    log_info(f"Output 2: {display_path(potenzial_file)}")
    log_info(f"Output 3: {display_path(geeignet_file)}")
    log_info(f"Output 4: {display_path(unused_file)}")
    log_detail(f"Ausschluss layers: {format_source_layers(WIND_AUSSCHLUSS)}")
    log_detail(f"Potenzial layers: {format_source_layers(WIND_POTENZIAL)}")
    log_detail(f"Geeignet layers: {format_source_layers(WIND_GEEIGNET)}")
    log_detail(f"Unused layers: {format_source_layers(WIND_UNUSED)}")
    validate_landuse_group_assignment(
        "Wind",
        {
            "ausschluss": WIND_AUSSCHLUSS,
            "potenzial": WIND_POTENZIAL,
            "geeignet": WIND_GEEIGNET,
            "unused": WIND_UNUSED,
        },
    )

    wind_ausschluss = filter_landuse_by_source_layers(
        landuse,
        WIND_AUSSCHLUSS,
        "wind_ausschluss",
    )
    wind_potenzial = filter_landuse_by_source_layers(
        landuse,
        WIND_POTENZIAL,
        "wind_potenzial",
    )
    wind_geeignet = filter_landuse_by_source_layers(
        landuse,
        WIND_GEEIGNET,
        "wind_geeignet",
    )
    wind_unused = filter_landuse_by_source_layers(
        landuse,
        WIND_UNUSED,
        "wind_unused",
    )

    write_layer(ausschluss_file, "landuse_wind_ausschluss", wind_ausschluss)
    write_layer(potenzial_file, "landuse_wind_potenzial", wind_potenzial)
    write_layer(geeignet_file, "landuse_wind_geeignet", wind_geeignet)
    write_layer(
        unused_file,
        "landuse_wind_unused",
        wind_unused,
    )

    log_success("Wind landuse preparation finished.")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = ColoredArgumentParser(
        description="Prepare wind-specific landuse layers for one municipality."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    return parser.parse_args()


def main() -> None:
    """Run the wind landuse preparation for one municipality."""

    args = parse_arguments()
    prepare_wind_landuse(args.municipality)


if __name__ == "__main__":
    main()
