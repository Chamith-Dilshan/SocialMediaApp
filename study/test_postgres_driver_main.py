import pytest
from fastapi.testclient import TestClient

from study.postgres_driver_main import app

# Use a test database URL (separate PostgreSQL instance)
TEST_DATABASE_URL = "postgresql://postgres:password@localhost/socialmedia_test"


@pytest.fixture(scope="session")
def engine():
    """Create an engine for a test database."""
    return create_engine(TEST_DATABASE_URL)


@pytest.fixture
def db_session(engine):
    """Create a fresh transaction for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    transaction.rollback()
    connection.close()


@pytest.fixture
def test_db(db_session):
    """Set up a test database with a real connection."""
    db = Database(TEST_DATABASE_URL)
    db.connect()

    # Clear and repopulate
    db.execute("TRUNCATE posts CASCADE")
    db.execute("""
               INSERT INTO posts (id, title, content, published)
               VALUES (1, 'Test Post 1', 'Content 1', true),
                      (2, 'Test Post 2', 'Content 2', false)
               """)
    db.commit()

    yield db

    # Cleanup
    db.execute("TRUNCATE posts CASCADE")
    db.commit()
    db.disconnect()


def override_get_db(test_db):
    return test_db


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_overrides(test_db):
    """Override dependency with real test DB."""
    app.dependency_overrides[get_db] = lambda: test_db
    yield
    app.dependency_overrides.clear()


class TestRootEndpoint:
    def test_root_returns_hello(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World For real"}


class TestGetPosts:
    def test_get_posts_success(self):
        response = client.get("/posts")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert len(data["posts"]) == 2

    def test_get_posts_returns_correct_data(self):
        response = client.get("/posts")
        assert response.status_code == 200
        posts = response.json()["posts"]
        assert posts[0]["id"] == 1
        assert posts[1]["id"] == 2


class TestGetPostById:
    def test_get_post_valid_id(self):
        # At this point, db should be reset with 2 posts
        assert len(mock_db.posts) == 2, "Mock DB should have 2 posts"
        assert mock_db.posts[0]["id"] == 1, "Post 1 should exist"

        response = client.get("/posts/1")
        assert response.status_code == 200
        post = response.json()["post"]
        assert post["id"] == 1
        assert post["title"] == "Test Post 1"

    def test_get_post_not_found(self):
        response = client.get("/posts/9999")
        assert response.status_code == 404


class TestCreatePost:
    def test_create_post_success(self):
        payload = {"title": "New Post", "content": "New content", "published": True}
        response = client.post("/posts", json=payload)
        assert response.status_code == 201
        post = response.json()["post"]
        assert post["title"] == "New Post"
        assert post["id"] == 3

    def test_create_post_empty_title(self):
        payload = {"title": "", "content": "Content", "published": True}
        response = client.post("/posts", json=payload)
        assert response.status_code == 422

    def test_create_post_title_too_long(self):
        payload = {"title": "x" * 201, "content": "Content", "published": True}
        response = client.post("/posts", json=payload)
        assert response.status_code == 422


class TestUpdatePost:
    def test_update_post_success(self):
        # Reset should have happened, post 1 should exist
        assert len(mock_db.posts) == 2, "Mock DB should have 2 posts"

        payload = {"title": "Updated", "content": "Updated content", "published": False}
        response = client.put("/posts/1", json=payload)
        assert response.status_code == 200
        post = response.json()["post"]
        assert post["title"] == "Updated"
        assert post["published"] is False

    def test_update_post_not_found(self):
        payload = {"title": "Title", "content": "Content", "published": True}
        response = client.put("/posts/9999", json=payload)
        assert response.status_code == 404


class TestDeletePost:
    def test_delete_post_success(self):
        # Reset should have happened
        assert len(mock_db.posts) == 2, "Mock DB should have 2 posts"

        # Verify post exists before delete
        response = client.get("/posts/1")
        assert response.status_code == 200

        # Delete it
        response = client.delete("/posts/1")
        assert response.status_code == 204

        # Verify it's gone
        response = client.get("/posts/1")
        assert response.status_code == 404

    def test_delete_post_not_found(self):
        response = client.delete("/posts/9999")
        assert response.status_code == 404

    def test_delete_post_removes_from_list(self):
        # Before deletion
        assert len(mock_db.posts) == 2

        # Delete post 2
        response = client.delete("/posts/2")
        assert response.status_code == 204

        # After deletion
        assert len(mock_db.posts) == 1
