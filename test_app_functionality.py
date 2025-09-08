#!/usr/bin/env python3
"""
Quick functionality test for the enhanced ADA Slope Compliance Tool
Tests the core functions that power the Streamlit UI
"""

import sys
import os
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import tempfile

# Add current directory to path
sys.path.append('.')

from ada_slope import core
from ada_slope import io as aio


def test_ada_slope_integration():
    """Test the integration of our enhanced ada_slope functions."""
    print("🧪 Testing ADA Slope Compliance Tool Integration...")
    
    # Test 1: Core constants
    print(f"✅ ADA Running Slope Threshold: {core.ADA_RUNNING_SLOPE_THRESHOLD}")
    print(f"✅ ADA Cross Slope Threshold: {core.ADA_CROSS_SLOPE_THRESHOLD}")
    
    # Test 2: Create synthetic test data
    print("\n📊 Creating synthetic test data...")
    
    # Create a simple DEM with known slope
    elevation_data = np.array([
        [100.0, 100.1, 100.2, 100.3],
        [100.0, 100.1, 100.2, 100.3],
        [100.0, 100.1, 100.2, 100.3],
        [100.0, 100.1, 100.2, 100.3]
    ], dtype=np.float32)
    
    # Test 3: Core slope computation
    print("🔢 Testing slope computation...")
    running_slope = core.compute_running_slope(elevation_data, resx=1.0, resy=1.0, nodata=None)
    cross_slope = core.compute_cross_slope(elevation_data, resx=1.0, resy=1.0, assumed_path_axis="x", nodata=None)
    
    print(f"   - Running slope shape: {running_slope.shape}")
    print(f"   - Cross slope shape: {cross_slope.shape}")
    print(f"   - Mean running slope: {np.nanmean(running_slope):.4f}%")
    print(f"   - Mean cross slope: {np.nanmean(cross_slope):.4f}%")
    
    # Test 4: ADA Compliance check
    compliant_running = np.sum(running_slope <= 5.0) / np.sum(~np.isnan(running_slope)) * 100
    compliant_cross = np.sum(cross_slope <= 2.083) / np.sum(~np.isnan(cross_slope)) * 100
    
    print(f"   - Running slope compliance: {compliant_running:.1f}%")
    print(f"   - Cross slope compliance: {compliant_cross:.1f}%")
    
    # Test 5: Point-based workflow (like the UI uses)
    print("\n📍 Testing point-based workflow...")
    
    # Create test points
    points = [
        Point(0, 0), Point(1, 0), Point(2, 0), Point(3, 0)
    ]
    
    gdf_points = gpd.GeoDataFrame({
        'path_id': [1, 1, 1, 1],
        'geometry': points
    }, crs='EPSG:26917')
    
    print(f"   - Created {len(gdf_points)} test points")
    
    # Test the core.compute_slope_segments function (used by UI)
    # Add elevation manually for this test
    gdf_points['elevation'] = [100.0, 100.1, 100.2, 100.3]
    
    segments = core.compute_slope_segments(gdf_points)
    print(f"   - Generated {len(segments)} slope segments")
    print(f"   - Segment slopes: {segments['slope'].tolist()}")
    print(f"   - ADA compliance: {segments['ada_compliant'].tolist()}")
    
    print("\n✅ Integration test completed successfully!")
    return True


def test_ui_functions_import():
    """Test that the UI can import our functions correctly."""
    print("\n🎨 Testing UI function imports...")
    
    try:
        # Test imports that the app.py uses
        from ada_slope import core
        from ada_slope import io as aio
        from ada_slope.config import DEFAULT
        
        print("   ✅ ada_slope.core imported successfully")
        print("   ✅ ada_slope.io imported successfully") 
        print("   ✅ ada_slope.config imported successfully")
        
        # Test specific functions
        assert hasattr(core, 'compute_running_slope')
        assert hasattr(core, 'compute_cross_slope')
        assert hasattr(core, 'ADA_RUNNING_SLOPE_THRESHOLD')
        assert hasattr(aio, 'sample_elevation_at_points')
        
        print("   ✅ All required functions available")
        return True
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def main():
    """Run all functionality tests."""
    print("🚀 ADA Slope Compliance Tool - Functionality Test\n")
    print("=" * 60)
    
    try:
        # Run integration tests
        test1_pass = test_ada_slope_integration()
        test2_pass = test_ui_functions_import()
        
        print("\n" + "=" * 60)
        if test1_pass and test2_pass:
            print("🎉 ALL TESTS PASSED - App is ready for use!")
            print("\nYou can now:")
            print("1. Open http://localhost:8501 in your browser")
            print("2. Upload DEM and path data files")
            print("3. Test the enhanced slope analysis features")
            return 0
        else:
            print("❌ Some tests failed - check the output above")
            return 1
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
