import pandas as pd
import pytest

from iris_classifier.data import (
    CLASSES,
    DEFAULT_DATA_PATH,
    EXPECTED_SHA256,
    FEATURES,
    file_sha256,
    validate,
)


def test_dataset_checksum_is_unchanged():
    """The data in the repository must be exactly the published dataset."""
    assert file_sha256(DEFAULT_DATA_PATH) == EXPECTED_SHA256


def test_shape_matches_uci_description(iris_df):
    # UCI: 150 instances, 4 features + 1 class column
    assert iris_df.shape == (150, 5)


def test_classes_are_balanced(iris_df):
    counts = iris_df["species"].value_counts().to_dict()
    assert counts == {c: 50 for c in CLASSES}


def test_no_missing_values(iris_df):
    assert not iris_df.isnull().any().any()


def test_known_corrected_samples(iris_df):
    """UCI documents errors in samples 35 and 38; we use corrected values."""
    assert iris_df.loc[34, FEATURES].tolist() == [4.9, 3.1, 1.5, 0.2]
    assert iris_df.loc[37, FEATURES].tolist() == [4.9, 3.6, 1.4, 0.1]


def test_validate_rejects_missing_column(iris_df):
    with pytest.raises(ValueError, match="Missing columns"):
        validate(iris_df.drop(columns=["petal_width_cm"]))


def test_validate_rejects_unknown_label(iris_df):
    bad = iris_df.copy()
    bad.loc[0, "species"] = "Iris-unknown"
    with pytest.raises(ValueError, match="Unknown class"):
        validate(bad)


def test_validate_rejects_negative_values(iris_df):
    bad = iris_df.copy()
    bad.loc[0, "sepal_length_cm"] = -1.0
    with pytest.raises(ValueError, match="positive"):
        validate(bad)


def test_validate_rejects_nan(iris_df):
    bad = iris_df.copy()
    bad.loc[0, "sepal_width_cm"] = pd.NA
    with pytest.raises(ValueError, match="missing"):
        validate(bad)
