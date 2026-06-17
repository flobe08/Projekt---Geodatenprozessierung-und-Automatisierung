# Solar Workflow Notes

## Grundidee

Der aktuelle Solar-Workflow verwendet einen nachvollziehbaren und
reproduzierbaren Ansatz:

1. offizielle Gemeindegrenze
2. OSM-Verkehrsdaten als Vektorgrundlage
3. daraus abgeleitete 200-m- und 500-m-Pufferzonen
4. finale Ausgabe als GeoPackage für QGIS und Kartenerstellung

Die Solarpipeline übernimmt die amtlichen Solarflächen also nicht direkt als
Vektorlayer, sondern erzeugt eine eigene räumliche Näherung aus
Verkehrsachsen und Bufferoperationen.

## Aktuelle Skriptreihenfolge

1. `scripts/1_prepare_data/1_download_data.py`
2. `scripts/1_prepare_data/2_extract_municipality_boundary.py`
3. `scripts/1_prepare_data/3_build_protection_layers.py`
4. `scripts/1_prepare_data/4_clip_landuse.py`
5. `scripts/1_prepare_data/5_download_osm_network_data.py --technology solar`
6. `scripts/2_2_solar/4_prepare_solar_osm_streets.py`
7. `scripts/2_2_solar/2_prepare_solar_corridor_layers.py`
8. `scripts/2_2_solar/3_prepare_solar_landuse.py`
9. `scripts/3_generate_map/1_create_map_qgis_project.py`
10. `scripts/3_generate_map/2_generate_map_pdf.py`

## Hauptdatensätze

### Gemeindegrenze

- Quelle: Bayerischer ALKIS-Verwaltungsdatensatz
- Output: `data/processed/boundaries/<municipality>_boundary.gpkg`

### OSM-Verkehrsdaten

Für die Solarpipeline werden aus OSM nur fachlich relevante Verkehrsachsen
verwendet:

- `highway = motorway`
- `highway = motorway_link`
- `railway = rail`

Diese Achsen werden nicht nur für die Gemeinde selbst geladen, sondern für
einen erweiterten Analysekontext.

Die gemeinsame OSM-Straßenbasis liegt hier:

- `data/processed/osm_streets/<municipality>_osm_streets.gpkg`

Wichtige Layer:

- `osm_streets_raw`

Der allgemeine Solar-Straßenausschluss wird separat gespeichert:

- `data/processed/solar/<municipality>_osm_solar_streets.gpkg`
- Layer: `osm_streets_solar_ausschluss`

Die Korridorgrundlage für 200-m- und 500-m-Puffer liegt hier:

- `data/processed/solar/<municipality>_solar_corridor_basis.gpkg`

Wichtige Layer:

- `solar_corridor_autobahnen_<gemeinde>`
- `solar_corridor_schienenwege_<gemeinde>`

Hinweis:

- Der Layer `osm_streets_solar_ausschluss` ist aktuell ein vorbereiteter
  Arbeitslayer und noch nicht aktiv in die finale Solarkarte eingebunden.

### Amtliche Landnutzung

- Quelle: `data/raw/landuse/landnutzung.gpkg`
- Gemeindeclip:
  `data/processed/landuse/landnutzung_<municipality>.gpkg`

Zusätzliche solarspezifische Arbeitslayer:

- `data/processed/solar/<municipality>_landuse_solar_ausschluss.gpkg`
- `data/processed/solar/<municipality>_landuse_solar_potenzial.gpkg`
- `data/processed/solar/<municipality>_landuse_solar_geeignet.gpkg`
- `data/processed/solar/<municipality>_landuse_solar_unused.gpkg`

Hinweis:

- Diese Landnutzungs-Layer sind aktuell vorbereitet und für Prüfung sowie
  spätere Eignungslogik gedacht.
- Sie sind im QGIS-Projektskript bereits als TODO-Stufe vorgesehen, aber noch
  nicht aktiv in die finale Solarkarte eingebunden.

### Allgemeine Schutzgebiete

Zusätzlich zur Solarlogik werden inzwischen auch die allgemeinen
Naturschutzlayer erzeugt und in der Solarkarte als Kontext mitgeführt:

- `data/processed/schutzgebiete/<municipality>_naturschutz_allgemein_hart.gpkg`
- `data/processed/schutzgebiete/<municipality>_naturschutz_allgemein_weich.gpkg`

### Solarspezifische Landnutzung

Zusätzliche Arbeitslayer aus der amtlichen Landnutzung:

- `data/processed/solar/<municipality>_landuse_solar_ausschluss.gpkg`
- `data/processed/solar/<municipality>_landuse_solar_potenzial.gpkg`
- `data/processed/solar/<municipality>_landuse_solar_geeignet.gpkg`
- `data/processed/solar/<municipality>_landuse_solar_unused.gpkg`

Hinweis:

- Diese Landnutzungs-Layer werden bereits erzeugt.
- Sie sind aber aktuell noch nicht in die finale Solarkarte eingebunden.
- Im QGIS-Projektskript sind sie als nächste `TODO`-Stufe bereits
  vorbereitet.

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

Im aktuellen Projekt werden diese beiden WMS-Referenzlayer zusätzlich direkt
im automatisch erzeugten Solar-QGIS-Projekt eingebunden.

Zusätzlich werden vor der QGIS-Projekterstellung lokale Referenzbilder mit

- `scripts/2_2_solar/1_download_solar_reference_wms.py`

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
> „Planungsgrundlagen Solar“ des Energie-Atlas Bayern visuell abgeglichen.
