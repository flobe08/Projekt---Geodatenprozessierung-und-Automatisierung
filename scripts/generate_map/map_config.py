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
    # A4 landscape page size: 297 x 210 mm.
    # The layout is intentionally static. If wind, solar or hydropower need
    # different spacing later, change only the technology-specific overrides.
    "map_x": 12,  # Left position of the main map in millimeters.
    "map_y": 18,  # Top position of the main map in millimeters.
    "map_width": 210,  # Width of the main map frame.
    "map_height": 175,  # Height of the main map frame.
    "map_extent_scale": "auto",  # Map zoom padding; use a number for manual zoom.
    "title_y": 7,  # Top position of the map title.
    "title_font_size": 14,  # Font size of the map title.
    "title_width": 210,  # Width used to center the map title.
    "title_height": 8,  # Height of the title text box.
    "footer_y": 194.5,  # Top position of the data source footer.
    "footer_height": 12,  # Height of the data source footer.
    "panel_x": 232,  # Left position of the right information panel.
    "panel_y": 18,  # Top reference position of the right panel.
    "panel_width": 58,  # Width of legend, description and scale components.
    "description_y": 18,  # Top position of the description text.
    "description_font_size": 8,  # Font size of the description text.
    "description_height": 34,  # Height of the description text box.
    "description_wrap_width": 34,  # Character width used for description wrapping.
    "legend_y": 72,  # Top position of the legend frame.
    "legend_width": 58,  # Width of the legend frame.
    "legend_height": 52,  # Height of the legend frame.
    "legend_title_y": 75,  # Top position of the "Legende" heading.
    "legend_section_y": 82,  # Top position of the legend section heading.
    "legend_row_start_y": 88,  # Top position of the first legend item row.
    "legend_row_gap": 8,  # Vertical distance between legend item rows.
    "grid_title_y": 112,  # Top position of the "Gitternetz" heading.
    "grid_row_y": 117,  # Top position of the grid legend row.
    "north_arrow_y": 140,  # Top position of the north arrow.
    "north_arrow_width": 15,  # Width of the north arrow SVG.
    "north_arrow_height": 15,  # Height of the north arrow SVG.
    "scale_bar_y": 160,  # Top position of the scale bar box.
    "scale_text_y": 176,  # Top position of the scale denominator text.
    "author_y": 185,  # Top position of the author line.
    "date_y": 189,  # Top position of the date line.
    "metadata_font_size": 7,  # Font size for author and date.
    "footer_font_size": 6,  # Font size for data sources and CRS.
    "footer_wrap_width": 1000,  # Character width used for footer wrapping.
}


TECHNOLOGY_CONFIG = {
    # -------------------------------------------------------------------------
    # Wind map configuration
    # -------------------------------------------------------------------------
    "wind": {
        "title": "Potenzielle Standorte für Windkraftanlagen in {municipality}",
        "description": PLACEHOLDER_TEXT,
        "sources": PLACEHOLDER_TEXT,
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
                "color": "232,177,35,255",
                "outline_color": "232,177,35,255",
            },
        ],
        "grid_distance_label": "Abstand: 500 m",
        "scale_units_per_segment": 1000,
        "layout_overrides": {
            "legend_height": 60,
            "grid_title_y": 120,
            "grid_row_y": 125,
            "north_arrow_y": 147,
            "scale_bar_y": 165,
            "scale_text_y": 180,
            "author_y": 188,
            "date_y": 192,
        },
    },

    # -------------------------------------------------------------------------
    # Solar map configuration
    # -------------------------------------------------------------------------
    "solar": {
        "title": "Potenzieller Standort für einen Photovoltaikpark in {municipality}",
        "description": PLACEHOLDER_TEXT,
        "sources": PLACEHOLDER_TEXT,
        "legend_section": "Standortinformationen",
        "legend_items": [
            {
                "label": "Gemeindegrenze",
                "color": "255,255,255,255",
                "outline_color": "255,0,0,255",
            },
            {
                "label": "Geeignete Flaechen",
                "color": "31,60,160,255",
                "outline_color": "31,60,160,255",
            },
            {
                "label": "Gewaehlter Standort",
                "color": "255,255,255,255",
                "outline_color": "255,0,0,255",
            },
        ],
        "grid_distance_label": "Abstand: 500 m",
        "scale_units_per_segment": 1000,
        "layout_overrides": {
            "legend_height": 52,
            "grid_title_y": 112,
            "grid_row_y": 117,
        },
    },

    # -------------------------------------------------------------------------
    # Hydropower map configuration
    # -------------------------------------------------------------------------
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
            {
                "label": "Nutzungsdaten",
                "color": "90,118,145,255",
                "outline_color": "90,118,145,255",
            },
            {
                "label": "OSM-Straßendaten",
                "color": "255,170,0,255",
                "outline_color": "255,170,0,255",
                "symbol": "line",
            },
        ],
        "grid_distance_label": "Abstand: 500 m",
        "scale_units_per_segment": 1000,
        "layout_overrides": {
            "legend_height": 52,
            "grid_title_y": 112,
            "grid_row_y": 117,
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
