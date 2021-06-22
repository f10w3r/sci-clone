import json, argparse, os, time, logging
import requests, progressbar
from bs4 import BeautifulSoup

logo = r"""
 _______  _______ _________     _______  _        _______  _        _______
(  ____ \(  ____ \\__   __/    (  ____ \( \      (  ___  )( (    /|(  ____ \
| (    \/| (    \/   ) (       | (    \/| (      | (   ) ||  \  ( || (    \/
| (_____ | |         | | _____ | |      | |      | |   | ||   \ | || (__
(_____  )| |         | |(_____)| |      | |      | |   | || (\ \) ||  __)
      ) || |         | |       | |      | |      | |   | || | \   || (
/\____) || (____/\___) (___    | (____/\| (____/\| (___) || )  \  || (____/\
\_______)(_______/\_______/    (_______/(_______/(_______)|/    )_)(_______/

            Welcome to SCI-CLONE Ver 1.1 (by f10w3r)
"""


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
}

parser = argparse.ArgumentParser()
parser.add_argument('-i', dest='issn', type=str, required=True, nargs=1, help="journal ISSN (e.g.: 0002-9602)")
parser.add_argument('-y', dest='year', type=str, required=True, nargs='*', help="from year to year (e.g.: 2010 2012)")
parser.add_argument('-d', dest='dir', type=str, required=False, nargs=1, default=[os.getcwd(),], help="directory to download (default: current directory)")
parser.add_argument('-s', dest='scihub', type=str, required=False, nargs=1, default=['sci-hub.tf',], help="Valid Sci-Hub URL (default: sci-hub.tf)")
args = parser.parse_args()

if len(args.year) not in (1, 2):
    parser.error('Invalid year, please follow: -y FROM [TO]')
if not os.path.exists(args.dir[0]):
    parser.error('Invalid path, please follow: -d DIR')
if args.scihub[0].startswith("http"):
    parser.error('Invalid URL, example: -s sci-hub.tf')
else:
    args.scihub[0] = "https://" + args.scihub[0] + "/"


def get_html(url):
    s = requests.Session()
    html = s.get(url, timeout=60, headers=headers, allow_redirects=False)
    html.encoding = 'utf-8'
    html.raise_for_status()
    html = BeautifulSoup(html.text, 'html.parser')
    return html

def get_article(article, folder):
    new_fn = '{0}_{1}.pdf'.format(article['volume'], article['DOI'].replace('/', '-'))
    file_path = os.path.join(args.dir[0], folder, new_fn)
    if os.path.exists(file_path):
        return True
    """Downloads a single article based on its DOI."""
    article_url = args.scihub[0] + article['DOI']
    html = get_html(article_url)
    time.sleep(1)

    save = html.find('a', {'href': '#'})
    if save:
        pdf_url = save['onclick'].split("'")[1].replace('\\', '')
        if pdf_url.startswith('//'):
            pdf_url = 'https:' + pdf_url
        pdf = requests.get(pdf_url, stream=True, headers = headers)
            
        with open(file_path, 'wb') as f:
            for chunk in pdf.iter_content(2000):
                f.write(chunk)
        time.sleep(1)
        return True
    else:
        # Logs DOI when there is no iframe#pdf on the page
        return False
#        print('no DOI: ', article['DOI'])

def get_doi(year, issn):
    url = "https://api.crossref.org/journals/" + issn + "/works"
    cursor = '*'
    doi_list = list()
    while True:
        params = {'rows': 1000,
                  'filter': 'from-pub-date:'+ str(year) + '-01' + ',until-pub-date:' + str(year) + '-12',
                  'cursor': cursor}
        r = requests.get(url, params=params)
        j = json.loads(r.text)
    #    print(j)
        if len(j['message']['items']) != 0:
            doi_list.extend(j['message']['items'])
            cursor = j['message']['next-cursor']
        else:
            break
    return doi_list
        
if __name__ == "__main__":
    print(logo)
    print('\tSCI-HUB URL:', args.scihub[0][8:-1])
    print('\tDOI source:', "crossref.org", '\n')
    if len(args.year) == 1:
        year_queue = [int(args.year[0]),]
    else:
        year_queue = range(int(args.year[0]), int(args.year[1]) + 1)
    for year in year_queue:
        folder = args.issn[0] + '_' + str(year)
        if not os.path.exists(os.path.join(args.dir[0], folder)):
            os.mkdir(os.path.join(args.dir[0], folder))
        log_file = os.path.join(args.dir[0], folder, 'missing.log')
        logging.basicConfig(filename=log_file, filemode='w')
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
                done = get_article(article, folder=folder)
                if not done:
                    logging.info('NO DOI:', article['DOI'], '(position:{0}_{1})'.format(article['volume'], article['issue']))
                bar.update(i+1)
                time.sleep(0.01)
            bar.finish()
            downloaded_article = len([i for i in os.listdir(os.path.join(args.dir[0], folder)) if (i.endswith('.pdf') or i.endswith('.PDF'))])
            print('{0}: year {1} download finished, {2}/{3} downloaded.'.format(article_list[0]['container-title'][0], year, downloaded_article, total_article))
            print("missing articles see:", log_file)
        else:
            print('no article.')
            continue
