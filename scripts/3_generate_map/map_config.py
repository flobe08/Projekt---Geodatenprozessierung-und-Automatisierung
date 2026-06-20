"""Technology-specific map text and legend configuration."""

# -----------------------------------------------------------------------------
# Shared static PDF layout template
# -----------------------------------------------------------------------------
LAYOUT_TEMPLATE = {
    # Main map frame.
    "map_x": 6,
    "map_y": 18,
    "map_width": 216,
    "map_height": 175,
    "map_extent_scale": "auto",
    "main_scale_step": 500,  # Scale in 500 steps for stable map scales.
    # Centered map title.
    "title_y": 7,
    "title_font_size": 14,
    "title_width": 216,
    "title_height": 8,
    # Data source footer below the map.
    "footer_y": 194.5,
    "footer_height": 12,
    "footer_line_height": 3.4,
    # Right information panel with description, legend, scale and metadata.
    "panel_x": 228,
    "panel_y": 18,
    "panel_width": 63,
    # Description text at the top of the right panel.
    "description_y": 18,
    "description_font_size": 8,
    "description_height": 34,
    # Legend block in the right panel.
    "legend_y": 72,
    "legend_width": 63,
    "legend_height": 95,
    "legend_title_offset": 2,
    "legend_section_offset": 9,
    "legend_section_font_size": 9,
    "legend_row_start_offset": 16,
    "legend_row_gap": 8,
    # Grid legend row.
    "grid_title_gap_after_last_row": 10,
    "grid_row_offset": 5,
    # North arrow. It can either live in the panel or inside the main map.
    "north_arrow_y": 147,
    "north_arrow_width": 18,
    "north_arrow_height": 18,
    "north_arrow_inside_map": True,
    "north_arrow_map_margin": 3,
    # Optional overview map / locator map.
    "overview_map_enabled": True,
    "overview_map_x": 6,
    "overview_map_y": 18,
    "overview_map_width": 72,
    "overview_map_height": 58,
    # Scale bar and metadata.
    "scale_bar_y": 176,
    "scale_text_y": 190,
    "author_y": 204,
    "date_y": 208,
    "metadata_font_size": 7,
    "footer_font_size": 6,
    "debug_frames": False,
}

