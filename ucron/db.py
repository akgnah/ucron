#!/usr/bin/python
# -*- coding: utf-8 -*
from __future__ import absolute_import

import sqlite3
from threading import Thread

from ucron import conf
from ucron.utils import Queue, iterbetter, dumps, loads


class DB(Thread):
    def __init__(self, dbn=':memory:'):
        Thread.__init__(self)
        self.dbn = dbn
        self.reqs = Queue()
        self.daemon = True
        self.start()

    def run(self):
        self.con = sqlite3.connect(self.dbn, check_same_thread=False)
        self.cur = self.con.cursor()

        while True:
            req, arg, res = self.reqs.get()
            if req == '--close--':
                break
            if req == '--commit--':
                self.con.commit()

            try:
                self.cur.execute(req, arg)
            except:
                self.con.rollback()

            if self.cur.description:
                for row in self.cur:
                    res.put(row)
            else:
                res.put(self.cur.rowcount)
            res.put('--no more--')

        self.con.close()

    def execute(self, req, arg=tuple()):
        res = Queue()
        self.reqs.put((req, arg, res))

    def query(self, req, arg=tuple()):
        res = Queue()
        self.reqs.put((req, arg, res))

        def iterwrapper():
            while True:
                row = res.get()
                if row == '--no more--':
                    break
                yield row

        return iterbetter(iterwrapper())

    def close(self):
        self.execute('--close--')

    def commit(self):
        self.execute('--commit--')


class Cron(DB):
    def __init__(self, dbn):
        DB.__init__(self, dbn)
        self.execute("create table cron (path blob, args text, \
        method blob, schedule text, id blob primary key)")
        self.commit()

    def push(self, _id, path, args, method, schedule):
        rowcount = self.query("insert into cron (id, path, args, method, schedule) \
        values (?, ?, ?, ?, ?)", (_id, path, args, method, dumps(schedule))).first()
        self.commit()
        return rowcount

    def fetchall(self):
        rows = []
        for row in self.query("select id, path, args, method, schedule from cron"):
            job = dict(zip(['id', 'path', 'args', 'method'], row[:-1]))
            job.update(loads(row[-1]))
            rows.append(job)
        return rows

    def empty(self):
        rowcount = self.query("delete from cron").first()
        self.commit()
        return rowcount


class Status(DB):
    def __init__(self, dbn):
        DB.__init__(self, dbn)  # status: [time] - status
        self.execute("create table status (id blob primary key, \
        schedule blob, status text default '[None] - None')")
        self.commit()

    def push(self, _id, schedule):
        rowcount = self.query("insert into status (id, schedule) \
        values (?, ?)", (_id, schedule)).first()
        self.commit()
        return rowcount

    def update(self, _id, status):
        rowcount = self.query("update status set status = ? \
        where id = ?", (status, _id)).first()
        self.commit()
        return rowcount

    def fetch(self, _id):
        return self.query("select schedule, status from status \
        where id = ?", (_id,)).first()


class TaskQ(DB):
    def __init__(self, dbn):
        DB.__init__(self, dbn)
        self.execute("create table taskq (name blob primary key, mode blob)")
        self.commit()

    def push(self, name, mode):  # mode: 'seq' or 'con'
        rowcount = self.query("insert into taskq (name, mode) \
        values (?, ?)", (name, mode)).first()
        self.commit()
        return rowcount

    def fetchall(self):
        return self.query("select name, mode from taskq")

    def delete(self, name):
        rowcount = self.query("delete from taskq where name = ?", (name,)).first()
        self.commit()
        return rowcount


class Task(DB):
    def __init__(self, dbn):
        DB.__init__(self, dbn)
        self.execute("create table task (path blob, args text, method blob, \
        name blob, json integer, id integer primary key)")
        self.commit()

    def push(self, path, args, method, name, json):
        rowcount = self.query("insert into task (path, args, method, name, json) \
        values (?, ?, ?, ?, ?)", (path, args, method, name, json)).first()
        self.commit()
        return rowcount

    def pop(self, name):
        row = self.query("select path, args, method, json, id from task \
        where name = ? order by id", (name,)).first()
        if row:
            self.query("delete from task where id = ?", (row[-1],))
            self.commit()
        return row

    def fetchall(self, name):
        rows = self.query("select path, args, method, json, id from task \
        where name = ? order by id", (name,))
        if rows:
            self.query("delete from task where name = ?", (name,))
            self.commit()
        return rows

    def delete(self, name):
        rowcount = self.query("delete from task where name = ?", (name,)).first()
        self.commit()
        return rowcount

    def length(self, name='%'):
        return self.query("select count(*) from task \
        where name = ?", (name,)).first()[0]


def initalize():
    global cron, task, taskq, status
    cron = Cron(conf.dbn)
    task = Task(conf.dbn)
    taskq = TaskQ(conf.dbn)
    status = Status(conf.dbn)
