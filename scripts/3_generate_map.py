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

# -----------------------------------------------------------------------------
# 0. Script paths
# -----------------------------------------------------------------------------
# input
SCRIPTS_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(SCRIPTS_DIR / "utils"))
from utils import ColoredArgumentParser, log_info, log_section, log_success


# =============================================================================
# General helper functions
# =============================================================================
def run_script(
    step_name: str,
    script_name: str,
    args: list[str] | None = None,
) -> None:
    """Run a Python script from the scripts workspace."""

    script_path = (SCRIPTS_DIR / "3_generate_map" / script_name).resolve()

    if not script_path.exists():
        script_path = (SCRIPTS_DIR / script_name).resolve()

    command = [sys.executable, str(script_path)]

    if args:
        command.extend(args)

    try:
        display_path = script_path.relative_to(SCRIPTS_DIR)
        display_command = [str(display_path).replace("\\", "/")]
    except ValueError:
        display_command = [str(script_path)]

    if args:
        display_command.extend(args)

    log_section(step_name)
    log_info(f"Running: python {' '.join(display_command)}")
    subprocess.run(command, check=True)


# =============================================================================
# General argument parsing
# =============================================================================
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


# =============================================================================
# Wind, solar and water map generation workflow
# =============================================================================
def generate_map(municipality: str, technology: str) -> None:
    """Run all map generation steps for one municipality."""

    if technology == "solar":
        # Solar needs official PV WMS reference rasters before the project is built.
        run_script(
            "Step 3.1: Download solar WMS reference rasters",
            "2_2_solar/3_download_solar_reference_wms.py",
            ["--municipality", municipality],
        )
        overview_step = "Step 3.2: Prepare overview map layers"
        create_project_step = "Step 3.3: Create QGIS map project"
        generate_pdf_step = "Step 3.4: Generate map PDF"
    elif technology == "wasser":
        # Wasser needs official WMS reference rasters for hydropower and flood context.
        run_script(
            "Step 3.1: Download water WMS reference rasters",
            "2_3_wasser/1_download_wasser_reference_wms.py",
            ["--municipality", municipality],
        )
        overview_step = "Step 3.2: Prepare overview map layers"
        create_project_step = "Step 3.3: Create QGIS map project"
        generate_pdf_step = "Step 3.4: Generate map PDF"
    else:
        # Wind can start directly with the overview layer because all thematic
        # inputs are already produced during data preparation.
        overview_step = "Step 3.1: Prepare overview map layers"
        create_project_step = "Step 3.2: Create QGIS map project"
        generate_pdf_step = "Step 3.3: Generate map PDF"

    run_script(
        overview_step,
        "1_prepare_overview_layers.py",
        ["--municipality", municipality],
    )

    run_script(
        create_project_step,
        "2_create_map_qgis_project.py",
        ["--municipality", municipality, "--technology", technology],
    )

    run_script(
        generate_pdf_step,
        "3_generate_map_pdf.py",
        ["--municipality", municipality, "--technology", technology],
    )


# =============================================================================
# Main entry point
# =============================================================================
def main() -> None:
    """Run the complete map generation workflow."""

    args = parse_arguments()
    generate_map(args.municipality, args.technology)
    log_success("\nMap generation finished successfully.")


if __name__ == "__main__":
    main()
