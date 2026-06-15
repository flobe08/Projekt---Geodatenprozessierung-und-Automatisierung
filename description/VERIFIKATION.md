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

## 1. Allgemein

### 1.1 Verifikation der Gemeindegrenze

Verwendeter Datensatz:

- offizieller Verwaltungsgebietsdatensatz Bayern
- daraus wurde die Gemeinde Drachselsried gefiltert

Vorgehen zur Verifikation:

1. Der originale Verwaltungsdatensatz wurde in QGIS geladen.
2. In der Attributtabelle wurde die Gemeinde **Drachselsried** geprüft.
3. Die Gemeinde wurde im Originaldatensatz räumlich lokalisiert.
4. Der aktuelle Skript-Output wurde geladen:

```text
data/processed/boundaries/drachselsried_boundary.gpkg
```

5. Der Skript-Output wurde mit dem offiziellen Verwaltungsdatensatz
   überlagert und visuell verglichen.

Ergebnis:

- Der Output des Skripts stimmt räumlich mit der offiziellen Gemeindegrenze
  von Drachselsried überein.
- Damit ist die Extraktion der Gemeindegrenze fachlich plausibel verifiziert.

Historische Referenz:

```text
# TODO: nicht mehr verwendet
scripts/prepare_data/1_grenzen.py
```

Aktuelle Referenz:

```text
scripts/1_prepare_data/2_extract_municipality_boundary.py
```

## 2. Allgemeine Schutzgebiete

### 2.1 Verifikation der Schutzgebietsdaten

Verwendete Datensätze:

- allgemeine Schutzgebietsdatensätze des LfU Bayern
- Natura-2000-Datensätze FFH und Vogelschutz
- automatischer Skript-Output:

```text
data/processed/schutzgebiete/drachselsried_naturschutz_allgemein_hart.gpkg
data/processed/schutzgebiete/drachselsried_naturschutz_allgemein_weich.gpkg
data/processed/schutzgebiete/drachselsried_naturschutz_wind.gpkg
```

Vorgehen zur Verifikation:

1. Die originalen Schutzgebietsdatensätze wurden in QGIS geladen.
2. Die Gemeindegrenze von Drachselsried wurde ergänzt.
3. Die flächenhaften Datensätze wurden manuell mit der Gemeinde verglichen.
4. Der automatische Output aus
   `scripts/1_prepare_data/3_build_protection_layers.py` wurde geladen.
5. Die zusammengeführten Ergebnislayer
   - `naturschutz_allgemein_hart_merged`
   - `naturschutz_allgemein_weich_merged`
   - `naturschutz_wind_merged`
   wurden mit den Originaldaten visuell überlagert.

Ergebnis:

- Die automatisierten Schutzgebietslayer sind räumlich plausibel.
- Die Einteilung in harte und weiche Restriktionen ist methodisch nachvollziehbar.
- Großräumige Schutzkategorien wie Naturparke, Landschaftsschutzgebiete und
  Biosphärenreservate werden bewusst nicht automatisch als absolute
  Ausschlussflächen behandelt.

Methodischer Hinweis:

- punktförmige Schutzobjekte bleiben weiterhin dokumentiert und verfügbar
- sie werden als eigene geclippte Punktlayer mit ausgegeben
- für den zusammengeführten harten Ausschlusslayer werden aber weiterhin die
  flächenhaften Schutzgebietsdaten bevorzugt

## 3. Wind

### 3.1 Verifikation der Wind-WFS-Daten

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

### 3.2 Verifikation des Clips der Windflächen

Verwendete Datensätze:

- offizieller Wind-Datensatz
- Gemeindegrenze Drachselsried
- automatischer Skript-Output

Automatischer Output:

```text
data/processed/wind/drachselsried_wind_layers.gpkg
```

Relevante Layer:

- `wind_vorranggebiete_drachselsried`
- `wind_vorbehaltsgebiete_drachselsried`
- `wind_spezifisch`

Vorgehen zur Verifikation:

1. Der originale Wind-Datensatz wurde manuell in QGIS geladen.
2. Die Gemeindegrenze von Drachselsried wurde geladen.
3. Der originale Wind-Datensatz wurde manuell mit der Gemeindegrenze
   zugeschnitten.
4. Der manuelle Zuschnitt wurde mit dem Output des aktuellen Skripts
   überlagert.
5. Die Geometrien wurden visuell verglichen.

Ergebnis:

- Der automatische Skript-Output stimmt räumlich mit dem manuell erzeugten
  Zuschnitt überein.
- Der Clip der Windflächen ist damit fachlich nachvollziehbar verifiziert.
- Der Layer `wind_spezifisch` fasst die technologiespezifischen Windflächen
  für eine einfache QGIS-Prüfung zusammen.

Historische Referenz:

```text
# TODO: nicht mehr verwendet
scripts/wind/3_clip_wind_planning_areas.py
```

Aktuelle Referenz:

```text
scripts/2_1_wind/1_clip_wind_planning_areas.py
```

### 3.3 Verifikation der optionalen OSM-Kontextdaten

