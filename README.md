# ADA Slope Compliance Tool

This repository evaluates pedestrian paths against a Digital Elevation Model (DEM) for **running** (≤ 5%) and **cross-slope** (≤ 2.083%) compliance, then renders results in a web map. No server infrastructure required.

## Quickstart

**Important**: DEM must be projected in meters; if your DEM is EPSG:4326 or in degrees, reproject first with `gdalwarp` or QGIS.

1) Put your DEM at `data/dem.tif` (**projected CRS in meters**).
2) Create a venv and install deps:
```bash
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
```

3. Fetch OSM pedestrian paths for a bbox (edit coordinates as needed):
```bash
python scripts/fetch_paths.py --bbox -84.30 30.43 -84.28 30.46 --out data/paths_osm.geojson
```

4. Evaluate ADA compliance:
```bash
python scripts/eval_ada.py --dem data/dem.tif --paths data/paths_osm.geojson --out outputs/paths_ada_eval.geojson
```

5. View locally:
```bash
cp outputs/paths_ada_eval.geojson web/
cd web && python -m http.server 8080
# open http://localhost:8080
```

## What it does

* **Paths (UrbanAccess)**: pulls pedestrian edges from OSM for a bounding box.
* **Slope**: computes via `np.gradient` using DEM pixel spacing.
* **Aspect**: downslope azimuth from DEM.
* **Cross-slope**: `cross = slope_pct * |sin(aspect_deg - bearing_deg)|`.
* **Outputs**: `outputs/paths_ada_eval.geojson` with `running_max`, `cross_max`, `running_ok`, `cross_ok`.

## Notes & Assumptions

* DEM CRS must be projected (meters). Reproject if needed in QGIS or `gdalwarp`.
* Densification interval default is 2 m; adjust `--interval-m`.
* Thresholds: running `--running-thr 5.0`, cross `--cross-thr 2.083`.

## Optional: Host on S3 (static)

```bash
aws s3 mb s3://<your-bucket>
aws s3 website s3://<your-bucket> --index-document index.html
aws s3 sync web/ s3://<your-bucket> --acl public-read
```

## License

MIT

## Performance

- Processing time: 1-2 seconds for typical DEMs
- Memory usage: Minimal Python environment
- File support: GeoTIFF format
- Scalability: Local processing, no server dependencies

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add feature description'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

