# -*- coding: utf-8 -*-
# Standard library imports
import re

# Third party imports
from setuptools import find_packages, setup


def get_meta(pyfile, readme):
    meta = {}

    # Get dunder values from python file
    pattern = re.compile(r"^__(\w+)__ = ['\"](.*)['\"]")
    with open(pyfile, 'r') as f:
        for line in f.readlines():
            match = pattern.search(line)
            if match:
                meta[match.group(1)] = match.group(2)

    # Get contents of readme
    with open(readme, 'r') as f:
        meta['readme'] = f.read()

    return meta


meta = get_meta('./construct/__init__.py', 'README.rst')


setup(
    name=meta['title'],
    version=meta['version'],
    author=meta['author'],
    author_email=meta['email'],
    description=meta['description'],
    url=meta['url'],
    long_description=meta['readme'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=[
        'bson',
        'cachetools',
        'cerberus',
        'colorama',
        'entrypoints',
        'fsfs',
        'pathlib2; python_version<"3.6"',
        'pyyaml',
        'Qt.py',
        'qtsass @ git+https://github.com/spyder-ide/qtsass', # TODO: pypi
        'scrim',
        'win_unicode_console',
    ],
    entry_points={
        'console_scripts': [
            'pyconstruct = construct.cli.__main__:main'
        ]
    },
    scripts=[
        'bin/construct.bat',
        'bin/construct.ps1',
        'bin/construct',
    ],
)
