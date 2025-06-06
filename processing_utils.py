# processing_utils.py

import geopandas as gpd
import rasterio
from shapely.geometry import LineString

ADA_SLOPE_THRESHOLD = 0.05  # 5%

def sample_elevation_at_points(points_gdf, dem_path):
    with rasterio.open(dem_path) as src:
        # Reproject to match raster CRS
        if points_gdf.crs != src.crs:
            points_gdf = points_gdf.to_crs(src.crs)

        # ✅ Only keep Point geometries
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

def compute_slope_segments(points_gdf):
    """
    Computes slope segments between consecutive points,
    classifies ADA compliance, and returns a GeoDataFrame.
    """
    if points_gdf.crs is None:
        raise ValueError("Input GeoDataFrame must have a CRS")
    if points_gdf.crs.is_geographic:
        points_gdf = points_gdf.to_crs("EPSG:26917")

    if 'path_id' in points_gdf.columns:
        grouped = points_gdf.groupby('path_id')
    else:
        grouped = [(None, points_gdf)]

    segments = []
    slopes = []
    compliance = []
    group_ids = []

    for group_id, group in grouped:
        # Skip empty or invalid geometries
        group = group[group.geometry.notnull()]
        # Preserve the original ordering of points for accurate slope
        # calculations rather than sorting by coordinates
        group = group.copy().sort_index().reset_index(drop=True)

        for i in range(len(group) - 1):
            pt1, pt2 = group.iloc[i], group.iloc[i + 1]
            if pt1["elevation"] is None or pt2["elevation"] is None:
                continue

            elev_diff = pt2["elevation"] - pt1["elevation"]
            dist = pt1.geometry.distance(pt2.geometry)
            slope = elev_diff / dist if dist != 0 else 0

            segment = LineString([pt1.geometry, pt2.geometry])
            segments.append(segment)
            slopes.append(round(slope, 4))
            compliance.append(abs(slope) <= ADA_SLOPE_THRESHOLD)
            group_ids.append(group_id)

    return gpd.GeoDataFrame({
        "path_id": group_ids,
        "slope": slopes,
        "ada_compliant": compliance,
        "geometry": segments
    }, crs=points_gdf.crs)

