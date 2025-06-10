import os
import sys
import geopandas as gpd
from shapely.geometry import Point
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # noqa: E402
from processing_utils import (
    compute_slope_segments,
    convert_polygons_to_lines,
    align_crs,
)  # noqa: E402
from app import compute_smoothed_slopes  # noqa: E402


def test_compute_slope_segments_basic():
    points = gpd.GeoDataFrame(
        {
            "path_id": [1, 1, 1],
            "elevation": [0.0, 1.0, 1.5],
            "geometry": [Point(0, 0), Point(10, 0), Point(20, 0)],
        },
        crs="EPSG:26917",
    )

    segments = compute_slope_segments(points)
    slopes = list(segments["slope"])  # slopes are rounded to 4 decimals in function
    compliance = list(segments["ada_compliant"])

    assert slopes == pytest.approx([0.1, 0.05])
    assert compliance == [False, True]


def test_convert_polygons_to_lines():
    from shapely.geometry import Polygon, MultiPolygon, LineString

    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
    multipoly = MultiPolygon([Polygon([(2, 0), (3, 0), (3, 1), (2, 1), (2, 0)])])
    line = LineString([(4, 0), (5, 0)])

    gdf = gpd.GeoDataFrame({"geometry": [poly, multipoly, line]}, crs="EPSG:4326")
    lines = convert_polygons_to_lines(gdf)

    assert len(lines) == 3
    assert all(lines.geometry.type == "LineString")


def test_align_crs(tmp_path):
    import numpy as np
    import rasterio
    from rasterio.transform import from_origin

    raster_path = tmp_path / "test.tif"
    transform = from_origin(0, 1, 1, 1)
    with rasterio.open(
        raster_path,
        "w",
        driver="GTiff",
        height=1,
        width=1,
        count=1,
        dtype="float32",
        crs="EPSG:3857",
        transform=transform,
    ) as dst:
        dst.write(np.zeros((1, 1), dtype="float32"), 1)

    gdf = gpd.GeoDataFrame({"geometry": [Point(0, 0)]}, crs="EPSG:4326")
    aligned = align_crs(gdf, str(raster_path))

    assert aligned.crs.to_string() == "EPSG:3857"


def test_compute_smoothed_slopes_insufficient_points():
    gdf = gpd.GeoDataFrame(
        {
            "path_id": [1, 1],
            "elevation": [0.0, 1.0],
            "geometry": [Point(0, 0), Point(10, 0)],
        },
        crs="EPSG:26917",
    )

    with pytest.raises(ValueError):
        compute_smoothed_slopes(gdf, window_size=5)
