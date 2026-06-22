# Datensatzinformationen

Diese Datei dient als Quellen- und Lizenzübersicht für die im Projekt
verwendeten Datensätze. 

## 1. Allgemeine Datengrundlagen

### 1.1 Amtliche Basisdaten Bayern

Anbieter: Bayerische Vermessungsverwaltung 
Format: ZIP mit Shapefiles bzw. GeoPackage, überwiegend EPSG:25832  



Datensatz: | ALKIS Verwaltungsgebiet Bayern 
Informationsseite / Metadaten: https://geodaten.bayern.de/opengeodata/OpenDataDetail.html?pn=verwaltung
Technischer Abruf: https://geodaten.bayern.de/odd/m/4/verwaltung/alkis-verwaltung.zip 
Lizenz / Nutzungsbedingungen: CC BY 4.0, "Bayerische Vermessungsverwaltung – www.geodaten.bayern.de"
Abrufdatum: 01.07.2026 
Aktualisierung: monatlich
Methodische Nutzung:Gemeindegrenze, Bayern-Umriss, Locator Map

Datensatz: | Amtliche tatsächliche Nutzung Bayern
Informationsseite / Metadaten: https://geodaten.bayern.de/opengeodata/OpenDataDetail.html?pn=ln
Technischer Abruf: https://geodaten.bayern.de/odd/m/3/daten/ln/landnutzung.gpkg
Lizenz / Nutzungsbedingungen: CC BY 4.0, "Bayerische Vermessungsverwaltung – www.geodaten.bayern.de"
Abrufdatum: 01.07.2026 
Aktualisierung: jährlich
Methodische Nutzung: Landnutzungsanalyse für Wind und Solar

### 1.2 OpenStreetMap
"Bayerische Vermessungsverwaltung – www.geodaten.bayern.de"
Anbieter: OpenStreetMap contributors  
Format: Overpass-API-Abfrage bzw. XYZ-Kacheldienst  
Lizenz / Nutzungsbedingungen: Open Data Commons Open Database License 1.0

| Datensatz | Informationsseite / Metadaten | Technischer Abruf | Stand / Abrufdatum | Methodische Nutzung |
| --- | --- | --- | --- | --- |
| OpenStreetMap Netzdaten | https://www.openstreetmap.org/copyright | https://overpass-api.de/api/interpreter | dynamischer Datenstand; Abrufdatum: 01.07.2026 | Straßen-, Wege- und Schienennetze als Eingangsdaten |
| OpenStreetMap Hintergrundkarte | https://www.openstreetmap.org/copyright | https://tile.openstreetmap.org/{z}/{x}/{y}.png | dynamischer Datenstand; Abrufdatum: 01.07.2026 | Hintergrundkarte in QGIS, PDF und Übersichtskarte |

Hinweis zur Landnutzung:

- Der amtliche Landnutzungsdatensatz ist sehr groß und wird lokal vorgehalten.
- Der Workflow erzeugt daraus einen gemeindebezogenen Arbeitsdatensatz.
- Die Datei ist methodisch ein Eingangsdatenblock, die erzeugten
  Technologie-Layer werden in der Output-Übersicht dokumentiert.

## 2. Schutzgebiete und Natura 2000

### 2.1 Allgemeine Schutzgebietsdaten
Anbieter: Bayerisches Landesamt für Umwelt (LfU Bayern)  
Format: ZIP mit Shapefiles, überwiegend EPSG:25832  
Informationsseite / Downloadübersicht: https://www.lfu.bayern.de/umweltdaten/geodatendienste/pretty_downloaddienst.htm?dld=schutzgebiete.xml  
Metadaten / Aktualisierung / Nutzungsbedingungen: https://www.lfu.bayern.de/umweltdaten/geodatendienste/index_detail.htm?id=39243719-fb94-4e03-90d3-3ecc2b1a3b16&profil=Download  
Lizenz / Nutzungsbedingungen: Creative Commons Namensnennung 4.0 International (CC BY 4.0); Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de 
Aktualisierung: halbjährlich laut LfU-Metadatenseite; Aktualisierung am 01.05. und 01.12. jährlich, sofern neue Daten vorliegen.  
Stand / Gültigkeitsstand: Mai 2026 laut Begleitdokument „Schutzgebiete_Beschreibung_Sachdaten.pdf“.  
Abrufdatum: 01.07.2026

