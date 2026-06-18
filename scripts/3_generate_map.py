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

sys.path.append(str(SCRIPTS_DIR / "utils"))
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

    # =========================================================================
    # Wind
    # =========================================================================
    # The current wind workflow uses the same QGIS project and PDF scripts as
    # the other technologies, but with wind-specific layers and map text.

    # =========================================================================
    # Solar
    # =========================================================================
    # The current solar workflow uses the same QGIS project and PDF scripts as
    # the other technologies, but with solar-specific layers, map text and
    # additional amtliche WMS-Referenzraster.

    # =========================================================================
    # Wasser
    # =========================================================================
    # Hydropower is structurally prepared already. The shared map scripts are
    # called in the same way, once the required water layers are available.

    if technology == "solar":
        run_script(
            "Step 3.1: Download solar WMS reference rasters",
            "2_2_solar/1_download_solar_reference_wms.py",
            ["--municipality", municipality],
        )
        create_project_step = "Step 3.2: Create QGIS map project"
        generate_pdf_step = "Step 3.3: Generate map PDF"
    else:
        create_project_step = "Step 3.1: Create QGIS map project"
        generate_pdf_step = "Step 3.2: Generate map PDF"

    run_script(
        create_project_step,
        "1_create_map_qgis_project.py",
        ["--municipality", municipality, "--technology", technology],
    )

    run_script(
        generate_pdf_step,
        "2_generate_map_pdf.py",
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
