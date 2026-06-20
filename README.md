# Reproduzierbarer Energie-Workflow für eine Gemeinde

Dieses Projekt erstellt einen reproduzierbaren Geodaten-Workflow für eine
ausgewählte Gemeinde in Bayern. Aktuell ist der **Wind-Workflow** als
Referenzworkflow durchgängig umgesetzt. Der **Solar-Workflow** ist strukturell
angebunden und basiert auf OSM-Verkehrsachsen, amtlichen WMS-Referenzlayern
sowie rechtlichen 200-m- und 500-m-Pufferzonen. **Wasser** ist als
Platzhalter/TODO vorbereitet.

## Zentrale Fragestellung

Welche räumlichen Potenzial- und Konfliktflächen für erneuerbare Energien
lassen sich für eine Gemeinde automatisiert aus offenen Geodaten ableiten und
kartografisch darstellen?

Das Projekt beantwortet damit nicht die Frage, wo eine Anlage rechtsverbindlich
genehmigt werden darf. Ziel ist eine reproduzierbare Pipeline, die für eine
ausgewählte bayerische Gemeinde relevante offene Geodaten automatisch sammelt,
harmonisiert, zuschneidet und kartografisch ausgibt.

Die Karten zeigen, welche Flächen aus Sicht von Raumplanung,
Energieinfrastruktur, Landnutzung und Naturschutz für Windenergie,
Freiflächen-Photovoltaik und wasserbezogene Planung besonders relevant oder
konfliktbehaftet sind.

Die einzelnen Karten beantworten dabei:

- **Windkarte:** Wo liegen offizielle regionalplanerische
  Windenergieflächen innerhalb der Gemeinde und welche allgemeinen bzw.
  windspezifischen Restriktionsflächen überschneiden oder begrenzen diese?
- **Solarkarte:** Wo liegen potenziell relevante
  Freiflächen-Photovoltaikbereiche in der Gemeinde und wie verhalten sie sich
  zu 200-m-/500-m-Randstreifen sowie Naturschutz-Konfliktflächen?
- **Wasserkarte:** Welche wasserbezogenen Infrastruktur-, Schutz- und
  Konfliktflächen liegen innerhalb der Gemeinde und welche Bereiche sind für
  eine weitere wasserbezogene Energie- oder Planungsanalyse relevant?

## Setup

Empfohlenes System:

- Windows mit **WSL / Ubuntu**
- QGIS in WSL installiert
- Verwendete QGIS-Version im Projekt: **QGIS 4.0 Norrköping**

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

Installation prüfen:

```bash
python3 --version
qgis --version
source .venv-wsl/bin/activate
python3 -c "import geopandas; print('geopandas ok')"
deactivate
python3 -c "from qgis.core import QgsApplication; print('qgis ok')"
```

Wichtig zur Python-Umgebung:

- Die Datenvorbereitung läuft in der lokalen Umgebung `.venv-wsl`.
- Die Kartenerzeugung läuft außerhalb von `.venv-wsl` mit dem System-/QGIS-Python.
- Deshalb wird vor `scripts/3_generate_map.py` immer `deactivate` ausgeführt.
- Wenn `from qgis.core import QgsApplication` fehlschlägt, fehlen meistens
  `qgis` oder `python3-qgis`.

## Schnellstart

Empfohlener Gesamtworkflow:

```bash
bash run_workflow.sh Drachselsried wind
```

Hinweis:

- Der erste vollständige Durchlauf kann deutlich länger dauern.
- Grund dafür sind mehrere große Bayern-Datensätze.
- Vor allem die offizielle Landnutzung wird lokal als großer Datensatz
  vorgehalten und liegt ungefähr im Bereich von 5 bis 6 GB.

## Ergebnisstruktur

Die automatisch erzeugten Daten liegen unter `data/processed/`. Die Ordner sind
nach Verarbeitungsebene nummeriert, damit Basisdaten, technologiespezifische
Zwischenergebnisse und finale Ausgaben klar getrennt bleiben:

