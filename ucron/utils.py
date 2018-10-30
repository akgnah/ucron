#!/usr/bin/python
# -*- coding: utf-8 -*
from __future__ import absolute_import

import sys
from numbers import Number
try:
    from ujson import dumps, loads
except ImportError:
    from json import dumps, loads

py3k = sys.version_info.major > 2

# Lots of stdlib and builtin differences.
if py3k:
    from urllib import request
    from urllib.parse import urlencode
    from urllib.parse import parse_qsl
    from urllib.error import URLError
    from queue import Queue
    unicode = str
else:  # 2.x
    import urllib2 as request
    from urllib import urlencode
    from urlparse import parse_qsl
    from urllib2 import URLError
    from Queue import Queue
    unicode = unicode


# Some helpers for string/bytes handling
def to_bytes(s, encoding='utf8'):
    if isinstance(s, unicode):
        return s.encode(encoding)
    if isinstance(s, (bool, Number)):
        return str(s).encode(encoding)
    return bytes('' if s is None else s)


def to_unicode(s, encoding='utf8', errors='strict'):
    if isinstance(s, bytes):
        return s.decode(encoding, errors)
    return unicode('' if s is None else s)


to_string = to_unicode if py3k else to_bytes


def dict_encode(d, encoding='utf8'):
    return dict({(to_bytes(k, encoding), to_bytes(v, encoding))
                 for k, v in d.items()})


# Copy from https://github.com/webpy/webpy/blob/master/web/utils.py
class IterBetter:
    """
    Returns an object that can be used as an iterator 
    but can also be used via __getitem__ (although it 
    cannot go backwards -- that is, you cannot request 
    `iterbetter[0]` after requesting `iterbetter[1]`).
    
        >>> import itertools
        >>> c = iterbetter(itertools.count())
        >>> c[1]
        1
        >>> c[5]
        5
        >>> c[3]
        Traceback (most recent call last):
            ...
        IndexError: already passed 3
    It is also possible to get the first value of the iterator or None.
        >>> c = iterbetter(iter([3, 4, 5]))
        >>> print(c.first())
        3
        >>> c = iterbetter(iter([]))
        >>> print(c.first())
        None
    For boolean test, IterBetter peeps at first value in the itertor without effecting the iteration.
        >>> c = iterbetter(iter(range(5)))
        >>> bool(c)
        True
        >>> list(c)
        [0, 1, 2, 3, 4]
        >>> c = iterbetter(iter([]))
        >>> bool(c)
        False
        >>> list(c)
        []
    """
    def __init__(self, iterator): 
        self.i, self.c = iterator, 0

    def first(self, default=None):
        """Returns the first element of the iterator or None when there are no
        elements.
        If the optional argument default is specified, that is returned instead
        of None when there are no elements.
        """
        try:
            return next(iter(self))
        except StopIteration:
            return default

    def list(self):
        return list(self)

    def __iter__(self): 
        if hasattr(self, "_head"):
            yield self._head

        while 1:
            try:
                yield next(self.i)
            except StopIteration:
                return
            self.c += 1

    def __getitem__(self, i):
        # todo: slices
        if i < self.c: 
            raise IndexError("already passed " + str(i))
        try:
            while i > self.c: 
                next(self.i)
                self.c += 1
            # now self.c == i
            self.c += 1
            return next(self.i)
        except StopIteration: 
            raise IndexError(str(i))
            
    def __nonzero__(self):
        if hasattr(self, "__len__"):
            return self.__len__() != 0
        elif hasattr(self, "_head"):
            return True
        else:
            try:
                self._head = next(self.i)
            except StopIteration:
                return False
            else:
                return True

    __bool__ = __nonzero__


iterbetter = IterBetter


__all__ = ['py3k', 'request', 'urlencode', 'parse_qsl', 'URLError', 'Queue', 'unicode',
           'to_bytes', 'to_unicode', 'to_string', 'dict_encode', 'iterbetter']
