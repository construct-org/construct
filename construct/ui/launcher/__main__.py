# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Local imports
import construct
from construct.ui.eventloop import get_event_loop


def main():

    api = construct.API()
    launcher = api.ui.launcher()
    launcher.show()

    # Start Qt Event Loop
    get_event_loop().start()


if __name__ == '__main__':
    main()
