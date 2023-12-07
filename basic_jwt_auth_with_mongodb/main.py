from database import init_database, db_client
from typing import Union
from fastapi import FastAPI
from apis import auth

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.on_event("startup")
def init_app():
    init_database()

@app.on_event("shutdown")
def shutdown():
    db_client.close()


app.include_router(auth.router)