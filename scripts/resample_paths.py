import geopandas as gpd
from shapely.geometry import LineString, Point

def generate_points_along_line(line, distance_interval):
    """
    Given a LineString and a distance interval (in meters),
    returns a list of Points evenly spaced along the line.
    """
    points = []
    total_length = line.length

    for dist in range(0, int(total_length), distance_interval):
        point = line.interpolate(dist)
        points.append(point)

    return points

def resample_paths_to_points(path_fp, output_fp, interval_meters=5):
    """
    Resamples each LineString in a path GeoDataFrame into evenly spaced points.
    Tags each point with a 'path_id' corresponding to the original feature.
    """
    gdf_paths = gpd.read_file(path_fp)

    if gdf_paths.crs.to_epsg() != 26917:
        gdf_paths = gdf_paths.to_crs(epsg=26917)

    all_points = []
    path_ids = []

    for idx, row in gdf_paths.iterrows():
        line = row.geometry

        if isinstance(line, LineString):
            points = generate_points_along_line(line, interval_meters)
            all_points.extend(points)
            path_ids.extend([idx] * len(points))  # assign path_id based on row index

    # Create output GeoDataFrame
    gdf_points = gpd.GeoDataFrame({
        "path_id": path_ids,
        "geometry": all_points
    }, crs=gdf_paths.crs)

    gdf_points.to_file(output_fp, driver="GeoJSON")
    print(f"Resampled points with path IDs saved to: {output_fp}")
    print(f"Total points generated: {len(gdf_points)}")

if __name__ == "__main__":
    resample_paths_to_points(
        path_fp="data/processed/fsu_paths_cleaned.geojson",
        output_fp="data/processed/fsu_paths_resampled_points.geojson",
        interval_meters=5
    )
