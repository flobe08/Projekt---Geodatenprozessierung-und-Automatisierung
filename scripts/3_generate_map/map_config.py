"""Technology-specific map text and legend configuration."""


PLACEHOLDER_TEXT = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed eiusmod "
    "tempor incidunt ut labore et dolore magna aliqua. Ut enim ad minim "
    "veniam, quis nostrud exercitation ullamco laboris nisi ut aliquid ex ea "
    "commodi consequat. Quis aute iure reprehenderit in voluptate velit esse "
    "cillum dolore eu fugiat nulla pariatur. Excepteur sint obcaecat "
    "cupiditat non proident, sunt in culpa qui officia deserunt mollit anim "
    "id est laborum."
)


# -----------------------------------------------------------------------------
# Shared static PDF layout template
# -----------------------------------------------------------------------------
LAYOUT_TEMPLATE = {
    "map_x": 12,
    "map_y": 18,
    "map_width": 210,
    "map_height": 175,
    "map_extent_scale": "auto",
    "title_y": 7,
    "title_font_size": 14,
    "title_width": 210,
    "title_height": 8,
    "footer_y": 194.5,
    "footer_height": 12,
    "panel_x": 232,
    "panel_y": 18,
    "panel_width": 58,
    "description_y": 18,
    "description_font_size": 8,
    "description_height": 34,
    "description_wrap_width": 34,
    "legend_y": 72,
    "legend_width": 58,
    "legend_height": 60,
    "legend_title_y": 75,
    "legend_section_y": 83,
    "legend_row_start_y": 89,
    "legend_row_gap": 8,
    "grid_title_y": 120,
    "grid_row_y": 125,
    "north_arrow_y": 147,
    "north_arrow_width": 15,
    "north_arrow_height": 15,
    "scale_bar_y": 165,
    "scale_text_y": 181,
    "author_y": 188,
    "date_y": 192,
    "metadata_font_size": 7,
    "footer_font_size": 6,
    "footer_wrap_width": 350,
}


