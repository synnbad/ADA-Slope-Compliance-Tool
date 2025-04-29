import geopandas as gpd
from shapely.geometry import LineString, Point

def generate_points_along_line(line, distance_interval):
    """
    Given a LineString and a distance interval (in meters),
    returns a list of Points evenly spaced along the line.
    """
    points = []
    total_length = line.length

    # Generate points at every 'distance_interval' along the LineString
    for dist in range(0, int(total_length), distance_interval):
        point = line.interpolate(dist)  # Interpolates a point at given distance
        points.append(line.interpolate(dist))
    
    return points

def resample_paths_to_points(path_fp, output_fp, interval_meters=5):
    """
    Loads pedestrian paths, resamples them into evenly spaced points,
    and saves the result as a GeoJSON file (output format is hardcoded as GeoJSON).
    """
    # Load cleaned, reprojected pedestrian paths
    gdf_paths = gpd.read_file(path_fp)

    resampled_points = []

    # Loop through each LineString
    for row in gdf_paths.itertuples():
        line = row.geometry

        # Only process valid LineStrings
        if isinstance(line, LineString):
            points = generate_points_along_line(line, distance_interval=interval_meters)
            resampled_points.extend(points)

    # Create a GeoDataFrame of points
    # Ensure all elements in resampled_points are valid Point objects
    valid_points = [pt for pt in resampled_points if isinstance(pt, Point)]
    gdf_points = gpd.GeoDataFrame(geometry=valid_points, crs=gdf_paths.crs)

    # Save the resampled points
    gdf_points.to_file(output_fp, driver="GeoJSON")

    print(f"Resampled points saved to: {output_fp}")
    print(f"Total points generated from '{path_fp}': {len(gdf_points)}")

if __name__ == "__main__":
    resample_paths_to_points(
        path_fp="data/processed/fsu_paths_cleaned.geojson",
        output_fp="data/processed/fsu_paths_resampled_points.geojson",
        interval_meters=5
    )
