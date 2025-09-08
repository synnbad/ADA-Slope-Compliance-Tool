import sys
sys.path.append("../../")  # Add parent directory to path

import numpy as np
from ada_slope.core import compute_running_slope, compute_cross_slope
from ada_slope.io import load_dem_from_bytes


def process_dem_in_memory(
    geotiff_bytes: bytes,
    running_slope_max: float = 0.05,
    cross_slope_max: float = 0.02083,
    assumed_path_axis: str = "x",
):
    """
    Compute running and cross-slope (percent) from a DEM GeoTIFF and return compliance stats.

    running_slope_max/cross_slope_max are expressed as rise/run (e.g., 0.05 -> 5%).
    """
    # Load DEM from bytes using ada_slope functions
    dem, resx, resy, nodata = load_dem_from_bytes(geotiff_bytes)
    
    # Compute slopes using ada_slope core functions
    running_slope = compute_running_slope(dem, resx, resy, nodata)
    cross_slope = compute_cross_slope(dem, resx, resy, assumed_path_axis, nodata)
    
    # Calculate compliance statistics
    valid = np.isfinite(running_slope)
    total = int(valid.sum())

    run_over = (running_slope > (running_slope_max * 100.0)) & valid
    cross_over = (cross_slope > (cross_slope_max * 100.0)) & np.isfinite(cross_slope)

    pixels_violating_running = int(run_over.sum())
    pixels_violating_cross = int(cross_over.sum())
    percent_violating_running = float((pixels_violating_running / total) * 100.0) if total else 0.0
    percent_violating_cross = float((pixels_violating_cross / total) * 100.0) if total else 0.0

    max_slope = float(np.nanmax(running_slope)) if total else 0.0
    mean_slope = float(np.nanmean(running_slope)) if total else 0.0

    summary = {
        "running_slope_threshold_pct": round(running_slope_max * 100.0, 5),
        "cross_slope_threshold_pct": round(cross_slope_max * 100.0, 5),
        "pixels_total": total,
        "pixels_violating_running": pixels_violating_running,
        "percent_violating_running": round(percent_violating_running, 3),
        "pixels_violating_cross": pixels_violating_cross,
        "percent_violating_cross": round(percent_violating_cross, 3),
        "max_slope_pct": round(max_slope, 3),
        "mean_slope_pct": round(mean_slope, 3),
        "pass_running": pixels_violating_running == 0,
        "pass_cross": pixels_violating_cross == 0,
    }

    hist_max = max(10.0, max_slope)
    hist, _ = np.histogram(running_slope[valid], bins=10, range=(0, hist_max))
    artifacts = {"histogram": hist.astype(int).tolist()}

    return {"summary": summary, "artifacts": artifacts}
