# -*- coding: utf-8 -*-
import sphinx_rtd_theme
import os
import sys

docs_root = os.path.dirname(__file__)
lib_root = os.path.dirname(docs_root)
sys.path.insert(1, lib_root)
from setup import get_info

info = get_info(os.path.join(lib_root, 'construct', '__init__.py'))

project = info['title']
copyright = '2017, ' + info['author']
author = info['author']
version = info['version']
release = info['version']
language = None

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'
todo_include_todos = True
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
html_sidebars = {
    '**': [
        'relations.html',
        'searchbox.html',
    ]
}
htmlhelp_basename = project + 'doc'
intersphinx_mapping = {'https://docs.python.org/': None}
