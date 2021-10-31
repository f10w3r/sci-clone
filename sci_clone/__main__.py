#!/usr/bin/env python3
#-*- coding: UTF-8 -*-
import json, os, typer, sys
from datetime import datetime
from loguru import logger
from typing import List, Optional
from pathlib import Path
from rich.table import Column
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.console import Console
from rich.panel import Panel
from bs4 import BeautifulSoup
from requests import Session
from requests.adapters import HTTPAdapter
from requests.compat import urljoin

__version__ = "0.3.0"
__scihub__ = "sci-hub.tf"
__github__ = "[link=https://github.com/f10w3r/sci-clone]Github: f10w3r/sci-clone[/link]"
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

@app.callback()
def version_callback(version: Optional[bool] = typer.Option(None, '--version', '-v', help="Show version")):
    if version:
        console.print(
            Panel(__banner__,
                title=f'[i b #fcec0c on #58482c]{" "*2} =====   W  E  L  C  O  M  E  !  ===== {" "*2}[/]', 
                subtitle=f'[#fcec0c on #58482c]{" "*4}[i]Ver. {__version__}   [/i]| {__github__}{" "*4}',
                width=70)
        )
        raise typer.Exit()

def get_doi_list(year, issn):
    """
        get DOI list anually from CrossRef.org
    """
    url = "https://api.crossref.org/journals/" + issn + "/works"; cursor = '*'; doi_list = list()
    while True:
        r = session.get(url, params={'rows': 1000,'cursor': cursor,
                        'filter': 'from-pub-date:'+ str(year) + '-01' + ',until-pub-date:' + str(year) + '-12'})
        j = json.loads(r.text)
        if len(j['message']['items']):
            doi_list.extend(j['message']['items'])
            cursor = j['message']['next-cursor']
        else:
            break
    return doi_list

def get_link(url):
    """
        get pdf link from sci-hub webpage
    """
    html = session.get(url, timeout=60, allow_redirects=False)
    html.encoding = 'utf-8'
    html.raise_for_status()
    tag = BeautifulSoup(html.text, 'html.parser').find('a', {'href': '#'})
    if tag:
        return tag['onclick'].split("'")[1].replace('\\', '')
    else:
        return None

def get_article(article_url, file_path):
    """
        download a pdf
        Downloads a single article based on its DOI.
    """
    if os.path.exists(file_path): return True
    link = get_link(article_url)
    if link:
        pdf_url = urljoin('https:', link) if link.startswith('//') else link
        pdf = session.get(pdf_url, stream=True)
        with open(file_path, 'wb') as f:
            for chunk in pdf.iter_content(2000): f.write(chunk)
        return True
    else:
        # no iframe#pdf on the page
        return False

def download(batch, articles, folder):
    """
        download a pdf batch
    """
    log_file = os.path.join(folder, 'missing.log')
    logger.remove()
    logger.add(log_file, format="{time} {level} {message}", mode='w', level="INFO")
    assert len(articles) > 0, 'no article.'
    progress = Progress(
        TextColumn("[progress.description]{task.description}", table_column=Column(ratio=1)),
        TimeElapsedColumn(table_column=Column(ratio=1)),
        BarColumn(table_column=Column(ratio=2)),
        "| {task.completed} of {task.total:>2.0f}",
        expand=False
    )
    missing = 0
    with progress:
        task = progress.add_task(f" {batch} |", total=len(articles))
        for article in articles:
            done = get_article(article['article_url'], os.path.join(folder, article['file_name']))
            if done:
                progress.update(task, advance=1)
            else:
                missing += 1
                logger.info("NOT_FOUND_IN_SCI-HUB | " + article['warning_str'])
    typer.echo(f"      | {missing} missing: {log_file}")

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

    for idx, y in enumerate(range(year[0].year, year[1].year + 1)):
        doi_list = get_doi_list(y, issn)
        if not idx: console.print(f"   {doi_list[0]['container-title'][0]}   ".upper(), style="bold white italic on blue")
        articles = [{
            "article_url": urljoin(scihub, article['DOI']), 
            "file_name": f"VOL{article['volume']}_{article['DOI'].replace('/', '-')}.pdf",
            "warning_str": f"{article['DOI']} | {issn} | {y}_VOL{article['volume']}"}
            for article in doi_list
        ]
        folder = os.path.join(dir, issn + '_' + str(y))
        if not os.path.exists(folder): os.mkdir(folder)
        download(y, articles, folder)

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

    articles = [{
        "article_url": urljoin(scihub, d), 
        "file_name": f"{d.replace('/', '-')}.pdf", 
        "warning_str": d} 
        for d in doi
    ]
    download(" DOI", articles, dir)

def main():
    app()

if __name__ == "__main__":
    sys.exit(main())