# Projektarbeit: Inhaltsverzeichnis und Kapitelinhalt

Diese Datei dient als Arbeitsgliederung parallel zur Word-Datei
`description/Projektarbeit.docx`. Der Schwerpunkt liegt auf dem
Inhaltsverzeichnis und darauf, welche Inhalte in die einzelnen Kapitel
geschrieben werden sollen. Die Gliederung orientiert sich am aktuellen
Word-Stand und enthält bereits ausgearbeitete Textbausteine für Abstract,
Einleitung und gemeinsame Datenvorbereitung.

## Vorschlag für das Inhaltsverzeichnis

```text
Abstract
Eidesstattliche Erklärung
Genderklausel
Inhaltsverzeichnis

1. Einleitung
   1.1 Ausgangslage und Motivation
   1.2 Zielsetzung und Fragestellung
   1.3 Abgrenzung der Arbeit

2. Datenbasis
   2.1 Allgemeine Datengrundlagen
       2.1.1 Verwaltungsgrenzen
       2.1.2 Landnutzung
       2.1.3 Schutzgebiete
       2.1.4 OpenStreetMap
   2.2 Windbezogene Datengrundlagen
   2.3 Solarbezogene Datengrundlagen
   2.4 Wasserbezogene Datengrundlagen

3. Methodik
   3.1 Allgemeiner Workflow und Gesamtaufbau der Pipeline
   3.2 Gemeinsame Datenvorbereitung
   3.3 Wind-Workflow
   3.4 Solar-Workflow
   3.5 Wasser-Workflow
   3.6 Kartenerzeugung und QGIS-Projekt
   3.7 Verifikation

4. Ergebnisse
   4.1 Windkarte
   4.2 Solarkarte
   4.3 Wasserkarte
   4.4 Auswertung und Übertragbarkeit

5. Diskussion
   5.1 Vorteile des Workflows
   5.2 Grenzen und fachliche Einschätzung

6. Fazit und Ausblick
   6.1 Was wurde erreicht?
   6.2 Beantwortung der Fragestellung
   6.3 Ausblick

Literaturverzeichnis

Anhang
   A Workflowdiagramm
   B Datensatzübersicht
   C Zusätzliche Karten
```

## Abstract

Im Rahmen dieser Projektarbeit wurde eine reproduzierbare Geodatenpipeline zur automatisierten Verarbeitung und Visualisierung von Geodaten für erneuerbare Energien entwickelt. Ziel war es, offene und amtliche Geodaten automatisiert zu verarbeiten, zu harmonisieren und für die Technologien Windenergie, Freiflächen-Photovoltaik und Wasserkraft auf Gemeindeebene nutzbar zu machen.

Die entwickelte Pipeline kombiniert Verwaltungsgrenzen, Schutzgebiete, Landnutzungsdaten und OpenStreetMap-Daten mit offiziellen Planungs- und Referenzdaten des Freistaats Bayern. Dazu zählen unter anderem Vorrang- und Vorbehaltsgebiete für Windenergie sowie Planungskulissen für Freiflächen-Photovoltaik. Ergänzend werden aus den verfügbaren Geodaten weitere Konflikt-, Ausschluss- und Kontextinformationen abgeleitet und gemeinsam kartografisch dargestellt.

Die Verarbeitung umfasst den automatisierten Download der Datensätze, die Aufbereitung der Geometrien, die Erstellung technologiespezifischer Layer sowie die automatisierte Erzeugung von GeoPackages, QGIS-Projekten und PDF-Karten. Als Untersuchungsgebiet wurde die Gemeinde Drachselsried gewählt. Zur Bewertung der Übertragbarkeit wurde die Pipeline zusätzlich auf weitere Gemeinden angewendet.

Die Ergebnisse zeigen, dass sich unterschiedliche Geodatenquellen automatisiert zusammenführen und für kommunale Analysen im Bereich erneuerbarer Energien nutzbar machen lassen. Durch den modularen Aufbau kann die entwickelte Pipeline mit geringem Anpassungsaufwand auf weitere Gemeinden übertragen werden.
## 1. Einleitung

