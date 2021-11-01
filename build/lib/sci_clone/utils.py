#-*- coding: UTF-8 -*-
import json, os, typer
from loguru import logger
from rich.table import Column
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from bs4 import BeautifulSoup

class Utils:
    """
        Utilities for downloading from Sci-Hub
    """
    def __init__(self, session):
        self.session = session

    def get_doi_list(self, year, issn):
        """
            get DOI list by year from CrossRef.org
        """
        url = f"https://api.crossref.org/journals/{issn}/works"; cursor = '*'; doi_list = list()
        while True:
            r = self.session.get(url, params={'rows': 1000,'cursor': cursor,
                            'filter': 'from-pub-date:'+ str(year) + '-01' + ',until-pub-date:' + str(year) + '-12'})
            j = json.loads(r.text)
            if len(j['message']['items']):
                doi_list.extend(j['message']['items'])
                cursor = j['message']['next-cursor']
            else:
                break
        return doi_list

    def get_link(self, url):
        """
            get pdf link from Sci-Hub webpage
        """
        html = self.session.get(url, timeout=60, allow_redirects=False)
        html.encoding = 'utf-8'
        html.raise_for_status()
        tag = BeautifulSoup(html.text, 'html.parser').find('a', {'href': '#'})
        if tag:
            return tag['onclick'].split("'")[1].replace('\\', '')
        else:
            return None

    def get_article(self, article_url, file_path):
        """
            download a pdf
            Downloads a single article based on its DOI.
        """
        if os.path.exists(file_path): return True
        link = self.get_link(article_url)
        if link:
            pdf_url = urljoin('https:', link) if link.startswith('//') else link
            pdf = self.session.get(pdf_url, stream=True)
            with open(file_path, 'wb') as f:
                for chunk in pdf.iter_content(2000): f.write(chunk)
            return True
        else:
            # no iframe#pdf on the page
            return False

    def download(self, batch, articles, folder):
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
                done = self.get_article(article['article_url'], os.path.join(folder, article['file_name']))
                if done:
                    progress.update(task, advance=1)
                else:
                    missing += 1
                    logger.info("NOT_FOUND_IN_SCI-HUB | " + article['warning_str'])
        typer.echo(f"      | {missing} missing: {log_file}")