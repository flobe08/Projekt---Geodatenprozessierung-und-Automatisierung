from pathlib import Path
import requests
import zipfile


BASE_DIR = Path(__file__).resolve().parent.parent

BAYERN_OSM_URL = "https://download.geofabrik.de/europe/germany/bayern-latest.osm.pbf"
ALKIS_VERWALTUNG_URL = "https://geodaten.bayern.de/odd/m/4/verwaltung/alkis-verwaltung.zip"

BAYERN_OSM_FILE = BASE_DIR / "data/raw/osm/bayern-latest.osm.pbf"
ALKIS_VERWALTUNG_FILE = BASE_DIR / "data/raw/Verwaltungsgebiet_Bayern/alkis_verwaltungsgebiete.zip"
ALKIS_EXTRACT_DIR = BASE_DIR / "data/raw/Verwaltungsgebiet_Bayern"


def download_file(url: str, output_file: Path) -> None:
    """Download a file if it does not already exist."""

    output_file.parent.mkdir(parents=True, exist_ok=True)

    if output_file.exists():
        print(f"File already exists: {output_file.resolve()}")
        return

    print(f"Downloading: {url}")
    print(f"Saving to: {output_file.resolve()}")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)

    print(f"Saved to: {output_file.resolve()}")


# unpack zip
def unzip_file(zip_file: Path, extract_dir: Path) -> None:
    """Extract a zip file into the given folder."""

    if not zip_file.exists():
        raise FileNotFoundError(f"ZIP file not found: {zip_file}")

    print(f"Extracting: {zip_file.resolve()}")
    print(f"Extracting to: {extract_dir.resolve()}")

    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    print("Extraction finished.")


def main() -> None:
    """Download and extract all required raw datasets."""

    download_file(BAYERN_OSM_URL, BAYERN_OSM_FILE)
    download_file(ALKIS_VERWALTUNG_URL, ALKIS_VERWALTUNG_FILE)

    unzip_file(ALKIS_VERWALTUNG_FILE, ALKIS_EXTRACT_DIR)


if __name__ == "__main__":
    main()