# Solar Workflow Notes

## Grundidee

Der aktuelle Solar-Workflow verwendet einen nachvollziehbaren und
reproduzierbaren Ansatz:

1. offizielle Gemeindegrenze
2. OSM-Verkehrsdaten als Vektorgrundlage
3. daraus abgeleitete 200-m- und 500-m-Pufferzonen
4. finale Ausgabe als GeoPackage fÃ¼r QGIS und Kartenerstellung

Die Solarpipeline Ã¼bernimmt die amtlichen SolarflÃ¤chen also nicht direkt als
Vektorlayer, sondern erzeugt eine eigene rÃ¤umliche NÃ¤herung aus
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
9. `scripts/2_2_solar/1_download_solar_reference_wms.py`
10. `scripts/3_generate_map/1_prepare_overview_layers.py`
11. `scripts/3_generate_map/2_create_map_qgis_project.py`
12. `scripts/3_generate_map/3_generate_map_pdf.py`

## HauptdatensÃ¤tze

### Gemeindegrenze

- Quelle: Bayerischer ALKIS-Verwaltungsdatensatz
- Output: `data/processed/boundaries/<municipality>_boundary.gpkg`

### OSM-Verkehrsdaten

FÃ¼r die Solarpipeline werden aus OSM nur fachlich relevante Verkehrsachsen
verwendet:

- `highway = motorway`
- `highway = motorway_link`
- `railway = rail`

Diese Achsen werden nicht nur fÃ¼r die Gemeinde selbst geladen, sondern fÃ¼r
einen erweiterten Analysekontext.

Die gemeinsame OSM-StraÃŸenbasis liegt hier:

- `data/processed/osm_streets/<municipality>_osm_streets.gpkg`

Wichtige Layer:

- `osm_streets_raw`

Der allgemeine Solar-StraÃŸenausschluss wird separat gespeichert:

- `data/processed/solar/<municipality>_osm_solar_streets.gpkg`
- Layer: `osm_streets_solar_ausschluss`

Die Korridorgrundlage fÃ¼r 200-m- und 500-m-Puffer liegt hier:

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

ZusÃ¤tzliche solarspezifische Arbeitslayer:

- `data/processed/solar/<municipality>_landuse_solar_ausschluss.gpkg`
- `data/processed/solar/<municipality>_landuse_solar_potenzial.gpkg`
- `data/processed/solar/<municipality>_landuse_solar_geeignet.gpkg`
- `data/processed/solar/<municipality>_landuse_solar_unused.gpkg`

Hinweis:

- Diese Landnutzungs-Layer sind aktuell vorbereitet und fÃ¼r PrÃ¼fung sowie
  spÃ¤tere Eignungslogik gedacht.
- Sie sind im QGIS-Projektskript bereits als TODO-Stufe vorgesehen, aber noch
  nicht aktiv in die finale Solarkarte eingebunden.

### Allgemeine Schutzgebiete

ZusÃ¤tzlich zur Solarlogik werden inzwischen auch die allgemeinen
Naturschutzlayer erzeugt und in der Solarkarte als Kontext mitgefÃ¼hrt:

- `data/processed/schutzgebiete/<municipality>_naturschutz_allgemein_hart.gpkg`
- `data/processed/schutzgebiete/<municipality>_naturschutz_allgemein_weich.gpkg`

### Solarspezifische Landnutzung

ZusÃ¤tzliche Arbeitslayer aus der amtlichen Landnutzung:

- `data/processed/solar/<municipality>_landuse_solar_ausschluss.gpkg`
- `data/processed/solar/<municipality>_landuse_solar_potenzial.gpkg`
- `data/processed/solar/<municipality>_landuse_solar_geeignet.gpkg`
- `data/processed/solar/<municipality>_landuse_solar_unused.gpkg`

Hinweis:

- Diese Landnutzungs-Layer werden bereits erzeugt.
- Sie sind aber aktuell noch nicht in die finale Solarkarte eingebunden.
- Im QGIS-Projektskript sind sie als nÃ¤chste `TODO`-Stufe bereits
  vorbereitet.

### Amtliche Referenz zur PrÃ¼fung

- `Energie-Atlas Bayern: Planungsgrundlagen Solar - WMS`
- <https://www.lfu.bayern.de/gdi/wms/energieatlas/planungsgrundlagen_solar>

Relevante Referenzlayer:

- `PV-FreiflÃ¤chenkulisse - Zoomstufe 1`
- `PV-FreiflÃ¤chenkulisse - Zoomstufe 2`
- `PV-FÃ¶rderkulisse 500 m Randstreifen (EEG)`
- `PV-Privilegierung 200 m Randstreifen (BauGB)`

Manuelle Einbindung in QGIS:

1. `WMS/WMTS` Ã¶ffnen
2. Dienst `Planungsgrundlagen Solar` registrieren
3. URL eintragen:

