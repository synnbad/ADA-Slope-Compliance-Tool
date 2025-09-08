#!/usr/bin/env python3
"""
Compute running & cross-slope along pedestrian paths against a DEM.

- Reprojects paths to DEM CRS (must be projected in meters).
- Densifies each path every N meters (default: 2 m).
- Computes slope magnitude from DEM via np.gradient (percent).
- Computes aspect (downslope azimuth).
- Computes cross-slope as S * |sin(aspect - bearing)| in degrees.
- Aggregates per-path max running/cross and boolean flags vs thresholds.

Usage:
  python scripts/eval_ada.py --dem data/dem.tif --paths data/paths_osm.geojson --out outputs/paths_ada_eval.geojson
"""
import math
import argparse
from typing import List
import numpy as np
import geopandas as gpd
import rasterio
from shapely.geometry import LineString, Point
from pyproj import Transformer

def _densify_line(line: LineString, every_m: float, crs: str) -> List[Point]:
    # project to meters for even spacing
    to_m = Transformer.from_crs(crs, 3857, always_xy=True)
    to_src = Transformer.from_crs(3857, crs, always_xy=True)
    xs, ys = to_m.transform(*line.xy)
    metr = LineString(list(zip(xs, ys)))
    length = metr.length
    pts_m = [metr.interpolate(d) for d in np.arange(0, length + 1e-6, every_m)]
    x, y = to_src.transform([p.x for p in pts_m], [p.y for p in pts_m])
    return [Point(px, py) for px, py in zip(x, y)]

def _bearing_deg(p0: Point, p1: Point) -> float:
    dx, dy = (p1.x - p0.x), (p1.y - p0.y)
    return (math.degrees(math.atan2(dx, dy)) + 360.0) % 360.0  # 0=N, 90=E

def main(dem_path: str, paths_path: str, out_path: str,
         interval_m: float = 2.0, run_thr: float = 5.0, cross_thr: float = 2.083):
    paths = gpd.read_file(paths_path)

    with rasterio.open(dem_path) as dem:
        if dem.crs is None:
            raise SystemExit("DEM must have a valid CRS (projected, in meters).")
        
        # GUARD RAIL: Check if CRS is geographic (degrees)
        if dem.crs.is_geographic:
            raise SystemExit(f"ERROR: DEM CRS {dem.crs} uses degrees. DEM must be projected in meters (e.g., UTM). Reproject first with gdalwarp or QGIS.")
        
        # Align paths to DEM CRS
        paths = paths.to_crs(dem.crs)
        arr = dem.read(1).astype("float32")
        if dem.nodata is not None:
            arr[arr == dem.nodata] = np.nan
        resx, resy = dem.res
        gy, gx = np.gradient(arr, resy, resx)  # dz/dy, dz/dx
        slope_pct = np.sqrt(gx**2 + gy**2) * 100.0
        aspect_deg = (np.degrees(np.arctan2(gx, gy)) + 360.0) % 360.0  # downslope azimuth

        def sample(values: np.ndarray, pt: Point) -> float:
            r, c = dem.index(pt.x, pt.y)
            if 0 <= r < values.shape[0] and 0 <= c < values.shape[1]:
                v = float(values[r, c])
                return v if math.isfinite(v) else float("nan")
            return float("nan")

        results = []
        for i, row in paths.iterrows():
            geom: LineString = row.geometry
            if geom is None or geom.is_empty or not isinstance(geom, LineString):
                results.append({"running_max": np.nan, "cross_max": np.nan,
                                "running_ok": False, "cross_ok": False})
                continue

            pts = _densify_line(geom, every_m=interval_m, crs=str(paths.crs))
            if len(pts) < 2:
                results.append({"running_max": np.nan, "cross_max": np.nan,
                                "running_ok": False, "cross_ok": False})
                continue

            # segment bearings
            bears = [_bearing_deg(pts[j], pts[j+1]) for j in range(len(pts)-1)]

            # sample at segment midpoints for stability
            run_vals, cross_vals = [], []
            for j in range(len(pts)-1):
                p0, p1 = pts[j], pts[j+1]
                mid = Point((p0.x + p1.x) / 2.0, (p0.y + p1.y) / 2.0)
                S = sample(slope_pct, mid)
                A = sample(aspect_deg, mid)
                b = bears[j]
                if not (math.isfinite(S) and math.isfinite(A)):
                    continue
                cross = S * abs(math.sin(math.radians(A - b)))
                run_vals.append(S)
                cross_vals.append(cross)

            rmax = float(np.nanmax(run_vals)) if run_vals else np.nan
            cmax = float(np.nanmax(cross_vals)) if cross_vals else np.nan
            results.append({
                "running_max": rmax,
                "cross_max": cmax,
                "running_ok": (rmax <= run_thr) if math.isfinite(rmax) else False,
                "cross_ok":   (cmax <= cross_thr) if math.isfinite(cmax) else False,
            })

        out = paths.copy()
        for k in results[0].keys():
            out[k] = [r[k] for r in results]
        out.to_file(out_path, driver="GeoJSON")
        print(f"Wrote {out_path} — {len(out)} features")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dem", required=True)
    ap.add_argument("--paths", required=True)
    ap.add_argument("--out", default="outputs/paths_ada_eval.geojson")
    ap.add_argument("--interval-m", type=float, default=2.0)
    ap.add_argument("--running-thr", type=float, default=5.0)
    ap.add_argument("--cross-thr", type=float, default=2.083)
    a = ap.parse_args()
    main(a.dem, a.paths, a.out, a.interval_m, a.running_thr, a.cross_thr)
