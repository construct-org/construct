# -*- coding: utf-8 -*-
"""Creates uis with live-linked stylesheets."""

# Standard library imports
from __future__ import absolute_import
import argparse
import inspect
import sys

# Third party imports
from qtsass.watchers import Watcher

# Local imports
import construct


def dialogs():
    '''Show a series of dialogs.'''

    short_notification('alert')
    short_notification('error')
    short_notification('success')
    short_notification('info')
    notification('alert')
    notification('error')
    notification('success')
    notification('info')
    ask()


def short_notification(type):
    '''Show a short notification.'''

    api = construct.API()
    method = getattr(api, type)
    method('This is a short %s message.' % type)


def notification(type):
    '''Show a notification.'''

    api = construct.API()
    method = getattr(api, type)
    method(
        'This is a much longer %s message.'
        ' There is a full header with an icon, title, and close button.'
        ' This dialog can include additional widgets if necessary.' % type
    )


def ask(title=None, message=None, icon=None):
    '''Show an ask dialog.'''

    api = construct.API()
    api.ask(
        title=title or 'Question',
        message=message or 'This is a question. Do you choose yes or no?',
        icon=icon,
    )


def flowlayout():
    '''Show a widget that uses a FlowLayout'''

    from Qt import QtWidgets, QtCore
    from construct.ui.layouts import FlowLayout
    from construct.ui.widgets import ToolButton
    from construct.ui.eventloop import get_event_loop

    api = construct.API()

    loop = get_event_loop()

    w = QtWidgets.QWidget()
    w.setWindowFlags(w.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    w.setObjectName('surface')
    api.ui.theme.apply(w)

    l = FlowLayout()
    for icon in api.ui.resources.font_charmaps['construct'].keys():
        b = ToolButton(icon, icon=icon, icon_size=(24, 24), parent=w)
        l.addWidget(b)
    w.setLayout(l)

    w.show()

    loop.start()


def _setup_autoreload_stylesheets():
    api = construct.API()
    watcher = Watcher(
        watch_dir=str(api.ui.resources.path / 'styles'),
        compiler=api.ui.theme.refresh_stylesheet,
    )
    watcher.start()


def _add_func_args(parser, func):
    spec = inspect.getargspec(func)
    for arg in spec.args:
        parser.add_argument('-' + arg)


def _main():
    parser = argparse.ArgumentParser(
        prog='UI Tasks',
        usage='ui_tasks <task> [options]',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument('task', action='store')
    parser.epilog = 'Tasks:\n'

    tasks = {}
    funcs = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
    for name, func in sorted(funcs):

        if name.startswith('_'):
            continue

        task_parser = argparse.ArgumentParser(
            prog=name,
            usage='ui_tasks {} [options]'.format(name),
            description=func.__doc__,
            formatter_class=argparse.RawTextHelpFormatter,
        )
        _add_func_args(task_parser, func)
        tasks[name] = {'func': func, 'parser': task_parser}

        parser.epilog += '    {} - {}\n'.format(name, func.__doc__)

    args, task_args = parser.parse_known_args()
    if args.task not in tasks:
        print('No task named ' + args.task)
        print(parser.epliog)
        sys.exit(1)

    task = tasks[args.task]
    args = task['parser'].parse_args(task_args)

    _setup_autoreload_stylesheets()
    task['func'](**args.__dict__)


if __name__ == '__main__':
    _main()
