# OilGuard (Stage 1)

SIH-style MVP: **fully simulated** oil-spill investigation.

Upload any image. A small Python API returns demo spill facts and three
demo ships. The website shows them on a Leaflet map. Nothing here is a
real satellite detection, real AIS lookup, or a legal finding.

**Every result is labeled `SIMULATED / DEMO DATA`.**
The attribution score is a simple ranking heuristic. It is **not** legal
guilt and **not** a statistically calibrated probability.

## What talks to what

```
Browser (React)
    POST /api/analyze  (the image file)
        -> FastAPI
            -> simulated detector
            -> simulated AIS
            -> heuristic ranking
        <- JSON investigation result
    Leaflet map draws spill + ships
```

Later you can replace `backend/app/services/detector.py` and
`backend/app/services/ais.py` with real components. Keep the same JSON
fields so the frontend does not need a rewrite.

## Run locally (Windows PowerShell)

Use **two terminals**. Start the backend first.

### 1. Backend (FastAPI)

```powershell
cd "C:\Users\amit nagar\Projects\oilguard\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs (optional): http://127.0.0.1:8000/docs

If PowerShell blocks the venv script, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate again.

### 2. Frontend (React + Vite)

```powershell
cd "C:\Users\amit nagar\Projects\oilguard\frontend"
npm install
npm run dev
```

Open the URL Vite prints, usually http://localhost:5173

The frontend proxies `/api` to the backend, so keep both processes running.

## File map (beginner)

| Path | Why it exists |
| --- | --- |
| `backend/app/main.py` | HTTP server: `/api/analyze` |
| `backend/app/schemas.py` | JSON field names (the contract) |
| `backend/app/services/detector.py` | Fake spill from filename/size |
| `backend/app/services/ais.py` | Three fake nearby ships |
| `backend/app/services/attribution.py` | Demo ranking scores + explanations |
| `frontend/src/api.js` | Sends the image to the API |
| `frontend/src/App.jsx` | Page layout and upload flow |
| `frontend/src/components/UploadPanel.jsx` | File picker |
| `frontend/src/components/InvestigationDashboard.jsx` | Results dashboard |
| `frontend/src/components/SpillMap.jsx` | Leaflet map |
| `frontend/src/components/CandidateCard.jsx` | One candidate vessel |
| `frontend/src/styles.css` | Look and feel |

## Not in Stage 1

No real satellites, AIS APIs, machine learning, database, login,
blockchain, or chatbot.
