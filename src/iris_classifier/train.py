"""Command-line entry point: train the model and write artifacts.

Usage:
    python -m iris_classifier.train --out models/
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .data import DEFAULT_DATA_PATH, file_sha256, load_iris
from .model import metrics_dict, save_model, train_and_evaluate


def main(argv: list[str] | None = None) -> dict:
    parser = argparse.ArgumentParser(description="Train the Iris classifier")
    parser.add_argument("--data", default=str(DEFAULT_DATA_PATH))
    parser.add_argument("--out", default="models")
    parser.add_argument("--min-accuracy", type=float, default=0.90,
                        help="Fail if test accuracy is below this value")
    args = parser.parse_args(argv)

    df = load_iris(args.data)
    model, metrics = train_and_evaluate(df)

    out_dir = Path(args.out)
    save_model(model, out_dir / "model.joblib")
    report = metrics_dict(metrics)
    report.update(
        {
            "model_version": __version__,
            "data_sha256": file_sha256(args.data),
            "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        }
    )
    (out_dir / "metrics.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))

    if metrics.accuracy < args.min_accuracy:
        raise SystemExit(
            f"Accuracy {metrics.accuracy:.3f} is below the quality gate "
            f"{args.min_accuracy:.2f}"
        )
    return report


if __name__ == "__main__":
    main()
