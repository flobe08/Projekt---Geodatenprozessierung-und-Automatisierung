# Struktur für die spätere Ausarbeitung

Diese Datei sammelt eine mögliche Gliederung für die schriftliche
Projektarbeit. Sie ist als Arbeitsgrundlage gedacht und verweist auf die
Dokumentationsdateien, die bereits im Projekt gepflegt werden.

## 1. Abstract

Kurz zusammenfassen:

- Ziel: reproduzierbare Geodaten-Pipeline für eine bayerische Gemeinde
- Technologien: Wind, Solar, später Wasser
- Datenquellen: amtliche Geodaten, OpenStreetMap, WMS/WFS
- Ergebnis: strukturierte GeoPackages, QGIS-Projekte und PDF-Karten
- Einordnung: keine rechtsverbindliche Genehmigungsprüfung, sondern
  automatisierte Potenzial- und Konfliktdarstellung

## 2. Einleitung

Inhalt:

- Motivation erneuerbarer Energien auf kommunaler Ebene
- Bedarf an reproduzierbaren und nachvollziehbaren Geodaten-Workflows
- Problem: viele Datenquellen, unterschiedliche Formate, unterschiedliche
  fachliche Bedeutung
- Zielgemeinde als Beispiel, Pipeline aber auf andere Gemeinden übertragbar

Mögliche zentrale Fragestellung:

> Welche räumlichen Potenzial- und Konfliktflächen für erneuerbare Energien
> lassen sich für eine Gemeinde automatisiert aus offenen Geodaten ableiten
> und kartografisch darstellen?

## 3. Untersuchungsgebiet

Beschreiben:

- ausgewählte Gemeinde
- Datenbasis der Gemeindegrenze
- Koordinatensystem `EPSG:25832 / ETRS89 UTM Zone 32N`
- Rolle der Gemeindegrenze als harte räumliche Bezugsfläche

Wichtige Projektdateien:

- `description/DATASET_INFORMATION.md`
- `description/VERIFIKATION.md`

## 4. Datenbasis und Datensatzwahl

Dieses Kapitel sollte erklären, warum welche Daten verwendet werden.

### 4.1 Allgemeine Basisdaten

| Datensatz | Zweck im Projekt |
| --- | --- |
| Verwaltungsgrenzen Bayern | Extraktion der Zielgemeinde und Zuschnitt aller Fachlayer |
| Amtliche tatsächliche Nutzung Bayern | Landnutzung, Nutzungsausschluss, technologiebezogene Detailanalyse |
| Schutzgebiete LfU Bayern | harte und weiche Naturschutzrestriktionen |
| OSM-Straßen und Verkehrswege | ergänzende Netz- und Korridorinformationen |
| Übersichtslayer Bayern | Locator Map in der PDF-Karte |

Wichtig:

- Amtliche Daten werden bevorzugt für rechtlich oder planerisch relevante
  Flächen verwendet.
- OSM wird als ergänzende, nachvollziehbare Näherung genutzt, wenn amtliche
  Vektorinformationen fehlen oder wenn linienhafte Verkehrsachsen benötigt
  werden.

### 4.2 Winddaten

| Datensatz | Verwendung |
| --- | --- |
| WFS Regionalplanung Bayern: Vorranggebiete Wind | sichtbarer Wind-Kartenlayer |
| WFS Regionalplanung Bayern: Vorbehaltsgebiete Wind | sichtbarer Wind-Kartenlayer |
| Vogelkulissen | windspezifische Restriktionsflächen |
| Landnutzung | Nutzungsausschluss und Detailanalyse |
| OSM-Straßen und Wege | sichtbarer Kontextlayer und mögliche Grundlage für spätere Puffer |

Hinweis:

- Vorrang- und Vorbehaltsgebiete sind offizielle Planungskulissen.
- Die Karte zeigt zusätzlich Konflikte und Ausschlussflächen, ersetzt aber
  keine Genehmigungsprüfung.

### 4.3 Solardaten

| Datensatz | Verwendung |
| --- | --- |
| Energie-Atlas Bayern: PV-Freiflächenkulisse WMS | amtliche visuelle Referenz |
| OSM-Autobahnen und Schienenwege | Grundlage für 500-m- und 200-m-Korridore |
| Landnutzung | Detail- und Attributlayer für PV-Freiflächen-Näherung und Ausschluss |
| Naturschutz | harte und weiche Konfliktrahmen |

