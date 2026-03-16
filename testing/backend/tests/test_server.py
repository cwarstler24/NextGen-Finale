from fastapi.testclient import TestClient

from main.backend.server import app

client = TestClient(app)


def test_root_returns_200():
    response = client.get("/")
    assert response.status_code == 200


def test_root_returns_hello_world():
    response = client.get("/")
    assert response.json() == {
        "message": "Restaurant Order API",
        "version": "1.0.0",
        "status": "operational",
    }


def test_root_response_is_json():
    response = client.get("/")
    assert "application/json" in response.headers["content-type"]
