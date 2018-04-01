# -*- coding: utf-8 -*-
'''
Terminal UI Framework
=====================
'''

from __future__ import absolute_import, print_function
import re
import sys
import colorama
from backports.shutil_get_terminal_size import get_terminal_size
import win_unicode_console


TAB_WIDTH = 4
orig_stdout = None
orig_stderr = None
_console = None


def get_console():
    return _console


def set_console(console):
    global _console
    _console = console


def clean_text(text):
    from functools import reduce
    substitutions = [('\n', ''), ('\r', ''), ('\t', ' ' * TAB_WIDTH)]
    return reduce(lambda s, sre: str.replace(s, *sre), substitutions, text)


class AnsiToken(str):

    def __new__(cls, value, pattern):
        inst = str.__new__(cls, value)
        inst.pattern = re.compile(pattern)
        return inst

    def __call__(self, *args):
        return self.format(*args)

    def search(self, text):
        return self.pattern.search(text)


class Ansi(object):
    '''Ansi cursor movement parsing'''

    pattern = re.compile('\\x1b\[([\d+];[\d+]H|[\d+]?[ABCDK]|\?25[lh])')

    # Ansi cursor movement tokens
    move = AnsiToken('\x1b[{};{}H', '\\x1b\[(\d+)\;(\d+)H')
    move_up = AnsiToken('\x1b[{}A', '\\x1b\[(\d+)?A')
    move_down = AnsiToken('\x1b[{}B', '\\x1b\[(\d+)?B')
    move_right = AnsiToken('\x1b[{}C', '\\x1b\[(\d+)?C')
    move_left = AnsiToken('\x1b[{}D', '\\x1b\[(\d+)?D')
    clear = AnsiToken('\x1b[K', '\\x1b\[K')
    hide_cursor = AnsiToken('\x1b[?25l', '\\x1b\[?25l')
    show_cursor = AnsiToken('\x1b[?25h', '\\x1b\[?25h')
    home = AnsiToken('\r', '\\r')
    tokens = [t for t in locals().items() if isinstance(t[1], AnsiToken)]

    @classmethod
    def get_token_args(cls, text):
        '''Parses text returning method name and arguments.

        Examples:
            >>> Ansi.get_token_args('\x1b[10;2H')
            ('move', (10, 2))
            >>> Ansi.get_token_args('\x1b[4A')
            ('move_up', (4,))
        '''

        for name, token in cls.tokens:
            if token == '\r':
                continue
            match = token.search(text)
            if match:
                args = [int(g) for g in match.groups()]
                return name, args

    @classmethod
    def match(cls, text):
        '''Returns True if the text matches ANY token in Ansi.tokens'''

        return cls.pattern.match(text)


class Cursor(object):
    '''Provides terminal console cursor interaction'''

    def __init__(self, console):
        self.console = console
        self.dx = 0
        self.dy = 0

    def show(self):
        self.console.stream.write(Ansi.show_cursor)

    def hide(self):
        self.console.stream.write(Ansi.hide_cursor)

    def home(self):
        self.console.stream.write(Ansi.home)
        self.dx = 0

    def clear(self):
        self.console.stream.write(Ansi.clear)

    def reset(self):
        self.move(-self.dx, -self.dy)

    def move_up(self, y=1):
        self.console.stream.write(Ansi.move_up(y))
        self.dy += y

    def move_down(self, y=1):
        self.console.stream.write(Ansi.move_down(y))
        self.dy -= y

    def move_right(self, x=1):
        self.console.stream.write(Ansi.move_right(x))
        self.dx += min(self.console.width, self.dx + x)

    def move_left(self, x=1):
        self.console.stream.write(Ansi.move_left(x))
        self.dx = max(0, self.dx - x)

    def move(self, x, y):
        if x > 0:
            self.move_right(x)
        else:
            self.move_left(abs(x))
        if y > 0:
            self.move_up(y)
        else:
            self.move_down(abs(y))


class ConsoleStream(object):
    '''Parse and redirect stream.write to console.write.

    This stream wrapper parses text written to a stream and splits it line by
    line and sends it to Console. This allows Console to maintain a buffered
    list of Line widgets.
    '''

    def __init__(self, stream, console):
        self.stream = stream
        self.console = console

    def __getattr__(self, attr):
        return self.stream.__getattr__(attr)

    def write(self, value):
        buffer = list(value)
        indent = 0
        string = ''
        while buffer:
            string += buffer.pop(0)
            indent = len(string) - len(string.lstrip())
            if len(string) == self.console.width - 2:
                self.console.write(string + '-\n')
                string = ' ' * indent
            elif string[-1] in ['\r', '\n']:
                self.console.write(string)
                string = ''
            elif Ansi.match(string):
                name, args = Ansi.get_token_args(string)
                cursor_meth = getattr(self.console.cursor, name)
                cursor_meth(*args)
                string = ''

        if string:
            if Ansi.match(string):
                name, args = Ansi.get_token_args(string)
                cursor_meth = getattr(self.console.cursor, name)
                cursor_meth(*args)
            else:
                self.console.write(''.join(string))


