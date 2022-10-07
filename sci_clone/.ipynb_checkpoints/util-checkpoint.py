from . import config
import typer
from os import path, mkdir
from datetime import datetime
from urllib import request, parse
import time, re, json, configparser


class Requester:
    def __init__(self, config, timeout):
        etiquette = f"{config.__name__ }/{config.__version__} ({config.__url__}; " + \
                f"mailto:{config.__author_email__}) " + \
                f"BasedOn:{config.__name__}/{config.__version__}"
        self.header = {"user-agent": etiquette}
        self.timeout = timeout
    
    # retry decorator
    # Example:
    # @retry(3, 2) or @retry()
    # def test():
    #     pass
    def retry(retry_count, retry_interval):
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
                        print(f"\nFATAL: retry: {count + 1}. Function execution failed for {decor_method.__name__}")
                        time.sleep(retry_interval)
                        if count == retry_count-1:
                            raise error
            return wrapper
        return real_decorator
    
    @retry(retry_count=3, retry_interval=2)
    def request(self, url, params="", method="GET"):
        query_string = parse.urlencode(params)
        if method == "GET":
            if params:
                req = request.Request(f"{url}?{query_string}")
            else:
                req = request.Request(url)
        elif method == "POST":
            req = request.Request(url, query_string.encode("UTF-8"))
        for key in self.header.keys():
            req.add_header(key, self.header[key])
        response = request.urlopen(req, timeout=self.timeout)
        return response

class GenList:
    def __init__(self, query, requester):
        self.query = query
        self.requester = requester
        
    def get_query_list(self):
        if re.match("^[0-9]{4}-[0-9]{3}[0-9xX]$", self.query[0]):
            issn = self.query[0]
            if len(self.query) in (2, 3) and all([re.match("^[\d]{4}$", i) for i in self.query[1:]]):
                year0, year1 = int(self.query[1]), int(self.query[-1])
                if not (1666 < year0 <= year1 <= datetime.now().year):
                    typer.secho('Please ensure valid year.', fg=typer.colors.MAGENTA)
                    raise typer.Exit(code=1)
            else:
                typer.secho('Please follow format: "sci-clone ISSN FROM_YEAR [TO_YEAR]"',
                            fg=typer.colors.MAGENTA)
                raise typer.Exit(code=1)
            container_title, list_dict = self.get_journal_works(issn, year0, year1)
        else:
            query_list = []
            for line in self.query:
                if line.endswith('.txt') or line.endswith('.bib'):
                    query_list += list(self.get_file_list(line))
                else:
                    query_list += [line,]
            container_title = "paper list"
            list_dict = {container_title: query_list}
        return container_title, list_dict
    
    def get_file_list(self, file_path):
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
            
    def get_journal_works(self, issn, year_start, year_end):
        url = f"http://api.crossref.org/journals/{issn}/works"
        cursor = '*'
        results = list()
        while True:
            from_to = f"from-pub-date:{year_start},until-pub-date:{year_end}"
            r = self.requester.request(url, params={"rows": 1000, "cursor": cursor, "filter": from_to})
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
    
class Processing:
    def __init__(self, scihub, requester, query, save_to):
        self.scihub = scihub
        self.requester = requester
        self.query = query
        self.save_to = save_to
        
    def download(self):
        title, list_dict = self.query
        for key,query_list in list_dict.items():
            if title == key:
                label = f"{title}: {len(query_list)}"
                sub_dir = self.save_to
            else:
                label = f"{title} ({key}): {len(query_list)}"
                sub_dir = path.join(self.save_to, str(key))
                if not path.exists(sub_dir): mkdir(sub_dir)
            self.walk_the_list(label, query_list, sub_dir)
        
    def walk_the_list(self, label, query_list, sub_dir):
   #     print(version_callback(False))
        undone = list()
        with typer.progressbar(query_list, label=label, show_eta=False, show_percent=False, fill_char="▒", 
                               item_show_func=lambda x: f"{str(query_list.index(x))} | {x}" if x else x) as progress:
            for query in progress:
                item_done = self.get_pdf_scihub(query, sub_dir)
                if not item_done:
                    undone.append(query)
        log = path.join(sub_dir, "missing.log")
        with open(log, 'w') as f:
            if undone:
                f.writelines([f"{i}\n" for i in undone])
                typer.secho(f'missing log: {log}', fg=typer.colors.MAGENTA, bold=True, italic=True)
            else:
                f.write("all done.")
                typer.secho("all done.", fg=typer.colors.GREEN, bold=True, italic=True)
        return undone
    
    def get_pdf_scihub(self, query, sub_dir):
        response = self.requester.request(self.scihub, params={"request": query}, method="POST")
        response_text = response.read().decode()
        if "Sorry, sci-hub has not included this article yet" in response_text:
            file_url, file_name = False, False
        else:
            file_url = re.search("location.href=\'(.+)'\">(.+) save", response_text).group(1).replace("\\", "")
            if "/pdf/" in file_url: 
                file_name = re.search("/pdf/(.+)\?", file_url).group(1).replace("/", "@")
            else:
                file_name = file_url.split("/")[-1].replace("?download=true", "")
        if file_name:
            file_path = path.join(sub_dir, file_name)
            if path.exists(file_path):
                return True
            else:
                response = self.requester.request(file_url)
                with open(file_path, 'b+w') as f:
                    f.write(response.read())
                return True
        else:
            return False