from httpx import AsyncClient

from app.tests.utils.constants import USERS_URL
from app.tests.utils.helpers import create_authenticated_user


# ===========================================================================
# GET /users
# ===========================================================================
class TestListUsers:
    async def test_list_users_success(
        self, client: AsyncClient, auth_headers: dict, user: dict
    ):
        response = await client.get(USERS_URL, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)
        assert data["total"] >= 1

    async def test_list_users_pagination(self, client: AsyncClient, auth_headers: dict):
        for _ in range(3):
            await create_authenticated_user(client)

        response = await client.get(
            USERS_URL, params={"skip": 0, "limit": 2}, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2

    async def test_list_users_pagination_skip(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(
            USERS_URL, params={"skip": 1, "limit": 1}, headers=auth_headers
        )

        assert response.status_code == 200

    async def test_list_users_invalid_limit_zero(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(
            USERS_URL, params={"limit": 0}, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_list_users_invalid_limit_over_max(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(
            USERS_URL, params={"limit": 101}, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_list_users_invalid_skip_negative(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(
            USERS_URL, params={"skip": -1}, headers=auth_headers
        )

        assert response.status_code == 422

    async def test_list_users_unauthorized(self, client: AsyncClient):
        response = await client.get(USERS_URL)

        assert response.status_code == 401

    async def test_list_users_schema(
        self, client: AsyncClient, auth_headers: dict, user: dict
    ):
        response = await client.get(USERS_URL, headers=auth_headers)

        item = response.json()["items"][0]
        assert "id" in item
        assert "email" in item
        assert "first_name" in item
        assert "last_name" in item
        assert "password" not in item


# ===========================================================================
# GET /users/{id}
# ===========================================================================
class TestGetUser:
    async def test_get_user_success(
        self, client: AsyncClient, auth_headers: dict, user: dict
    ):
        response = await client.get(f"{USERS_URL}/{user['id']}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user["id"]
        assert data["email"] == user["email"]

    async def test_get_user_not_found(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(
            f"{USERS_URL}/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_get_user_invalid_uuid(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(f"{USERS_URL}/not-a-uuid", headers=auth_headers)

        assert response.status_code == 422

    async def test_get_user_unauthorized(self, client: AsyncClient, user: dict):
        response = await client.get(f"{USERS_URL}/{user['id']}")

        assert response.status_code == 401

    async def test_get_user_response_has_no_password(
        self, client: AsyncClient, auth_headers: dict, user: dict
    ):
        response = await client.get(f"{USERS_URL}/{user['id']}", headers=auth_headers)

        assert "password" not in response.json()


# ===========================================================================
# PATCH /users/{id}
# ===========================================================================
class TestUpdateUser:
    async def test_update_user_success(
        self, client: AsyncClient, auth_headers: dict, user: dict
    ):
        response = await client.patch(
            f"{USERS_URL}/{user['id']}",
            json={"first_name": "UpdatedName"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["first_name"] == "UpdatedName"

    async def test_update_user_partial_last_name(
        self, client: AsyncClient, auth_headers: dict, user: dict
    ):
        response = await client.patch(
            f"{USERS_URL}/{user['id']}",
            json={"last_name": "UpdatedLast"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["last_name"] == "UpdatedLast"

    async def test_update_user_password_too_short(
        self, client: AsyncClient, auth_headers: dict, user: dict
    ):
        # password has min_length=8 in the DTO
        response = await client.patch(
            f"{USERS_URL}/{user['id']}",
            json={"password": "short"},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_update_user_not_found(self, client: AsyncClient, auth_headers: dict):
        response = await client.patch(
            f"{USERS_URL}/00000000-0000-0000-0000-000000000000",
            json={"first_name": "Ghost"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_update_user_unauthorized(self, client: AsyncClient, user: dict):
        response = await client.patch(
            f"{USERS_URL}/{user['id']}",
            json={"first_name": "Hack"},
        )

        assert response.status_code == 401

    async def test_update_user_returns_updated_data(
        self, client: AsyncClient, auth_headers: dict, user: dict
    ):
        new_first = "ChangedFirst"
        new_last = "ChangedLast"
        response = await client.patch(
            f"{USERS_URL}/{user['id']}",
            json={"first_name": new_first, "last_name": new_last},
            headers=auth_headers,
        )

        data = response.json()
        assert data["first_name"] == new_first
        assert data["last_name"] == new_last
        assert data["id"] == user["id"]


# ===========================================================================
# DELETE /users/{id}
# ===========================================================================
class TestDeleteUser:
    async def test_delete_user_success(self, client: AsyncClient):
        user, headers = await create_authenticated_user(client)
        response = await client.delete(f"{USERS_URL}/{user['id']}", headers=headers)

        assert response.status_code == 204

    async def test_delete_user_verifies_deletion(
        self, client: AsyncClient, auth_headers: dict
    ):
        new_user, new_headers = await create_authenticated_user(client)
        await client.delete(f"{USERS_URL}/{new_user['id']}", headers=new_headers)

        get_response = await client.get(
            f"{USERS_URL}/{new_user['id']}", headers=auth_headers
        )
        assert get_response.status_code == 404

    async def test_delete_user_not_found(self, client: AsyncClient, auth_headers: dict):
        response = await client.delete(
            f"{USERS_URL}/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_delete_user_unauthorized(self, client: AsyncClient, user: dict):
        response = await client.delete(f"{USERS_URL}/{user['id']}")

        assert response.status_code == 401
