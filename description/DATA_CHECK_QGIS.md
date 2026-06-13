# Manuelle Datenprüfung in QGIS

Diese Datei beschreibt, wie die aktuellen Wind-Daten in QGIS geprüft werden
können. Die Prüfung ist sinnvoll, bevor das QGIS-Projekt und die finale
PDF-Karte erstellt werden.

Der aktuelle Workflow basiert auf:

- Verwaltungsgrenze der Gemeinde
- offiziellen Wind-WFS-Datensätzen aus der Regionalplanung Bayern
- optionalen OSM-Straßen als Kontext


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

1. OpenStreetMap über `Browser > XYZ Tiles > OpenStreetMap` hinzufügen.
2. Rechtsklick auf den Layer `Drachselsried`.
3. `Auf Layer zoomen` auswählen.


## 2. Originale Wind-Datensätze prüfen

Diese beiden Dateien in QGIS laden:

```text
data/raw/wind/wind_vorranggebiete.gpkg
data/raw/wind/wind_vorbehaltsgebiete.gpkg
```

Erfolgreiche Prüfung:

- Beide GeoPackages lassen sich in QGIS öffnen.
- Die Layer liegen räumlich plausibel in Bayern.
- Der Datensatz `wind_vorranggebiete.gpkg` enthält Flächen.
- Der Datensatz `wind_vorbehaltsgebiete.gpkg` kann je nach Region ebenfalls
  Flächen enthalten, muss aber im Gemeindeausschnitt nicht zwingend Treffer
  liefern.

Fachliche Einordnung:

- `wind_vorranggebiete` ist der wichtigste Datensatz für die aktuelle Karte.
- `wind_vorbehaltsgebiete` ist ein ergänzender optionaler Datensatz.

Kurzer Hinweis zur manuellen WFS-Einbindung in QGIS:

1. `Layer > Layer hinzufügen > WFS/OGC API - Features-Layer hinzufügen`
2. Neue Verbindung anlegen
3. URL einfügen:

```text
https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung
```

4. Verbinden
5. Die Wind-Layer auswählen und laden


## 3. Automatisch geclippten Wind-Output prüfen

Nach Skript 3 sollte diese Datei vorhanden sein:

```text
data/processed/wind/drachselsried_wind_layers.gpkg
```

Erwartete Layer:

```text
wind_vorranggebiete_drachselsried
wind_vorbehaltsgebiete_drachselsried
```

Hinweis:

- Wenn für `wind_vorbehaltsgebiete` im Gemeindeausschnitt keine Fläche
  vorhanden ist, wird der Layer trotzdem als leerer Layer mit 0 Features
  geschrieben.
- Das ist nicht automatisch ein Fehler, sondern ein bewusst konstanter Output.

Erfolgreiche Prüfung:

- `wind_vorranggebiete` liegt innerhalb von Drachselsried.
- Die Fläche ist sauber an der Gemeindegrenze abgeschnitten.
- Es gibt keine Flächen weit außerhalb der Gemeinde.
- Die Geometrie wirkt konsistent mit dem Originaldatensatz.
- Der automatische Output wurde sowohl mit dem WFS-Originaldatensatz als auch
  mit der Gemeindegrenze abgeglichen.


## 4. Manuelle Validierung des Wind-Clips in QGIS

Diese Prüfung validiert Skript 3.

Ziel:

```text
Originalen Wind-Datensatz manuell mit der Drachselsried-Grenze zuschneiden
und danach mit dem automatischen Skript-Output vergleichen.
```

`Clip` heißt in der deutschen QGIS-Oberfläche:

```text
Zuschneiden
```


### 4.1 Originalen Vorrang-Datensatz laden

Diese Layer in QGIS laden:

```text
data/raw/wind/wind_vorranggebiete.gpkg
data/processed/boundaries/drachselsried_boundary.gpkg
```


### 4.2 Manuell zuschneiden

1. `Verarbeitung > Werkzeugkiste` öffnen.
2. Werkzeug suchen:

```text
Zuschneiden
```

3. Eingabelayer:

```text
wind_vorranggebiete
```

4. Overlay-Layer:

```text
drachselsried_boundary
```

5. Ergebnis speichern, zum Beispiel:

```text
wind_vorranggebiete_drachselsried_manuell.gpkg
```


### 4.3 Manuellen und automatischen Output vergleichen

Diese beiden Layer in QGIS laden:

```text
wind_vorranggebiete_drachselsried_manuell.gpkg
data/processed/wind/drachselsried_wind_layers.gpkg
```

Erfolgreiche Prüfung:

- Beide Layer decken denselben Bereich in Drachselsried ab.
- Die Flächenformen stimmen räumlich überein.
- Der automatische Output entspricht dem manuell erzeugten Zuschnitt.


## 5. Dokumentierte Verifikation für die spätere Arbeit

Diese Verifikation wurde bereits manuell durchgeführt:

- Der originale Wind-Datensatz wurde manuell in QGIS geladen.
- Der WFS-Datensatz wurde zusätzlich mit der direkten WFS-Einbindung in QGIS
  gegengeprüft.
- Die Gemeindegrenze von Drachselsried wurde manuell geladen.
- Der originale Wind-Datensatz wurde manuell mit der Gemeindegrenze
  zugeschnitten.
- Der manuelle Zuschnitt wurde anschließend mit dem automatischen
  Pipeline-Output überlagert.
- Die Flächen wurden visuell miteinander verglichen.

Ergebnis dieser Verifikation:

- Der automatische Clip der Pipeline stimmt räumlich mit dem manuell
  erzeugten Zuschnitt überein.
- Damit ist der Kernschritt von Skript 3 fachlich nachvollziehbar validiert.

Diese Passage kann später auch in der schriftlichen Arbeit verwendet werden,
zum Beispiel im Abschnitt:

- Methodenvalidierung
- Qualitätssicherung
- Plausibilitätsprüfung der Geodatenverarbeitung


## 6. OSM-Kontextstraßen prüfen

Falls OSM mit `--with-osm-context` geladen wurde, diese Datei in QGIS öffnen:

```text
data/processed/osm_context/drachselsried_osm_context.gpkg
```

Zu prüfender Layer:

```text
osm_context_roads
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
- Die Straßen liegen innerhalb der Gemeinde.
- Die Straßen passen optisch zur OSM-Basiskarte.

Wichtig:

- Diese OSM-Daten sind nur Kontextdaten.
- Sie dienen der Orientierung in QGIS und in der PDF-Karte.
- Sie sind nicht die offizielle Wind-Planungsgrundlage.


## 7. Ergebnis einer erfolgreichen Prüfung

Die Prüfung ist erfolgreich, wenn:

- die Gemeindegrenze von Drachselsried korrekt ist,
- die originalen Wind-Datensätze lesbar sind,
- der automatische Clip in Drachselsried plausibel ist,
- der manuelle Zuschnitt und der automatische Output übereinstimmen,
- optionale OSM-Straßen korrekt als Kontext dargestellt werden,
- die Daten als Grundlage für das QGIS-Projekt und die finale Karte verwendet
  werden können.
