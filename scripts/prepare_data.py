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
BASE_DIR = SCRIPTS_DIR.parent

sys.path.append(str(SCRIPTS_DIR / "utils"))
from utils import ColoredArgumentParser, log_info, log_section, log_success


def run_script(
    step_name: str,
    script_name: str,
    args: list[str] | None = None,
) -> None:
    """Run a Python script from the prepare_data scripts folder."""

    script_path = SCRIPTS_DIR / "prepare_data" / script_name

    command = [sys.executable, str(script_path)]

    if args:
        command.extend(args)

    display_command = [f"prepare_data/{script_name}"]

    if args:
        display_command.extend(args)

    log_section(step_name)
    log_info(f"Running: python {' '.join(display_command)}")
    subprocess.run(command, check=True)


def parse_arguments() -> argparse.Namespace:
    """Read command line arguments for data preparation."""

    # Select municipality and energy technology for this data preparation run.
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


def prepare_data(municipality: str, technology: str) -> None:
    """Run all data preparation steps for one municipality and technology."""

    # Step 0: Download base data and technology-specific raw data.
    run_script(
        "Step 0: Download raw data",
        "0_download_data.py",
        ["--technology", technology],
    )

    # Step 1: Extract the selected municipality boundary.
    run_script(
        "Step 1: Extract municipality boundary",
        "1_grenzen.py",
        ["--municipality", municipality],
    )

    # Step 2: Download OSM roads from Overpass and clip them.
    run_script(
        "Step 2: Download OSM roads",
        "2_download_overpass_data.py",
        ["--municipality", municipality],
    )

    # Step 3: Clip official landuse data to the municipality boundary.
    run_script(
        "Step 3: Clip official landuse",
        "3_clip_landuse.py",
        ["--municipality", municipality],
    )


def main() -> None:
    """Run the complete data preparation workflow."""

    args = parse_arguments()
    prepare_data(args.municipality, args.technology)

    log_success("\nData preparation finished successfully.")


if __name__ == "__main__":
    main()

#
# source .venv-wsl/bin/activate
# python3 scripts/prepare_data.py --municipality Drachselsried --technology wind
