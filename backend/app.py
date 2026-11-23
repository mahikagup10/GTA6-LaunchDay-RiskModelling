from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from backend.data.config import (
    ATTACK_CHAIN,
    ATTACK_PATHS,
    BUILD_THEFT_PATH,
    CONTROLS,
    CRITICAL_ASSETS,
    EVIDENCE_CLASSES,
    METHODOLOGY,
    MODEL_VERSION,
    READINESS_MODEL,
    SCENARIOS,
    SOURCES,
    TIME_BASES,
    WATCHLIST,
)
from backend.model.fair import (
    DEFAULT_SEED,
    DEFAULT_TRIALS,
    PRIORITY_WEIGHTS,
    control_priorities,
    readiness,
    run_portfolio,
    run_simulation,
    scenario_overview,
)


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"

app = Flask(__name__, static_folder=None)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})


def _payload():
    return request.get_json(silent=True) or {}


def _bad_request(error):
    return jsonify({"error": str(error)}), 400


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "cyber-attack-workbench-api", "modelVersion": MODEL_VERSION})


@app.get("/api/config")
def config():
    return jsonify(
        {
            "scenarios": SCENARIOS,
            "controls": CONTROLS,
            "attackChain": ATTACK_CHAIN,
            "buildTheftPath": BUILD_THEFT_PATH,
            "attackPaths": ATTACK_PATHS,
            "criticalAssets": CRITICAL_ASSETS,
            "watchlist": WATCHLIST,
            "readinessModel": READINESS_MODEL,
            "sources": SOURCES,
            "methodology": METHODOLOGY,
            "evidenceClasses": EVIDENCE_CLASSES,
            "timeBases": TIME_BASES,
            "priorityWeights": PRIORITY_WEIGHTS,
            "model": {
                "trials": DEFAULT_TRIALS,
                "seed": DEFAULT_SEED,
                "version": MODEL_VERSION,
                "status": "all-scenarios-implemented",
            },
        }
    )


@app.post("/api/simulate")
def simulate():
    payload = _payload()
    try:
        result = run_simulation(
            scenario_id=payload.get("scenarioId", "launch-ddos"),
            control_ids=payload.get("controlIds", []),
            mode=payload.get("analysisMode"),
            trials=payload.get("trials", DEFAULT_TRIALS),
            seed=payload.get("seed", DEFAULT_SEED),
        )
    except (TypeError, ValueError) as error:
        return _bad_request(error)
    return jsonify(result)


@app.post("/api/portfolio")
def portfolio():
    payload = _payload()
    try:
        result = run_portfolio(
            control_ids=payload.get("controlIds"),
            mode=payload.get("analysisMode"),
            trials=payload.get("trials", DEFAULT_TRIALS),
            seed=payload.get("seed", DEFAULT_SEED),
        )
    except (TypeError, ValueError) as error:
        return _bad_request(error)
    return jsonify(result)


@app.get("/api/overview")
def overview():
    try:
        trials = int(request.args.get("trials", DEFAULT_TRIALS))
        seed = int(request.args.get("seed", DEFAULT_SEED))
        return jsonify(scenario_overview(trials=trials, seed=seed))
    except (TypeError, ValueError) as error:
        return _bad_request(error)


@app.get("/api/controls/priority")
def priorities():
    try:
        trials = int(request.args.get("trials", DEFAULT_TRIALS))
        seed = int(request.args.get("seed", DEFAULT_SEED))
        return jsonify(control_priorities(trials=trials, seed=seed))
    except (TypeError, ValueError) as error:
        return _bad_request(error)


@app.post("/api/readiness")
def readiness_endpoint():
    payload = _payload()
    return jsonify(readiness(payload.get("controlIds", [])))


@app.get("/assets/<path:filename>")
def serve_frontend_asset(filename):
    return send_from_directory(FRONTEND_DIST / "assets", filename)


@app.get("/")
@app.get("/<path:path>")
def serve_frontend(path=""):
    if path.startswith("api/"):
        return jsonify({"error": "Unknown API route"}), 404
    if not FRONTEND_DIST.exists():
        return jsonify(
            {
                "message": "Frontend build not found. Run the Vite development server during development.",
                "api_health": "/api/health",
            }
        )

    requested_file = FRONTEND_DIST / path
    if path and requested_file.is_file():
        return send_from_directory(FRONTEND_DIST, path)
    return send_from_directory(FRONTEND_DIST, "index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
