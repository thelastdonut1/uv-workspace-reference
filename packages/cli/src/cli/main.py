import os

import typer
from core import fetch_headlines
from dotenv import load_dotenv
from rich.console import Console
from summarizer import SummarizationError, summarize_text

app = typer.Typer()
console = Console()

load_dotenv()


@app.command()
def headlines(limit: int = 5):
    headlines = fetch_headlines(limit)
    console.print(f"[bold blue]Top {limit} Hacker News Headlines:[/bold blue]")

    for i, title in enumerate(headlines, start=1):
        console.print(f"[green]{i}.[/green] {title}")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        console.print("[red]Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.[/red]")
        raise typer.Exit(code=1)

    try:
        summary = summarize_text("\n".join(headlines), api_key)

    except SummarizationError as exc:
        console.print(f"[red]Error: summarization failed: {exc}[/red]")
        raise typer.Exit(code=1) from exc

    console.print(f"\n[bold blue]Summary:[/bold blue] {summary}")
