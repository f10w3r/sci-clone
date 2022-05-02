#!/usr/bin/env python3
#-*- coding: UTF-8 -*-
from . import utils, config
from os import path, getcwd, mkdir
from typer import Typer, Argument, Option, echo, Exit, FileText
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from requests import Session
from requests.adapters import HTTPAdapter
from requests.compat import urljoin

session = Session()
session.mount('http', HTTPAdapter(max_retries=3))
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
operator = utils.Utils(session)

console = Console()
app = Typer(invoke_without_command=True, no_args_is_help=True, help=config.__description__)

@app.callback()
def version_callback(version: Optional[bool] = Option(None, '--version', '-V', is_eager=True, help="Show version")):
    global console
    if version:
        console.print(
            Panel(config.__banner__,
                title=f'[i b #fcec0c on #58482c]{" "*2} =====   W  E  L  C  O  M  E  !  ===== {" "*2}[/]',
                subtitle=f'[#fcec0c on #58482c]{" "*4}[i]Ver. {config.__version__}   [/i]| [link={config.__url__}]Github: f10w3r/sci-clone[/link]{" "*4}',
                width=70)
        )
        raise Exit()

@app.command("issn", no_args_is_help=True, help="Download by year (of a journal).")
def issn_process(
        issn: str = Argument(..., help="Journal ISSN (e.g.: 0002-9602)"),
        year: List[datetime] = Argument(..., formats=['%Y'], help="From year to year (e.g.: 2011 2012)"),
        dir: Path = Option(getcwd, '--dir', '-d', help="Directory to download"),
        scihub: str = Option(config.__scihub__, '--scihub', '-s', help="Valid Sci-Hub URL")
    ):
    try:
        assert len(year) in (1, 2), "Argument Error: 'year' takes 1 or 2 values."
        if len(year) == 1: year = [year[0], year[0]]
        assert datetime.strptime("1665", "%Y") < year[0] <= year[1] <= datetime.now(), "Argument Error: Invalid 'year', not a time machine."
        assert not scihub.startswith("http"), 'Argument Error: Invalid URL, example: sci-hub.tf'; scihub = "https://" + scihub
        assert path.exists(dir), 'Argument Error: Invalid path.'
    except AssertionError as e:
        echo(e.args[0], err=True)
        raise Exit()
    global operator, console
    for idx, y in enumerate(range(year[0].year, year[1].year + 1)):
        doi_list = operator.get_doi_list(y, issn)
        if not idx: console.print(f"   {doi_list[0]['container-title'][0]}   ".upper(), style="bold white italic on blue")
        articles = [{
            "article_url": urljoin(scihub, article['DOI']),
            "file_name": f"VOL{article['volume']}_{article['DOI'].replace('/', '-')}.pdf",
            "warning_str": f"{article['DOI']} | {issn} | {y}_VOL{article['volume']}"}
            for article in doi_list
        ]
        folder = path.join(dir, issn + '_' + str(y))
        if not path.exists(folder): mkdir(folder)
        missing, log_file = operator.download(y, articles, folder)
        echo(f" {' '*4} | {missing} missing: {log_file}")

@app.command("doi", no_args_is_help=True, help="Download by DOI/arXivID.")
def doi_process(
        ids: List[str] = Argument(..., help="Valid DOI/arXivID(s) or file (*.bib, *.txt)"),
        dir: Path = Option(getcwd, '--dir', '-d', help="Directory to download"),
        scihub: str = Option(config.__scihub__, '--scihub', '-s', help="Valid Sci-Hub URL")
    ):
    global operator
    try:
        assert not scihub.startswith("http"), 'Argument Error: Invalid URL, example: sci-hub.tf'; scihub = "https://" + scihub
        assert path.exists(dir), 'Argument Error: Invalid path.'
        if ids[0].lower().endswith('.bib'):
            assert path.exists(ids[0]), 'Argument Error: Invalid file path.'
            ids_list = operator.parseBibTex(ids[0])
        elif ids[0].lower().endswith('.txt'):
            assert path.exists(ids[0]), 'Argument Error: Invalid file path.'
            ids_list = operator.parseTxt(ids[0])
        else:
            ids_list = ids
    except AssertionError as e:
        echo(e.args[0], err=True)
        raise Exit()
    if not ids_list:
        echo("There is no valid DOI.", err=True)
        raise Exit()
    articles = list()
    for d in ids_list:
        if d.startswith('arXiv'):
            articles.append({
                "article_url": urljoin('https://arxiv.org/abs', d.split(':')[1]),
                "file_name": f"{d.replace(':', '-')}.pdf",
                "warning_str": d})
        else:
            articles.append({
                "article_url": urljoin(scihub, d),
                "file_name": f"{d.replace('/', '-')}.pdf",
                "warning_str": d})
    task = "ID"
    missing, log_file = operator.download(task, articles, dir)
    echo(f" {' '*len(task)} | {missing} missing: {log_file}")
