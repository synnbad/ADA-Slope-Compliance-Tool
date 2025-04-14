import geopandas as gpd
import matplotlib.pyplot as plt

def plot_paths(path_fp):
    # Load the preprocessed and reprojected pedestrian path data
    # This GeoDataFrame contains only LineString geometries in EPSG:26917 (meters)
    gdf = gpd.read_file(path_fp)

    # Create a matplotlib figure and axis
    # figsize controls how large the output plot appears (in inches)
    fig, ax = plt.subplots(figsize=(10, 10))

    # Plot the paths on the axis
    # color sets the line color; linewidth controls the visual thickness of the paths
    gdf.plot(ax=ax, color="steelblue", linewidth=1)

    # Set the plot title
    ax.set_title("FSU Campus Pedestrian Paths", fontsize=14)

    # Turn off axis tick marks and labels for a cleaner visual
    ax.set_axis_off()

    # Save the figure as a PNG file to the outputs/maps directory
    # dpi=300 ensures high-resolution export suitable for use in reports
    plt.savefig("outputs/maps/fsu_paths_preview.png", dpi=300)

    # Display the plot interactively
    plt.show()

if __name__ == "__main__":
    # Entry point for script execution
    # Loads the cleaned path dataset and visualizes it as a static map
    plot_paths("data/processed/fsu_paths_cleaned.geojson")
