# ADA Slope Compliance Tool

This project provides a GIS-based, Python-powered solution for analyzing pedestrian pathway accessibility. It identifies ADA-compliant segments based on slope, leveraging spatial data automation and visualization. Initially developed to analyze Florida State University (FSU) pathways, it is now a generalized tool to help institutions assess ADA pathway compliance.

## Features
- Analyze pathways for ADA compliance using elevation and slope
- Automatically clean, convert, resample, and evaluate spatial data
- Generate visual outputs: compliance maps, elevation reports
- Web-ready pipeline for user-uploaded raster inputs (GeoTIFFs)
- Designed for expansion into a hosted web tool

## Tech Stack
- **Python Libraries:** geopandas, rasterio, shapely, matplotlib, pandas
- **GIS Tools:** QGIS / ArcGIS Pro (for preprocessing)
- **Visualization:** matplotlib, folium
- **Hosting Prep:** AWS Free Tier (S3, EC2, Lambda or Streamlit Cloud)
- **Version Control:** GitHub

## Setup
1. Clone the repository and enter the project directory
   ```bash
   git clone https://github.com/<your-org>/ADA-Slope-Compliance-Tool.git
   cd ADA-Slope-Compliance-Tool
   ```
2. (Optional) create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install the required dependencies
   ```bash
   pip install geopandas rasterio shapely matplotlib pandas numpy folium streamlit
   ```

## How to Use

### Streamlit Web App
Run the interactive tool with
```bash
streamlit run app.py
```
Upload a DEM raster (.tif) and a GeoJSON of points with elevations to view ADA
slope compliance results directly in your browser.

### Command Line Workflow
Each script in the `scripts/` folder performs a step in the processing pipeline:
```bash
python scripts/check_paths.py                 # clean and reproject path data
python scripts/resample_paths.py              # convert polygons & generate points
python scripts/sample_elevation.py            # sample DEM elevations
python scripts/compute_slope.py               # compute slope segments
python scripts/summarize_slope_data.py        # create a Markdown summary
```
Processed files and reports will be written to the `outputs/` directory.


## Running Tests

Install the project requirements (includes `pytest`):

```bash
pip install -r requirements.txt
```

Then run the test suite from the project root:

```bash
pytest
```
Sample GeoJSON data for conversion testing is available in `data/test/test_paths.geojson`.

## Roadmap

- Data cleaning, slope classification, and compliance visualization  
- Export maps and markdown summaries  
- **Next Phase: AWS-Hosted Web App**  
  - Build web UI (Flask/Streamlit)  
  - Accept GeoTIFF uploads  
  - Return slope compliance maps & reports  

## License
[MIT License](LICENSE) — free to use, adapt, and build upon.

