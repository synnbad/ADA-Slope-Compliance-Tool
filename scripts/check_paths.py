import geopandas as gpd
from ada_slope.core import convert_polygons_to_lines
from ada_slope.io import ensure_vector_matches_raster_crs as align_crs


def inspect_paths(path_fp, raster_fp=None):
    # Load the path dataset (GeoJSON) using GeoPandas
    # Each row in this GeoDataFrame represents a geographic feature, like a footpath or sidewalk
    gdf = gpd.read_file(path_fp)

    print("Original feature count (includes all geometry types):", len(gdf))

    gdf = convert_polygons_to_lines(gdf)
    print("Geometry types after conversion:")
    print(gdf.geometry.type.value_counts())

    if raster_fp:
        gdf = align_crs(gdf, raster_fp)
    if gdf.crs.to_epsg() != 26917:
        gdf = gdf.to_crs(epsg=26917)
    print("Reprojected coordinate reference system:", gdf.crs)

    # Step 3: Save the cleaned and reprojected path dataset for later use
    # Saving as GeoJSON retains both the geometry and attribute fields
    gdf.to_file("data/processed/fsu_paths_cleaned.geojson", driver="GeoJSON")
    print("Cleaned path data saved to: data/processed/fsu_paths_cleaned.geojson")

    # Step 4: Display a sample path geometry to verify structure
    print("\nSample LineString geometry:")
    print(gdf.geometry.iloc[0])


if __name__ == "__main__":
    # Main entry point for standalone script execution
    # This loads, converts, reprojects, and saves path data from OpenStreetMap
    inspect_paths(
        "data/raw/fsu_paths.geojson",
        raster_fp="data/raw/elevation_fsu.tif",
    )
