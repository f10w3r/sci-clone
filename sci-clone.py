#!/usr/bin/env python3

import json, argparse, os, time, logging, random
import requests, progressbar
from bs4 import BeautifulSoup
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
    html.encoding = 'utf-8'
    html.raise_for_status()
    html = BeautifulSoup(html.text, 'html.parser')
    return html

def get_article(article_url, file_path):
    if os.path.exists(file_path):
        return True
    """Downloads a single article based on its DOI."""
    html = get_html(article_url)
    time.sleep(1)

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

def year_process(args):
    print(logo)
    print(title)
    print(source)
    if len(args.year) == 1:
        year_queue = [int(args.year[0]),]
    else:
        year_queue = range(int(args.year[0]), int(args.year[1]) + 1)
    for year in year_queue:
        folder = args.issn[0] + '_' + str(year)
        if not os.path.exists(os.path.join(args.dir[0], folder)):
            os.mkdir(os.path.join(args.dir[0], folder))
        log_file = os.path.join(args.dir[0], folder, 'missing.log')
        logger = setup_logger(folder, log_file)
        article_list = get_doi(year, args.issn[0])
        total_article = len(article_list)
        if  total_article > 0:
            print('{0}: {1} articles in year {2}.'.format(article_list[0]['container-title'][0], len(article_list), year))
            widgets = ['Progress: ', progressbar.Percentage(), 
                   ' ', progressbar.Bar('=', '[', ']'), 
                   ' ', progressbar.Timer(), 
                   ' ', progressbar.ETA()]
            bar = progressbar.ProgressBar(maxval=len(article_list), widgets=widgets)
            bar.start()
            for i, article in enumerate(article_list):
                new_fn = '{0}_{1}.pdf'.format(article['volume'], article['DOI'].replace('/', '-'))
                file_path = os.path.join(args.dir[0], folder, new_fn)
                article_url = urljoin(args.scihub[0], article['DOI'])
                done = get_article(article_url, file_path)
                if not done:
                    warning_str = 'NOT_FOUND_IN_SCI-HUB:{}:{}_{}_vol{}_issue{}'.format(article['DOI'], args.issn[0], year, article['volume'],article['issue'])
                    logger.warning(warning_str)
                bar.update(i+1)
                time.sleep(0.01)
            bar.finish()
            downloaded_article = len([i for i in os.listdir(os.path.join(args.dir[0], folder)) if (i.endswith('.pdf') or i.endswith('.PDF'))])
            print('{0}: year {1} download finished, {2}/{3} downloaded.'.format(article_list[0]['container-title'][0], year, downloaded_article, total_article))
            print("missing articles see:", log_file)
        else:
            print('no article.')
            continue
        logging.shutdown()

def doi_process(args):
    print(logo)
    print(title)
    print(source)
    log_file = os.path.join(args.dir[0], 'missing.log')
    logger = setup_logger('doi_process', log_file)
    doi_list = args.doi
    total_doi = len(doi_list)
    if  total_doi > 0:
        print('{} DOIs in the list.'.format(total_doi))
        widgets = ['Progress: ', progressbar.Percentage(), 
               ' ', progressbar.Bar('=', '[', ']'), 
               ' ', progressbar.Timer(), 
               ' ', progressbar.ETA()]
        bar = progressbar.ProgressBar(maxval=total_doi, widgets=widgets)
        bar.start()
        for i, doi in enumerate(doi_list):
            new_fn = '{}.pdf'.format(doi.replace('/', '-'))
            file_path = os.path.join(args.dir[0], new_fn)
            article_url = urljoin(args.scihub[0], doi)
            done = get_article(article_url, file_path)
            if not done:
                warning_str = 'NOT_FOUND_IN_SCI-HUB:{}'.format(doi)
                logger.warning(warning_str)
            bar.update(i+1)
            time.sleep(0.01)
        bar.finish()
        downloaded_doi = len([i for i in os.listdir(args.dir[0]) if (i.endswith('.pdf') or i.endswith('.PDF'))])
        print('download finished, {}/{} downloaded.'.format(downloaded_doi, total_doi))
        print("missing articles see:", log_file)
    else:
        print('no article.')
    logging.shutdown()
        
if __name__ == "__main__":

    # logo and title
    fonts = [
        'graceful', 'epic', 'big', 'small', 'shimrod', 'wavy', 'slant', 'doom', 'contessa', 
        'cyberlarge', 'cybermedium', 'bell', 'smslant', 'ogre', 'weird', 'standard'
    ]
    font = random.choice(fonts)
    f = Figlet(font=font)
    logo = '\n\n' + f.renderText('SCI-CLONE')
    title = "\tWelcome to SCI-CLONE ver_0.2.0 (by f10w3r)\n"


    # Requests Session with Retry
    retry = HTTPAdapter(max_retries=3)
    s = requests.Session()
    s.mount('http://', retry)
    s.mount('https://', retry)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    }

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

    source = 'Sci-Hub URL: {}'.format(args.scihub[0]) + '\nDOI source: {}\n'.format("crossref.org")

    # sci-hub url
    if args.scihub[0].startswith("http"):
        parser.error('Invalid URL, example: -s sci-hub.tf')
    else:
        args.scihub[0] = "https://" + args.scihub[0]

    # directory
    if not os.path.exists(args.dir[0]):
        year_arg.error('Invalid path, please follow: -d DIR')
    

    if args.command == 'doi':
        doi_process(args)
    elif args.command == 'year':
        if len(args.year) not in (1, 2):
            parser.error('Invalid year, please follow: -y FROM [TO]')
        year_process(args)

    
        
        
    
    
        