Wichtig zur WMS-/Rasterlogik:

- Die PV-Freiflächenkulisse wird als WMS bereitgestellt.
- Ein WMS liefert ein georeferenziertes Kartenbild, keinen sauber
  weiterverarbeitbaren Vektorlayer mit Attributtabelle.
- Deshalb wird die WMS-Referenz auf Basis der Gemeinde-Bounding-Box geladen
  und in der Karte visuell eingebunden.
- Ein exakter harter Vektor-Zuschnitt an der Gemeindegrenze ist für diesen
  WMS methodisch nicht der eigentliche Verarbeitungsschritt.
- Die eigenen 200-m- und 500-m-Korridore werden dagegen als Vektorlayer aus
  OSM-Verkehrsachsen berechnet.

### 4.4 Wasserdaten

Wasser ist als Erweiterung vorgesehen.

Mögliche Datensätze:

- Gewässer
- Wasserschutzgebiete
- Überschwemmungsgebiete
- Hochwasserschutzflächen
- wasserbezogene Infrastruktur

Die Struktur sollte später analog zu Wind und Solar aufgebaut werden:

- Rohdaten
- gemeindebezogener Zuschnitt
- technologiespezifische Layer
- QGIS-Projekt
- PDF-Karte

## 5. Reproduzierbarer Workflow

Hier den technischen Ablauf erklären.

### 5.1 Gemeinsame Datenvorbereitung

Schritte:

1. Rohdaten herunterladen
2. Gemeindegrenze extrahieren
3. Schutzgebietslayer aufbauen
4. Landnutzung auf die Gemeinde clippen
5. OSM-Netzwerkdaten laden

Warum:

- Alle Technologien verwenden dieselbe Gemeindegrenze.
- Allgemeine Basisdaten werden nur einmal vorbereitet.
- Technologiespezifische Skripte greifen danach auf strukturierte
  Zwischenergebnisse zu.

### 5.2 Wind-Workflow

Schritte:

1. Windplanungsdaten zuschneiden
2. Windbezogene Landnutzung vorbereiten
3. Landnutzungspuffer erzeugen
4. OSM-Straßen für Wind vorbereiten
5. Nutzungsausschluss zusammenführen
6. QGIS-Projekt und PDF-Karte erzeugen

Wichtige Outputlayer:

| Output | Zweck |
| --- | --- |
| `wind_layers.gpkg` | Vorrang- und Vorbehaltsgebiete |
| `landuse_wind_ausschluss.gpkg` | ungeeignete Nutzungen als Grundlage |
| `landuse_wind_ausschluss_puffer.gpkg` | gepufferte Nutzungsausschlüsse |
| `osm_wind_streets.gpkg` | Straßen und Wege als sichtbarer Kontext |
| `wind_ausschluss_gesamt.gpkg` | aggregierter Nutzungsausschluss für Karte |

### 5.3 Solar-Workflow

Schritte:

1. OSM-basierte Korridorgrundlage vorbereiten
2. 200-m- und 500-m-Korridore als Vektorlayer erzeugen
3. Solar-Landnutzung als Detail- und Attributlayer vorbereiten
4. WMS-Referenzbilder des Energie-Atlas Bayern laden
5. QGIS-Projekt und PDF-Karte erzeugen

Wichtige Outputlayer:

| Output | Zweck |
| --- | --- |
| `solar_corridor_basis.gpkg` | OSM-Verkehrsachsen für Solar-Korridore |
| `solar_layers.gpkg` | 200-m- und 500-m-Korridore |
| `landuse_solar_pv_freiflaechen_naehung_vektorlayer.gpkg` | PV-Freiflächen-Näherung aus Landnutzung als Detailansicht |
| `reference/*.png` | WMS-Referenzbilder der PV-Freiflächenkulisse |

### 5.4 Wasser-Workflow

Aktuell als Erweiterung dokumentieren:

- noch nicht final umgesetzt
- gleiche Pipeline-Logik vorgesehen
- spätere Layer und Bewertungskriterien fachlich ergänzen

### 5.5 Kartenerzeugung

Schritte:

1. Übersichtslayer vorbereiten
2. QGIS-Projekt erzeugen
3. PDF-Karte exportieren

Besonderheit:

- Das QGIS-Projekt enthält sichtbare Kartenlayer und ausgeblendete Detail- und
  Attributlayer.
