"""
Script 2: Prepare wind-specific landuse layers.

Workflow:
1. Read the municipality landuse GeoPackage created by script 4.
2. Filter the official landuse classes via the field ``source_layer``.
3. Build four wind-specific output layers.
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


OUTPUT_DIR = BASE_DIR / "data/processed/wind"


# =============================================================================
# 1. Wind landuse groups
# =============================================================================
# Ausschluss:
# Wohnen, sensible Einrichtungen, Freizeitnutzungen und wasserbezogene
# Nutzungen sollen in der ersten Windanalyse direkt ausgeschlossen werden.
WIND_AUSSCHLUSS = {
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
}

# Potenzial:
# Hier werden sowohl die klaren Suchraumklassen als auch Einzelfallflächen
# gesammelt, die später noch weiter geprüft werden können.
WIND_POTENZIAL = {
    "ln_landwirtschaft",
    "ln_ohnenutzung",
    "ln_abbau",
    "ln_lagerung",
    "ln_forstwirtschaft",
}

# Geeignet:
# Diese kleinere Teilmenge beschreibt die fachlich klarsten Kernflächen, zum
# Beispiel Landwirtschaft und nutzungsarme Freiflächen.
WIND_GEEIGNET = {
    "ln_landwirtschaft",
    "ln_ohnenutzung",
}

# Unentschlossen:
# Verkehrsflächen aus dem offiziellen Landnutzungsdatensatz werden bewusst
# separat gehalten. Die Klasse ``ln_strassenundwegeverkehr`` ist für die erste
# Windbewertung zu grob, weil sie neben größeren Straßen auch kleinere Wege
# enthalten kann. Der Layer geht dadurch nicht verloren, wird aktuell aber noch
# nicht pauschal ausgeschlossen. Später kann er gezielt mit OSM-Straßenklassen
# oder fachlich begründeten Puffern weiter verfeinert werden.
WIND_UNENTSCHLOSSEN = {
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
    # Output aktuell nicht direkt in der finalen Karte verwendet.
    potenzial_file = OUTPUT_DIR / f"{safe_name}_landuse_wind_potenzial.gpkg"
    # Output aktuell nicht direkt in der finalen Karte verwendet.
    geeignet_file = OUTPUT_DIR / f"{safe_name}_landuse_wind_geeignet.gpkg"
    # Output aktuell nicht direkt in der finalen Karte verwendet.
    unentschlossen_file = OUTPUT_DIR / f"{safe_name}_landuse_wind_unentschlossen.gpkg"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    remove_existing_output(ausschluss_file)
    remove_existing_output(potenzial_file)
    remove_existing_output(geeignet_file)
    remove_existing_output(unentschlossen_file)

    landuse = load_official_landuse(municipality_name)

    log_info(f"Preparing wind landuse for: {municipality_name}")
    log_info("Filtering official landuse classes by source_layer.")
    log_info(f"Output 1: {display_path(ausschluss_file)}")
    log_info(f"Output 2: {display_path(potenzial_file)}")
    log_info(f"Output 3: {display_path(geeignet_file)}")
    log_info(f"Output 4: {display_path(unentschlossen_file)}")
    log_detail(f"Ausschluss layers: {format_source_layers(WIND_AUSSCHLUSS)}")
    log_detail(f"Potenzial layers: {format_source_layers(WIND_POTENZIAL)}")
    log_detail(f"Geeignet layers: {format_source_layers(WIND_GEEIGNET)}")
    log_detail(
        f"Unentschlossen layers: {format_source_layers(WIND_UNENTSCHLOSSEN)}"
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
    wind_unentschlossen = filter_landuse_by_source_layers(
        landuse,
        WIND_UNENTSCHLOSSEN,
        "wind_unentschlossen",
    )

    write_layer(ausschluss_file, "landuse_wind_ausschluss", wind_ausschluss)
    write_layer(potenzial_file, "landuse_wind_potenzial", wind_potenzial)
    write_layer(geeignet_file, "landuse_wind_geeignet", wind_geeignet)
    write_layer(
        unentschlossen_file,
        "landuse_wind_unentschlossen",
        wind_unentschlossen,
    )

    log_success("Wind landuse preparation finished.")


def main() -> None:
    """Run the wind landuse preparation for one municipality."""

    parser = ColoredArgumentParser(
        description="Prepare wind-specific landuse layers for one municipality."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()
    prepare_wind_landuse(args.municipality)


if __name__ == "__main__":
    main()
