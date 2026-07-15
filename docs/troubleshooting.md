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

Wenn `set: pipefail: invalid option name` erscheint, enthält das Startskript wahrscheinlich Windows-Zeilenenden (CRLF).

Zeilenenden prüfen:

```bash
git ls-files --eol run_workflow.sh
```

Eine korrekte Ausgabe enthält:

```text
i/lf    w/lf    attr/text eol=lf
```

Falls bei der Arbeitsdatei `w/crlf` angezeigt wird, können die Zeilenenden mit
`dos2unix` korrigiert werden:

```bash
sudo apt install dos2unix
dos2unix run_workflow.sh
```

Alternativ ohne zusätzliche Installation:

```bash
sed -i 's/\r$//' run_workflow.sh
```

Anschließend erneut prüfen:

```bash
git ls-files --eol run_workflow.sh
```

Danach kann der Workflow erneut gestartet werden:

```bash
bash run_workflow.sh Drachselsried wind
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
