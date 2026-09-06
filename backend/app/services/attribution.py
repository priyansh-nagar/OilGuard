"""
SIMULATED heuristic attribution.

This is a teaching/demo ranking, not legal proof and not a calibrated
probability of guilt. Scores are 0–1 only so the UI can sort candidates.

Later, replace the formulas here; keep the same output field names.
"""

from datetime import datetime, timezone
from math import radians, sin, cos, sqrt, atan2

# Weights are simple and documented on purpose.
WEIGHT_SPATIAL = 0.40
WEIGHT_TEMPORAL = 0.30
WEIGHT_TRAJECTORY = 0.30

# Default drift vector for prototype (NOT real ocean-current modeling)
# South-East drift: slightly south, slightly east
# km per hour
DEFAULT_DRIFT_VECTOR_KM_HR = {"north": -0.5, "east": 0.5}

# Distance scale for spatial consistency (km)
SPATIAL_SCALE_KM = 15.0

# Time scale for temporal consistency (minutes)
TEMPORAL_SCALE_MIN = 30.0


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in kilometers. Earth radius ~6371 km."""
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


def _spatial_consistency(spill: dict, vessel: dict) -> float:
    """
    Minimum Haversine distance from spill center to any vessel trajectory point.
    Closer = higher score. SPATIAL_SCALE_KM is soft 'nearby' scale.
    """
    if not vessel.get("trajectory"):
        return 0.0

    min_dist_km = min(
        _haversine_km(
            spill["center"]["lat"],
            spill["center"]["lon"],
            p["lat"],
            p["lon"],
        )
        for p in vessel["trajectory"]
    )
    return _clamp(1.0 - min_dist_km / SPATIAL_SCALE_KM)


def _temporal_consistency(spill: dict, vessel: dict) -> float:
    """
    Compare spill detection timestamp with timestamps across vessel trajectory.
    Find trajectory point closest in time to spill detection.
    """
    if not vessel.get("trajectory"):
        return 0.0

    spill_time = datetime.fromisoformat(spill["detection_timestamp"].replace("Z", "+00:00"))
    min_minutes = min(
        abs(
            (
                datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00")) - spill_time
            ).total_seconds()
            / 60
        )
        for p in vessel["trajectory"]
    )
    return _clamp(1.0 - min_minutes / TEMPORAL_SCALE_MIN)


def _trajectory_consistency(spill: dict, vessel: dict) -> float:
    """
    Calculate whether vessel's recent movement is directionally compatible
    with assumed spill drift direction.

    Uses cosine similarity between vessel's average course vector and drift vector.
    This is a PROTOTYPE drift assumption — not real ocean-current modeling.
    """
    if not vessel.get("trajectory") or len(vessel["trajectory"]) < 2:
        return 0.5  # insufficient data

    spill_time = datetime.fromisoformat(spill["detection_timestamp"].replace("Z", "+00:00"))

    # Consider last 6 hours of trajectory before spill
    recent = [
        p
        for p in vessel["trajectory"]
        if (spill_time - datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00"))).total_seconds()
        <= 6 * 3600
    ]

    if len(recent) < 2:
        return 0.5

    # Weighted average course vector (weighted by speed)
    vec_north = 0.0
    vec_east = 0.0
    total_speed = 0.0

    for p in recent:
        speed = p.get("speed_kn", 0.0)
        course_deg = p.get("course_deg", 0.0)
        course_rad = radians(course_deg)
        # North component = speed * cos(course), East = speed * sin(course)
        vec_north += speed * cos(course_rad)
        vec_east += speed * sin(course_rad)
        total_speed += speed

    if total_speed == 0:
        return 0.5

    vessel_course_n = vec_north / total_speed
    vessel_course_e = vec_east / total_speed

    # Drift vector (prototype default: South-East)
    drift_n = spill.get("drift_vector_km_per_hr", DEFAULT_DRIFT_VECTOR_KM_HR).get("north", -0.5)
    drift_e = spill.get("drift_vector_km_per_hr", DEFAULT_DRIFT_VECTOR_KM_HR).get("east", 0.5)

    drift_mag = sqrt(drift_n ** 2 + drift_e ** 2)
    if drift_mag == 0:
        return 0.5

    drift_n /= drift_mag
    drift_e /= drift_mag

    # Cosine similarity: 1 = same direction, -1 = opposite
    cos_sim = vessel_course_n * drift_n + vessel_course_e * drift_e

    # Map [-1, 1] → [0, 1]
    return _clamp((cos_sim + 1) / 2)


def _explanation(
    name: str,
    spatial: float,
    temporal: float,
    trajectory: float,
    score: float,
) -> str:
    spatial_desc = "close" if spatial >= 0.6 else ("moderate" if spatial >= 0.3 else "far")
    temporal_desc = "recent" if temporal >= 0.6 else ("moderate" if temporal >= 0.3 else "distant")
    trajectory_desc = (
        "aligned" if trajectory >= 0.6 else ("partially aligned" if trajectory >= 0.3 else "misaligned")
    )

    return (
        f"{name} is a SIMULATED candidate for investigative ranking only. "
        f"Spatial consistency: {spatial_desc} ({spatial:.2f}) — "
        f"vessel track passed near the detected spill. "
        f"Temporal consistency: {temporal_desc} ({temporal:.2f}) — "
        f"vessel was observed near the detection time. "
        f"Trajectory consistency with assumed drift: {trajectory_desc} ({trajectory:.2f}) — "
        f"vessel movement {'supports' if trajectory >= 0.5 else 'does not strongly support'} "
        f"the prototype drift direction (PROTOTYPE DEFAULT: South-East). "
        f"Overall rank score: {score:.2f}. "
        "This is not a finding of legal responsibility and is not a calibrated probability."
    )


def score_candidates(spill: dict, vessels: list[dict]) -> list[dict]:
    ranked = []
    for vessel in vessels:
        spatial = _spatial_consistency(spill, vessel)
        temporal = _temporal_consistency(spill, vessel)
        trajectory = _trajectory_consistency(spill, vessel)

        score = (
            WEIGHT_SPATIAL * spatial
            + WEIGHT_TEMPORAL * temporal
            + WEIGHT_TRAJECTORY * trajectory
        )
        score = round(_clamp(score), 3)

        ranked.append(
            {
                "vessel_id": vessel["vessel_id"],
                "name": vessel["name"],
                "coordinates": vessel["coordinates"],
                "timestamp": vessel["timestamp"],
                "spatial_consistency": round(spatial, 3),
                "temporal_consistency": round(temporal, 3),
                "trajectory_consistency": round(trajectory, 3),
                "attribution_score": score,
                "explanation": _explanation(
                    vessel["name"], spatial, temporal, trajectory, score
                ),
                "trajectory": [[p["lon"], p["lat"]] for p in vessel.get("trajectory", [])],
            }
        )

    ranked.sort(key=lambda item: item["attribution_score"], reverse=True)
    return ranked