#!/usr/bin/env python3
#-*- coding: UTF-8 -*-
import json, argparse, os, time, logging, random, progressbar
from bs4 import BeautifulSoup
from requests import Session
from requests.adapters import HTTPAdapter
from requests.compat import urljoin
from pyfiglet import Figlet

class color:
   PURPLE = '\033[95m'; CYAN = '\033[96m'; DARKCYAN = '\033[36m'; BLUE = '\033[94m'
   GREEN = '\033[92m'; YELLOW = '\033[93m'; RED = '\033[91m'
   BOLD = '\033[1m'; ITALIC = '\033[3m'; UNDERLINE = '\033[4m'; END = '\033[0m'

def init():
    # args define
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command')
    year_arg = subparser.add_parser('year')
    year_arg.add_argument('-i', dest='issn', type=str, required=True, nargs=1,
        help="journal ISSN (e.g.: 0002-9602)")
    year_arg.add_argument('-y', dest='year', type=str, required=True, nargs='*',
        help="from year [to year] (e.g.: 2010 2012)")
    year_arg.add_argument('-d', dest='dir', type=str, required=False, nargs=1, default=[os.getcwd(),],
        help="directory to download (default: current directory)")
    year_arg.add_argument('-s', dest='scihub', type=str, required=False, nargs=1, default=['sci-hub.tf',],
        help="valid Sci-Hub URL (default: sci-hub.tf)")
    doi_arg = subparser.add_parser('doi')
    doi_arg.add_argument('-a', dest='doi', type=str, required=True, nargs='*',
        help="valid DOI(s)")
    doi_arg.add_argument('-d', dest='dir', type=str, required=False, nargs=1, default=[os.getcwd(),],
        help="directory to download (default: current directory)")
    doi_arg.add_argument('-s', dest='scihub', type=str, required=False, nargs=1, default=['sci-hub.tf',],
        help="valid Sci-Hub URL (default: sci-hub.tf)")
    args = parser.parse_args()

    # args year
    if args.command == None:
        year_arg.print_help()
        print()
        doi_arg.print_help()
        parser.exit(2)
    else:
        if args.command == 'year':
            if len(args.year) == 2:
                if int(args.year[0]) > int(args.year[1]): 
                    year_arg.error('Invalid year, please arrange arguments chronologically.')
                if int(args.year[1]) < 1665 or int(args.year[0]) < 1665: 
                    year_arg.error('Invalid year, no journal that old.')
                if int(args.year[1]) > time.localtime().tm_year or int(args.year[0]) > time.localtime().tm_year: 
                    year_arg.error('Invalid year, not a time machine.')
            elif len(args.year) == 1:
                if int(args.year[0]) < 1665: 
                    year_arg.error('Invalid year, no journal that old.')
                if int(args.year[0]) > time.localtime().tm_year: 
                    year_arg.error('Invalid year, not a time machine.')
            else:
                year_arg.error('Invalid year, please follow: -y FROM [TO]')
        # args sci-hub url
        if args.scihub[0].startswith("http"):
            parser.error('Invalid URL, example: -s sci-hub.tf')
        else:
            args.scihub[0] = "https://" + args.scihub[0]

        # args directory
        if not os.path.exists(args.dir[0]): year_arg.error('Invalid path, please follow: -d DIR')

    # Requests Session with Retry
    session = Session()
    session.mount('http', HTTPAdapter(max_retries=3))
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})

    return args, session

def setup_logger(name, log_file, level=logging.INFO):
    # logging format
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file, mode='w') 
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

def get_link(url):
    html = session.get(url, timeout=60, allow_redirects=False)
    html.encoding = 'utf-8'
    html.raise_for_status()
    time.sleep(1)
    tag = BeautifulSoup(html.text, 'html.parser').find('a', {'href': '#'})
    if tag:
        return tag['onclick'].split("'")[1].replace('\\', '')
    else:
        return None

def get_article(article_url, file_path):
    if os.path.exists(file_path): return True
    """Downloads a single article based on its DOI."""
    link = get_link(article_url)
    if link:
        pdf_url = urljoin('https:', link) if link.startswith('//') else link
        pdf = session.get(pdf_url, stream=True)
        with open(file_path, 'wb') as f:
            for chunk in pdf.iter_content(2000): f.write(chunk)
        return True
    else:
        # Logs DOI when there is no iframe#pdf on the page
        return False