Der Ausbau erneuerbarer Energien stellt Kommunen, Planungsbehörden und Energieversorger vor die Herausforderung, große Mengen raumbezogener Daten auszuwerten und miteinander zu verknüpfen. Für die Planung von Windenergieanlagen, Freiflächen-Photovoltaikanlagen oder Wasserkraftstandorten müssen unterschiedliche Einflussfaktoren berücksichtigt werden. Dazu zählen beispielsweise Schutzgebiete, bestehende Infrastruktur, Landnutzung, Gewässer oder bereits ausgewiesene Planungsflächen.

Viele dieser Informationen stehen heute als offene oder amtliche Geodaten zur Verfügung. Die Datensätze stammen jedoch aus unterschiedlichen Quellen, verwenden verschiedene Formate und müssen vor einer gemeinsamen Analyse zunächst aufbereitet werden. Dadurch entsteht ein hoher manueller Aufwand, insbesondere wenn dieselben Verarbeitungsschritte für mehrere Gemeinden wiederholt werden sollen.

Vor diesem Hintergrund wurde im Rahmen dieser Projektarbeit eine automatisierte Geodatenpipeline entwickelt. Ziel ist es, relevante Datensätze zu beschaffen, zu vereinheitlichen und in einer reproduzierbaren Struktur für die weitere Analyse bereitzustellen. Die Ergebnisse werden als GeoPackages, QGIS-Projekte und PDF-Karten ausgegeben, sodass sie direkt in QGIS analysiert und weiterverwendet werden können. Aufbauend darauf werden thematische Karten erstellt, die sowohl offizielle Planungsgrundlagen als auch zusätzlich abgeleitete Konflikt-, Ausschluss- und Kontextinformationen für erneuerbare Energien darstellen.

### 1.1 Ausgangslage und Motivation

Für zahlreiche Fragestellungen im Bereich erneuerbarer Energien existieren bereits umfangreiche Datengrundlagen. Der Freistaat Bayern stellt beispielsweise Vorrang- und Vorbehaltsgebiete für Windenergie sowie verschiedene Planungskulissen für Freiflächen-Photovoltaik bereit. Gleichzeitig stehen mit OpenStreetMap und weiteren offenen Geodatenquellen zusätzliche Informationen zur Verfügung, die für die Analyse und Kartendarstellung genutzt werden können.

Die Herausforderung besteht darin, diese heterogenen Datenquellen effizient zusammenzuführen und für unterschiedliche Gemeinden reproduzierbar auszuwerten. Ziel ist daher nicht die Entwicklung einer vollständigen Standortbewertung, sondern die automatisierte Aufbereitung relevanter Geodaten und deren Zusammenführung in einer gemeinsamen Analyse- und Kartenpipeline.

### 1.2 Zielsetzung und Fragestellung

Ziel dieser Arbeit ist die Entwicklung einer reproduzierbaren Geodatenpipeline zur automatisierten Verarbeitung und Visualisierung von Geodaten für erneuerbare Energien auf Gemeindeebene. Dabei sollen sowohl offizielle Planungs- und Referenzdaten des Freistaats Bayern als auch selbst erzeugte Analyse-, Konflikt- und Ausschlusslayer in einem gemeinsamen Workflow verarbeitet werden.

Für die Windenergie werden unter anderem Vorrang- und Vorbehaltsgebiete der Regionalplanung berücksichtigt. Im Bereich der Freiflächen-Photovoltaik werden offizielle Planungskulissen des Energie-Atlas Bayern integriert. Ergänzend werden aus weiteren Geodatenquellen zusätzliche Konflikt-, Ausschluss- und Kontextinformationen abgeleitet und gemeinsam kartografisch dargestellt.

Die zentrale Fragestellung lautet:

> Wie können amtliche und offene Geodaten automatisiert verarbeitet und kombiniert werden, um Planungsgrundlagen sowie zusätzliche Konflikt- und Kontextinformationen für erneuerbare Energien auf Gemeindeebene kartografisch darzustellen?

Dabei steht nicht die vollständige rechtliche Bewertung potenzieller Standorte im Vordergrund, sondern die Entwicklung eines reproduzierbaren Workflows zur automatisierten Datenaufbereitung und Kartenerstellung.

