import uuid
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from mangum import Mangum
from pydantic import BaseModel

from .processing import process_dem_in_memory

app = FastAPI(title="ADA Slope Compliance API", version="0.1.0")

# Simple in-memory job store for MVP (replace with DynamoDB later)
JOBS: dict[str, dict[str, Any]] = {}


class Results(BaseModel):
    status: str
    summary: dict[str, Any]
    artifacts: dict[str, Any]


@app.post("/upload")
async def upload_dem(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".tif", ".tiff")):
        raise HTTPException(
            status_code=400, detail="Please upload a GeoTIFF (.tif/.tiff) DEM."
        )
    data = await file.read()
    job_id = str(uuid.uuid4())
    try:
        result = process_dem_in_memory(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}") from e
    JOBS[job_id] = {
        "status": "done",
        "summary": result["summary"],
        "artifacts": result["artifacts"],
    }
    return {"job_id": job_id}


@app.get("/status/{job_id}")
def status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": job["status"]}


@app.get("/results/{job_id}", response_model=Results)
def results(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JSONResponse(job)


handler = Mangum(app)
