"""
Script 1: Prepare data workflow.

This entry point runs the data preparation steps in the correct order for one
selected municipality and one selected energy technology.
"""

from pathlib import Path
import argparse
import subprocess
import sys

# -----------------------------------------------------------------------------
# 0. Script paths
# -----------------------------------------------------------------------------
# input
SCRIPTS_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPTS_DIR.parent

sys.path.insert(0, str(SCRIPTS_DIR / "utils"))
from utils import ColoredArgumentParser, log_info, log_section, log_success


def run_script(
    step_name: str,
    script_path: str,
    args: list[str] | None = None,
) -> None:
    """Run a Python script from the scripts folder."""

    full_script_path = SCRIPTS_DIR / script_path
    command = [sys.executable, str(full_script_path)]

    if args:
        command.extend(args)

    display_command = [script_path]
    if args:
        display_command.extend(args)

    log_section(step_name)
    log_info(f"Running: python {' '.join(display_command)}")
    subprocess.run(command, check=True)


def safe_filename(name: str) -> str:
    """Create the same filename format as the processing scripts."""

    return name.lower().replace(" ", "_")


def skip_existing_step(step_name: str, output_file: Path, skip_existing: bool) -> bool:
    """Return True when an existing output should be reused."""

    if not skip_existing or not output_file.exists():
        return False

    log_section(step_name)
    log_info(f"Output already exists, step skipped: {output_file}")
    return True


def parse_arguments() -> argparse.Namespace:
    """Read command line arguments for data preparation."""

    parser = ColoredArgumentParser(
        description="Prepare geodata for one municipality."
    )
    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )
    parser.add_argument(
        "--technology",
        required=True,
        choices=["wind", "solar", "wasser"],
        help="Energy technology to prepare data for.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Reuse existing processed outputs where possible.",
    )

    return parser.parse_args()


def prepare_data(
    municipality: str,
    technology: str,
    skip_existing: bool = False,
) -> None:
    """Run all data preparation steps for one municipality and technology."""

    safe_name = safe_filename(municipality)

    log_info(
        "Hinweis: Der allgemeine Download-Workflow kann länger dauern, "
        "weil mehrere große Bayern-Datensätze verarbeitet werden."
    )
    log_info(
        "Vor allem die amtliche Landnutzung liegt im Bereich von mehreren GB "
        "und braucht beim ersten lokalen Download spürbar länger."
    )

    run_script(
        "Step 1.1: Download raw datasets",
        "1_prepare_data/1_download_data.py",
        ["--technology", technology],
    )

    run_script(
        "Step 1.2: Extract municipality boundary",
        "1_prepare_data/2_extract_municipality_boundary.py",
        ["--municipality", municipality],
    )

    run_script(
        "Step 1.3: Build general protection layers",
        "1_prepare_data/3_build_protection_layers.py",
        ["--municipality", municipality],
    )

    if not skip_existing_step(
        "Step 1.4: Clip official landuse",
        BASE_DIR / "data/processed/1_base_landuse" / f"landnutzung_{safe_name}.gpkg",
        skip_existing,
    ):
        run_script(
            "Step 1.4: Clip official landuse",
            "1_prepare_data/4_clip_landuse.py",
            ["--municipality", municipality],
        )

    match technology:
        case "wind":
            run_script(
                "Step 1.5: Download OSM network data",
                "1_prepare_data/5_download_osm_network_data.py",
                ["--municipality", municipality, "--technology", technology],
            )

            run_script(
                "Step 2.1: Prepare wind OSM street layers",
                "2_1_wind/4_prepare_wind_osm_streets.py",
                ["--municipality", municipality],
            )

            run_script(
                "Step 2.2: Clip wind datasets to the municipality",
                "2_1_wind/1_clip_wind_planning_areas.py",
                ["--municipality", municipality],
            )

            run_script(
                "Step 2.3: Prepare wind landuse layers",
                "2_1_wind/2_prepare_wind_landuse.py",
                ["--municipality", municipality],
            )

            run_script(
                "Step 2.4: Build wind landuse buffer layers",
                "2_1_wind/3_build_wind_landuse_buffers.py",
                ["--municipality", municipality],
            )

            run_script(
                "Step 2.5: Build combined wind exclusion layer",
                "2_1_wind/5_build_wind_exclusion_layer.py",
                ["--municipality", municipality],
            )

        case "solar":
            run_script(
                "Step 1.5: Download OSM network data",
                "1_prepare_data/5_download_osm_network_data.py",
                ["--municipality", municipality, "--technology", technology],
            )

            run_script(
                "Step 2.1: Prepare solar corridor layers",
                "2_2_solar/1_prepare_solar_corridor_layers.py",
                ["--municipality", municipality],
            )

            run_script(
                "Step 2.2: Prepare solar landuse layers",
                "2_2_solar/2_prepare_solar_landuse.py",
                ["--municipality", municipality],
            )

        case "wasser":
            run_script(
                "Step 1.5: Download OSM network data",
                "1_prepare_data/5_download_osm_network_data.py",
                ["--municipality", municipality, "--technology", technology],
            )

            run_script(
                "Step 2.1: Build water protection layers",
                "2_3_wasser/2_build_wasser_protection_layers.py",
                ["--municipality", municipality],
            )

            log_section("Step 2.x: Water-specific WMS references")
            log_info(
                "Water-specific WMS reference rasters for hydropower and "
                "flood hazard context are downloaded during map generation "
                "because they need the final municipality extent and the QGIS runtime."
            )
        case _:
            raise ValueError(f"Unknown technology: {technology}")


def main() -> None:
    """Run the complete data preparation workflow."""

    args = parse_arguments()
    prepare_data(args.municipality, args.technology, args.skip_existing)
    log_success("\nData preparation finished successfully.")


if __name__ == "__main__":
    main()