### 1.3 Abgrenzung der Arbeit

Die im Rahmen dieser Arbeit erzeugten Karten stellen keine rechtsverbindliche Planungs- oder Genehmigungsgrundlage dar. Die Genehmigungsfähigkeit von Windenergie-, Photovoltaik- oder Wasserkraftstandorten hängt von zahlreichen technischen, rechtlichen und kommunalen Rahmenbedingungen ab, die nicht vollständig automatisiert berücksichtigt werden können. Hierzu zählen beispielsweise lokale Bebauungspläne, kommunale Vorgaben oder standortspezifische Abstandsregelungen.

Aus diesem Grund werden bereits vorhandene und fachlich geprüfte Datensätze des Freistaats Bayern, wie Wind-Vorranggebiete, Wind-Vorbehaltsgebiete oder die PV-Freiflächenkulisse, in die Analyse integriert. Die zusätzlich erzeugten Konflikt- und Ausschlussflächen dienen als ergänzende Informationsgrundlage und ersetzen keine fachliche Einzelfallprüfung.

Der Schwerpunkt der Arbeit liegt auf der Entwicklung eines reproduzierbaren Geodaten-Workflows, der unterschiedliche Datenquellen automatisiert zusammenführt und für die kartografische Darstellung aufbereitet.

## 2. Datenbasis

Dieses Kapitel erklärt die verwendeten Datensätze und warum sie genutzt werden.

### 2.1 Allgemeine Datengrundlagen

#### 2.1.1 Verwaltungsgrenzen

Inhalt:

- ALKIS-Verwaltungsgrenzen Bayern
- Extraktion der Zielgemeinde
- Grundlage für alle Zuschnitte
- Koordinatensystem `EPSG:25832 / ETRS89 UTM Zone 32N`

#### 2.1.2 Landnutzung

Inhalt:

- amtliche tatsächliche Nutzung Bayern
- Nutzung als Grundlage für Ausschluss-, Potenzial- und Detailflächen
- vollständiger Bayern-Datensatz wird lokal genutzt und anschließend auf die
  Gemeinde zugeschnitten

#### 2.1.3 Schutzgebiete

Inhalt:

- harte Naturschutzrestriktionen
- weiche Naturschutz-Konfliktflächen
- windspezifische Schutz- bzw. Konfliktflächen
- Erklärung, warum die Layer getrennt, aber auch aggregiert verwendet werden

#### 2.1.4 OpenStreetMap

Inhalt:

- OSM als ergänzende Datenquelle
- Straßen und Wege als Linienlayer
- Verkehrsachsen für Solar-Korridore
- Hinweis: OSM ist keine amtliche Planungsgrundlage, aber gut für
  reproduzierbare Näherungen geeignet

### 2.2 Windbezogene Datengrundlagen

Inhalt:

- WFS Regionalplanung Bayern
- Vorranggebiete Wind
- Vorbehaltsgebiete Wind
- windspezifische Schutzdaten wie Vogelkulissen

### 2.3 Solarbezogene Datengrundlagen

Inhalt:

- Energie-Atlas Bayern: Planungsgrundlagen Solar
- PV-Freiflächenkulisse als WMS-Referenz
- OSM-Autobahnen und Schienenwege für 500-m- und 200-m-Korridore
- rechtliche Orientierung:
  - EEG 2023 für 500-m-Förderkulisse
  - BauGB für 200-m-Privilegierung

Wichtig erklären:

- Der WMS ist ein georeferenziertes Kartenbild.
- Er ist kein sauber bearbeitbarer Vektorlayer mit Attributtabelle.
- Deshalb wird er als Referenzlayer genutzt, während eigene Korridore als
  Vektorlayer berechnet werden.

### 2.4 Wasserbezogene Datengrundlagen

Falls Wasser noch nicht vollständig umgesetzt ist:

- geplante Datenquellen nennen
- mögliche Layer: Gewässer, Wasserschutzgebiete, Überschwemmungsgebiete
- erklären, dass die Pipeline-Struktur bereits vorbereitet ist

## 3. Methodik

### 3.1 Allgemeiner Workflow und Gesamtaufbau der Pipeline

