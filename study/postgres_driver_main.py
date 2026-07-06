import time

import psycopg
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import Response
from psycopg.rows import dict_row
from pydantic import BaseModel, Field

app = FastAPI()


class Post(BaseModel):
    id: int | None = None
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    published: bool = Field(default=True)


while True:
    try:
        conn = psycopg.connect(
            conninfo="host=localhost port=5432 dbname=social-media-app user=postgres password=<password>",
            row_factory=dict_row,
        )
        cursor = conn.cursor()
        print("Connected to the database")
        break
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        time.sleep(5)

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
    cursor.execute("""SELECT * FROM posts""")
    post_list = cursor.fetchall()
    print(post_list)
    return {"message": "This is a list of posts", "posts": post_list}


@app.get("/posts/{post_id}")
async def get_post(post_id: int) -> dict:
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(post_id),))
    post = cursor.fetchone()
    if post is not None:
        return {"message": f"Post {post_id} found", "post": post}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post with id {post_id} not found",
    )


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post) -> dict:
    cursor.execute(
        """INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING *""",
        (post.title, post.content, post.published),
    )
    new_post = cursor.fetchone()
    conn.commit()
    return {"message": "New Post :", "post": new_post}


@app.put("/posts/{post_id}")
async def update_post(post_id: int, post: Post) -> dict:
    cursor.execute(
        """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
        (post.title, post.content, post.published, str(post_id)),
    )
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
    return {"message": f"Post {post_id} updated", "post": updated_post}


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int) -> Response:
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(post_id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
