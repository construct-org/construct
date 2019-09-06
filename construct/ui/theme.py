# -*- coding: utf-8 -*-

# Standard library imports
from functools import wraps

# Third party imports
import qtsass

# Local imports
from ..compat import Path, basestring
from ..types import WeakSet
from . import resources


def ensure_loaded(method):
    '''A decorator that ensures an objects resources are loaded before
    executing.
    '''

    @wraps(method)
    def call_method(self, *args, **kwargs):
        self.load()
        resources = getattr(self, 'resources', None)
        if resources:
            resources.load()
        return method(self, *args, **kwargs)
    return call_method


def clamp(value, lower, upper):
    '''Clamp a value between lower and upper bounds

    Arguments:
        value (int or float): the number to clamp
        lower (int or float): the lower bound
        upper (int or float): the upper bound
    '''
    return max(lower, min(value, upper))


def rgb_to_hex(r, g, b):
    '''Convert r, g, b ints to a hex string.

    Arguments:
        r (int): Red value between 0 and 255
        g (int): Green value between 0 and 255
        b (int): Blue value between 0 and 255
    Returns:
        Hex string in "#RRGGBB" format
    '''

    return '#{:02x}{:02x}{:02x}'.format(
        clamp(r, 0, 255),
        clamp(g, 0, 255),
        clamp(b, 0, 255),
    )


def hex_to_rgb(code):
    '''Convert a hex code to rgb tuple.

    Arguments:
        r (int): Red value between 0 and 255
        g (int): Green value between 0 and 255
        b (int): Blue value between 0 and 255
    Returns:
        Tuple of ints - (r, g, b)
    '''

    return tuple([ord(i) for i in code[1:].decode('hex')])


class Theme(object):
    """Represents the UI Font and Color theme.

    Colors are based on the Material design color system. All attributes can
    be passed to the constructor. Colors can be passed as either Hex strings
    or RGB tuples.

    Attributes:
        name (str): name of the theme
        font_stack (str): Comma separated list of font-families
        font_size (str): Font point size
        font_weight (str): Font weight
        primary (color): Used for accents and emphasis
        primary_variant (color): Variant of primary color
        on_primary (color): Color of type and icons on primary
        alert (color): Indicates warnings and alerts
        error (color): Indicates error
        success (color): Indicates success
        info (color): Indicates info
        on_secondary (color): Color of type and icons on secondary colors
        background (color): Used for underlying background fill
        on_background (color): Color of type and icons on background
        surface (color): Background color of most cards and widgets
        on_surface (color): Color of type on surface

    Arguments:
        resources (Resource): Used to lookup icons, pixmaps, and images
    """

    defaults = dict(
        name='default',
        font_stack='Roboto',
        font_size='12pt',
        font_weight='400',
        primary='#F63659',
        primary_variant='#D72F57',
        on_primary='#FFFFFF',
        alert='#FACE49',
        error='#F15555',
        success='#7EDC9E',
        info='#87CDEB',
        on_secondary='#000000',
        background='#F2F2F2',
        on_background='#000000',
        surface='#FFFFFF',
        on_surface='#000000',
    )
    color_options = [
        'primary',
        'primary_variant',
        'on_primary',
        'alert',
        'error',
        'success',
        'info',
        'on_secondary',
        'background',
        'on_background',
        'surface',
        'on_surface',
    ]
    variables = list(defaults.keys())

    def __init__(self, resources, **options):
        self.__dict__.update(**self.defaults)
        self.__dict__.update(**options)
        self.resources = resources
        self.stylesheet = self.compile_stylesheet()
        self._widgets = WeakSet()
        self._signals = None
        self._loaded = False

    def load(self):
        if self._loaded:
            return

        from Qt.QtCore import QObject, Signal

        class ThemeSignals(QObject):
            changed = Signal(str)

        self._signals = ThemeSignals()
        self._signals.changed.connect(self.on_theme_changed)

        self._loaded = True

    @ensure_loaded
    def apply(self, widget):
        widget.setStyleSheet(self.stylesheet)
        self._widgets.add(widget)

    def set_resources(self, resources):
        self.resources = resources

    def refresh_stylesheet(self):
        self.stylesheet = self.compile_stylesheet()
        if self._signals:
            self._signals.changed.emit(self.stylesheet)
        else:
            self.on_theme_changed()

    def on_theme_changed(self):
        for widget in self._widgets:
            widget.setStyleSheet(self.stylesheet)

    def compile_stylesheet(self):
        """Compile a stylesheet for this theme."""

        sass = ''
        var_tmpl = '${}: {};\n'
        rgb_tmpl = '${}: rgb({}, {}, {});\n'
        rgba_tmpl = '${}: rgba({}, {}, {}, {});\n'
        for var in self.variables:
            value = getattr(self, var)
            if isinstance(value, basestring):
                sass += var_tmpl.format(var, value)
            elif isinstance(value, (tuple, list)):
                if len(value) == 3:
                    sass += rgb_tmpl.format(var, *value)
                elif len(value) == 4:
                    sass += rgba_tmpl.format(var, *value)
                else:
                    raise ValueError(
                        '%s: Expected a length or 3 or 4 got %s.' %
                        (var, len(value))
                    )
            else:
                raise TypeError(
                    '%s: Expected (str, tuple) got %s' %
                    (var, type(value))
                )

        sass += "@import 'theme'"

        return qtsass.compile(
            sass,
            include_paths=[
                str(self.resources.path / 'styles'),
            ],
        )

    @ensure_loaded
    def pixmap(self, resource, size=None, family=None):
        '''Get a pixmap for a resource.

        Arguments:
            resource (str):  Path relative to Construct PATH or font icon name
            size (QSize): Size of pixmap to return
            family (str): Font family for font icon character (optional)
        '''

        from Qt.QtGui import QPixmap, QIcon

        path = self.resources.get(resource, None)
        if path:
            if path.suffix == '.svg':
                return QIcon(str(path)).pixmap(size)
            elif path.suffix in self.resources.image_extensions:
                return QPixmap(str(path), size)
            else:
                raise TypeError("Can't create a pixmap for %s" % str(path))

        char = self.resources.get_char(resource, family)
        return FontIcon(char, family).pixmap(size)

    @ensure_loaded
    def icon(self, resource, family=None, parent=None):
        '''Get a QIcon for a resource.

        Arguments:
            resource (str): Path relative to Construct PATH or font icon name
            family (str): Font family for font icon character (optional)
            parent (QWidget): Parent QWidget of QIcon - used for coloring
        '''

        from Qt.QtGui import QIcon
        from .icons import SvgIcon, FontIcon

        path = self.resources.get(resource, None)
        if path:
            if path.suffix == '.svg':
                return SvgIcon(str(path), parent)
            elif path.suffix in self.resources.image_extensions:
                return QIcon(str(path))
            else:
                raise TypeError("Can't create a pixmap for %s" % str(path))

        char = self.resources.get_char(resource, family)
        return FontIcon(char, family, parent)


# Theme singleton
theme = Theme(resources.Resources([]))
