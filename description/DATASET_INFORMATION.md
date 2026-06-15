# Datensatzinformationen

Diese Datei dokumentiert die wichtigsten Eingabedaten der Pipeline.

Zusätzlich bleiben frühere Datensätze im unteren Teil bewusst erhalten, damit
bereits recherchierte Quellen nicht verloren gehen.

## Allgemein

### Verwaltungsgrenzen Bayern

Datensatz: ALKIS Verwaltungsgebiet Bayern  
Link: https://geodaten.bayern.de/odd/m/4/verwaltung/alkis-verwaltung.zip  
Stand: monatlich aktualisiert  
Lizenz: Creative Commons Namensnennung 4.0 International (CC BY 4.0),
Bayerische Vermessungsverwaltung / LDBV. Quelle angeben.

### Landnutzung Bayern

Datensatz: Landnutzung Bayern, GeoPackage  
Link: https://geodaten.bayern.de/odd/m/3/daten/ln/landnutzung.gpkg  
Stand: abhängig vom Downloadzeitpunkt  
Lizenz: Creative Commons Namensnennung 4.0 International (CC BY 4.0),
Bayerische Vermessungsverwaltung / LDBV. Quelle angeben.

Hinweis:

- wird aktuell nicht im Standard-Download geladen
- wird bei Bedarf separat über `scripts/1_prepare_data/4_clip_landuse.py`
  verarbeitet
- das Original bleibt unter `data/raw/landuse/landnutzung.gpkg` unverändert
- der Output ist ein kleinerer Gemeinde-Arbeitsdatensatz mit den einzelnen
  zugeschnittenen `ln_*`-Layern:
  `data/processed/landuse/landnutzung_<gemeinde>.gpkg`
- methodisch wird der vollständige offizielle Bayern-Datensatz einmal lokal
  vorgehalten, weil ein echter Teil-Download nur für eine Gemeinde über das
  große GeoPackage nicht zuverlässig möglich ist

## Allgemein: Schutzgebiete des Naturschutzes

### Biosphärenreservate

Datensatz: Biosphärenreservate, EPSG:25832, Shapefile  
Link: https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/biosphaerenreservate_epsg25832_shp.zip  
Stand: 01.03.2024 12:00 Uhr  
Lizenz: Creative Commons Namensnennung 4.0 International (CC BY 4.0).
Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de.

### Landschaftsschutzgebiete

Datensatz: Landschaftsschutzgebiete, EPSG:25832, Shapefile  
Link: https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/lsg_epsg25832_shp.zip  
Stand: 01.03.2024 12:00 Uhr  
Lizenz: Creative Commons Namensnennung 4.0 International (CC BY 4.0).
Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de.

### Nationalparke

Datensatz: Nationalparke, EPSG:25832, Shapefile  
Link: https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/nlp_epsg25832_shp.zip  
Stand: 01.03.2024 12:00 Uhr  
Lizenz: Creative Commons Namensnennung 4.0 International (CC BY 4.0).
Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de.

### Naturparke

Datensatz: Naturparke, EPSG:25832, Shapefile  
Link: https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/naturparke_epsg25832_shp.zip  
Stand: 01.03.2024 12:00 Uhr  
Lizenz: Creative Commons Namensnennung 4.0 International (CC BY 4.0).
Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de.

### Naturschutzgebiete

Datensatz: Naturschutzgebiete, EPSG:25832, Shapefile  
Link: https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/nsg_epsg25832_shp.zip  
Stand: 01.03.2024 12:00 Uhr  
Lizenz: Creative Commons Namensnennung 4.0 International (CC BY 4.0).
Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de.

### Nationale Naturmonumente

Datensatz: Nationale Naturmonumente, EPSG:25832, Shapefile  
Link: https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/nationale_naturmonumente_epsg25832_shp.zip  
Stand: 01.03.2024 12:00 Uhr  
Lizenz: Creative Commons Namensnennung 4.0 International (CC BY 4.0).
Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de.

### Geschützte Landschaftsbestandteile Punkte

Datensatz: Geschützte Landschaftsbestandteile Punkte, EPSG:25832, Shapefile  
Link: https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/landschaftsbestandteil_punktfoermig_epsg25832_shp.zip  
Stand: 01.03.2024 12:00 Uhr  
Lizenz: Creative Commons Namensnennung 4.0 International (CC BY 4.0).
Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de.

