"""
Shared data shapes for the API response.

Think of these as a contract: the frontend expects this JSON.
Later, real satellite/AIS code can fill the same fields.
"""

from pydantic import BaseModel, Field
from typing import List


class GeoPoint(BaseModel):
    lat: float
    lon: float


class SourceImage(BaseModel):
    filename: str
    size_bytes: int


class SpillResult(BaseModel):
    detected: bool
    confidence: float = Field(ge=0, le=1)
    center: GeoPoint
    estimated_area_km2: float
    detection_timestamp: str


class CandidateVessel(BaseModel):
    vessel_id: str
    name: str
    coordinates: GeoPoint
    timestamp: str
    spatial_consistency: float = Field(ge=0, le=1)
    temporal_consistency: float = Field(ge=0, le=1)
    trajectory_consistency: float = Field(ge=0, le=1)
    attribution_score: float = Field(ge=0, le=1)
    explanation: str
    trajectory: List[List[float]] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    data_mode: str = "SIMULATED / DEMO DATA"
    disclaimer: str
    source_image: SourceImage
    spill: SpillResult
    candidates: List[CandidateVessel]