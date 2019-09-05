from fastapi import FastAPI

import mysql.connector


app = FastAPI()




@app.get("/v1")
def read_root():
    return {"Paxful": "API"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}