### Geschützte Landschaftsbestandteile Flächen

Datensatz: Geschützte Landschaftsbestandteile Flächen, EPSG:25832, Shapefile  
Link: https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/landschaftsbestandteil_flaechig_epsg25832_shp.zip  
Stand: 01.03.2024 12:00 Uhr  
Lizenz: Creative Commons Namensnennung 4.0 International (CC BY 4.0).
Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de.

### Naturdenkmale Punkte

Datensatz: Naturdenkmale Punkte, EPSG:25832, Shapefile  
Link: https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/naturdenkmal_punktfoermig_epsg25832_shp.zip  
Stand: 01.03.2024 12:00 Uhr  
Lizenz: Creative Commons Namensnennung 4.0 International (CC BY 4.0).
Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de.

### Naturdenkmale Flächen

Datensatz: Naturdenkmale Flächen, EPSG:25832, Shapefile  
Link: https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/naturdenkmal_flaechig_epsg25832_shp.zip  
Stand: 01.03.2024 12:00 Uhr  
Lizenz: Creative Commons Namensnennung 4.0 International (CC BY 4.0).
Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de.

### Ramsar-Gebiete

Datensatz: Ramsar-Gebiete, EPSG:25832, Shapefile  
Link: https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/ramsar_epsg25832_shp.zip  
Stand: abhängig vom Downloadzeitpunkt  
Lizenz: Creative Commons Namensnennung 4.0 International (CC BY 4.0).
Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de.

### Output Schutzgebiete

Output:

- separate GeoPackages für:
  - `naturschutz_allgemein_hart`
  - `naturschutz_allgemein_weich`
  - `naturschutz_wind`

Datei:

- `data/processed/schutzgebiete/<gemeinde>_naturschutz_allgemein_hart.gpkg`
- `data/processed/schutzgebiete/<gemeinde>_naturschutz_allgemein_weich.gpkg`
- `data/processed/schutzgebiete/<gemeinde>_naturschutz_wind.gpkg`

Hinweis:

- Jede Datei enthält die einzeln zugeschnittenen Ursprungslayer.
- Zusätzlich wird pro Datei ein zusammengeführter Layer geschrieben:
  - `naturschutz_allgemein_hart_merged`
  - `naturschutz_allgemein_weich_merged`
  - `naturschutz_wind_merged`
- Im harten allgemeinen Schutzgebiets-Output werden zusätzlich die geclippten
  Punktlayer `naturdenkmale_punkte` und
  `geschuetzte_landschaftsbestandteile_punkte` mit ausgegeben.
- Diese Punktlayer sind aktuell Hinweislayer und werden noch nicht in
  `naturschutz_allgemein_hart_merged` übernommen.

## Wind

### Natura 2000 FFH-Gebiete

Datensatz: Fauna-Flora-Habitat-Gebiete, EPSG:25832, Shapefile  
Link: https://www.lfu.bayern.de/gdi/dls/daten/natura2000/ffh_epsg25832_shp.zip  
Stand: 22.04.2024 12:00 Uhr  
Lizenz: Creative Commons Namensnennung 4.0 International (CC BY 4.0).
Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de.

### Natura 2000 Vogelschutzgebiete

Datensatz: Vogelschutzgebiete, EPSG:25832, Shapefile  
Link: https://www.lfu.bayern.de/gdi/dls/daten/natura2000/vogelschutz_epsg25832_shp.zip  
Stand: 22.04.2024 12:00 Uhr  
Lizenz: Creative Commons Namensnennung 4.0 International (CC BY 4.0).
Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de.

### Wiesenbrüter- und Feldvogelkulissen 2024

Datensatz: Wiesenbrüterkulisse und Feldvogelkulissen 2024  
Link: https://www.lfu.bayern.de/natur/artenhilfsprogramme_voegel/wiesenbrueter/vogelkulissen_2024/doc/vogelkulissen24.zip  
Stand: nicht dokumentiert  
Lizenz: nicht dokumentiert

### Wind-Vorranggebiete

Datensatz: Vorranggebiete für Windenergienutzung  
Link: https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung?service=WFS&request=GetCapabilities  
Stand: abhängig vom Abrufzeitpunkt des WFS  
Lizenz: laut WFS Regionalplanung Bayern / Datenbereitstellung des Freistaats
Bayern prüfen und in der Arbeit angeben.