| Datensatz | Technischer Abruf | Methodische Nutzung |
| --- | --- | --- |
| Naturschutzgebiete | https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/nsg_epsg25832_shp.zip | allgemeine harte Naturschutz-Restriktion |
| Nationalparke | https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/nlp_epsg25832_shp.zip | allgemeine harte Naturschutz-Restriktion |
| Nationale Naturmonumente | https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/nationale_naturmonumente_epsg25832_shp.zip | allgemeine harte Naturschutz-Restriktion |
| Naturdenkmale, flächig | https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/naturdenkmal_flaechig_epsg25832_shp.zip | allgemeine harte Naturschutz-Restriktion |
| Naturdenkmale, punktförmig | https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/naturdenkmal_punktfoermig_epsg25832_shp.zip | Detail- und Attributlayer |
| Geschützte Landschaftsbestandteile, flächig | https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/landschaftsbestandteil_flaechig_epsg25832_shp.zip | allgemeine harte Naturschutz-Restriktion |
| Geschützte Landschaftsbestandteile, punktförmig | https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/landschaftsbestandteil_punktfoermig_epsg25832_shp.zip | Detail- und Attributlayer |
| Ramsar-Gebiete | https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/ramsar_epsg25832_shp.zip | allgemeine harte Naturschutz-Restriktion |
| Landschaftsschutzgebiete | https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/lsg_epsg25832_shp.zip | allgemeine weiche Naturschutzfläche |
| Naturparke | https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/naturparke_epsg25832_shp.zip | allgemeine weiche Naturschutzfläche |
| Biosphärenreservate | https://www.lfu.bayern.de/gdi/dls/daten/schutzgebiete/biosphaerenreservate_epsg25832_shp.zip | allgemeine weiche Naturschutzfläche |

### 2.2 Natura 2000

Anbieter: Bayerisches Landesamt für Umwelt (LfU Bayern)  
Format: ZIP mit Shapefiles, EPSG:25832  
Informationsseite / Downloadübersicht: https://www.lfu.bayern.de/natur/natura_2000/index.htm  
Metadaten / Aktualisierung / Nutzungsbedingungen: https://www.lfu.bayern.de/umweltdaten/geodatendienste/pretty_downloaddienst.htm?dld=natura2000.xml  
Lizenz / Nutzungsbedingungen: Creative Commons Namensnennung 4.0 International (CC BY 4.0); Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de  
Stand / Gültigkeitsstand: Mai 2026 laut Begleitdokument „Schutzgebiete_Beschreibung_Sachdaten.pdf“.  
Abrufdatum: 01.07.2026

| Datensatz | Technischer Abruf | Methodische Nutzung |
| --- | --- | --- |
| Natura 2000 FFH-Gebiete | https://www.lfu.bayern.de/gdi/dls/daten/natura2000/ffh_epsg25832_shp.zip | allgemeine harte Naturschutz-Restriktion |
| Natura 2000 Vogelschutzgebiete | https://www.lfu.bayern.de/gdi/dls/daten/natura2000/vogelschutz_epsg25832_shp.zip | allgemeine harte Naturschutz-Restriktion, zusätzlich windrelevant |

### 2.3 Windspezifische Vogelkulissen

Anbieter: Bayerisches Landesamt für Umwelt (LfU Bayern)  
Format: ZIP mit Shapefiles, überwiegend EPSG:25832  
Informationsseite / Downloadübersicht: https://www.lfu.bayern.de/natur/artenhilfsprogramme_voegel/wiesenbrueter/vogelkulissen_2024/index.htm  
Metadaten / Aktualisierung / Nutzungsbedingungen: https://www.lfu.bayern.de/umweltdaten/geodatendienste/index_detail.htm?id=091d8c46-b539-4dcb-af4e-0329c5abec65&profil=WMS  
Lizenz / Nutzungsbedingungen: Für den zugehörigen LfU-WMS-Dienst ist Creative Commons Namensnennung 4.0 International (CC BY 4.0) mit der Datenquelle „Bayerisches Landesamt für Umwelt, www.lfu.bayern.de“ angegeben. Für das verwendete ZIP-File wurde keine davon abweichende Lizenzangabe gefunden.  
Stand / Gültigkeitsstand: 2024 laut Datensatzbezeichnung „Wiesenbrüter- und Feldvogelkulissen 2024“.  
Abrufdatum: 01.07.2026

| Datensatz | Technischer Abruf | Methodische Nutzung |
| --- | --- | --- |
| Wiesenbrüter- und Feldvogelkulissen 2024 | https://www.lfu.bayern.de/natur/artenhilfsprogramme_voegel/wiesenbrueter/vogelkulissen_2024/doc/vogelkulissen24.zip | windspezifische Restriktions- und Konfliktflächen |

## 3. Windbezogene Datengrundlagen

