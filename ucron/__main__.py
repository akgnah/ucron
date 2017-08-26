#!/usr/bin/python
# -*- coding: utf-8 -*
from __future__ import absolute_import

from ucron import db, cli, server, worker

if __name__ == '__main__':
    cli.parse_args()
    db.initalize()  # initalize database
    worker.start()  # start worker threads
    server.start()  # start bottle server
