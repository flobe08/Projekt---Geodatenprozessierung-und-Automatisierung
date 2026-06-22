# Verifikation der Verarbeitungsschritte

Diese Datei dokumentiert die fachliche Verifikation der aktuellen
Verarbeitungsschritte. Sie ist getrennt von der reinen Bedienanleitung in
QGIS gehalten, damit die Ergebnisse später leichter in die schriftliche Arbeit
übernommen werden können.

Die Struktur ist bereits für drei Technologierichtungen vorbereitet:

- Wind
- Solar
- Wasser

Aktuell ist der Bereich **Wind** am vollständigsten umgesetzt und verifiziert.
Für **Solar** sind die zentralen Referenz- und Korridorlayer ebenfalls
dokumentiert. **Wasser** ist weiterhin als vorbereiteter Bereich vorgesehen.

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
data/processed/1_base_boundaries/drachselsried_boundary.gpkg
```

5. Der Skript-Output wurde mit dem offiziellen Verwaltungsdatensatz
   überlagert und visuell verglichen.

Ergebnis:

- Der Output des Skripts stimmt räumlich mit der offiziellen Gemeindegrenze
  von Drachselsried überein.
- Damit ist die Extraktion der Gemeindegrenze fachlich plausibel verifiziert.

Aktuelle Referenz:

```text
scripts/1_prepare_data/2_extract_municipality_boundary.py
```

Frühere Skriptversion:

```text
scripts/prepare_data/1_grenzen.py
```

Diese frühere Skriptversion wird nicht mehr aktiv verwendet. Sie bleibt hier
nur als historische Referenz dokumentiert.

## 2. Schutzgebiete

### 2.1 Verifikation der allgemeinen Schutzgebietslayer

Verwendete Datensätze:

- Schutzgebietsdaten des Bayerischen Landesamts für Umwelt
- Natura-2000-Daten
- Ramsar-Gebiete
- weitere Schutzgebietskategorien

Automatische Outputs:

```text
data/processed/1_base_protection_areas/drachselsried_naturschutz_allgemein_hart.gpkg
data/processed/1_base_protection_areas/drachselsried_naturschutz_allgemein_weich.gpkg
data/processed/1_base_protection_areas/drachselsried_naturschutz_wind.gpkg
```

Vorgehen zur Verifikation:

1. Die erzeugten GeoPackages wurden in QGIS geladen.
2. Die enthaltenen Ursprungslayer wurden mit den heruntergeladenen Rohdaten
   verglichen.
3. Die zusammengeführten Layer wurden gegen die Einzel-Layer geprüft.
4. Die Layer wurden mit der Gemeindegrenze überlagert.

Ergebnis:

- Die Schutzgebiete werden fachlich in harte und weiche Restriktionen
  getrennt.
- Harte Restriktionen werden als strengere Konflikt- und Ausschlussflächen
  behandelt.
- Weiche Restriktionen dienen als Konflikt- und Hinweisflächen.
- Windspezifische Schutz- und Konfliktflächen werden zusätzlich separat
  vorbereitet.
- Punktförmige Naturdenkmale und punktförmige geschützte
  Landschaftsbestandteile werden als Detail- und Attributlayer mitgeführt,
  aber nicht ohne fachlich begründeten Puffer in den flächenhaften
  Merged-Layer übernommen.

Aktuelle Referenz:

```text
scripts/1_prepare_data/3_build_protection_layers.py
```

## 3. Wind

### 3.1 Verifikation der Wind-Ausgangsdaten

Verwendeter Datensatz:

- WFS Regionalplanung Bayern
- Vorranggebiete Windenergienutzung
- Vorbehaltsgebiete Windenergienutzung

Vorgehen zur Verifikation:

1. Der WFS-Dienst wurde manuell in QGIS eingebunden.
2. Die relevanten Layer wurden geladen.
3. Die automatisch heruntergeladenen und zugeschnittenen Daten wurden mit den
   WFS-Layern verglichen.
4. Die Lage innerhalb der Gemeinde Drachselsried wurde geprüft.

Ergebnis:

- Die Windflächen stammen aus einer offiziellen regionalplanerischen Quelle.
- Die im Workflow erzeugten Layer sind räumlich plausibel.
- Vorrang- und Vorbehaltsgebiete werden in der Karte getrennt dargestellt.

Aktuelle Referenz:

```text
scripts/1_prepare_data/1_download_data.py --technology wind
```

### 3.2 Verifikation des Wind-Clips

Automatischer Output:

```text
data/processed/2_technology_wind/drachselsried_wind_layers.gpkg
```

Vorgehen zur Verifikation:

1. Die Windflächen wurden mit der Gemeindegrenze überlagert.
2. Es wurde geprüft, ob nur die innerhalb der Gemeinde liegenden Teilflächen
   übernommen wurden.
3. Die Attributtabelle wurde stichprobenartig geprüft.

Ergebnis:

- Die Windflächen wurden korrekt auf die Gemeinde zugeschnitten.
- Die Attributinformationen bleiben für die Nachvollziehbarkeit erhalten.

Aktuelle Referenz:

```text
scripts/2_1_wind/1_clip_wind_planning_areas.py
```

Frühere Skriptversion:

```text
scripts/wind/3_clip_wind_planning_areas.py
```

Diese frühere Skriptversion wird nicht mehr aktiv verwendet. Die aktuelle
Verarbeitung erfolgt über die oben genannte Referenz.

### 3.3 Verifikation der Wind-Landnutzungslayer

Verwendete Datensätze:

- offizieller Landnutzungsdatensatz Bayern
- zugeschnittener Gemeinde-Landnutzungsdatensatz
- windbezogene Landnutzungsausgaben

Automatische Outputs:

```text
data/processed/1_base_landuse/landnutzung_drachselsried.gpkg
data/processed/2_technology_wind/drachselsried_landuse_wind_ausschluss.gpkg
data/processed/2_technology_wind/drachselsried_landuse_wind_potenzial.gpkg
data/processed/2_technology_wind/drachselsried_landuse_wind_geeignet.gpkg
data/processed/2_technology_wind/drachselsried_landuse_wind_unused.gpkg
```

Relevante Layer:

- `landuse_wind_ausschluss`
- `landuse_wind_potenzial`
- `landuse_wind_geeignet`
- `landuse_wind_unused`

Vorgehen zur Verifikation:

1. Der originale Datensatz `landnutzung.gpkg` wurde in QGIS geladen.
2. Die einzeln enthaltenen `ln_*`-Layer wurden mit dem automatisch
   zugeschnittenen Gemeinde-Output verglichen.
3. Die Datei `landnutzung_drachselsried.gpkg` wurde geprüft, ob die
   erwarteten Nutzungs-Layer für Drachselsried enthalten sind.
4. Die windbezogenen Ergebnisdateien wurden in QGIS geladen.
5. Die Attributspalte `source_layer` wurde geprüft, um nachzuvollziehen,
   aus welchen offiziellen Nutzungs-Layern die Wind-Gruppen erzeugt wurden.

Ergebnis:

- Die Wind-Landnutzungslayer sind als Arbeits- und Prüflayer vorhanden.
- `landuse_wind_ausschluss` enthält die aktuell als kritisch eingestuften
  Nutzungen.
- `landuse_wind_potenzial` und `landuse_wind_geeignet` dienen als
  nachvollziehbare Suchraum- und Prüflayer.
- `landuse_wind_unused` enthält alle offiziellen Landnutzungs-Layer, die im
  aktuellen Wind-Landuse-Schritt noch keiner methodischen Kategorie zugeordnet
  sind.
- Die Landnutzungslayer bleiben als Detail- und Attributlayer im QGIS-Projekt
  verfügbar.
- Für die finale Windkarte wird daraus nicht jeder Einzellayer dargestellt,
  sondern der aggregierte Layer `Nutzungsausschluss` verwendet.

Aktuelle Referenz:

```text
scripts/2_1_wind/2_prepare_wind_landuse.py
```

### 3.4 Verifikation der OSM-Highway-Daten für Wind

Verwendete Datensätze:

```text
data/processed/1_base_osm_streets/drachselsried_osm_streets.gpkg
data/processed/2_technology_wind/drachselsried_osm_wind_streets.gpkg
```

Relevante Layer:

- `osm_streets_raw`
- windbezogen gefilterte Straßen und Wege

Vorgehen zur Verifikation:

1. Der Layer `osm_streets_raw` wurde in QGIS geladen.
2. Eine OpenStreetMap-Basiskarte wurde ergänzt.
3. Die Straßen wurden visuell mit der Basiskarte verglichen.
4. Die Attribute wurden stichprobenartig geprüft, insbesondere das Feld
   `highway`.
5. Der windbezogene OSM-Layer wurde geprüft, weil er die für Wind relevanten
   Straßen- und Wegeklassen zusammenfasst.

Ergebnis:

- Die OSM-Straßendaten liegen räumlich plausibel im Analysekontext der
  Gemeinde.
- Die Straßenklassen sind nachvollziehbar und können über `highway`
  kontrolliert werden.
- Die gefilterten OSM-Straßen werden in der finalen Windkarte als
  `Straßen und Wege` dargestellt.
- Zusätzlich bleiben die OSM-Layer als Detail- und Attributlayer für die
  Prüfung der Straßenklassen verfügbar.

Hinweis:

```text
OSM ist keine amtliche Planungsgrundlage. Die Daten werden als zusätzlicher
Kontext- und Prüflayer verwendet.
```

Aktuelle Referenz:

```text
scripts/1_prepare_data/5_download_osm_network_data.py --technology wind
scripts/2_1_wind/4_prepare_wind_osm_streets.py
```

### 3.5 Verifikation der finalen Windkarte

Automatische Outputs:

```text
data/processed/3_qgis_projects/drachselsried_map_wind.qgz
data/processed/3_maps/drachselsried_map_wind.pdf
```

In der finalen Windkarte aktiv dargestellte Layer:

- Gemeindegrenze
- Wind-Vorranggebiete
- Wind-Vorbehaltsgebiete, falls innerhalb der Gemeinde vorhanden
- harte allgemeine Naturschutz-Restriktionen
- weiche allgemeine Naturschutz-Konfliktflächen
- windspezifische Naturschutz-Restriktionen
- Straßen und Wege aus OSM
- Nutzungsausschluss als aggregierte Ausschlussfläche aus Landnutzung und
  vorbereiteten Ausschlusslayern
- OpenStreetMap als Hintergrundkarte

Im QGIS-Projekt zusätzlich als Detail- und Attributlayer verfügbar:

- einzelne Landnutzungsgruppen wie `landuse_wind_ausschluss`,
  `landuse_wind_potenzial`, `landuse_wind_geeignet` und
  `landuse_wind_unused`
- OSM-Ausgangs- und Filterlayer
- einzelne Naturschutz-Ursprungslayer

Ergebnis:

- Die finale Windkarte fokussiert bewusst auf aggregierte und gut lesbare
  Kartenlayer.
- Detail- und Attributlayer bleiben im QGIS-Projekt verfügbar, werden aber
  nicht einzeln in der PDF-Karte dargestellt.
- Dadurch bleibt die Karte lesbar, während die fachliche Entstehung der Layer
  weiterhin nachvollziehbar ist.

### 3.6 Zusammenfassung Wind

Für den Wind-Workflow wurden die zentralen Schritte verifiziert:

- Gemeindegrenze aus offiziellem Verwaltungsdatensatz
- Windflächen aus offiziellem WFS
- Clip der Windflächen auf die Gemeinde
- allgemeine und windspezifische Naturschutzlayer
- windbezogene Landnutzungslayer als Detail- und Attributlayer
- OSM-Highway-Daten als sichtbarer Straßen-/Wegekontext und als Detaillayer
- aggregierter Nutzungsausschluss als finaler Kartenlayer
- QGIS-Projekt und PDF-Karte

Damit ist der aktuelle Wind-Workflow fachlich plausibel und für die weitere
Kartenerstellung geeignet.

## 4. Solar

### 4.1 Verifikation der OSM-Verkehrsachsen

Verwendete Datensätze:

- `data/processed/1_base_osm_streets/drachselsried_osm_streets.gpkg`
- `data/processed/2_technology_solar/corridor/drachselsried_solar_corridor_basis.gpkg`
- OpenStreetMap-Basiskarte in QGIS

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

- `data/processed/2_technology_solar/drachselsried_solar_layers.gpkg`
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
  Referenz für die Einordnung.
- Die WMS-Referenzdaten werden als Raster auf Basis der Gemeinde-Bounding-Box
  eingebunden. Ein exakter harter Zuschnitt an der Gemeindegrenze ist bei
  diesen Darstellungsdaten nicht das Ziel der Verarbeitung.

Hinweis zur Methodik:

- Die beiden Zoomstufen sind WMS-Layer und damit primär Darstellungsdienste.
- Sie dienen in diesem Projekt als amtliche Referenz und Plausibilisierung.
- Die eigentliche automatisierte Analyse erfolgt weiterhin über die eigenen
  Vektorlayer aus OSM und Bufferoperationen.

Historische Notiz:

Frühere Solar-Zwischenstände bleiben bewusst dokumentiert, auch wenn der
aktuelle Workflow inzwischen über die neuen Skripte und Referenzlayer läuft.

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

Wichtig:

- In QGIS kann derselbe WFS-Dienst mehrere Layer bereitstellen.
- Für den Wind-Workflow sind insbesondere die regionalplanerischen
  Vorrang- und Vorbehaltsgebiete relevant.
