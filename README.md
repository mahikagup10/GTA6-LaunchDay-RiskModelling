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

Four real React routes
Shared scenario, control, readiness, and live simulation state
Responsive base styling
Flask health, evidence-rich config, simulation, portfolio, overview, and control-priority endpoints
Production-build serving path prepared
Evidence-based FAIR-style Monte Carlo models for all four scenarios (10,000 trials, fixed seed 20261124) with baseline/residual results
Launch-Day DDoS is measured per seven-day launch event; Build Theft, Insider Leak, and Fake Downloads are annual (each scenario has a fixed time basis)
Component-level inputs (frequency, conditional success, outage hours, revenue at risk, response, refunds, support, secondary-effect probability and magnitude), each labeled Public fact, Derived value, Team estimate, or Model assumption with sources, rationale, confidence, owner, and reviewer
Controls change only the factors they influence, with low/likely/high effectiveness ranges; costs are reconciled to the scenario's time basis
Compact histogram bins, mean/P50/P90/P95/P99, threshold probabilities, control economics (net benefit, ROSI, cost of inaction, P95 reduction), Spearman sensitivity drivers, and a low/high tornado
Automated model, API, and data-integrity tests, including an independent analytic check of the Monte Carlo means
Interactive Plotly baseline/residual histogram, sensitivity and tornado charts, model-derived scenario heat map, and a control-to-scenario benefit heat map with click-through details
Seven-step Launch-Day DDoS attack chain with playback, MITRE/STRIDE mappings, affected assets, model factors, control interruption points, evidence labels, and source links; compact Build Theft comparison path and summary paths for the other two scenarios
Scenario-aware control catalogue with recommendations, applicability, exact model effects, NIST CSF 2.0 mapping, cost ranges and basis, implementation time, confidence, cross-scenario coverage, and a 100-point priority score with implementation sequence
All-scenario first-year portfolio planner (one launch event plus one year of the annual scenarios) that counts shared controls once
Expandable methodology and evidence register with loss event statements, input provenance, source register, and framework disclaimers
Launch Protection Readiness Index (weights 25/25/20/15/15, levels 0/0.5/1) showing current readiness and readiness with the selected plan
Demo-safe loading and connection states with exact-match browser caching for scenario and portfolio calculations
Retry controls and clear saved-result timestamps when Flask is temporarily unavailable
Lazy-loaded Plotly bundle so non-chart pages start without downloading the chart engine
Global demo reset that returns to Launch-Day DDoS, recommended controls, the first attack stage, and selected-scenario planning

All model inputs, controls, attack paths, and sources live in one file: backend/data/config.py. The engine is backend/model/fair.py.

Export the results package and model documentation

With the Python environment activated, from the project root:

python3 -m backend.model.export_results

This writes results/ (model_inputs.csv, control_catalogue.csv, scenario_results.csv, evidence_register.csv, results_package.json) and docs/FAIR_MODEL.md, so the report and slides reuse the exact numbers the app shows. Add --samples to also save every sampled input with its loss (results/samples/, git-ignored).

Run the automated checks

With the Python environment activated:

```bash
python3 -m unittest discover -s backend/tests -v
```

Then verify the frontend production build:

```bash
cd frontend
npm run build
```
