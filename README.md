```

             _____ __________     ________    ____  _   ________
            / ___// ____/  _/    / ____/ /   / __ \/ | / / ____/
            \__ \/ /    / /_____/ /   / /   / / / /  |/ / __/
           ___/ / /____/ /_____/ /___/ /___/ /_/ / /|  / /___
          /____/\____/___/     \____/_____/\____/_/ |_/_____/

               A simple tool for cloning from Sci-Hub.

```
### Procedure

1. Query the *Digital Object Identifier* (DOI) from crossref.org;
2. Download articles from Sci-Hub with the DOIs.

## Installation

- The simple command:

```console
$ pip install sci-clone
```

- or provide PyPI index if the above command fails:

```console
$ pip install sci-clone -i https://pypi.org/simple
```

- or install from this repository if your country cannot connect to PyPI:

```console
$ pip install git+https://github.com/f10w3r/sci-clone
```

## Default Sources

- **DOI**: [crossref.org](https://crossref.org)

- **Sci-Hub**: [sci-hub.tf](https://sci-hub.tf)

## Usage

### I. Download by DOI.

```console
$ sci-clone doi
Usage: sci-clone doi [OPTIONS] DOI...

Arguments:
  DOI...  Valid DOI(s) or file (*.bib, *.txt)  [required]

Options:
  -d, --dir PATH     Directory to download  [default: (dynamic)]
  -s, --scihub TEXT  Valid Sci-Hub URL  [default: sci-hub.tf]
  --help             Show this message and exit.
```

#### Examples

- Download two articles with DOIs:

```console
$ sci-clone doi 10.1126/science.1248506 10.1017/S0003055413000014
```

- Download with the DOIs within a file: _doi.txt_ or _doi.bib_

```console
$ sci-clone doi examples/doi.txt
```

```{console}
$ sci-clone doi examples/doi.bib
```

### II. Download by Year (from a journal).

```console
$ sci-clone issn
Usage: sci-clone issn [OPTIONS] ISSN YEAR:[%Y]...

Arguments:
  ISSN          Journal ISSN (e.g.: 0002-9602)  [required]
  YEAR:[%Y]...  From year to year (e.g.: 2011 2012)  [required]

Options:
  -d, --dir PATH     Directory to download  [default: (dynamic)]
  -s, --scihub TEXT  Valid Sci-Hub URL  [default: sci-hub.tf]
  --help             Show this message and exit.
```

#### Examples

- Download articles from journal _American Journal of Sociology_ (ISSN: 0002-9602) in year 2020:

```console
$ sci-clone issn 0002-9602 2020
```

- Download articles from journal _Sociology of Education_ (ISSN: 0038-0407) from year 2010 to 2012:

```console
$ sci-clone issn 0038-0407 2010 2012
```

## Useful Configs

- Download and save the files to directory ```papers``` (should be created before download):

```{console}
$ sci-clone issn 0038-0407 2010 2012 -d papers
```

- If the default Sci-Hub URL is invalid, change it to another valid one:

```console
$ sci-clone doi 10.1126/science.1248506 -s sci-hub.tw
```

## Uninstallation

```console
$ pip uninstall sci-clone
```

## Notes

- Sci-Hub does not have every article that has DOI, the ones that not found are logged in file ```missing.log``` under each sub-directory.