Die entwickelte Pipeline ist modular aufgebaut und gliedert sich in drei Verarbeitungsebenen. Zunächst werden allgemeine Basisdaten vorbereitet, anschließend werden technologiespezifische Layer für Windenergie, Freiflächen-Photovoltaik und perspektivisch Wasserkraft erzeugt. Abschließend werden die Ergebnisse automatisiert in QGIS-Projekten und PDF-Karten zusammengeführt.

Die übergeordnete Ausführung erfolgt über Steuerungsskripte wie `run_workflow.sh`, `scripts/1_prepare_data.py` und `scripts/3_generate_map.py`. Dadurch kann der Workflow mit einer Gemeinde und einer Technologie als Parameter gestartet werden. Die Trennung zwischen Datenvorbereitung und Kartenerzeugung ist bewusst gewählt, da die Datenverarbeitung überwiegend in der Python-Umgebung `.venv-wsl` ausgeführt wird, während die Kartenerstellung auf PyQGIS und damit auf die QGIS-/System-Python-Umgebung angewiesen ist.

Eine vollständige Übersicht der Skripte sowie ihrer jeweiligen Eingabe- und Ausgabedaten befindet sich im Anhang. Zusätzlich dokumentiert die Skript-Output-Übersicht, welche Ergebnisse in der finalen PDF-Karte dargestellt werden und welche Layer im QGIS-Projekt als Detail- und Attributlayer für Analyse und Nachvollziehbarkeit verfügbar bleiben.

### 3.2 Gemeinsame Datenvorbereitung

Die gemeinsame Datenvorbereitung bildet die Grundlage für alle technologiespezifischen Verarbeitungsschritte. Sie wird unabhängig davon durchgeführt, ob anschließend Wind-, Solar- oder Wasserdaten verarbeitet werden. Ziel ist es, die benötigten Basisdaten automatisiert bereitzustellen, auf die ausgewählte Gemeinde zu beziehen und in einer einheitlichen Projektstruktur für die weiteren Schritte abzulegen.

Zunächst werden mit dem Skript `1_download_data.py` die benötigten Rohdaten heruntergeladen oder bereits vorhandene Datensätze wiederverwendet. Dazu gehören insbesondere Verwaltungsgrenzen, Schutzgebietsdaten, Landnutzungsdaten sowie weitere fachbezogene Ausgangsdaten. Die Rohdaten bleiben unverändert im Projektordner `data/raw` erhalten, damit die Verarbeitung reproduzierbar bleibt und spätere Schritte nachvollzogen werden können.

Anschließend wird mit `2_extract_municipality_boundary.py` die Grenze der ausgewählten Gemeinde aus dem amtlichen Verwaltungsdatensatz extrahiert. Diese Gemeindegrenze dient im gesamten Workflow als zentrale räumliche Bezugsfläche. Alle weiteren Daten werden entweder auf diese Grenze zugeschnitten oder in einem erweiterten Analysebereich um die Gemeinde herum verarbeitet.

Das Skript `3_build_protection_layers.py` erstellt aus den verschiedenen Schutzgebietsdaten zusammengefasste Schutzgebietslayer. Dabei werden die Schutzgebiete methodisch in harte und weiche Restriktionen eingeteilt. Harte Restriktionen umfassen streng geschützte Flächen, während weiche Restriktionen großräumige Konflikt- oder Prüfflächen darstellen. Zusätzlich werden windbezogene Schutz- und Konfliktflächen separat vorbereitet.

Mit `4_clip_landuse.py` werden die amtlichen Landnutzungsdaten auf die Gemeinde zugeschnitten. Da der originale Landnutzungsdatensatz sehr umfangreich ist, wird die Gemeinde-Bounding-Box zur effizienteren Verarbeitung als räumlicher Vorfilter genutzt. Anschließend werden die relevanten Flächen exakt mit der Gemeindegrenze verschnitten. Die einzelnen Landnutzungslayer bleiben im Output erhalten, sodass später nachvollzogen werden kann, aus welchen Nutzungsklassen technologiespezifische Ausschluss-, Potenzial- oder Detailflächen abgeleitet wurden.

