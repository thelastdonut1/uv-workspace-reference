import os

import uvicorn
from core import fetch_headlines
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

app = FastAPI()


@app.get("/headlines")
def get_headlines(limit: int = 5):
    return {"headlines": fetch_headlines(limit)}


def main() -> None:
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
