#!/usr/bin/env bash
set -euo pipefail

MUNICIPALITY="${1:-Drachselsried}"
TECHNOLOGY="${2:-wind}"
EXTRA_ARGS="${3:-}"

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
python3 scripts/prepare_data.py --municipality "${MUNICIPALITY}" --technology "${TECHNOLOGY}" ${EXTRA_ARGS}
deactivate

echo "Generating QGIS project and PDF map for: ${MUNICIPALITY}"
python3 scripts/generate_map.py --municipality "${MUNICIPALITY}" --technology "${TECHNOLOGY}"

echo "Workflow finished successfully."
