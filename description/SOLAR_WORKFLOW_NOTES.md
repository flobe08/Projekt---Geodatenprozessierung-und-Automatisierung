# Solar Workflow Notes

## Grundidee

Der aktuelle Solar-Workflow verwendet einen nachvollziehbaren und
reproduzierbaren Ansatz:

1. offizielle Gemeindegrenze
2. OSM-Verkehrsdaten als Vektorgrundlage
3. daraus abgeleitete 200-m- und 500-m-Pufferzonen
4. amtliche WMS-Referenzbilder für die PV-Freiflächenkulisse
5. finale Ausgabe als GeoPackage für QGIS und Kartenerstellung

Die Solarpipeline übernimmt die amtlichen Solarflächen also nicht direkt als
Vektorlayer, sondern erzeugt eine eigene räumliche Näherung aus
Verkehrsachsen und Bufferoperationen.

## Aktuelle Skriptreihenfolge

1. `scripts/1_prepare_data/1_download_data.py`
2. `scripts/1_prepare_data/2_extract_municipality_boundary.py`
3. `scripts/1_prepare_data/3_build_protection_layers.py`
4. `scripts/1_prepare_data/4_clip_landuse.py`
5. `scripts/1_prepare_data/5_download_osm_network_data.py --technology solar`
6. `scripts/2_2_solar/1_prepare_solar_corridor_layers.py`
7. `scripts/2_2_solar/2_prepare_solar_landuse.py`
8. `scripts/2_2_solar/3_download_solar_reference_wms.py`
9. `scripts/3_generate_map/1_prepare_overview_layers.py`
10. `scripts/3_generate_map/2_create_map_qgis_project.py`
11. `scripts/3_generate_map/3_generate_map_pdf.py`

Hinweis: Schritt 8 wird im automatischen Gesamtworkflow über
`scripts/3_generate_map.py` gestartet, nicht innerhalb der `.venv-wsl`.
Der Grund ist, dass der WMS-Download PyQGIS verwendet und deshalb mit dem
QGIS-/System-Python ausgeführt werden muss.

## Hauptdatensätze

### Gemeindegrenze

- Quelle: Bayerischer ALKIS-Verwaltungsdatensatz
- Output: `data/processed/1_base_boundaries/<municipality>_boundary.gpkg`

### OSM-Verkehrsdaten

Für die Solarpipeline werden aus OSM nur fachlich relevante Verkehrsachsen
verwendet:

- `highway = motorway`
- `highway = motorway_link`
- `railway = rail`

Diese Achsen werden nicht nur für die Gemeinde selbst geladen, sondern für
einen erweiterten Analysekontext.

Die gemeinsame OSM-Straßenbasis liegt hier:

- `data/processed/1_base_osm_streets/<municipality>_osm_streets.gpkg`

Wichtige Layer:

- `osm_streets_raw`

Die Korridorgrundlage für 200-m- und 500-m-Puffer liegt hier:

- `data/processed/2_technology_solar/corridor/<municipality>_solar_corridor_basis.gpkg`

Wichtige Layer:

- `solar_corridor_autobahnen_<gemeinde>`
- `solar_corridor_schienenwege_<gemeinde>`

Hinweis:

- Das frühere Skript `unused_prepare_solar_osm_streets.py` bleibt als
  Reserve erhalten, ist aber nicht Teil des aktiven Solar-Workflows.
- Für die aktuelle Solarkarte werden OSM-Achsen über `solar_corridor_basis`
  verwendet, weil die Karte die 200-m- und 500-m-Korridore entlang von
  Autobahnen und Schienenwegen zeigen soll.

### Amtliche Landnutzung

- Quelle: `data/raw/landuse/landnutzung.gpkg`
- Gemeindeclip:
  `data/processed/1_base_landuse/landnutzung_<municipality>.gpkg`

Zusätzliche solarspezifische Arbeitslayer:

- `data/processed/2_technology_solar/<municipality>_landuse_solar_ausschluss.gpkg`
- `data/processed/2_technology_solar/<municipality>_landuse_solar_pv_freiflaechen_naehung_vektorlayer.gpkg`
- `data/processed/2_technology_solar/<municipality>_landuse_solar_unused.gpkg`

Hinweis:

