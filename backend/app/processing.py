import numpy as np

try:
    from rasterio.io import MemoryFile
except Exception as e:
    raise RuntimeError("rasterio is required for GeoTIFF DEM processing") from e

def process_dem_in_memory(
    geotiff_bytes: bytes,
    running_slope_max: float = 0.05,   # 5%
    cross_slope_max: float = 0.02083, # ~2.083%
):
    """
    Compute slope (in percent) from a DEM GeoTIFF and return basic ADA compliance stats.
    running_slope_max/cross_slope_max are expressed as rise/run (e.g., 0.05 -> 5%).
    """
    with MemoryFile(geotiff_bytes) as memfile:
        with memfile.open() as src:
            dem = src.read(1).astype("float32")
            # Handle nodata
            if src.nodata is not None:
                dem[dem == src.nodata] = np.nan

            # Pixel size (map units, assume meters)
            resx, resy = src.res  # (xsize, ysize)
            # Gradient of elevation
            gy, gx = np.gradient(dem, resy, resx)  # dz/dy, dz/dx
            # Running slope magnitude (rise/run)
            slope = np.sqrt(gx**2 + gy**2)
            slope_pct = slope * 100.0

            valid = np.isfinite(slope_pct)
            total = int(valid.sum())
            over_mask = (slope_pct > (running_slope_max * 100.0)) & valid
            violations = int(over_mask.sum())
            pct_viol = float((violations / total) * 100.0) if total else 0.0
            max_slope = float(np.nanmax(slope_pct)) if total else 0.0
            mean_slope = float(np.nanmean(slope_pct)) if total else 0.0

            summary = {
                "running_slope_threshold_pct": round(running_slope_max * 100.0, 5),
                "cross_slope_threshold_pct": round(cross_slope_max * 100.0, 5),
                "pixels_total": total,
                "pixels_violating": violations,
                "percent_violating": round(pct_viol, 3),
                "max_slope_pct": round(max_slope, 3),
                "mean_slope_pct": round(mean_slope, 3),
                "pass": violations == 0,
            }

            # 10-bin histogram from 0 to max_slope (guard low max)
            hist_max = max(10.0, max_slope)
            hist, _ = np.histogram(slope_pct[valid], bins=10, range=(0, hist_max))
            artifacts = {"histogram": hist.astype(int).tolist()}

            return {"summary": summary, "artifacts": artifacts}
