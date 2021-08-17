# SCI-CLONE

```
   _____ __________     ________    ____  _   ________
  / ___// ____/  _/    / ____/ /   / __ \/ | / / ____/
  \__ \/ /    / /_____/ /   / /   / / / /  |/ / __/   
 ___/ / /____/ /_____/ /___/ /___/ /_/ / /|  / /___   
/____/\____/___/     \____/_____/\____/_/ |_/_____/ 
```
A simple script for downloading journal articles from Sci-Hub. 

The main idea:

1. Query the *Digital Object Identifier* (DOI) from crossref.org;
2. Download articles from Sci-Hub with the DOIs.

## Dependencies

Only available on Python 3.x:

  ```{python}
  pip3 install -r requirements.txt
  ```

## Default Sources

  DOI: [crossref.org](https://crossref.org)

  Sci-Hub: [sci-hub.tf](https://sci-hub.tf)

## Usage

Assign execution permissions:

```bash
$ chmod +x ./sci-clone.py
```

### I. Download Articles Annually 

  ```./sci-clone.py year -h``` for help.
  ```{bash}
usage: sci-clone.py year [-h] -i ISSN -y [YEAR [YEAR ...]] [-d DIR] [-s SCIHUB]

optional arguments:
  -h, --help            show this help message and exit
  -i ISSN               journal ISSN (e.g.: 0002-9602)
  -y [YEAR [YEAR ...]]  from year [to year] (e.g.: 2010 2012)
  -d DIR                directory to download (default: current directory)
  -s SCIHUB             valid Sci-Hub URL (default: sci-hub.tf)
  ```
   ```-i -y``` are compulsory arguments.

#### Examples

   1. Download articles from journal _American Journal of Sociology_ (ISSN: 0002-9602) in year 2020:
   ```{bash}
   $ ./sci-clone.py -i 0002-9602 -y 2020
   ```

   2. Download articles from journal _Sociology of Education_ (ISSN: 0038-0407) from year 2010 to 2012, save the files to directory ```AJS_2010-2012``` (should be created in advance):
   ```{bash}
   $ ./sci-clone.py -i 0038-0407 -y 2010 2012 -d ./AJS_2010-2012
   ```

   3. If the default Sci-Hub URL is invalid, change it to another valid:
   ```{bash}
   $ ./sci-clone.py -i 0038-0407 -y 2010 2012 -s sci-hub.tw
   ```

### II. Download Article(s) w/ DOI(s)

```./sci-clone.py doi -h``` for help.

```{bash}
usage: sci-clone.py doi [-h] -a [DOI [DOI ...]] [-d DIR] [-s SCIHUB]

optional arguments:
  -h, --help          show this help message and exit
  -a [DOI [DOI ...]]  valid DOI(s)
  -d DIR              directory to download (default: current directory)
  -s SCIHUB           valid Sci-Hub URL (default: sci-hub.tf)
```

```-a``` is compulsory argument.

#### Examples

1. Download two articles with DOIs:

```{bash}
$ ./sci-clone.py doi -a 10.1126/science.1248506 10.1017/S0003055413000014
```

2. Download an article to directory ```papers``` (should be created in advance):

```{bash}
$ ./sci-clone.py doi -a 10.1126/science.1248506 -d ./papers
```



### Notes

   Sci-Hub does not have every article that has DOI, the ones that not found are logged in file ```missing.log``` under each sub-directory.

   