def get_doi(year, issn):
    url = "https://api.crossref.org/journals/" + issn + "/works"; cursor = '*'; doi_list = list()
    while True:
        r = session.get(url, params={'rows': 1000,'cursor': cursor,
                               'filter': 'from-pub-date:'+ str(year) + '-01' + ',until-pub-date:' + str(year) + '-12'})
        j = json.loads(r.text)
        if len(j['message']['items']) != 0:
            doi_list.extend(j['message']['items'])
            cursor = j['message']['next-cursor']
        else:
            break
    return doi_list

def dowload(articles, folder):
    log_file = os.path.join(folder, 'missing.log')
    logger = setup_logger(folder, log_file)
    if  len(articles) > 0:
        widgets = [progressbar.AdaptiveETA(format=' %(elapsed)s │ %(eta)s ',format_finished='        %(elapsed)s    ',),
                    progressbar.Bar('░', '├', '┤'),'   ', 
                    progressbar.Percentage(), '  ']
        bar = progressbar.ProgressBar(maxval=len(articles), widgets=widgets)
        bar.start()
        for i, article in enumerate(articles):
            done = get_article(article['article_url'], os.path.join(folder, article['file']))
            if not done: logger.warning("NOT_FOUND_IN_SCI-HUB:" + article['warning_str'])
            bar.update(i+1)
            time.sleep(0.01)
        bar.finish()
        downloaded = len([i for i in os.listdir(folder) if i.lower().endswith('.pdf')])
        print(f"\tDownloaded: {downloaded}/{len(articles)}")
        print("\tMissing Log:", log_file)
    else:
        print('no article.')
    logging.shutdown()

def year_process(args):
    year_queue = [int(args.year[0]),] if len(args.year) == 1 else range(int(args.year[0]), int(args.year[1]) + 1)
    for year in year_queue:
        article_list = get_doi(year, args.issn[0])
        journal_title = color.ITALIC + article_list[0]['container-title'][0] + ':' + color.END
        print(f"\n{journal_title} {len(article_list)} articles in year {year}.")
        folder = os.path.join(args.dir[0], args.issn[0] + '_' + str(year))
        if not os.path.exists(folder): os.mkdir(folder)
        articles = []
        for article in article_list:
            articles.append({
                "article_url": urljoin(args.scihub[0], article['DOI']), 
                "file": f"{article['volume']}_{article['DOI'].replace('/', '-')}.pdf",
                "warning_str": f"{article['DOI']}:{args.issn[0]}_{year}_vol{article['volume']}_issue{article['issue']}"})
        dowload(articles, folder)

def doi_process(args):
    print(f'\n{len(args.doi)} DOI(s) in the list.')
    articles = []
    for doi in args.doi:
        articles.append({
            "article_url": urljoin(args.scihub[0], doi),
            "file": f"{doi.replace('/', '-')}.pdf", 
            "warning_str": doi})
    dowload(articles, args.dir[0])

if __name__ == "__main__":
    args, session = init()

    # logo and title
    fonts = ['graceful', 'epic', 'big', 'small', 'shimrod', 'wavy', 'slant', 'doom', 'contessa',
        'cyberlarge', 'cybermedium', 'bell', 'smslant', 'ogre', 'weird', 'standard']
    f = Figlet(font=random.choice(fonts))
    logo = '\n\n' + color.GREEN + f.renderText('SCI-CLONE') + color.END
    title = "\tWelcome to " + color.ITALIC + "SCI-CLONE" + color.END + " ver_0.2.4 (by f10w3r)\n"
    source = f"Sci-Hub URL: {args.scihub[0].split('://')[-1]}\nDOI source: crossref.org"
    
    # main 
    print('\n'.join([logo, title, source]))
    try:
        if args.command == 'doi': doi_process(args)
        if args.command == 'year': year_process(args)
    except KeyboardInterrupt:
        print(color.RED + '\n=== mission aborted ===' + color.END)