TECHNOLOGY_CONFIG = {
    "wind": {
        "title": "Potenzielle Standorte für Windkraftanlagen in {municipality}",
        "description": (
            "Die Karte zeigt offizielle Vorrang- und Vorbehaltsgebiete für "
            "Windenergienutzung innerhalb der Gemeinde {municipality}. "
            "Zusätzlich werden harte Naturschutz-Restriktionen und weiche "
            "Konfliktflächen zusammengefasst dargestellt. Die Flächen stammen "
            "aus offiziellen Planungs- und Schutzgebietsdaten und wurden mit "
            "der amtlichen Gemeindegrenze verschnitten."
        ),
        "sources": (
            "Windflächen: Regionalplanung Bayern, WFS Regionalplanung "
            "(Vorranggebiet und Vorbehaltsgebiet Windenergienutzung), "
            "https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung. "
            "Naturschutz: Bayerisches Landesamt für Umwelt, Schutzgebiete und "
            "Natura-2000-Daten. Gemeindegrenze: ALKIS Bayern, Bayerische "
            "Vermessungsverwaltung, https://geodaten.bayern.de. "
            "Hintergrundkarte: OpenStreetMap."
        ),
        "legend_section": "Standortinformationen",
        "legend_items": [
            {
                "label": "Gemeindegrenze",
                "color": "255,255,255,255",
                "outline_color": "255,0,0,255",
            },
            {
                "label": "Vorranggebiete Wind",
                "color": "90,118,145,255",
                "outline_color": "90,118,145,255",
            },
            {
                "label": "Vorbehaltsgebiete Wind",
                "color": "142,108,185,255",
                "outline_color": "94,64,140,255",
            },
            {
                "label": "Harte Naturschutz-Restriktionen",
                "color": "255,0,0,255",
                "outline_color": "255,0,0,255",
                "symbol": "stripe_box",
            },
            {
                "label": "Windspezifische Restriktionen",
                "color": "232,136,20,255",
                "outline_color": "196,108,0,255",
                "symbol": "stripe_box",
            },
            {
                "label": "Weiche Naturschutz-Konfliktflächen",
                "color": "230,155,52,255",
                "outline_color": "190,120,20,255",
            },
        ],
        "grid_distance_label": "Abstand: 500 m",
        "scale_units_per_segment": 1000,
        "layout_overrides": {
            "legend_height": 84,
            "grid_title_y": 144,
            "grid_row_y": 149,
            "north_arrow_y": 164,
            "scale_bar_y": 182,
            "scale_text_y": 198,
            "author_y": 204,
            "date_y": 208,
        },
    },
    "solar": {
        "title": "Potenzielle Standorte für Freiflächen-Photovoltaik in {municipality}",
        "description": (
            "Die Karte zeigt zwei solarbezogene Randstreifen entlang von "
            "Autobahnen und Schienenwegen in {municipality}. Der 500-m-Bereich "
            "bildet die EEG-Förderkulisse näherungsweise ab, der 200-m-Bereich "
            "eine strengere BauGB-orientierte Privilegierung entlang von "
            "Autobahnen und passend gefilterten Schienenwegen. Zusätzlich wird "
            "die amtliche Freiflächenkulisse des Energie-Atlas Bayern als "
            "visuelle Referenz eingeblendet. Die Analyse-Layer sind räumliche "
            "Näherungen und keine abschließende Genehmigungsprüfung."
        ),
        "sources": (
            "Gemeindegrenze: ALKIS Bayern. OSM-Verkehrsachsen: OpenStreetMap "
            "über Overpass. Förderkulisse: angenähert nach EEG 2023 "
            "Paragraf 37 Abs. 1 Nr. 2 Buchstabe c. Privilegierung: "
            "angenähert nach BauGB Paragraf 35 Abs. 1 Nr. 8 Buchstabe b. "
            "Amtliche Referenz: Energie-Atlas Bayern, Planungsgrundlagen Solar "
            "(PV-Freiflächenkulisse Zoomstufe 1 und 2) als WMS."
        ),
        "legend_section": "Analyse und Referenz",
        "legend_items": [
            {
                "label": "Gemeindegrenze",
                "color": "255,255,255,255",
                "outline_color": "255,0,0,255",
            },
            {
                "label": "Freiflächenkulisse geeignet",
                "color": "55,166,53,255",
                "outline_color": "55,166,53,255",
            },
            {
                "label": "Freiflächenkulisse bedingt",
                "color": "247,235,59,255",
                "outline_color": "247,235,59,255",
            },
            {
                "label": "EEG-Förderkulisse 500 m",
                "color": "242,186,33,255",
                "outline_color": "189,136,0,255",
            },
            {
                "label": "BauGB-Privilegierung 200 m",
                "color": "31,60,160,255",
                "outline_color": "18,40,120,255",
            },
            {
                "label": "Autobahnen und Schienenwege",
                "color": "60,60,60,255",
                "outline_color": "60,60,60,255",
                "symbol": "line",
            },
        ],
        "grid_distance_label": "Abstand: 500 m",
        "scale_units_per_segment": 1000,
        "layout_overrides": {
            "legend_height": 76,
            "grid_title_y": 136,
            "grid_row_y": 141,
            "north_arrow_y": 156,
            "scale_bar_y": 174,
            "scale_text_y": 190,
            "author_y": 196,
            "date_y": 200,
        },
    },
    "wasser": {
        "title": "Potenzielle Standorte für Wasserkraftanlagen in {municipality}",
        "description": PLACEHOLDER_TEXT,
        "sources": PLACEHOLDER_TEXT,
        "legend_section": "Standortinformationen",
        "legend_items": [
            {
                "label": "Gemeindegrenze",
                "color": "255,255,255,255",
                "outline_color": "255,0,0,255",
            },
        ],
        "grid_distance_label": "Abstand: 500 m",
        "scale_units_per_segment": 1000,
        "layout_overrides": {},
    },
}


def get_map_config(technology: str) -> dict:
    """Return map configuration for one technology with merged layout settings."""

    config = TECHNOLOGY_CONFIG[technology].copy()
    config["layout"] = get_layout_config(technology)
    return config


def get_layout_config(technology: str) -> dict:
    """Return the shared layout template with optional technology overrides."""

    layout = LAYOUT_TEMPLATE.copy()
    layout.update(TECHNOLOGY_CONFIG[technology].get("layout_overrides", {}))
    return layout
