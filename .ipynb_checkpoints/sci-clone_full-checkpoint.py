import typer
from typing import List, Tuple
from pathlib import Path
from os import path, getcwd, mkdir
from datetime import datetime
import configparser
from requests_html import HTMLSession

def get_url(session, url_scihub, query):
    payload = {"request": query}
    header = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    r = session.post(url_scihub, data=payload, headers=header)
    if "Sorry, sci-hub has not included this article yet" in r.text:
        return False, False
    else:
        element = r.html.xpath('//*[@id="buttons"]/ul/li[2]/a', first=True)
        url_pdf = element.attrs['onclick'][15:-1].replace('\\', '')
        return url_pdf, f"{'_'.join(r.url.split('/')[3:])}.pdf"

def download_pdf(session, file_url, file_name):
    req = request.Request(file_url, method='GET')
    req.add_header("user-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)")
    response = request.urlopen(req)
    with open(file_name, 'b+w') as f:
        f.write(response.read())

def get_file_list(file_path):
    with open(file_path, 'r') as f:
        if file_path.endswith('.txt'):
            for line in f.readlines():
                yield line.strip()
        elif file_path.endswith('.bib'):
            items = f.read().lower().strip().split('@')[1:]
            for item in items:
                bibtex = configparser.ConfigParser(allow_no_value=True)
                bibtex.read_string('[item]' + item.rstrip('}\n'))
                bibtex['item']['cate'] = item.split(',')[0].split('{')[0]
                bibtex['item']['citekey'] = item.split(',')[0].split('{')[1]
                for key in bibtex['item']:
                    bibtex['item'][key] = bibtex['item'][key].lstrip('{"').rstrip(',')
                    if bibtex['item'][key].endswith('}') or bibtex['item'][key].endswith('"'):
                        bibtex['item'][key] = bibtex['item'][key][:-1]
                    bibtex['item'][key] = bibtex['item'][key].replace('\n', ' ')
                item_dict = dict(bibtex.items('item'))
                if 'doi' in item_dict:
                    yield item_dict['doi']
                elif 'url' in item_dict:
                    yield item_dict['url']
                elif 'pmid' in item_dict:
                    yield item_dict['pmid']

def get_issn_list(session, year, issn):
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
            r = session.get(url, params=params, timeout=30)
            j = json.loads(r.text)
            if len(j['message']['items']):
                doi_list.extend(j['message']['items'])
                cursor = j['message']['next-cursor']
            else:
                break
        return doi_list

def walk_the_list(session, list_name, query_list, url_scihub, save_to):
    with typer.progressbar(query_list, label=f"Downloading {list_name}: {len(query_list)}") as progress:
        for q in progress:
            file_url, file_name = get_url(session, url_scihub, q)
            if file_url:
                download_pdf(session, file_url, path.join(save_to, file_name))
            else:
                pass
                #print("Sorry, sci-hub has not included this article yet.")

def main(
        query: List[str],
        url_scihub: str = typer.Option('sci-hub.wf'),
        save_to: Path = typer.Option(getcwd, '--dir', '-d', help="Directory to download"),
    ):
    try:
        assert not url_scihub.startswith("http"), 'Error: Invalid URL, example: sci-hub.tf'
        url_scihub = "https://" + url_scihub
        assert path.exists(save_to), 'Error: Invalid path.'
    except AssertionError as e:
        typer.echo(e.args[0], err=True)
        raise typer.Exit()
    session = HTMLSession()
    if not "/" in query[0]:
        try:
            assert len(query) in (1, 2, 3), 'Error: Option "year" requires 1 or 2 arguments.'
            if len(query) == 1:
                year = [datetime.now().year, datetime.now().year]
            elif len(query) == 2:
                assert datetime.strptime("1665", "%Y") < datetime.strptime(query[1], "%Y"), 'Error: Invalid "year", not a time machine.'
                assert datetime.strptime(query[1], "%Y") <= datetime.now(), 'Error: Invalid "year", not a time machine.'
                year = [datetime.strptime(query[1], "%Y").year, datetime.strptime(query[1], "%Y").year]
            else:
                assert datetime.strptime("1665", "%Y") < datetime.strptime(query[1], "%Y"), 'Error: Invalid "year", not a time machine.'
                assert datetime.strptime(query[1], "%Y") <= datetime.strptime(query[2], "%Y"), 'Error: Invalid "year", not a time machine.'
                assert datetime.strptime(query[2], "%Y") <= datetime.now(), 'Error: Invalid "year", not a time machine.'
                year = [datetime.strptime(query[1], "%Y").year, datetime.strptime(query[2], "%Y").year]
        except AssertionError as e:
            typer.echo(e.args[0], err=True)
            raise typer.Exit()
        for y in range(year[0], year[1]+1):
            query_list = get_issn_list(session, y, issn=query[0])
            print(query_list)
    else:
        query_list = []
        for line in query:
            if line.endswith('.txt') or line.endswith('.bib'):
                query_list += list(get_file_list(line))
            else:
                query_list += [line,]
        list_name = "paper list"
        walk_the_list(session, list_name, query_list, url_scihub, save_to)
            

if __name__ == "__main__":
    typer.run(main)