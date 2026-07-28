from httpx import AsyncClient

from app.tests.factories.post_factory import PostFactory
from app.tests.utils.constants import POSTS_URL, PUBLIC_POSTS_URL
from app.tests.utils.helpers import create_authenticated_user


# ===========================================================================
# POST /posts
# ===========================================================================
class TestCreatePost:
    async def test_create_post_success(self, client: AsyncClient, auth_headers: dict):
        payload = PostFactory.build()
        response = await client.post(POSTS_URL, json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["content"] == payload["content"]
        assert "id" in data
        assert "author" in data

    async def test_create_post_unauthorized(self, client: AsyncClient):
        payload = PostFactory.build()
        response = await client.post(POSTS_URL, json=payload)

        assert response.status_code == 401

    async def test_create_post_missing_title(
        self, client: AsyncClient, auth_headers: dict
    ):
        payload = PostFactory.build()
        del payload["title"]
        response = await client.post(POSTS_URL, json=payload, headers=auth_headers)

        assert response.status_code == 422

    async def test_create_post_missing_content(
        self, client: AsyncClient, auth_headers: dict
    ):
        payload = PostFactory.build()
        del payload["content"]
        response = await client.post(POSTS_URL, json=payload, headers=auth_headers)

        assert response.status_code == 422

    async def test_create_post_empty_title(
        self, client: AsyncClient, auth_headers: dict
    ):
        payload = PostFactory.build(title="")
        response = await client.post(POSTS_URL, json=payload, headers=auth_headers)

        assert response.status_code == 422

    async def test_create_post_empty_content(
        self, client: AsyncClient, auth_headers: dict
    ):
        payload = PostFactory.build(content="")
        response = await client.post(POSTS_URL, json=payload, headers=auth_headers)

        assert response.status_code == 422

    async def test_create_post_response_has_author(
        self, client: AsyncClient, auth_headers: dict, user: dict
    ):
        payload = PostFactory.build()
        response = await client.post(POSTS_URL, json=payload, headers=auth_headers)

        data = response.json()
        assert data["author"]["id"] == user["id"]

    async def test_create_post_like_count_zero(
        self, client: AsyncClient, auth_headers: dict
    ):
        payload = PostFactory.build()
        response = await client.post(POSTS_URL, json=payload, headers=auth_headers)

        assert response.json().get("like_count", 0) == 0


# ===========================================================================
# GET /posts  (My Posts)
# ===========================================================================
class TestMyPosts:
    async def test_my_posts_success(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        response = await client.get(POSTS_URL, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(p["id"] == post["id"] for p in data["items"])

    async def test_my_posts_empty_for_new_user(self, client: AsyncClient):
        _, headers = await create_authenticated_user(client)
        response = await client.get(POSTS_URL, headers=headers)

        assert response.status_code == 200
        assert response.json()["total"] == 0

    async def test_my_posts_search(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        title_fragment = post["title"][:5]
        response = await client.get(
            POSTS_URL, params={"search": title_fragment}, headers=auth_headers
        )

        assert response.status_code == 200

    async def test_my_posts_pagination(self, client: AsyncClient, auth_headers: dict):
        for _ in range(3):
            await client.post(POSTS_URL, json=PostFactory.build(), headers=auth_headers)

        response = await client.get(
            POSTS_URL, params={"skip": 0, "limit": 2}, headers=auth_headers
        )

        assert response.status_code == 200
        assert len(response.json()["items"]) <= 2

    async def test_my_posts_unauthorized(self, client: AsyncClient):
        response = await client.get(POSTS_URL)

        assert response.status_code == 401

    async def test_my_posts_schema(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        response = await client.get(POSTS_URL, headers=auth_headers)
        item = response.json()["items"][0]

        assert "id" in item
        assert "title" in item
        assert "content" in item
        assert "author" in item


# ===========================================================================
# GET /posts/users/{author_id}
# ===========================================================================
class TestUserPosts:
    async def test_user_posts_success(
        self, client: AsyncClient, auth_headers: dict, user: dict, post: dict
    ):
        response = await client.get(
            f"{POSTS_URL}/users/{user['id']}", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(p["id"] == post["id"] for p in data["items"])

    async def test_user_posts_author_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(
            f"{POSTS_URL}/users/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )

        # Repository returns empty list for unknown author — 200 with total=0
        assert response.status_code == 200
        assert response.json()["total"] == 0

    async def test_user_posts_search(
        self, client: AsyncClient, auth_headers: dict, user: dict, post: dict
    ):
        title_fragment = post["title"][:5]
        response = await client.get(
            f"{POSTS_URL}/users/{user['id']}",
            params={"search": title_fragment},
            headers=auth_headers,
        )

        assert response.status_code == 200

    async def test_user_posts_pagination(
        self, client: AsyncClient, auth_headers: dict, user: dict
    ):
        for _ in range(3):
            await client.post(POSTS_URL, json=PostFactory.build(), headers=auth_headers)

        response = await client.get(
            f"{POSTS_URL}/users/{user['id']}",
            params={"skip": 0, "limit": 2},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert len(response.json()["items"]) <= 2

    async def test_user_posts_unauthorized(self, client: AsyncClient, user: dict):
        response = await client.get(f"{POSTS_URL}/users/{user['id']}")

        assert response.status_code == 401


# ===========================================================================
# GET /posts/public
# ===========================================================================
class TestPublicPosts:
    async def test_public_posts_success(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        response = await client.get(PUBLIC_POSTS_URL, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data

    async def test_public_posts_search(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        title_fragment = post["title"][:5]
        response = await client.get(
            PUBLIC_POSTS_URL,
            params={"search": title_fragment},
            headers=auth_headers,
        )

        assert response.status_code == 200

    async def test_public_posts_pagination(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        response = await client.get(
            PUBLIC_POSTS_URL, params={"skip": 0, "limit": 1}, headers=auth_headers
        )

        assert response.status_code == 200
        assert len(response.json()["items"]) <= 1

    async def test_public_posts_unauthorized(self, client: AsyncClient):
        response = await client.get(PUBLIC_POSTS_URL)

        assert response.status_code == 401

    async def test_public_posts_empty_search(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(
            PUBLIC_POSTS_URL,
            params={"search": "zxqwerty_impossible_string_xyz"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert isinstance(response.json()["items"], list)


# ===========================================================================
# GET /posts/{id}
# ===========================================================================
class TestGetPost:
    async def test_get_post_success(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        response = await client.get(f"{POSTS_URL}/{post['id']}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == post["id"]
        assert data["title"] == post["title"]

    async def test_get_post_not_found(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(
            f"{POSTS_URL}/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_get_post_invalid_uuid(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(f"{POSTS_URL}/not-a-uuid", headers=auth_headers)

        assert response.status_code == 422

    async def test_get_post_unauthorized(self, client: AsyncClient, post: dict):
        response = await client.get(f"{POSTS_URL}/{post['id']}")

        assert response.status_code == 401

    async def test_get_post_has_like_count(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        response = await client.get(f"{POSTS_URL}/{post['id']}", headers=auth_headers)

        data = response.json()
        assert "like_count" in data
        assert isinstance(data["like_count"], int)

    async def test_get_post_has_is_liked(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        response = await client.get(f"{POSTS_URL}/{post['id']}", headers=auth_headers)

        data = response.json()
        assert "is_liked" in data
        assert isinstance(data["is_liked"], bool)


# ===========================================================================
# PATCH /posts/{id}
# ===========================================================================
class TestUpdatePost:
    async def test_update_post_success(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        response = await client.patch(
            f"{POSTS_URL}/{post['id']}",
            json={"title": "Updated Title"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    async def test_update_post_partial_content(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        new_content = "Brand new content for the post."
        response = await client.patch(
            f"{POSTS_URL}/{post['id']}",
            json={"content": new_content},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["content"] == new_content

    async def test_update_post_not_owner(self, client: AsyncClient, post: dict):
        _, other_headers = await create_authenticated_user(client)
        response = await client.patch(
            f"{POSTS_URL}/{post['id']}",
            json={"title": "Hijacked"},
            headers=other_headers,
        )

        assert response.status_code in (403, 404)

    async def test_update_post_not_found(self, client: AsyncClient, auth_headers: dict):
        response = await client.patch(
            f"{POSTS_URL}/00000000-0000-0000-0000-000000000000",
            json={"title": "Ghost"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_update_post_empty_title_invalid(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        response = await client.patch(
            f"{POSTS_URL}/{post['id']}",
            json={"title": ""},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_update_post_unauthorized(self, client: AsyncClient, post: dict):
        response = await client.patch(
            f"{POSTS_URL}/{post['id']}",
            json={"title": "Hacked"},
        )

        assert response.status_code == 401


# ===========================================================================
# DELETE /posts/{id}
# ===========================================================================
class TestDeletePost:
    async def test_delete_post_success(self, client: AsyncClient, auth_headers: dict):
        payload = PostFactory.build()
        create_resp = await client.post(POSTS_URL, json=payload, headers=auth_headers)
        post_id = create_resp.json()["id"]

        response = await client.delete(f"{POSTS_URL}/{post_id}", headers=auth_headers)

        assert response.status_code == 204

    async def test_delete_post_verifies_deletion(
        self, client: AsyncClient, auth_headers: dict
    ):
        payload = PostFactory.build()
        create_resp = await client.post(POSTS_URL, json=payload, headers=auth_headers)
        post_id = create_resp.json()["id"]

        await client.delete(f"{POSTS_URL}/{post_id}", headers=auth_headers)
        get_resp = await client.get(f"{POSTS_URL}/{post_id}", headers=auth_headers)

        assert get_resp.status_code == 404

    async def test_delete_post_not_owner(self, client: AsyncClient, post: dict):
        _, other_headers = await create_authenticated_user(client)
        response = await client.delete(
            f"{POSTS_URL}/{post['id']}", headers=other_headers
        )

        assert response.status_code in (403, 404)

    async def test_delete_post_not_found(self, client: AsyncClient, auth_headers: dict):
        response = await client.delete(
            f"{POSTS_URL}/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_delete_post_unauthorized(self, client: AsyncClient, post: dict):
        response = await client.delete(f"{POSTS_URL}/{post['id']}")

        assert response.status_code == 401