Abschließend werden mit `5_download_osm_network_data.py` OpenStreetMap-Daten für Straßen und Schienenwege geladen. Diese Daten werden nicht nur innerhalb der Gemeinde, sondern in einem erweiterten Analysekontext um die Gemeinde herum abgefragt. Dadurch werden auch Verkehrsachsen berücksichtigt, die knapp außerhalb der Gemeinde liegen, deren Puffer oder Wirkbereiche aber in das Untersuchungsgebiet hineinreichen können.

Die OSM-Daten ergänzen die amtlichen Landnutzungsdaten insbesondere bei der Darstellung von Straßen und Wegen. Im amtlichen Landnutzungsdatensatz werden Verkehrsflächen als flächenhafte Landnutzung erfasst. Dadurch ist nur eingeschränkt erkennbar, welche Art von Verkehrsweg vorliegt. OpenStreetMap bietet hier eine feinere Differenzierung, da Verkehrsobjekte als Linien mit zusätzlichen Attributen gespeichert werden. So kann beispielsweise zwischen Autobahnen, regionalen Straßen, Wohnstraßen, landwirtschaftlichen Wegen und Schienenwegen unterschieden werden. Für die Verarbeitung werden diese Klassen über OSM-Tags wie `motorway`, `primary`, `residential`, `track` oder `rail` gefiltert. Dadurch können je nach Technologie gezielt nur die fachlich relevanten Verkehrsachsen berücksichtigt oder ausgeschlossen werden.

### 3.3 Wind-Workflow

Nach der gemeinsamen Datenvorbereitung erfolgt die windspezifische Verarbeitung. Ziel des Wind-Workflows ist es, offizielle Planungsdaten mit Schutzgebieten, Landnutzungsinformationen und weiteren Konfliktflächen zusammenzuführen. Dadurch entsteht eine einheitliche Datengrundlage für die spätere Darstellung und Prüfung in QGIS.

Zunächst werden mit dem Skript `1_clip_wind_planning_areas.py` die offiziellen Vorrang- und Vorbehaltsgebiete der Regionalplanung auf das Untersuchungsgebiet zugeschnitten. Diese Windplanungsflächen werden über den WFS-Dienst der Regionalplanung Bayern als Vektordaten bereitgestellt. Dadurch können sie exakt mit der Gemeindegrenze verschnitten werden. Neben den einzelnen Layern für Vorrang- und Vorbehaltsgebiete wird zusätzlich ein gemeinsamer Layer für windspezifische Planungsflächen erzeugt.

Anschließend werden mit `2_prepare_wind_landuse.py` die amtlichen Landnutzungsdaten für die Windanalyse ausgewertet. Die einzelnen Landnutzungsklassen werden dabei in Ausschlussflächen, Potenzialflächen, geeignete Flächen und aktuell nicht genutzte Flächen eingeteilt. Für die finale Kartendarstellung sind vor allem die Ausschlussflächen relevant. Dazu zählen beispielsweise Wohnnutzung, Freizeitanlagen, sensible Nutzungen oder wasserbezogene Flächen. Die weiteren Kategorien werden nicht direkt als Ergebnisflächen in der finalen Karte dargestellt, bleiben jedoch als Detail- und Prüflayer im QGIS-Projekt erhalten. Dadurch kann nachvollzogen werden, welche Nutzungsklassen verarbeitet wurden und wie sie methodisch eingeordnet sind.

Im nächsten Schritt erstellt `3_build_wind_landuse_buffers.py` zusätzliche Pufferzonen um ausgewählte sensible Nutzungen. Für Wohnnutzung wird beispielsweise ein erster Arbeitsabstand verwendet. Die erzeugten Puffer werden anschließend wieder auf die Gemeindegrenze zugeschnitten. Die verwendeten Abstände sind als methodische Arbeitsannahmen zu verstehen und können bei geänderten fachlichen oder rechtlichen Anforderungen angepasst werden.

Mit `4_prepare_wind_osm_streets.py` werden die zuvor geladenen OpenStreetMap-Straßen für die Windanalyse aufbereitet. Dabei werden relevante Straßenklassen aus den OSM-Daten gefiltert. Da OSM-Straßen als Linien mit differenzierten Attributen vorliegen, können sie genauer unterschieden werden als die flächenhaften Verkehrsangaben im amtlichen Landnutzungsdatensatz. Die erzeugten Layer dienen vor allem als Straßen- und Wegekontext sowie als mögliche Grundlage für spätere Ausschluss- oder Prüfflächen.

