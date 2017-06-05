#!/usr/bin/python
# -*- coding: utf-8 -*
import os


def abspath(args):
    for key in ['cron', 'dbn', 'log']:
        value = args.__getattribute__(key)
        if value and value != ':memory:':
            args.__setattr__(key, os.path.join(os.getcwd(), value))


def checktab(args):
    if len(args.tab[0].split(' ')) != 5:
        print('the crontab rule is invalid.')
        print("example:\n  --tab '0 5 * * *'")
        print('note that arg included in single quotes')
        exit(1)
    args.tab = args.tab[0]
