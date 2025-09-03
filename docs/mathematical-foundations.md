# Mathematical Foundations of ADA Slope Compliance Analysis

## 🧮 Core Mathematical Concepts

### 1. Digital Elevation Model (DEM) Representation

A DEM is a 2D grid of elevation values `Z(x, y)` where:
- `x, y` are spatial coordinates (typically in meters)
- `Z` is elevation above a reference datum (typically meters above sea level)
- Each grid cell represents a square area with resolution `resx × resy`

```
DEM Grid Example (4x4):
Z = [[ 100.0, 100.5, 101.0, 101.5],
     [ 100.2, 100.8, 101.3, 101.8],
     [ 100.4, 101.0, 101.6, 102.1],
     [ 100.6, 101.2, 101.8, 102.4]]
```

### 2. Gradient Computation Using Finite Differences

Our system uses NumPy's `gradient` function, which implements **central finite differences**:

#### Horizontal Gradient (∂Z/∂x):
```
∂Z/∂x ≈ [Z(x+Δx, y) - Z(x-Δx, y)] / (2 × Δx)
```

#### Vertical Gradient (∂Z/∂y):
```
∂Z/∂y ≈ [Z(x, y+Δy) - Z(x, y-Δy)] / (2 × Δy)
```

Where:
- `Δx = resx` (pixel resolution in X direction)
- `Δy = resy` (pixel resolution in Y direction)

### 3. Slope Magnitude Calculation

The **slope magnitude** represents the steepest rate of elevation change at each point:

```python
slope_magnitude = √[(∂Z/∂x)² + (∂Z/∂y)²]
```

This gives us the **rise/run ratio** (dimensionless).

#### Mathematical Proof:
If we consider a 3D surface Z(x,y), the gradient vector is:
```
∇Z = (∂Z/∂x, ∂Z/∂y)
```

The magnitude of this vector represents the maximum rate of change:
```
|∇Z| = √[(∂Z/∂x)² + (∂Z/∂y)²]
```

This is the **slope in decimal form** (e.g., 0.05 = 5%).

### 4. ADA Compliance Mathematics

#### Running Slope (Longitudinal):
- **ADA Standard**: Maximum 5% (1:20 ratio)
- **Mathematical threshold**: `slope_magnitude ≤ 0.05`
- **Physical meaning**: For every 20 units horizontal, elevation changes ≤ 1 unit

#### Cross Slope (Transverse):
- **ADA Standard**: Maximum 2% (1:50 ratio), but we use 2.083% (1:48)
- **Mathematical threshold**: `slope_magnitude ≤ 0.02083`
- **Physical meaning**: For every 48 units horizontal, elevation changes ≤ 1 unit

## 🔬 Implementation Deep Dive

### Code Analysis from `backend/app/processing.py`:

```python
def process_dem_in_memory(geotiff_bytes, running_slope_max=0.05, cross_slope_max=0.02083):
    with MemoryFile(geotiff_bytes) as memfile:
        with memfile.open() as src:
            dem = src.read(1).astype("float32")
            
            # Handle nodata values
            if src.nodata is not None:
                dem[dem == src.nodata] = np.nan
            
            # Get pixel spacing
            resx, resy = src.res  # (x_size, y_size) in map units
            
            # Compute gradients with proper spacing
            gy, gx = np.gradient(dem, resy, resx)  # dz/dy, dz/dx
            
            # Slope magnitude (rise/run)
            slope = np.sqrt(gx**2 + gy**2)
            slope_pct = slope * 100.0  # Convert to percentage
```

### Mathematical Steps Breakdown:

1. **Gradient Computation**:
   ```python
   gy, gx = np.gradient(dem, resy, resx)
   ```
   - `gx` = ∂Z/∂x (east-west gradient)
   - `gy` = ∂Z/∂y (north-south gradient)
   - Units: elevation_units/distance_units (typically m/m)

2. **Slope Magnitude**:
   ```python
   slope = np.sqrt(gx**2 + gy**2)
   ```
   - Euclidean norm of gradient vector
   - Represents steepest slope direction
   - Units: dimensionless (rise/run)

3. **Percentage Conversion**:
   ```python
   slope_pct = slope * 100.0
   ```
   - 0.05 → 5%
   - 0.02083 → 2.083%

## 📊 Statistical Analysis

### Compliance Metrics:

