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
- Scenario-aware control categorization with recommendations, applicability, exact model effects, cost ranges, implementation time, confidence, and cross-scenario coverage
- All-scenario portfolio planner that counts shared controls once and reports combined cost, loss reduction, net benefit, ROSI, and scenario-level impact
- Expandable methodology and evidence register with input provenance, rationale, confidence, source scope, access dates, and framework disclaimers
- Transparent team readiness index calculated from Prevent, Detect, Respond, and Recover dimensions plus scenario-relevant control impacts
- Demo-safe loading and connection states with exact-match browser caching for scenario and portfolio calculations
- Retry controls and clear saved-result timestamps when Flask is temporarily unavailable
- Lazy-loaded Plotly bundle so non-chart pages start without downloading the chart engine
- Global demo reset that returns to Launch-Day DDoS, launch-event mode, recommended controls, the first attack stage, and selected-scenario planning

All four scenarios have reproducible FAIR-style models. Launch-Day DDoS remains the deeply detailed attack-path scenario and primary demo story.

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
