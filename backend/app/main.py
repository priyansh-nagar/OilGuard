"""
OilGuard API — Stage 1 (fully simulated).

This file only handles HTTP: receive an image, call the three services,
return JSON. It does not detect oil or talk to AIS itself.
"""

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .schemas import AnalysisResponse
from .services.ais import simulate_ais_candidates
from .services.attribution import score_candidates
from .services.detector import predict_spill

DISCLAIMER = (
    "All results are SIMULATED / DEMO DATA for a hackathon vertical slice. "
    "No real satellite processing or AIS lookup was performed. "
    "The attribution score is a simple ranking heuristic for demonstration only. "
    "It is not legal guilt and not a statistically calibrated probability."
)

app = FastAPI(
    title="OilGuard API",
    version="0.1.0",
    description="Stage 1 simulated oil-spill investigation API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "data_mode": "SIMULATED / DEMO DATA"}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze(image: UploadFile = File(...)):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    contents = await image.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    spill = predict_spill(contents)
    vessels = simulate_ais_candidates(spill)
    candidates = score_candidates(spill, vessels)

    return {
        "data_mode": "SIMULATED / DEMO DATA",
        "disclaimer": DISCLAIMER,
        "source_image": {
            "filename": image.filename or "upload.jpg",
            "size_bytes": len(contents),
        },
        "spill": spill,
        "candidates": candidates,
    }
