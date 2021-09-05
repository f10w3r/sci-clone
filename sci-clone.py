#!/usr/bin/env python3

import json, argparse, os, time, logging, random, progressbar
from bs4 import BeautifulSoup
from requests import Session
from requests.adapters import HTTPAdapter
from requests.compat import urljoin
from pyfiglet import Figlet



def setup_logger(name, log_file, level=logging.INFO):
    # logging format
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler = logging.FileHandler(log_file, mode='w')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

def get_html(url):
    html = s.get(url, timeout=60, headers=headers, allow_redirects=False)
    time.sleep(1)
    html.encoding = 'utf-8'
    html.raise_for_status()
    html = BeautifulSoup(html.text, 'html.parser')
    return html

def get_article(article_url, file_path):
    if os.path.exists(file_path):
        return True
    """Downloads a single article based on its DOI."""
    html = get_html(article_url)
    save = html.find('a', {'href': '#'})
    if save:
        pdf_url = save['onclick'].split("'")[1].replace('\\', '')
        if pdf_url.startswith('//'):
            pdf_url = 'https:' + pdf_url
        pdf = s.get(pdf_url, stream=True, headers = headers)
            
        with open(file_path, 'wb') as f:
            for chunk in pdf.iter_content(2000):
                f.write(chunk)
        time.sleep(1)
        return True
    else:
        # Logs DOI when there is no iframe#pdf on the page
        return False

def get_doi(year, issn):
    url = "https://api.crossref.org/journals/" + issn + "/works"
    cursor = '*'
    doi_list = list()
    while True:
        params = {'rows': 1000,
                  'filter': 'from-pub-date:'+ str(year) + '-01' + ',until-pub-date:' + str(year) + '-12',
                  'cursor': cursor}
        r = s.get(url, params=params)
        j = json.loads(r.text)
        if len(j['message']['items']) != 0:
            doi_list.extend(j['message']['items'])
            cursor = j['message']['next-cursor']
        else:
            break
    return doi_list


def dowload(articles, folder, intro_str):
    log_file = os.path.join(folder, 'missing.log')
    logger = setup_logger(folder, log_file)
    total_article = len(articles)
    if  total_article > 0:
        print(intro_str)
        widgets = ['Progress: ', progressbar.Percentage(), ' ', progressbar.Bar('=', '[', ']'),' ', progressbar.Timer(), ' ', progressbar.ETA()]
        bar = progressbar.ProgressBar(maxval=total_article, widgets=widgets)
        bar.start()
        for i, article in enumerate(articles):
            done = get_article(article['article_url'], os.path.join(folder, article['file']))
            if not done:
                logger.warning(article['warning_str'])
            bar.update(i+1)
            time.sleep(0.01)
        bar.finish()
        downloaded = len([i for i in os.listdir(folder) if (i.endswith('.pdf') or i.endswith('.PDF'))])
        print('download finished, {}/{} downloaded.'.format(downloaded, total_article))
        print("missing articles see:", log_file)
    else:
        print('no article.')
    logging.shutdown()


def year_process(args):
    if len(args.year) == 1:
        year_queue = [int(args.year[0]),]
    else:
        year_queue = range(int(args.year[0]), int(args.year[1]) + 1)
    for year in year_queue:
        folder = os.path.join(args.dir[0], args.issn[0] + '_' + str(year))
        if not os.path.exists(os.path.join(args.dir[0], folder)):
            os.mkdir(folder)
        article_list = get_doi(year, args.issn[0])
        intro_str = '{0}: {1} articles in year {2}.'.format(article_list[0]['container-title'][0], len(article_list), year)
        articles = []
        for article in article_list:
            article_url = urljoin(args.scihub[0], article['DOI'])
            file = '{0}_{1}.pdf'.format(article['volume'], article['DOI'].replace('/', '-'))
            warning_str = 'NOT_FOUND_IN_SCI-HUB:{}:{}_{}_vol{}_issue{}'.format(article['DOI'], args.issn[0], year, article['volume'],article['issue'])
            articles.append({"article_url": article_url, "file": file, "warning_str": warning_str})
        dowload(articles, folder, intro_str)


