import pytest
from fastapi.testclient import TestClient


def test_app_initialization():
    """Test FastAPI app can be imported and initialized"""
    from src.main import app

    assert app is not None
    assert app.title == "Frank the Assistant"


def test_health_endpoint():
    """Test health check endpoint exists"""
    from src.main import app
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
