# Cyber Attack Decision Workbench

A four-page decision-support application for comparing cyber attack scenarios, FAIR-style financial risk, and security control investments.

## Project structure

- `frontend/` — React user interface, run and built by Vite
- `backend/` — Flask API and NumPy/SciPy simulation model
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
- Compact histogram bins, P50/P90/P95/P99, $10M/$25M/$50M/$100M threshold probabilities, control economics, and sensitivity drivers
- Automated model tests
- Interactive Plotly baseline/residual histogram, sensitivity chart, and scenario heat map
- Detailed Launch-Day DDoS showcase plus selectable four-stage paths for Source Code Theft, Insider Leak, and Fake Downloads & Phishing, with playback, MITRE/STRIDE mappings, control interruption points, evidence labels, and source links
- Scenario-aware control categorization with recommendations, applicability, exact model effects, cost ranges, implementation time, confidence, and cross-scenario coverage
- All-scenario portfolio planner that counts shared controls once, combines trial-by-trial losses, uses DDoS launch-event exposure plus annual exposure for the other scenarios, and reports combined cost, loss reduction, net benefit, ROSI, and scenario-level impact
- Expandable methodology and evidence register with input provenance, rationale, confidence, source scope, access dates, and framework disclaimers
- Transparent team readiness index calculated from Prevent, Detect, Respond, and Recover dimensions plus scenario-relevant control impacts
- Demo-safe loading and connection states with exact-match browser caching for scenario and portfolio calculations
- Retry controls and clear saved-result timestamps when Flask is temporarily unavailable
- Lazy-loaded Plotly bundle so non-chart pages start without downloading the chart engine
- Global demo reset that returns to Launch-Day DDoS, launch-event mode, recommended controls, the first attack stage, and selected-scenario planning
- Editable low/most-likely/high FAIR-style inputs with client and server validation, explicit apply/reset behavior, and exact-input result caching
- Evidence-anchored assumptions are the official default; the original app estimates remain available as a clearly labelled comparison profile
- Secondary loss has an explicit occurrence probability, so it is not automatically added after every successful event
- Baseline and residual calculations reuse the same random draws, isolating the effect of selected controls
- DDoS primary loss exposes its component calculation, assumptions, evidence links, and review warnings
- Spearman rank sensitivity and low-to-high tornado sensitivity provide two understandable views of influential model inputs
- Control cost uses the expected value of its triangular range: `(low + most likely + high) / 3`
- Per-control effectiveness evidence with team-estimate labels, rationale, confidence, methodology URL, access date, and validation scope

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