Abschließend kombiniert `5_build_wind_exclusion_layer.py` die erzeugten Landnutzungspuffer und die vorbereiteten OSM-Layer zu einer gemeinsamen Ausschlusskulisse. Das Ergebnis ist ein zusammengefasster Wind-Ausschlusslayer, der für die weitere Prüfung im QGIS-Projekt bereitgestellt wird. Zusätzlich bleiben die einzelnen Eingabelayer erhalten, damit die Entstehung der Ausschlussflächen nachvollzogen werden kann.

### 3.4 Solar-Workflow

Der Solar-Workflow kombiniert offizielle Planungskulissen für Freiflächen-Photovoltaik mit selbst erzeugten Analyse- und Ausschlusslayern. Im Unterschied zu den Windplanungsdaten liegen wichtige Solardaten des Energie-Atlas Bayern als WMS-Dienst vor. Diese Daten eignen sich vor allem als visuelle Referenz, besitzen aber nicht dieselbe Weiterverarbeitbarkeit wie Vektordaten.

Mit `1_prepare_solar_corridor_layers.py` werden zunächst die 200-m- und 500-m-Korridore entlang relevanter Verkehrsachsen erzeugt. Vergleichbare Informationen sind zwar in den amtlichen Planungsgrundlagen enthalten, werden dort jedoch als WMS beziehungsweise Rasterdarstellung bereitgestellt. Für die weitere Analyse wurden die Korridore deshalb zusätzlich als eigene Vektorlayer aus OpenStreetMap-Verkehrsachsen aufgebaut. Dadurch können die Flächen in QGIS attributbasiert untersucht, gefiltert und mit weiteren Geodaten kombiniert werden. Der Abgleich mit den amtlichen Referenzdaten erfolgt später im Rahmen der Verifikation.

Mit `2_prepare_solar_landuse.py` werden die amtlichen Landnutzungsdaten für die Solaranalyse ausgewertet. Waldflächen, Wohnnutzung, Gewässer, Verkehrsflächen sowie weitere sensible oder bereits genutzte Flächen werden als Ausschlussflächen klassifiziert. Zusätzlich wird ein vektorbasierter Landnutzungslayer erzeugt, der eine vereinfachte Annäherung an mögliche PV-Freiflächen darstellt. Dieser Layer ist keine amtliche Planungskulisse und ersetzt nicht die offiziellen Daten des Energie-Atlas Bayern. Er dient im QGIS-Projekt als zusätzlicher Detail- und Prüflayer, um Flächen und Attribute besser auszuwerten sowie blockierte oder potenziell relevante Standorte nachvollziehen zu können.

Das Skript `3_download_solar_reference_wms.py` lädt anschließend die offiziellen WMS-Layer der PV-Freiflächenkulisse des Energie-Atlas Bayern herunter. Da diese Daten als Rasterbilder bereitgestellt werden, können sie nicht exakt mit der Gemeindegrenze verschnitten werden. Stattdessen erfolgt die Abfrage über die Bounding Box des Untersuchungsgebiets. Die erzeugten georeferenzierten Rasterdateien dienen im QGIS-Projekt als amtliche Referenz und werden zusätzlich in die Kartendarstellung integriert.

Die Ergebnisse des Solar-Workflows bestehen somit aus offiziellen Referenzrastern, selbst erzeugten Vektorlayern sowie den 200-m- und 500-m-Korridoren entlang relevanter Verkehrsachsen. Dadurch können sowohl amtliche Planungskulissen dargestellt als auch eigene Analyseflächen im QGIS-Projekt attributbasiert geprüft werden.

### 3.5 Wasser-Workflow

