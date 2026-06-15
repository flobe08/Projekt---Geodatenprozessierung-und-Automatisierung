"""
Script 4: Prepare solar-specific landuse layers.

Workflow:
1. Read the municipality landuse GeoPackage created by script 4.
2. Filter the official landuse classes via the field ``source_layer``.
3. Build three solar-specific output layers.
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
    write_layer,
)
from utils import ColoredArgumentParser, log_detail, log_info, log_success


OUTPUT_DIR = BASE_DIR / "data/processed/solar"


# =============================================================================
# 1. Solar landuse groups
# =============================================================================
# Ausschluss:
# Für Solar wird strenger gefiltert als bei Wind. Wald, Siedlung, sensible
# Nutzungen und technische Infrastruktur sollen hier direkt herausfallen.
SOLAR_AUSSCHLUSS = {
    "ln_wohnnutzung",
    "ln_bestattung",
    "ln_oeffentlicheeinrichtungen",
    "ln_sportanlage",
    "ln_freizeitanlage",
    "ln_freiluftundnaherholung",
    "ln_bahnverkehr",
    "ln_flugverkehr",
    "ln_schiffsverkehr",
    "ln_wasserwirtschaft",
    "ln_aquakulturundfischereiwirtschaft",
    "ln_strassenundwegeverkehr",
    "ln_forstwirtschaft",
    "ln_gewerblichedienstleistungen",
    "ln_industrieundverarbeitendesgewerbe",
    "ln_versorgungundentsorgung",
    "ln_kulturundunterhaltung",
}

# Potenzial:
# Diese Gruppe enthält alle Flächen, die in einer ersten Solaranalyse noch in
# Betracht kommen können, auch wenn ein Teil davon später manuell geprüft werden
# sollte. Output aktuell nicht direkt in der finalen Karte verwendet.
SOLAR_POTENZIAL = {
    "ln_landwirtschaft",
    "ln_ohnenutzung",
    "ln_abbau",
    "ln_lagerung",
}

# Geeignet:
# Die kleinste Kernmenge für eine erste Solar-Vorprüfung.
# Output aktuell nicht direkt in der finalen Karte verwendet.
SOLAR_GEEIGNET = {
    "ln_landwirtschaft",
    "ln_ohnenutzung",
}


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
    # Output aktuell nicht direkt in der finalen Karte verwendet.
    potenzial_file = OUTPUT_DIR / f"{safe_name}_landuse_solar_potenzial.gpkg"
    # Output aktuell nicht direkt in der finalen Karte verwendet.
    geeignet_file = OUTPUT_DIR / f"{safe_name}_landuse_solar_geeignet.gpkg"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(ausschluss_file)
    remove_existing_output(potenzial_file)
    remove_existing_output(geeignet_file)

    landuse = load_official_landuse(municipality_name)

    log_info(f"Preparing solar landuse for: {municipality_name}")
    log_info("Filtering official landuse classes by source_layer.")
    log_info(f"Output 1: {display_path(ausschluss_file)}")
    log_info(f"Output 2: {display_path(potenzial_file)}")
    log_info(f"Output 3: {display_path(geeignet_file)}")
    log_detail(f"Ausschluss layers: {format_source_layers(SOLAR_AUSSCHLUSS)}")
    log_detail(f"Potenzial layers: {format_source_layers(SOLAR_POTENZIAL)}")
    log_detail(f"Geeignet layers: {format_source_layers(SOLAR_GEEIGNET)}")

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

    write_layer(ausschluss_file, "landuse_solar_ausschluss", solar_ausschluss)
    write_layer(potenzial_file, "landuse_solar_potenzial", solar_potenzial)
    write_layer(geeignet_file, "landuse_solar_geeignet", solar_geeignet)

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
