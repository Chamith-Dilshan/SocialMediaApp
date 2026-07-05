from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    author: str


@app.get("/")
async def root() -> dict:
    return {"message": "Hello World For real"}

@app.get("/posts")
async def get_posts()-> dict:
    return {"message": f"This is a list of posts"}


@app.post("/posts")
async def create_posts(post:Post) -> dict:
    return {"message": f"{post.author} - Post created!"}