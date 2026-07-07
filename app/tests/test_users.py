import pytest


@pytest.mark.anyio
async def test_create_user(
    client,
):
    response = await client.post(
        "/api/v1/users",
        json={
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["email"] == "john@example.com"


@pytest.mark.anyio
async def test_get_user(
    client,
):
    create_response = await client.post(
        "/api/v1/users",
        json={
            "email": "jane@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
        },
    )

    user_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["id"] == user_id


@pytest.mark.anyio
async def test_update_user(
    client,
):
    create_response = await client.post(
        "/api/v1/users",
        json={
            "email": "update@example.com",
            "first_name": "Old",
            "last_name": "Name",
        },
    )

    user_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/users/{user_id}",
        json={
            "first_name": "New",
        },
    )

    assert response.status_code == 200
    assert response.json()["first_name"] == "New"


@pytest.mark.anyio
async def test_delete_user(
    client,
):
    create_response = await client.post(
        "/api/v1/users",
        json={
            "email": "delete@example.com",
            "first_name": "Delete",
            "last_name": "Me",
        },
    )

    user_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/users/{user_id}")

    assert response.status_code == 204
