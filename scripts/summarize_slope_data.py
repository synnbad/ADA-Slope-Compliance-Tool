import geopandas as gpd
import json
import os

def summarize_slope_compliance(slope_fp, output_md_fp=None, output_json_fp=None):
    """
    Loads a GeoJSON file with slope segment data and computes ADA compliance summary.
    Saves the results to a Markdown file for easy viewing or sharing.
    """

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

    if output_md_fp:
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

        # Step 5: Save to Markdown file
        os.makedirs(os.path.dirname(output_md_fp), exist_ok=True)
        with open(output_md_fp, "w") as f:
            f.write(md_text)

        print("ADA slope compliance summary saved to:", output_md_fp)

    if output_json_fp:
        os.makedirs(os.path.dirname(output_json_fp), exist_ok=True)
        with open(output_json_fp, "w") as f:
            json.dump(summary, f, indent=4)
        print("JSON summary saved to:", output_json_fp)

if __name__ == "__main__":
    summarize_slope_compliance(
        slope_fp="data/processed/fsu_slope_segments.geojson",
        output_md_fp="outputs/fsu_slope_summary.md",
        output_json_fp="outputs/summaries/slope_summary.json",
    )