- Die PDF zeigt nur die aggregierte Karteninformation.
- Die kleine Übersichtskarte `Lage in Bayern` wird nur eingefügt, wenn sie im
  Hauptkartenbild keinen relevanten Teil der Gemeinde verdeckt.

## 6. Layer- und Outputstruktur

Hier die Ordnerlogik erklären:

```text
data/processed/
  1_base_boundaries/
  1_base_landuse/
  1_base_osm_streets/
  1_base_overview/
  1_base_protection_areas/

  2_technology_wind/
  2_technology_solar/

  3_qgis_projects/
  3_maps/
```

Diese Struktur trennt:

- gemeinsame Basisdaten
- technologiespezifische Ableitungen
- finale Kartenprodukte

Wichtige Projektdatei:

- `description/SKRIPT_OUTPUT_UEBERSICHT.md`

## 7. Methodische Verarbeitung

Beschreiben:

- Reprojektion bzw. einheitliches Koordinatensystem
- Zuschnitt mit Gemeindegrenze
- Bounding-Box-Laden bei großen Datensätzen
- Pufferlogik
- Zusammenführung aggregierter Layer
- Trennung von sichtbaren Kartenlayern und Detail-/Attributlayern
- Umgang mit Raster/WMS gegenüber Vektordaten

## 8. Ergebnisse

### 8.1 Wind

Beschreiben:

- offizielle Windflächen
- harte und windspezifische Restriktionen
- weiche Naturschutzflächen
- Nutzungsausschluss
- Straßen und Wege als Kontext

### 8.2 Solar

Beschreiben:

- PV-Freiflächenkulisse als WMS-Referenz
- 500-m-EEG-Korridor
- 200-m-BauGB-Korridor
- Naturschutzkonflikte
- Landnutzungsdetaildaten im QGIS-Projekt

### 8.3 Wasser

Als geplante Erweiterung oder Prototyp beschreiben, je nach Projektstand.

## 9. Verifikation

Beschreiben:

- manuelle Prüfung in QGIS
- Vergleich offizieller Ausgangsdaten mit Skript-Outputs
- Gemeindegrenze gegen offiziellen Verwaltungsdatensatz
- Wind-WFS direkt gegen QGIS-WFS-Verbindung
- Solar-WMS als visuelle Referenz
- Prüfung von Detail- und Attributlayern

Wichtige Projektdatei:

- `description/VERIFIKATION.md`

## 10. Diskussion und Limitationen

Mögliche Punkte:

- OSM ist keine amtliche Planungsgrundlage.
- WMS-Referenzen sind visuelle Kartenbilder und keine vollwertigen
  Vektordatensätze.
- Puffer sind methodische Näherungen.
- Die Pipeline ersetzt keine rechtsverbindliche Einzelfallprüfung.
- Die Ergebnisse hängen von Datenaktualität, Verfügbarkeit und
  Datenqualität ab.

## 11. Fazit und Ausblick

Zusammenfassen:

- Pipeline ist für andere Gemeinden wiederholbar.
- Wind und Solar sind strukturiert umgesetzt.
- Wasser kann nach gleicher Logik ergänzt werden.
- QGIS-Projekt und PDF-Karte erfüllen unterschiedliche Zwecke:
  explorierbarer Datensatz vs. kompakte Ergebnisdarstellung.

## 12. Verknüpfung zu vorhandenen Dokumentationsdateien

| Datei | Verwendung in der Ausarbeitung |
| --- | --- |
| `README.md` | Einstieg, Installation, Gesamtziel |
| `Anleitung.md` | Bedienung und manuelle Ausführung |
| `description/DATASET_INFORMATION.md` | Datenquellen und Datensatzwahl |
| `description/SKRIPT_OUTPUT_UEBERSICHT.md` | Skript-Input und Skript-Output |
| `description/WORKFLOW_DIAGRAMME.md` | Methodenfigur und Ablaufdiagramme |
| `description/QGIS_DATENSATZ_UEBERSICHT.md` | Erklärung des QGIS-Projekts |
| `description/WIND_WORKFLOW_NOTES.md` | fachliche Wind-Methodik |
| `description/SOLAR_WORKFLOW_NOTES.md` | fachliche Solar-Methodik |
| `description/VERIFIKATION.md` | Validierung und QGIS-Prüfung |
| `description/LANDUSE_BY_TECHNOLOGY.md` | Landnutzungslogik nach Technologie |
| `description/HIGHWAY_CLASSES.md` | OSM-Straßenklassen und Technologiebezug |

