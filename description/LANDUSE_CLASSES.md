# Landnutzung: Layer und erste Einordnung

Diese Datei dokumentiert die Layer des offiziellen Landnutzungsdatensatzes
und wie sie im Wind-Workflow zunächst eingeordnet werden.

Wichtig: Der Datensatz `landnutzung.gpkg` aus dem Jahr 2026 ist nach
einzelnen Layern aufgebaut. Jeder Layer beschreibt eine Nutzungsgruppe, zum
Beispiel:

```text
ln_landwirtschaft
ln_forstwirtschaft
ln_wohnnutzung
ln_strassenundwegeverkehr
```

Beim Zusammenführen schreibt Skript 3 deshalb das Feld:

```text
source_layer
```

Dieses Feld zeigt, aus welchem Original-Layer ein Objekt stammt. Die spätere
fachliche Einordnung erfolgt deshalb auf Basis von `source_layer`.

## Workflow-Entscheidung

Die Landnutzung wird zuerst vollständig als Flächendatensatz übernommen:

1. `landnutzung.gpkg` wird als offizieller Originaldatensatz geladen.
2. Die Gemeinde-Bounding-Box wird als schneller Vorfilter verwendet.
3. Jeder Polygon-Layer wird exakt mit der Gemeindegrenze zugeschnitten.
4. Die zugeschnittenen Layer werden zusammengeführt.
5. Punkte und Linien werden für den Landnutzungs-Output nicht übernommen.

Beim Zuschnitt können an der Gemeindegrenze technisch Punkt- oder Linienreste
entstehen. Diese werden im Skript bewusst entfernt, weil die Landnutzung als
reiner Flächendatensatz für spätere Ausschlussflächen und Puffer verwendet
wird.

## Output-Dateien

Auf die Gemeinde zugeschnittener Landnutzungsdatensatz:

```text
data/processed/landuse/landnutzung_<gemeinde>.gpkg
```

Beispiel:

```text
data/processed/landuse/landnutzung_drachselsried.gpkg
```

## Layer im Originaldatensatz

Diese Layer werden in `data/raw/landuse/landnutzung.gpkg` erwartet und in
Skript 3 geprüft:

| source_layer | Geometrie | Erste Interpretation im Wind-Workflow |
| --- | --- | --- |
| ln_abbau | Polygon | Manuelle Prüfung |
| ln_aquakulturundfischereiwirtschaft | Polygon | Ausschluss / Gewässernutzung |
| ln_bahnverkehr | Polygon | Ausschluss / Verkehrspuffer |
| ln_bestattung | Polygon | Ausschluss / sensible Nutzung |
| ln_flugverkehr | Polygon | Ausschluss |
| ln_forstwirtschaft | Polygon | Eingeschränkt / möglicher Ausschluss |
| ln_freiluftundnaherholung | Polygon | Ausschluss / Erholung |
| ln_freizeitanlage | Polygon | Ausschluss / Erholung |
| ln_gewerblichedienstleistungen | Polygon | Ausschluss / Gewerbenutzung |
| ln_industrieundverarbeitendesgewerbe | Polygon | Ausschluss / Gewerbe- und Industriefläche |
| ln_kulturundunterhaltung | Polygon | Ausschluss / sensible Nutzung |
| ln_lagerung | Polygon | Manuelle Prüfung |
| ln_landwirtschaft | Polygon | Potenzielle Fläche |
| ln_oeffentlicheeinrichtungen | Polygon | Ausschluss / sensible Nutzung |
| ln_ohnenutzung | Polygon | Manuelle Prüfung / potenziell |
| ln_schiffsverkehr | Polygon | Ausschluss / Verkehr |
| ln_sportanlage | Polygon | Ausschluss / Erholung |
| ln_strassenundwegeverkehr | Polygon | Ausschluss / Verkehrsfläche |
| ln_versorgungundentsorgung | Polygon | Ausschluss / Infrastruktur |
| ln_wasserwirtschaft | Polygon | Ausschluss / Gewässerbezug |
| ln_wohnnutzung | Polygon | Ausschluss / Siedlungspuffer |

## Hinweise

Die Einordnung ist eine erste Arbeitshypothese. Die endgültigen Ausschluss-
und Pufferregeln müssen später mit den gewählten Planungsregeln abgeglichen
werden.

OSM-Straßen bleiben zusätzlich wichtig, obwohl es in der Landnutzung
`ln_strassenundwegeverkehr` gibt. Die Landnutzung beschreibt Verkehrsflächen.
OSM liefert dagegen linienbasierte Straßen mit `highway`-Attributen. Dadurch
können später unterschiedliche Puffer für verschiedene Straßentypen erstellt
werden.