Der Wasser-Workflow ist in der Projektstruktur vorgesehen, aber noch nicht in demselben Umfang umgesetzt wie Wind und Solar. Methodisch soll er später wasserbezogene Datengrundlagen wie Gewässer, Wasserschutzgebiete, Überschwemmungsflächen oder weitere hydrologische Kontextdaten aufnehmen. Die vorhandene Pipeline-Struktur erlaubt es, diese Daten analog zu Wind und Solar herunterzuladen, auf die Gemeinde zu beziehen und als QGIS- sowie Kartenlayer bereitzustellen.

In der Arbeit kann dieser Abschnitt daher als vorbereiteter Erweiterungspfad beschrieben werden. Wichtig ist dabei die Abgrenzung, dass die automatisierte Verarbeitung für Wind und Solar bereits als Referenzworkflow umgesetzt ist, während Wasser perspektivisch ergänzt und fachlich weiter konkretisiert werden muss.

### 3.6 Kartenerzeugung und QGIS-Projekt

Nach Abschluss der gemeinsamen und technologiespezifischen Verarbeitung werden die erzeugten Daten automatisiert für QGIS und den PDF-Export vorbereitet. Dieser Teil der Pipeline stellt sicher, dass die Ergebnisse nicht nur als einzelne Dateien vorliegen, sondern direkt in einem QGIS-Projekt geprüft, analysiert und kartografisch dargestellt werden können.

Mit `1_prepare_overview_layers.py` werden zunächst Übersichtslayer für die Karten erstellt. Dazu gehören ein vereinfachter Bayern-Umriss sowie ein Locator-Layer für die ausgewählte Gemeinde. Der Bayern-Umriss wird einmalig erzeugt und anschließend für weitere Karten wiederverwendet. Die ausgewählte Gemeinde wird in der Übersichtskarte hervorgehoben, sodass ihre Lage innerhalb Bayerns schnell erkennbar ist.

Anschließend erstellt `2_create_map_qgis_project.py` ein technologiespezifisches QGIS-Projekt. Dabei werden die Gemeindegrenze, die vorbereiteten Fachlayer, Schutzgebiete, Referenzdaten und weitere Kontextlayer automatisch geladen. Zusätzlich wird eine grundlegende Symbolisierung angewendet, damit die Layer direkt in QGIS geprüft werden können. Neben den sichtbaren Kartenlayern enthält das Projekt auch Detail- und Attributlayer. Diese sind teilweise standardmäßig deaktiviert und dienen vor allem der Nachvollziehbarkeit. So können zusammengeführte Layer, etwa harte und weiche Naturschutzflächen oder Nutzungsausschlüsse, bei Bedarf wieder auf ihre ursprünglichen Einzellayer wie Nationalparke, Ramsar-Gebiete, Landschaftsschutzgebiete oder einzelne Landnutzungsklassen zurückgeführt werden.

Bei der Solarkarte wird zusätzlich ein vektorbasierter Landnutzungslayer eingebunden, der eine vereinfachte Annäherung an mögliche PV-Freiflächen darstellt. Dieser Layer dient nicht als amtliche Planungskulisse, sondern als zusätzlicher Analyse- und Prüflayer im QGIS-Projekt. Dadurch können die zugrunde liegenden Attribute besser untersucht und mit den amtlichen Referenzdaten eingeordnet werden.

Zum Schluss erzeugt `3_generate_map_pdf.py` aus dem QGIS-Projekt eine PDF-Karte. Das Skript erstellt ein Kartenlayout im Querformat mit Hauptkarte, Legende, Maßstab, Nordpfeil, Quellenangaben und Übersichtskarte. Die Kartentexte, Legenden und Layoutparameter werden über `map_config.py` technologiespezifisch gesteuert. Dadurch besitzen Wind- und Solarkarten einen einheitlichen Aufbau, während Inhalt, Beschreibung und Legende an die jeweilige Technologie angepasst sind.

Die Legende ist bewusst technologiespezifisch standardisiert. Dadurch können Karten verschiedener Gemeinden besser miteinander verglichen werden. Je nach Gemeinde müssen jedoch nicht alle in der Legende aufgeführten Kategorien tatsächlich im Untersuchungsgebiet vorkommen. Beispielsweise kann eine Gemeinde keine Wind-Vorranggebiete, keine Vorbehaltsgebiete oder keine Flächen einer bestimmten PV-Kategorie enthalten. Die standardisierte Legende bleibt dennoch erhalten, um den Kartenaufbau über mehrere Gemeinden hinweg konsistent zu halten.

