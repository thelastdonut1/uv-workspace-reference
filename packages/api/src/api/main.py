import os

import uvicorn
from core import fetch_headlines
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from summarizer import SummarizationError, summarize_text

load_dotenv()

app = FastAPI()


@app.get("/headlines")
def get_headlines(limit: int = 5):
    headlines = fetch_headlines(limit)

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.",
        )

    try:
        summary = summarize_text("\n".join(headlines), api_key)
    except SummarizationError as exc:
        raise HTTPException(status_code=502, detail=f"Summarization failed: {exc}") from exc

    return {"headlines": headlines, "summary": summary}


def main() -> None:
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