```python
# Valid pixels (excluding nodata/NaN)
valid = np.isfinite(slope_pct)
total = int(valid.sum())

# Violation detection
over_mask = (slope_pct > (running_slope_max * 100.0)) & valid
violations = int(over_mask.sum())

# Statistics
pct_violating = (violations / total) * 100.0
max_slope = np.nanmax(slope_pct)
mean_slope = np.nanmean(slope_pct)
```

### Histogram Generation:
```python
# 10-bin histogram from 0 to max_slope
hist_max = max(10.0, max_slope)
hist, _ = np.histogram(slope_pct[valid], bins=10, range=(0, hist_max))
```

## 🎯 Real-World Example

Let's trace through a simple 3x3 DEM:

```python
DEM = [[100.0, 100.0, 100.0],    # Flat top
       [100.5, 100.5, 100.5],    # Small step
       [102.0, 102.0, 102.0]]    # Large step

# With 1m resolution:
resx = resy = 1.0

# Gradients at center pixel (1,1):
gx = (100.5 - 100.5) / (2 × 1) = 0.0        # No east-west change
gy = (102.0 - 100.0) / (2 × 1) = 1.0        # 1m rise per 1m run

# Slope magnitude:
slope = √(0.0² + 1.0²) = 1.0 = 100%

# ADA Compliance:
100% > 5% → VIOLATION
```

## 🔍 Accuracy Considerations

### 1. Finite Difference Accuracy:
- **Central differences** are more accurate than forward/backward
- **Error order**: O(Δx²) for smooth surfaces
- **Edge effects**: Handled by NumPy using forward/backward differences at boundaries

### 2. Pixel Resolution Impact:
```
slope_error ≈ elevation_error / pixel_resolution
```
- Higher resolution → more accurate slope estimates
- Sub-pixel features may be missed

### 3. Coordinate System:
- **Geographic CRS** (lat/lon): Non-uniform pixel spacing, requires projection
- **Projected CRS** (UTM, etc.): Uniform spacing, direct calculation
- Our system assumes **projected coordinates** for accuracy

## 📈 Validation Against Test Cases

### Test Case 1: Flat DEM
```python
# 50x50 flat surface at 100m elevation
dem = np.zeros((50, 50)) + 100.0
# Expected: slope = 0%, violations = 0
```

### Test Case 2: Steep Plane
```python
# 10% slope in X direction
x = np.arange(50)
dem = (x * 0.1)[None, :].repeat(50, axis=0)
# Expected: slope = 10%, violations = 100% (all pixels)
```

### Mathematical Verification:
For a plane with slope `s` in X direction:
- `∂Z/∂x = s`
- `∂Z/∂y = 0`
- `slope_magnitude = √(s² + 0²) = s`
- For s = 0.1 → 10% slope ✓

## 🎨 Advanced Topics

### 1. Directional Slope Analysis (Future):
```python
# Slope in specific direction (azimuth θ)
slope_direction = gx * cos(θ) + gy * sin(θ)
```

### 2. Curvature Analysis (Future):
```python
# Second derivatives for curvature
∂²Z/∂x² = second_gradient(dem, axis=1)
∂²Z/∂y² = second_gradient(dem, axis=0)
```

### 3. Multi-scale Analysis (Future):
```python
# Different window sizes for local vs regional slopes
slope_local = compute_slope(dem, window=3x3)
slope_regional = compute_slope(dem, window=9x9)
```

This mathematical foundation ensures our ADA compliance analysis is:
- ✅ **Mathematically rigorous**: Based on established gradient computation
- ✅ **ADA compliant**: Uses correct 5% and 2.083% thresholds
- ✅ **Spatially accurate**: Accounts for pixel spacing and coordinate systems
- ✅ **Statistically robust**: Proper handling of nodata and edge cases

## 💻 Pseudocode Translation

### High-Level Algorithm:
```
ALGORITHM: ADA_Slope_Compliance_Analysis

INPUT: 
    - DEM_file: GeoTIFF digital elevation model
    - running_threshold: maximum allowed running slope (default 0.05 = 5%)
    - cross_threshold: maximum allowed cross slope (default 0.02083 = 2.083%)

OUTPUT:
    - compliance_report: statistics and violations summary
    - slope_histogram: distribution of slope values

BEGIN
    1. LOAD DEM from GeoTIFF file
    2. EXTRACT elevation_grid, pixel_resolution_x, pixel_resolution_y
    3. HANDLE nodata_values by marking as NaN
    4. COMPUTE spatial_gradients using finite differences
    5. CALCULATE slope_magnitude from gradient components
    6. CONVERT slopes to percentage values
    7. IDENTIFY pixels exceeding ADA thresholds
    8. COMPUTE compliance statistics
    9. GENERATE slope histogram
    10. RETURN compliance_report and histogram
END
```

