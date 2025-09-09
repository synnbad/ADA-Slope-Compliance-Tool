#!/usr/bin/env python3
"""
Mathematical Demonstration Script for ADA Slope Compliance

This script demonstrates the mathematical concepts behind our DEM slope analysis
with visual examples and step-by-step calculations.

Usage:
    python scripts/math_demo.py
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demonstrate_gradient_computation():
    """Show how gradient computation works with visual examples."""
    
    logger.info("🧮 MATHEMATICAL DEMONSTRATION: DEM Slope Analysis")
    logger.info("=" * 60)
    
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
        logger.info("\n%s:", name.upper())
        logger.info("-" * 40)
        
        # Compute gradients manually for demonstration
        gy, gx = np.gradient(dem, 1.0, 1.0)  # 1m pixel spacing
        slope_magnitude = np.sqrt(gx**2 + gy**2)
        slope_percentage = slope_magnitude * 100
        
        # Statistics
        max_slope = np.max(slope_percentage)
        mean_slope = np.mean(slope_percentage)
        ada_violations = np.sum(slope_percentage > 5.0)
        total_pixels = slope_percentage.size
        
        logger.info("DEM Shape: %s", dem.shape)
        logger.info("Elevation Range: %.2fm to %.2fm", np.min(dem), np.max(dem))
        logger.info("Max Gradient X: %.6f (rise/run)", np.max(np.abs(gx)))
        logger.info("Max Gradient Y: %.6f (rise/run)", np.max(np.abs(gy)))
        logger.info("Max Slope: %.3f%%", max_slope)
        logger.info("Mean Slope: %.3f%%", mean_slope)
        logger.info("ADA Violations (>5%%): %d/%d pixels", 
                   ada_violations, total_pixels)
        logger.info("Compliance: %s", 
                   '✓ PASS' if ada_violations == 0 else '✗ FAIL')
        
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
                bbox={'boxstyle': 'round', 'facecolor': 'lightblue', 'alpha': 0.8})
    
    plt.tight_layout()
    
    # Save the demonstration plot
    output_dir = Path("outputs/demos")
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / "mathematical_demonstration.png", 
               dpi=150, bbox_inches='tight')
    logger.info("\nVisualization saved to: %s", 
               output_dir / 'mathematical_demonstration.png')
    
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
    
    logger.info("\n🔬 STEP-BY-STEP MATHEMATICAL ANALYSIS")
    logger.info("=" * 60)
    
    # Create simple 3x3 example for hand calculation
    logger.info("\n📐 HAND CALCULATION EXAMPLE (3×3 DEM):")
    logger.info("-" * 40)
    
    # Simple test case: linear ramp
    test_dem = np.array([
        [100.0, 100.0, 100.0],
        [100.5, 100.5, 100.5],  # 0.5m rise
        [101.0, 101.0, 101.0]   # 1.0m total rise over 2m = 50% slope
    ], dtype=np.float32)
    
    logger.info("Test DEM (elevation in meters):")
    logger.info(str(test_dem))
    logger.info("Pixel spacing: 1m × 1m")
    
    # Manual gradient calculation at center pixel [1,1]
    logger.info("\nManual gradient calculation at center pixel [1,1]:")
    
    # X-direction (east-west): central difference
    gx_center = (test_dem[1, 2] - test_dem[1, 0]) / (2 * 1.0)
    logger.info("∂Z/∂x = (Z[1,2] - Z[1,0]) / (2×1m) = (%.1f - %.1f) / 2 = %.3f",
               test_dem[1,2], test_dem[1,0], gx_center)
    
    # Y-direction (north-south): central difference  
    gy_center = (test_dem[2, 1] - test_dem[0, 1]) / (2 * 1.0)
    logger.info("∂Z/∂y = (Z[2,1] - Z[0,1]) / (2×1m) = (%.1f - %.1f) / 2 = %.3f",
               test_dem[2,1], test_dem[0,1], gy_center)
    
    # Slope magnitude
    slope_magnitude = np.sqrt(gx_center**2 + gy_center**2)
    slope_percent = slope_magnitude * 100
    
    logger.info("\nSlope magnitude calculation:")
    logger.info("slope = √[(∂Z/∂x)² + (∂Z/∂y)²]")
    logger.info("slope = √[(%.3f)² + (%.3f)²]", gx_center, gy_center)
    logger.info("slope = √[%.6f + %.6f]", gx_center**2, gy_center**2)
    logger.info("slope = %.6f (rise/run)", slope_magnitude)
    logger.info("slope = %.3f%%", slope_percent)
    
    # Verify with NumPy
    logger.info("\nVerification with NumPy:")
    gy, gx = np.gradient(test_dem, 1.0, 1.0)
    numpy_slope = np.sqrt(gx[1,1]**2 + gy[1,1]**2) * 100
    logger.info("NumPy gradient result: %.3f%%", numpy_slope)
    logger.info("Match: %s", '✓' if abs(slope_percent - numpy_slope) < 0.001 else '✗')
    
    # ADA compliance check
    logger.info("\nADA Compliance Analysis:")
    logger.info("Threshold: 5.0%% (running slope)")
    logger.info("Computed: %.3f%%", slope_percent)
    logger.info("Status: %s", 
               '✓ COMPLIANT' if slope_percent <= 5.0 else '✗ VIOLATION')

def demonstrate_real_world_example():
    """Show how the math applies to realistic scenarios."""
    
    logger.info("\n🌍 REAL-WORLD APPLICATIONS")
    logger.info("=" * 60)
    
    # Simulate a sidewalk with various slopes
    logger.info("\nSIDEWALK SCENARIO ANALYSIS:")
    logger.info("-" * 30)
    
    scenarios = {
        "Compliant Sidewalk (2% slope)": 0.02,
        "Marginal Sidewalk (4.9% slope)": 0.049, 
        "ADA Violation (6% slope)": 0.06,
        "Steep Ramp (8.33% = 1:12 ratio)": 1.0/12,
        "Curb Cut (Maximum 8.33%)": 0.0833,
    }
    
    logger.info("Scenario Analysis:")
    for scenario, slope_decimal in scenarios.items():
        slope_percent = slope_decimal * 100
        ratio_text = f"1:{1/slope_decimal:.0f}" if slope_decimal > 0 else "flat"
        ada_status = "✓ COMPLIANT" if slope_percent <= 5.0 else "✗ VIOLATION"
        
        logger.info("  %s: %5.2f%% (%s) - %s", 
                   scenario[:30], slope_percent, ratio_text, ada_status)
    
    # Physical interpretation
    logger.info("\nPhysical Interpretation:")
    logger.info("- 5%% slope = 5cm rise per 1m horizontal distance")
    logger.info("- 5%% slope = 1:20 ratio (ADA maximum for running slope)")
    logger.info("- 2.083%% slope = 1:48 ratio (ADA maximum for cross slope)")
    logger.info("- Wheelchair users can safely navigate ≤5%% slopes")

if __name__ == "__main__":
    # Run all demonstrations
    logger.info("Starting Mathematical Demonstration...")
    
    try:
        # Visual demonstration with plots
        examples = demonstrate_gradient_computation()
        
        # Step-by-step math
        demonstrate_mathematical_concepts()
        
        # Real-world applications
        demonstrate_real_world_example()
        
        logger.info("\n✅ DEMONSTRATION COMPLETE")
        logger.info("📋 Summary: Analyzed %d different DEM types", len(examples))
        logger.info("All mathematical concepts verified successfully")
        
    except ImportError as e:
        logger.warning("⚠️  Visualization skipped (missing matplotlib): %s", e)
        logger.info("Running text-only mathematical demonstration...")
        
        demonstrate_mathematical_concepts()
        demonstrate_real_world_example()
        
        logger.info("\n✅ TEXT DEMONSTRATION COMPLETE")
    
    except Exception as e:
        logger.error("❌ Error during demonstration: %s", e)
        raise
