#!/usr/bin/env bash
set -euo pipefail

# Full workflow wrapper.
# Internally this script calls:
# - scripts/1_prepare_data.py
# - scripts/3_generate_map.py
# The technology-specific steps are triggered there:
# - wind   -> scripts/2_1_wind/
# - solar  -> scripts/2_2_solar/
# - wasser -> scripts/2_3_wasser/ (later)

MUNICIPALITY="${1:-Drachselsried}"
TECHNOLOGY="${2:-wind}"

if [ ! -f ".venv-wsl/bin/activate" ]; then
  echo "Python environment not found: .venv-wsl"
  echo "Create it first with:"
  echo "python3 -m venv .venv-wsl"
  echo "source .venv-wsl/bin/activate"
  echo "pip install -r requirements.txt"
  exit 1
fi

echo "Preparing data for: ${MUNICIPALITY} (${TECHNOLOGY})"
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data.py --municipality "${MUNICIPALITY}" --technology "${TECHNOLOGY}"
deactivate

echo "Generating QGIS project and PDF map for: ${MUNICIPALITY}"
python3 scripts/3_generate_map.py --municipality "${MUNICIPALITY}" --technology "${TECHNOLOGY}"

echo "Workflow finished successfully."
