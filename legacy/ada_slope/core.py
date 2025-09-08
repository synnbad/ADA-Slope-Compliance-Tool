"""Core processing functions for ADA slope computations.

This module centralizes numerical algorithms and keeps them pure for easy testing.
"""
from __future__ import annotations

from typing import Tuple, Optional

import numpy as np
import geopandas as gpd
from shapely.geometry import LineString, Polygon, MultiPolygon


# ADA compliance thresholds
ADA_RUNNING_SLOPE_THRESHOLD = 0.05  # 5% (1:20)
ADA_CROSS_SLOPE_THRESHOLD = 0.02083  # 2.083% (1:48)


def convert_polygons_to_lines(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Convert Polygon and MultiPolygon geometries to LineStrings.

    Returns a new GeoDataFrame with the same CRS.
    """
    lines = []
    for geom in gdf.geometry:
        if isinstance(geom, Polygon):
            lines.append(LineString(geom.exterior.coords))
        elif isinstance(geom, MultiPolygon):
            for poly in geom.geoms:
                lines.append(LineString(poly.exterior.coords))
        elif isinstance(geom, LineString):
            lines.append(geom)
    return gpd.GeoDataFrame(geometry=lines, crs=gdf.crs)


def compute_slope_segments(points_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Compute slope segments between consecutive points and classify ADA compliance.

    Args:
        points_gdf: GeoDataFrame containing Point geometries and an "elevation" column.

    Returns:
        GeoDataFrame of LineString segments with columns: path_id, slope, ada_compliant, geometry
    """
    if points_gdf.crs is None:
        raise ValueError("Input GeoDataFrame must have a CRS")
    if points_gdf.crs.is_geographic:
        # Choose a metric projection for distance-based slope calculations
        points_gdf = points_gdf.to_crs("EPSG:26917")

    if "path_id" in points_gdf.columns:
        points_gdf = points_gdf.dropna(subset=["path_id"])
        grouped = points_gdf.groupby("path_id")
    else:
        grouped = [(None, points_gdf)]

    segments = []
    slopes = []
    compliance = []
    group_ids = []

    for group_id, group in grouped:
        group = group[group.geometry.notnull()]
        group = group.copy().sort_index().reset_index(drop=True)

        for i in range(len(group) - 1):
            pt1, pt2 = group.iloc[i], group.iloc[i + 1]
            if pt1.get("elevation") is None or pt2.get("elevation") is None:
                continue

            elev_diff = pt2["elevation"] - pt1["elevation"]
            dist = pt1.geometry.distance(pt2.geometry)
            slope = elev_diff / dist if dist != 0 else 0.0

            segment = LineString([pt1.geometry, pt2.geometry])
            segments.append(segment)
            slopes.append(round(slope, 4))
            compliance.append(abs(slope) <= ADA_RUNNING_SLOPE_THRESHOLD)
            group_ids.append(group_id)

    return gpd.GeoDataFrame(
        {
            "path_id": group_ids,
            "slope": slopes,
            "ada_compliant": compliance,
            "geometry": segments,
        },
        crs=points_gdf.crs,
    )


def compute_running_slope(
    dem: np.ndarray, 
    resx: float, 
    resy: float, 
    nodata: Optional[float] = None
) -> np.ndarray:
    """Compute running slope from DEM using numpy gradient with pixel spacing.
    
    Args:
        dem: 2D elevation array
        resx: Pixel size in X direction (meters)
        resy: Pixel size in Y direction (meters)  
        nodata: Nodata value to mask (will be converted to NaN)
    
    Returns:
        2D array of slope magnitudes in percentage
    """
    # Mask nodata values
    masked_dem = mask_nodata(dem, nodata)
    
    # Compute gradients with proper pixel spacing
    gy, gx = np.gradient(masked_dem, resy, resx)
    
    # Compute slope magnitude as percentage
    slope_magnitude = np.sqrt(gx**2 + gy**2) * 100.0
    
    return slope_magnitude


def compute_cross_slope(
    dem: np.ndarray,
    resx: float, 
    resy: float,
    assumed_path_axis: str = "x",
    nodata: Optional[float] = None
) -> np.ndarray:
    """Compute cross-slope (perpendicular to assumed path direction).
    
    Args:
        dem: 2D elevation array
        resx: Pixel size in X direction (meters)
        resy: Pixel size in Y direction (meters)
        assumed_path_axis: Direction of path ("x" or "y")
        nodata: Nodata value to mask
    
    Returns:
        2D array of cross-slope values in percentage
    """
    # Mask nodata values
    masked_dem = mask_nodata(dem, nodata)
    
    # Compute gradients with proper pixel spacing
    gy, gx = np.gradient(masked_dem, resy, resx)
    
    # Cross-slope is component perpendicular to path direction
    if assumed_path_axis.lower() == "x":
        cross_slope = np.abs(gy) * 100.0  # Y component for X-axis paths
    else:
        cross_slope = np.abs(gx) * 100.0  # X component for Y-axis paths
        
    return cross_slope


def mask_nodata(arr: np.ndarray, nodata: Optional[float] = None) -> np.ndarray:
    """Apply robust nodata masking using np.isfinite.
    
    Args:
        arr: Input array
        nodata: Specific nodata value to mask to NaN
        
    Returns:
        Array with nodata values set to NaN and non-finite values masked
    """
    masked = arr.copy().astype(np.float64)
    
    # Set specific nodata value to NaN
    if nodata is not None:
        masked[arr == nodata] = np.nan
        
    # Mask any remaining non-finite values
    masked[~np.isfinite(masked)] = np.nan
    
    return masked
