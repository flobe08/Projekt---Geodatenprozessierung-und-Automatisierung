# Reproduzierbarer Energie-Workflow fÃ¼r eine Gemeinde

Dieses Projekt erstellt einen reproduzierbaren Geodaten-Workflow fÃ¼r eine
ausgewÃ¤hlte Gemeinde in Bayern. Aktuell ist der **Wind-Workflow**
durchgÃ¤ngig umgesetzt. Der **Solar-Workflow** wird vorbereitet und basiert auf
OSM-Verkehrsachsen sowie rechtlichen 200-m- und 500-m-Pufferzonen.

## Zentrale Fragestellung

Welche rÃ¤umlichen Potenzial- und KonfliktflÃ¤chen fÃ¼r erneuerbare Energien
lassen sich fÃ¼r eine Gemeinde automatisiert aus offenen Geodaten ableiten und
kartografisch darstellen?

Das Projekt beantwortet damit nicht die Frage, wo eine Anlage rechtsverbindlich
genehmigt werden darf. Ziel ist eine reproduzierbare Pipeline, die fÃ¼r eine
ausgewÃ¤hlte bayerische Gemeinde relevante offene Geodaten automatisch sammelt,
harmonisiert, zuschneidet und kartografisch ausgibt.

Die Karten zeigen, welche FlÃ¤chen aus Sicht von Raumplanung,
Energieinfrastruktur, Landnutzung und Naturschutz fÃ¼r Windenergie,
FreiflÃ¤chen-Photovoltaik und wasserbezogene Planung besonders relevant oder
konfliktbehaftet sind.

Die einzelnen Karten beantworten dabei:

- **Windkarte:** Wo liegen offizielle regionalplanerische
  WindenergieflÃ¤chen innerhalb der Gemeinde und welche allgemeinen bzw.
  windspezifischen RestriktionsflÃ¤chen Ã¼berschneiden oder begrenzen diese?
- **Solarkarte:** Wo liegen potenziell relevante
  FreiflÃ¤chen-Photovoltaikbereiche in der Gemeinde und wie verhalten sie sich
  zu 200-m-/500-m-Randstreifen sowie Naturschutz-KonfliktflÃ¤chen?
- **Wasserkarte:** Welche wasserbezogenen Infrastruktur-, Schutz- und
  KonfliktflÃ¤chen liegen innerhalb der Gemeinde und welche Bereiche sind fÃ¼r
  eine weitere wasserbezogene Energie- oder Planungsanalyse relevant?

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

Python-Umgebung fÃ¼r die Datenvorbereitung anlegen:

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

Hinweis:

- Der erste vollstÃ¤ndige Durchlauf kann deutlich lÃ¤nger dauern.
- Grund dafÃ¼r sind mehrere groÃŸe Bayern-DatensÃ¤tze.
- Vor allem die offizielle Landnutzung wird lokal als groÃŸer Datensatz
  vorgehalten und liegt ungefÃ¤hr im Bereich von 5 bis 6 GB.

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

## Manuelle AusfÃ¼hrung ohne Bash-Skript

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
python3 scripts/2_2_solar/4_prepare_solar_osm_streets.py --municipality Drachselsried
python3 scripts/2_2_solar/2_prepare_solar_corridor_layers.py --municipality Drachselsried
python3 scripts/2_2_solar/3_prepare_solar_landuse.py --municipality Drachselsried
deactivate
python3 scripts/2_2_solar/1_download_solar_reference_wms.py --municipality Drachselsried
python3 scripts/3_generate_map/1_prepare_overview_layers.py --municipality Drachselsried
python3 scripts/3_generate_map/2_create_map_qgis_project.py --municipality Drachselsried --technology solar
python3 scripts/3_generate_map/3_generate_map_pdf.py --municipality Drachselsried --technology solar
```

## Wichtige Hinweise

- `.venv-wsl` ist eine **lokale** Umgebung und wird **nicht** in Git
  eingecheckt.
- GroÃŸe Roh- und Ergebnisdaten unter `data/` werden ebenfalls nicht normal in
  Git versioniert.
- Die genaue Schritt-fÃ¼r-Schritt-Anleitung steht in
  [ANLEITUNG.md](ANLEITUNG.md).
- Die manuelle DatenprÃ¼fung und Verifikation steht in
  [description/VERIFIKATION.md](description/VERIFIKATION.md).
- Die Workflow-Diagramme mit den Log-Step-Namen stehen in
  [description/WORKFLOW_DIAGRAMME.md](description/WORKFLOW_DIAGRAMME.md).
