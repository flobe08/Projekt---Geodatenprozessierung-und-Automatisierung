# Reproduzierbarer Wind-Workflow für eine Gemeinde

Dieses Projekt erstellt einen reproduzierbaren Workflow für eine Gemeinde in
Bayern. Der aktuelle Fokus liegt auf **Windkraft**.

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

Benötigte Systempakete installieren:

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

## Vollständiger Start

Empfohlener Gesamtworkflow:

```bash
bash run_workflow.sh Drachselsried wind
```

## Einzelne Hauptskripte

Daten vorbereiten:

```bash
source .venv-wsl/bin/activate
python3 scripts/prepare_data.py --municipality Drachselsried --technology wind
deactivate
```

QGIS-Projekt und PDF-Karte erzeugen:

```bash
python3 scripts/generate_map.py --municipality Drachselsried --technology wind
```

## Manueller Ablauf ohne Bash-Skript

Wenn du nicht `run_workflow.sh` verwenden willst, kannst du alle Schritte auch
manuell ausführen. Das Ergebnis ist dasselbe.

### 1. Datenvorbereitung

```bash
source .venv-wsl/bin/activate
python3 scripts/prepare_data/0_download_data.py --technology wind
python3 scripts/prepare_data/1_grenzen.py --municipality Drachselsried
python3 scripts/wind/3_clip_wind_planning_areas.py --municipality Drachselsried
deactivate
```

### 2. Kartenerzeugung

```bash
python3 scripts/generate_map/4_create_map_qgis_project.py --municipality Drachselsried --technology wind
python3 scripts/generate_map/5_generate_map_pdf.py --municipality Drachselsried --technology wind
```

Kurz zusammengefasst:

1. `0_download_data.py` lädt die Rohdaten herunter.
2. `1_grenzen.py` extrahiert die Gemeindegrenze.
3. `3_clip_wind_planning_areas.py` schneidet die Windflächen auf die Gemeinde zu.
4. `4_create_map_qgis_project.py` erzeugt das QGIS-Projekt.
5. `5_generate_map_pdf.py` exportiert die PDF-Karte.

## Wichtige Hinweise

- `.venv-wsl` ist eine **lokale** Umgebung und wird **nicht** in Git
  eingecheckt.
- Große Roh- und Ergebnisdaten unter `data/` werden ebenfalls nicht normal in
  Git versioniert.
- Die genaue Schritt-für-Schritt-Anleitung steht in
  [ANLEITUNG.md](ANLEITUNG.md).
