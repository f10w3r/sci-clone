```

             _____ __________     ________    ____  _   ________
            / ___// ____/  _/    / ____/ /   / __ \/ | / / ____/
            \__ \/ /    / /_____/ /   / /   / / / /  |/ / __/
           ___/ / /____/ /_____/ /___/ /___/ /_/ / /|  / /___
          /____/\____/___/     \____/_____/\____/_/ |_/_____/

               A simple tool for cloning from Sci-Hub.

```

- Python Version > 3.6


### Procedure

1. Query the *Digital Object Identifier* (DOI)/URL from crossref.org;
2. Download articles from Sci-Hub with the DOI/URL.

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

- **DOI/URL**: [crossref.org](https://crossref.org)

- **Sci-Hub**: [sci-hub.wf](https://sci-hub.wf)

## Usage

### I. Download by DOI.

```console
$ sci-clone DOI [DOI] ...
```

#### Examples

- Download two articles with DOI/URL:

```console
$ sci-clone 10.1126/science.1248506 https://www.jstor.org/stable/27854031
```

- Download with the DOI/URL within a file: _doi.txt_ or _doi.bib_

```console
$ sci-clone examples/doi.txt
```

```{console}
$ sci-clone examples/doi.bib
```

### II. Download by Year (from a journal).

```console
$ sci-clone ISSN YEAR_FROM [YEAR_TO]
```

#### Examples

- Download articles from journal _American Journal of Sociology_ (ISSN: 0002-9602) in year 2020:

```console
$ sci-clone 0002-9602 2020
```

- Download articles from journal _Sociology of Education_ (ISSN: 0038-0407) from year 2010 to 2012:

```console
$ sci-clone 0038-0407 2010 2012
```

## Useful Configs

- Download and save the files to directory ```papers``` (should be created before download):

```{console}
$ sci-clone 0038-0407 2010 2012 -d papers
```

- If the default Sci-Hub URL is invalid, change it to another valid one:

```console
$ sci-clone 10.1126/science.1248506 -s sci-hub.tw
```

## Uninstallation

```console
$ pip uninstall sci-clone
```

## Notes

- Sci-Hub does not have every article that has DOI, the ones that not found are logged in file ```missing.log``` under each sub-directory.