TECHNOLOGY_CONFIG = {
    "wind": {
        "title": "Windenergieflächen und Restriktionen in {municipality}",
        "description": (
            "Die Karte zeigt offizielle Vorrang- und\n"
            "Vorbehaltsgebiete für Windenergienutzung\n"
            "innerhalb der Gemeinde {municipality}.\n\n"
            "Zusätzlich werden harte und wind-\n"
            "spezifische Naturschutz-Restriktionen,\n"
            "weiche Konfliktflächen sowie Nutzungs-\n"
            "ausschlüsse aus Landnutzung und Straßen\n"
            "dargestellt.\n\n"
            "Die Layer wurden aus offiziellen\n"
            "Planungs-, Schutzgebiets- und\n"
            "Landnutzungsdaten sowie OSM-\n"
            "Straßendaten abgeleitet und mit\n"
            "der amtlichen Gemeindegrenze\n"
            "verschnitten."
        ),
        "sources": (
            "Gemeindegrenze: ALKIS Bayern, Bayerische Vermessungsverwaltung, "
            "https://geodaten.bayern.de. "
            "Naturschutz: LfU Bayern, Schutzgebiete und Natura-2000-Daten.\n"
            "OSM: OpenStreetMap über Overpass."
            "Nutzungsdaten: Amtliche tatsächliche Nutzung Bayern. "
            "Windflächen: Regionalplanung Bayern, WFS Regionalplanung.\n"
            "WFS: https://risby.bayern.de/RisGate/servlet/WFSRegionalplanung.\n"
            "Hintergrundkarte: OpenStreetMap.\n"
            "Koordinatensystem: EPSG:25832 / ETRS89 UTM Zone 32N"
        ),
        "legend_section": "Standortinformationen",
        "legend_items": [
            {
                "label": "Gemeindegrenze",
                "color": "255,255,255,255",
                "outline_color": "0,0,0,255",
            },
            {
                "label": "Vorranggebiete Wind",
                "color": "90,118,145,255",
                "outline_color": "90,118,145,255",
            },
            {
                "label": "Vorbehaltsgebiete Wind",
                "color": "45,150,155,255",
                "outline_color": "24,110,115,255",
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
                "label": "Weiche Naturschutzflächen",
                "color": "245,210,80,90",
                "outline_color": "196,150,35,180",
            },
            {
                "label": "Straßen und Wege",
                "color": "110,110,110,255",
                "outline_color": "110,110,110,255",
                "symbol": "line",
            },
            {
                "label": "Nutzungsausschluss",
                "color": "125,72,165,160",
                "outline_color": "92,47,128,255",
            },
        ],
        "grid_distance_label": "Abstand: 500 m",
        "scale_units_per_segment": 1000,
        "layout_overrides": {
            "debug_frames": False,
        },
    },
    "solar": {
        "title": (
            "Potenzial- und Planungskulissen für Freiflächen-Photovoltaik "
            "in {municipality}"
        ),
        "description": (
            "Die Karte zeigt solare Planungs- und\n"
            "Potenzialkulissen für {municipality}.\n\n"
            "Dargestellt werden die PV-Freiflächenkulisse\n"
            "des Energie-Atlas Bayern, ein eigener\n"
            "500-m-Korridor als angenäherte\n"
            "EEG-Förderkulisse sowie ein eigener\n"
            "200-m-Korridor als angenäherte\n"
            "BauGB-Privilegierung entlang relevanter\n"
            "Verkehrsachsen.\n\n"
            "Ergänzend werden harte und weiche\n"
            "Naturschutzflächen als Konflikträume\n"
            "gezeigt.\n\n"
            "Die Ergebnisse sind räumliche\n"
            "Näherungen und keine abschließende\n"
            "Genehmigungsprüfung."
        ),
        "sources": (
            "Gemeindegrenze: ALKIS Bayern, Bayerische Vermessungsverwaltung, "
            "https://geodaten.bayern.de. "
            "Naturschutz: LfU Bayern, Schutzgebiete und Natura-2000-Daten. "
            "OSM: OpenStreetMap über Overpass. "
            "Nutzungsdaten: Amtliche tatsächliche Nutzung Bayern. "
            "Solarflächen: Energie-Atlas Bayern, Planungsgrundlagen Solar. "
            "WMS: https://www.lfu.bayern.de/gdi/wms/energieatlas/planungsgrundlagen_solar. "
            "Solar-Korridore: eigene Näherung nach EEG 2023 § 37 Abs. 1 Nr. 2c "
            "und BauGB § 35 Abs. 1 Nr. 8b.\n"
            "Hintergrundkarte: OpenStreetMap.\n"
            "Koordinatensystem: EPSG:25832 / ETRS89 UTM Zone 32N"
        ),
        "legend_section": "Analyse und Referenz",
        "legend_items": [
            {
                "label": "Gemeindegrenze",
                "color": "255,255,255,255",
                "outline_color": "0,0,0,255",
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
                "label": "Harte Naturschutz-Restriktionen",
                "color": "255,0,0,255",
                "outline_color": "255,0,0,255",
                "symbol": "stripe_box",
            },
            {
                "label": "Weiche Naturschutzflächen",
                "color": "245,210,80,90",
                "outline_color": "196,150,35,180",
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
            "debug_frames": False,
            "title_font_size": 12,
            "legend_y": 80,
            "legend_height": 88,
            "legend_section_font_size": 8,
            "legend_row_gap": 7,
        },
    },
    "wasser": {
        "title": "Potenzielle Standorte für Wasserkraftanlagen in {municipality}",
        "description": (
            "Die Wasserkarte ist aktuell als\n"
            "Platzhalter für den späteren Workflow\n"
            "vorbereitet. Wasserbezogene Daten,\n"
            "Schutzflächen und Konfliktflächen\n"
            "werden in einem nächsten Schritt ergänzt."
        ),
        "sources": (
            "Gemeindegrenze: ALKIS Bayern, Bayerische Vermessungsverwaltung, "
            "https://geodaten.bayern.de.\n"
            "Wasserdaten: TODO, noch nicht im aktiven Workflow umgesetzt.\n"
            "Hintergrundkarte: OpenStreetMap. "
            "Koordinatensystem: EPSG:25832 / ETRS89 UTM Zone 32N"
        ),
        "legend_section": "Standortinformationen",
        "legend_items": [
            {
                "label": "Gemeindegrenze",
                "color": "255,255,255,255",
                "outline_color": "0,0,0,255",
            },
        ],
        "grid_distance_label": "Abstand: 500 m",
        "scale_units_per_segment": 1000,
        "layout_overrides": {
            "debug_frames": True,
        },
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
