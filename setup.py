#-*- coding: UTF-8 -*-
from setuptools import setup, find_packages
from sci_clone import config

with open('requirements.txt') as f:
    REQUIREMENTS = f.readlines()

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name=config.__name__,
    version=config.__version__,    
    description=config.__description__,
    url=config.__url__,
    author=config.__author__,
    author_email=config.__author_email__,
    long_description = LONG_DESCRIPTION,
    long_description_content_type = "text/markdown",
    license = "MIT",
    packages = find_packages(),
    entry_points = {
        "console_scripts": [
            "sci-clone=sci_clone.main:app"
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