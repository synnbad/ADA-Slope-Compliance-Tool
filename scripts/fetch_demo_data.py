#!/usr/bin/env python3
"""
Fetch or generate small DEMs for tests and demos.

USAGE (synthetic):
  python scripts/fetch_demo_data.py synthetic --pattern flat --out data/demo/flat_50x50.tif --shape 50 50
  python scripts/fetch_demo_data.py synthetic --pattern plane --slope-pct 10 --axis x --out data/demo/plane_10pct_x_128.tif
  python scripts/fetch_demo_data.py synthetic --pattern hill --amp 50 --out data/demo/hill_256.tif --shape 256 256

USAGE (download from URL):
  python scripts/fetch_demo_data.py url --url "https://example.com/small_dem.tif" --out data/demo/sample.tif
"""
from __future__ import annotations
import argparse, pathlib, sys
from typing import Tuple

import numpy as np
import rasterio
from rasterio.transform import from_origin
from urllib.request import urlopen

def write_geotiff(arr: np.ndarray, out_path: pathlib.Path, res: Tuple[float, float] = (1.0, 1.0), nodata=None) -> None:
    h, w = arr.shape
    transform = from_origin(0, 0, res[0], res[1])
    profile = {"driver": "GTiff","dtype": "float32","width": w,"height": h,"count": 1,"crs": None,"transform": transform,"nodata": nodata,"tiled": False,"compress": "LZW"}
    arr = arr.astype("float32")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(arr, 1)

def synthetic_flat(shape): return np.zeros(shape, dtype="float32")

def synthetic_plane(shape, slope_pct: float, axis: str, resx: float, resy: float):
    h, w = shape; slope = slope_pct / 100.0
    if axis == "x":
        x = np.arange(w, dtype="float32"); return (x * resx * slope)[None, :].repeat(h, axis=0)
    elif axis == "y":
        y = np.arange(h, dtype="float32"); return (y * resy * slope)[:, None].repeat(w, axis=1)
    raise ValueError("axis must be 'x' or 'y'")

def synthetic_hill(shape, amp: float = 50.0):
    h, w = shape; cy, cx = (h - 1) / 2.0, (w - 1) / 2.0
    yy, xx = np.meshgrid(np.arange(h, dtype="float32"), np.arange(w, dtype="float32"), indexing="ij")
    rr = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2); rr_norm = rr / rr.max() if rr.max() > 0 else rr
    arr = amp * (1.0 - rr_norm**2); arr[arr < 0] = 0.0; return arr

def cmd_synthetic(args):
    shape = (args.shape[0], args.shape[1]); resx, resy = args.res[0], args.res[1]
    if args.pattern == "flat": arr = synthetic_flat(shape)
    elif args.pattern == "plane": arr = synthetic_plane(shape, slope_pct=args.slope_pct, axis=args.axis, resx=resx, resy=resy)
    elif args.pattern == "hill": arr = synthetic_hill(shape, amp=args.amp)
    else: raise ValueError(f"Unknown pattern: {args.pattern}")
    write_geotiff(arr, pathlib.Path(args.out), res=(resx, resy))
    print(f"Wrote synthetic DEM → {args.out}")

def cmd_url(args):
    url = args.url; out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} …")
    with urlopen(url) as resp: data = resp.read()
    if not (out.suffix.lower() in [".tif", ".tiff"]):
        print("Warning: Output extension is not .tif/.tiff. Saving bytes anyway.")
    out.write_bytes(data); print(f"Wrote downloaded file → {out}")

def main(argv=None):
    p = argparse.ArgumentParser(description="Fetch or generate small DEMs for tests/demos.")
    sub = p.add_subparsers(dest="cmd", required=True)
    ps = sub.add_parser("synthetic", help="Generate a deterministic synthetic DEM GeoTIFF.")
    ps.add_argument("--pattern", choices=["flat","plane","hill"], required=True)
    ps.add_argument("--shape", type=int, nargs=2, default=[128,128], metavar=("H","W"))
    ps.add_argument("--res", type=float, nargs=2, default=[1.0,1.0], metavar=("RESX","RESY"))
    ps.add_argument("--out", required=True)
    plane = ps.add_argument_group("plane options")
    plane.add_argument("--slope-pct", type=float, default=10.0)
    plane.add_argument("--axis", choices=["x","y"], default="x")
    hill = ps.add_argument_group("hill options")
    hill.add_argument("--amp", type=float, default=50.0)
    pu = sub.add_parser("url", help="Download a small DEM from a direct .tif/.tiff URL.")
    pu.add_argument("--url", required=True); pu.add_argument("--out", required=True)
    args = p.parse_args(argv)
    return {"synthetic": cmd_synthetic, "url": cmd_url}[args.cmd](args)

if __name__ == "__main__": main()