- `landuse_solar_ausschluss` fasst Landnutzungsklassen zusammen, die für
  Freiflächen-Photovoltaik im ersten Screening nicht geeignet sind.
- `landuse_solar_pv_freiflaechen_naehung_vektorlayer` bildet eine eigene
  vektorbasierte Näherung potenzieller PV-Freiflächen aus Landnutzungsdaten.
  Der Layer dient im QGIS-Projekt vor allem der Analyse und Attributprüfung.

### Allgemeine Schutzgebiete

Zusätzlich zur Solarlogik werden inzwischen auch die allgemeinen
Naturschutzlayer erzeugt und in der Solarkarte als Kontext mitgeführt:

- `data/processed/1_base_protection_areas/<municipality>_naturschutz_allgemein_hart.gpkg`
- `data/processed/1_base_protection_areas/<municipality>_naturschutz_allgemein_weich.gpkg`

### Amtliche Referenz zur Prüfung

- `Energie-Atlas Bayern: Planungsgrundlagen Solar - WMS`
- <https://www.lfu.bayern.de/gdi/wms/energieatlas/planungsgrundlagen_solar>

Relevante Referenzlayer:

- `PV-Freiflächenkulisse - Zoomstufe 1`
- `PV-Freiflächenkulisse - Zoomstufe 2`
- `PV-Förderkulisse 500 m Randstreifen (EEG)`
- `PV-Privilegierung 200 m Randstreifen (BauGB)`

Manuelle Einbindung in QGIS:

1. `WMS/WMTS` öffnen
2. Dienst `Planungsgrundlagen Solar` registrieren
3. URL eintragen:

```text
https://www.lfu.bayern.de/gdi/wms/energieatlas/planungsgrundlagen_solar
```

4. Verbinden
5. Für die fachliche Einordnung insbesondere diese Layer laden:
   - `PV-Freiflächenkulisse - Zoomstufe 1`
   - `PV-Freiflächenkulisse - Zoomstufe 2`

Im aktuellen Projekt werden diese beiden WMS-Referenzlayer zusätzlich als
lokale Rasterbilder in `data/processed/2_technology_solar/reference/` abgelegt und im automatisch
erzeugten Solar-QGIS-Projekt eingebunden.

Zusätzlich werden vor der QGIS-Projekterstellung lokale Referenzbilder mit

- `scripts/2_2_solar/3_download_solar_reference_wms.py`

heruntergeladen, damit die amtliche Referenz auch ohne manuelle
WMS-Registrierung direkt im Projekt verfügbar ist.

## Warum der amtliche Solar-Dienst nicht direkt als Pipeline-Input verwendet wird

Der amtliche Solar-Dienst liegt als WMS vor.

Das bedeutet:

- die Daten werden primär als Kartenbild dargestellt
- es gibt keinen direkt nutzbaren Vektor-Workflow mit sauberer Attributtabelle
- eine reproduzierbare Weiterverarbeitung in der Pipeline ist dadurch
  eingeschränkt

Deshalb wird der WMS in diesem Projekt als **amtliche Referenz zur
Verifikation** verwendet, aber nicht als eigentlicher Eingabedatensatz für die
automatisierte Verarbeitung.

Der WMS wird für die Pipeline auf die Bounding Box der Gemeinde geladen. Ein
exakter harter Zuschnitt an der Gemeindegrenze ist hier nicht wie bei einem
Vektorlayer möglich, weil der WMS nur ein georeferenziertes Kartenbild liefert
und keine bearbeitbaren Polygongeometrien mit Attributtabelle. Der harte
Gemeindezuschnitt erfolgt deshalb bei den eigenen Vektorlayern. Die
WMS-Rasterbilder dienen als visuelle Referenz, um die selbst erzeugten
Korridore und die vektorbasierte PV-Freiflächen-Näherung plausibel zu
vergleichen.

## Layer in QGIS-Projekt und finaler Karte

Die finale Solar-PDF bleibt bewusst aggregiert und zeigt nur die wichtigsten
Kartenlayer:

- Gemeindegrenze
- PV-Freiflächenkulisse aus dem Energie-Atlas Bayern als WMS-Referenz
- EEG-Förderkulisse 500 m als eigener Vektorkorridor
- BauGB-Privilegierung 200 m als eigener Vektorkorridor
- Autobahnen und Schienenwege als Grundlage der beiden Korridore
- harte Naturschutz-Restriktionen
- weiche Naturschutzflächen

