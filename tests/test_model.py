import json

import pytest

from iris_classifier import train
from iris_classifier.model import (
    load_model,
    predict_one,
    save_model,
    train_and_evaluate,
)

SETOSA = {"sepal_length_cm": 5.1, "sepal_width_cm": 3.5,
          "petal_length_cm": 1.4, "petal_width_cm": 0.2}
VIRGINICA = {"sepal_length_cm": 6.3, "sepal_width_cm": 3.3,
             "petal_length_cm": 6.0, "petal_width_cm": 2.5}


def test_accuracy_quality_gate(trained):
    """The model must reach at least 90% accuracy on the held-out set."""
    _, metrics = trained
    assert metrics.accuracy >= 0.90
    assert metrics.f1_macro >= 0.90


def test_split_sizes(trained):
    _, metrics = trained
    assert (metrics.n_train, metrics.n_test) == (120, 30)


def test_training_is_reproducible(iris_df, trained):
    """Same data + same seed => identical results (reproducibility)."""
    _, first = trained
    _, second = train_and_evaluate(iris_df)
    assert first == second


def test_predicts_known_samples(trained):
    model, _ = trained
    # Sample 1 and sample 101 of the UCI dataset
    assert predict_one(model, SETOSA)["species"] == "Iris-setosa"
    assert predict_one(model, VIRGINICA)["species"] == "Iris-virginica"


def test_probabilities_sum_to_one(trained):
    model, _ = trained
    probs = predict_one(model, SETOSA)["probabilities"]
    assert sum(probs.values()) == pytest.approx(1.0, abs=1e-3)


@pytest.mark.parametrize(
    "bad",
    [
        {"sepal_length_cm": 5.1},
        {**SETOSA, "petal_width_cm": "abc"},
        {**SETOSA, "petal_width_cm": -0.2},
    ],
)
def test_predict_rejects_bad_input(trained, bad):
    model, _ = trained
    with pytest.raises(ValueError):
        predict_one(model, bad)


def test_save_and_load_roundtrip(trained, tmp_path):
    model, _ = trained
    path = tmp_path / "model.joblib"
    save_model(model, path)
    loaded = load_model(path)
    assert predict_one(loaded, SETOSA) == predict_one(model, SETOSA)


def test_train_cli_writes_artifacts(tmp_path):
    report = train.main(["--out", str(tmp_path)])
    assert (tmp_path / "model.joblib").exists()
    saved = json.loads((tmp_path / "metrics.json").read_text())
    assert saved["accuracy"] == report["accuracy"]
    assert len(saved["data_sha256"]) == 64


def test_train_cli_quality_gate_fails(tmp_path):
    with pytest.raises(SystemExit):
        train.main(["--out", str(tmp_path), "--min-accuracy", "1.01"])
