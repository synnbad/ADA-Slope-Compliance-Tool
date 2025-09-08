#!/usr/bin/env python3
"""
Quick script to download additional real-world test data
"""

import requests
import json
from pathlib import Path


def download_seattle_accessibility_data():
    """Download Seattle's real accessibility data."""
    print("🌊 Downloading Seattle Accessibility Data...")
    
    # Seattle Open Data Portal - Sidewalk data
    seattle_urls = {
        "sidewalks": "https://data.seattle.gov/api/geospatial/3vpb-cqnt?method=export&format=GeoJSON",
        "curb_ramps": "https://data.seattle.gov/api/geospatial/qk8d-fzhu?method=export&format=GeoJSON"
    }
    
    for name, url in seattle_urls.items():
        try:
            print(f"   Downloading {name}...")
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                output_file = f"seattle_{name}.geojson"
                with open(output_file, 'w') as f:
                    json.dump(response.json(), f)
                print(f"   ✅ Saved to {output_file}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error downloading {name}: {e}")


def create_overpass_query_examples():
    """Create example Overpass queries for different regions."""
    print("\n🗺️  OpenStreetMap Query Examples...")
    
    queries = {
        "university_of_washington": {
            "bbox": [47.6520, -122.3200, 47.6580, -122.3050],  # lat1, lon1, lat2, lon2
            "query": """
[out:json][timeout:25];
(
  way["highway"~"^(footway|path|cycleway|pedestrian)$"]["surface"](47.6520,-122.3200,47.6580,-122.3050);
  way["area:highway"~"^(footway|path)$"](47.6520,-122.3200,47.6580,-122.3050);
);
out geom;""",
            "description": "University of Washington campus pathways"
        },
        
        "stanford_university": {
            "bbox": [37.4200, -122.1817, 37.4400, -122.1600],
            "query": """
[out:json][timeout:25];
(
  way["highway"~"^(footway|path|cycleway)$"]["wheelchair"="yes"](37.4200,-122.1817,37.4400,-122.1600);
  way["highway"~"^(footway|path)$"]["surface"~"^(concrete|paved|asphalt)$"](37.4200,-122.1817,37.4400,-122.1600);
);
out geom;""",
            "description": "Stanford University ADA-accessible paths"
        },
        
        "mit_campus": {
            "bbox": [42.3580, -71.0950, 42.3640, -71.0850], 
            "query": """
[out:json][timeout:25];
(
  way["highway"~"^(footway|path|pedestrian)$"](42.3580,-71.0950,42.3640,-71.0850);
  way["amenity"="university"](42.3580,-71.0950,42.3640,-71.0850);
);
out geom;""",
            "description": "MIT campus pathways and buildings"
        }
    }
    
    # Save queries to files
    Path("overpass_queries").mkdir(exist_ok=True)
    
    for name, data in queries.items():
        query_file = f"overpass_queries/{name}.overpassql"
        with open(query_file, 'w') as f:
            f.write(data['query'])
        
        print(f"   ✅ {data['description']}")
        print(f"      📁 Query saved: {query_file}")
        print(f"      🔗 Run at: https://overpass-turbo.eu/")
        print(f"      📍 Bbox: {data['bbox']}")
        print()


def suggest_immediate_testing():
    """Suggest what to test right now."""
    print("🚀 Immediate Testing Recommendations")
    print("=" * 50)
    
    print("1. 🏫 FSU Campus (Most Complete Dataset)")
    print("   📁 Use: data/raw/fsu_paths.geojson")
    print("   📊 Contains: 857 real pathways from OpenStreetMap")
    print("   🎯 Test: Large-scale campus analysis")
    print("   ♿ Expected: ~71.6% ADA compliance")
    print()
    
    print("2. 🧪 Synthetic Test DEM")  
    print("   📁 Use: test_dem_3percent.tif (we created this)")
    print("   📊 Contains: 50x50 synthetic DEM with 3% slope")
    print("   🎯 Test: Known compliant scenario")
    print("   ♿ Expected: ~100% ADA compliance")
    print()
    
    print("3. 📐 Manual Test Scenarios")
    print("   • Upload FSU paths + any DEM to test point sampling")
    print("   • Upload synthetic DEM + FSU paths for mixed analysis")
    print("   • Test error handling with invalid files")
    print()
    
    print("🎯 Best First Test:")
    print("   1. Open http://localhost:8501")
    print("   2. Upload data/raw/fsu_paths.geojson as paths")
    print("   3. Upload test_dem_3percent.tif as DEM (or find a real DEM)")
    print("   4. Run analysis and compare with processed results")


if __name__ == "__main__":
    print("🎯 ADA Slope Compliance Tool - Additional Real Data")
    print("=" * 60)
    
    # Try to download Seattle data (example)
    print("Note: Some downloads may require internet connection and may be large files")
    print()
    
    # Create OSM query examples
    create_overpass_query_examples()
    
    # Show immediate testing options
    suggest_immediate_testing()
    
    print("\n✅ Summary: Multiple Real Data Sources Ready")
    print("   • FSU Campus: 857 real pathways (ready to use)")
    print("   • Overpass Queries: 3 university campuses (download needed)")
    print("   • Seattle Open Data: Municipal accessibility data (large download)")
    print("   • USGS DEMs: Any US location (web download)")