### Detailed Pseudocode:

```
PROCEDURE: Compute_DEM_Slope_Compliance(elevation_grid, resx, resy, threshold)

BEGIN
    // Step 1: Preprocess elevation data
    FOR each pixel (i,j) in elevation_grid DO
        IF elevation_grid[i,j] == nodata_value THEN
            elevation_grid[i,j] = NaN
        END IF
    END FOR
    
    // Step 2: Compute spatial gradients using central differences
    gradient_x = EMPTY_GRID(same_size_as_elevation_grid)
    gradient_y = EMPTY_GRID(same_size_as_elevation_grid)
    
    FOR i = 1 TO height-2 DO
        FOR j = 1 TO width-2 DO
            // Central difference for interior points
            gradient_x[i,j] = (elevation_grid[i, j+1] - elevation_grid[i, j-1]) / (2 * resx)
            gradient_y[i,j] = (elevation_grid[i+1, j] - elevation_grid[i-1, j]) / (2 * resy)
        END FOR
    END FOR
    
    // Handle boundary conditions with forward/backward differences
    HANDLE_BOUNDARY_GRADIENTS(gradient_x, gradient_y, elevation_grid, resx, resy)
    
    // Step 3: Compute slope magnitude
    slope_magnitude = EMPTY_GRID(same_size_as_elevation_grid)
    FOR each pixel (i,j) DO
        slope_magnitude[i,j] = SQRT(gradient_x[i,j]^2 + gradient_y[i,j]^2)
    END FOR
    
    // Step 4: Convert to percentage and analyze compliance
    slope_percentage = slope_magnitude * 100
    valid_pixels = COUNT_FINITE_VALUES(slope_percentage)
    violating_pixels = COUNT_WHERE(slope_percentage > threshold * 100 AND is_finite)
    
    // Step 5: Compute statistics
    max_slope = MAX(slope_percentage, ignore_nan=True)
    mean_slope = MEAN(slope_percentage, ignore_nan=True)
    violation_percentage = (violating_pixels / valid_pixels) * 100
    
    // Step 6: Generate histogram
    histogram = COMPUTE_HISTOGRAM(slope_percentage, bins=10, range=[0, max_slope])
    
    RETURN {
        pixels_total: valid_pixels,
        pixels_violating: violating_pixels,
        percent_violating: violation_percentage,
        max_slope_pct: max_slope,
        mean_slope_pct: mean_slope,
        histogram: histogram,
        pass: violating_pixels == 0
    }
END
```

## 🐍 Readable Python Implementation

### Complete Annotated Implementation:

