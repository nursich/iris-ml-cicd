"""Loading and validating the Iris dataset (UCI, DOI 10.24432/C56C76)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "iris.csv"

FEATURES = [
    "sepal_length_cm",
    "sepal_width_cm",
    "petal_length_cm",
    "petal_width_cm",
]
TARGET = "species"
CLASSES = ["Iris-setosa", "Iris-versicolor", "Iris-virginica"]

# SHA-256 of data/iris.csv. If the data changes, the tests fail.
EXPECTED_SHA256 = (
    "7866a81bd4601f74577a9cd0a7f03b35dcb0c361cf1e578a3930697524b0edeb"
)


def file_sha256(path: Path | str) -> str:
    """Return the SHA-256 hex digest of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(df: pd.DataFrame) -> None:
    """Raise ValueError if the dataframe does not look like the Iris data."""
    expected_cols = FEATURES + [TARGET]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if df[expected_cols].isnull().any().any():
        raise ValueError("Dataset contains missing values")
    unknown = set(df[TARGET]) - set(CLASSES)
    if unknown:
        raise ValueError(f"Unknown class labels: {sorted(unknown)}")
    if (df[FEATURES] <= 0).any().any():
        raise ValueError("All measurements must be positive (cm)")


def load_iris(path: Path | str = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load the Iris CSV and validate its structure."""
    df = pd.read_csv(path)
    validate(df)
    return df
