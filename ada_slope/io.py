"""I/O utilities: raster/vector helpers, CRS alignment and validation."""
from __future__ import annotations

from typing import Optional

import geopandas as gpd
import rasterio
from rasterio.io import DatasetReader
import logging

logger = logging.getLogger(__name__)


def ensure_vector_matches_raster_crs(vector_gdf: gpd.GeoDataFrame, raster_path: str) -> gpd.GeoDataFrame:
    """Return a GeoDataFrame reprojected to the raster CRS if needed.

    Raises on IO errors. Does not mutate the input in-place.
    """
    with rasterio.open(raster_path) as src:
        raster_crs = src.crs

    if vector_gdf.crs is None:
        raise ValueError("Input vector has no CRS")

    if raster_crs is None:
        logger.warning("Raster %s has no CRS; returning original vector", raster_path)
        return vector_gdf

    if vector_gdf.crs != raster_crs:
        logger.info("Reprojecting vector from %s to %s", vector_gdf.crs, raster_crs)
        return vector_gdf.to_crs(raster_crs)
    return vector_gdf


def open_raster(path: str) -> DatasetReader:
    """Open a raster and perform a quick sanity check.

    Caller is responsible for closing the DatasetReader (use context manager).
    """
    src = rasterio.open(path)
    if src.count < 1:
        src.close()
        raise RuntimeError("Raster has no bands")
    return src


def sample_elevation_at_points(points_gdf: gpd.GeoDataFrame, dem_path: str) -> gpd.GeoDataFrame:
    """Sample elevation values for Point geometries from a DEM and return a new GeoDataFrame

    This mirrors the previous `processing_utils.sample_elevation_at_points` behavior.
    """
    with rasterio.open(dem_path) as src:
        # Reproject to match raster CRS
        if points_gdf.crs != src.crs:
            points_gdf = points_gdf.to_crs(src.crs)

        # Only keep Point geometries
        points_gdf = points_gdf[points_gdf.geometry.type == "Point"].copy()

        # Sample elevation values
        coords = [(geom.x, geom.y) for geom in points_gdf.geometry]
        elevations = list(src.sample(coords))
        nodata = src.nodata or -9999
        points_gdf["elevation"] = [val[0] if val and val[0] != nodata else None for val in elevations]

    # Reproject sampled points to a metric CRS for distance-based calculations
    if points_gdf.crs is None:
        raise ValueError("Input GeoDataFrame must have a CRS")
    if points_gdf.crs.is_geographic:
        points_gdf = points_gdf.to_crs("EPSG:26917")

    return points_gdf
