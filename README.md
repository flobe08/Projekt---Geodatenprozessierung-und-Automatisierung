# Reproduzierbarer Energie-Workflow für eine Gemeinde

Dieses Projekt erstellt für eine ausgewählte bayerische Gemeinde automatisch
QGIS-Projekte und PDF-Karten für die Technologien **Wind**, **Solar** und
**Wasser**. Das README beschreibt Setup und Ausführung der Pipeline. 

## Dokumentation

Eine ausführlichere technische Dokumentation zu Installation, Ausführung,
Reproduktion und Fehlerbehebung befindet sich in MkDocs.

Die Dokumentation kann lokal gestartet werden mit:

```bash
source .venv-wsl/bin/activate
mkdocs serve
```
Falls für MkDocs eine eigene virtuelle Umgebung verwendet wird, muss diese
vorher aktiviert werden.

Die fachliche Beschreibung von Methodik, Datengrundlagen und Ergebnissen erfolgt
in der beigefügten Studienarbeit.

---

## Setup

Empfohlenes System:

- Windows mit **WSL / Ubuntu**
- QGIS in WSL installiert
- verwendete QGIS-Version im Projekt: **QGIS 4.0 Norrköping**

### Projekt herunterladen

Projekt herunterladen, zum Beispiel im gewünschten Arbeitsordner:

```powershell
git clone https://github.com/flobe08/Projekt---Geodatenprozessierung-und-Automatisierung.git
cd Projekt---Geodatenprozessierung-und-Automatisierung
```

Für die Ausführung des Workflows unter Windows wird WSL mit Ubuntu verwendet.

### WSL prüfen und starten

Zunächst prüfen, ob bereits eine WSL-Distribution installiert ist:

```powershell
wsl -l -v
```

#### Fall A: Ubuntu ist bereits installiert

Wenn `Ubuntu` bereits angezeigt wird, kann WSL direkt gestartet werden:

```powershell
wsl -d Ubuntu
```

#### Fall B: Ubuntu ist noch nicht installiert

Falls Ubuntu noch nicht installiert ist, kann es mit folgendem Befehl installiert
werden:

```powershell
wsl --install -d Ubuntu
```

Nach der Installation muss das Terminal gegebenenfalls neu geöffnet werden.
Anschließend kann Ubuntu gestartet werden mit:

```powershell
wsl -d Ubuntu
```

### Projektordner in WSL öffnen

In den Projektordner wechseln. Wenn das Projekt auf einem Windows-Laufwerk
liegt, wird es in WSL über `/mnt/<laufwerk>/...` erreicht, zum Beispiel:

```bash
cd "/mnt/e/Eigene Daten/Studium/THD/Module/Semester 6/Geodatenprozessierung und Automatisierung/Projekt/Projekt---Geodatenprozessierung-und-Automatisierung"
```

Wenn das Projekt direkt in WSL geklont wurde:

```bash
cd Projekt---Geodatenprozessierung-und-Automatisierung
```

### Systempakete installieren

Die benötigten Systempakete werden in WSL installiert:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip qgis python3-qgis
```

### Python-Umgebung anlegen

Python-Umgebung für die Datenvorbereitung anlegen:

```bash
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
pip install -r requirements.txt
deactivate
```

Der Schritt `pip install -r requirements.txt` kann je nach Internetverbindung
und System einige Zeit dauern, da alle benötigten Python-Pakete installiert
werden.

### Installation prüfen

```bash
python3 --version
qgis --version
source .venv-wsl/bin/activate
python3 -c "import geopandas; print('geopandas ok')"
deactivate
python3 -c "from qgis.core import QgsApplication; print('qgis ok')"
```

### Hinweis zur Python-Umgebung

- Die Datenvorbereitung läuft in `.venv-wsl`.
- Die Kartenerzeugung läuft außerhalb von `.venv-wsl` mit dem
  System-/QGIS-Python.
- Deshalb wird vor `scripts/3_generate_map.py` immer `deactivate` ausgeführt.

---

## Ausführung

### Gesamtworkflow über Bash-Skript

Der einfachste Weg ist das Bash-Skript `run_workflow.sh`. Es erwartet zwei
Parameter: Gemeinde und Technologie.

```bash
bash run_workflow.sh <gemeinde> <technologie>
```

Parameter:

| Parameter | Bedeutung | Mögliche Werte |
| --- | --- | --- |
| `<gemeinde>` | Name der zu verarbeitenden Gemeinde | z. B. `Drachselsried`, `Bodenmais`, `München` |
| `<technologie>` | Technologie-Workflow | `wind`, `solar`, `wasser` |

Beispiele:

```bash
bash run_workflow.sh Drachselsried wind
bash run_workflow.sh Drachselsried solar
bash run_workflow.sh Drachselsried wasser
```

Hinweis: Der erste vollständige Durchlauf kann deutlich länger dauern, weil
mehrere große Bayern-Datensätze geladen und verarbeitet werden. Vor allem die
amtliche Landnutzung wird lokal als großer Datensatz vorgehalten.

### Ausführung über die beiden Einstiegsskripte

Alternativ können Datenvorbereitung und Kartenerzeugung getrennt gestartet
werden.

```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data.py --municipality <gemeinde> --technology <technologie>
deactivate
python3 scripts/3_generate_map.py --municipality <gemeinde> --technology <technologie>
```

Parameter:

| Parameter | Bedeutung | Mögliche Werte |
| --- | --- | --- |
| `<gemeinde>` | Name der zu verarbeitenden Gemeinde | z. B. `Drachselsried`, `Bodenmais`, `München` |
| `<technologie>` | Technologie-Workflow | `wind`, `solar`, `wasser` |

Beispiel:

```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data.py --municipality Drachselsried --technology wind
deactivate
python3 scripts/3_generate_map.py --municipality Drachselsried --technology wind
```

Wenn bereits erzeugte Zwischenergebnisse wiederverwendet werden sollen, kann
die Datenvorbereitung mit `--skip-existing` gestartet werden:

```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data.py --municipality Drachselsried --technology wind --skip-existing
deactivate
python3 scripts/3_generate_map.py --municipality Drachselsried --technology wind
```

---

## Ergebnisse

Die finalen Ausgaben werden unter `data/processed/` erzeugt.

Wichtige Ergebnisordner sind:

```text
data/processed/3_maps/
data/processed/3_qgis_projects/
```
Die PDF-Karten liegen in `3_maps`, die QGIS-Projekte in `3_qgis_projects`.

Weitere Informationen zur vollständigen Ausgabe- und Ordnerstruktur stehen in der MkDocs-Dokumentation.