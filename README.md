# Cyber Attack Decision Workbench

A four-page decision-support application for comparing cyber attack scenarios, FAIR-style financial risk, and security control investments.

## Project structure

- `frontend/` — React user interface, run and built by Vite
- `backend/` — Flask API and, later, the NumPy/SciPy simulation model
- `requirements.txt` — Python dependencies

## Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Run the backend

From the project root:

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m backend.app
```

The API will be available at `http://127.0.0.1:5000/api/health`.

During development, Vite forwards browser requests beginning with `/api` to Flask. For the final submission, Flask will serve the optimized files produced by `npm run build`.

## Current milestone

- Four real React routes
- Shared scenario, mode, control, readiness, and live simulation state
- Responsive base styling
- Flask health, evidence-rich config, and simulation endpoints
- Production-build serving path prepared
- Fixed-seed Monte Carlo models for all four scenarios with baseline/residual results
- Compact histogram bins, P50/P90/P95, threshold probabilities, control economics, and sensitivity drivers
- Automated model tests
- Interactive Plotly baseline/residual histogram, sensitivity chart, and scenario heat map
- Detailed Launch-Day DDoS attack chain with playback, MITRE/STRIDE mappings, control interruption points, evidence labels, and source links

The Launch-Day DDoS model is implemented. The other three scenario models are deliberately marked as planned so the interface never presents unsupported estimates as completed analysis.

## Run the automated checks

With the Python environment activated:

```bash
python3 -m unittest discover -s backend/tests -v
```

Then verify the frontend production build:

```bash
cd frontend
npm run build
```
