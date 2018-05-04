# -*- coding: utf-8 -*-
from __future__ import absolute_import

try:
    basestring = basestring
except NameError:
    basestring = (str, bytes)


def pkg_resources():
    '''Make sure we get the pkg_resources that installed construct.

    Nuke ships with setuptools-0.6c11-py26.egg - an extremely archaic version
    of setuptools. In setuptools prior to the introduction of python wheels
    pkg_resources found entry_points by parsing .egg-info directories. Nowadays
    we install wheels and package metadata is stored in .dist-info directories.
    '''
    from os.path import exists
    from construct.utils import package_path, import_file

    pkg_resources_path = package_path('../pkg_resources')
    if not exists(pkg_resources_path):
        # Fallback to standard import
        import pkg_resources
        return pkg_resources

    pkg_resources = import_file(pkg_resources_path, remove=True)
    return pkg_resources