def doi_process(args):
    folder = args.dir[0]
    doi_list = args.doi
    intro_str = '{} DOI(s) in the list.'.format(len(doi_list))
    articles = []
    for doi in doi_list:
        article_url = urljoin(args.scihub[0], doi)
        file = '{}.pdf'.format(doi.replace('/', '-'))
        warning_str = 'NOT_FOUND_IN_SCI-HUB:{}'.format(doi)
        articles.append({"article_url": article_url, "file": file, "warning_str": warning_str})
    dowload(articles, folder, intro_str)


        
if __name__ == "__main__":
    # Requests Session with Retry
    retry = HTTPAdapter(max_retries=3)
    s = Session()
    s.mount('http://', retry)
    s.mount('https://', retry)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}

    # args
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command')

    year_arg = subparser.add_parser('year')
    year_arg.add_argument('-i', dest='issn', type=str, required=True, nargs=1, help="journal ISSN (e.g.: 0002-9602)")
    year_arg.add_argument('-y', dest='year', type=str, required=True, nargs='*', help="from year [to year] (e.g.: 2010 2012)")
    year_arg.add_argument('-d', dest='dir', type=str, required=False, nargs=1, default=[os.getcwd(),], help="directory to download (default: current directory)")
    year_arg.add_argument('-s', dest='scihub', type=str, required=False, nargs=1, default=['sci-hub.tf',], help="valid Sci-Hub URL (default: sci-hub.tf)")

    doi_arg = subparser.add_parser('doi')
    doi_arg.add_argument('-a', dest='doi', type=str, required=True, nargs='*', help="valid DOI(s)")
    doi_arg.add_argument('-d', dest='dir', type=str, required=False, nargs=1, default=[os.getcwd(),], help="directory to download (default: current directory)")
    doi_arg.add_argument('-s', dest='scihub', type=str, required=False, nargs=1, default=['sci-hub.tf',], help="valid Sci-Hub URL (default: sci-hub.tf)")

    args = parser.parse_args()


    # year
    if len(args.year) == 2:
        if int(args.year[0]) > int(args.year[1]):
            year_arg.error('Invalid year, please arrange arguments chronologically.')
        if int(args.year[1]) < 1665:
            year_arg.error('Invalid year, no journal that old.')
        if int(args.year[1]) > time.localtime().tm_year:
            year_arg.error('Invalid year, not a time machine.')
    elif len(args.year) == 1:
        if int(args.year[0]) > time.localtime().tm_year:
            year_arg.error('Invalid year, not a time machine.')
        if int(args.year[0]) < 1665:
            year_arg.error('Invalid year, no journal that old.')
    else:
        year_arg.error('Invalid year, please follow: -y FROM [TO]')


    # sci-hub url
    if args.scihub[0].startswith("http"):
        parser.error('Invalid URL, example: -s sci-hub.tf')
    else:
        args.scihub[0] = "https://" + args.scihub[0]

    # directory
    if not os.path.exists(args.dir[0]):
        year_arg.error('Invalid path, please follow: -d DIR')

    # logo and title
    fonts = [
        'graceful', 'epic', 'big', 'small', 'shimrod', 'wavy', 'slant', 'doom', 'contessa', 
        'cyberlarge', 'cybermedium', 'bell', 'smslant', 'ogre', 'weird', 'standard'
    ]
    font = random.choice(fonts)
    f = Figlet(font=font)
    logo = '\n\n' + f.renderText('SCI-CLONE')
    title = "\tWelcome to SCI-CLONE ver_0.2.2 (by f10w3r)\n"
    source = 'Sci-Hub URL: {}'.format(args.scihub[0]) + '\nDOI source: {}\n'.format("crossref.org")

    
    # main
    print('\n'.join([logo, title, source]))
    if args.command == 'doi':
        doi_process(args)
    elif args.command == 'year':
        year_process(args)

    
        
        
    
    
        