Das QGIS-Projekt enthält zusätzlich Detail- und Attributlayer. Diese Layer
sind für Analyse, Nachvollziehbarkeit und manuelle Kontrolle gedacht und
müssen nicht alle in der PDF erscheinen. Dazu gehört insbesondere:

- `landuse_solar_ausschluss`
- `landuse_solar_pv_freiflaechen_naehung_vektorlayer`

`landuse_solar_ausschluss` bleibt bewusst als Detail- und Attributlayer im
QGIS-Projekt, wird aber nicht als sichtbarer Hauptlayer in der finalen
Solar-PDF dargestellt. Dadurch bleibt die Solarkarte auf PV-Freiflächenkulisse,
200-m-/500-m-Korridore und Naturschutzkontext fokussiert.

`landuse_solar_pv_freiflaechen_naehung_vektorlayer` ist eine eigene
vektorbasierte Näherung der PV-Freiflächenkulisse aus Landnutzungsklassen. Er
ersetzt nicht den amtlichen WMS, sondern dient als bearbeitbarer Vergleichs-
und Prüflayer.

## Rechtlicher Hintergrund

### PV-Privilegierung 200 m

Rechtsgrundlage:

- `§ 35 Abs. 1 Nr. 8 Buchstabe b BauGB`

Bedeutung für das Projekt:

Freiflächen-Photovoltaikanlagen können im Außenbereich privilegiert sein, wenn
sie auf Flächen längs von Autobahnen oder Schienenwegen des übergeordneten
Netzes mit mindestens zwei Hauptgleisen liegen und höchstens 200 m vom
äußeren Rand der Fahrbahn entfernt sind.

### PV-Förderkulisse 500 m

Rechtsgrundlage:

- `§ 37 Abs. 1 Nr. 2 Buchstabe c EEG 2023`

Bedeutung für das Projekt:

Die EEG-Förderkulisse umfasst unter anderem Flächen längs von Autobahnen oder
Schienenwegen, wenn die Freiflächenanlage in einer Entfernung von bis zu
500 m vom äußeren Rand der Fahrbahn errichtet werden soll.

## Umgesetzte methodische Näherung

### 500-m-Zone

Für die `PV-Förderkulisse 500 m` wird eine breite OSM-Näherung verwendet:

```text
highway = motorway
oder
highway = motorway_link
oder
railway = rail
```

### 200-m-Zone

Für die `PV-Privilegierung 200 m` wird eine strengere OSM-Näherung verwendet:

```text
highway = motorway
oder
highway = motorway_link
oder (
  railway = rail
  und tracks >= 2
)
```

Damit gilt:

- Autobahnen werden immer berücksichtigt.
- Schienenwege werden für die 200-m-Zone nur dann verwendet, wenn in OSM
  explizit `tracks >= 2` gepflegt ist.

## Wichtige methodische Einschränkung

Die gesetzliche Bedingung

```text
mindestens zwei Hauptgleise
```

kann mit OSM nicht vollständig rechtsverbindlich geprüft werden. In der
Pipeline wird deshalb die vereinfachte technische Näherung `tracks >= 2`
verwendet.

Das ist für die Arbeit wichtig:

- fachlich vertretbar
- technisch nachvollziehbar
- aber keine rechtsverbindliche Einzelfallprüfung

## Warum mit Analysekontext gearbeitet wird

Ein harter Zuschnitt direkt an der Gemeindegrenze wäre für Bufferanalysen
fachlich zu früh.

Beispiel:

- Eine Bahnlinie kann knapp außerhalb von Drachselsried liegen.
- Ihr 200-m- oder 500-m-Puffer kann trotzdem in die Gemeinde hineinreichen.
- Würde die Linie schon beim Download an der Gemeindegrenze abgeschnitten,
  ginge diese Wirkung verloren.

Deshalb lädt die Pipeline OSM-Verkehrsdaten zunächst für einen erweiterten
Analysekontext um die Gemeinde.

Aktuell wird dafür ein Kontext-Buffer von `1000 m` verwendet.

Erst die finalen Fachlayer werden anschließend exakt auf die Gemeindegrenze
zugeschnitten.

