import numpy as np
import pytest

rasterio = pytest.importorskip("rasterio")
from rasterio.io import MemoryFile
from rasterio.transform import from_origin

def geotiff_bytes_from_array(arr: np.ndarray, res=(1.0, 1.0), nodata=None) -> bytes:
    """Write a 2D array to an in-memory GeoTIFF and return bytes."""
    h, w = arr.shape
    transform = from_origin(0, 0, res[0], res[1])
    profile = {
        "driver": "GTiff",
        "dtype": "float32",
        "width": w,
        "height": h,
        "count": 1,
        "crs": None,
        "transform": transform,
        "nodata": nodata,
    }
    arr = arr.astype("float32")
    with MemoryFile() as mem:
        with mem.open(**profile) as dst:
            dst.write(arr, 1)
        return mem.read()
