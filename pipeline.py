from pathlib import Path
import argparse
import subprocess
import sys

sys.path.append(str(Path(__file__).resolve().parent / "scripts"))
from utils import log_info, log_section, log_success


BASE_DIR = Path(__file__).resolve().parent


def run_script(
    step_name: str,
    script_name: str,
    args: list[str] | None = None,
) -> None:
    """Run a Python script from the scripts folder."""

    script_path = BASE_DIR / "scripts" / script_name

    command = [sys.executable, str(script_path)]

    if args:
        command.extend(args)

    display_command = [script_name]

    if args:
        display_command.extend(args)

    log_section(step_name)
    log_info(f"Running: python {' '.join(display_command)}")
    subprocess.run(command, check=True)


def parse_arguments() -> argparse.Namespace:
    """Read command line arguments for the pipeline."""

    # Select municipality and energy technology for this pipeline run.
    parser = argparse.ArgumentParser(
        description="Run the geodata processing pipeline."
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


def run_pipeline(municipality: str, technology: str) -> None:
    """Run all processing steps for one municipality and technology."""

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

    # Step 2: Cut the OSM dataset to the municipality boundary.
    run_script(
        "Step 2: Cut OSM dataset",
        "2_extract_osm.py",
        ["--municipality", municipality],
    )


def main() -> None:
    """Run the complete geodata processing pipeline."""

    args = parse_arguments()
    run_pipeline(args.municipality, args.technology)

    log_success("\nPipeline finished successfully.")


if __name__ == "__main__":
    main()

# python pipeline.py --municipality Drachselsried --technology wind
