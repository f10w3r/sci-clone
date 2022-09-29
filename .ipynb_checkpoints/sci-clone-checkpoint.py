import typer # the only external dependency
from typing import List, Tuple
from pathlib import Path
from os import path, getcwd, mkdir
from datetime import datetime
import time
import re
import json
from urllib import request, parse
import configparser

app = typer.Typer()

v_APP = 'Sci-Clone'
v_APP_Ver = 'v0.4'
v_APP_URL = 'https://github.com/f10w3r/sci-clone'
v_APP_Email = 'lifuminster@gmail.com'
v_API = "innerFunction"
v_API_Ver = "v1.5"
etiquette = f"{v_APP}/{v_APP_Ver} ({v_APP_URL}; mailto:{v_APP_Email}) BasedOn:{v_API}/{v_API_Ver}"
header = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

def get_file_list(file_path):
    with open(file_path, 'r') as f:
        file_content = f.read()
    if file_path.endswith('.txt'):
        for line in file_content.split('\n'):
            yield line
    elif file_path.endswith('.bib'):
        items = file_content.lower().strip().split('@')[1:]
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

def get_journal_works(issn, year_start, year_end, header=header):
    url = f"http://api.crossref.org/journals/{issn}/works"
    cursor = '*'
    results = list()
    while True:
        from_to = f"from-pub-date:{year_start},until-pub-date:{year_end}"
        r = request_to(url, headers = header,
                       params={"rows": 1000, 
                               "cursor": cursor, 
                               "filter": from_to})
        r_json = json.loads(r.read())
        total = r_json['message']['total-results']
        cursor = r_json['message']['next-cursor']
        items = r_json['message']['items']
        results += items
        if len(results) < total:
            continue
        else:
            break
    container_title = results[0]['container-title'][0]
    yearly_result = dict()
    for year in range(year_start, year_end+1):
        year_list = list()
        for r in results:
            if r['published']['date-parts'][0][0] == year:
                if 'DOI' in r:
                    year_list.append(r['DOI'])
                elif 'URL' in r:
                    year_list.append(r['URL'])
        yearly_result[year] = year_list
    return container_title, yearly_result

def retry(retry_count=3, retry_interval=2):
    """
    retry decorator
    """
    def real_decorator(decor_method):
        def wrapper(*args, **kwargs):
            for count in range(retry_count):
                try:
                    return_values = decor_method(*args, **kwargs)
                    return return_values
                except Exception as error:
                    # On exception, retry till retry_frequency is exhausted
                    print("\nFATAL: retry: %s . Function execution failed for %s" %
                                 (count + 1, decor_method.__name__))
                    # sleep for retry_interval
                    time.sleep(retry_interval)
                    # If the retries are exhausted, raise the exception
                    if count == retry_count-1:
                        raise error
        return wrapper
    return real_decorator

@retry(retry_count=3, retry_interval=5)
def request_to(url, headers=False, params="", timeout=30, method="GET"):
    query_string = parse.urlencode(params)
    if method == "GET":
        if params:
            req = request.Request(f"{url}?{query_string}")
        else:
            req = request.Request(url)
    elif method == "POST":
        req = request.Request(url, query_string.encode("UTF-8"))
    if headers:
        for key in headers.keys():
            req.add_header(key, headers[key])
    response = request.urlopen(req, timeout=timeout)
    return response

def walk_the_list(list_name, query_list, url_scihub, save_to):
    label = f"{list_name}: {len(query_list)}"
    undone = list()
    with typer.progressbar(query_list, label=label, show_eta=False, show_percent=False, fill_char="▒", 
                           item_show_func=lambda x: f"{str(query_list.index(x))} | {x}" if x else x) as progress:
        for query in progress:
            item_done = get_pdf_scihub(url_scihub, query, save_to)
            if not item_done:
                undone.append(query)
    log = path.join(save_to, "missing.log")
    with open(log, 'w') as f:
        if undone:
            f.writelines([f"{i}\n" for i in undone])
            typer.secho(f'missing log: {log}', fg=typer.colors.MAGENTA, bold=True, italic=True)
        else:
            f.write("all done.")
            typer.secho("all done.", fg=typer.colors.GREEN, bold=True, italic=True)
    return undone

def get_pdf_scihub(url_scihub, query, save_to, header=header):
    payload = {"request": query}
    response = request_to(url_scihub, headers=header, params=payload, method="POST")
    response_text = response.read().decode()
    if "Sorry, sci-hub has not included this article yet" in response_text:
        file_url, file_name = False, False
    else:
        file_url = re.search("location.href='(.+)'", response_text).group(1).replace("\\", "")
        file_name = re.search("pdf/(.+)\?", file_url).group(1).replace("/", "_")
    if file_name:
        file_path = path.join(save_to, file_name)
        if path.exists(file_path):
            return True
        else:
            response = request_to(file_url, headers=header)
            with open(file_path, 'b+w') as f:
                f.write(response.read())
            return True
    else:
        return False

#def get_pdf_libgen(url_scihub, query, save_to):
#    pass


@app.command()
def main(
        query: List[str] = typer.Argument(..., help="by DOI/URL or by ISSN"),
        url_scihub: str = typer.Option('sci-hub.wf', '--scihub', '-s'),
#        url_libgen: str = typer.Option('libgen.rs', '--libgen', '-l'),
        save_to: Path = typer.Option(getcwd, '--dir', '-d', help="Directory to download"),
    ):
    
    try:
        assert not url_scihub.startswith("http"), 'Error: Invalid URL, example: sci-hub.tf'
        url_scihub = "https://" + url_scihub
#        assert not url_libgen.startswith("http"), 'Error: Invalid URL, example: libgen.rs'
#        url_libgen = f"http://{url_libgen}/scimag/"
        assert path.exists(save_to), 'Error: Invalid path.'
    except AssertionError as e:
        typer.secho(e.args[0], err=True, fg=typer.colors.MAGENTA)
        raise typer.Exit()
    
    if re.match("^[0-9]{4}-[0-9]{3}[0-9xX]$", query[0]):
        issn = query[0]
        if len(query) in (2, 3) and all([re.match("^[\d]{4}$", i) for i in query[1:]]):
            year0, year1 = int(query[1]), int(query[-1])
            if not (1666 < year0 <= year1 <= datetime.now().year):
                typer.secho('Please ensure valid year.', fg=typer.colors.MAGENTA)
                raise typer.Exit(code=1)
        else:
            typer.secho('Please follow format: "sci-clone ISSN FROM_YEAR [TO_YEAR]"',
                        fg=typer.colors.MAGENTA)
            raise typer.Exit(code=1)
        container_title, yearly_dict = get_journal_works(issn, year0, year1)
        journal_dir = path.join(save_to, issn)
        if not path.exists(journal_dir): mkdir(journal_dir)
        for k,v in yearly_dict.items():
            year_dir = path.join(journal_dir, str(k))
            if not path.exists(year_dir): mkdir(year_dir)
            list_name = f"{container_title} in {k}"
            walk_the_list(list_name, v, url_scihub, year_dir)
    else:
        query_list = []
        for line in query:
            if line.endswith('.txt') or line.endswith('.bib'):
                query_list += list(get_file_list(line))
            else:
                query_list += [line,]
        list_name = "paper list"
        walk_the_list(list_name, query_list, url_scihub, save_to)

#if __name__ == "__main__":
#    app()