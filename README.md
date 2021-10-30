# SCI-CLONE

```
   _____ __________     ________    ____  _   ________
  / ___// ____/  _/    / ____/ /   / __ \/ | / / ____/
  \__ \/ /    / /_____/ /   / /   / / / /  |/ / __/   
 ___/ / /____/ /_____/ /___/ /___/ /_/ / /|  / /___   
/____/\____/___/     \____/_____/\____/_/ |_/_____/ 
```
A simple script for downloading articles from Sci-Hub. 

The main idea:

1. Query the *Digital Object Identifier* (DOI) from crossref.org;
2. Download articles from Sci-Hub with the DOIs.

## Installation

  ```{bash}
  $ git clone https://github.com/f10w3r/sci-clone
  $ cd sci-clone
  $ pip install .
  ```

## Default Sources

  DOI: [crossref.org](https://crossref.org)

  Sci-Hub: [sci-hub.tf](https://sci-hub.tf)

## 

### I. Download Articles Annually 

  ```sci-clone issn --help``` for help.
  ```{bash}
Usage: sci-clone issn [OPTIONS] ISSN YEAR:[%Y]...

Arguments:
  ISSN          Journal ISSN (e.g.: 0002-9602)  [required]
  YEAR:[%Y]...  From year to year (e.g.: 2011 2012)  [required]

Options:
  -d, --dir PATH     Directory to download  [default: (dynamic)]
  -s, --scihub TEXT  Valid Sci-Hub URL  [default: sci-hub.tf]
  -v, --version      Show version
  --help             Show this message and exit.
  ```
#### Examples

   1. Download articles from journal _American Journal of Sociology_ (ISSN: 0002-9602) in year 2020:
   ```{bash}
   $ sci-clone issn 0002-9602 2020
   ```

   2. Download articles from journal _Sociology of Education_ (ISSN: 0038-0407) from year 2010 to 2012, save the files to directory ```AJS_2010-2012``` (should be created in advance):
   ```{bash}
   $ sci-clone issn 0038-0407 2010 2012 -d AJS_2010-2012
   ```

   3. If the default Sci-Hub URL is invalid, change it to another valid:
   ```{bash}
   $ sci-clone issn 0038-0407 2010 2012 -s sci-hub.tw
   ```

### II. Download Article w/ DOI

```sci-clone doi --help``` for help.

```{bash}
Usage: sci-clone doi [OPTIONS] DOI...

Arguments:
  DOI...  valid DOI(s)  [required]

Options:
  -d, --dir PATH     Directory to download  [default: (dynamic)]
  -s, --scihub TEXT  Valid Sci-Hub URL  [default: sci-hub.tf]
  -v, --version      Show version
  --help             Show this message and exit.
```

#### Examples

- Download two articles with DOIs:

```{bash}
$ sci-clone doi 10.1126/science.1248506 10.1017/S0003055413000014
```

## Uninstallation

```{bash}
$ pip uninstall sci-clone
```

### Notes

   Sci-Hub does not have every article that has DOI, the ones that not found are logged in file ```missing.log``` under each sub-directory.

   