```text
https://www.lfu.bayern.de/gdi/wms/energieatlas/planungsgrundlagen_solar
```

4. Verbinden
5. FÃ¼r die fachliche Einordnung insbesondere diese Layer laden:
   - `PV-FreiflÃ¤chenkulisse - Zoomstufe 1`
   - `PV-FreiflÃ¤chenkulisse - Zoomstufe 2`

Im aktuellen Projekt werden diese beiden WMS-Referenzlayer zusÃ¤tzlich direkt
im automatisch erzeugten Solar-QGIS-Projekt eingebunden.

ZusÃ¤tzlich werden vor der QGIS-Projekterstellung lokale Referenzbilder mit

- `scripts/2_2_solar/1_download_solar_reference_wms.py`

heruntergeladen, damit die amtliche Referenz auch ohne manuelle
WMS-Registrierung direkt im Projekt verfÃ¼gbar ist.

## Warum der amtliche Solar-Dienst nicht direkt als Pipeline-Input verwendet wird

Der amtliche Solar-Dienst liegt als WMS vor.

Das bedeutet:

- die Daten werden primÃ¤r als Kartenbild dargestellt
- es gibt keinen direkt nutzbaren Vektor-Workflow mit sauberer Attributtabelle
- eine reproduzierbare Weiterverarbeitung in der Pipeline ist dadurch
  eingeschrÃ¤nkt

Deshalb wird der WMS in diesem Projekt als **amtliche Referenz zur
Verifikation** verwendet, aber nicht als eigentlicher Eingabedatensatz fÃ¼r die
automatisierte Verarbeitung.

## Rechtlicher Hintergrund

### PV-Privilegierung 200 m

Rechtsgrundlage:

- `Â§ 35 Abs. 1 Nr. 8 Buchstabe b BauGB`

Bedeutung fÃ¼r das Projekt:

FreiflÃ¤chen-Photovoltaikanlagen kÃ¶nnen im AuÃŸenbereich privilegiert sein, wenn
sie auf FlÃ¤chen lÃ¤ngs von Autobahnen oder Schienenwegen des Ã¼bergeordneten
Netzes mit mindestens zwei Hauptgleisen liegen und hÃ¶chstens 200 m vom
Ã¤uÃŸeren Rand der Fahrbahn entfernt sind.

### PV-FÃ¶rderkulisse 500 m

Rechtsgrundlage:

- `Â§ 37 Abs. 1 Nr. 2 Buchstabe c EEG 2023`

Bedeutung fÃ¼r das Projekt:

Die EEG-FÃ¶rderkulisse umfasst unter anderem FlÃ¤chen lÃ¤ngs von Autobahnen oder
Schienenwegen, wenn die FreiflÃ¤chenanlage in einer Entfernung von bis zu
500 m vom Ã¤uÃŸeren Rand der Fahrbahn errichtet werden soll.

## Umgesetzte methodische NÃ¤herung

### 500-m-Zone

FÃ¼r die `PV-FÃ¶rderkulisse 500 m` wird eine breite OSM-NÃ¤herung verwendet:

```text
highway = motorway
oder
highway = motorway_link
oder
railway = rail
```

### 200-m-Zone

FÃ¼r die `PV-Privilegierung 200 m` wird eine strengere OSM-NÃ¤herung verwendet:

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

- Autobahnen werden immer berÃ¼cksichtigt.
- Schienenwege werden fÃ¼r die 200-m-Zone nur dann verwendet, wenn in OSM
  explizit `tracks >= 2` gepflegt ist.

## Wichtige methodische EinschrÃ¤nkung

Die gesetzliche Bedingung

```text
mindestens zwei Hauptgleise
```

kann mit OSM nicht vollstÃ¤ndig rechtsverbindlich geprÃ¼ft werden. In der
Pipeline wird deshalb die vereinfachte technische NÃ¤herung `tracks >= 2`
verwendet.

Das ist fÃ¼r die Arbeit wichtig:

- fachlich vertretbar
- technisch nachvollziehbar
- aber keine rechtsverbindliche EinzelfallprÃ¼fung

## Warum mit Analysekontext gearbeitet wird

Ein harter Zuschnitt direkt an der Gemeindegrenze wÃ¤re fÃ¼r Bufferanalysen
fachlich zu frÃ¼h.

Beispiel:

- Eine Bahnlinie kann knapp auÃŸerhalb von Drachselsried liegen.
- Ihr 200-m- oder 500-m-Puffer kann trotzdem in die Gemeinde hineinreichen.
- WÃ¼rde die Linie schon beim Download an der Gemeindegrenze abgeschnitten,
  ginge diese Wirkung verloren.

Deshalb lÃ¤dt die Pipeline OSM-Verkehrsdaten zunÃ¤chst fÃ¼r einen erweiterten
Analysekontext um die Gemeinde.

Aktuell wird dafÃ¼r ein Kontext-Buffer von `1000 m` verwendet.

