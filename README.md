# ADA Slope Compliance Tool

This project provides a GIS-based, Python-powered solution for analyzing pedestrian pathway accessibility. It identifies ADA-compliant segments based on slope, leveraging spatial data automation and visualization. Initially developed to analyze Florida State University (FSU) pathways, it is now a generalized tool to help institutions assess ADA pathway compliance.

## Features
- Analyze pathways for ADA compliance using elevation and slope
- Automatically clean, resample, and evaluate spatial data
- Generate visual outputs: compliance maps, elevation reports
- Web-ready pipeline for user-uploaded raster inputs (GeoTIFFs)
- Designed for expansion into a hosted web tool

## Tech Stack
- **Python Libraries:** geopandas, rasterio, shapely, matplotlib, pandas
- **GIS Tools:** QGIS / ArcGIS Pro (for preprocessing)
- **Visualization:** matplotlib, folium
- **Hosting Prep:** AWS Free Tier (S3, EC2, Lambda or Streamlit Cloud)
- **Version Control:** GitHub


## Roadmap

- Data cleaning, slope classification, and compliance visualization  
- Export maps and markdown summaries  
- **Next Phase: AWS-Hosted Web App**  
  - Build web UI (Flask/Streamlit)  
  - Accept GeoTIFF uploads  
  - Return slope compliance maps & reports  

## License
[MIT License](LICENSE) — free to use, adapt, and build upon.

