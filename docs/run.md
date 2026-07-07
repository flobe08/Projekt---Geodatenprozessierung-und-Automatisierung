# Workflow ausführen

Der gesamte Workflow wird über das Skript `run_workflow.sh` gestartet.

## Allgemeiner Aufruf

```bash
bash run_workflow.sh <Gemeinde> <Technologie>
```

### Parameter

| Parameter | Bedeutung | Beispiel |
|---|---|---|
| `<Gemeinde>` | Name der Gemeinde, die verarbeitet werden soll | `Drachselsried` |
| `<Technologie>` | Energieform, für die der Workflow ausgeführt wird | `wind`, `solar`, `wasser` |

### Wind ausführen
```bash
bash run_workflow.sh Drachselsried wind
```

### Solar ausführen
```bash
bash run_workflow.sh Drachselsried solar
```

### Wasser ausführen
```bash
bash run_workflow.sh Drachselsried wasser
```

### Andere Gemeinde ausführen
Die Pipeline kann auch für eine andere bayerische Gemeinde gestartet werden:
```bash
bash run_workflow.sh München wasser
```
Der Gemeindename muss in den verwendeten Verwaltungsgrenzen enthalten sein.


### Ausführung über die beiden Einstiegsskripte

Alternativ können Datenvorbereitung und Kartenerzeugung getrennt gestartet werden. 
Diese Variante ist hilfreich, wenn beide Schritte separat geprüft werden sollen.

```bash
source .venv-wsl/bin/activate
python3 scripts/1_prepare_data.py --municipality <Gemeinde> --technology <Technologie>
deactivate
python3 scripts/3_generate_map.py --municipality <Gemeinde> --technology <Technologie>
```

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