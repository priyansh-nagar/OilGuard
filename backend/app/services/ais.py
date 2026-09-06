"""
SIMULATED AIS (ship tracking) candidates.

A real system would query AIS around the spill time and location.
Here we invent three nearby vessels with plausible names and IDs.

Swap this file later without changing the frontend.
"""

from datetime import datetime, timedelta, timezone
import math


DEMO_VESSELS = [
    {
        "vessel_id": "IMO9234101",
        "name": "MV Ocean Pioneer",
        "base_dlat": 0.042,
        "base_dlon": -0.031,
        "minutes_before": 35,
        "speed_kn": 12.0,
        "course_deg": 135.0,  # SE direction (toward spill)
    },
    {
        "vessel_id": "IMO9418826",
        "name": "MT Gulf Harmony",
        "base_dlat": -0.021,
        "base_dlon": 0.055,
        "minutes_before": 110,
        "speed_kn": 10.5,
        "course_deg": 315.0,  # NW direction (away from spill)
    },
    {
        "vessel_id": "IMO8507733",
        "name": "FV Sagar Kiran",
        "base_dlat": 0.088,
        "base_dlon": 0.019,
        "minutes_before": 18,
        "speed_kn": 8.0,
        "course_deg": 180.0,  # South direction
    },
]


def _generate_trajectory(
    spill_center: dict,
    vessel: dict,
    spill_time: datetime,
    num_historical_points: int = 10,
    interval_minutes: int = 30,
) -> list[dict]:
    """
    Generate a deterministic time-ordered AIS trajectory for a vessel.

    The trajectory consists of:
    1. Historical points going BACKWARD from the last known AIS position
       (at minutes_before detection) for ~5 hours
    2. A final projected point AT spill detection time (dead reckoning
       from last known position using course/speed)

    This simulates: we have historical AIS up to minutes_before, and
    we project forward to estimate position at spill time.

    Each point contains: lat, lon, timestamp, speed_kn, course_deg.
    """
    # Last known AIS position (at minutes_before from spill)
    known_lat = spill_center["lat"] + vessel["base_dlat"]
    known_lon = spill_center["lon"] + vessel["base_dlon"]
    known_time = spill_time - timedelta(minutes=vessel["minutes_before"])

    speed_kn = vessel["speed_kn"]
    course_deg = vessel["course_deg"]

    # Convert speed to degrees per minute (approximate)
    # 1 knot = 1.852 km/h = 0.0308667 km/min
    # 1 degree lat ≈ 111 km, 1 degree lon ≈ 111 * cos(lat) km
    lat_rad = math.radians(known_lat)
    km_per_min = speed_kn * 1.852 / 60.0
    deg_per_min_lat = km_per_min / 111.0
    deg_per_min_lon = km_per_min / (111.0 * math.cos(lat_rad))

    # Course to vector components (0° = North, 90° = East)
    course_rad = math.radians(course_deg)
    dlat_per_min = deg_per_min_lat * math.cos(course_rad)
    dlon_per_min = deg_per_min_lon * math.sin(course_rad)

    trajectory = []

    # 1. Historical points: go BACKWARD from known position
    for i in range(num_historical_points):
        point_time = known_time - timedelta(minutes=(i + 1) * interval_minutes)
        # Position at this time (going backwards along course)
        lat = known_lat - (dlat_per_min * (i + 1) * interval_minutes)
        lon = known_lon - (dlon_per_min * (i + 1) * interval_minutes)

        trajectory.append(
            {
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "timestamp": point_time.replace(tzinfo=timezone.utc).isoformat(timespec="seconds"),
                "speed_kn": speed_kn,
                "course_deg": course_deg,
            }
        )

    # 2. The known AIS position (last real observation)
    trajectory.append(
        {
            "lat": round(known_lat, 6),
            "lon": round(known_lon, 6),
            "timestamp": known_time.replace(tzinfo=timezone.utc).isoformat(timespec="seconds"),
            "speed_kn": speed_kn,
            "course_deg": course_deg,
        }
    )

    # 3. Projected position AT spill time (dead reckoning forward)
    minutes_to_spill = vessel["minutes_before"]
    projected_lat = known_lat + (dlat_per_min * minutes_to_spill)
    projected_lon = known_lon + (dlon_per_min * minutes_to_spill)

    trajectory.append(
        {
            "lat": round(projected_lat, 6),
            "lon": round(projected_lon, 6),
            "timestamp": spill_time.replace(tzinfo=timezone.utc).isoformat(timespec="seconds"),
            "speed_kn": speed_kn,
            "course_deg": course_deg,
        }
    )

    # Trajectory is already time-ordered (oldest first, newest last = spill time)
    return trajectory


def simulate_ais_candidates(spill: dict) -> list[dict]:
    spill_time = datetime.fromisoformat(spill["detection_timestamp"])
    center = spill["center"]
    vessels = []
    for item in DEMO_VESSELS:
        observed_at = spill_time - timedelta(minutes=item["minutes_before"])
        trajectory = _generate_trajectory(center, item, spill_time)
        vessels.append(
            {
                "vessel_id": item["vessel_id"],
                "name": item["name"],
                "coordinates": {
                    "lat": round(center["lat"] + item["base_dlat"], 4),
                    "lon": round(center["lon"] + item["base_dlon"], 4),
                },
                "timestamp": observed_at.replace(tzinfo=timezone.utc).isoformat(timespec="seconds"),
                "minutes_before_detection": item["minutes_before"],
                "trajectory": trajectory,
            }
        )
    return vessels