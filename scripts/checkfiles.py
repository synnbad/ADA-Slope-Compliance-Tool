import geopandas as gpd
import rasterio

def check_crs_consistency(raster_fp, points_fp, elevation_points_fp):
    # Load raster
    with rasterio.open(raster_fp) as raster:
        print(f"Raster CRS: {raster.crs.to_string()}")

    # Load input resampled points
    gdf_points = gpd.read_file(points_fp)
    print(f"Original Points CRS: {gdf_points.crs.to_string()}")

    # Load output points with elevation
    gdf_elevated = gpd.read_file(elevation_points_fp)
    print(f"Elevation-Sampled Points CRS: {gdf_elevated.crs.to_string()}")

if __name__ == "__main__":
    check_crs_consistency(
        raster_fp="data/raw/elevation_fsu.tif",
        points_fp="data/processed/fsu_paths_resampled_points.geojson",
        elevation_points_fp="data/processed/fsu_points_with_elevation.geojson"
    )
