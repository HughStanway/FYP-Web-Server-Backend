# pylint: skip-file

from fastapi import FastAPI

app = FastAPI()

@app.post("/query")
def search():
    return {"message": "Query called"}