```text
data/processed/
  1_base_boundaries/
  1_base_landuse/
  1_base_osm_streets/
  1_base_overview/
  1_base_protection_areas/

  2_technology_wind/
  2_technology_solar/

  3_qgis_projects/
  3_maps/
```

Im Solar-Ordner werden die Korridorgrundlage und die amtlichen
WMS-Referenzbilder zusätzlich getrennt abgelegt:

```text
data/processed/2_technology_solar/corridor/
data/processed/2_technology_solar/reference/
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
python3 scripts/1_prepare_data/3_build_protection_layers.py --municipality Drachselsried
python3 scripts/1_prepare_data/4_clip_landuse.py --municipality Drachselsried
python3 scripts/1_prepare_data/5_download_osm_network_data.py --municipality Drachselsried --technology wind
python3 scripts/2_1_wind/4_prepare_wind_osm_streets.py --municipality Drachselsried
python3 scripts/2_1_wind/1_clip_wind_planning_areas.py --municipality Drachselsried
python3 scripts/2_1_wind/2_prepare_wind_landuse.py --municipality Drachselsried
python3 scripts/2_1_wind/3_build_wind_landuse_buffers.py --municipality Drachselsried
python3 scripts/2_1_wind/5_build_wind_exclusion_layer.py --municipality Drachselsried
deactivate
python3 scripts/3_generate_map/1_prepare_overview_layers.py --municipality Drachselsried
python3 scripts/3_generate_map/2_create_map_qgis_project.py --municipality Drachselsried --technology wind
python3 scripts/3_generate_map/3_generate_map_pdf.py --municipality Drachselsried --technology wind
```

### Solar

```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data/1_download_data.py --technology solar
python3 scripts/1_prepare_data/2_extract_municipality_boundary.py --municipality Drachselsried
python3 scripts/1_prepare_data/3_build_protection_layers.py --municipality Drachselsried
python3 scripts/1_prepare_data/4_clip_landuse.py --municipality Drachselsried
python3 scripts/1_prepare_data/5_download_osm_network_data.py --municipality Drachselsried --technology solar
python3 scripts/2_2_solar/1_prepare_solar_corridor_layers.py --municipality Drachselsried
python3 scripts/2_2_solar/2_prepare_solar_landuse.py --municipality Drachselsried
deactivate
python3 scripts/2_2_solar/3_download_solar_reference_wms.py --municipality Drachselsried
python3 scripts/3_generate_map/1_prepare_overview_layers.py --municipality Drachselsried
python3 scripts/3_generate_map/2_create_map_qgis_project.py --municipality Drachselsried --technology solar
python3 scripts/3_generate_map/3_generate_map_pdf.py --municipality Drachselsried --technology solar
```

Hinweis: `3_download_solar_reference_wms.py` nutzt PyQGIS und wird deshalb
außerhalb der `.venv-wsl` mit dem QGIS-/System-Python ausgeführt.

## Troubleshooting

Wenn `python3` nicht gefunden wird:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Wenn `qgis` oder `from qgis.core import QgsApplication` nicht funktioniert:

```bash
sudo apt update
sudo apt install qgis python3-qgis
```

Wenn PowerShell Befehle wie `source .venv-wsl/bin/activate` nicht erkennt,
läuft der Befehl wahrscheinlich außerhalb von WSL. Dann zuerst WSL starten:

```powershell
wsl -d Ubuntu
```

## Wichtige Hinweise

- `.venv-wsl` ist eine **lokale** Umgebung und wird **nicht** in Git
  eingecheckt.
- Große Roh- und Ergebnisdaten unter `data/` werden ebenfalls nicht normal in
  Git versioniert.
- Die genaue Schritt-für-Schritt-Anleitung steht in
  [Anleitung.md](Anleitung.md).
- Die manuelle Datenprüfung und Verifikation steht in
  [description/VERIFIKATION.md](description/VERIFIKATION.md).
- Die Workflow-Diagramme mit den Log-Step-Namen stehen in
  [description/WORKFLOW_DIAGRAMME.md](description/WORKFLOW_DIAGRAMME.md).
