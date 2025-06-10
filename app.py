import streamlit as st
import geopandas as gpd
import rasterio
import numpy as np
from shapely.geometry import LineString, Point
import matplotlib.pyplot as plt
import os
from tempfile import NamedTemporaryFile
from fiona.errors import DriverError

st.set_page_config(
    page_title="ADA Slope Compliance Tool",
    layout="wide",
)

ADA_SLOPE_THRESHOLD = 0.05  # 5%

def sample_elevation(points_gdf, dem_path):
    with rasterio.open(dem_path) as src:
        if points_gdf.crs is None:
            raise ValueError("Input points must have a CRS")
        if points_gdf.crs != src.crs:
            points_gdf = points_gdf.to_crs(src.crs)

        # Filter to Point geometries but keep existing attributes
        points_gdf = points_gdf[points_gdf.geometry.apply(lambda g: isinstance(g, Point))].copy()

        coords = [(pt.x, pt.y) for pt in points_gdf.geometry]
        elevations = list(src.sample(coords))
        nodata = src.nodata or -9999
        points_gdf["elevation"] = [val[0] if val and val[0] != nodata else None for val in elevations]

    # After sampling, ensure points are in a metric CRS for distance calculations
    if points_gdf.crs.is_geographic:
        points_gdf = points_gdf.to_crs("EPSG:26917")

    return points_gdf

def compute_smoothed_slopes(points_gdf, window_size=3, slope_threshold=ADA_SLOPE_THRESHOLD):
    """Compute slope segments with a sliding window of *window_size* points."""

    if window_size < 3 or window_size % 2 == 0:
        raise ValueError("window_size must be an odd integer >= 3")

    if points_gdf.crs is None:
        raise ValueError("Points must have a CRS")
    if points_gdf.crs.is_geographic:
        points_gdf = points_gdf.to_crs("EPSG:26917")

    half_window = window_size // 2
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
        # Preserve the original ordering from the input instead of sorting by
        # coordinates which can reorder curved paths incorrectly
        group = group.sort_index().reset_index(drop=True)

        if len(group) < window_size:
            raise ValueError(
                f"Group {group_id} has {len(group)} point(s), fewer than window_size {window_size}"
            )

        for i in range(half_window, len(group) - half_window):
            window = group.iloc[i - half_window:i + half_window + 1]
            if window["elevation"].isnull().any():
                continue

            pt1, pt2 = window.iloc[0], window.iloc[-1]
            elev_diff = pt2["elevation"] - pt1["elevation"]
            dist = pt1.geometry.distance(pt2.geometry)
            slope = elev_diff / dist if dist != 0 else 0

            segment = LineString([pt1.geometry, pt2.geometry])
            segments.append(segment)
            slopes.append(round(slope, 4))
            compliance.append(abs(slope) <= slope_threshold)
            group_ids.append(group_id)

    return gpd.GeoDataFrame({
        "path_id": group_ids,
        "slope": slopes,
        "ada_compliant": compliance,
        "geometry": segments
    }, crs=points_gdf.crs)

def render_map(gdf_slopes):
    """Render a map of ADA compliant and non-compliant slope segments."""

    # Check 1: Is the GeoDataFrame empty?
    if gdf_slopes.empty:
        st.warning("No slope segments were computed. Check your path and DEM alignment.")
        return

    # Check 2: Does it have geometry?
    if "geometry" not in gdf_slopes.columns:
        st.error("Slope segments are missing geometry.")
        return

    # Ensure geometry is active
    try:
        gdf_slopes = gdf_slopes.set_geometry("geometry")
    except Exception as e:  # pragma: no cover - sanity check
        st.error(f"Failed to activate geometry: {e}")
        return

    # Check 3: Validate 'ada_compliant' column
    if "ada_compliant" not in gdf_slopes.columns:
        st.error("Missing ADA compliance classification column.")
        return

    ada_yes = gdf_slopes[gdf_slopes["ada_compliant"] == True]
    ada_no = gdf_slopes[gdf_slopes["ada_compliant"] == False]

    if ada_yes.empty and ada_no.empty:
        st.warning(
            "Slope segments exist but none could be classified. Check elevation sampling."
        )
        return

    fig, ax = plt.subplots(figsize=(12, 8))
    if not ada_yes.empty:
        ada_yes.plot(ax=ax, color="green", linewidth=1, label="ADA Compliant")
    if not ada_no.empty:
        ada_no.plot(ax=ax, color="red", linewidth=1, label="Non-Compliant")

    ax.legend()
    ax.set_title("ADA Slope Compliance Map")
    ax.axis("off")
    st.pyplot(fig)

def main():
    st.title("ADA Slope Compliance Tool")
    st.markdown(
        "Upload a DEM raster (GeoTIFF) and a GeoJSON of points with elevations to analyze walkway compliance."
    )

    with st.sidebar:
        st.header("Input Data")
        raster_file = st.file_uploader("DEM raster (.tif)", type=["tif"])
        points_file = st.file_uploader("Sampled points (.geojson)", type=["geojson"])

        st.header("Options")
        slope_percent = st.slider("ADA slope threshold (%)", 1, 20, 5)
        window_size = st.number_input(
            "Smoothing window size (odd)", min_value=3, step=2, value=3
        )
        compute = st.button("Compute Slopes")

    if compute and raster_file and points_file:
        with NamedTemporaryFile(delete=False, suffix=".tif") as tmp_raster:
            tmp_raster.write(raster_file.read())
            dem_path = tmp_raster.name

        with NamedTemporaryFile(delete=False, suffix=".geojson") as tmp_points:
            tmp_points.write(points_file.read())
            points_path = tmp_points.name

        try:
            gdf_points = gpd.read_file(points_path)
        except (IOError, DriverError) as e:
            st.error(f"Error reading points file: {e}")
            return

        gdf_sampled = sample_elevation(gdf_points, dem_path)

        slope_threshold = slope_percent / 100.0
        gdf_slopes = compute_smoothed_slopes(
            gdf_sampled, window_size=int(window_size), slope_threshold=slope_threshold
        )

        st.success("Slope computation complete!")

        compliant = int(gdf_slopes["ada_compliant"].sum())
        non_compliant = len(gdf_slopes) - compliant
        compliance_rate = (
            round(100 * compliant / len(gdf_slopes), 2)
            if len(gdf_slopes) > 0
            else 0.0
        )

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Segments", len(gdf_slopes))
        col2.metric("Compliant", compliant)
        col3.metric("Non-Compliant", non_compliant)
        col4.metric("Compliance Rate", f"{compliance_rate}%")

        st.markdown("### Slope Map")
        render_map(gdf_slopes)

        gdf_download = gdf_slopes.to_crs("EPSG:4326")
        geojson = gdf_download.to_json()
        st.download_button(
            "Download GeoJSON",
            geojson,
            file_name="slope_segments.geojson",
            mime="application/geo+json",
        )
    else:
        st.info("Upload data and click Compute to begin.")

if __name__ == "__main__":
    main()

