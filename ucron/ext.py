#!/usr/bin/python
# -*- coding: utf-8 -*
from __future__ import absolute_import

from ucron.utils import request, urlencode, URLError, dumps, unicode


def add_task(path, args='', method='GET', name='default_seq', port='8089', host='127.0.0.1', json=None):
    if args != '' and not isinstance(args, dict):
        raise Exception('TypeError: Argument args should be dict.')
    headers = {'Content-Type': 'application/json'}
    req = request.Request('http://%s:%s/add_task' % (host, port), headers=headers)
    data = {'path': path, 'args': args, 'method': method, 'name': name, 'json': json}
    try:
        resp = request.urlopen(req, dumps(data).encode('utf8'))
        return resp.read().decode()
    except(URLError):
        raise Exception('Connection refused. Please check host or port.')


def add_queue(name, mode='seq', port='8089', host='127.0.0.1'):
    data = {'name': name, 'mode': mode, 'opt': 'add', 'cli': 'true'}
    url = 'http://%s:%s/taskq?%s' % (host, port, urlencode(data))
    try:
        resp = request.urlopen(url)
        return resp.read().decode()
    except(URLError):
        raise Exception('Connection refused. Please check host or port.')


def del_queue(name, port='8089', host='127.0.0.1'):
    data = {'name': name, 'opt': 'del', 'cli': 'true'}
    url = 'http://%s:%s/taskq?%s' % (host, port, urlencode(data))
    try:
        resp = request.urlopen(url)
        return resp.read().decode()
    except(URLError):
        raise Exception('Connection refused. Please check host or port.')
