# -*- coding: UTF-8 -*-
import json
import os
import sys
from loguru import logger
from rich.table import Column
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from bs4 import BeautifulSoup
from requests.compat import urljoin
import configparser


class Utils:
    """
        Utilities for downloading from Sci-Hub
    """

    def __init__(self, session):
        self.session = session

    def parseBibTex(self, file):
        with open(file, 'r') as file:
            items = file.read().strip().split('@')
            for item in items[1:]:
                bibtex = configparser.ConfigParser(allow_no_value=True)
                bibtex.read_string('[item]' + item.rstrip('}\n'))
                bibtex['item']['cate'] = item.split(',')[0].split('{')[0]
                bibtex['item']['citekey'] = item.split(',')[0].split('{')[1]
                for key in bibtex['item']:
                    bibtex['item'][key] = bibtex['item'][key].lstrip(
                        '{"').rstrip(',')
                    if bibtex['item'][key].endswith('}') or bibtex['item'][key].endswith('"'):
                        bibtex['item'][key] = bibtex['item'][key][:-1]
                    bibtex['item'][key] = bibtex['item'][key].replace(
                        '\n', ' ')
                item_dict = dict(bibtex.items('item'))
                if 'doi' in item_dict:
                    yield item_dict['doi']

    def parseTxt(self, file):
        with open(file, 'r') as file:
            for line in file.readlines():
                if "/" in line:
                    yield line.replace('\n', '')

    def get_doi_list(self, year, issn):
        """
            get DOI list by year from CrossRef.org
        """
        url = f"https://api.crossref.org/journals/{issn}/works"
        cursor = '*'
        doi_list = list()
        year = str(year)
        while True:
            params = {
                "rows": 1000,
                "cursor": cursor,
                "filter": f"from-pub-date:{year}-01,until-pub-date:{year}-12"
            }
            r = self.session.get(url, params=params, timeout=30)
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
        html = self.session.get(url, timeout=30)
        html.encoding = 'utf-8'
        html.raise_for_status()
        article = BeautifulSoup(html.text, 'html.parser').find(
            'div', {'id': 'article'})
        if article:
            iframe = article.find('iframe')
            embed = article.find('embed')
            if iframe:
                raw_url = iframe['src'].split('#')[0]
            elif embed:
                raw_url = embed['src'].split('#')[0]
            else:
                sys.exit("new pattern of sci-hub webpage, please report to github")
            pdf_url = urljoin('https:', raw_url) if raw_url.startswith(
                '//') else raw_url
        else:
            pdf_url = None
        return pdf_url

    def get_article(self, article_url, file_path):
        """
            download a pdf
            Downloads a single article based on its DOI.
        """
        if os.path.exists(file_path):
            return True
        link = self.get_link(article_url)
        if link:
            pdf = self.session.get(link, params={'download': True}, timeout=30)
            with open(file_path, 'wb') as pdf_file:
                pdf_file.write(pdf.content)
            return True
        else:
            # no iframe#pdf on the page
            return False

    def download(self, batch, articles, folder):
        """
            Download a pdf batch
        """
        log_file = os.path.join(folder, 'missing.log')
        logger.remove()
        logger.add(
            log_file, format="{time} {level} {message}", mode='w', level="INFO")
        assert len(articles) > 0, 'no article.'
        progress = Progress(
            TextColumn(
                "[progress.description]{task.description}", table_column=Column(ratio=1)),
            TimeElapsedColumn(table_column=Column(ratio=1)),
            BarColumn(table_column=Column(ratio=2)),
            "| {task.completed} of {task.total:>2.0f}",
            expand=False
        )
        missing = 0
        with progress:
            task = progress.add_task(f" {batch} |", total=len(articles))
            for article in articles:
                done = self.get_article(
                    article['article_url'], os.path.join(folder, article['file_name']))
                if done:
                    progress.update(task, advance=1)
                else:
                    missing += 1
                    logger.info("NOT_FOUND_IN_SCI-HUB | " +
                                article['warning_str'])
        return missing, log_file
