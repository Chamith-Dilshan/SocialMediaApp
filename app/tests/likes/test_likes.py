from httpx import AsyncClient

from app.tests.utils.constants import LIKES_URL, POSTS_URL
from app.tests.utils.helpers import create_authenticated_user


# ===========================================================================
# POST /likes/{post_id}/like  (toggle)
# ===========================================================================
class TestToggleLike:
    async def test_like_post_first_call(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        response = await client.post(
            f"{LIKES_URL}/{post['id']}/like", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["liked"] is True
        assert str(data["post_id"]) == post["id"]

    async def test_unlike_post_second_call(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        await client.post(f"{LIKES_URL}/{post['id']}/like", headers=auth_headers)
        response = await client.post(
            f"{LIKES_URL}/{post['id']}/like", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["liked"] is False

    async def test_like_again_third_call(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        # Like → Unlike → Like
        await client.post(f"{LIKES_URL}/{post['id']}/like", headers=auth_headers)
        await client.post(f"{LIKES_URL}/{post['id']}/like", headers=auth_headers)
        response = await client.post(
            f"{LIKES_URL}/{post['id']}/like", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["liked"] is True

    async def test_like_increments_like_count(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        before = (
            await client.get(f"{POSTS_URL}/{post['id']}", headers=auth_headers)
        ).json()["like_count"]

        await client.post(f"{LIKES_URL}/{post['id']}/like", headers=auth_headers)

        after = (
            await client.get(f"{POSTS_URL}/{post['id']}", headers=auth_headers)
        ).json()["like_count"]

        assert after == before + 1

    async def test_unlike_decrements_like_count(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        await client.post(f"{LIKES_URL}/{post['id']}/like", headers=auth_headers)
        liked_count = (
            await client.get(f"{POSTS_URL}/{post['id']}", headers=auth_headers)
        ).json()["like_count"]

        await client.post(f"{LIKES_URL}/{post['id']}/like", headers=auth_headers)
        unliked_count = (
            await client.get(f"{POSTS_URL}/{post['id']}", headers=auth_headers)
        ).json()["like_count"]

        assert unliked_count == liked_count - 1

    async def test_is_liked_reflects_state(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        before = (
            await client.get(f"{POSTS_URL}/{post['id']}", headers=auth_headers)
        ).json()["is_liked"]
        assert before is False

        await client.post(f"{LIKES_URL}/{post['id']}/like", headers=auth_headers)
        after = (
            await client.get(f"{POSTS_URL}/{post['id']}", headers=auth_headers)
        ).json()["is_liked"]
        assert after is True

    async def test_multiple_users_can_like_same_post(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        _, other_headers = await create_authenticated_user(client)

        r1 = await client.post(f"{LIKES_URL}/{post['id']}/like", headers=auth_headers)
        r2 = await client.post(f"{LIKES_URL}/{post['id']}/like", headers=other_headers)

        assert r1.json()["liked"] is True
        assert r2.json()["liked"] is True

    async def test_like_post_not_found(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            f"{LIKES_URL}/00000000-0000-0000-0000-000000000000/like",
            headers=auth_headers,
        )

        assert response.status_code == 404

    async def test_like_post_unauthorized(self, client: AsyncClient, post: dict):
        response = await client.post(f"{LIKES_URL}/{post['id']}/like")

        assert response.status_code == 401

    async def test_like_post_invalid_uuid(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.post(
            f"{LIKES_URL}/not-a-uuid/like", headers=auth_headers
        )

        assert response.status_code == 422

    async def test_like_response_contains_post_id(
        self, client: AsyncClient, auth_headers: dict, post: dict
    ):
        response = await client.post(
            f"{LIKES_URL}/{post['id']}/like", headers=auth_headers
        )

        data = response.json()
        assert "liked" in data
        assert "post_id" in data
        assert isinstance(data["liked"], bool)
