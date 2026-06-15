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
3. `scripts/1_prepare_data/5_download_osm_network_data.py --technology solar`
4. `scripts/2_2_solar/3_prepare_solar_layers.py`
5. `scripts/3_generate_map/1_create_map_qgis_project.py`
6. `scripts/3_generate_map/2_generate_map_pdf.py`

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
- `osm_autobahnen_<gemeinde>`
- `osm_schienenwege_<gemeinde>`
- `pv_verkehrsachsen_500m_<gemeinde>`
- `pv_verkehrsachsen_200m_<gemeinde>`
- `pv_förderkulisse_500m_<gemeinde>`
- `pv_privilegierung_200m_<gemeinde>`

Damit lässt sich später in QGIS nachvollziehen:

- welcher Analysekontext verwendet wurde
- welche Achsen für 500 m benutzt wurden
- welche strengere Teilmenge für 200 m verwendet wurde
- wie daraus die finalen Puffer entstanden sind

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
