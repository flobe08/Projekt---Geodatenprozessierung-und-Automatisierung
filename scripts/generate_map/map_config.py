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
    # The layout is intentionally static. If wind_self, solar or hydropower need
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
    "wind_self": {
        "title": "Potenzielle Standorte für Windkraftanlagen in {municipality}",  # PDF title.
        "description": PLACEHOLDER_TEXT,  # Text block in the right panel.
        "sources": PLACEHOLDER_TEXT,  # Data source text in the footer.
        "legend_section": "Standortinformationen",  # Bold legend subsection title.
        "legend_items": [
            {
                "label": "Gemeindegrenze",  # Legend label.
                "color": "255,255,255,255",  # fill color.
                "outline_color": "255,0,0,255",  # outline color.
            },
            {
                "label": "Nutzungsdaten",  # Legend label.
                "color": "90,118,145,255",  # fill color.
                "outline_color": "90,118,145,255",  # outline color.
            },
            {
                "label": "OSM-Straßendaten",  # Legend label.
                "color": "255,170,0,255",  # line color.
                "outline_color": "255,170,0,255",  #  symbol outline color.
                "symbol": "line",  # Use road-like legend symbol instead of box.
            },
        ],
        "grid_distance_label": "Abstand: 500 m",  # Text next to grid symbol.
        "scale_units_per_segment": 1000,  # Scale bar segment length in meters.
        "layout_overrides": {},  # Not needed: LAYOUT_TEMPLATE is currently tuned for wind_self.
    },

    # -------------------------------------------------------------------------
    # Solar map configuration
    # -------------------------------------------------------------------------
    "solar": {
        "title": "Potenzieller Standort für einen Photovoltaikpark in {municipality}",  # PDF title.
        "description": PLACEHOLDER_TEXT,  # Text block in the right panel.
        "sources": PLACEHOLDER_TEXT,  # Data source text in the footer.
        "legend_section": "Standortinformationen",  # Bold legend subsection title.
        "legend_items": [
            {
                "label": "Gemeindegrenze",  # Legend label.
                "color": "255,255,255,255",  # fill color.
                "outline_color": "255,0,0,255",  # outline color.
            },
            {
                "label": "Geeignete Flächen",  # Legend label.
                "color": "31,60,160,255",  # fill color.
                "outline_color": "31,60,160,255",  # outline color.
            },
            {
                "label": "Gewählter Standort",  # Legend label.
                "color": "255,255,255,255",  # fill color.
                "outline_color": "255,0,0,255",  # outline color.
            },
        ],
        "grid_distance_label": "Abstand: 500 m",  # Text next to grid symbol.
        "scale_units_per_segment": 1000,  # Scale bar segment length in meters.
        "layout_overrides": {
            # Example overrides with current default values.
            "legend_height": 52,
            "grid_title_y": 112,
            "grid_row_y": 117,
        },
    },

    # -------------------------------------------------------------------------
    # Hydropower map configuration
    # -------------------------------------------------------------------------
    "wasser": {
        "title": "Potenzielle Standorte für Wasserkraftanlagen in {municipality}",  # PDF title.
        "description": PLACEHOLDER_TEXT,  # Text block in the right panel.
        "sources": PLACEHOLDER_TEXT,  # Data source text in the footer.
        "legend_section": "Standortinformationen",  # Bold legend subsection title.
        "legend_items": [
            {
                "label": "Gemeindegrenze",  # Legend label.
                "color": "255,255,255,255",  # fill color.
                "outline_color": "255,0,0,255",  # outline color.
            },
            {
                "label": "Nutzungsdaten",  # Legend label.
                "color": "90,118,145,255",  # fill color.
                "outline_color": "90,118,145,255",  # outline color.
            },
            {
                "label": "OSM-Straßendaten",  # Legend label.
                "color": "255,170,0,255",  # line color.
                "outline_color": "255,170,0,255",  # symbol outline color.
                "symbol": "line",  # Use road-like legend symbol instead of box.
            },
        ],
        "grid_distance_label": "Abstand: 500 m",  # Text next to grid symbol.
        "scale_units_per_segment": 1000,  # Scale bar segment length in meters.
        "layout_overrides": {
            # Example overrides with current default values.
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
