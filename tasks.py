#!/usr/bin/env
# -*- coding: utf-8 -*-

# Standard library imports
from __future__ import absolute_import, print_function
import os

# Third party imports
import qtsass
from invoke import task


def joinpath(*parts):
    return os.path.join(*parts).replace('\\', '/')


@task
def build_resources(ctx):
    '''Build qresources'''

    def find_rcc_cmd():
        from Qt import _QtGui
        qtdir = os.path.dirname(_QtGui.__file__)
        potential_names = [
            'pyrcc4', 'pyrcc4.exe', 'pyrcc4.bat',  # PyQt4
            'pyrcc5', 'pyrcc5.exe', 'pyrcc5.bat',  # PyQt5
            'pyside-rcc', 'pyside-rcc.exe',  # PySide
            'pyside2-rcc', 'pyside2-rcc.exe',  # PySide2
        ]
        for name in potential_names:
            potential_path = joinpath(qtdir, name)
            if os.path.isfile(potential_path):
                return potential_path

        raise OSError('Could not find Qt rcc...is PySide2 available?')

    def generate_qrc(**resources):
        '''Generate qrc file'''

        qrc_tmpl = '''
        <!DOCTYPE RCC><RCC version="1.0">
        <qresource>
        {}
        </qresource>
        </RCC>
        '''
        qrc_file_tmpl = '    <file alias="{alias}">{path}</file>'

        lines = []

        for key, (path, exts) in resources.items():
            for file in os.listdir(path):
                name, ext = os.path.splitext(file)
                if ext not in exts:
                    continue

                line = qrc_file_tmpl.format(
                    alias=joinpath(key, file),
                    path=joinpath(path, file),
                )
                lines.append(line)

        return qrc_tmpl.format('\n'.join(lines))

    def patch_qrcpy(resource):
        '''Patch qrcpy file'''

        import Qt

        with open(resource, 'r') as f:
            contents = f.read()

        # Patch imports
        contents = contents.replace(Qt.__binding__, 'Qt')

        with open(resource, 'w') as f:
            f.write(contents)

    # Build css
    qtsass.compile_dirname(
        joinpath('construct', 'resources', 'scss'),
        joinpath('construct', 'resources', 'styles'),
    )

    qrc_src = joinpath('resources.qrc')
    qrc_bld = joinpath('construct', 'resources', '_resources.py')
    qrc_cmd = (find_rcc_cmd() + ' %s -o %s') % (qrc_src, qrc_bld)

    # Write qrc file
    text = generate_qrc(
        icons=(joinpath('construct', 'resources', 'icons'), ['.png']),
        brand=(joinpath('construct', 'resources', 'brand'), ['.png']),
        fonts=(joinpath('construct', 'resources', 'fonts'), ['.ttf']),
        styles=(joinpath('construct', 'resources', 'styles'), ['.css']),
    )
    with open(qrc_src, 'w') as f:
        f.write(text)

    # Generate python qresource and patch imports to use Qt.py
    ctx.run(qrc_cmd)
    patch_qrcpy(qrc_bld)

    # Remove source resources.qrc
    os.remove(qrc_src)


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
