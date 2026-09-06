# OilGuard

### AI-Powered Marine Oil Spill Detection & Vessel Investigation

OilGuard is an SIH-style MVP for detecting potential oil spills from uploaded SAR imagery and investigating nearby vessels that may be associated with a detected spill.

The system combines a trained **PyTorch SmallCNN** image-classification model with **simulated AIS vessel trajectories** and a deterministic vessel-attribution heuristic to demonstrate an end-to-end maritime intelligence workflow.

> **Important:** OilGuard is a prototype. Vessel attribution is a ranking based on spatial, temporal, and trajectory consistency. It is not legal proof of responsibility or a statistically calibrated probability of guilt.

---

## What OilGuard Does

```text
SAR Image Upload
       │
       ▼
┌─────────────────────┐
│   SmallCNN Model    │
│   PyTorch Inference │
└──────────┬──────────┘
           │
           ▼
   Oil Spill Detected?
       │         │
      YES        NO
       │         │
       ▼         ▼
 Spill Location  Clear
       │
       ▼
 Simulated AIS
 Vessel Trajectories
       │
       ▼
 Spatial + Temporal
 + Trajectory Analysis
       │
       ▼
 Candidate Vessel Ranking
       │
       ▼
 Maritime Investigation
 Dashboard
```

---

## Key Features

- 🛰️ **SAR Image Analysis**
  - Upload SAR imagery through the web interface.
  - Image preprocessing and inference are performed by the backend.

- 🤖 **Machine Learning Detection**
  - PyTorch-based SmallCNN binary classifier.
  - Classifies imagery as potential oil-spill / non-oil-spill.
  - Frozen detection threshold: **0.52**.

- 🌍 **Interactive Maritime Globe**
  - MapLibre GL JS with MapTiler satellite imagery.
  - Arabian Sea / western India investigation view.
  - Interactive zoom, pan and vessel selection.

- 🚢 **Vessel Tracking**
  - Displays candidate vessels around the detected spill.
  - Shows vessel trajectories.
  - Supports vessel playback.

- 📊 **Vessel Attribution Ranking**
  - Candidates are ranked using:
    - Spatial consistency
    - Temporal consistency
    - Trajectory consistency
  - Scores are deterministic and intended for demonstration.

- 🔎 **Investigation Dashboard**
  - Detection status
  - AI confidence
  - Detection coordinates
  - Spill visualization
  - Candidate vessel information
  - Investigation scores
  - Vessel trajectory playback

---

## Technology Stack

### Frontend

- React.js
- Vite
- JavaScript
- CSS
- MapLibre GL JS
- MapTiler

### Backend

- Python
- FastAPI
- REST API

### Machine Learning

- PyTorch
- SmallCNN
- Grayscale SAR image preprocessing

### Data

- SAR imagery
- Simulated AIS trajectories
- Prototype geospatial investigation data

---

## Project Structure

```text
OilGuard/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── services/
│   │       ├── detector.py
│   │       ├── ais.py
│   │       └── attribution.py
│   │
│   ├── ml/
│   │   └── outputs/
│   │       └── class_weight_25/
│   │           └── oil_spill_cnn_best.pt
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── components/
│   │   └── styles.css
│   ├── package.json
│   └── vite.config.js
│
├── data/
│
├── .gitignore
└── README.md
```

---

## Backend API

The main analysis endpoint is:

```text
POST /api/analyze
```

It accepts an uploaded image and returns the investigation result as JSON.

The response contains information such as:

```text
Detection status
AI confidence
Spill center
Estimated area
Detection timestamp
Candidate vessels
Vessel trajectories
Attribution scores
```

API documentation is available through FastAPI's interactive documentation:

```text
/docs
```

---

## Machine Learning Pipeline

The current detection pipeline uses:

```text
Input SAR Image
      │
      ▼
Grayscale Conversion
      │
      ▼
Float32 Normalization
      │
      ▼
SmallCNN
      │
      ▼
Oil Probability
      │
      ▼
Threshold = 0.52
      │
      ▼
Detection Result
```

The model uses a single binary logit with sigmoid-based oil probability.

The current model checkpoint is:

```text
backend/ml/outputs/class_weight_25/oil_spill_cnn_best.pt
```

---

## Vessel Attribution

OilGuard currently uses **simulated AIS trajectories** for the prototype.

Candidate vessels are evaluated using three components:

```text
Spatial Consistency       40%
Temporal Consistency      30%
Trajectory Consistency    30%
```

The system combines these components into an attribution ranking.

### Important

The attribution score represents **prototype investigative relevance**, not:

- Legal guilt
- Confirmed responsibility
- A statistically calibrated probability
- Proof that a vessel caused the spill

Real AIS data and validated ocean-drift modelling would be required for operational deployment.

---

## Spill Visualization

When a potential spill is detected, OilGuard displays a visual investigation zone around the prototype detection center.

The current spill coordinates and estimated area are part of the MVP demonstration and should not be interpreted as independently geolocated measurements produced by the image classifier.

---

## Data & Prototype Limitations

The current version is an **MVP / proof of concept**.

### Currently implemented

- Trained CNN inference
- SAR image upload
- Oil-spill classification
- Interactive globe
- Vessel visualization
- Simulated AIS trajectories
- Vessel trajectory playback
- Deterministic attribution ranking
- Investigation dashboard

### Currently simulated / prototype

- AIS vessel trajectories
- Vessel positions used for the demonstration
- Spill coordinates
- Spill area estimation
- Ocean-drift modelling
- Vessel attribution

### Not currently implemented

- Live satellite data feeds
- Live AIS API integration
- Production-grade ocean-current modelling
- Operational maritime surveillance
- Legal or enforcement-grade attribution
- User authentication
- Database-backed investigation history

---

## Running Locally

### 1. Backend

Open a terminal:

```powershell
cd "C:\Users\amit nagar\Projects\oilguard\backend"

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend API:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

### 2. Frontend

Open a second terminal:

```powershell
cd "C:\Users\amit nagar\Projects\oilguard\frontend"

npm install

npm run dev
```

Open the URL displayed by Vite, usually:

```text
http://localhost:5173
```

The frontend communicates with the FastAPI backend through the `/api` endpoint.

---

## Intended Workflow

```text
1. Upload SAR imagery
          ↓
2. Run AI inference
          ↓
3. Detect potential oil spill
          ↓
4. Display investigation zone
          ↓
5. Display candidate vessels
          ↓
6. Inspect vessel trajectories
          ↓
7. Compare spatial / temporal /
   trajectory consistency
          ↓
8. Rank candidate vessels
```

---

## Future Development

The current architecture is designed so that prototype components can be replaced with real systems without redesigning the complete frontend.

Potential future integrations include:

- Real satellite/SAR data sources
- Live AIS feeds
- Improved deep-learning architectures
- Oil-spill segmentation
- Real spill geolocation
- Ocean-current and wind data
- Physics-based oil drift modelling
- Historical vessel trajectory analysis
- Persistent investigation database
- Automated alerts
- Multi-satellite data fusion

---

## Disclaimer

**OilGuard is an experimental prototype developed for demonstration and hackathon purposes.**

The current AIS data, vessel trajectories, spill coordinates and attribution calculations are simulated or prototype data.

The AI model demonstrates the technical workflow for oil-spill image classification but should not be treated as an operational satellite-monitoring system without further validation.

**Vessel attribution results are investigative rankings only and must not be interpreted as legal findings, confirmed responsibility, or statistically calibrated probabilities.**
