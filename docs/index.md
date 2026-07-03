# Reproduzierbare Geodatenpipeline

Diese Dokumentation beschreibt, wie die entwickelte Geodatenpipeline installiert, ausgeführt und reproduziert werden kann.

Die Pipeline verarbeitet amtliche Geodaten und OpenStreetMap-Daten für eine ausgewählte Gemeinde in Bayern. Für die Technologien Wind, Solar und Wasser werden relevante Eingangsdatensätze automatisch heruntergeladen, vorbereitet, harmonisiert und in strukturierte Ausgabeformate überführt. Zusätzlich werden QGIS-Projekte und finale Karten erzeugt.

Die Pipeline ist so aufgebaut, dass sie mit möglichst geringem manuellem Aufwand für unterschiedliche Gemeinden erneut ausgeführt werden kann.

## Unterstützte Technologien

- `wind`
- `solar`
- `wasser`

## Beispiel

```bash
bash run_workflow.sh Drachselsried wasser
```