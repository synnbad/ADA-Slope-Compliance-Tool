import numpy as np
import pytest
from typing import Tuple

rasterio = pytest.importorskip("rasterio")
from rasterio.io import MemoryFile
from rasterio.transform import from_origin


def geotiff_bytes_from_array(
    arr: np.ndarray, res: Tuple[float, float] = (1.0, 1.0), nodata: float | None = None
) -> bytes:
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


@pytest.fixture
def flat_dem() -> np.ndarray:
    """Create a flat DEM (0% slope everywhere)."""
    return np.full((10, 10), 100.0, dtype=np.float32)


@pytest.fixture
def gentle_slope_dem() -> np.ndarray:
    """Create a DEM with 3% slope (ADA compliant)."""
    # 3% slope = 0.03 rise/run
    x = np.arange(10)
    y = np.arange(10)
    xx, yy = np.meshgrid(x, y)
    # Slope in x direction: 3% = 3m rise per 100m run
    # With 1m pixels: 0.03m rise per 1m run
    return (xx * 0.03 + 100.0).astype(np.float32)


@pytest.fixture
def steep_slope_dem() -> np.ndarray:
    """Create a DEM with 8% slope (ADA non-compliant)."""
    # 8% slope = 0.08 rise/run
    x = np.arange(10)
    y = np.arange(10)
    xx, yy = np.meshgrid(x, y)
    # Slope in x direction: 8% = 8m rise per 100m run
    # With 1m pixels: 0.08m rise per 1m run
    return (xx * 0.08 + 100.0).astype(np.float32)


@pytest.fixture
def nodata_dem() -> np.ndarray:
    """Create a DEM with nodata values."""
    arr = np.full((10, 10), 100.0, dtype=np.float32)
    # Set some nodata values
    arr[0:2, 0:2] = -9999.0
    arr[8:10, 8:10] = -9999.0
    return arr


@pytest.fixture
def complex_dem() -> np.ndarray:
    """Create a DEM with varying slopes for comprehensive testing."""
    # Create a more complex elevation surface
    x = np.linspace(0, 20, 20)
    y = np.linspace(0, 20, 20)
    xx, yy = np.meshgrid(x, y)
    
    # Combination of linear and quadratic terms
    # Linear: 2% slope in x, 1% slope in y
    # Quadratic: gentle curvature
    elevation = (
        100.0 +  # base elevation
        xx * 0.02 +  # 2% slope in x direction
        yy * 0.01 +  # 1% slope in y direction
        (xx - 10) ** 2 * 0.001 +  # gentle curvature
        (yy - 10) ** 2 * 0.0005
    )
    return elevation.astype(np.float32)


@pytest.fixture
def flat_dem_bytes(flat_dem) -> bytes:
    """Flat DEM as GeoTIFF bytes."""
    return geotiff_bytes_from_array(flat_dem)


@pytest.fixture
def gentle_slope_dem_bytes(gentle_slope_dem) -> bytes:
    """Gentle slope DEM as GeoTIFF bytes."""
    return geotiff_bytes_from_array(gentle_slope_dem)


@pytest.fixture
def steep_slope_dem_bytes(steep_slope_dem) -> bytes:
    """Steep slope DEM as GeoTIFF bytes."""
    return geotiff_bytes_from_array(steep_slope_dem)


@pytest.fixture
def nodata_dem_bytes(nodata_dem) -> bytes:
    """Nodata DEM as GeoTIFF bytes."""
    return geotiff_bytes_from_array(nodata_dem, nodata=-9999.0)
