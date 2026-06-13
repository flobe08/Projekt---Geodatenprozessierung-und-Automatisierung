"""
Generate map entry point.

This script runs the QGIS map generation steps for one selected municipality.
It must be executed with the system QGIS Python environment, not the normal
Python virtual environment.
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
    script_name: str,
    args: list[str] | None = None,
) -> None:
    """Run a Python script from the generate_map scripts folder."""

    script_path = SCRIPTS_DIR / "generate_map" / script_name
    command = [sys.executable, str(script_path)]

    if args:
        command.extend(args)

    display_command = [f"generate_map/{script_name}"]
    if args:
        display_command.extend(args)

    log_section(step_name)
    log_info(f"Running: python {' '.join(display_command)}")
    subprocess.run(command, check=True)


def parse_arguments() -> argparse.Namespace:
    """Read command line arguments for map generation."""

    parser = ColoredArgumentParser(
        description="Generate a QGIS project and PDF map for one municipality."
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
        help="Energy technology used for the map title and layer setup.",
    )

    return parser.parse_args()


def generate_map(municipality: str, technology: str) -> None:
    """Run all map generation steps for one municipality."""

    run_script(
        "Step 7: Create QGIS map project",
        "4_create_map_qgis_project.py",
        ["--municipality", municipality, "--technology", technology],
    )

    run_script(
        "Step 8: Generate map PDF",
        "5_generate_map_pdf.py",
        ["--municipality", municipality, "--technology", technology],
    )


def main() -> None:
    """Run the complete map generation workflow."""

    args = parse_arguments()
    generate_map(args.municipality, args.technology)
    log_success("\nMap generation finished successfully.")


if __name__ == "__main__":
    main()
