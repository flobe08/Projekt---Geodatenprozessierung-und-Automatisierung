0. Conda/Miniconda installieren, falls noch nicht vorhanden
1. Umgebung erstellen:
   .\setup.ps1
2. Umgebung aktivieren:
   conda activate geodata-pipeline
3. Pipeline laufen lassen:
   python pipeline.py --municipality Drachselsried --technology wind

Notizen:
- Script 0: Daten downloaden
  - Verwaltungsgebiet Bayern
  - OSM Bayern
  - für wind: FFH und Vogelschutzgebiete
- Script 1: Gemeindegrenze aus VerwaltungsEinheit.shp extrahieren
- Script 2: OSM-Datensatz mit der vorher erstellten Gemeindegrenze schneiden
- zipfile muss nicht installiert werden, ist in Python enthalten
- osmium-tool kommt über environment.yml / Conda
