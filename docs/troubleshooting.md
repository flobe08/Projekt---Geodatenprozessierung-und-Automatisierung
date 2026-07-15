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

Installation prüfen:
```bash
python3 -c "from qgis.core import QgsApplication; print('qgis ok')"
```

Wenn PowerShell Befehle wie `source .venv-wsl/bin/activate` nicht erkennt,
läuft der Befehl wahrscheinlich außerhalb von WSL. Dann zuerst WSL starten:
```powershell
wsl -d Ubuntu
```

Wenn `.venv-wsl/bin/activate` nicht gefunden wird, wurde die virtuelle Umgebung noch nicht erstellt:
```bash
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
pip install -r requirements.txt
deactivate
```

Wenn beim Erstellen der virtuellen Umgebung `ensurepip is not available` erscheint:
```bash
sudo apt install python3-venv
rm -rf .venv-wsl
python3 -m venv .venv-wsl
```

Wenn `pip` nicht gefunden wird:
```bash
sudo apt install python3-pip
```

Wenn `set: pipefail: invalid option name` erscheint, enthält das Startskript wahrscheinlich Windows-Zeilenenden:
```bash
sudo apt install dos2unix
dos2unix run_workflow.sh
```
Alternativ:
```bash
sed -i 's/\r$//' run_workflow.sh
```
Wenn `ModuleNotFoundError: No module named 'qgis'` während der Kartenerstellung erscheint, wird der QGIS-Schritt wahrscheinlich innerhalb der virtuellen Umgebung ausgeführt. Dann die Umgebung verlassen und den Kartenschritt mit dem System-Python starten:
Beispiel Wasser:
```bash
deactivate
python3 scripts/3_generate_map.py --municipality Drachselsried --technology wasser
```

Wenn alte Daten oder Karten neu erzeugt werden sollen:
```bash
rm -rf data/raw
rm -rf data/processed
bash run_workflow.sh Drachselsried wasser
```

Wenn nur eine Technologie neu erzeugt werden soll, können die entsprechenden Technologie- und Kartenordner gelöscht werden. Beispiel für Wasser:
```bash
rm -rf data/processed/2_technology_wasser
rm -rf data/processed/3_maps/*wasser*
rm -rf data/processed/3_qgis_projects/*wasser*
bash run_workflow.sh Drachselsried wasser
```

---

### Overpass-Timeout beim OSM-Download

Wenn beim Schritt `Download OSM network data` ein Fehler wie `Read timed out`, `Overpass endpoint failed` oder `Could not download OSM network data` erscheint, konnte der Overpass-Server die OSM-Abfrage nicht rechtzeitig beantworten.
Das ist meistens ein temporäres Problem des externen Dienstes und kein Fehler im Code. In diesem Fall kann der Workflow später erneut gestartet werden:

```bash
bash run_workflow.sh Drachselsried wind
```
Wenn bereits Zwischenergebnisse erzeugt wurden, kann die Datenvorbereitung mit vorhandenen Outputs fortgesetzt werden:
```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data.py --municipality Drachselsried --technology wind --skip-existing
deactivate
python3 scripts/3_generate_map.py --municipality Drachselsried --technology wind
```
Bei großen Gemeinden kann die Abfrage länger dauern oder häufiger fehlschlagen. In diesem Fall sollte der Workflow zu einem späteren Zeitpunkt erneut ausgeführt werden.