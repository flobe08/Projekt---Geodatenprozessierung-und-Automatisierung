# Installation

Die Pipeline wird unter WSL/Ubuntu ausgeführt. Für die Kartenerstellung wird QGIS mit Python-Unterstützung benötigt.

## Voraussetzungen

Benötigt werden:

- WSL mit Ubuntu
- Python 3
- Python virtual environment
- QGIS
- Python-QGIS
- Git

## 1. Systempakete installieren

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip qgis python3-qgis
```

## 2. Projektordner öffnen

```bash
cd "/mnt/c/Users/elena/Desktop/Uni/Semester 6/Geodaten/Projekt---Geodatenprozessierung-und-Automatisierung"
```

## 3. Virtuelle Python-Umgebung erstellen

```bash
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
pip install -r requirements.txt
deactivate
```
Die virtuelle Umgebung wird für die allgemeine Datenverarbeitung verwendet. Die QGIS-basierten Schritte werden mit dem systemweiten Python ausgeführt, da nur dort das Modul `qgis` verfügbar ist.

## 4. Installation prüfen

```bash
python3 -c "from qgis.core import QgsApplication; print('qgis ok')"
```

Wenn `qgis` ok ausgegeben wird, ist die QGIS-Python-Umgebung korrekt installiert.