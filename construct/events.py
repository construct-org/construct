# -*- coding: utf-8 -*-
from operator import itemgetter
from collections import defaultdict, OrderedDict
import logging

from . import utils

_log = logging.getLogger(__name__)


class EventManager(object):
    '''The EventManager class maintains a priority list of handlers for events
    to be executed in order when an event is sent.

    Examples:
        >>> events = EventManager()
        >>> events.define('my_event', 'My simple event')
        >>> events.on('my_event', lambda msg: msg.upper())
        >>> events.send('my_event', 'Hello world!')
        ['HELLO WORLD!']
    '''
    # TODO: Needs a better docstring

    def __init__(self):
        self._events = OrderedDict()
        self._priority_map = defaultdict(set)
        self._handlers_map = defaultdict(dict)

    def load(self):
        self.define('before_setup', '(api): Sent before api initialization.')
        self.define('after_setup', '(api): Sent after api initialization.')
        self.define('before_close', '(api): Sent before api uninitialization.')
        self.define('after_close', '(api): Sent after api uninitialization.')

    def unload(self):
        self.undefine('before_setup')
        self.undefine('after_setup')
        self.undefine('before_close')
        self.undefine('after_close')

    def define(self, event, doc):
        '''Define a new event.

        Arguments:
            event (str): Name of the event
            doc (str): Documentation for event
        '''

        _log.debug('Defining event %s', event)
        self._events[event] = doc

    def undefine(self, event):
        '''Undefine an event

        Arguments:
            event (str): Name of the event
        '''

        _log.debug('Undefining event %s', event)
        self._events.pop(event, None)
        self.clear(event)

    def on(self, *args):
        '''Adds a handler to the specified event. Can be used as a decorator.

        Examples:
            >>> events = EventHandler()
            >>> events.on('greet', lambda person: print('Hello %s' % person))

            >>> @events.on('greet')
            ... def greeter(person):
            ...     print('Hello %s' % person)

        Arguments:
            event (str): Name of event
            handler (callable): Function to add as handler
            priority (int): Priority of handler

        Decorator Arguments:
            event (str): Name of event
            priority (int): Priority of handler
        '''

        argtypes = tuple([arg.__class__ for arg in args])

        if len(args) >= 2 and callable(args[1]):
            return self._on(*args)
        elif argtypes in [(str,), (str, int)]:
            return self._on_deco(*args)
        else:
            raise ValueError(
                'EventManager.on accepts the following signatures:\n'
                '    (str, callable, [int]) when used normally\n'
                ' OR (str, [int]) - when used as a decorator'
            )

    def _on(self, event, handler, priority=0):
        if handler in self._handlers_map[event]:
            return

        _log.debug('Added %s to event "%s"', handler, event)
        entry = (priority, handler)
        self._priority_map[event].add(entry)
        self._handlers_map[event][handler] = entry

    def _on_deco(self, event, priority=0):
        def _add_handler(handler):
            self._on(event, handler, priority)
            return handler
        return _add_handler

    def off(self, event, handler):
        '''Remove a handler from an event.

        Arguments:
            event (str): Name of the event
            handler (callable): Handler to remove
        '''

        if handler not in self._handlers_map[event]:
            return

        _log.debug('Removed %s from event "%s"', handler, event)
        entry = self._handlers_map[event].pop(handler)
        self._priority_map[event].discard(entry)

    def send(self, event, *args, **kwargs):
        '''Send an event. Executes all the event handlers and returns a
        list of the handlers results.

        Arguments:
            event (str): Name of event to send
            *args: Event arguments
            **kwargs: Event keyword arguments
        '''

        _log.debug('Sending event "%s"', event)
        results = []
        for handler in self.handlers(event):
            _log.debug('Calling %s', handler)
            results.append(handler(*args, **kwargs))
        return results

    def handlers(self, event):
        '''Get the handlers for an event in order of priority.'''

        sorted_handlers = sorted(self._priority_map[event], key=itemgetter(0))
        return [h[1] for h in sorted_handlers]

    def clear(self, event):
        '''Remove all handlers from an event.'''

        self._handlers_map.pop(event, None)
        self._priority_map.pop(event, None)

    def ls(self):
        return list(self._events.items())

    def show(self):
        print('\n'.join([' '.join(e) for e in self.ls()]))
