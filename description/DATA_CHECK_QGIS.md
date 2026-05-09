# Manuelle Datenprüfung in QGIS

Diese Datei beschreibt, wie die heruntergeladenen und verarbeiteten Daten in
QGIS geprüft werden können. Die Prüfung ist sinnvoll, bevor Puffer,
Ausschlussflächen und die finale Karte erstellt werden.

## 1. Gemeindegrenze prüfen

Diese Datei in QGIS laden:

```text
data/processed/boundaries/drachselsried_boundary.gpkg
```

Zu prüfender Layer:

```text
drachselsried_boundary
```

Erfolgreiche Prüfung:

- Es ist nur eine Gemeinde sichtbar.
- Die Gemeinde ist Drachselsried.
- Die Form der Grenze wirkt plausibel.
- Die Grenze liegt korrekt in Bayern.
- Die Grenze passt zur OpenStreetMap-Basiskarte.

Empfohlene Sichtprüfung:

- OpenStreetMap über `Browser > XYZ Tiles > OpenStreetMap` hinzufügen.
- Rechtsklick auf den Layer `Drachselsried`.
- `Auf Layer zoomen` auswählen.

## 2. Originale Landnutzung prüfen

Der originale offizielle Landnutzungsdatensatz wird durch Skript 0 geladen:

```text
data/raw/landuse/landnutzung.gpkg
```

Download-Link:

```text
https://geodaten.bayern.de/odd/m/3/daten/ln/landnutzung.gpkg
```

Erfolgreiche Prüfung:

- Das GeoPackage lässt sich in QGIS öffnen.
- Es sind mehrere Layer mit dem Muster `ln_...` vorhanden.
- Flächenlayer wie `ln_landwirtschaft`, `ln_forstwirtschaft` oder
  `ln_wohnnutzung` sind vorhanden.
- Der Datensatz 2026 enthält die Nutzungsgruppen als einzelne Layer.
- Die spätere Einordnung erfolgt über das im Skript erzeugte Feld
  `source_layer`.

Erwartete Layer im Originaldatensatz:

```text
ln_abbau
ln_aquakulturundfischereiwirtschaft
ln_bahnverkehr
ln_bestattung
ln_flugverkehr
ln_forstwirtschaft
ln_freiluftundnaherholung
ln_freizeitanlage
ln_gewerblichedienstleistungen
ln_industrieundverarbeitendesgewerbe
ln_kulturundunterhaltung
ln_lagerung
ln_landwirtschaft
ln_oeffentlicheeinrichtungen
ln_ohnenutzung
ln_schiffsverkehr
ln_sportanlage
ln_strassenundwegeverkehr
ln_versorgungundentsorgung
ln_wasserwirtschaft
ln_wohnnutzung
```

## 3. Verarbeitete Layer prüfen

Nach Skript 2 und Skript 3 sollten diese Dateien vorhanden sein:

```text
data/processed/osm_highways/drachselsried_osm_highways.gpkg
data/processed/landuse/landnutzung_drachselsried.gpkg
```

Erwartete Layer:

```text
osm_roads
official_landuse
```

Erfolgreiche Prüfung:

- `osm_roads` ist auf Drachselsried zugeschnitten.
- `official_landuse` ist auf Drachselsried zugeschnitten.
- `official_landuse` enthält das Feld `source_layer`.
- `official_landuse` enthält nur Polygon- oder MultiPolygon-Geometrien.
- Punkt- und Linienfragmente aus dem Zuschnitt werden bewusst entfernt, weil
  die Landnutzung als Flächendatensatz verwendet wird.

## 4. Landnutzung manuell in QGIS validieren

Diese Prüfung validiert Skript 3. Ziel ist, denselben Ablauf manuell in QGIS
nachzubauen:

```text
Landnutzungslayer zusammenführen -> Zuschneiden mit Drachselsried
```

`Clip` heißt in der deutschen QGIS-Oberfläche:

```text
Zuschneiden
```

### 4.1 Landnutzungslayer zusammenführen

1. QGIS öffnen.
2. Originale Landnutzung laden:

```text
data/raw/landuse/landnutzung.gpkg
```

3. Gemeindegrenze laden:

```text
data/processed/boundaries/drachselsried_boundary.gpkg
```

4. Werkzeugkiste öffnen:

```text
Verarbeitung > Werkzeugkiste
```

