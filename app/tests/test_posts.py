import pytest


@pytest.mark.anyio
async def test_create_post(client):
    user_response = await client.post(
        "/api/v1/users",
        json={
            "email": "author@example.com",
            "password": "s3cr3t123",
            "first_name": "Author",
            "last_name": "User",
        },
    )
    user_id = user_response.json()["id"]

    response = await client.post(
        "/api/v1/posts",
        json={
            "title": "Hello world",
            "content": "This is a test post",
            "published": True,
            "user_id": user_id,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Hello world"
    assert body["user_id"] == user_id


@pytest.mark.anyio
async def test_get_missing_post_returns_not_found(client):
    response = await client.get("/api/v1/posts/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json()["message"] == "Post not found"


@pytest.mark.anyio
async def test_update_post(client):
    user_response = await client.post(
        "/api/v1/users",
        json={
            "email": "editor@example.com",
            "password": "s3cr3t123",
            "first_name": "Editor",
            "last_name": "User",
        },
    )
    user_id = user_response.json()["id"]

    create_response = await client.post(
        "/api/v1/posts",
        json={
            "title": "Draft",
            "content": "Will be updated",
            "published": False,
            "user_id": user_id,
        },
    )
    post_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/posts/{post_id}",
        json={"title": "Updated", "published": True},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated"
    assert response.json()["published"] is True


@pytest.mark.anyio
async def test_delete_post(client):
    user_response = await client.post(
        "/api/v1/users",
        json={
            "email": "deleter@example.com",
            "password": "s3cr3t123",
            "first_name": "Delete",
            "last_name": "User",
        },
    )
    user_id = user_response.json()["id"]

    create_response = await client.post(
        "/api/v1/posts",
        json={
            "title": "Delete me",
            "content": "Should be removed",
            "published": True,
            "user_id": user_id,
        },
    )
    post_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/posts/{post_id}")

    assert response.status_code == 204
