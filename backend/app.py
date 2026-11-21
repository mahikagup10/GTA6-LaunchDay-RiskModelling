from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from backend.data.config import ATTACK_CHAIN, CONTROLS, SCENARIOS, SOURCES
from backend.model.fair import DEFAULT_SEED, DEFAULT_TRIALS, run_simulation


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
            "controls": CONTROLS,
            "attackChain": ATTACK_CHAIN,
            "sources": SOURCES,
            "model": {
                "trials": DEFAULT_TRIALS,
                "seed": DEFAULT_SEED,
                "status": "launch-ddos-implemented",
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

