# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import sys
import re


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
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'werkzeug',
        'scrim',
        'fstrings',
        'chainmap',
        'colorama',
        'scandir',
        'backports.shutil_get_terminal_size',
        'win_unicode_console',
        'fsfs',
        'entrypoints'
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
