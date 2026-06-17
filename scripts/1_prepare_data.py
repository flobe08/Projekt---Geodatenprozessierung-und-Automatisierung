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

sys.path.append(str(SCRIPTS_DIR / "utils"))
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

    return parser.parse_args()


def prepare_data(
    municipality: str,
    technology: str,
) -> None:
    """Run all data preparation steps for one municipality and technology."""

    log_info(
        "Hinweis: Der allgemeine Download-Workflow kann länger dauern, "
        "weil mehrere große Bayern-Datensätze verarbeitet werden."
    )
    log_info(
        "Vor allem die amtliche Landnutzung liegt im Bereich von mehreren GB "
        "und braucht beim ersten lokalen Download spürbar länger."
    )

    run_script(
        "Step 1: Download raw datasets",
        "1_prepare_data/1_download_data.py",
        ["--technology", technology],
    )

    run_script(
        "Step 2: Extract municipality boundary",
        "1_prepare_data/2_extract_municipality_boundary.py",
        ["--municipality", municipality],
    )

    run_script(
        "Step 3: Build general protection layers",
        "1_prepare_data/3_build_protection_layers.py",
        ["--municipality", municipality],
    )

    run_script(
        "Step 4: Clip official landuse",
        "1_prepare_data/4_clip_landuse.py",
        ["--municipality", municipality],
    )

    match technology:
        case "wind":
            run_script(
                "Step 5: Download OSM network data",
                "1_prepare_data/5_download_osm_network_data.py",
                ["--municipality", municipality, "--technology", technology],
            )

            run_script(
                "Step 6: Prepare wind OSM street layers",
                "2_1_wind/4_prepare_wind_osm_streets.py",
                ["--municipality", municipality],
            )

            run_script(
                "Step 7: Clip wind datasets to the municipality",
                "2_1_wind/1_clip_wind_planning_areas.py",
                ["--municipality", municipality],
            )

            run_script(
                "Step 8: Prepare wind landuse layers",
                "2_1_wind/2_prepare_wind_landuse.py",
                ["--municipality", municipality],
            )

            run_script(
                "Step 9: Build wind landuse buffer layers",
                "2_1_wind/3_build_wind_landuse_buffers.py",
                ["--municipality", municipality],
            )

            run_script(
                "Step 10: Build combined wind exclusion layer",
                "2_1_wind/5_build_wind_exclusion_layer.py",
                ["--municipality", municipality],
            )

        case "solar":
            run_script(
                "Step 5: Download OSM network data",
                "1_prepare_data/5_download_osm_network_data.py",
                ["--municipality", municipality, "--technology", technology],
            )

            run_script(
                "Step 6: Prepare solar OSM street layers",
                "2_2_solar/4_prepare_solar_osm_streets.py",
                ["--municipality", municipality],
            )

            run_script(
                "Step 7: Prepare solar corridor layers",
                "2_2_solar/2_prepare_solar_corridor_layers.py",
                ["--municipality", municipality],
            )

            run_script(
                "Step 8: Prepare solar landuse layers",
                "2_2_solar/3_prepare_solar_landuse.py",
                ["--municipality", municipality],
            )

        case "wasser":
            run_script(
                "Step 5: Download OSM network data",
                "1_prepare_data/5_download_osm_network_data.py",
                ["--municipality", municipality, "--technology", technology],
            )

            run_script(
                "Step 6: Prepare water OSM street layers",
                "2_3_wasser/2_prepare_water_osm_streets.py",
                ["--municipality", municipality],
            )

            run_script(
                "Step 7: Prepare water landuse layers",
                "2_3_wasser/1_prepare_water_landuse.py",
                ["--municipality", municipality],
            )
        case _:
            raise ValueError(f"Unknown technology: {technology}")


def main() -> None:
    """Run the complete data preparation workflow."""

    args = parse_arguments()
    prepare_data(args.municipality, args.technology)
    log_success("\nData preparation finished successfully.")


if __name__ == "__main__":
    main()
