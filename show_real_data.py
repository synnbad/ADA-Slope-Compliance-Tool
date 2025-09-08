#!/usr/bin/env python3
"""
Quick guide to available real data for ADA Slope Compliance Tool testing
"""

import json
from pathlib import Path
import os

def analyze_existing_data():
    """Analyze the real data we already have."""
    print("🎯 Real Data Available for Testing")
    print("=" * 50)
    
    # FSU Campus Data
    fsu_raw_path = Path("data/raw/fsu_paths.geojson")
    if fsu_raw_path.exists():
        try:
            with open(fsu_raw_path, 'r') as f:
                fsu_data = json.load(f)
            
            feature_count = len(fsu_data.get('features', []))
            print(f"🏫 FSU Campus Pathways (REAL DATA)")
            print(f"   📁 File: {fsu_raw_path}")
            print(f"   📊 Pathways: {feature_count}")
            print(f"   🎯 Status: ✅ Ready to use")
            print(f"   ♿ Type: University campus sidewalks/paths")
            print()
        except Exception as e:
            print(f"   ❌ Error reading FSU data: {e}")
    
    # Test Data
    test_path = Path("data/test/test_paths.geojson")
    if test_path.exists():
        try:
            with open(test_path, 'r') as f:
                test_data = json.load(f)
            
            test_count = len(test_data.get('features', []))
            print(f"🧪 Washington DC Test Paths (REAL DATA)")
            print(f"   📁 File: {test_path}")
            print(f"   📊 Pathways: {test_count}")
            print(f"   🎯 Status: ✅ Ready to use")
            print(f"   ♿ Type: Urban test scenarios")
            print()
        except Exception as e:
            print(f"   ❌ Error reading test data: {e}")
    
    # Processed FSU Data
    processed_dir = Path("data/processed")
    if processed_dir.exists():
        processed_files = list(processed_dir.glob("fsu_*.geojson"))
        if processed_files:
            print(f"📊 FSU Processed Results (REAL ANALYSIS)")
            for pfile in processed_files:
                file_size = os.path.getsize(pfile) / 1024  # KB
                print(f"   📁 {pfile.name} ({file_size:.1f} KB)")
            print(f"   🎯 Status: ✅ Contains real slope analysis results")
            print(f"   ♿ Contains: Elevation points, slope segments, compliance data")
            print()

def show_immediate_testing_options():
    """Show what you can test right now."""
    print("🚀 Ready to Test RIGHT NOW")
    print("=" * 40)
    
    print("Option 1: 🏫 FSU Campus Analysis (Recommended)")
    print("   1. Make sure app is running: http://localhost:8501")
    print("   2. Upload: data/raw/fsu_paths.geojson")
    print("   3. Need DEM? Create synthetic or download real DEM")
    print("   4. Results: Compare with data/processed/fsu_* files")
    print()
    
    print("Option 2: 🧪 Small Test Scenario")
    print("   1. Upload: data/test/test_paths.geojson")
    print("   2. Create small synthetic DEM for test area")
    print("   3. Quick validation test")
    print()
    
    print("Option 3: 📋 Review Existing Results")
    print("   1. Open: data/processed/fsu_slope_segments.geojson")
    print("   2. Review: outputs/fsu_slope_summary.md") 
    print("   3. Analyze: Real slope compliance data")
    print()

def show_external_data_sources():
    """Show where to get more real data."""
    print("🌍 External Real Data Sources")
    print("=" * 35)
    
    print("University DEMs (High Resolution):")
    print("   🏫 University of Washington: 47.6550, -122.3080")
    print("   🏫 Stanford University: 37.4300, -122.1700") 
    print("   🏫 MIT: 42.3600, -71.0900")
    print("   🔗 USGS 3DEP: https://apps.nationalmap.gov/downloader/")
    print()
    
    print("OpenStreetMap Campus Paths:")
    print("   🗺️  Overpass Turbo: https://overpass-turbo.eu/")
    print("   📝 Query Example: way[highway~'footway|path'][surface]")
    print("   📍 Use university coordinates above")
    print()
    
    print("Municipal Open Data:")
    print("   🌊 Seattle: data.seattle.gov (sidewalks, curb ramps)")
    print("   🌉 San Francisco: data.sfgov.org")
    print("   🗽 NYC: opendata.cityofnewyork.us")
    print("   🌹 Portland: gis-pdx.opendata.arcgis.com")

if __name__ == "__main__":
    print("📋 ADA Slope Compliance Tool - Real Data Guide")
    print("=" * 55)
    print()
    
    # Check what we have locally
    analyze_existing_data()
    
    # Show testing options
    show_immediate_testing_options()
    
    # Show where to get more data
    show_external_data_sources()
    
    print("🎯 BOTTOM LINE: You have FSU campus data (857 real pathways) ready to test!")
    print("   Just need to run the app and upload data/raw/fsu_paths.geojson")
