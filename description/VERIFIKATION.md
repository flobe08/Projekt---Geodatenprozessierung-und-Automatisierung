# Verifikation der Verarbeitungsschritte

Diese Datei dokumentiert die fachliche Verifikation der aktuellen
Verarbeitungsschritte. Sie ist getrennt von der reinen Bedienanleitung in
QGIS gehalten, damit die Ergebnisse später leichter in die schriftliche Arbeit
übernommen werden können.

Die Struktur ist bereits für drei Technologierichtungen vorbereitet:

- Wind
- Solar
- Wasser

Aktuell ist nur der Bereich **Wind** vollständig umgesetzt und verifiziert.


## 1. Wind

### 1.1 Verifikation der Gemeindegrenze

Verwendeter Datensatz:

- offizieller Verwaltungsgebietsdatensatz Bayern
- daraus wurde die Gemeinde Drachselsried gefiltert

Vorgehen zur Verifikation:

1. Der originale Verwaltungsdatensatz wurde in QGIS geladen.
2. In der Attributtabelle wurde die Gemeinde **Drachselsried** geprüft.
3. Die Gemeinde wurde im Originaldatensatz räumlich lokalisiert.
4. Der von `scripts/prepare_data/1_grenzen.py` erzeugte Output wurde geladen:

```text
data/processed/boundaries/drachselsried_boundary.gpkg
```

5. Der Skript-Output wurde mit dem offiziellen Verwaltungsdatensatz
   überlagert und visuell verglichen.

Ergebnis:

- Der Output des Skripts stimmt räumlich mit der offiziellen Gemeindegrenze
  von Drachselsried überein.
- Damit ist die Extraktion der Gemeindegrenze fachlich plausibel verifiziert.


### 1.2 Verifikation der Wind-WFS-Daten

Verwendete Datensätze:

- `wind_vorranggebiete.gpkg`
- `wind_vorbehaltsgebiete.gpkg`

Quelle:

- WFS Regionalplanung Bayern
- URL:

```text
https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung
```

Vorgehen zur Verifikation:

1. Die automatisch heruntergeladenen WFS-Datensätze wurden in QGIS geöffnet.
2. Die WFS-Layer wurden zusätzlich direkt über die WFS-Verbindung in QGIS
   eingebunden.
3. Beide Darstellungen wurden visuell gegengeprüft.

Ergebnis:

- Die automatisch geladenen GeoPackages entsprechen den direkt eingebundenen
  WFS-Layern.
- Damit ist der Download der offiziellen Winddatensätze fachlich plausibel
  verifiziert.


### 1.3 Verifikation des Clips der Windflächen

Verwendete Datensätze:

- offizieller Wind-Datensatz
- Gemeindegrenze Drachselsried
- automatischer Skript-Output

Automatischer Output:

```text
data/processed/wind/drachselsried_wind_layers.gpkg
```

Vorgehen zur Verifikation:

1. Der originale Wind-Datensatz wurde manuell in QGIS geladen.
2. Die Gemeindegrenze von Drachselsried wurde geladen.
3. Der originale Wind-Datensatz wurde manuell mit der Gemeindegrenze
   zugeschnitten.
4. Der manuelle Zuschnitt wurde mit dem Output von
   `scripts/wind/3_clip_wind_planning_areas.py` überlagert.
5. Die Geometrien wurden visuell verglichen.

Ergebnis:

- Der automatische Skript-Output stimmt räumlich mit dem manuell erzeugten
  Zuschnitt überein.
- Der Clip der Windflächen ist damit fachlich nachvollziehbar verifiziert.


### 1.4 Verifikation der optionalen OSM-Kontextdaten

Verwendeter Datensatz:

- `data/processed/osm_context/drachselsried_osm_context.gpkg`

Vorgehen zur Verifikation:

1. Der Layer `osm_context_roads` wurde in QGIS geladen.
2. Eine OpenStreetMap-Basiskarte wurde ergänzt.
3. Die Straßen wurden visuell mit der Basiskarte verglichen.
4. Die Attribute wurden stichprobenartig geprüft, insbesondere das Feld
   `highway`.

Ergebnis:

- Die OSM-Kontextdaten liegen räumlich plausibel innerhalb der Gemeinde.
- Die Straßenklassen sind nachvollziehbar.
- Die OSM-Daten eignen sich als Kontextlayer, nicht als offizielle
  Planungsgrundlage.


### 1.5 Zusammenfassung Wind

Für den Wind-Workflow wurden die zentralen Schritte verifiziert:

- Gemeindegrenze aus offiziellem Verwaltungsdatensatz
- Windflächen aus offiziellem WFS
- Clip der Windflächen auf die Gemeinde
- optionale OSM-Kontextdaten

Damit ist der aktuelle Wind-Workflow fachlich plausibel und für die weitere
Kartenerstellung geeignet.


## 2. Solar

Noch nicht fachlich verifiziert.

Geplant ist später die Dokumentation von:

- Eingabedatensätzen
- Vergleich Originaldaten vs. Skript-Output
- Verifikation der Zuschnitte und Kartenlayer


## 3. Wasser

Noch nicht fachlich verifiziert.

Geplant ist später die Dokumentation von:

- Eingabedatensätzen
- Vergleich Originaldaten vs. Skript-Output
- Verifikation der Zuschnitte und Kartenlayer
