import pytest
from fastapi.testclient import TestClient

from study.without_db_main import Post, app, posts, status

client = TestClient(app)


# Fixture to reset posts before each test
@pytest.fixture(autouse=True)
def reset_posts():
    """Reset posts to the initial state before each test."""
    posts.clear()
    posts.extend(
        [
            Post(
                id=1,
                title="First Post",
                content="This is the first post",
                author="John Doe",
            ),
            Post(
                id=2,
                title="Second Post",
                content="This is the second post",
                author="Jane Doe",
            ),
        ]
    )
    yield


# ROOT ENDPOINT TESTS
class TestRoot:
    def test_root_success(self):
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Hello World For real"}


# LIST POSTS TESTS
class TestListPosts:
    def test_list_posts_success(self):
        response = client.get("/posts")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "This is a list of posts"
        assert len(data["posts"]) == 2
        assert data["posts"][0]["id"] == 1
        assert data["posts"][1]["id"] == 2

    def test_list_posts_empty(self):
        posts.clear()
        response = client.get("/posts")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["posts"] == []


# GET SINGLE POST TESTS
class TestGetPost:
    def test_get_post_success(self):
        response = client.get("/posts/1")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Post 1 found"
        assert data["post"]["id"] == 1
        assert data["post"]["title"] == "First Post"
        assert data["post"]["author"] == "John Doe"

    def test_get_post_second_post(self):
        response = client.get("/posts/2")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["post"]["title"] == "Second Post"

    def test_get_post_not_found(self):
        response = client.get("/posts/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_get_post_invalid_id_type(self):
        response = client.get("/posts/abc")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# CREATE POST-TESTS
class TestCreatePost:
    def test_create_post_success(self):
        new_post = {
            "title": "Third Post",
            "content": "This is the third post",
            "author": "Bob Smith",
        }
        response = client.post("/posts", json=new_post)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["message"] == "Post created by Bob Smith"
        assert data["post"]["title"] == "Third Post"
        assert data["post"]["id"] == 3
        assert len(posts) == 3

    def test_create_post_with_id_ignored(self):
        """Test that provided ID is overridden with an auto-generated one."""
        new_post = {
            "id": 999,
            "title": "Post with ID",
            "content": "Test content",
            "author": "Test Author",
        }
        response = client.post("/posts", json=new_post)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["post"]["id"] == 3  # Auto-incremented, not 999

    def test_create_post_missing_title(self):
        new_post = {"content": "This is content", "author": "John Doe"}
        response = client.post("/posts", json=new_post)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_post_missing_content(self):
        new_post = {"title": "Title Only", "author": "John Doe"}
        response = client.post("/posts", json=new_post)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_post_missing_author(self):
        new_post = {"title": "Title Only", "content": "Content only"}
        response = client.post("/posts", json=new_post)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_post_empty_title(self):
        new_post = {"title": "", "content": "Content", "author": "Author"}
        response = client.post("/posts", json=new_post)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_post_empty_content(self):
        new_post = {"title": "Title", "content": "", "author": "Author"}
        response = client.post("/posts", json=new_post)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_post_empty_author(self):
        new_post = {"title": "Title", "content": "Content", "author": ""}
        response = client.post("/posts", json=new_post)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# UPDATE POST-TESTS
class TestUpdatePost:
    def test_update_post_success(self):
        updated_post = {
            "title": "Updated Title",
            "content": "Updated content",
            "author": "Updated Author",
        }
        response = client.put("/posts/1", json=updated_post)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Post 1 updated"
        assert data["post"]["title"] == "Updated Title"
        assert data["post"]["content"] == "Updated content"
        assert data["post"]["author"] == "Updated Author"
        assert data["post"]["id"] == 1  # ID unchanged

    def test_update_post_partial(self):
        """Test updating only one field (should still require all fields in the request)."""
        updated_post = {
            "title": "New Title",
            "content": "Original content",
            "author": "John Doe",
        }
        response = client.put("/posts/1", json=updated_post)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["post"]["title"] == "New Title"

    def test_update_post_not_found(self):
        updated_post = {"title": "Title", "content": "Content", "author": "Author"}
        response = client.put("/posts/999", json=updated_post)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_update_post_missing_field(self):
        updated_post = {"title": "Title", "content": "Content"}
        response = client.put("/posts/1", json=updated_post)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_update_post_empty_title(self):
        updated_post = {"title": "", "content": "Content", "author": "Author"}
        response = client.put("/posts/1", json=updated_post)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_update_post_invalid_id_type(self):
        updated_post = {"title": "Title", "content": "Content", "author": "Author"}
        response = client.put("/posts/abc", json=updated_post)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# DELETE POST-TESTS
class TestDeletePost:
    def test_delete_post_success(self):
        response = client.delete("/posts/1")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""  # No content in 204 response
        assert len(posts) == 1
        assert posts[0].id == 2

    def test_delete_post_removes_correct_post(self):
        client.delete("/posts/1")
        response = client.get("/posts/1")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_post_not_found(self):
        response = client.delete("/posts/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]

    def test_delete_post_invalid_id_type(self):
        response = client.delete("/posts/abc")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_delete_post_twice(self):
        """Test deleting the same post twice."""
        client.delete("/posts/1")
        response = client.delete("/posts/1")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# EDGE CASE TESTS
# class TestEdgeCases:
#     def test_create_then_delete_all_posts(self):
#         """Test creating and deleting to ensure ID generation works."""
#         utils.delete("/posts/1")
#         utils.delete("/posts/2")
#         assert len(posts) == 0
#
#         new_post = {
#             "title": "New Post After Delete",
#             "content": "Content",
#             "author": "Author",
#         }
#         response = utils.post("/posts", json=new_post)
#         assert response.status_code == status.HTTP_201_CREATED
#         assert response.json()["post"]["id"] == 3  # Not reset to 1
#
#     def test_multiple_creates_increment_id(self):
#         """Test that IDs increment correctly across multiple creations."""
#         for i in range(3):
#             new_post = {
#                 "title": f"Post {i}",
#                 "content": f"Content {i}",
#                 "author": f"Author {i}",
#             }
#             response = utils.post("/posts", json=new_post)
#             assert response.status_code == status.HTTP_201_CREATED
#             assert response.json()["post"]["id"] == 3 + i
#         assert len(posts) == 5
