#!/usr/bin/env python3
"""
Quick test of the backend API functionality using our enhanced processing
"""

import sys
import os
import requests
import json
from pathlib import Path

# Add tests path for conftest
tests_path = Path(__file__).parent / "tests"
sys.path.insert(0, str(tests_path))

try:
    from conftest import geotiff_bytes_from_array
except ImportError:
    print("Note: conftest not available, will skip binary tests")
    geotiff_bytes_from_array = None

import numpy as np


def test_backend_api_locally():
    """Test the FastAPI backend if it's running locally."""
    print("🔌 Testing FastAPI Backend API...")
    
    # Test if backend is running (usually on port 8000)
    backend_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{backend_url}/healthz", timeout=2)
        if response.status_code == 200:
            print(f"✅ Backend health check passed: {response.json()}")
            
            # Test upload with synthetic data
            test_dem_upload(backend_url)
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("ℹ️  Backend API not running on localhost:8000")
        print("   (This is expected - run 'cd backend && uvicorn app.main:app' to start)")
    except Exception as e:
        print(f"❌ Backend test failed: {e}")


def test_dem_upload(backend_url):
    """Test DEM upload functionality."""
    print("\n📤 Testing DEM upload...")
    
    # Create synthetic flat DEM
    flat_dem = np.zeros((20, 20), dtype=np.float32)
    dem_bytes = geotiff_bytes_from_array(flat_dem)
    
    files = {"file": ("test_dem.tif", dem_bytes, "image/tiff")}
    
    try:
        response = requests.post(f"{backend_url}/upload", files=files, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get("job_id")
            print(f"✅ Upload successful! Job ID: {job_id}")
            
            # Test results retrieval
            test_results_retrieval(backend_url, job_id)
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Upload test failed: {e}")


def test_results_retrieval(backend_url, job_id):
    """Test results retrieval."""
    print(f"\n📊 Testing results retrieval for job {job_id}...")
    
    try:
        response = requests.get(f"{backend_url}/results/{job_id}", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Results retrieved successfully!")
            
            # Check result structure
            if "summary" in result and "artifacts" in result:
                summary = result["summary"]
                print(f"   - Total pixels: {summary.get('pixels_total', 'N/A')}")
                print(f"   - Running compliance: {summary.get('pass_running', 'N/A')}")
                print(f"   - Cross compliance: {summary.get('pass_cross', 'N/A')}")
                print("✅ API integration working correctly!")
            else:
                print("❌ Result structure incomplete")
        else:
            print(f"❌ Results retrieval failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Results test failed: {e}")


def main():
    """Run backend API tests."""
    print("🚀 Backend API Functionality Test\n")
    print("=" * 50)
    
    test_backend_api_locally()
    
    print("\n" + "=" * 50)
    print("📝 Backend Testing Notes:")
    print("- To start backend: cd backend && uvicorn app.main:app --reload")
    print("- Backend will run on http://localhost:8000")
    print("- Our enhanced processing uses ada_slope functions")
    print("- Zero code duplication in DEM processing pipeline")


if __name__ == "__main__":
    main()