Technischer Layername:

- `WFS_Regionalplanung:Vorranggebiet_Windenergienutzung`

### Wind-Vorbehaltsgebiete

Datensatz: Vorbehaltsgebiete für Windenergienutzung  
Link: https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung?service=WFS&request=GetCapabilities  
Stand: abhängig vom Abrufzeitpunkt des WFS  
Lizenz: laut WFS Regionalplanung Bayern / Datenbereitstellung des Freistaats
Bayern prüfen und in der Arbeit angeben.

Technischer Layername:

- `WFS_Regionalplanung:Vorbehaltsgebiet_Windenergienutzung`

### Output Wind

Output:

- `wind_vorranggebiete_<gemeinde>`
- `wind_vorbehaltsgebiete_<gemeinde>`
- `wind_spezifisch`

Datei:

- `data/processed/wind/<gemeinde>_wind_layers.gpkg`

## Solar

### OSM-Verkehrsdaten für Solar

Datensatz: OpenStreetMap Verkehrsachsen über Overpass API  
Link: https://overpass-api.de/api/interpreter  
Stand: dynamisch, abhängig vom Abrufzeitpunkt  
Lizenz: Open Data Commons Open Database License 1.0 (ODbL). Quelle:
OpenStreetMap contributors.

### Energie-Atlas Bayern: Planungsgrundlagen Solar

Datensatz: Planungsgrundlagen Solar - WMS  
Link: https://www.lfu.bayern.de/gdi/wms/energieatlas/planungsgrundlagen_solar  
Stand: Webdienst, abhängig vom aktuellen Dienststand  
Lizenz: Quelle und Lizenzhinweise des Bayerischen Landesamts für Umwelt prüfen
und in der Arbeit angeben.

Relevante Layer:

- `PV-Förderkulisse 500 m Randstreifen (EEG)`
- `PV-Privilegierung 200 m Randstreifen (BauGB)`
- `PV-Freiflächenkulisse - Zoomstufe 1`
- `PV-Freiflächenkulisse - Zoomstufe 2`

### Output Solar

Output:

- `pv_förderkulisse_500m_<gemeinde>`
- `pv_privilegierung_200m_<gemeinde>`

Datei:

- `data/processed/solar/<gemeinde>_solar_layers.gpkg`

## OSM-Netzdaten als gemeinsamer Eingangsdatenblock

Datensatz: OpenStreetMap Straßen- und optional Schienenachsen über Overpass API  
Link: https://overpass-api.de/api/interpreter  
Stand: dynamisch, abhängig vom Abrufzeitpunkt  
Lizenz: Open Data Commons Open Database License 1.0 (ODbL). Quelle:
OpenStreetMap contributors.

Verwendetes Skript:

- `scripts/1_prepare_data/5_download_osm_network_data.py`

Hinweis:

- Das Skript arbeitet mit `--technology wind`, `--technology solar` oder
  `--technology wasser`.
- Es lädt OSM-Daten nicht direkt nur für die Gemeinde, sondern mit einem
  Analysekontext von aktuell `1000 m`.
- Für Wind und Wasser werden allgemeine Straßen- und Wegeklassen geladen.
- Für Solar werden zusätzlich Schienenwege geladen; die eigentliche juristische
  200-m- und 500-m-Logik nutzt später vor allem Autobahnen und Schienen.

Typische Output-Dateien:

- `data/processed/osm_highways/<gemeinde>_osm_highways.gpkg`
- `data/processed/osm_transport/<gemeinde>_osm_transport.gpkg`

## Wasser

Noch keine endgültigen Datensätze festgelegt.

## Frühere Datensätze und Recherche

Die folgenden Datensätze wurden in früheren Versionen des Projekts recherchiert
oder testweise verwendet. Sie bleiben hier bewusst dokumentiert.

### OSM-Straßen allgemein

```text
# TODO: frühere Dokumentation, jetzt durch scripts/1_prepare_data/5_download_osm_network_data.py ersetzt
```

Datensatz: OSM-Straßen über Overpass API  
Link: https://overpass-api.de/api/interpreter  
Stand: dynamisch, abhängig vom Abrufzeitpunkt  
Lizenz: Open Data Commons Open Database License 1.0 (ODbL). Quelle:
OpenStreetMap contributors.
