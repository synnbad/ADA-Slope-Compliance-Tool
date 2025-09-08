import rasterio


def inspect_raster(path):
    """Inspect the raster file to check it's properties."""
    with rasterio.open(path) as src:
        print("File Info:")
        print(f" - CRS: {src.crs}")
        print(f" - Width x Height: {src.width} x {src.height}")
        print(f" - Resolution: {src.res}")
        print(f" - Bounds: {src.bounds}")
        print(f" - Bands: {src.count}")
        print(f" - Data Type: {src.dtypes[0]}")

    # Centering the pixel values
        row, col = src.height // 2, src.width // 2
        value = src.read(1)[row, col]
    print(f" - Sample elevation at center: {value} meters")


if __name__ == "__main__":
    inspect_raster("data/raw/USGS_13_n31w085_20230215.tif")
