"""Test ada_slope core processing functions."""

import numpy as np
import pytest

from ada_slope.core import (
    compute_running_slope,
    compute_cross_slope,
    mask_nodata
)
from ada_slope.io import load_dem_from_bytes


def test_compute_running_slope_flat_surface(flat_dem_bytes):
    """Test running slope computation on flat surface."""
    elevation_data, resx, resy, nodata = load_dem_from_bytes(flat_dem_bytes)
    
    # Compute running slope
    running_slope = compute_running_slope(elevation_data, resx, resy, nodata)
    
    # Flat surface should have near-zero slopes
    assert np.all(np.abs(running_slope) < 0.001)


def test_compute_running_slope_gentle_slope(gentle_slope_dem_bytes):
    """Test running slope computation on 3% slope."""
    elevation_data, resx, resy, nodata = load_dem_from_bytes(gentle_slope_dem_bytes)
    
    # Compute running slope
    running_slope = compute_running_slope(elevation_data, resx, resy, nodata)
    
    # Should be approximately 3% slope
    # Remove edge effects by checking interior
    interior_slopes = running_slope[2:-2, 2:-2]
    mean_slope = np.mean(interior_slopes[~np.isnan(interior_slopes)])
    assert 2.5 < mean_slope < 3.5  # 2.5% to 3.5%


def test_compute_running_slope_steep_slope(steep_slope_dem_bytes):
    """Test running slope computation on 8% slope (non-compliant)."""
    elevation_data, resx, resy, nodata = load_dem_from_bytes(steep_slope_dem_bytes)
    
    # Compute running slope  
    running_slope = compute_running_slope(elevation_data, resx, resy, nodata)
    
    # Should be approximately 8% slope
    interior_slopes = running_slope[2:-2, 2:-2]
    mean_slope = np.mean(interior_slopes[~np.isnan(interior_slopes)])
    assert 7.5 < mean_slope < 8.5  # 7.5% to 8.5%


def test_compute_cross_slope_flat_surface(flat_dem_bytes):
    """Test cross slope computation on flat surface."""
    elevation_data, resx, resy, nodata = load_dem_from_bytes(flat_dem_bytes)
    
    # Compute cross slope
    cross_slope = compute_cross_slope(
        elevation_data, resx, resy, assumed_path_axis="x", nodata=nodata
    )
    
    # Flat surface should have near-zero cross slopes
    assert np.all(np.abs(cross_slope) < 0.001)


def test_mask_nodata_functionality(nodata_dem_bytes):
    """Test nodata masking functionality."""
    elevation_data, resx, resy, nodata = load_dem_from_bytes(nodata_dem_bytes)
    
    # Mask nodata values
    masked_elevation = mask_nodata(elevation_data, nodata)
    
    # Check that nodata values are properly masked
    assert np.isnan(masked_elevation[0, 0])  # Should be NaN where nodata was
    assert np.isnan(masked_elevation[9, 9])  # Should be NaN where nodata was
    assert not np.isnan(masked_elevation[5, 5])  # Should not be NaN for valid data


def test_ada_compliance_thresholds(gentle_slope_dem_bytes, steep_slope_dem_bytes):
    """Test ADA compliance checking against standard thresholds."""
    # Test compliant slope (3%)
    elevation_data, resx, resy, nodata = load_dem_from_bytes(gentle_slope_dem_bytes)
    running_slope = compute_running_slope(elevation_data, resx, resy, nodata)
    
    # Check compliance (5% threshold)
    compliant_pixels = np.abs(running_slope) <= 5.0  # 5% threshold
    compliance_rate = np.sum(compliant_pixels) / np.sum(~np.isnan(running_slope))
    assert compliance_rate > 0.9  # Should be mostly compliant
    
    # Test non-compliant slope (8%)
    elevation_data, resx, resy, nodata = load_dem_from_bytes(steep_slope_dem_bytes)
    running_slope = compute_running_slope(elevation_data, resx, resy, nodata)
    
    # Check compliance (5% threshold)
    compliant_pixels = np.abs(running_slope) <= 5.0  # 5% threshold
    compliance_rate = np.sum(compliant_pixels) / np.sum(~np.isnan(running_slope))
    assert compliance_rate < 0.1  # Should be mostly non-compliant


def test_pixel_spacing_affects_slope_calculation():
    """Test that pixel spacing correctly affects slope calculations."""
    # Create a simple 2x2 elevation array with known slope
    elevation = np.array([[0.0, 1.0], [0.0, 1.0]], dtype=np.float32)
    
    # Test with 1m spacing: slope = 1m rise / 1m run = 100%
    slope_1m = compute_running_slope(elevation, 1.0, 1.0, None)
    
    # Test with 2m spacing: slope = 1m rise / 2m run = 50%  
    slope_2m = compute_running_slope(elevation, 2.0, 2.0, None)
    
    # Slope should be half when pixel spacing is doubled
    # Check the valid (non-edge) values
    valid_1m = slope_1m[~np.isnan(slope_1m)]
    valid_2m = slope_2m[~np.isnan(slope_2m)]
    
    if len(valid_1m) > 0 and len(valid_2m) > 0:
        ratio = valid_2m[0] / valid_1m[0]
        assert 0.45 < ratio < 0.55  # Should be approximately 0.5
