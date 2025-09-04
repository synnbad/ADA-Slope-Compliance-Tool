"""Central configuration and defaults for the project."""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    outputs_dir: Path = Path("outputs")
    report_md: str = "fsu_slope_summary.md"
    ada_slope_threshold_pct: float = 5.0  # percent
    default_raster_path: str = "data/raw/elevation_fsu.tif"
    default_slope_geojson: str = "data/processed/fsu_slope_segments.geojson"


DEFAULT = Config()
