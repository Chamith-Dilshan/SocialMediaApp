from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World For real"}

def test_get_posts():
    response = client.get("/posts")
    assert response.status_code == 200
    assert response.json() == {"message": "This is a list of posts"}

def test_create_posts():
    response = client.post("/posts", json={"title": "My First Post", "content": "This is my first post", "author": "John"})
    assert response.status_code == 200
    assert response.json() == {"message": "John - Post created!"}