# -*- coding: utf-8 -*-
"""Creates uis with live-linked stylesheets."""

# Standard library imports
from __future__ import absolute_import
import sys

# Third party imports
from qtsass.watchers import Watcher

# Local imports
import construct


def short_notification(type):
    api = construct.API()
    method = getattr(api, type)
    method('This is a short %s message.' % type)


def notification(type):
    api = construct.API()
    method = getattr(api, type)
    method(
        'This is a much longer %s message.'
        ' There is a full header with an icon, title, and close button.'
        ' This dialog can include additional widgets if necessary.' % type
    )


def ask():
    api = construct.API()
    api.ask(
        title='Question',
        message='This is question. Do you choose yes or no?',
        icon='question',
    )


def main():

    api = construct.API()

    watcher = Watcher(
        watch_dir=str(api.ui.resources.path / 'styles'),
        compiler=api.ui.theme.refresh_stylesheet,
    )
    watcher.start()

    short_notification('alert')
    short_notification('error')
    short_notification('success')
    short_notification('info')
    notification('alert')
    notification('error')
    notification('success')
    notification('info')
    ask()

if __name__ == '__main__':
    main()
