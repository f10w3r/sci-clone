from . import util, config
import typer
from typing import List, Tuple, Optional
from pathlib import Path
from os import path, getcwd, mkdir


app = typer.Typer()

def version_callback(value: bool):
    if value:
        typer.secho(util.LOGO, fg=typer.colors.GREEN)
        typer.secho(f"version: {config.__version__}", fg=typer.colors.YELLOW)
        typer.echo("For detailed usage, please view: https://github.com/f10w3r/sci-clone")
        raise typer.Exit(code=0)


@app.command(help="For detailed usage, please view: https://github.com/f10w3r/sci-clone")
def main(
    query_str: List[str] = typer.Argument(..., metavar="Query String", 
                                          help="by DOI/URL or by ISSN", show_default=False, hidden=True),
    url_scihub: str = typer.Option(config.__scihub__, '--scihub', '-s'),
    save_to: Path = typer.Option(getcwd, '--dir', '-d', 
                                 help="Directory to download", show_default="Current directory"),
    version: Optional[bool] = typer.Option(None, "--version", "-v", 
                                           help="Show version", callback=version_callback)
):  
    if url_scihub.startswith("http"):
        typer.secho(f'Error: Invalid URL, example: {config.__scihub__}', fg=typer.colors.MAGENTA)
        raise typer.Exit(code=1)
    url_scihub = "https://" + url_scihub
    if not path.exists(save_to):
        typer.secho('Error: Invalid path.', fg=typer.colors.MAGENTA)
        raise typer.Exit(code=1)
    
    requester = util.Requester(config, timeout=30)
    generator = util.GenList(query_str, requester)
    query = generator.get_query_list()
    processing = util.Processing(url_scihub, requester, query, save_to)
    processing.download()

if __name__ == "__main__":
    app()