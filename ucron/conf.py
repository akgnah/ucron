#!/usr/bin/python
# -*- coding: utf-8 -*
from __future__ import absolute_import

import os


def save(args):
    for key in ['cron', 'dbn', 'log']:
        value = getattr(args, key)
        if value and value != ':memory:':
            setattr(args, key, os.path.join(os.getcwd(), value))
    setattr(args, 'local', 'http://127.0.0.1:%s' % args.port)
    globals().update(args.__dict__)
