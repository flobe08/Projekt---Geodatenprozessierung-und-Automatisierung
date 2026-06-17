"""
Script 3: Prepare solar-specific landuse layers.

Workflow:
1. Read the municipality landuse GeoPackage created by prepare-data script 4.
2. Filter the official landuse classes via the field ``source_layer``.
3. Build four solar-specific output layers.
4. Save each category as its own GeoPackage for QGIS and manual validation.
"""

from pathlib import Path
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
OUTPUT_DIR = BASE_DIR / "data/processed/solar"


# =============================================================================
# 1. Solar landuse groups
# =============================================================================
# Ausschluss:
# Solar is filtered more strictly than wind. Forest, settlement, sensitive
# uses and technical infrastructure are excluded directly.
SOLAR_AUSSCHLUSS = {
    "ln_aquakulturundfischereiwirtschaft",
    "ln_bahnverkehr",
    "ln_bestattung",
    "ln_flugverkehr",
    "ln_forstwirtschaft",
    "ln_freiluftundnaherholung",
    "ln_freizeitanlage",
    "ln_gewerblichedienstleistungen",
    "ln_industrieundverarbeitendesgewerbe",
    "ln_kulturundunterhaltung",
    "ln_oeffentlicheeinrichtungen",
    "ln_schiffsverkehr",
    "ln_sportanlage",
    "ln_strassenundwegeverkehr",
    "ln_versorgungundentsorgung",
    "ln_wasserwirtschaft",
    "ln_wohnnutzung",
}

# Potential:
# This group contains areas that may still be considered in a first solar
# screening, even if some of them need later manual review.
# Output currently not used directly in the final map.
SOLAR_POTENZIAL = {
    "ln_abbau",
    "ln_lagerung",
    "ln_landwirtschaft",
    "ln_ohnenutzung",
}

# Geeignet:
# Smallest core set for a first solar pre-check.
# Output currently not used directly in the final map.
SOLAR_GEEIGNET = {
    "ln_landwirtschaft",
    "ln_ohnenutzung",
}

# Unused:
# Remaining class for layers that are currently not actively used.
SOLAR_UNUSED = set()


# =============================================================================
# 2. Prepare municipality output
# =============================================================================
def format_source_layers(source_layers: set[str]) -> str:
    """Format one source-layer set for compact log output."""

    return ", ".join(sorted(source_layers))


def prepare_solar_landuse(municipality_name: str) -> None:
    """Create solar-specific landuse layers for one municipality."""

    safe_name = safe_filename(municipality_name)
    ausschluss_file = OUTPUT_DIR / f"{safe_name}_landuse_solar_ausschluss.gpkg"
    # Output is currently not used directly in the final map.
    potenzial_file = OUTPUT_DIR / f"{safe_name}_landuse_solar_potenzial.gpkg"
    # Output is currently not used directly in the final map.
    geeignet_file = OUTPUT_DIR / f"{safe_name}_landuse_solar_geeignet.gpkg"
    # Output is currently not used directly in the final map.
    unused_file = OUTPUT_DIR / f"{safe_name}_landuse_solar_unused.gpkg"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(ausschluss_file)
    remove_existing_output(potenzial_file)
    remove_existing_output(geeignet_file)
    remove_existing_output(unused_file)

    landuse = load_official_landuse(municipality_name)

    log_info(f"Preparing solar landuse for: {municipality_name}")
    log_info("Filtering official landuse classes by source_layer.")
    log_info(f"Output 1: {display_path(ausschluss_file)}")
    log_info(f"Output 2: {display_path(potenzial_file)}")
    log_info(f"Output 3: {display_path(geeignet_file)}")
    log_info(f"Output 4: {display_path(unused_file)}")
    log_detail(f"Ausschluss layers: {format_source_layers(SOLAR_AUSSCHLUSS)}")
    log_detail(f"Potenzial layers: {format_source_layers(SOLAR_POTENZIAL)}")
    log_detail(f"Geeignet layers: {format_source_layers(SOLAR_GEEIGNET)}")
    log_detail(f"Unused layers: {format_source_layers(SOLAR_UNUSED)}")
    validate_landuse_group_assignment(
        "Solar",
        {
            "ausschluss": SOLAR_AUSSCHLUSS,
            "potenzial": SOLAR_POTENZIAL,
            "geeignet": SOLAR_GEEIGNET,
            "unused": SOLAR_UNUSED,
        },
    )

    solar_ausschluss = filter_landuse_by_source_layers(
        landuse,
        SOLAR_AUSSCHLUSS,
        "solar_ausschluss",
    )
    solar_potenzial = filter_landuse_by_source_layers(
        landuse,
        SOLAR_POTENZIAL,
        "solar_potenzial",
    )
    solar_geeignet = filter_landuse_by_source_layers(
        landuse,
        SOLAR_GEEIGNET,
        "solar_geeignet",
    )
    solar_unused = filter_landuse_by_source_layers(
        landuse,
        SOLAR_UNUSED,
        "solar_unused",
    )

    write_layer(ausschluss_file, "landuse_solar_ausschluss", solar_ausschluss)
    write_layer(potenzial_file, "landuse_solar_potenzial", solar_potenzial)
    write_layer(geeignet_file, "landuse_solar_geeignet", solar_geeignet)
    write_layer(unused_file, "landuse_solar_unused", solar_unused)

    log_success("Solar landuse preparation finished.")


def main() -> None:
    """Run the solar landuse preparation for one municipality."""

    parser = ColoredArgumentParser(
        description="Prepare solar-specific landuse layers for one municipality."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()
    prepare_solar_landuse(args.municipality)


if __name__ == "__main__":
    main()
