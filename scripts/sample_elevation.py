import geopandas as gpd
import rasterio


def sample_elevation_at_points(points_fp, raster_fp, output_fp):
    """
    Loads a GeoJSON of point features and samples elevation values
    from a DEM raster. The elevation is added to each point and saved
    to a new GeoJSON file.
    """

    # Step 1: Load the GeoDataFrame of resampled points
    gdf_points = gpd.read_file(points_fp)

    # Step 2: Open the elevation raster (DEM)
    with rasterio.open(raster_fp) as src:

        # Step 2a: Reproject points to match the raster's CRS if different
        if gdf_points.crs != src.crs:
            gdf_points = gdf_points.to_crs(src.crs)  # Reproject geometries
            # Forcefully overwrite CRS metadata to match raster
            gdf_points.set_crs(src.crs, inplace=True, allow_override=True)

        # Step 3: Extract coordinates from point geometries
        coords = [(pt.x, pt.y) for pt in gdf_points.geometry]

        # Step 4: Sample elevation values at each point's location
        elevations = list(src.sample(coords))

        # Step 5: Flatten the elevation results and handle NoData values
        nodata = src.nodata or -9999
        gdf_points["elevation"] = [
            val[0] if val and val[0] != nodata else None
            for val in elevations
        ]

    # Step 6: Save the output GeoJSON file with new elevation data
    gdf_points.to_file(output_fp, driver="GeoJSON")
    print(f"Elevation-sampled points saved to: {output_fp}")


if __name__ == "__main__":
    sample_elevation_at_points(
        points_fp="data/processed/fsu_paths_resampled_points.geojson",
        raster_fp="data/raw/elevation_fsu.tif",
        output_fp="data/processed/fsu_points_with_elevation.geojson"
    )