```python
import numpy as np
from rasterio.io import MemoryFile

def analyze_ada_slope_compliance(geotiff_bytes, running_threshold=0.05):
    """
    Analyze DEM for ADA slope compliance using mathematical gradient computation.
    
    Parameters:
    -----------
    geotiff_bytes : bytes
        Raw GeoTIFF file data containing elevation model
    running_threshold : float
        Maximum allowed slope as decimal (0.05 = 5%)
    
    Returns:
    --------
    dict : Compliance analysis results
    """
    
    # === STEP 1: Load and Preprocess DEM ===
    with MemoryFile(geotiff_bytes) as memory_file:
        with memory_file.open() as raster_dataset:
            
            # Read elevation data as 2D array
            elevation_grid = raster_dataset.read(1).astype("float32")
            print(f"DEM dimensions: {elevation_grid.shape}")
            
            # Handle missing/invalid data
            if raster_dataset.nodata is not None:
                nodata_mask = (elevation_grid == raster_dataset.nodata)
                elevation_grid[nodata_mask] = np.nan
                print(f"Masked {nodata_mask.sum()} nodata pixels")
            
            # Extract pixel spacing (resolution)
            pixel_width, pixel_height = raster_dataset.res
            print(f"Pixel resolution: {pixel_width}m × {pixel_height}m")
    
    # === STEP 2: Compute Spatial Gradients ===
    # Mathematical: ∂Z/∂x and ∂Z/∂y using central finite differences
    
    # NumPy gradient computes: [Z(i,j+1) - Z(i,j-1)] / (2 * spacing)
    gradient_y, gradient_x = np.gradient(elevation_grid, pixel_height, pixel_width)
    
    print("Gradient computation:")
    print(f"  - X-direction (east-west): {gradient_x.shape}")
    print(f"  - Y-direction (north-south): {gradient_y.shape}")
    print(f"  - Max gradient_x: {np.nanmax(np.abs(gradient_x)):.6f}")
    print(f"  - Max gradient_y: {np.nanmax(np.abs(gradient_y)):.6f}")
    
    # === STEP 3: Calculate Slope Magnitude ===
    # Mathematical: slope = √[(∂Z/∂x)² + (∂Z/∂y)²]
    
    slope_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
    slope_percentage = slope_magnitude * 100.0
    
    print(f"Slope computation:")
    print(f"  - Slope range: {np.nanmin(slope_percentage):.3f}% to {np.nanmax(slope_percentage):.3f}%")
    
    # === STEP 4: Identify Valid Pixels ===
    # Exclude NaN values from analysis
    
    valid_pixel_mask = np.isfinite(slope_percentage)
    total_valid_pixels = int(valid_pixel_mask.sum())
    
    if total_valid_pixels == 0:
        raise ValueError("No valid elevation data found in DEM")
    
    print(f"Valid pixels for analysis: {total_valid_pixels}")
    
    # === STEP 5: ADA Compliance Analysis ===
    threshold_percentage = running_threshold * 100.0
    
    # Find pixels exceeding ADA threshold
    violation_mask = (slope_percentage > threshold_percentage) & valid_pixel_mask
    violating_pixels = int(violation_mask.sum())
    
    # Calculate compliance statistics
    violation_percentage = (violating_pixels / total_valid_pixels) * 100.0
    max_slope = float(np.nanmax(slope_percentage))
    mean_slope = float(np.nanmean(slope_percentage))
    
    print(f"ADA Compliance Analysis:")
    print(f"  - Threshold: {threshold_percentage}%")
    print(f"  - Violating pixels: {violating_pixels}/{total_valid_pixels}")
    print(f"  - Violation rate: {violation_percentage:.2f}%")
    print(f"  - Max slope found: {max_slope:.3f}%")
    print(f"  - Mean slope: {mean_slope:.3f}%")
    
    # === STEP 6: Generate Slope Distribution ===
    # Create histogram for slope analysis
    
    histogram_max = max(10.0, max_slope)  # Ensure reasonable histogram range
    valid_slopes = slope_percentage[valid_pixel_mask]
    
    histogram_counts, bin_edges = np.histogram(
        valid_slopes, 
        bins=10, 
        range=(0, histogram_max)
    )
    
    print(f"Slope distribution (10 bins from 0% to {histogram_max:.1f}%):")
    for i, count in enumerate(histogram_counts):
        bin_start = bin_edges[i]
        bin_end = bin_edges[i+1]
        print(f"  {bin_start:.1f}%-{bin_end:.1f}%: {count} pixels")
    
    # === STEP 7: Compile Results ===
    compliance_results = {
        "summary": {
            "running_slope_threshold_pct": round(threshold_percentage, 3),
            "cross_slope_threshold_pct": round(0.02083 * 100, 3),  # Future use
            "pixels_total": total_valid_pixels,
            "pixels_violating": violating_pixels,
            "percent_violating": round(violation_percentage, 3),
            "max_slope_pct": round(max_slope, 3),
            "mean_slope_pct": round(mean_slope, 3),
            "pass": violating_pixels == 0,
        },
        "artifacts": {
            "histogram": histogram_counts.astype(int).tolist(),
            "bin_edges": bin_edges.tolist(),
        },
        "debug_info": {
            "dem_shape": elevation_grid.shape,
            "pixel_resolution": [pixel_width, pixel_height],
            "gradient_ranges": {
                "x": [float(np.nanmin(gradient_x)), float(np.nanmax(gradient_x))],
                "y": [float(np.nanmin(gradient_y)), float(np.nanmax(gradient_y))]
            }
        }
    }
    
    return compliance_results

# === USAGE EXAMPLE ===
if __name__ == "__main__":
    # Example: Load and analyze a DEM file
    with open("path/to/your/dem.tif", "rb") as file:
        dem_bytes = file.read()
    
    # Analyze with 5% ADA threshold
    results = analyze_ada_slope_compliance(dem_bytes, running_threshold=0.05)
    
    # Print compliance summary
    summary = results["summary"]
    print(f"\n=== ADA COMPLIANCE REPORT ===")
    print(f"Total area analyzed: {summary['pixels_total']} pixels")
    print(f"ADA compliant: {'✓' if summary['pass'] else '✗'}")
    print(f"Violation rate: {summary['percent_violating']}%")
    print(f"Steepest slope: {summary['max_slope_pct']}%")
```

