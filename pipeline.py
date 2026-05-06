from pathlib import Path
import argparse
import subprocess
import sys


BASE_DIR = Path(__file__).resolve().parent


def run_script(script_name: str, args: list[str] | None = None) -> None:
    """Run a Python script from the scripts folder."""

    script_path = BASE_DIR / "scripts" / script_name

    command = [sys.executable, str(script_path)]

    if args:
        command.extend(args)

    print(f"\nRunning: {' '.join(command)}")
    subprocess.run(command, check=True)


def main() -> None:
    """Run the complete geodata processing pipeline."""

    parser = argparse.ArgumentParser(
        description="Run the geodata processing pipeline."
    )

    parser.add_argument(
        "--municipality",
        required=True,
        help="Name of the municipality, e.g. Drachselsried",
    )

    args = parser.parse_args()

    run_script("0_download_data.py")
    run_script("1_grenzen.py", ["--municipality", args.municipality])
    run_script("2_extract_osm.py", ["--municipality", args.municipality])

    print("\nPipeline finished successfully.")


if __name__ == "__main__":
    main()

# python pipeline.py --municipality Drachselsried