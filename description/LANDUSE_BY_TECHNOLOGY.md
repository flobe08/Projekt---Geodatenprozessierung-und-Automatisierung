# Landnutzung nach Technologie

Diese Datei dokumentiert, wie die offiziellen Landnutzungs-Layer für die
weiteren Technologien fachlich eingeordnet werden können.

Wichtig:

- Die Tabelle ist eine **erste methodische Einordnung** für die Pipeline.
- Sie ersetzt keine abschließende Genehmigungs- oder Einzelfallprüfung.
- Für die **finalen Karten** sollten in der Regel eher die
  **Ausschluss- und Konfliktflächen** dargestellt werden als alle potenziell
  geeigneten Flächen gleichzeitig. Das hält die Karte lesbar.


## Layer im Originaldatensatz

Diese Layer werden in `data/raw/landuse/landnutzung.gpkg` erwartet:

| Layer | Wind | Solar | Wasser | Begründung |
| --- | --- | --- | --- | --- |
| `ln_abbau` | Manuelle Prüfung | Manuelle Prüfung | Kontext | Abbauflächen sind oft vorbelastet, aber nicht pauschal geeignet oder ausgeschlossen. |
| `ln_aquakulturundfischereiwirtschaft` | Ausschluss | Ausschluss | wichtig / Kontext | Wassergebundene Nutzung, für Wind und Solar ungeeignet, für Wasser fachlich relevant. |
| `ln_bahnverkehr` | Ausschluss / Puffer | Ausschluss / Puffer | Kontext | Verkehrsfläche; für Solar zusätzlich wichtig wegen 200-m- und 500-m-Randstreifen. |
| `ln_bestattung` | Ausschluss | Ausschluss | Ausschluss | Sensibler Nutzungsbereich. |
| `ln_flugverkehr` | Ausschluss | Ausschluss | Ausschluss | Infrastruktur- und Sicherheitsbereich. |
| `ln_forstwirtschaft` | Einzelfall / eingeschränkt | Ausschluss | Kontext | Wald ist für Solar in der Regel ungeeignet, bei Wind aber nicht automatisch ausgeschlossen. |
| `ln_freiluftundnaherholung` | Ausschluss | Ausschluss | Ausschluss / Kontext | Erholungsfunktion, meist konfliktträchtig. |
| `ln_freizeitanlage` | Ausschluss | Ausschluss | Ausschluss / Kontext | Freizeitnutzung soll in der Regel freigehalten werden. |
| `ln_gewerblichedienstleistungen` | Ausschluss | Ausschluss | Kontext | Siedlungs- und Gewerbenutzung. |
| `ln_industrieundverarbeitendesgewerbe` | Ausschluss | Ausschluss | Kontext | Stark anthropogen genutzte Fläche. |
| `ln_kulturundunterhaltung` | Ausschluss | Ausschluss | Ausschluss | Sensible Nutzung. |
| `ln_lagerung` | Manuelle Prüfung | Manuelle Prüfung | Kontext | Nicht pauschal ungeeignet, aber meist nur eingeschränkt nutzbar. |
| `ln_landwirtschaft` | Potenzialfläche | Potenzialfläche | Kontext | Für Wind und Solar meist die wichtigste Suchraumklasse. |
| `ln_oeffentlicheeinrichtungen` | Ausschluss | Ausschluss | Ausschluss | Sensible bzw. öffentliche Nutzung. |
| `ln_ohnenutzung` | Potenzial / Prüfung | Potenzial / Prüfung | Kontext | Kann je nach Lage geeignete Freiflächen enthalten. |
| `ln_schiffsverkehr` | Ausschluss | Ausschluss | wichtig / Kontext | Verkehrs- und Gewässernutzung. |
| `ln_sportanlage` | Ausschluss | Ausschluss | Ausschluss | Bestehende Nutzung mit Konfliktpotenzial. |
| `ln_strassenundwegeverkehr` | unused / spätere Prüfung | Ausschluss / Puffer | Kontext | Verkehrsfläche; für Wind im amtlichen Datensatz zu grob, für Solar rechtlich relevanter Nähebezug. |
| `ln_versorgungundentsorgung` | Ausschluss | Ausschluss | Kontext | Technische Infrastrukturfläche. |
| `ln_wasserwirtschaft` | Ausschluss | Ausschluss | wichtig | Für Wasserkraft fachlich besonders relevant, für Wind und Solar ungeeignet. |
| `ln_wohnnutzung` | Ausschluss / Siedlungspuffer | Ausschluss / Siedlungspuffer | Ausschluss | Wohnnutzung ist für alle drei Technologien konfliktträchtig. |


## Vorgeschlagene Gruppen für die Pipeline

### Wind

#### `landuse_wind_ausschluss`

- `ln_wohnnutzung`
- `ln_bestattung`
- `ln_oeffentlicheeinrichtungen`
- `ln_sportanlage`
- `ln_freizeitanlage`
- `ln_freiluftundnaherholung`
- `ln_bahnverkehr`
- `ln_flugverkehr`
- `ln_schiffsverkehr`
- `ln_wasserwirtschaft`
- `ln_aquakulturundfischereiwirtschaft`

#### `landuse_wind_potenzial`

- `ln_landwirtschaft`
- `ln_ohnenutzung`

Optional nach Einzelfallprüfung:

- `ln_abbau`
- `ln_lagerung`
- `ln_forstwirtschaft`

#### `landuse_wind_geeignet`

- `ln_landwirtschaft`
- `ln_ohnenutzung`

#### `landuse_wind_unused`

- `ln_strassenundwegeverkehr`
- weitere aktuell nicht genutzte Wind-Layer aus dem offiziellen Datensatz

Hinweis:

- Wald wird für Wind hier **nicht pauschal ausgeschlossen**, sondern eher als
  fachlich eingeschränkter Fall behandelt.
- `ln_strassenundwegeverkehr` wird bewusst getrennt gehalten, weil die
  offizielle Landnutzungsklasse auch kleinere Wege enthalten kann und damit
  für einen pauschalen Ausschluss zu grob wäre.
- Die Wind-Landnutzung wird als vier separate Dateien geschrieben:
  - `data/processed/2_technology_wind/<gemeinde>_landuse_wind_ausschluss.gpkg`
  - `data/processed/2_technology_wind/<gemeinde>_landuse_wind_potenzial.gpkg`
  - `data/processed/2_technology_wind/<gemeinde>_landuse_wind_geeignet.gpkg`
  - `data/processed/2_technology_wind/<gemeinde>_landuse_wind_unused.gpkg`


### Solar

#### `landuse_solar_ausschluss`

- `ln_aquakulturundfischereiwirtschaft`
- `ln_bahnverkehr`
- `ln_bestattung`
- `ln_flugverkehr`
- `ln_forstwirtschaft`
- `ln_freiluftundnaherholung`
- `ln_freizeitanlage`
- `ln_gewerblichedienstleistungen`
- `ln_industrieundverarbeitendesgewerbe`
- `ln_kulturundunterhaltung`
- `ln_lagerung`
- `ln_oeffentlicheeinrichtungen`
- `ln_schiffsverkehr`
- `ln_sportanlage`
- `ln_strassenundwegeverkehr`
- `ln_versorgungundentsorgung`
- `ln_wasserwirtschaft`
- `ln_wohnnutzung`

#### `landuse_solar_pv_freiflaechen_naehung_vektorlayer`

- `ln_abbau`
- `ln_landwirtschaft`
- `ln_ohnenutzung`

Hinweis:

- Wald (`ln_forstwirtschaft`) wird für Solar hier als **Ausschluss** behandelt.
- `ln_lagerung` wird ebenfalls als Ausschluss behandelt.
- `landuse_solar_pv_freiflaechen_naehung_vektorlayer` ist eine eigene
  vektorbasierte Näherung möglicher PV-Freiflächen aus der amtlichen
  Landnutzung. Der Layer dient vor allem als Detail- und Attributlayer im
  QGIS-Projekt.
- Die Solar-Landnutzung wird als drei separate Dateien geschrieben:
  - `data/processed/2_technology_solar/<gemeinde>_landuse_solar_ausschluss.gpkg`
  - `data/processed/2_technology_solar/<gemeinde>_landuse_solar_pv_freiflaechen_naehung_vektorlayer.gpkg`
  - `data/processed/2_technology_solar/<gemeinde>_landuse_solar_unused.gpkg`
- Die amtliche PV-Freiflächenkulisse wird zusätzlich als WMS-Referenz genutzt.
  Der Vektorlayer ersetzt diese Referenz nicht, sondern macht die eigene
  Näherung prüfbar und weiterverarbeitbar.


### Wasser

#### `landuse_wasser_kontext`

- `ln_wasserwirtschaft`
- `ln_aquakulturundfischereiwirtschaft`
- `ln_schiffsverkehr`
- `ln_ohnenutzung`

Zusätzlich über andere Datensätze wichtig:

- Gewässer
- Wasserschutzgebiete
- Überschwemmungsgebiete

Hinweis:

- Für Wasser ist Landnutzung eher **Kontextinformation** als der wichtigste
  Hauptfilter. Die eigentlichen Fachlayer kommen dort eher aus Gewässer- und
  Schutzgebietsdaten.
- Die Wasser-Landnutzung wird als vier separate Dateien geschrieben:
  - `data/processed/2_technology_wasser/<gemeinde>_landuse_wasser_ausschluss.gpkg`
  - `data/processed/2_technology_wasser/<gemeinde>_landuse_wasser_kontext.gpkg`
  - `data/processed/2_technology_wasser/<gemeinde>_landuse_wasser_geeignet.gpkg`
  - `data/processed/2_technology_wasser/<gemeinde>_landuse_wasser_unused.gpkg`
- `landuse_wasser_kontext` und `landuse_wasser_geeignet` sind aktuell
  Arbeitslayer für Prüfung und Vergleich, werden aber noch nicht direkt in der
  finalen Karte verwendet.


## Darstellung in finalen Karten

Für die **finale Karte** ist es meist besser, nicht alle potenziellen Flächen
gleichzeitig anzuzeigen. Besser lesbar ist meistens:

1. Gemeindegrenze
2. harte Ausschlussflächen
3. weiche Konfliktflächen
4. technologiespezifische Restriktionen
5. offizielle Energie- oder Planungslayer

Die **Potenzialflächen** können später als abgeleiteter Restflächen-Layer
berechnet werden, müssen aber nicht in jeder Arbeitskarte sofort vollständig
dargestellt werden.
