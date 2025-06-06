import os
import sys
import geopandas as gpd
from shapely.geometry import Point
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # noqa: E402
from processing_utils import compute_slope_segments  # noqa: E402


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
