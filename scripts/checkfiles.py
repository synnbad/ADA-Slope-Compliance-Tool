import geopandas as gpd
import rasterio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_crs_consistency(raster_fp, points_fp, elevation_points_fp):
    # Load raster
    try:
        with rasterio.open(raster_fp) as raster:
            raster_crs = raster.crs
            logger.info("Raster CRS: %s", 
                   raster_crs.to_string() if raster_crs else "None")
    except Exception as e:
        logger.exception("Failed to open raster %s: %s", raster_fp, e)
        raise

    # Load input resampled points
    try:
        gdf_points = gpd.read_file(points_fp)
        logger.info("Original Points CRS: %s", 
                   gdf_points.crs.to_string() if gdf_points.crs else "None")
    except Exception as e:
        logger.exception("Failed to read points %s: %s", points_fp, e)
        raise

    # Load output points with elevation
    try:
        gdf_elevated = gpd.read_file(elevation_points_fp)
        logger.info("Elevation-Sampled Points CRS: %s", 
                   gdf_elevated.crs.to_string() if gdf_elevated.crs else "None")
    except Exception as e:
        logger.exception("Failed to read elevation points %s: %s", elevation_points_fp, e)
        raise


if __name__ == "__main__":
    check_crs_consistency(
        raster_fp="data/raw/elevation_fsu.tif",
        points_fp="data/processed/fsu_paths_resampled_points.geojson",
        elevation_points_fp="data/processed/fsu_points_with_elevation.geojson"
    )
