import typer
from core import fetch_headlines
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def headlines(limit: int = 5):
    headlines = fetch_headlines(limit)
    console.print(f"[bold blue]Top {limit} Hacker News Headlines:[/bold blue]")
    for i, title in enumerate(headlines, start=1):
        console.print(f"[green]{i}.[/green] {title}")
