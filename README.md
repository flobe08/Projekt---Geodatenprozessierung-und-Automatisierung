# Reproduzierbarer Energie-Workflow für eine Gemeinde

Dieses Projekt erstellt einen reproduzierbaren Geodaten-Workflow für eine
ausgewählte Gemeinde in Bayern. Aktuell ist der **Wind-Workflow**
durchgängig umgesetzt. Der **Solar-Workflow** wird vorbereitet und basiert auf
OSM-Verkehrsachsen sowie rechtlichen 200-m- und 500-m-Pufferzonen.

## Setup

Empfohlenes System:

- Windows mit **WSL / Ubuntu**
- QGIS in WSL installiert

WSL starten:

```powershell
wsl -d Ubuntu
```

In den Projektordner wechseln:

```bash
cd "/mnt/e/Eigene Daten/Studium/THD/Module/Semester 6/Geodatenprozessierung und Automatisierung/Projekt/Projekt---Geodatenprozessierung-und-Automatisierung"
```

Systempakete installieren:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip qgis python3-qgis
```

Python-Umgebung für die Datenvorbereitung anlegen:

```bash
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
pip install -r requirements.txt
deactivate
```

## Schnellstart

Empfohlener Gesamtworkflow:

```bash
bash run_workflow.sh Drachselsried wind
```

## Hauptskripte

Daten vorbereiten:

```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data.py --municipality Drachselsried --technology wind
deactivate
```

QGIS-Projekt und PDF-Karte erzeugen:

```bash
python3 scripts/3_generate_map.py --municipality Drachselsried --technology wind
```

## Manuelle Ausführung ohne Bash-Skript

Wenn du jeden Schritt einzeln starten willst, erreichst du dasselbe Ergebnis
mit diesen Befehlen.

### Wind

```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data/1_download_data.py --technology wind
python3 scripts/1_prepare_data/2_extract_municipality_boundary.py --municipality Drachselsried
python3 scripts/2_1_wind/1_clip_wind_planning_areas.py --municipality Drachselsried
deactivate
python3 scripts/3_generate_map/1_create_map_qgis_project.py --municipality Drachselsried --technology wind
python3 scripts/3_generate_map/2_generate_map_pdf.py --municipality Drachselsried --technology wind
```

### Solar

```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data/1_download_data.py --technology solar
python3 scripts/1_prepare_data/2_extract_municipality_boundary.py --municipality Drachselsried
python3 scripts/2_2_solar/1_download_osm_transport_data.py --municipality Drachselsried
python3 scripts/2_2_solar/3_prepare_solar_layers.py --municipality Drachselsried
deactivate
python3 scripts/3_generate_map/1_create_map_qgis_project.py --municipality Drachselsried --technology solar
python3 scripts/3_generate_map/2_generate_map_pdf.py --municipality Drachselsried --technology solar
```

## Wichtige Hinweise

- `.venv-wsl` ist eine **lokale** Umgebung und wird **nicht** in Git
  eingecheckt.
- Große Roh- und Ergebnisdaten unter `data/` werden ebenfalls nicht normal in
  Git versioniert.
- Die genaue Schritt-für-Schritt-Anleitung steht in
  [ANLEITUNG.md](ANLEITUNG.md).
- Die manuelle Datenprüfung und Verifikation steht in
  [description/VERIFIKATION.md](description/VERIFIKATION.md).
