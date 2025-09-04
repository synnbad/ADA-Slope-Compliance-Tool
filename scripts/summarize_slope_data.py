import geopandas as gpd
import os
import json
from pathlib import Path
import logging

from ada_slope.config import DEFAULT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of relative paths where we want .gitkeep files
folders = [
    "data/raw",
    "data/processed",
    "notebooks",
    "scripts",
    "outputs/maps",
    "outputs/reports",
    "docs",
]


def summarize_slope_compliance(slope_fp: str | None = None, output_md_fp: str | None = None, output_json_fp: str | None = None):
    """
    Loads a GeoJSON file with slope segment data and computes ADA compliance summary.
    Saves the results to a Markdown file for easy viewing or sharing.
    """

    # Resolve defaults
    slope_fp = slope_fp or str(DEFAULT.default_slope_geojson)
    output_md_fp = output_md_fp or str(Path(DEFAULT.outputs_dir) / DEFAULT.report_md)
    output_json_fp = output_json_fp or str(Path(DEFAULT.outputs_dir) / "summaries" / "slope_summary.json")

    # Step 1: Load the slope segment GeoDataFrame
    gdf = gpd.read_file(slope_fp)

    # Step 2: Compute statistics
    total_segments = len(gdf)
    ada_compliant = gdf["ada_compliant"].sum()
    non_compliant = total_segments - ada_compliant
    compliance_pct = round((ada_compliant / total_segments) * 100, 2)

    # Step 3: Prepare summary dictionary
    summary = {
        "total_segments": total_segments,
        "ada_compliant_segments": int(ada_compliant),
        "non_compliant_segments": int(non_compliant),
        "compliance_percentage": compliance_pct,
    }

    # Step 4: Create Markdown output
    md_lines = [
        "# ADA Slope Compliance Summary\n",
        "| Metric | Value |",
        "|--------|-------|",
    ]
    for key, value in summary.items():
        pretty_key = key.replace("_", " ").title()
        md_lines.append(f"| {pretty_key} | {value} |")

    md_text = "\n".join(md_lines)

    # Safe write the markdown and JSON outputs
    if output_md_fp:
        os.makedirs(os.path.dirname(output_md_fp) or ".", exist_ok=True)
        with open(output_md_fp, "w", encoding="utf-8") as f:
            f.write(md_text)
        logger.info("ADA slope compliance summary saved to: %s", output_md_fp)

    if output_json_fp:
        os.makedirs(os.path.dirname(output_json_fp) or ".", exist_ok=True)
        with open(output_json_fp, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)
        logger.info("JSON summary saved to: %s", output_json_fp)


def add_gitkeeps(base_path: Path = Path(".")):
    for rel in folders:
        folder = (base_path / rel)
        folder.mkdir(parents=True, exist_ok=True)
        keep_path = folder / ".gitkeep"
        keep_path.touch(exist_ok=True)
        logger.info(".gitkeep added in %s", folder)


if __name__ == "__main__":
    summarize_slope_compliance(
        slope_fp="data/processed/fsu_slope_segments.geojson",
        output_md_fp="outputs/fsu_slope_summary.md",
        output_json_fp="outputs/summaries/slope_summary.json",
    )
    add_gitkeeps()
