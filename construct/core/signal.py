# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from bisect import bisect_right
from collections import defaultdict
from fnmatch import fnmatch


DEFAULT_PRIORITY = 0


class SignalHub(object):
    '''Manages and sends signals by string identifier. Supports fuzzy signal
    subscriptions using fnmatch with *. So you could connect to "new.*" to
    subscribe to all signals that start with "new.".

    Examples:

        Basic subscription:

            >>> hub = SignalHub()
            >>> def subscriber():
            ...     return 'HI'
            ...
            >>> hub.connect('my.signal', subscriber)
            >>> hub.send('my.signal')
            ['HI']

        Fuzzy subscription:

            >>> hub = SignalHub()
            >>> @hub.route('foo.*')
            ... def foo_subscriber():
            ...     return 'FOO'
            ...
            >>> hub.send('foo.bar')
            ['FOO']
            >>> hub.send('foo.baz')
            ['FOO']

        Use a Signal alias:

            >>> hub = SignalHub()
            >>> my_signal = hub.signal('my.signal')
            >>> @my_signal.route()
            ... def my_subscriber():
            ...     return 'HI'
            ...
            >>> my_signal()
            ['HI']
    '''

    def __init__(self):
        self._subscribers = defaultdict(list)
        self._subscriber_keys = defaultdict(list)
        self._signals = {}

    def __call__(self, identifier, *args, **kwargs):
        '''Shorthand for :meth:`send`'''

        return self.send(identifier, *args, **kwargs)

    def signal(self, identifier):
        '''Get a :class:`Signal` alias that forwards all calls to this signal
        hub. Multiple calls to :meth:`signal` with the same identifier will
        return the same :class:`Signal` instance.
        '''

        if identifier not in self._signals:
            self._signals[identifier] = Signal(self, identifier)
        return self._signals.get(identifier)

    @property
    def signals(self):
        '''Return a dict containing all signal aliases.'''

        return dict(self._signals)

    def subscribers(self, identifier):
        '''Get all subscribers in order of priority for a specific signal.

        Arguments:
            identifier (str): Signal identifier

        Returns:
            list: subscribers
        '''

        subscribers = list(self._subscribers[identifier])
        subscriber_keys = list(self._subscriber_keys[identifier])

        for key in self._subscribers.keys():
            if key == identifier:
                continue

            # Incorporate fuzzy subscriptions
            if fnmatch(identifier, key):
                objs_priorities = zip(
                    self._subscribers[key],
                    self._subscriber_keys[key]
                )
                for obj, priority in objs_priorities:
                    index = bisect_right(subscriber_keys, priority)
                    subscribers.insert(index, obj)
                    subscriber_keys.insert(index, obj)

        return subscribers

    def connect(self, identifier, obj, priority=DEFAULT_PRIORITY):
        '''Connect an object to a signal. Subscribers are ordered by priority.
        New subscribers are inserted after existing subscribers with the same
        priority.

        Arguments:
            identifier (str): Signal identifier
            obj (callable): Object to connect to signal
            priority (int): priority of obj
        '''

        if obj in self._subscribers[identifier]:
            return

        if not self._subscribers[identifier]:
            self._subscribers[identifier].append(obj)
            self._subscriber_keys[identifier].append(priority)
            return

        index = bisect_right(self._subscriber_keys[identifier], priority)
        self._subscribers[identifier].insert(index, obj)
        self._subscriber_keys[identifier].insert(index, priority)

    def route(self, identifier, priority=DEFAULT_PRIORITY):
        '''Connect an obj to a signal via a decoration. Only works on functions
        and callable class instances at the moment.

        Arguments:
            identifier (str): Signal identifier
            priority (int): obj priority

        Examples:
            >>> hub = SignalHub()
            >>> @hub.route('my.signal')
            ... def subscriber():
            ...     pass
            ...
            >>> assert subscriber in hub.subscribers('my.signal')

        '''

        def connect_to_signal(obj):
            # TODO: Support class methods using a descriptor with a get method
            #       Remove "Only works on functions"
            self.connect(identifier, obj, priority)
            return obj

        return connect_to_signal

    def disconnect(self, identifier, obj):
        '''Disconnect obj from signal

        Arguments:
            identifier (str): signal to connect obj to
            obj (callable): callable obj to connect to signal
        '''

        if obj not in self._subscribers[identifier]:
            return

        index = self._subscribers[identifier].index(obj)
        self._subscribers[identifier].pop(index)
        self._subscriber_keys[identifier].pop(index)

    def clear(self, identifier=None):
        '''Disconnect subscribers from one or all signals

        Arguments:
            identifier (str): If passed clear subscribers for just this signal

        Examples:
            Clear all signals' subscribers:

                >>> hub = SignalHub()
                >>> hub.clear()

            Clear one signal's subscribers:

                >>> hub = SignalHub()
                >>> hub.clear('my.signal')
        '''
        if not identifier:
            self._subscribers = defaultdict(list)
            self._subscriber_keys = defaultdict(list)
            return

        self._subscribers[identifier][:] = []
        self._subscriber_keys[identifier][:] = []

    def send(self, identifier, *args, **kwargs):
        '''Send a signal. Calls each subscriber with args and kwargs.

        Arguments:
            identifier (str): signal to send out
            *args: args to send
            **kwargs: kwargs to send

        Returns:
            list: contains results in order
        '''

        results = []
        for subscriber in self.subscribers(identifier):
            results.append(subscriber(*args, **kwargs))
        return results

    def chain(self, identifier, *args, **kwargs):
        '''Chain a signals subscribers. The first subscriber will be passed
        args and kwargs. Then each successive subscriber will be passed the
        return value of the previous subscriber. Unlike :meth:`send` this
        returns one value.

        Arguments:
            identifier (str): signal to send
            *args: args to send
            **kwargs: kwargs to send

        Returns:
            Final value returned from last subscriber
        '''

        subscribers = self.subscribers(identifier)
        if not subscribers:
            return

        result = subscribers[0](*args, **kwargs)
        if not len(subscribers) > 1:
            return result

        for subscriber in subscribers[1:]:
            result = subscriber(result)
        return result


class Signal(object):
    '''Alias for a Signal identifier. Forwards all calls to a parent hub
    sending the aliases identifier with it. Users should not instance Signal
    themselves, instead they should get them from a hub using the
    :meth:`signal`:

        >>> hub = SignalHub()
        >>> hub.signal('my.signal') # doctest: +ELLIPSIS
        Signal(hub=..., identifier='my.signal')
    '''

    def __init__(self, hub, identifier):
        self.hub = hub
        self.identifier = identifier

    def __repr__(self):
        return (
            self.__class__.__name__ + '(hub={hub}, identifier={identifier})'
        ).format(hub=self.hub, identifier=repr(self.identifier))

    def __call__(self, *args, **kwargs):
        return self.hub(self.identifier, *args, **kwargs)

    def subscribers(self):
        return self.hub.subscribers(self.identifier)

    def connect(self, obj, priority):
        return self.hub.connect(self.identifier, obj, priority)

    def route(self, priority=DEFAULT_PRIORITY):
        return self.hub.route(self.identifier, priority)

    def disconnect(self, obj):
        return self.hub.disconnect(self.identifier, obj)

    def chain(self, *args, **kwargs):
        return self.hub.chain(self.identifier, *args, **kwargs)

    def send(self, *args, **kwargs):
        return self.hub.send(self.identifier, *args, **kwargs)

    def clear(self):
        return self.hub.clear(self.identifier)
