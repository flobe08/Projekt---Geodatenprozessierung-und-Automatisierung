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