Erst die finalen Fachlayer werden anschlieÃŸend exakt auf die Gemeindegrenze
zugeschnitten.

## Was im Output gespeichert wird

Die Solar-Ausgabe enthÃ¤lt mehrere Layer, damit die Herleitung transparent
bleibt:

- `analysekontext_<gemeinde>`
- `solar_corridor_autobahnen_<gemeinde>`
- `solar_corridor_schienenwege_<gemeinde>`
- `pv_verkehrsachsen_500m_<gemeinde>`
- `pv_verkehrsachsen_200m_<gemeinde>`
- `pv_fÃ¶rderkulisse_500m_<gemeinde>`
- `pv_privilegierung_200m_<gemeinde>`

Damit lÃ¤sst sich spÃ¤ter in QGIS nachvollziehen:

- welcher Analysekontext verwendet wurde
- welche Achsen fÃ¼r 500 m benutzt wurden
- welche strengere Teilmenge fÃ¼r 200 m verwendet wurde
- wie daraus die finalen Puffer entstanden sind

## Aktueller Kartenstand

Die aktuelle Solarkarte bindet bereits ein:

- harte allgemeine Naturschutz-Restriktionen
- weiche allgemeine Naturschutz-KonfliktflÃ¤chen
- `PV-FreiflÃ¤chenkulisse - Zoomstufe 1`
- `PV-FreiflÃ¤chenkulisse - Zoomstufe 2`
- `pv_fÃ¶rderkulisse_500m_<gemeinde>`
- `pv_privilegierung_200m_<gemeinde>`
- `pv_verkehrsachsen_500m_<gemeinde>`

ZusÃ¤tzlich vorbereitet, aber noch bewusst nicht aktiv eingebunden:

- `landuse_solar_ausschluss`
- `osm_streets_solar_ausschluss`

Diese beiden Layer stehen im QGIS-Projektskript bereits als `TODO` bereit und
werden spÃ¤ter zugeschaltet, sobald die endgÃ¼ltige Solar-Eignungslogik
feststeht.

## Was wir in der Arbeit sicher behaupten kÃ¶nnen

Was wir sicher schreiben kÃ¶nnen:

- die Solarpipeline erzeugt reproduzierbare rÃ¤umliche NÃ¤herungen fÃ¼r zwei
  rechtlich relevante Randstreifen
- die 500-m-Zone orientiert sich an der EEG-FÃ¶rderkulisse
- die 200-m-Zone orientiert sich an der BauGB-Privilegierung
- die FlÃ¤chen wurden automatisiert aus OSM-Verkehrsdaten abgeleitet
- der amtliche WMS wurde zur fachlichen Plausibilisierung verwendet

Was wir nicht behaupten sollten:

- dass die Pipeline eine rechtsverbindliche GenehmigungsprÃ¼fung ersetzt
- dass jeder einzelne rechtliche Sonderfall vollstÃ¤ndig aus OSM ableitbar ist
- dass der WMS direkt als bearbeitbarer Vektordatensatz vorliegt

## Validierung

Der Solar-Workflow wurde manuell in QGIS geprÃ¼ft:

- OSM-Verkehrsachsen geladen
- Analysekontext geladen
- finale 200-m- und 500-m-Puffer geladen
- amtlichen WMS `Planungsgrundlagen Solar` eingebunden
- visuelle Ãœberlagerung und PlausibilitÃ¤tsprÃ¼fung durchgefÃ¼hrt

Die detaillierten Schritte stehen in:

- [VERIFIKATION.md](VERIFIKATION.md)

## Geeignete Formulierung fÃ¼r die Arbeit

> FÃ¼r die Solar-Potenzialanalyse wurden zwei Randstreifen modelliert. Der
> 200-m-Randstreifen orientiert sich an Â§ 35 Abs. 1 Nr. 8 Buchstabe b BauGB
> und bildet die bauplanungsrechtliche Privilegierung von
> FreiflÃ¤chen-Photovoltaikanlagen entlang von Autobahnen und bestimmten
> Schienenwegen nÃ¤herungsweise ab. FÃ¼r Schienenwege wurde dazu in OSM die
> vereinfachte Bedingung `tracks >= 2` verwendet. Der 500-m-Randstreifen
> orientiert sich an Â§ 37 Abs. 1 Nr. 2 Buchstabe c EEG 2023 und beschreibt
> eine fÃ¶rderrechtlich relevante FlÃ¤chenkulisse entlang von Autobahnen und
> Schienenwegen. Beide Randstreifen wurden aus OSM-Verkehrsdaten abgeleitet,
> stellen jedoch keine rechtsverbindliche PrÃ¼fung dar. Zur fachlichen
> Plausibilisierung wurden die Ergebnisse mit dem amtlichen WMS-Dienst
> â€žPlanungsgrundlagen Solarâ€œ des Energie-Atlas Bayern visuell abgeglichen.