### 3.7 Verifikation

Die Verifikation erfolgt sowohl durch automatische Ausgaben der Skripte als auch durch manuelle Kontrolle in QGIS. Dabei werden die erzeugten Layer mit den ursprünglichen Datenquellen verglichen und auf räumliche Plausibilität geprüft. Besonders wichtig ist die Kontrolle der Gemeindegrenze, der Schutzgebietsflächen, der Windplanungsdaten, der Solar-WMS-Referenz sowie der aus Landnutzung und OSM abgeleiteten Layer.

Die Detail- und Attributlayer im QGIS-Projekt dienen genau dieser Nachvollziehbarkeit. Während die finale PDF-Karte bewusst nur aggregierte und lesbare Kartenlayer zeigt, bleiben im QGIS-Projekt die zugrunde liegenden Einzellayer erhalten. Dadurch kann geprüft werden, aus welchen Ursprungsdaten ein zusammengefasster Layer entstanden ist und welche Attribute einzelnen Flächen zugeordnet sind.

## 4. Ergebnisse

### 4.1 Windkarte

Inhalt:

- finale Windkarte einfügen
- Aussage der Karte erklären
- sichtbare Layer kurz beschreiben
- erklären, was Nutzungsausschluss und Naturschutzrestriktionen bedeuten

### 4.2 Solarkarte

Inhalt:

- finale Solarkarte einfügen
- PV-Freiflächenkulisse erklären
- 200-m- und 500-m-Korridore erklären
- WMS-Referenz und eigene Vektorkorridore voneinander abgrenzen

### 4.3 Wasserkarte

Falls vorhanden:

- Karte einfügen und Layer erklären

Falls noch nicht vollständig umgesetzt:

- Stand der Vorbereitung beschreiben
- fachlichen Ausbau nennen

### 4.4 Auswertung und Übertragbarkeit

Inhalt:

- Drachselsried als Hauptbeispiel
- Bodenmais und München als Testfälle für andere Gemeindegrößen
- zeigen, dass die Pipeline grundsätzlich auf andere Gemeinden übertragbar ist
- Grenzen bei sehr großen oder sehr kleinen Gemeinden nennen

## 5. Diskussion

### 5.1 Vorteile des Workflows

Inhalt:

- reproduzierbar
- modular
- auf andere Gemeinden übertragbar
- QGIS-Projekt bleibt explorierbar
- PDF-Karte bleibt lesbar

### 5.2 Grenzen und fachliche Einschätzung

Inhalt:

- OSM ist nicht amtlich
- WMS ist nur ein Kartenbild
- Puffer sind Näherungen
- keine Genehmigungsprüfung
- Datenaktualität und Datenqualität begrenzen die Aussagekraft

## 6. Fazit und Ausblick

### 6.1 Was wurde erreicht?

Kurz zusammenfassen:

- automatisierte Pipeline
- Wind- und Solarworkflow
- QGIS-Projekte
- PDF-Karten
- strukturierte Outputdaten

### 6.2 Beantwortung der Fragestellung

Die Fragestellung direkt aufgreifen und beantworten.

### 6.3 Ausblick

Mögliche Erweiterungen:

- Wasserworkflow fertigstellen
- weitere Gemeinden testen
- Stromnetz, Umspannwerke, Verbraucher ergänzen
- Eignungsmodell verfeinern
- zusätzliche Validierungsschritte

## Literaturverzeichnis

Hier alle verwendeten Quellen aufführen:

- amtliche Geodatenportale
- WFS/WMS-Dienste
- OpenStreetMap
- gesetzliche Bezüge EEG und BauGB
- QGIS-Dokumentation, falls verwendet

## Anhang

Mögliche Inhalte:

- Workflowdiagramm
- Datensatzübersicht
- Skriptübersicht
- zusätzliche Karten
  - Drachselsried Wind
  - Drachselsried Solar
  - Drachselsried Wasser, falls vorhanden
  - Bodenmais
  - München
- Verifikationsscreenshots oder QGIS-Hinweise

