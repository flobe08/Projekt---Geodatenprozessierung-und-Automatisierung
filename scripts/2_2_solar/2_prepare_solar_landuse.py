"""
Script 2: Prepare solar-specific landuse layers.

Workflow:
1. Read the municipality landuse GeoPackage created by prepare-data script 4.
2. Filter the official landuse classes via the field ``source_layer``.
3. Build solar-specific exclusion and PV open-space approximation layers.
4. Save each category as its own GeoPackage for QGIS and manual validation.
"""

from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "utils"))
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
OUTPUT_DIR = BASE_DIR / "data/processed/2_technology_solar"


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
    "ln_lagerung",
    "ln_oeffentlicheeinrichtungen",
    "ln_schiffsverkehr",
    "ln_sportanlage",
    "ln_strassenundwegeverkehr",
    "ln_versorgungundentsorgung",
    "ln_wasserwirtschaft",
    "ln_wohnnutzung",
}

# PV open-space approximation:
# This vector layer is a simplified landuse-based approximation of possible
# open-space PV areas. It is mainly used for QGIS inspection and comparison
# with the official PV open-space WMS reference.
SOLAR_PV_FREIFLAECHEN_NAEHUNG = {
    "ln_abbau",
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
    # Output is currently used as a detail and attribute layer in QGIS.
    pv_freiflaechen_file = (
        OUTPUT_DIR
        / f"{safe_name}_landuse_solar_pv_freiflaechen_naehung_vektorlayer.gpkg"
    )
    # Output is currently not used directly in the final map.
    unused_file = OUTPUT_DIR / f"{safe_name}_landuse_solar_unused.gpkg"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(ausschluss_file)
    remove_existing_output(pv_freiflaechen_file)
    remove_existing_output(unused_file)

    landuse = load_official_landuse(municipality_name)

    log_info(f"Preparing solar landuse for: {municipality_name}")
    log_info("Filtering official landuse classes by source_layer.")
    log_info(f"Output 1: {display_path(ausschluss_file)}")
    log_info(f"Output 2: {display_path(pv_freiflaechen_file)}")
    log_info(f"Output 3: {display_path(unused_file)}")
    log_detail(f"Ausschluss layers: {format_source_layers(SOLAR_AUSSCHLUSS)}")
    log_detail(
        "PV-Freiflächen-Näherung layers: "
        f"{format_source_layers(SOLAR_PV_FREIFLAECHEN_NAEHUNG)}"
    )
    log_detail(f"Unused layers: {format_source_layers(SOLAR_UNUSED)}")
    validate_landuse_group_assignment(
        "Solar",
        {
            "ausschluss": SOLAR_AUSSCHLUSS,
            "pv_freiflaechen_naehung": SOLAR_PV_FREIFLAECHEN_NAEHUNG,
            "unused": SOLAR_UNUSED,
        },
    )

    solar_ausschluss = filter_landuse_by_source_layers(
        landuse,
        SOLAR_AUSSCHLUSS,
        "solar_ausschluss",
    )
    solar_pv_freiflaechen = filter_landuse_by_source_layers(
        landuse,
        SOLAR_PV_FREIFLAECHEN_NAEHUNG,
        "solar_pv_freiflaechen_naehung",
    )
    solar_unused = filter_landuse_by_source_layers(
        landuse,
        SOLAR_UNUSED,
        "solar_unused",
    )

    write_layer(ausschluss_file, "landuse_solar_ausschluss", solar_ausschluss)
    write_layer(
        pv_freiflaechen_file,
        "landuse_solar_pv_freiflaechen_naehung_vektorlayer",
        solar_pv_freiflaechen,
    )
    write_layer(unused_file, "landuse_solar_unused", solar_unused)

    log_success("Solar landuse preparation finished.")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = ColoredArgumentParser(
        description="Prepare solar-specific landuse layers for one municipality."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    return parser.parse_args()


def main() -> None:
    """Run the solar landuse preparation for one municipality."""

    args = parse_arguments()
    prepare_solar_landuse(args.municipality)


if __name__ == "__main__":
    main()
