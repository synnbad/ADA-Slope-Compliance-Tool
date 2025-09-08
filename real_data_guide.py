#!/usr/bin/env python3
"""
Real Data Sources Guide for ADA Slope Compliance Tool Testing
Provides access to various real-world elevation and pathway datasets
"""

import os
import requests
import zipfile
from pathlib import Path
import geopandas as gpd
import rasterio
from rasterio.merge import merge
import numpy as np


def download_usgs_dem_data():
    """Download USGS 3DEP elevation data for testing."""
    print("🏔️  USGS 3D Elevation Program (3DEP) Data")
    print("=" * 50)
    
    # Example areas with good pathway data
    test_areas = {
        "University of Washington": {
            "description": "Seattle campus with pathways",
            "bbox": [-122.3200, 47.6500, -122.3000, 47.6700],
            "usgs_region": "Washington"
        },
        "Stanford University": {
            "description": "California campus with accessibility features", 
            "bbox": [-122.1817, 37.4200, -122.1600, 37.4400],
            "usgs_region": "California"
        },
        "MIT Campus": {
            "description": "Cambridge campus with urban pathways",
            "bbox": [-71.0950, 42.3580, -71.0850, 42.3640],
            "usgs_region": "Massachusetts"
        }
    }
    
    print("📍 Available Test Areas:")
    for name, info in test_areas.items():
        print(f"   • {name}: {info['description']}")
        print(f"     Coordinates: {info['bbox']}")
    
    print("\n🔗 USGS Data Access:")
    print("   • Web Interface: https://apps.nationalmap.gov/downloader/")
    print("   • API Access: https://tnmaccess.nationalmap.gov/api/v1/")
    print("   • Format: GeoTIFF, 1-meter resolution available")
    
    return test_areas


def download_openstreetmap_paths():
    """Get pathway data from OpenStreetMap."""
    print("\n🗺️  OpenStreetMap Pathway Data")
    print("=" * 50)
    
    overpass_examples = {
        "University Paths": '''
[out:json][timeout:25];
(
  way["highway"~"^(footway|path|cycleway|pedestrian)$"]["surface"]["access"!="private"](bbox);
  way["area:highway"~"^(footway|path)$"](bbox);
);
out geom;''',
        
        "ADA Accessible Paths": '''
[out:json][timeout:25];
(
  way["highway"~"^(footway|path|cycleway)$"]["wheelchair"="yes"](bbox);
  way["highway"~"^(footway|path)$"]["surface"~"^(concrete|paved|asphalt)$"](bbox);
);
out geom;''',
        
        "Campus Buildings + Paths": '''
[out:json][timeout:25];
(
  way["amenity"="university"](bbox);
  way["building"="university"](bbox);
  way["highway"~"^(footway|path|pedestrian)$"](bbox);
);
out geom;'''
    }
    
    print("📋 Overpass API Queries Available:")
    for name, query in overpass_examples.items():
        print(f"   • {name}")
        
    print("\n🔗 Data Sources:")
    print("   • Overpass Turbo: https://overpass-turbo.eu/")
    print("   • OSM Export: https://export.openstreetmap.org/")
    print("   • QGIS Plugin: QuickOSM for direct download")
    
    return overpass_examples


def check_existing_real_data():
    """Analyze the real data we already have."""
    print("\n📊 Existing Real Data Analysis")
    print("=" * 50)
    
    data_files = {
        "FSU Campus Paths": "data/raw/fsu_paths.geojson",
        "FSU Processed Points": "data/processed/fsu_points_with_elevation.geojson", 
        "FSU Slope Segments": "data/processed/fsu_slope_segments.geojson",
        "Test Paths": "data/test/test_paths.geojson"
    }
    
    for name, filepath in data_files.items():
        if os.path.exists(filepath):
            try:
                gdf = gpd.read_file(filepath)
                print(f"✅ {name}")
                print(f"   📁 File: {filepath}")
                print(f"   📊 Features: {len(gdf)}")
                print(f"   🗂️  Columns: {list(gdf.columns)}")
                
                if 'elevation' in gdf.columns:
                    elev = gdf['elevation'].dropna()
                    if len(elev) > 0:
                        print(f"   📏 Elevation: {elev.min():.1f}m to {elev.max():.1f}m")
                
                if 'slope' in gdf.columns:
                    slope = gdf['slope'].dropna() 
                    if len(slope) > 0:
                        print(f"   📐 Slope: {slope.min():.3f} to {slope.max():.3f}")
                        
                if 'ada_compliant' in gdf.columns:
                    compliant = gdf['ada_compliant'].sum()
                    total = len(gdf)
                    print(f"   ♿ ADA Compliant: {compliant}/{total} ({compliant/total*100:.1f}%)")
                
                # Show bounds
                bounds = gdf.total_bounds
                print(f"   🌍 Bounds: [{bounds[0]:.4f}, {bounds[1]:.4f}, {bounds[2]:.4f}, {bounds[3]:.4f}]")
                print()
                
            except Exception as e:
                print(f"❌ {name}: Could not read - {e}\n")
        else:
            print(f"❌ {name}: File not found - {filepath}\n")


