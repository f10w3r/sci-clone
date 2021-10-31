from setuptools import setup
from json import loads
from sci_clone.__config__ import CONFIG

with open('requirements.txt') as f:
    requirements = f.readlines()

with open('README.md') as f:
    long_description = f.read()

setup(
    name=CONFIG['name'],
    version=CONFIG['version'],    
    description=CONFIG['description'],
    url=CONFIG['url'],
    author=CONFIG['author'],
    author_email=CONFIG['author_email'],
    long_description = long_description,
    long_description_content_type = CONFIG['long_description_content_type'],
    license = CONFIG['license'],
    packages = CONFIG['packages'],
    entry_points = CONFIG['entry_points'],
    classifiers = CONFIG['classifiers'],
    keywords = CONFIG['keywords'],
    install_requires = requirements,
    zip_safe = CONFIG['zip_safe']
)