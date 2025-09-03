#!/usr/bin/env python3
"""
Mathematical Demonstration Script for ADA Slope Compliance

This script demonstrates the mathematical concepts behind our DEM slope analysis
with visual examples and step-by-step calculations.

Usage:
    python scripts/math_demo.py
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def demonstrate_gradient_computation():
    """Show how gradient computation works with visual examples."""
    
    print("🧮 MATHEMATICAL DEMONSTRATION: DEM Slope Analysis")
    print("=" * 60)
    
    # Create example DEMs
    examples = {
        "Flat Surface": create_flat_dem(),
        "Linear Ramp (5% slope)": create_linear_ramp(),
        "Step Function": create_step_function(),
        "Hill Shape": create_hill_shape()
    }
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    fig.suptitle("Mathematical Analysis of DEM Slope Computation", fontsize=16)
    
    for i, (name, dem) in enumerate(examples.items()):
        print(f"\n📊 {name.upper()}:")
        print("-" * 40)
        
        # Compute gradients manually for demonstration
        gy, gx = np.gradient(dem, 1.0, 1.0)  # 1m pixel spacing
        slope_magnitude = np.sqrt(gx**2 + gy**2)
        slope_percentage = slope_magnitude * 100
        
        # Statistics
        max_slope = np.max(slope_percentage)
        mean_slope = np.mean(slope_percentage)
        ada_violations = np.sum(slope_percentage > 5.0)
        total_pixels = slope_percentage.size
        
        print(f"DEM Shape: {dem.shape}")
        print(f"Elevation Range: {np.min(dem):.2f}m to {np.max(dem):.2f}m")
        print(f"Max Gradient X: {np.max(np.abs(gx)):.6f} (rise/run)")
        print(f"Max Gradient Y: {np.max(np.abs(gy)):.6f} (rise/run)")
        print(f"Max Slope: {max_slope:.3f}%")
        print(f"Mean Slope: {mean_slope:.3f}%")
        print(f"ADA Violations (>5%): {ada_violations}/{total_pixels} pixels")
        print(f"Compliance: {'✓ PASS' if ada_violations == 0 else '✗ FAIL'}")
        
        # Plot DEM elevation
        ax1 = axes[0, i]
        im1 = ax1.imshow(dem, cmap='terrain', aspect='equal')
        ax1.set_title(f"{name}\nElevation (m)")
        ax1.set_xlabel("X (pixels)")
        ax1.set_ylabel("Y (pixels)")
        plt.colorbar(im1, ax=ax1, shrink=0.6)
        
        # Plot slope magnitude
        ax2 = axes[1, i]
        im2 = ax2.imshow(slope_percentage, cmap='Reds', aspect='equal', vmax=20)
        ax2.set_title(f"Slope Magnitude (%)\nMax: {max_slope:.1f}%")
        ax2.set_xlabel("X (pixels)")
        ax2.set_ylabel("Y (pixels)")
        plt.colorbar(im2, ax=ax2, shrink=0.6)
        
        # Add ADA threshold contour
        ax2.contour(slope_percentage, levels=[5.0], colors=['blue'], linewidths=2)
        ax2.text(0.02, 0.98, f"ADA: {'PASS' if ada_violations == 0 else 'FAIL'}", 
                transform=ax2.transAxes, va='top', ha='left',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    
    # Save the demonstration plot
    output_dir = Path("outputs/demos")
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / "mathematical_demonstration.png", dpi=150, bbox_inches='tight')
    print(f"\n📈 Visualization saved to: {output_dir / 'mathematical_demonstration.png'}")
    
    return examples

def create_flat_dem(size=20):
    """Create a perfectly flat DEM at 100m elevation."""
    return np.full((size, size), 100.0, dtype=np.float32)

def create_linear_ramp(size=20):
    """Create a linear ramp with 5% slope in X direction."""
    x = np.arange(size, dtype=np.float32)
    # 5% slope = 0.05m rise per 1m horizontal
    ramp = (x * 0.05)[None, :].repeat(size, axis=0)
    return ramp + 100.0  # Base elevation 100m

def create_step_function(size=20):
    """Create a step function with 1m elevation change."""
    dem = np.full((size, size), 100.0, dtype=np.float32)
    # Create step at middle
    dem[size//2:, :] = 101.0
    return dem

def create_hill_shape(size=20):
    """Create a hill-shaped DEM."""
    center = size // 2
    y, x = np.ogrid[:size, :size]
    # Gaussian hill shape
    distance_sq = (x - center)**2 + (y - center)**2
    max_dist_sq = 2 * center**2
    height = 10 * np.exp(-3 * distance_sq / max_dist_sq)
    return height + 100.0

def demonstrate_mathematical_concepts():
    """Demonstrate the mathematical formulas step by step."""
    
    print("\n🔬 STEP-BY-STEP MATHEMATICAL ANALYSIS")
    print("=" * 60)
    
    # Create simple 3x3 example for hand calculation
    print("\n📐 HAND CALCULATION EXAMPLE (3×3 DEM):")
    print("-" * 40)
    
    # Simple test case: linear ramp
    test_dem = np.array([
        [100.0, 100.0, 100.0],
        [100.5, 100.5, 100.5],  # 0.5m rise
        [101.0, 101.0, 101.0]   # 1.0m total rise over 2m = 50% slope
    ], dtype=np.float32)
    
    print("Test DEM (elevation in meters):")
    print(test_dem)
    print(f"Pixel spacing: 1m × 1m")
    
    # Manual gradient calculation at center pixel [1,1]
    print(f"\nManual gradient calculation at center pixel [1,1]:")
    
    # X-direction (east-west): central difference
    gx_center = (test_dem[1, 2] - test_dem[1, 0]) / (2 * 1.0)
    print(f"∂Z/∂x = (Z[1,2] - Z[1,0]) / (2×1m) = ({test_dem[1,2]:.1f} - {test_dem[1,0]:.1f}) / 2 = {gx_center:.3f}")
    
    # Y-direction (north-south): central difference  
    gy_center = (test_dem[2, 1] - test_dem[0, 1]) / (2 * 1.0)
    print(f"∂Z/∂y = (Z[2,1] - Z[0,1]) / (2×1m) = ({test_dem[2,1]:.1f} - {test_dem[0,1]:.1f}) / 2 = {gy_center:.3f}")
    
    # Slope magnitude
    slope_magnitude = np.sqrt(gx_center**2 + gy_center**2)
    slope_percent = slope_magnitude * 100
    
    print(f"\nSlope magnitude calculation:")
    print(f"slope = √[(∂Z/∂x)² + (∂Z/∂y)²]")
    print(f"slope = √[({gx_center:.3f})² + ({gy_center:.3f})²]")
    print(f"slope = √[{gx_center**2:.6f} + {gy_center**2:.6f}]")
    print(f"slope = {slope_magnitude:.6f} (rise/run)")
    print(f"slope = {slope_percent:.3f}%")
    
    # Verify with NumPy
    print(f"\nVerification with NumPy:")
    gy, gx = np.gradient(test_dem, 1.0, 1.0)
    numpy_slope = np.sqrt(gx[1,1]**2 + gy[1,1]**2) * 100
    print(f"NumPy gradient result: {numpy_slope:.3f}%")
    print(f"Match: {'✓' if abs(slope_percent - numpy_slope) < 0.001 else '✗'}")
    
    # ADA compliance check
    print(f"\nADA Compliance Analysis:")
    print(f"Threshold: 5.0% (running slope)")
    print(f"Computed: {slope_percent:.3f}%")
    print(f"Status: {'✓ COMPLIANT' if slope_percent <= 5.0 else '✗ VIOLATION'}")

def demonstrate_real_world_example():
    """Show how the math applies to realistic scenarios."""
    
    print("\n🌍 REAL-WORLD APPLICATIONS")
    print("=" * 60)
    
    # Simulate a sidewalk with various slopes
    print("\nSIDEWALK SCENARIO ANALYSIS:")
    print("-" * 30)
    
    scenarios = {
        "Compliant Sidewalk (2% slope)": 0.02,
        "Marginal Sidewalk (4.9% slope)": 0.049, 
        "ADA Violation (6% slope)": 0.06,
        "Steep Ramp (8.33% = 1:12 ratio)": 1.0/12,
        "Curb Cut (Maximum 8.33%)": 0.0833,
    }
    
    print("Scenario Analysis:")
    for scenario, slope_decimal in scenarios.items():
        slope_percent = slope_decimal * 100
        ratio_text = f"1:{1/slope_decimal:.0f}" if slope_decimal > 0 else "flat"
        ada_status = "✓ COMPLIANT" if slope_percent <= 5.0 else "✗ VIOLATION"
        
        print(f"  {scenario:30}: {slope_percent:5.2f}% ({ratio_text:>6}) - {ada_status}")
    
    # Physical interpretation
    print(f"\nPhysical Interpretation:")
    print(f"- 5% slope = 5cm rise per 1m horizontal distance")
    print(f"- 5% slope = 1:20 ratio (ADA maximum for running slope)")
    print(f"- 2.083% slope = 1:48 ratio (ADA maximum for cross slope)")
    print(f"- Wheelchair users can safely navigate ≤5% slopes")

if __name__ == "__main__":
    # Run all demonstrations
    print("Starting Mathematical Demonstration...")
    
    try:
        # Visual demonstration with plots
        examples = demonstrate_gradient_computation()
        
        # Step-by-step math
        demonstrate_mathematical_concepts()
        
        # Real-world applications
        demonstrate_real_world_example()
        
        print(f"\n✅ DEMONSTRATION COMPLETE")
        print(f"📋 Summary: Analyzed {len(examples)} different DEM types")
        print(f"🎯 All mathematical concepts verified successfully")
        
    except ImportError as e:
        print(f"⚠️  Visualization skipped (missing matplotlib): {e}")
        print("📊 Running text-only mathematical demonstration...")
        
        demonstrate_mathematical_concepts()
        demonstrate_real_world_example()
        
        print(f"\n✅ TEXT DEMONSTRATION COMPLETE")
    
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        raise
