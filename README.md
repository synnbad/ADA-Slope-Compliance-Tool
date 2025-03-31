# Mapping Accessibility on Campus: A GIS Study of ADA-Compliant Pathways at FSU

This project analyzes pedestrian accessibility across Florida State University’s campus using GIS, spatial data, and Python automation. The goal is to identify ADA-compliant pathways, assess slope and surface challenges, and generate visual tools that highlight accessibility conditions across campus.

---

##  Goals

- Analyze pedestrian pathways for ADA compliance based on slope and other attributes
- Automate spatial data cleaning, classification, and visualization with Python
- Generate clear visual outputs: maps, reports, or dashboards
- Build a portfolio-worthy GIS and automation project

---

## Tools & Technologies

- **Python**: geopandas, rasterio, shapely, pandas, folium, matplotlib
- **GIS Platforms**: QGIS or ArcGIS Pro (for manual inspection or export)
- **Jupyter Notebooks**: Exploratory analysis and documentation
- **GitHub**: Version control and portfolio hosting

---


## Folder Structure

```
fsu-ada-accessibility-mapping/
├── data/
│   ├── raw/              # Original spatial datasets (shapefiles, DEMs, GeoJSON)
│   └── processed/        # Cleaned or classified data
├── notebooks/            # Jupyter notebooks for exploration and analysis
├── scripts/              # Python automation scripts
├── outputs/
│   ├── maps/             # Static map exports (PNG, PDF)
│   └── reports/          # Summary reports (Markdown, PDF, etc.)
├── docs/                 # Diagrams, flowcharts, and planning notes
├── environment.yml       # Conda environment file for reproducibility
├── .gitignore            # Ignore unnecessary files/folders in Git
├── README.md             # Project overview and instructions
└── run_pipeline.py       # Script to run full analysis pipeline
```

 ## Roadmap

- [x] Set up project structure and environment
- [ ] Collect spatial datasets (paths, elevation, building footprints)
- [ ] Write Python script to analyze slopes and classify accessibility
- [ ] Generate automated maps and reports
- [ ] Build an interactive map or dashboard
- [ ] Final polish and documentation

---

## License

MIT License — feel free to adapt and build upon this work.