5. Werkzeug suchen:

```text
Vektorlayer zusammenführen
```

6. Alle Landnutzungs-Flächenlayer `ln_...` auswählen.

7. Ergebnis speichern, zum Beispiel:

```text
landnutzung_zusammengefuehrt_manuell.gpkg
```

### 4.2 Landnutzung auf Drachselsried zuschneiden

1. Werkzeugkiste öffnen:

```text
Verarbeitung > Werkzeugkiste
```

2. Werkzeug suchen:

```text
Zuschneiden
```

3. Eingabelayer:

```text
landnutzung_zusammengefuehrt_manuell
```

4. Overlay-Layer:

```text
drachselsried_boundary
```

5. Ergebnis speichern, zum Beispiel:

```text
landnutzung_drachselsried_manuell.gpkg
```

### 4.3 Manuellen und automatischen Output vergleichen

Diese beiden Layer in QGIS laden:

```text
landnutzung_drachselsried_manuell.gpkg
data/processed/landuse/landnutzung_drachselsried.gpkg
```

Erfolgreiche Prüfung:

- Beide Layer decken denselben Gemeindebereich ab.
- Die Flächenformen sind räumlich sehr ähnlich.
- Der Skript-Output enthält nur Flächengeometrien.
- Das Feld `source_layer` ist im Skript-Output vorhanden.
- Linien und Punkte aus dem Originaldatensatz sind bewusst nicht enthalten.

## 5. OSM-Straßen prüfen

Attributtabelle von diesem Layer öffnen:

```text
osm_roads
```

Erfolgreiche Prüfung:

- Der Layer enthält Straßengeometrien.
- Das Feld `highway` ist vorhanden.
- Typische Werte sind zum Beispiel:
  - tertiary
  - residential
  - service
  - track
  - unclassified

OSM-Straßen bleiben trotz Landnutzung wichtig, weil sie Linien sind und über
`highway` verschiedene Pufferregeln ermöglichen.

Empfohlene Sichtprüfung:

1. `data/processed/osm_highways/drachselsried_osm_highways.gpkg` in QGIS laden.
2. Den Layer `osm_roads` aktivieren.
3. OpenStreetMap als Basiskarte hinzufügen.
4. Auf die Gemeindegrenze zoomen.
5. Prüfen, ob die Straßen innerhalb der Gemeinde liegen und zur Basiskarte passen.

Empfohlene Attributprüfung:

1. Rechtsklick auf `osm_roads`.
2. `Attributtabelle öffnen`.
3. Prüfen, ob das Feld `highway` vorhanden ist.
4. Nach `highway` sortieren oder filtern.
5. Typische Werte wie `tertiary`, `residential`, `service`, `track` und
   `unclassified` sollten vorkommen.

Empfohlene Symbolisierung:

1. Rechtsklick auf `osm_roads`.
2. `Eigenschaften` öffnen.
3. `Symbolisierung` auswählen.
4. `Kategorisiert` auswählen.
5. Als Wert `highway` verwenden.
6. `Klassifizieren` klicken.

Damit sieht man, welche Straßenklassen im Untersuchungsgebiet vorkommen.

## 6. Schutz- und Wind-Datensätze prüfen

Optional, aber empfohlen: ausgewählte Rohdaten aus diesen Ordnern laden:

```text
data/raw/schutzgebiete
data/raw/wind/natura2000
data/raw/wind/vogelkulissen_2024
```

Erfolgreiche Prüfung:

- Die Layer lassen sich in QGIS öffnen.
- Die Layer liegen plausibel im Untersuchungsraum.
- Schutzgebiete und Vogelkulissen sind sichtbar, falls sie den Bereich
  betreffen.

## 7. Ergebnis einer erfolgreichen Prüfung

Die Prüfung ist erfolgreich, wenn:

- die Gemeindegrenze von Drachselsried korrekt ist,
- die originale Landnutzung lesbar ist,
- die zusammengeführte Landnutzung erzeugt wurde,
- die zugeschnittene Landnutzung nur Drachselsried abdeckt,
- der OSM-Straßenlayer lesbar und zugeschnitten ist,
- alle Layer mit der OpenStreetMap-Basiskarte übereinstimmen,
- die Daten als Grundlage für Puffer, Ausschlussflächen und die finale Karte
  verwendet werden können.
