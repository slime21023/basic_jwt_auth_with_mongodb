from bunnet import Document, Link, init_bunnet
from settings import settings
from pymongo import MongoClient
from pydantic import EmailStr, Field, BaseModel
from typing import List

class User(Document):
    email: EmailStr 
    first_name: str = Field(max_length=30)
    last_name:str = Field(max_length=30)

class Account(Document):
    user: Link[User]
    password: str

class Comment(BaseModel):
    content: str = Field(max_length=120)
    name:str = Field(max_length=30)


class Post(Document):
    title:str = Field(max_length=120, required=True)
    author: Link[User]
    tags: List[str] = Field(max_length=10)
    comments: List[Comment]

    class Settings:
        is_root = True


class TextPost(Post):
    content: str 


class ImagePost(Post):
    image_path: str


class LinkPost(Post):
    link_url: str


db_client = MongoClient(settings.MONGODB_URL)

def init_database():
    db_name= settings.MONGODB_DBNAME
    # Initialize bunnet with the Product document class and a database
    init_bunnet(database=db_client[db_name], document_models=[User, Account])