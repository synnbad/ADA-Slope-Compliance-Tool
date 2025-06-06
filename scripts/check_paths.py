import geopandas as gpd


def inspect_paths(path_fp):
    # Load the path dataset (GeoJSON) using GeoPandas
    # Each row in this GeoDataFrame represents a geographic feature, like a footpath or sidewalk
    gdf = gpd.read_file(path_fp)

    print("Original feature count (includes all geometry types):", len(gdf))

    # Step 1: Filter to include only LineString geometries
    # These represent linear paths; other geometries like Polygon are not usable for our slope analysis
    gdf = gdf[gdf.geometry.type == "LineString"]
    print("Remaining LineString features:", len(gdf))

    # Step 2: Reproject the data from EPSG:4326 (lat/lon in degrees)
    # to EPSG:26917 (UTM Zone 17N, which uses meters as units)
    # This is necessary to measure distances and slopes correctly
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
    # This loads, filters, reprojects, and saves path data from OpenStreetMap
    inspect_paths("data/raw/fsu_paths.geojson")
