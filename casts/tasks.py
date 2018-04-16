#!/bin/bash
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import argparse
import os
import sys


class record(object):
    '''Uses spielbash and asciinema to record cli demos stored in scripts/.
    '''

    def __call__(self, args):
        build_cmd = (
            'docker build -q -f record.Dockerfile -t record_casts .'
        )
        os.system(build_cmd)
        cmd = (
            'docker run --rm -it -v %cd%:/data record_casts '
            '--width {width} '
            '--height {height} '
            '--speed {speed} '
            '--readtime {readtime}'
        ).format(**args.__dict__)
        os.system(cmd)

    def parser(self):
        parser = argparse.ArgumentParser(
            'tasks record',
            add_help=False,
            description=self.__doc__
        )
        parser.add_argument(
            '-w', '--width',
            type=int,
            help='Console width (default: 120)',
            default=120,
            required=False
        )
        parser.add_argument(
            '-h', '--height',
            type=int,
            help='Console height (default: 40)',
            default=40,
            required=False
        )
        parser.add_argument(
            '-s', '--speed',
            type=float,
            help='Typing Speed (default: 0.1)',
            default=0.1,
            required=False
        )
        parser.add_argument(
            '-r', '--readtime',
            type=float,
            help='Time to wait between scenes (default: 1.0)',
            default=1.0,
            required=False
        )
        parser.add_argument(
            '--help',
            help='show this help message and exit',
            action='store_true'
        )
        return parser


class convert(object):
    '''Uses asciicast2gif to convert all cast files in casts/ to gif files.
    Run after record task. Accepts the same arguments as asciicast2gif.'''

    def __call__(self, args):
        build_cmd = (
            'docker build -q -f convert.Dockerfile -t convert_casts .'
        )
        os.system(build_cmd)
        cmd = (
            'docker run --rm -it -v %cd%:/data convert_casts '
            '-w {width} '
            '-h {height} '
            '-s {speed} '
            '-t {theme} '
            '-S {scale}'
        ).format(**args.__dict__)
        os.system(cmd)

    def parser(self):
        parser = argparse.ArgumentParser(
            'tasks convert',
            add_help=False,
            description=self.__doc__
        )
        parser.add_argument(
            '-w', '--width',
            type=int,
            help='clip terminal to specified number of columns (width: 120)',
            default=120,
            required=False
        )
        parser.add_argument(
            '-h', '--height',
            type=int,
            help='clip terminal to specified number of rows (height: 40)',
            default=40,
            required=False
        )
        parser.add_argument(
            '-t', '--theme',
            help='color theme, one of: asciinema, tango, solarized-dark, solarized-light, monokai (default: asciinema)',
            default='asciinema',
            required=False
        )
        parser.add_argument(
            '-S', '--scale',
            help='image scale / pixel density (default: 2)',
            type=int,
            default=2,
            required=False
        )
        parser.add_argument(
            '-s', '--speed',
            type=int,
            help='animation speed (default: 1)',
            default=1,
            required=False
        )
        parser.add_argument(
            '--help',
            help='show this help message and exit',
            action='store_true'
        )
        return parser


class upload(object):
    '''Uploads all casts in casts/ to asciinema.org'''

    def __call__(self, args):
        cmd = (
            'docker run --rm -it '
            '-v %cd%/casts:/root/casts -v %cd%/.config:/root/.config '
            'asciinema/asciinema '
            'asciinema upload casts/{file}'
        )
        for f in os.listdir('casts'):
            if f.endswith('.cast'):
                os.system(cmd.format(file=f))

    def parser(self):
        parser = argparse.ArgumentParser(
            'tasks upload',
            description=self.__doc__
        )
        return parser


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        'command',
        choices=['record', 'convert', 'upload']
    )
    args, extra_args = parser.parse_known_args()

    cmd = getattr(sys.modules[__name__], args.command)()
    cmd_parser = cmd.parser()
    args = cmd_parser.parse_args(extra_args)
    if 'help' in args and args.help:
        cmd_parser.print_help()
        sys.exit(1)
    cmd(args)


if __name__ == '__main__':
    main()
