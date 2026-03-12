from fastapi.testclient import TestClient

from main.backend.server import app

client = TestClient(app)


def test_root_returns_200():
    response = client.get("/")
    assert response.status_code == 200


def test_root_returns_hello_world():
    response = client.get("/")
    assert response.json() == {"message": "Hello World"}


def test_root_response_is_json():
    response = client.get("/")
    assert "application/json" in response.headers["content-type"]
