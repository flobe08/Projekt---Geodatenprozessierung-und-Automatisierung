"""
Script 1: Prepare water-specific landuse layers.

Workflow:
1. Read the municipality landuse GeoPackage created by script 4.
2. Filter the official landuse classes via the field ``source_layer``.
3. Build four water-specific output layers.
4. Save each category as its own GeoPackage for QGIS and manual validation.

Note:
For hydropower, landuse is mainly contextual information. The more important
technical inputs will likely be watercourses, protected areas and flood areas.
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
OUTPUT_DIR = BASE_DIR / "data/processed/wasser"


# =============================================================================
# 1. Water landuse groups
# =============================================================================
# Ausschluss:
# Residential areas, public facilities and typical recreation or transport
# areas are not treated as search areas for hydropower.
WASSER_AUSSCHLUSS = {
    "ln_bestattung",
    "ln_flugverkehr",
    "ln_freiluftundnaherholung",
    "ln_freizeitanlage",
    "ln_gewerblichedienstleistungen",
    "ln_industrieundverarbeitendesgewerbe",
    "ln_kulturundunterhaltung",
    "ln_oeffentlicheeinrichtungen",
    "ln_sportanlage",
    "ln_versorgungundentsorgung",
    "ln_wohnnutzung",
}

# kontext:
# These landuse classes are relevant for hydropower context, without already
# guaranteeing suitability. Output currently not used directly in the final map.
WASSER_KONTEXT = {
    "ln_aquakulturundfischereiwirtschaft",
    "ln_ohnenutzung",
    "ln_schiffsverkehr",
    "ln_wasserwirtschaft",
}

# Geeignet:
# Preliminary core set for water-related or sparsely built-up areas.
# Output currently not used directly in the final map.
WASSER_GEEIGNET = {
    "ln_aquakulturundfischereiwirtschaft",
    "ln_ohnenutzung",
    "ln_wasserwirtschaft",
}

# Unused:
# Remaining class for layers that are currently not actively used.
WASSER_UNUSED = {
    "ln_abbau",
    "ln_bahnverkehr",
    "ln_forstwirtschaft",
    "ln_lagerung",
    "ln_landwirtschaft",
    "ln_strassenundwegeverkehr",
}


# =============================================================================
# 2. Prepare municipality output
# =============================================================================
def format_source_layers(source_layers: set[str]) -> str:
    """Format one source-layer set for compact log output."""

    return ", ".join(sorted(source_layers))


def prepare_water_landuse(municipality_name: str) -> None:
    """Create water-specific landuse layers for one municipality."""

    safe_name = safe_filename(municipality_name)
    ausschluss_file = OUTPUT_DIR / f"{safe_name}_landuse_wasser_ausschluss.gpkg"
    # Output is currently not used directly in the final map.
    kontext_file = OUTPUT_DIR / f"{safe_name}_landuse_wasser_kontext.gpkg"
    # Output is currently not used directly in the final map.
    geeignet_file = OUTPUT_DIR / f"{safe_name}_landuse_wasser_geeignet.gpkg"
    # Output is currently not used directly in the final map.
    unused_file = OUTPUT_DIR / f"{safe_name}_landuse_wasser_unused.gpkg"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(ausschluss_file)
    remove_existing_output(kontext_file)
    remove_existing_output(geeignet_file)
    remove_existing_output(unused_file)

    landuse = load_official_landuse(municipality_name)

    log_info(f"Preparing water landuse for: {municipality_name}")
    log_info("Filtering official landuse classes by source_layer.")
    log_info(f"Output 1: {display_path(ausschluss_file)}")
    log_info(f"Output 2: {display_path(kontext_file)}")
    log_info(f"Output 3: {display_path(geeignet_file)}")
    log_info(f"Output 4: {display_path(unused_file)}")
    log_detail(f"Ausschluss layers: {format_source_layers(WASSER_AUSSCHLUSS)}")
    log_detail(f"Kontext layers: {format_source_layers(WASSER_KONTEXT)}")
    log_detail(f"Geeignet layers: {format_source_layers(WASSER_GEEIGNET)}")
    log_detail(f"Unused layers: {format_source_layers(WASSER_UNUSED)}")
    validate_landuse_group_assignment(
        "Wasser",
        {
            "ausschluss": WASSER_AUSSCHLUSS,
            "kontext": WASSER_KONTEXT,
            "geeignet": WASSER_GEEIGNET,
            "unused": WASSER_UNUSED,
        },
    )

    wasser_ausschluss = filter_landuse_by_source_layers(
        landuse,
        WASSER_AUSSCHLUSS,
        "wasser_ausschluss",
    )
    wasser_kontext = filter_landuse_by_source_layers(
        landuse,
        WASSER_KONTEXT,
        "wasser_kontext",
    )
    wasser_geeignet = filter_landuse_by_source_layers(
        landuse,
        WASSER_GEEIGNET,
        "wasser_geeignet",
    )
    wasser_unused = filter_landuse_by_source_layers(
        landuse,
        WASSER_UNUSED,
        "wasser_unused",
    )

    write_layer(ausschluss_file, "landuse_wasser_ausschluss", wasser_ausschluss)
    write_layer(kontext_file, "landuse_wasser_kontext", wasser_kontext)
    write_layer(geeignet_file, "landuse_wasser_geeignet", wasser_geeignet)
    write_layer(unused_file, "landuse_wasser_unused", wasser_unused)

    log_success("Water landuse preparation finished.")


def main() -> None:
    """Run the water landuse preparation for one municipality."""

    parser = ColoredArgumentParser(
        description="Prepare water-specific landuse layers for one municipality."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()
    prepare_water_landuse(args.municipality)


if __name__ == "__main__":
    main()
