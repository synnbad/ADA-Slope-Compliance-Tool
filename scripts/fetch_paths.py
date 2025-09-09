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
    # bbox = [minx, miny, maxx, maxy] in WGS84 -> convert to tuple
    bbox_tuple = tuple(bbox)
    nodes, edges = ua.osm.load.ua_network_from_bbox(bbox=bbox_tuple)
    
    # Debug: Check what columns we have
    print(f"Available columns: {list(edges.columns)}")
    
    # UrbanAccess typically stores geometry in a different column or format
    # Let's work with what we have and create geometry from coordinates
    from shapely.geometry import LineString
    
    # Check if we have lat/lon columns or need to construct geometry
    if 'geometry' in edges.columns:
        gdf = gpd.GeoDataFrame(edges, geometry='geometry', crs="EPSG:4326")
    else:
        # Build geometry from node coordinates if needed
        # This is a simplified approach - UrbanAccess edges connect node IDs
        print("No geometry column found, creating simple GeoDataFrame")
        gdf = gpd.GeoDataFrame(edges, crs="EPSG:4326")
        
    if "highway" in gdf.columns:
        gdf = gdf[gdf["highway"].isin(PEDESTRIAN_TAGS)]
        
    print(f"Found {len(gdf)} pedestrian edges after filtering")
    
    if len(gdf) > 0:
        gdf.to_file(out_path, driver="GeoJSON")
        print(f"Wrote {out_path} with {len(gdf)} features")
    else:
        print("No pedestrian edges found to save")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bbox", type=float, nargs=4, required=True, help="minx miny maxx maxy (lon/lat WGS84)")
    ap.add_argument("--out", default="data/paths_osm.geojson")
    a = ap.parse_args()
    main(a.bbox, a.out)
