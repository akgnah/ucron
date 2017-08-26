#!/usr/bin/python
# -*- coding: utf-8 -*
from __future__ import absolute_import

import json

from ucron.utils import request, urlencode, URLError


def add_task(path, args={}, method='GET', queue='default_seq', port='8089', host='127.0.0.1'):
    if not isinstance(args, dict):
        raise Exception('TypeError: argument args: expected a dict')
    req = request.Request('http://%s:%s/add_task' % (host, port))
    data = {'path': path, 'args': args, 'method': method, 'queue': queue}
    try:
        resp = request.urlopen(req, json.dumps(data).encode('utf8'))
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
