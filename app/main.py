from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app import config, model
from app.database import engine, get_db

model.Base.metadata.create_all(bind=engine)
app = FastAPI()


# The @lru_cache decorator ensures the .env file is read only once on the first call, and the same
# Settings object is reused for all later requests.
# The @lru_cache + Depends(get_settings) pattern is most useful for route-level injection
# (e.g., when a route needs to read a setting). For module-level setup like creating the database engine,
# directly instantiating Settings() once is perfectly fine.
# example usage ->
# @app.get("/info")
# async def info (settings: Annotated[config.Settings, Depends(get_settings)]):
#     return {
#         "app_name": settings.app_name,
#         "admin_email": settings.admin_email,
#     }
@lru_cache
def get_settings():
    return config.Settings()


SessionDep = Annotated[Session, Depends(get_db)]


# When defining routers, the order of the endpoints is matter.
# Because the first endpoint that matches the request is executed.
# So, the root endpoint should be defined first.
# And if there are multiple endpoints that match the request, the first one is executed.
# For example, "posts/latest" should be defined before "posts/{post_id}".


@app.get("/")
async def root() -> dict:
    return {"message": "Hello World For real"}


@app.get("/posts")
async def get_posts(session: SessionDep) -> dict:
    posts = session.query(model.Post).all()
    print(posts)
    return {"message": "This is a list of posts", "posts": posts}


#
# @app.get("/posts/{post_id}")
# async def get_post(post_id: int) -> dict:
#     cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(post_id),))
#     post = cursor.fetchone()
#     if post is not None:
#         return {"message": f"Post {post_id} found", "post": post}
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail=f"Post with id {post_id} not found",
#     )
#
#
# @app.post("/posts", status_code=status.HTTP_201_CREATED)
# async def create_post(post: Post) -> dict:
#     cursor.execute(
#         """INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING *""",
#         (post.title, post.content, post.published),
#     )
#     new_post = cursor.fetchone()
#     conn.commit()
#     return {"message": "New Post :", "post": new_post}
#
#
# @app.put("/posts/{post_id}")
# async def update_post(post_id: int, post: Post) -> dict:
#     cursor.execute(
#         """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
#         (post.title, post.content, post.published, str(post_id)),
#     )
#     updated_post = cursor.fetchone()
#     conn.commit()
#     if updated_post is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Post with id {post_id} not found",
#         )
#     return {"message": f"Post {post_id} updated", "post": updated_post}
#
#
# @app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_post(post_id: int) -> Response:
#     cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(post_id),))
#     deleted_post = cursor.fetchone()
#     conn.commit()
#     if deleted_post is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Post with id {post_id} not found",
#         )
#     return Response(status_code=status.HTTP_204_NO_CONTENT)
