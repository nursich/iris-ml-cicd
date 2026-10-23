import pytest

from iris_classifier.api import create_app
from iris_classifier.model import metrics_dict

SETOSA = {"sepal_length_cm": 5.1, "sepal_width_cm": 3.5,
          "petal_length_cm": 1.4, "petal_width_cm": 0.2}


@pytest.fixture()
def client(trained):
    model, metrics = trained
    app = create_app(model=model, metrics=metrics_dict(metrics))
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_info_contains_metrics(client):
    data = client.get("/info").get_json()
    assert data["metrics"]["accuracy"] >= 0.9
    assert len(data["features"]) == 4


def test_predict_ok(client):
    resp = client.post("/predict", json=SETOSA)
    assert resp.status_code == 200
    assert resp.get_json()["species"] == "Iris-setosa"


def test_predict_missing_field(client):
    resp = client.post("/predict", json={"sepal_length_cm": 5.1})
    assert resp.status_code == 400
    assert "Missing features" in resp.get_json()["error"]


def test_predict_not_json(client):
    resp = client.post("/predict", data="hello",
                       content_type="text/plain")
    assert resp.status_code == 400
