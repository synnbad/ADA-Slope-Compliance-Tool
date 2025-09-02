import sys
import numpy as np
import pytest

sys.path.append("backend")

rasterio = pytest.importorskip("rasterio")
from app.processing import process_dem_in_memory
from conftest import geotiff_bytes_from_array

def test_flat_dem_passes():
    arr = np.zeros((50, 50), dtype="float32")
    data = geotiff_bytes_from_array(arr, res=(1.0, 1.0))
    result = process_dem_in_memory(data, running_slope_max=0.05)
    summary = result["summary"]
    assert summary["pixels_total"] == 2500
    assert summary["pixels_violating"] == 0
    assert summary["pass"] is True

def test_steep_plane_violates():
    h, w = 50, 50
    x = np.arange(w, dtype="float32")
    # ~10% slope along +x if resx=1
    arr = (x * 0.1)[None, :].repeat(h, axis=0)
    data = geotiff_bytes_from_array(arr, res=(1.0, 1.0))
    result = process_dem_in_memory(data, running_slope_max=0.05)
    assert result["summary"]["pixels_violating"] > 0
    assert result["summary"]["percent_violating"] >= 99.0
