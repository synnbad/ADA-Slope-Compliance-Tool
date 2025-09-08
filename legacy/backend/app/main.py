import uuid
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import BaseModel

from .processing import process_dem_in_memory


MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MiB


class Results(BaseModel):
    status: str
    summary: dict[str, Any]
    artifacts: dict[str, Any]


def create_app() -> FastAPI:
    app = FastAPI(title="ADA Slope Compliance API", version="0.2.0")

    # CORS will be tightened in API Gateway; allow narrow origin here if set
    allowed_origin = os.getenv("CORS_ORIGIN")
    if allowed_origin:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[allowed_origin],
            allow_credentials=False,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Content-Type"],
            max_age=600,
        )

    JOBS: dict[str, dict[str, Any]] = {}

    @app.get("/healthz")
    def healthz():
        build = os.getenv("BUILD_SHA", "unknown")
        return {"status": "ok", "build": build}

    @app.post("/upload")
    async def upload_dem(
        file: UploadFile = File(...),
        running_slope_max: float = 0.05,
        cross_slope_max: float = 0.02083,
        assumed_path_axis: str = "x",
    ):
        ct = (file.content_type or "").lower()
        if ct != "image/tiff":
            raise HTTPException(status_code=400, detail="ERR_BAD_MIME")
        if not file.filename.lower().endswith((".tif", ".tiff")):
            raise HTTPException(status_code=400, detail="ERR_BAD_MIME")

        data = await file.read()
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="ERR_SIZE_LIMIT")

        job_id = str(uuid.uuid4())
        try:
            result = process_dem_in_memory(
                data,
                running_slope_max=running_slope_max,
                cross_slope_max=cross_slope_max,
                assumed_path_axis=assumed_path_axis,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail="ERR_TIFF_READ") from e
        JOBS[job_id] = {
            "status": "done",
            "summary": result["summary"],
            "artifacts": result["artifacts"],
        }
        return {"job_id": job_id}

    @app.get("/results/{job_id}", response_model=Results)
    def results(job_id: str):
        job = JOBS.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return JSONResponse(job)

    return app


import os

app = create_app()
handler = Mangum(app)
