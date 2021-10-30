from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.readlines()

with open('README.md') as f:
    long_description = f.readlines()
  
setup(
    name='sci_clone',
    version='0.3.0',    
    description='A simple script for downloading articles from Sci-Hub.',
    url='https://github.com/f10w3r/sci-clone',
    author='f10w3r',
    author_email='lifuminster@gmail.com',
    long_description = long_description,
    long_description_content_type ="text/markdown",
    license ='MIT',
    packages = ['sci_clone'],
    entry_points ={
        'console_scripts': [
            'sci-clone=sci_clone.__main__:main'
        ]
    },
    classifiers =[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords ='sci-hub sci-clone sci_clone sciclone issn doi paper article journal',
    install_requires = requirements,
    zip_safe = False
)