Verwendeter Datensatz:

```text
data/processed/osm_context/drachselsried_osm_context.gpkg
```

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

Hinweis:

```text
# TODO: nicht mehr verwendet
Die optionalen OSM-Kontextdaten sind aktuell nicht mehr Teil des aktiven
Wind-Workflows, sollen aber als frühere Arbeitsschritte dokumentiert bleiben.
```

### 3.4 Zusammenfassung Wind

Für den Wind-Workflow wurden die zentralen Schritte verifiziert:

- Gemeindegrenze aus offiziellem Verwaltungsdatensatz
- Windflächen aus offiziellem WFS
- Clip der Windflächen auf die Gemeinde
- optionale OSM-Kontextdaten aus einem früheren Workflow-Schritt

Damit ist der aktuelle Wind-Workflow fachlich plausibel und für die weitere
Kartenerstellung geeignet.

## 4. Solar

### 4.1 Verifikation der OSM-Verkehrsachsen

Verwendete Datensätze:

- `data/processed/osm_transport/drachselsried_osm_transport.gpkg`
- amtliche OSM-Basiskarte in QGIS

Vorgehen zur Verifikation:

1. Der Analysekontext-Layer wurde geladen.
2. Die OSM-Verkehrsachsen wurden geladen.
3. Die geladenen Schienen- und Straßenachsen wurden mit der OSM-Basiskarte
   visuell abgeglichen.
4. Geprüft wurde, dass der erweiterte Analysekontext bewusst über die
   Gemeindegrenze hinausreicht.

Ergebnis:

- Die OSM-Verkehrsachsen sind als technischer Eingangsdatenblock plausibel.
- Der Analysekontext außerhalb der Gemeinde ist methodisch notwendig, weil
  spätere 200-m- und 500-m-Puffer in die Gemeinde hineinreichen können.

### 4.2 Verifikation der Solarpuffer und Referenzlayer

Verwendete Datensätze:

- `data/processed/solar/drachselsried_solar_layers.gpkg`
- amtlicher WMS-Dienst `Planungsgrundlagen Solar`
- daraus insbesondere:
  - `PV-Freiflächenkulisse - Zoomstufe 1`
  - `PV-Freiflächenkulisse - Zoomstufe 2`
  - `PV-Förderkulisse 500 m Randstreifen (EEG)`
  - `PV-Privilegierung 200 m Randstreifen (BauGB)`

Manueller QGIS-Weg für die Solar-Verifikation:

1. In QGIS `WMS/WMTS` öffnen.
2. Den Dienst `Planungsgrundlagen Solar` registrieren:

```text
https://www.lfu.bayern.de/gdi/wms/energieatlas/planungsgrundlagen_solar
```

3. Danach die verfügbaren Layer laden.
4. Für die Freiflächenkulisse besonders verwenden:
   - `PV-Freiflächenkulisse - Zoomstufe 1`
   - `PV-Freiflächenkulisse - Zoomstufe 2`
5. Zusätzlich die amtlichen Randstreifen-Layer
   - `PV-Förderkulisse 500 m Randstreifen (EEG)`
   - `PV-Privilegierung 200 m Randstreifen (BauGB)`
   laden.
6. Diese amtlichen WMS-Layer mit
   - Gemeindegrenze
   - OSM-Verkehrsachsen
   - 200-m- und 500-m-Pufferzonen
   visuell überlagern.

Ergebnis:

- Die selbst erzeugten 200-m- und 500-m-Puffer können gegen die amtlichen
  WMS-Darstellungen fachlich plausibilisiert werden.
- Die amtlichen PV-Freiflächenkulissen dienen zusätzlich als visuelle
  Referenz für die Einordnung, sind aber selbst kein gut weiterverarbeitbarer
  Vektor-Eingabedatensatz der Pipeline.

Hinweis zur Methodik:

- Die beiden Zoomstufen sind WMS-Layer und damit primär Darstellungsdienste.
- Sie dienen in diesem Projekt als amtliche Referenz und Plausibilisierung.
- Die eigentliche automatisierte Analyse erfolgt weiterhin über die eigenen
  Vektorlayer aus OSM und Bufferoperationen.

Historische Notizen:

```text
# TODO: nicht mehr verwendet
Frühere Solar-Zwischenstände bleiben bewusst dokumentiert, auch wenn der
aktuelle Workflow inzwischen über die neuen Skripte und Referenzlayer läuft.
```

## 5. Wasser

Noch nicht fachlich verifiziert.

Geplant ist später die Dokumentation von:

- Eingabedatensätzen
- Vergleich Originaldaten vs. Skript-Output
- Verifikation der Zuschnitte und Kartenlayer

## 6. WFS-Einbindung in QGIS

Zur manuellen WFS-Prüfung in QGIS:

1. `Layer > Layer hinzufügen > WFS/OGC API - Features-Layer hinzufügen`
2. Neue Verbindung anlegen
3. URL eintragen:

```text
https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung
```

4. Verbinden
5. Relevante Layer laden