## Was im Output gespeichert wird

Die Solar-Ausgabe enthält mehrere Layer, damit die Herleitung transparent
bleibt:

- `analysekontext_<gemeinde>`
- `solar_corridor_autobahnen_<gemeinde>`
- `solar_corridor_schienenwege_<gemeinde>`
- `pv_verkehrsachsen_500m_<gemeinde>`
- `pv_verkehrsachsen_200m_<gemeinde>`
- `pv_förderkulisse_500m_<gemeinde>`
- `pv_privilegierung_200m_<gemeinde>`

Damit lässt sich später in QGIS nachvollziehen:

- welcher Analysekontext verwendet wurde
- welche Achsen für 500 m benutzt wurden
- welche strengere Teilmenge für 200 m verwendet wurde
- wie daraus die finalen Puffer entstanden sind

## Aktueller Kartenstand

Die aktuelle Solarkarte bindet bereits ein:

- harte allgemeine Naturschutz-Restriktionen
- weiche allgemeine Naturschutz-Konfliktflächen
- `PV-Freiflächenkulisse - Zoomstufe 1`
- `PV-Freiflächenkulisse - Zoomstufe 2`
- `pv_förderkulisse_500m_<gemeinde>`
- `pv_privilegierung_200m_<gemeinde>`
- `pv_verkehrsachsen_500m_<gemeinde>`

Zusätzlich vorbereitet, aber noch bewusst nicht aktiv eingebunden:

- `landuse_solar_ausschluss`
- `osm_streets_solar_ausschluss`

Diese beiden Layer stehen im QGIS-Projektskript bereits als `TODO` bereit und
werden später zugeschaltet, sobald die endgültige Solar-Eignungslogik
feststeht.

## Was wir in der Arbeit sicher behaupten können

Was wir sicher schreiben können:

- die Solarpipeline erzeugt reproduzierbare räumliche Näherungen für zwei
  rechtlich relevante Randstreifen
- die 500-m-Zone orientiert sich an der EEG-Förderkulisse
- die 200-m-Zone orientiert sich an der BauGB-Privilegierung
- die Flächen wurden automatisiert aus OSM-Verkehrsdaten abgeleitet
- der amtliche WMS wurde zur fachlichen Plausibilisierung verwendet

Was wir nicht behaupten sollten:

- dass die Pipeline eine rechtsverbindliche Genehmigungsprüfung ersetzt
- dass jeder einzelne rechtliche Sonderfall vollständig aus OSM ableitbar ist
- dass der WMS direkt als bearbeitbarer Vektordatensatz vorliegt

## Validierung

Der Solar-Workflow wurde manuell in QGIS geprüft:

- OSM-Verkehrsachsen geladen
- Analysekontext geladen
- finale 200-m- und 500-m-Puffer geladen
- amtlichen WMS `Planungsgrundlagen Solar` eingebunden
- visuelle Überlagerung und Plausibilitätsprüfung durchgeführt

Die detaillierten Schritte stehen in:

- [VERIFIKATION.md](VERIFIKATION.md)

## Geeignete Formulierung für die Arbeit

> Für die Solar-Potenzialanalyse wurden zwei Randstreifen modelliert. Der
> 200-m-Randstreifen orientiert sich an § 35 Abs. 1 Nr. 8 Buchstabe b BauGB
> und bildet die bauplanungsrechtliche Privilegierung von
> Freiflächen-Photovoltaikanlagen entlang von Autobahnen und bestimmten
> Schienenwegen näherungsweise ab. Für Schienenwege wurde dazu in OSM die
> vereinfachte Bedingung `tracks >= 2` verwendet. Der 500-m-Randstreifen
> orientiert sich an § 37 Abs. 1 Nr. 2 Buchstabe c EEG 2023 und beschreibt
> eine förderrechtlich relevante Flächenkulisse entlang von Autobahnen und
> Schienenwegen. Beide Randstreifen wurden aus OSM-Verkehrsdaten abgeleitet,
> stellen jedoch keine rechtsverbindliche Prüfung dar. Zur fachlichen
> Plausibilisierung wurden die Ergebnisse mit dem amtlichen WMS-Dienst
> "Planungsgrundlagen Solar" des Energie-Atlas Bayern visuell abgeglichen.
