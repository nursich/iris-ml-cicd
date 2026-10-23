import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from iris_classifier.data import load_iris  # noqa: E402
from iris_classifier.model import train_and_evaluate  # noqa: E402


@pytest.fixture(scope="session")
def iris_df():
    return load_iris()


@pytest.fixture(scope="session")
def trained(iris_df):
    """Train once per test session: returns (model, metrics)."""
    return train_and_evaluate(iris_df)