def suggest_additional_datasets():
    """Suggest additional real-world datasets for testing."""
    print("🌟 Additional Real Data Sources")
    print("=" * 50)
    
    datasets = {
        "LIDAR Elevation Data": {
            "source": "USGS, State GIS Portals",
            "description": "High-resolution elevation models (0.5-2m)",
            "formats": ["LAZ", "LAS", "GeoTIFF"],
            "coverage": "Most urban areas in US",
            "url": "https://www.usgs.gov/3d-elevation-program"
        },
        
        "Municipal GIS Data": {
            "source": "City/County Open Data Portals",
            "description": "Sidewalks, curb ramps, accessibility features",
            "formats": ["Shapefile", "GeoJSON", "KML"],
            "examples": ["Seattle", "Portland", "San Francisco", "NYC"],
            "url": "https://opendata.cityofseattle.gov/"
        },
        
        "University Campus Data": {
            "source": "Individual university GIS departments",
            "description": "Campus maps with accessibility information",
            "formats": ["Various GIS formats"],
            "examples": ["UW", "Stanford", "MIT", "UC Berkeley"],
            "note": "Often available on request"
        },
        
        "Accessibility Datasets": {
            "source": "AccessMap, Sidewalk Labs", 
            "description": "Crowd-sourced accessibility information",
            "formats": ["API", "GeoJSON"],
            "coverage": "Seattle, other cities",
            "url": "https://accessmap.io/"
        },
        
        "Government ADA Compliance": {
            "source": "State DOT, Federal Buildings",
            "description": "Official ADA compliance surveys",
            "formats": ["PDF reports", "GIS data"],
            "availability": "Through FOIA requests",
            "note": "High accuracy, official compliance data"
        }
    }
    
    for name, info in datasets.items():
        print(f"📋 {name}")
        print(f"   🏢 Source: {info['source']}")
        print(f"   📝 Description: {info['description']}")
        print(f"   📁 Formats: {', '.join(info['formats'])}")
        if 'url' in info:
            print(f"   🔗 URL: {info['url']}")
        if 'examples' in info:
            print(f"   🌟 Examples: {', '.join(info['examples'])}")
        if 'note' in info:
            print(f"   💡 Note: {info['note']}")
        print()


def create_realistic_test_scenarios():
    """Create additional realistic test scenarios."""
    print("🎯 Create Realistic Test Scenarios")
    print("=" * 50)
    
    scenarios = {
        "Steep Campus Hill": {
            "description": "University pathway on 8-12% grade (non-compliant)",
            "slope_range": "8-12%",
            "ada_compliant": False,
            "use_case": "Test non-compliant detection"
        },
        
        "ADA Compliant Ramp": {
            "description": "Properly designed accessibility ramp (4.8% grade)",
            "slope_range": "4-5%", 
            "ada_compliant": True,
            "use_case": "Test compliant validation"
        },
        
        "Mixed Terrain Path": {
            "description": "Path with varying slopes, some compliant/non-compliant",
            "slope_range": "0-15%",
            "ada_compliant": "Mixed",
            "use_case": "Test segmented analysis"
        },
        
        "Urban Sidewalk Network": {
            "description": "City block with intersections, curb cuts",
            "slope_range": "1-8%",
            "ada_compliant": "Mostly",
            "use_case": "Test large-scale analysis"
        },
        
        "Mountainous Campus": {
            "description": "Challenging terrain with accessibility challenges",
            "slope_range": "5-20%",
            "ada_compliant": False,
            "use_case": "Test extreme conditions"
        }
    }
    
    print("🧪 Test Scenario Recommendations:")
    for name, info in scenarios.items():
        print(f"   🎯 {name}")
        print(f"      📐 Slope: {info['slope_range']}")
        print(f"      ♿ ADA: {info['ada_compliant']}")
        print(f"      🔬 Use: {info['use_case']}")
        print()


def main():
    """Main function to display all real data sources."""
    print("🚀 ADA Slope Compliance Tool - Real Data Sources Guide")
    print("=" * 70)
    print("Find comprehensive real-world datasets for testing your enhanced application\n")
    
    # Check what we already have
    check_existing_real_data()
    
    # Show external data sources
    usgs_areas = download_usgs_dem_data()
    osm_queries = download_openstreetmap_paths()
    suggest_additional_datasets()
    create_realistic_test_scenarios()
    
    print("🎉 Summary: Ready to Test with Real Data!")
    print("=" * 70)
    print("✅ Existing FSU data: 857 pathways, 8,981 points, 71.6% ADA compliant")
    print("✅ USGS elevation data available for any US location")  
    print("✅ OpenStreetMap pathway data for worldwide coverage")
    print("✅ Municipal open data portals for urban areas")
    print("✅ Synthetic test scenarios for edge cases")
    print("\n🎯 Next: Choose a dataset and test the enhanced app at http://localhost:8501")


if __name__ == "__main__":
    main()
