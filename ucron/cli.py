#!/usr/bin/python
# -*- coding: utf-8 -*
from __future__ import absolute_import

import argparse

from ucron import conf
from ucron.utils import request, urlencode, URLError, loads


class Check_Quiet(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        argparse.Action.__init__(self, option_strings, dest, nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if values.lower() == 'false':
            setattr(namespace, self.dest, False)
        else:
            setattr(namespace, self.dest, True)


class Check_Reload(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        argparse.Action.__init__(self, option_strings, dest, nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if values.lower() == 'false':
            setattr(namespace, self.dest, False)
        else:
            setattr(namespace, self.dest, True)


class Check_Tab(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        argparse.Action.__init__(self, option_strings, dest, nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if len(values.split(' ')) != 5:
            print('The crontab rule is invalid.')
            print("Example:\n  --tab '0 5 * * *'")
            print('Note that argument included in single quotes.')
            exit(1)
        else:
            setattr(namespace, self.dest, values)


class Add_Queue(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        argparse.Action.__init__(self, option_strings, dest, nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        port, name, mode = values
        if mode not in ['con', 'seq']:
            print('The mode must be either con or seq.')
            exit(1)
        if not name.strip():
            print('The name is invalid.')
            exit(1)
        data = {'name': name, 'mode': mode, 'opt': 'add', 'cli': 'true'}
        url = 'http://127.0.0.1:%s/taskq?%s' % (port, urlencode(data))
        try:
            resp = request.urlopen(url)
            print(resp.read().decode())
        except(URLError):
            print('Connection refused. Please check port.')
        exit(0)


class Del_Queue(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        argparse.Action.__init__(self, option_strings, dest, nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        port, name = values
        data = {'name': name, 'opt': 'del', 'cli': 'true'}
        url = 'http://127.0.0.1:%s/taskq?%s' % (port, urlencode(data))
        try:
            resp = request.urlopen(url)
            print(resp.read().decode())
        except(URLError):
            print('Connection refused. Please check port.')
        exit(0)


class Cls_Queue(argparse.Action):  # Clear
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        argparse.Action.__init__(self, option_strings, dest, nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        port, name = values
        data = {'name': name, 'opt': 'cls', 'cli': 'true'}
        url = 'http://127.0.0.1:%s/taskq?%s' % (port, urlencode(data))
        try:
            resp = request.urlopen(url)
            print(resp.read().decode())
        except(URLError):
            print('Connection refused. Please check port.')
        exit(0)


class List_Queue(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        argparse.Action.__init__(self, option_strings, dest, nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        url = 'http://127.0.0.1:%s/taskq?opt=list' % values  # port
        try:
            resp = request.urlopen(url)
            for item in loads(resp.read().decode()):
                print('%-16s%4s%4s' % tuple(item))
        except(URLError):
            print('Connection refused. Please check port.')
        exit(0)


def parse_args():
    parser = argparse.ArgumentParser(description='uCron - Micro(toy) Crontab and Task Queue', prog='python -m ucron',
                                     epilog='See https://github.com/akgnah/ucron/ for more details.')

    parser.add_argument('--host', default='127.0.0.1', metavar='host',
                        help='specify host, default is 127.0.0.1')
    parser.add_argument('--port', default='8089', metavar='port',
                        help='specify port number, default is 8089')
    parser.add_argument('--cron', metavar='file',
                        help='specify crontab file, required by crontab')
    parser.add_argument('--dbn', default=':memory:', metavar='file',
                        help='specify db file or :memory:, default is :memory:')
    parser.add_argument('--log', default='ucron.log', metavar='file',
                        help='specify log file, default is ucron.log in pwd')
    parser.add_argument('--max', default=10240, type=int, metavar='number',
                        help='specify maximum rows for log, default is 10240')
    parser.add_argument('--utc', default=8, type=int, metavar='tzinfo',
                        help='specify tzinfo for UTC, default is +8')
    parser.add_argument('--quiet', default=False, metavar='true/false', action=Check_Quiet,
                        help='specify value for bottle --quiet, default is False')
    parser.add_argument('--reload', default=False, metavar='true/false', action=Check_Reload,
                        help='specify value for reload ucron.tab, default is False')
    parser.add_argument('--tab', default='0 5 * * *', metavar="'x x x x x'", action=Check_Tab,
                        help="specify cron for clean log, default is '0 5 * * *'")
    parser.add_argument('--add', nargs=3, metavar=('port', 'name', 'mode'), action=Add_Queue,
                        help='specify port, name and mode to add a queue and exit')
    parser.add_argument('--cls', nargs=2, metavar=('port', 'name'), action=Cls_Queue,
                        help='specify port and name to clear a queue and exit')
    parser.add_argument('--del', nargs=2, metavar=('port', 'name'), action=Del_Queue,
                        help='specify port and name to delete a queue and exit')
    parser.add_argument('--list', metavar='port', action=List_Queue,
                        help='specify port to list all queues and exit')

    args = parser.parse_args()
    conf.save(args)  # save args to conf.py
