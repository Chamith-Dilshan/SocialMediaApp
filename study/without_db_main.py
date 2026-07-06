from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()


class Post(BaseModel):
    id: int | None = None
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=100)


posts: list[Post] = [
    Post(id=1, title="First Post", content="This is the first post", author="John Doe"),
    Post(
        id=2, title="Second Post", content="This is the second post", author="Jane Doe"
    ),
]


def find_post(post_id: int) -> Post | None:
    """Helper function to find a post by ID."""
    return next((post for post in posts if post.id == post_id), None)


def find_post_id(post_id: int) -> int | None:
    """Helper function to find the ID of a post."""
    for index, post in enumerate(posts):
        if post.id == post_id:
            return index
    return None


# When defining routers, the order of the endpoints is matter.
# Because the first endpoint that matches the request is executed.
# So, the root endpoint should be defined first.
# And if there are multiple endpoints that match the request, the first one is executed.
# For example, "posts/latest" should be defined before "posts/{post_id}".


@app.get("/")
async def root() -> dict:
    return {"message": "Hello World For real"}


@app.get("/posts")
async def get_posts() -> dict:
    return {"message": "This is a list of posts", "posts": posts}


@app.get("/posts/{post_id}")
async def get_post(post_id: int) -> dict:
    post = find_post(post_id)
    if post is not None:
        return {"message": f"Post {post_id} found", "post": post}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post with id {post_id} not found",
    )


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post) -> dict:
    new_post = post.model_copy()
    new_post.id = max((p.id for p in posts if p.id), default=0) + 1
    posts.append(new_post)
    return {"message": f"Post created by {new_post.author}", "post": new_post}


@app.put("/posts/{post_id}")
async def update_post(post_id: int, post: Post) -> dict:
    post_to_update = find_post(post_id)
    if post_to_update is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
    post_to_update.title = post.title
    post_to_update.content = post.content
    post_to_update.author = post.author
    return {"message": f"Post {post_id} updated", "post": post_to_update}


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int) -> None:
    post_to_delete = find_post_id(post_id)
    if post_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
    # posts.remove(posts[post_to_delete])
    posts.pop(post_to_delete)
