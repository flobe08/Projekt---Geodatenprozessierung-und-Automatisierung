# Anleitung

Diese Datei beschreibt den aktuellen Workflow für das Projekt sauber und in der
richtigen Reihenfolge.

## Aktueller Workflow

Der Wind-Workflow besteht aktuell aus diesen Schritten:

1. Rohdaten herunterladen
2. Gemeindegrenze extrahieren
3. Windflächen auf die Gemeinde zuschneiden
4. QGIS-Projekt erzeugen
5. PDF-Karte exportieren

Hinweis:
Die Dateinummern im Projekt folgen dem bisherigen Projektverlauf. Deshalb gibt
es aktuell bewusst `0`, `1`, `3`, `4` und `5`.

## Verwendete Hauptskripte

### 1. Daten vorbereiten

```bash
source .venv-wsl/bin/activate
python3 scripts/prepare_data.py --municipality Drachselsried --technology wind
deactivate
```

Dieses Skript ruft intern auf:

- `scripts/prepare_data/0_download_data.py`
- `scripts/prepare_data/1_grenzen.py`
- `scripts/wind/3_clip_wind_planning_areas.py`

### 2. Karte erzeugen

```bash
python3 scripts/generate_map.py --municipality Drachselsried --technology wind
```

Dieses Skript ruft intern auf:

- `scripts/generate_map/4_create_map_qgis_project.py`
- `scripts/generate_map/5_generate_map_pdf.py`

### 3. Alles zusammen

```bash
bash run_workflow.sh Drachselsried wind
```

## Manuelle Ausführung Schritt für Schritt

Wenn du jeden Schritt einzeln testen willst:

### Schritt 1: Rohdaten herunterladen

```bash
source .venv-wsl/bin/activate
python3 scripts/prepare_data/0_download_data.py --technology wind
```

### Schritt 2: Gemeindegrenze extrahieren

```bash
python3 scripts/prepare_data/1_grenzen.py --municipality Drachselsried
```

### Schritt 3: Windflächen clippen

```bash
python3 scripts/wind/3_clip_wind_planning_areas.py --municipality Drachselsried
deactivate
```

### Schritt 4: QGIS-Projekt erzeugen

```bash
python3 scripts/generate_map/4_create_map_qgis_project.py --municipality Drachselsried --technology wind
```

### Schritt 5: PDF-Karte erzeugen

```bash
python3 scripts/generate_map/5_generate_map_pdf.py --municipality Drachselsried --technology wind
```

## Was Script 0 aktuell macht

`scripts/prepare_data/0_download_data.py` lädt aktuell:

- die bayerischen Verwaltungsgrenzen
- die offiziellen Wind-WFS-Daten
  - `wind_vorranggebiete`
  - `wind_vorbehaltsgebiete`

## OSM-Kontext

OSM-Kontextdaten sind aktuell **nicht** Teil des normalen Workflows.

Im Code ist nur noch ein kurzer Kommentar als Platzhalter vorhanden, falls
später wieder optionale Kontextdaten ergänzt werden sollen.

## Warum kein `.venv-wsl` ins Git-Repository?

Die `.venv-wsl` ist eine lokale Python-Umgebung und bleibt absichtlich lokal:

- sie ist systemabhängig
- sie kann auf anderen Rechnern kaputt oder unnötig groß sein
- sie wird über `requirements.txt` reproduzierbar neu erstellt

Deshalb ist sie in `.gitignore` ausgeschlossen und soll **nicht** gepusht
werden.

## Hinweis zu `BASE_DIR = SCRIPTS_DIR.parent`

In `scripts/prepare_data.py` wird `BASE_DIR` aktuell nicht benötigt.

Darum ist es dort sinnvoller, nur mit `SCRIPTS_DIR` zu arbeiten. Ein zusätzliches
`BASE_DIR = SCRIPTS_DIR.parent` würde dort im Moment nur ungenutzten Code
einführen.
