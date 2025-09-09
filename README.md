# ADA Slope Compliance Tool

Evaluates pedestrian paths against Digital Elevation Models (DEMs) for ADA compliance regarding running slope (≤ 5%) and cross-slope (≤ 2.083%) requirements. Outputs results as an interactive web map.

## Requirements

- DEM must be in projected coordinate system (meters)
- If DEM uses geographic coordinates (EPSG:4326), reproject using `gdalwarp` or QGIS
- Python 3.8+

## Installation

1. Place your DEM at `data/dem.tif` (projected CRS in meters)
2. Set up Python environment:
```bash
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
```

## Usage

1. Fetch pedestrian paths from OpenStreetMap:
```bash
python scripts/fetch_paths.py --bbox -84.30 30.43 -84.28 30.46 --out data/paths_osm.geojson
```

2. Evaluate ADA compliance:
```bash
python scripts/eval_ada.py --dem data/dem.tif --paths data/paths_osm.geojson --out outputs/paths_ada_eval.geojson
```

3. View results:
```bash
cp outputs/paths_ada_eval.geojson web/
cd web && python -m http.server 8080
# Navigate to http://localhost:8080
```

## Methodology

- **Path Extraction**: Retrieves pedestrian paths from OpenStreetMap using UrbanAccess
- **Slope Calculation**: Computes gradients using `numpy.gradient` with DEM pixel spacing
- **Aspect Computation**: Determines downslope azimuth from elevation data
- **Cross-slope Analysis**: Calculates `cross_slope = slope_percentage × |sin(aspect - bearing)|`
- **Output Format**: GeoJSON with `running_max`, `cross_max`, `running_ok`, `cross_ok` attributes

## Configuration

- **Coordinate System**: DEM must use projected coordinates in meters
- **Sampling Interval**: Default 2m spacing; modify with `--interval-m`
- **Compliance Thresholds**: 
  - Running slope: 5.0% (adjustable with `--running-thr`)
  - Cross slope: 2.083% (adjustable with `--cross-thr`)

## Deployment

For static web hosting:
```bash
aws s3 mb s3://your-bucket-name
aws s3 website s3://your-bucket-name --index-document index.html
aws s3 sync web/ s3://your-bucket-name --acl public-read
```

## Performance

- **Processing Time**: 1-2 seconds for standard DEMs
- **Memory Requirements**: Standard Python environment
- **File Support**: GeoTIFF format
- **Architecture**: Local processing, no server infrastructure

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/description`)
3. Commit changes (`git commit -m 'Add feature description'`)
4. Push to branch (`git push origin feature/description`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

