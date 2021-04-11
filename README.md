# SCI-CLONE

A simple script for downloading journal articles yearly from Sci-hub. 

The main idea is that first to query the DOI from crossref.org, and then download article with the DOI from Sci-Hub.

## Dependencies

  ```{python}
  pip install requests BeautifulSoup progressbar
  ```

## Default Sources

  DOI: [crossref.org](https://crossref.org)

  Sci-Hub: [sci-hub.tf](https://sci-hub.tf)


## Usage

  ```./sci-clone -h``` for help.
  ```{bash}
  usage: sci-clone [-h] -i ISSN -y [YEAR [YEAR ...]] [-d DIR] [-s SCIHUB]

  optional arguments:
    -h, --help            show this help message and exit
    -i ISSN               journal ISSN (e.g.: 0002-9602)
    -y [YEAR [YEAR ...]]  from year to year (e.g.: 2010 2012)
    -d DIR                directory to download (default: current directory)
    -s SCIHUB             Valid Sci-Hub URL (default: sci-hub.tf)
   ```
   ```-i -y``` are compulsory arguments.
 
   ### Examples

   1. Download articles from journal _American Journal of Sociology_ (ISSN: 0002-9602) in year 2020:
   ```{bash}
   ./sci-clone -i 0002-9602 -y 2020
   ```

   2. Download articles from journal _Sociology of Education_ (ISSN: 0038-0407) from year 2010 to 2012, save the files to directory ```AJS_2010-2012``` (should be created in advance):
   ```{bash}
   ./sci-clone -i 0038-0407 -y 2010 2012 -d ./AJS_2010-2012
   ```

   3. If the default Sci-Hub URL is invalid, change it to another valid:
   ```{bash}
   ./sci-clone -i 0038-0407 -y 2010 2012 -s sci-hub.tw
   ```
   
   ### Notes
   
   Sic-Hub does not have every article that has DOI, the ones not found are logged in file ```missing.log``` under each sub-directory.
   
   
