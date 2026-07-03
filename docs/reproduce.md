# Workflow reproduzieren

Die Pipeline ist so aufgebaut, dass sie vollständig neu ausgeführt werden kann. Dabei werden Rohdaten erneut heruntergeladen, Zwischenergebnisse neu berechnet und die QGIS-Projekte sowie Karten neu erzeugt.

## Vollständig neu starten

Um alle vorhandenen Daten und Ergebnisse zu löschen:

```bash
rm -rf data/raw
rm -rf data/processed
```

Danach kann der Workflow erneut gestartet werden:
```bash
bash run_workflow.sh Drachselsried wasser
```

## Nur eine Technologie neu erzeugen
Wenn nur die Ergebnisse einer Technologie neu erzeugt werden sollen, können die entsprechenden verarbeiteten Daten gelöscht werden.
Beispiel für Wasser:

```bash
rm -rf data/processed/2_technology_wasser
rm -rf data/processed/3_maps/*wasser*
rm -rf data/processed/3_qgis_projects/*wasser*
bash run_workflow.sh Drachselsried wasser
```

## Erwartete Ausgaben
Nach erfolgreicher Ausführung werden die Ergebnisse unter `data/processed/` gespeichert.
Wichtige Ausgabeordner sind:

```text
data/processed/1_base_boundaries/
data/processed/1_base_protection_areas/
data/processed/2_technology_wind/
data/processed/2_technology_solar/
data/processed/2_technology_wasser/
data/processed/3_qgis_projects/
data/processed/3_maps/
```
Die finale Karte liegt im Ordner:
```text
data/processed/3_maps/
```
Das QGIS-Projekt liegt im Ordner: 
```text
data/processed/3_qgis_projects/
```

## Beispielausgabe
Für den Aufruf
```bash
bash run_workflow.sh Drachselsried wasser
```
werden unter anderem folgende Dateien erzeugt:
```text
data/processed/3_maps/drachselsried_map_wasser.pdf
data/processed/3_qgis_projects/drachselsried_map_wasser.qgz
```