Anbieter: Regionalplanung Bayern / Bayerisches Staatsministerium für Wirtschaft, Landesentwicklung und Energie  
Format: WFS-Dienst mit Vektordaten  
URL des Dienstes: https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung  
Technischer Abruf / GetCapabilities: https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung?service=WFS&request=GetCapabilities  
Informationsseite / Metadaten: dokumentiert über den GetCapabilities-Aufruf des WFS-Dienstes  
Lizenz / Hinweis: Creative Commons Namensnennung 4.0 (CC BY 4.0) laut GetCapabilities des WFS-Dienstes. Die Namensnennung hat mit folgender Datenquelle zu erfolgen: „Bayerisches Staatsministerium für Wirtschaft, Landesentwicklung und Energie - www.stmwi.bayern.de“. Der jeweilige Stand der Datenausspielung ist anzugeben. Zusätzlich gilt die Nutzungseinschränkung, dass Regionalplandaten nur mit den im jeweiligen Regionalplan entsprechenden Signaturen verwendet werden dürfen. Der Dienst ersetzt nicht die allein verbindliche Originalfassung der Regionalpläne.  
Aktualisierung: dynamischer WFS-Datenstand; maßgeblich ist der Stand zum Zeitpunkt des Abrufs.  
Abrufdatum: 01.07.2026  

| Datensatz | Technischer WFS-Layername | Methodische Nutzung |
| --- | --- | --- |
| Vorranggebiete Windenergienutzung | `WFS_Regionalplanung:Vorranggebiet_Windenergienutzung` | offizieller regionalplanerischer Wind-Hauptlayer |
| Vorbehaltsgebiete Windenergienutzung | `WFS_Regionalplanung:Vorbehaltsgebiet_Windenergienutzung` | offizieller regionalplanerischer Wind-Hinweislayer |

Technische WFS-Layernamen:

- `WFS_Regionalplanung:Vorranggebiet_Windenergienutzung`
- `WFS_Regionalplanung:Vorbehaltsgebiet_Windenergienutzung`

## 4. Solarbezogene Datengrundlagen

Anbieter: Energie-Atlas Bayern / Bayerisches Landesamt für Umwelt (LfU Bayern)  
Format: WMS-Dienst, Bild-/Rasterdarstellung  
URL des Dienstes: https://www.lfu.bayern.de/gdi/wms/energieatlas/planungsgrundlagen_solar  
Technischer Abruf / GetCapabilities: https://www.lfu.bayern.de/gdi/wms/energieatlas/planungsgrundlagen_solar?service=WMS&request=GetCapabilities  
Aktualisierung: dynamischer WMS-Datenstand; maßgeblich ist der Stand zum Zeitpunkt des Abrufs.  
Stand / Abrufdatum: 01.07.2026  
Lizenz / Hinweis: Creative Commons Namensnennung 4.0 International (CC BY 4.0) laut WMS-Dienst. Die Namensnennung hat in folgender Weise zu erfolgen: „Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de“.  

| Datensatz | Methodische Nutzung |
| --- | --- |
| PV-Freiflächenkulisse Bayern | amtliche WMS-Referenz zur Einordnung potenziell relevanter Freiflächen-Photovoltaik-Flächen |

Verwendete Solar-WMS-Layer:

- `PV-Freiflächenkulisse - Zoomstufe 1`
- `PV-Freiflächenkulisse - Zoomstufe 2`

Methodischer Hinweis:

- Die Solar-WMS-Referenz wird als georeferenziertes Raster auf die Bounding Box
  der Gemeinde geladen.
- Ein exakter Zuschnitt an der Gemeindegrenze erfolgt nicht, weil der WMS als
  Bild-/Rasterreferenz und nicht als editierbarer Vektorlayer verarbeitet wird.
- Die 200-m- und 500-m-Korridore sind eigene räumliche Näherungen und keine
  rechtsverbindliche Genehmigungsprüfung.

## 5. Wasserbezogene Datengrundlagen

### 5.1 Wasserschutzgebiete

Anbieter: Bayerisches Landesamt für Umwelt (LfU Bayern)  
Format: ZIP mit Shapefiles, überwiegend EPSG:25832  
Informationsseite / Metadaten: https://www.lfu.bayern.de/umweltdaten/geodatendienste/pretty_downloaddienst.htm?dld=wsg.xml
Lizenz / Nutzungsbedingungen: LfU Bayern; die Nutzungsbedingungen der
jeweiligen Download- oder Metadatenseite sind zu beachten.  
Publiziert am: 19.03.2009
Aktualisierungsintervall: wöchentlich
Abrufdatum: 01.07.2026


