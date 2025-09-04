"""Backward compatibility shim for older imports.

This module re-exports the newer `ada_slope` package symbols so existing scripts
that import `processing_utils` continue to work while the project migrates to
the `ada_slope` package layout.
"""

from ada_slope.core import convert_polygons_to_lines, compute_slope_segments
from ada_slope.io import ensure_vector_matches_raster_crs as align_crs, sample_elevation_at_points

__all__ = [
    "convert_polygons_to_lines",
    "align_crs",
    "sample_elevation_at_points",
    "compute_slope_segments",
]
