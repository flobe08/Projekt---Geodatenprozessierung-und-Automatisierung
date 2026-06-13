"""
Prepare data entry point.

This script runs the data preparation steps in the correct order for one
selected municipality and one selected energy technology.
"""

from pathlib import Path
import argparse
import subprocess
import sys

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

    run_script(
        "Step 1: Download raw datasets",
        "prepare_data/0_download_data.py",
        ["--technology", technology],
    )

    run_script(
        "Step 2: Extract municipality boundary",
        "prepare_data/1_grenzen.py",
        ["--municipality", municipality],
    )

    match technology:
        case "wind":
            # Future optional step:
            # OSM context roads can be added here later if the wind workflow
            # should include extra road context for orientation in the map.

            run_script(
                "Step 3: Clip wind datasets to the municipality",
                "wind/3_clip_wind_planning_areas.py",
                ["--municipality", municipality],
            )

        case "solar" | "wasser":
            log_info(f"No preparation scripts configured yet for: {technology}")
        case _:
            raise ValueError(f"Unknown technology: {technology}")


def main() -> None:
    """Run the complete data preparation workflow."""

    args = parse_arguments()
    prepare_data(args.municipality, args.technology)
    log_success("\nData preparation finished successfully.")


if __name__ == "__main__":
    main()
