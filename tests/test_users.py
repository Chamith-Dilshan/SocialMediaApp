from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to Fast API",
        "status": "healthy",
        "version": "1.0.0",
    }


def test_register_user():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "testuser1@gmail.com",
            "password": "12345678",
            "first_name": "testuser1",
            "last_name": "test",
        },
    )
    assert response.status_code == 201
