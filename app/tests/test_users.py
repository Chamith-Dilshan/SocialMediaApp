import pytest


@pytest.mark.anyio
async def test_create_user(client):
    response = await client.post(
        "/api/v1/users",
        json={
            "email": "john@example.com",
            "password": "s3cr3t123",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "john@example.com"
    assert "password" not in body


@pytest.mark.anyio
async def test_create_duplicate_user_returns_conflict(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "strong-pass",
        "first_name": "Duplicate",
        "last_name": "User",
    }

    first = await client.post("/api/v1/users", json=payload)
    second = await client.post("/api/v1/users", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["message"] == "Email already exists"


@pytest.mark.anyio
async def test_get_user(client):
    create_response = await client.post(
        "/api/v1/users",
        json={
            "email": "jane@example.com",
            "password": "s3cr3t123",
            "first_name": "Jane",
            "last_name": "Doe",
        },
    )

    user_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["id"] == user_id


@pytest.mark.anyio
async def test_get_missing_user_returns_not_found(client):
    response = await client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json()["message"] == "User not found"


@pytest.mark.anyio
async def test_update_user(client):
    create_response = await client.post(
        "/api/v1/users",
        json={
            "email": "update@example.com",
            "password": "s3cr3t123",
            "first_name": "Old",
            "last_name": "Name",
        },
    )

    user_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/users/{user_id}",
        json={"first_name": "New"},
    )

    assert response.status_code == 200
    assert response.json()["first_name"] == "New"


@pytest.mark.anyio
async def test_create_user_with_invalid_payload_returns_validation_error(client):
    response = await client.post(
        "/api/v1/users",
        json={
            "email": "invalid-email",
            "password": "",
            "first_name": "",
            "last_name": "Doe",
        },
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_delete_user(client):
    create_response = await client.post(
        "/api/v1/users",
        json={
            "email": "delete@example.com",
            "password": "s3cr3t123",
            "first_name": "Delete",
            "last_name": "Me",
        },
    )

    user_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/users/{user_id}")

    assert response.status_code == 204


@pytest.mark.anyio
async def test_delete_missing_user_returns_not_found(client):
    response = await client.delete("/api/v1/users/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json()["message"] == "User not found"
