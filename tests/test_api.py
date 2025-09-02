import sys
import numpy as np
import pytest

sys.path.append("backend")

rasterio = pytest.importorskip("rasterio")
from fastapi.testclient import TestClient
from app.main import app
from conftest import geotiff_bytes_from_array

client = TestClient(app)

def test_upload_and_results():
    arr = np.zeros((20, 20), dtype="float32")
    data = geotiff_bytes_from_array(arr)
    files = {"file": ("dem.tif", data, "image/tiff")}
    r = client.post("/upload", files=files)
    assert r.status_code == 200
    job_id = r.json()["job_id"]

    r2 = client.get(f"/results/{job_id}")
    assert r2.status_code == 200
    js = r2.json()
    assert "summary" in js and "artifacts" in js
    assert "histogram" in js["artifacts"]
