#!/usr/bin/env python3
"""
Fetch OSM pedestrian edges for a bounding box using UrbanAccess, save to GeoJSON.

Usage:
  python scripts/fetch_paths.py --bbox -84.30 30.43 -84.28 30.46 --out data/paths_osm.geojson
"""
import argparse
import geopandas as gpd
import urbanaccess as ua

PEDESTRIAN_TAGS = {"footway","path","pedestrian","steps","living_street","residential"}

def main(bbox, out_path):
    # bbox = [minx, miny, maxx, maxy] in WGS84
    nodes, edges = ua.osm.load.ua_network_from_bbox(bbox=bbox)
    gdf = gpd.GeoDataFrame(edges, geometry="geometry", crs="EPSG:4326")
    if "highway" in gdf.columns:
        gdf = gdf[gdf["highway"].isin(PEDESTRIAN_TAGS)]
    gdf.to_file(out_path, driver="GeoJSON")
    print(f"Wrote {out_path} with {len(gdf)} features")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bbox", type=float, nargs=4, required=True, help="minx miny maxx maxy (lon/lat WGS84)")
    ap.add_argument("--out", default="data/paths_osm.geojson")
    a = ap.parse_args()
    main(a.bbox, a.out)