## 🧪 Step-by-Step Mathematical Verification

### Verification Script:

```python
def verify_gradient_computation():
    """
    Verify our gradient computation with known mathematical examples.
    """
    import numpy as np
    
    print("=== MATHEMATICAL VERIFICATION ===\n")
    
    # Test Case 1: Flat surface (should have zero slope)
    print("1. FLAT SURFACE TEST:")
    flat_dem = np.full((5, 5), 100.0)  # 5x5 grid, all 100m elevation
    gy, gx = np.gradient(flat_dem, 1.0, 1.0)  # 1m resolution
    slope = np.sqrt(gx**2 + gy**2)
    print(f"   DEM: All pixels at 100m elevation")
    print(f"   Expected slope: 0%")
    print(f"   Computed slope: {np.max(slope)*100:.6f}%")
    print(f"   ✓ PASS" if np.allclose(slope, 0) else "   ✗ FAIL")
    
    # Test Case 2: Linear ramp (known slope)
    print("\n2. LINEAR RAMP TEST:")
    x_coords = np.arange(10)  # 0 to 9
    linear_dem = x_coords[None, :] * 0.05  # 5cm rise per meter = 5% slope
    linear_dem = np.repeat(linear_dem, 5, axis=0)  # Repeat for 5 rows
    
    gy, gx = np.gradient(linear_dem, 1.0, 1.0)
    slope = np.sqrt(gx**2 + gy**2)
    
    print(f"   DEM: Linear ramp, 5cm rise per 1m horizontal")
    print(f"   Expected slope: 5.0%")
    print(f"   Computed slope: {np.mean(slope[1:-1, 1:-1])*100:.3f}% (excluding edges)")
    print(f"   ✓ PASS" if abs(np.mean(slope[1:-1, 1:-1]) - 0.05) < 0.001 else "   ✗ FAIL")
    
    # Test Case 3: Step function (discontinuous)
    print("\n3. STEP FUNCTION TEST:")
    step_dem = np.array([
        [100, 100, 100],
        [100, 100, 100], 
        [101, 101, 101]  # 1m step up
    ], dtype=float)
    
    gy, gx = np.gradient(step_dem, 1.0, 1.0)
    slope = np.sqrt(gx**2 + gy**2)
    center_slope = slope[1, 1]  # Center pixel
    
    print(f"   DEM: 1m vertical step over 2m horizontal distance")
    print(f"   Expected slope at center: ~50% (1m rise over ~2m)")
    print(f"   Computed slope at center: {center_slope*100:.1f}%")
    print(f"   ✓ Reasonable approximation for discrete step")

# Run verification
verify_gradient_computation()
```

## 🔄 Algorithm Complexity Analysis

```python
def complexity_analysis():
    """
    Analyze computational complexity of our slope analysis.
    """
    print("=== COMPUTATIONAL COMPLEXITY ===\n")
    
    # Spatial complexity: O(n*m) where n,m are DEM dimensions
    # Time complexity breakdown:
    complexities = {
        "DEM Loading": "O(n×m)",
        "Nodata Masking": "O(n×m)", 
        "Gradient Computation": "O(n×m)",
        "Slope Magnitude": "O(n×m)",
        "Threshold Analysis": "O(n×m)",
        "Statistics": "O(n×m)",
        "Histogram": "O(n×m + k log k)", # k = histogram bins
    }
    
    print("Time Complexity by Operation:")
    for operation, complexity in complexities.items():
        print(f"  {operation:20}: {complexity}")
    
    print(f"\nOverall: O(n×m) - Linear in number of DEM pixels")
    print(f"Memory: O(n×m) - Store gradients + slope arrays")
    
    # Performance estimates
    test_sizes = [(100, 100), (1000, 1000), (5000, 5000), (10000, 10000)]
    print(f"\nEstimated Performance (single-threaded):")
    for height, width in test_sizes:
        pixels = height * width
        # Rough estimate: ~100ns per pixel for all operations
        time_estimate = pixels * 100e-9  # 100 nanoseconds per pixel
        memory_mb = pixels * 4 * 4 / 1024**2  # 4 arrays × 4 bytes/float32
        print(f"  {width:5d}×{height:<5d} ({pixels:8d} pixels): ~{time_estimate:.3f}s, ~{memory_mb:.1f}MB")

complexity_analysis()
```

This comprehensive breakdown shows how our mathematical concepts translate into practical, readable code that maintains mathematical rigor while being computationally efficient and easy to understand.
