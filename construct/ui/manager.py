# -*- coding: utf-8 -*-


# Local imports
from .resources import UIResources
from .theme import UITheme


class UIManager(object):
    """Manages UI resources, themes, and dialogs."""

    def __init__(self, api):
        self.api = api
        self.resources = UIResources(self.api.path)
        self.theme = UITheme(self.resources)

    def load(self):
        pass

    def unload(self):
        pass