| Datensatz | Technischer Abruf | Methodische Nutzung |
| --- | --- | --- |
| Trinkwasserschutzgebiete | https://www.lfu.bayern.de/gdi/dls/daten/wsg/twsg_epsg25832_shp.zip | harter wasserbezogener Schutz- und Restriktionslayer |
| Heilquellenschutzgebiete | https://www.lfu.bayern.de/gdi/dls/daten/wsg/hqsg_epsg25832_shp.zip | harter wasserbezogener Schutz- und Restriktionslayer |

### 5.2 Wasserkraft und wasserbezogene Potenziale

Anbieter: Energie-Atlas Bayern / Bayerisches Landesamt für Umwelt (LfU Bayern)  
Format: WMS-Dienst, Bild-/Rasterdarstellung  
URL des Dienstes: https://www.lfu.bayern.de/gdi/wms/energieatlas/wasserkraftanlagen  
Technischer Abruf / GetCapabilities: https://www.lfu.bayern.de/gdi/wms/energieatlas/wasserkraftanlagen?service=WMS&request=GetCapabilities  
Lizenz / Hinweis: Creative Commons Namensnennung 4.0 International (CC BY 4.0) laut WMS-Dienst. Die Namensnennung hat in folgender Weise zu erfolgen: „Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de“.  
Aktualisierung: dynamischer WMS-Datenstand; maßgeblich ist der Stand zum Zeitpunkt des Abrufs.  
Abrufdatum: 01.07.2026  

| Datensatz | Technischer WMS-Layername | Methodische Nutzung |
| --- | --- | --- |
| Wasserkraftanlagen | `wasserkraftanlagen_zv04b14` | Bestand bestehender Wasserkraftanlagen |
| Neubaupotenzial an Querbauwerken | `neubaupotenzial_querbauwerke` | wasserbezogener Potenziallayer |
| Modernisierung und Nachrüstung | `modernisierung_nachruestung` | wasserbezogener Potenziallayer |

### 5.3 Überschwemmungsgebiete und Hochwassergefahren

Anbieter: Bayerisches Landesamt für Umwelt (LfU Bayern)  
Format: WMS-Dienst, Bild-/Rasterdarstellung  
URL des Dienstes: https://www.lfu.bayern.de/gdi/wms/wasser/ueberschwemmungsgebiete  
Technischer Abruf / GetCapabilities: https://www.lfu.bayern.de/gdi/wms/wasser/ueberschwemmungsgebiete?service=WMS&request=GetCapabilities  
Lizenz / Hinweis: Creative Commons Namensnennung 4.0 International (CC BY 4.0) laut WMS-Dienst. Die Namensnennung hat in folgender Weise zu erfolgen: „Datenquelle: Bayerisches Landesamt für Umwelt, www.lfu.bayern.de“.  
Aktualisierung: dynamischer WMS-Datenstand; maßgeblich ist der Stand zum Zeitpunkt des Abrufs.  
Stand / Abrufdatum: 01.07.2026  

| Datensatz | Technischer WMS-Layername | Methodische Nutzung |
| --- | --- | --- |
| Festgesetzte Überschwemmungsgebiete | `festsetzung` | harte wasserrechtliche Restriktion |
| Vorläufig gesicherte Überschwemmungsgebiete | `sicherung` | harte wasserrechtliche Restriktion |
| Hochwassergefahrenflächen HQ100 | `hwgf_hq100` | weicher Hochwasser-Konfliktbereich |
| Hochwassergefahrenflächen HQextrem | `hwgf_hqextrem` | weicher Hochwasser-Risikokontext |

Methodischer Hinweis:

- Wasserschutzgebiete werden als Vektordaten verarbeitet und auf die Gemeinde
  zugeschnitten.
- Wasserkraft- und Hochwasserinformationen werden als WMS-Rasterreferenzen
  eingebunden.
- Die WMS-Raster werden auf die Bounding Box der Gemeinde geladen und nicht wie
  Vektordaten exakt an der Gemeindegrenze ausgeschnitten.

## 6. Hinweise zu Begleitdateien und Datenständen

Bei mehreren heruntergeladenen ZIP-Archiven liegen zusätzliche Begleitdateien,
Sachdatenbeschreibungen oder Metadaten im Downloadpaket. Diese Dateien werden
in dieser Übersicht nicht als eigene Datensätze geführt, dienen aber zur
Prüfung von Datenstand, Attributbeschreibung und Nutzungsbedingungen.

Bei WMS- und WFS-Diensten handelt es sich um dynamische Dienste. Deshalb wird
für diese Datensätze der Datenstand über den Abrufzeitpunkt sowie, soweit
verfügbar, über die Angaben im GetCapabilities-Dokument oder auf der
Metadatenseite dokumentiert.

