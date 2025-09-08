"""Test FastAPI backend endpoints."""

import sys
import os
import numpy as np
import pytest

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
sys.path.insert(0, backend_path)

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


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_bad_mime():
    data = b"not a tiff"
    files = {"file": ("bad.txt", data, "text/plain")}
    r = client.post("/upload", files=files)
    assert r.status_code == 400
    assert r.json()["detail"] == "ERR_BAD_MIME"


def test_oversize_rejected():
    # 26 MiB of zeros
    data = b"\x00" * (26 * 1024 * 1024)
    files = {"file": ("dem.tif", data, "image/tiff")}
    r = client.post("/upload", files=files)
    assert r.status_code == 413
    assert r.json()["detail"] == "ERR_SIZE_LIMIT"