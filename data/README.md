# Demo data

This folder holds **small** DEM samples for tests and demos.

## Synthetic (preferred for tests)
Generated using `scripts/fetch_demo_data.py synthetic ...`. Deterministic and license-free.

Examples:
```bash
python scripts/fetch_demo_data.py synthetic --pattern flat --out data/demo/flat_50x50.tif --shape 50 50
python scripts/fetch_demo_data.py synthetic --pattern plane --slope-pct 10 --axis x --out data/demo/plane_10pct_x_128.tif
python scripts/fetch_demo_data.py synthetic --pattern hill --amp 50 --out data/demo/hill_256.tif --shape 256 256
```

## Real-world samples (optional)

If you add a real DEM:

- Keep it small (≤ ~1024×1024).
- Ensure public-domain or properly licensed data and document here.

### Provenance template

**Source:**

**Dataset:**

**License:**

**Date accessed:**

**Spatial reference (CRS), pixel size:**
