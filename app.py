import streamlit as st
import geopandas as gpd
import rasterio
import numpy as np
from shapely.geometry import LineString, Point
import matplotlib.pyplot as plt
import os
from tempfile import NamedTemporaryFile

ADA_SLOPE_THRESHOLD = 0.05  # 5%

def sample_elevation(points_gdf, dem_path):
    with rasterio.open(dem_path) as src:
        if points_gdf.crs != src.crs:
            points_gdf = points_gdf.to_crs(src.crs)

        coords = [(pt.x, pt.y) for pt in points_gdf.geometry if isinstance(pt, Point)]
        elevations = list(src.sample(coords))
        nodata = src.nodata or -9999

        valid_points = [pt for pt in points_gdf.geometry if isinstance(pt, Point)]
        points_gdf = gpd.GeoDataFrame(geometry=valid_points, crs=points_gdf.crs)
        points_gdf["elevation"] = [val[0] if val and val[0] != nodata else None for val in elevations]

    return points_gdf

def compute_smoothed_slopes(points_gdf, window_size=3):
    if 'path_id' in points_gdf.columns:
        grouped = points_gdf.groupby('path_id')
    else:
        grouped = [(None, points_gdf)]

    segments = []
    slopes = []
    compliance = []
    group_ids = []

    for group_id, group in grouped:
        group = group.loc[group.geometry.apply(lambda p: isinstance(p, Point))]
        group = group.iloc[group.geometry.apply(lambda p: (p.x, p.y)).argsort()].reset_index(drop=True)

        for i in range(1, len(group) - 1):
            window = group.iloc[i - 1:i + 2]  # 3-point window
            if window["elevation"].isnull().any():
                continue

            pt1, pt2 = window.iloc[0], window.iloc[2]
            elev_diff = pt2["elevation"] - pt1["elevation"]
            dist = pt1.geometry.distance(pt2.geometry)
            slope = elev_diff / dist if dist != 0 else 0

            segment = LineString([pt1.geometry, pt2.geometry])
            segments.append(segment)
            slopes.append(round(slope, 4))
            compliance.append(slope <= ADA_SLOPE_THRESHOLD)
            group_ids.append(group_id)

    return gpd.GeoDataFrame({
        "path_id": group_ids,
        "slope": slopes,
        "ada_compliant": compliance,
        "geometry": segments
    }, crs=points_gdf.crs)

def render_map(gdf_slopes):
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf_slopes[gdf_slopes['ada_compliant']].plot(ax=ax, color='green', linewidth=1, label='ADA Compliant')
    gdf_slopes[~gdf_slopes['ada_compliant']].plot(ax=ax, color='red', linewidth=1.5, label='Non-Compliant')
    plt.legend()
    plt.axis('off')
    st.pyplot(fig)

def main():
    st.title("ADA Slope Compliance Tool")
    st.markdown("Upload a DEM raster (GeoTIFF) and point GeoJSON to compute ADA slope compliance.")

    raster_file = st.file_uploader("Upload DEM raster (.tif)", type=["tif"])
    points_file = st.file_uploader("Upload GeoJSON of elevation-sampled points", type=["geojson"])

    if raster_file and points_file:
        with NamedTemporaryFile(delete=False, suffix=".tif") as tmp_raster:
            tmp_raster.write(raster_file.read())
            dem_path = tmp_raster.name

        with NamedTemporaryFile(delete=False, suffix=".geojson") as tmp_points:
            tmp_points.write(points_file.read())
            points_path = tmp_points.name

        gdf_points = gpd.read_file(points_path)
        gdf_sampled = sample_elevation(gdf_points, dem_path)
        gdf_slopes = compute_smoothed_slopes(gdf_sampled)

        st.success("Slope computation complete!")

        compliant = gdf_slopes['ada_compliant'].sum()
        non_compliant = len(gdf_slopes) - compliant

        st.markdown("### Compliance Summary")
        st.markdown(f"**Total Segments:** {len(gdf_slopes)}")
        st.markdown(f"**ADA Compliant:** {compliant}")
        st.markdown(f"**Non-Compliant:** {non_compliant}")
        st.markdown(f"**Compliance Rate:** {round(100 * compliant / len(gdf_slopes), 2)}%")

        st.markdown("###Slope Map")
        render_map(gdf_slopes)

if __name__ == "__main__":
    main()
