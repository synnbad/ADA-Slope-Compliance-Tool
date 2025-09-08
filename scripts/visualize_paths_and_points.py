import geopandas as gpd
import matplotlib.pyplot as plt


def plot_paths_and_points(paths_fp, points_fp):
    """
    Loads the pedestrian paths and resampled points,
    and plots them together on a single static map.
    """

    # Load the preprocessed pedestrian paths (LineStrings)
    gdf_paths = gpd.read_file(paths_fp)

    # Load the resampled points generated along the paths
    gdf_points = gpd.read_file(points_fp)

    # Create a matplotlib figure and axis
    fig, ax = plt.subplots(figsize=(12, 12))

    # Plot the paths first (background layer)
    gdf_paths.plot(ax=ax, color="steelblue", linewidth=1, label="Paths")

    # Plot the resampled points on top (foreground layer)
    gdf_points.plot(ax=ax, color="crimson", markersize=8, label="Resampled Points")

    # Set plot title
    ax.set_title("FSU Campus Pedestrian Paths and Resampled Points", fontsize=16)

    # Turn off axis tick marks and labels
    ax.set_axis_off()

    # Add a legend to differentiate paths vs points
    plt.legend()

    # Save the figure as a PNG file to the outputs/maps directory
    plt.savefig("outputs/maps/fsu_paths_and_points_preview.png", dpi=300)

    # Display the plot interactively
    plt.show()


if __name__ == "__main__":
    # Entry point for running the script
    # Plots both paths and resampled points
    plot_paths_and_points(
        paths_fp="data/processed/fsu_paths_cleaned.geojson",
        points_fp="data/processed/fsu_paths_resampled_points.geojson"
    )
    print("Paths and points plotted successfully.")