class Console(object):
    '''Wraps stdout and stderr and wraps every line you write as a
    Line widget. Making it easy to modify previously printed lines. You
    can also subclass Line and manually add your own widgets to the output
    stream.
    '''

    def __init__(self):

        self.lines = []
        self.wrapper = None
        self.stream = None
        self.cursor = None

        # Terminal size used to split lines longer than console width
        t = get_terminal_size()
        self.width = t.columns
        self.height = t.lines  # TODO: cap self.lines at height - 2?

        # State from previous write used
        # to determine whether print modifies
        # a line or creates a new one
        self._n = True  # \n
        self._r = False  # \r
        self._e = False  # eol

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, type, value, traceback):
        self.deinit()

    def init(self):
        if self.stream:
            raise RuntimeError('Console already initialized.')

        global orig_stdout
        global orig_stderr
        win_unicode_console.enable()
        colorama.init()
        orig_stderr = sys.stderr
        orig_stdout = sys.stdout
        self.stream = sys.stdout
        self.wrapper = ConsoleStream(sys.stdout, self)
        sys.stdout = self.wrapper
        sys.stderr = self.wrapper
        self.cursor = Cursor(self)
        set_console(self)

    def deinit(self):
        if self.stream is None:
            raise RuntimeError('Console has not been initialized.')

        global orig_stdout
        global orig_stderr
        sys.stdout = orig_stdout
        sys.stderr = orig_stderr
        orig_stdout = None
        orig_stderr = None
        self.stream = None
        self.wrapper = None
        self.cursor = None
        colorama.deinit()
        win_unicode_console.disable()

    def set_state(self, n, r, e):
        self._n, self._r, self._e = n, r, e

    def add_widget(self, widget):
        '''Manually add a widget'''

        self.lines.insert(0, widget)
        self.set_state(True, False, False)
        self.stream.write(widget.text.rstrip('\n') + '\n')

    def insert_widget(self, index, widget):
        '''Manually insert a widget

        Examples:
            import stout, time
            with stout.Console() as con:
                print(100)
                w = stout.Spinner(con)
                con.insert_widget(1, w)  # insert spinner above '100'
                for i in range(20):
                    w.tick()
                    time.sleep(0.05)
        '''

        # Insert a blank line
        sys.__stdout__.write('\n')

        # Add widget to fill blank line
        self.lines.insert(index, widget)

        # Update all widgets
        for line in self.lines:
            line.update()

    def insert(self, index, text):
        '''Inserts text at the given index. Index starts at the bottom of your
        console, like this:

            3. a line
            2. another line
            1. yet another line
            0. last line
        '''

        # Store lines up to index and after index
        before_lines = self.lines[:index]
        after_lines = self.lines[index:]

        # Create new lines
        num_lines = len(self.lines)
        print(text)
        new_lines = self.lines[:len(self.lines) - num_lines]

        # Rebuild line ordering
        self.lines = before_lines + new_lines + after_lines

        # Update all lines
        for line in self.lines:
            line.update()

    def write(self, value):
        '''Line aware writing. Always returns a Line, either a new Line
        widget or the line that was written to.
        '''

        length = len(value)
        dy = self.cursor.dy
        dx = self.cursor.dx

        if dy > 0:  # Cursor is in another line

            line = self.lines[dy - 1]
            if dx:
                line._text = clean_text(
                    line._text[:dx] +
                    value +
                    line._text[dx + length:]
                )
            else:
                line._text = clean_text(value + line._text[length:])

        elif self._n:  # Cursor is on new line

            line = Line(value, self)
            self.lines.insert(0, line)

        elif self._r:  # Cursor is at the start of the last line

            line = self.lines[0]
            line._text = clean_text(value + line._text[length:])

        else:  # Cursor is somewhere on the last line

            line = self.lines[0]
            if dx:
                line._text = clean_text(
                    line._text[:dx] +
                    value +
                    line._text[dx + length:]
                )
            else:
                line._text = clean_text(value + line._text[length:])

        # Set state for next print
        if value.endswith('\n'):
            self.set_state(True, False, False)
            self.cursor.dx = 0
        elif value.endswith('\r'):
            self.set_state(False, True, False)
            self.cursor.dx = 0
        else:
            self.set_state(False, False, True)
            self.cursor.dx += length

        # Finally...print to stream
        self.stream.write(value)
        return line


class Line(object):
    '''Base widget class'''

    def __init__(self, text, console):
        self._text = clean_text(text)
        self.console = console

    def __repr__(self):
        return '{}(row={}, text={!r})'.format(
            self.__class__.__name__,
            self.row,
            self.text
        )

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = clean_text(value)
        self.update()

    @property
    def row(self):
        return self.console.lines.index(self)

    def update(self):
        row = self.row + 1
        if row > self.console.height - 2:  # Skip updates outside view
            return

        cursor = self.console.cursor
        cursor.move_up(row)
        cursor.home()
        cursor.clear()
        self.console.stream.write(self._text)
        cursor.move_down(row)
        cursor.home()


class Spinner(Line):

    chars = '|/-\\'
    interval = 0.2

    def __init__(self, console):
        self.chars = self.default
        self.index = 0
        super(Spinner, self).__init__(self.chars[0], console)

    def tick(self):
        self.index = (self.index + 1) % len(self.chars)
        self.text = self.chars[self.index]


class PingPong(Spinner):

    chars = [
        '.    ', '..   ', '...  ', ' ... ', '  ...', '   ..',
        '    .', '   ..', '  ...', ' ... ', '...  ', '..   '
    ]
