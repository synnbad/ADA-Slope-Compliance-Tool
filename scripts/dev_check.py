#!/usr/bin/env python3
"""
Synthetic test for slope math validation - quick sanity check.

Creates a 10% planar slope DEM and two test paths:
- Path along slope direction (should have ~10% running, ~0% cross)
- Path across slope direction (should have ~0% running, ~10% cross)
"""
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import LineString
import tempfile
import os

def create_test_dem(slope_pct=10.0, size=50):
    """Create synthetic DEM with uniform slope"""
    x = np.arange(size)
    y = np.arange(size)  
    xx, yy = np.meshgrid(x, y)
    
    # 10% slope in x direction (rise/run = 0.1)
    elevation = 100 + (xx * slope_pct / 100.0)
    
    # Create temporary DEM file
    transform = from_origin(0, 0, 1, 1)  # 1m pixels
    profile = {
        'driver': 'GTiff',
        'dtype': 'float32', 
        'nodata': None,
        'width': size,
        'height': size,
        'count': 1,
        'crs': 'EPSG:3857',  # Projected CRS in meters
        'transform': transform
    }
    
    tmp_dem = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)
    with rasterio.open(tmp_dem.name, 'w', **profile) as dst:
        dst.write(elevation.astype(np.float32), 1)
    
    return tmp_dem.name

def create_test_paths():
    """Create two test paths: along slope and across slope"""
    # Path 1: Along slope (x direction) - should have high running slope
    path_along = LineString([(10, 25), (40, 25)])
    
    # Path 2: Across slope (y direction) - should have high cross slope  
    path_across = LineString([(25, 10), (25, 40)])
    
    paths_gdf = gpd.GeoDataFrame({
        'name': ['along_slope', 'across_slope'],
        'geometry': [path_along, path_across]
    }, crs='EPSG:3857')
    
    tmp_paths = tempfile.NamedTemporaryFile(suffix='.geojson', delete=False)
    paths_gdf.to_file(tmp_paths.name, driver='GeoJSON')
    return tmp_paths.name

def main():
    print("🧪 Synthetic Slope Math Check")
    print("=" * 35)
    
    # Create test data
    dem_file = create_test_dem(slope_pct=10.0)
    paths_file = create_test_paths()
    
    try:
        # Import and run our eval_ada function
        import sys
        sys.path.append('scripts')
        from eval_ada import main as eval_main
        
        output_file = tempfile.NamedTemporaryFile(suffix='.geojson', delete=False).name
        eval_main(dem_file, paths_file, output_file, interval_m=2.0)
        
        # Check results
        result_gdf = gpd.read_file(output_file)
        
        print(f"Along-slope path: running={result_gdf.iloc[0]['running_max']:.1f}%, cross={result_gdf.iloc[0]['cross_max']:.1f}%")
        print(f"Across-slope path: running={result_gdf.iloc[1]['running_max']:.1f}%, cross={result_gdf.iloc[1]['cross_max']:.1f}%")
        
        # Validate expectations
        along_running = result_gdf.iloc[0]['running_max']
        along_cross = result_gdf.iloc[0]['cross_max'] 
        across_running = result_gdf.iloc[1]['running_max']
        across_cross = result_gdf.iloc[1]['cross_max']
        
        success = (
            8.0 < along_running < 12.0 and along_cross < 2.0 and  # Along slope: high running, low cross
            across_running < 2.0 and 8.0 < across_cross < 12.0   # Across slope: low running, high cross
        )
        
        print(f"✅ Slope math validation: {'PASS' if success else 'FAIL'}")
        
    finally:
        # Clean up temp files
        for f in [dem_file, paths_file, output_file]:
            if os.path.exists(f):
                os.unlink(f)

if __name__ == "__main__":
    main()
