"""
General helper functions for buffered analysis contexts.

These helpers are used when datasets must not be clipped too early to the
municipality boundary, for example before buffers or proximity analyses are
created.
"""

import geopandas as gpd


def build_analysis_context(
    boundary: gpd.GeoDataFrame,
    buffer_meters: int,
) -> gpd.GeoDataFrame:
    """Build one buffered analysis context around a municipality boundary."""

    context_geometry = boundary[["geometry"]].dissolve().buffer(buffer_meters)
    return gpd.GeoDataFrame(
        {"context_m": [buffer_meters]},
        geometry=context_geometry,
        crs=boundary.crs,
    )


def area_to_overpass_bbox(area: gpd.GeoDataFrame) -> str:
    """Convert one polygon area to an Overpass bounding box string."""

    min_lon, min_lat, max_lon, max_lat = area.to_crs(epsg=4326).total_bounds
    return f"{min_lat},{min_lon},{max_lat},{max_lon}"
