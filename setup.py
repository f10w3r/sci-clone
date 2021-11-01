#-*- coding: UTF-8 -*-
from setuptools import setup, find_packages
from sci_clone.version import __name__, __version__, __url__

with open('requirements.txt') as f:
    REQUIREMENTS = f.readlines()

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

NAME = __name__
VERSION = __version__
URL = __url__
AUTHOR = "f10w3r"
AUTHOR_EMAIL = "lifuminster@gmail.com"
DESCRIPTION = "A simple script for downloading articles from Sci-Hub."

setup(
    name=NAME,
    version=VERSION,    
    description=DESCRIPTION,
    url=__url__,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    long_description = LONG_DESCRIPTION,
    long_description_content_type = "text/markdown",
    license = "MIT",
    packages = find_packages(),
    entry_points = {
        "console_scripts": [
            "sci-clone=sci_clone.main:main"
        ]
    },
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    keywords = "sci-hub sci-clone sci_clone sciclone issn doi paper article journal",
    install_requires = REQUIREMENTS,
    zip_safe = False
)