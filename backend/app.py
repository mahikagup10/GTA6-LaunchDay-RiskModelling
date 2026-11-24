from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
try:
    from flask_cors import CORS
except ImportError:
    def CORS(flask_app, resources=None):
        """Small development fallback when flask-cors has not been installed yet."""
        @flask_app.after_request
        def add_development_cors_headers(response):
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            return response

from backend.data.config import ASSETS, ATTACK_CHAIN, ATTACK_CHAINS, ATTACK_PATH_DETAILS, CONTROLS, METHODOLOGY, SCENARIOS, SOURCES
from backend.model.fair import DEFAULT_SEED, DEFAULT_TRIALS, run_portfolio, run_simulation


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"

app = Flask(__name__, static_folder=None)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "cyber-attack-workbench-api"})


@app.get("/api/config")
def config():
    return jsonify(
        {
            "scenarios": SCENARIOS,
            "assets": ASSETS,
            "controls": CONTROLS,
            "attackChain": ATTACK_CHAIN,
            "attackChains": ATTACK_CHAINS,
            "attackPathDetails": ATTACK_PATH_DETAILS,
            "sources": SOURCES,
            "methodology": METHODOLOGY,
            "model": {
                "trials": DEFAULT_TRIALS,
                "seed": DEFAULT_SEED,
                "status": "all-four-scenarios-implemented",
            },
        }
    )


@app.post("/api/simulate")
def simulate():
    payload = request.get_json(silent=True) or {}
    try:
        result = run_simulation(
            scenario_id=payload.get("scenarioId", "launch-ddos"),
            control_ids=payload.get("controlIds", []),
            mode=payload.get("analysisMode", "launch-event"),
            trials=payload.get("trials", DEFAULT_TRIALS),
            seed=payload.get("seed", DEFAULT_SEED),
            assumptions=payload.get("assumptions"),
            assumption_profile_id=payload.get("assumptionProfileId"),
        )
    except (TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400
    return jsonify(result)


@app.post("/api/portfolio")
def portfolio():
    payload = request.get_json(silent=True) or {}
    try:
        result = run_portfolio(
            control_ids=payload.get("controlIds"),
            mode=payload.get("analysisMode"),
            trials=payload.get("trials", DEFAULT_TRIALS),
            seed=payload.get("seed", DEFAULT_SEED),
            assumption_profile_id=payload.get("assumptionProfileId"),
        )
    except (TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400
    return jsonify(result)


@app.get("/assets/<path:filename>")
def serve_frontend_asset(filename):
    return send_from_directory(FRONTEND_DIST / "assets", filename)


@app.get("/")
@app.get("/<path:path>")
def serve_frontend(path=""):
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

