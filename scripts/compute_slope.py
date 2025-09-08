import geopandas as gpd
from shapely.geometry import LineString
import matplotlib.pyplot as plt

ADA_SLOPE_THRESHOLD = 0.05  # ADA compliance: 5% max slope


def compute_slopes_by_path(points_fp, output_fp):
    """
    Computes slope segments between adjacent elevation points, grouped by path_id,
    flags whether each segment is ADA compliant, and saves results.
    """
    gdf_points = gpd.read_file(points_fp)
    if gdf_points.crs is None:
        raise ValueError("Input data must have a CRS")
    if gdf_points.crs.is_geographic:
        gdf_points = gdf_points.to_crs("EPSG:26917")

    if "path_id" not in gdf_points.columns:
        raise ValueError("Missing 'path_id' field in points dataset. Ensure resampling included path_id tagging.")

    grouped = gdf_points.groupby("path_id")

    segments, slopes, compliance, group_ids = [], [], [], []

    for path_id, group in grouped:
        group = group.sort_index().reset_index(drop=True)

        for i in range(len(group) - 1):
            pt1, pt2 = group.iloc[i], group.iloc[i + 1]

            if pt1["elevation"] is None or pt2["elevation"] is None:
                continue

            elev_diff = pt2["elevation"] - pt1["elevation"]
            dist = pt1.geometry.distance(pt2.geometry)
            slope = elev_diff / dist if dist != 0 else 0

            segment = LineString([pt1.geometry, pt2.geometry])
            segments.append(segment)
            slopes.append(round(slope, 4))
            compliance.append(abs(slope) <= ADA_SLOPE_THRESHOLD)
            group_ids.append(path_id)

    gdf_slopes = gpd.GeoDataFrame({
        "path_id": group_ids,
        "slope": slopes,
        "ada_compliant": compliance,
        "geometry": segments
    }, crs=gdf_points.crs)

    gdf_slopes.to_file(output_fp, driver="GeoJSON")
    print(f"Slope segments saved to: {output_fp}")
    print(f"Non-compliant segments: {(~gdf_slopes['ada_compliant']).sum()}")

    # Slope distribution debugging
    print("\nSlope Summary:")
    print(gdf_slopes[["slope", "ada_compliant"]].describe())
    print("\nTop 10 steepest segments:")
    print(gdf_slopes.sort_values("slope", ascending=False).head(10))

    return gdf_slopes


def plot_slope_segments(gdf):
    fig, ax = plt.subplots(figsize=(12, 10))
    gdf[gdf['ada_compliant']].plot(ax=ax, color='green', linewidth=1, label='ADA Compliant')
    gdf[~gdf['ada_compliant']].plot(ax=ax, color='red', linewidth=1.5, label='Non-Compliant')
    plt.legend()
    plt.title("Slope Segments and ADA Compliance")
    plt.axis('off')
    plt.savefig("outputs/maps/fsu_slope_segments.png", dpi=300)
    plt.show()

    fig, ax = plt.subplots(figsize=(12, 10))
    gdf.plot(column="slope", cmap="RdYlGn_r", linewidth=1.2, legend=True, ax=ax)
    plt.title("Slope Gradient Map")
    plt.axis('off')
    plt.savefig("outputs/maps/fsu_slope_gradient.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    output_fp = "data/processed/fsu_slope_segments.geojson"
    gdf_slopes = compute_slopes_by_path(
        points_fp="data/processed/fsu_points_with_elevation.geojson",
        output_fp=output_fp
    )
    plot_slope_segments(gdf_slopes)
