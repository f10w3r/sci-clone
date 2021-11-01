#!/usr/bin/env python3
#-*- coding: UTF-8 -*-
import os, typer, sys
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from requests import Session
from requests.adapters import HTTPAdapter
from requests.compat import urljoin
from .utils import Utils
from .version import __name__, __version__, __url__

__scihub__ = "sci-hub.tf"
__github__ = f"[link={__url__}]Github: f10w3r/sci-clone[/link]"
__banner__ = f"""
                                                                 
         _____ __________     ________    ____  _   ________     
        / ___// ____/  _/    / ____/ /   / __ \/ | / / ____/     
        \__ \/ /    / /_____/ /   / /   / / / /  |/ / __/        
       ___/ / /____/ /_____/ /___/ /___/ /_/ / /|  / /___        
      /____/\____/___/     \____/_____/\____/_/ |_/_____/        
                                                                 
    A simple script for downloading articles from Sci-Hub.       
                                                                 
"""

app = typer.Typer(invoke_without_command=True, no_args_is_help=True, help="A simple script for downloading articles from Sci-Hub.")
console = Console()
session = Session()
session.mount('http', HTTPAdapter(max_retries=3))
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})

utils = Utils(session)

@app.callback()
def version_callback(version: Optional[bool] = typer.Option(None, '--version', '-v', help="Show version")):
    global console
    if version:
        console.print(
            Panel(__banner__,
                title=f'[i b #fcec0c on #58482c]{" "*2} =====   W  E  L  C  O  M  E  !  ===== {" "*2}[/]', 
                subtitle=f'[#fcec0c on #58482c]{" "*4}[i]Ver. {__version__}   [/i]| {__github__}{" "*4}',
                width=70)
        )
        raise typer.Exit()

@app.command("issn", help="Download by year.")
def issn_process(
        issn: str = typer.Argument(..., help="Journal ISSN (e.g.: 0002-9602)"),
        year: List[datetime] = typer.Argument(..., formats=['%Y'], help="From year to year (e.g.: 2011 2012)"),
        dir: Path = typer.Option(os.getcwd, '--dir', '-d', help="Directory to download"),
        scihub: str = typer.Option(__scihub__, '--scihub', '-s', help="Valid Sci-Hub URL")
    ):
    try:
        assert len(year) in (1, 2), "Argument Error: 'year' takes 1 or 2 values."
        if len(year) == 1: year = [year[0], year[0]]
        assert datetime.strptime("1665", "%Y") < year[0] <= year[1] <= datetime.now(), "Argument Error: Invalid 'year', not a time machine."
        assert not scihub.startswith("http"), 'Argument Error: Invalid URL, example: sci-hub.tf'; scihub = "https://" + scihub
        assert os.path.exists(dir), 'Argument Error: Invalid path.'
    except AssertionError as e:
        typer.echo(e.args[0], err=True)
        raise typer.Exit()

    global utils, console
    for idx, y in enumerate(range(year[0].year, year[1].year + 1)):
        doi_list = utils.get_doi_list(y, issn)
        if not idx: console.print(f"   {doi_list[0]['container-title'][0]}   ".upper(), style="bold white italic on blue")
        articles = [{
            "article_url": urljoin(scihub, article['DOI']), 
            "file_name": f"VOL{article['volume']}_{article['DOI'].replace('/', '-')}.pdf",
            "warning_str": f"{article['DOI']} | {issn} | {y}_VOL{article['volume']}"}
            for article in doi_list
        ]
        folder = os.path.join(dir, issn + '_' + str(y))
        if not os.path.exists(folder): os.mkdir(folder)
        utils.download(y, articles, folder)

@app.command("doi", help="Download by DOI.")
def doi_process(
        doi: List[str] = typer.Argument(..., help="valid DOI(s)"),
        dir: Path = typer.Option(os.getcwd, '--dir', '-d', help="Directory to download"),
        scihub: str = typer.Option(__scihub__, '--scihub', '-s', help="Valid Sci-Hub URL")
    ):
    try:
        assert not scihub.startswith("http"), 'Argument Error: Invalid URL, example: sci-hub.tf'; scihub = "https://" + scihub
        assert os.path.exists(dir), 'Argument Error: Invalid path.'
    except AssertionError as e:
        typer.echo(e.args[0], err=True)
        raise typer.Exit()

    global utils
    articles = [{
        "article_url": urljoin(scihub, d), 
        "file_name": f"{d.replace('/', '-')}.pdf", 
        "warning_str": d} 
        for d in doi
    ]
    utils.download(" DOI", articles, dir)

def main():
    app()

if __name__ == "__main__":
    sys.exit(main())