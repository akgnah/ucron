#!/usr/bin/python
# -*- coding: utf-8 -*
import json
from six.moves.urllib import request


def add_task(path, args='', method='GET', host='http://127.0.0.1', port='8089'):
    req = request.Request('%s:%s/%s' % (host, port, 'add_task'))
    data = {'path': path, 'args': args, 'method': method}
    resp = request.urlopen(req, json.dumps(data).encode('utf8'))
    return resp
