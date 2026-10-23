"""REST API that serves the trained Iris classifier.

Endpoints:
    GET  /health   - liveness/readiness check
    GET  /info     - model version and evaluation metrics
    POST /predict  - JSON with the four measurements in cm
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from flask import Flask, jsonify, request

from . import __version__
from .data import FEATURES
from .model import load_model, predict_one

MODEL_DIR = Path(os.environ.get("MODEL_DIR", "models"))


def create_app(model=None, metrics: dict | None = None) -> Flask:
    app = Flask(__name__)

    if model is None:
        model = load_model(MODEL_DIR / "model.joblib")
    if metrics is None:
        metrics_path = MODEL_DIR / "metrics.json"
        metrics = (
            json.loads(metrics_path.read_text()) if metrics_path.exists() else {}
        )

    @app.get("/health")
    def health():
        return jsonify(status="ok", version=__version__)

    @app.get("/info")
    def info():
        return jsonify(
            version=__version__,
            features=FEATURES,
            metrics=metrics,
            hostname=os.environ.get("HOSTNAME", "local"),
        )

    @app.post("/predict")
    def predict():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="Request body must be a JSON object"), 400
        try:
            result = predict_one(model, payload)
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        return jsonify(result)

    return app
