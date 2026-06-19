# QGIS-Datensatz und Layerstruktur

Diese Datei beschreibt, wie das automatisch erzeugte QGIS-Projekt aufgebaut
ist und wie die Layer fachlich zu verstehen sind. Die Beschreibung ist so
formuliert, dass sie später in Bericht oder MkDocs übernommen und für Solar
und Wasser erweitert werden kann.

## Grundprinzip

Das QGIS-Projekt enthält zwei Ebenen:

1. **sichtbare Kartenlayer**
2. **Detail- und Attributlayer**

Die sichtbaren Kartenlayer bilden die eigentliche Kartenaussage. Sie sind
bewusst zusammengefasst, damit die Karte lesbar bleibt und nicht durch zu viele
Einzellayer überladen wird.

Die Detail- und Attributlayer dienen der Kontrolle, Attributprüfung und
Dokumentation. Sie zeigen, aus welchen Ursprungsdaten die aggregierten
Kartenlayer abgeleitet wurden. Dadurch kann in QGIS nachvollzogen werden,
welche Layer in die Verarbeitung eingegangen sind, ohne dass alle Einzellayer
in der PDF-Karte dargestellt werden müssen.

## Windkarte

Die Windkarte zeigt offizielle Windenergieflächen und verschiedene
Restriktionsflächen innerhalb der ausgewählten Gemeinde.

### Sichtbare Kartenlayer

Diese Layer sind für die kartografische Aussage sichtbar:

| Layergruppe | Bedeutung |
| --- | --- |
| Gemeindegrenze | amtliche Grenze der ausgewählten Gemeinde |
| Vorranggebiete Wind | offizielle regionalplanerische Vorranggebiete für Windenergienutzung |
| Vorbehaltsgebiete Wind | offizielle regionalplanerische Vorbehaltsgebiete für Windenergienutzung |
| Harte Naturschutz-Restriktionen | zusammengefasste strenge Schutzgebietsflächen |
| Windspezifische Restriktionen | zusätzliche windrelevante Schutz- oder Konfliktflächen |
| Weiche Naturschutz-Konfliktflächen | großräumige Schutz- und Konfliktflächen, die nicht pauschal ausgeschlossen werden |
| Nutzungsausschluss | zusammengefasste Ausschlussflächen aus Landnutzung und ggf. weiteren flächenhaften Ausschlusslayern |
| Straßen und Wege | linienhafte OSM-Straßen- und Wegeinformationen als Orientierung bzw. fachlicher Kontext |

### Detail- und Attributlayer Naturschutz

Die Naturschutzlayer werden fachlich getrennt abgelegt:

| Gruppe | Inhalt |
| --- | --- |
| Detail- und Attributlayer Naturschutz hart | Naturschutzgebiete, Nationalparke, Nationale Naturmonumente, flächenhafte Naturdenkmale, geschützte Landschaftsbestandteile, Ramsar-Gebiete, Natura 2000 FFH, Natura 2000 Vogelschutz sowie punktförmige Naturdenkmale und geschützte Landschaftsbestandteile |
| Detail- und Attributlayer Naturschutz weich | Biosphärenreservate, Landschaftsschutzgebiete, Naturparke |
| Detail- und Attributlayer Naturschutz Wind | windrelevante Vogelkulissen |

Die sichtbaren Naturschutzlayer in der Karte sind aggregiert. Die Detail- und
Attributlayer bleiben im QGIS-Projekt verfügbar, damit einzelne
Schutzgebietskategorien geprüft werden können.

### Detail- und Attributlayer Wind-Ausschluss

Diese Gruppe enthält die Einzellayer, aus denen der sichtbare
Nutzungsausschluss abgeleitet wird. Dazu gehören insbesondere gepufferte oder
zusammengefasste Landnutzungsflächen.

Wenn OSM-Straßen und Wege als flächenhafte Puffer in den Nutzungsausschluss
eingehen, werden diese ebenfalls dort dokumentiert. Reine Linienlayer werden
methodisch getrennt betrachtet, weil Linien keine Ausschlussflächen sind.

### Detail- und Attributlayer OSM

Diese Gruppe enthält die OSM-Straßen- und Wegeinformationen als
Attribut- und Kontrolllayer. Sie dient dazu, die geladenen OSM-Klassen in QGIS
zu prüfen, zum Beispiel über das Attribut `highway`.

Die OSM-Daten können zwei Rollen haben:

- als **sichtbare Linieninformation** in der Karte, wenn Straßen und Wege als
  Orientierung oder Kontext gezeigt werden sollen
- als **Basis für Pufferflächen**, wenn Straßenabstände fachlich als
  Ausschluss- oder Restriktionsflächen modelliert werden

Diese Trennung ist wichtig, weil ein Linienlayer nicht dasselbe ist wie eine
flächenhafte Ausschlusszone.

## Empfehlung zur Darstellung von Straßen und Wegen

Für die finale Windkarte ist eine konstante Darstellung sinnvoll:

1. Straßen und Wege werden als eigener sichtbarer Linienlayer dargestellt,
   wenn sie zur Orientierung oder zur fachlichen Einordnung relevant sind.
2. Flächenhafte Straßenpuffer werden nur dann in den Nutzungsausschluss
   übernommen, wenn ein fachlich begründeter Abstand größer als 0 m definiert
   ist.
3. Die PDF-Legende sollte den sichtbaren Linienlayer als **Straßen und Wege**
   bezeichnen.

Damit bleibt nachvollziehbar:

- OSM-Linien zeigen das Verkehrsnetz.
- OSM-Puffer zeigen methodisch abgeleitete Ausschlussflächen.
- Der Nutzungsausschluss bleibt ein flächenhafter Sammellayer.

## Solar

Der Solarbereich kann nach demselben Prinzip erweitert werden:

| Layergruppe | Bedeutung |
| --- | --- |
| PV-Förderkulisse 500 m | aus OSM-Verkehrsachsen abgeleitete Näherung zur EEG-Förderkulisse |
| PV-Privilegierung 200 m | aus OSM-Verkehrsachsen abgeleitete Näherung zur BauGB-Privilegierung |
| PV-Freiflächenkulisse WMS | amtlicher Referenzlayer aus dem Energie-Atlas Bayern |
| Detail- und Attributlayer Solar | OSM-Verkehrsachsen, Puffergrundlagen und weitere Arbeitslayer |

## Wasser

Der Wasserbereich ist noch erweiterbar. Das gleiche Prinzip kann später für
Gewässer, Wasserschutzgebiete, Überschwemmungsflächen und weitere
wasserbezogene Infrastruktur- oder Konfliktlayer verwendet werden.

## Formulierung für Bericht oder MkDocs

Das QGIS-Projekt wurde bewusst nicht nur als reine Kartenansicht aufgebaut,
sondern als explorierbarer Geodatensatz. Die sichtbaren Layer bilden die
kartografische Hauptaussage, während ausgeblendete Detail- und Attributlayer
die Nachvollziehbarkeit der Verarbeitung sichern. Dadurch können aggregierte
Kartenlayer im Bericht übersichtlich dargestellt werden, ohne die Möglichkeit
zu verlieren, einzelne Ursprungsdaten, Attribute und Zwischenergebnisse in QGIS
zu prüfen.
