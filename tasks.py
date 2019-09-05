#!/usr/bin/env
# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import
import os

# Third party imports
import qtsass
from invoke import task


def joinpath(*parts):
    return os.path.join(*parts).replace('\\', '/')


@task
def tests(ctx, level='WARNING', module=None):
    '''Run tests using nose'''

    nose_cmd = (
        'nosetests '
        '--verbosity=2 '
        '--nocapture '
        '--logging-level=%s ' % level
    )
    if module:
        nose_cmd += module

    ctx.run(nose_cmd)


@task
def build_docs(ctx):
    '''Build documentation using Sphinx.'''

    ctx.run('docs\\make html')
