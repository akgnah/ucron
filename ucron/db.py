#!/usr/bin/python
# -*- coding: utf-8 -*
import os
import json
import sqlite3
import threading


class Box(dict):
    def __init__(self, name='Box'):
        self.__dict__['__name__'] = name

    def __getattr__(self, key):
        try:
            return self[key]
        except (KeyError) as key_ex:
            raise AttributeError(key_ex)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except (KeyError) as key_ex:
            raise AttributeError(key_ex)

    def __repr__(self):
        return '<%s %s>' % (self.__dict__['__name__'], dict.__repr__(self))


class DB:
    def __init__(self, dbn=':memory:'):
        self.dbn = dbn
        self.lock = threading.Lock()
        if os.path.exists(self.dbn):
            self.cx = sqlite3.connect(self.dbn, check_same_thread=False)
            self.cu = self.cx.cursor()
        else:
            self.cx = sqlite3.connect(self.dbn, check_same_thread=False)
            self.cu = self.cx.cursor()
            self.execute("CREATE TABLE cron (path CHAR(512), args TEXT, method CHAR(16), schedule TEXT)", True)
            self.execute("CREATE TABLE task (path CHAR(512), args TEXT, method CHAR(16), id INTEGER PRIMARY KEY)", True)

    def __del__(self):
        self.cx.close()

    def execute(self, sql, commit=False):
        self.lock.acquire(True)
        resp = self.cu.execute(sql)
        if commit:
            self.cx.commit()
        self.lock.release()
        return resp


class Cron(DB):
    def __init__(self, dbn):
        DB.__init__(self, dbn)

    def push(self, path, args, method, schedule):
        schedule = json.dumps(schedule)
        self.execute("INSERT INTO cron (path, args, method, schedule) \
        VALUES ('%s', '%s', '%s', '%s')" % (path, args, method, schedule), True)

    def fetchall(self):
        data = []
        cron = self.execute("SELECT path, args, method, schedule FROM cron").fetchall()
        if cron:
            for item in cron:
                job = Box('Cron')
                job.update(dict(zip(['path', 'args', 'method'], item[:-1])))
                job.update(json.loads(item[-1]))
                data.append(job)
        return data

    def clean(self):
        self.execute("DELETE FROM cron", True)

    def length(self):
        data = self.execute("SELECT path FROM cron").fetchall()
        return len(data) if data else 0


class Task(DB):
    def __init__(self, dbn):
        DB.__init__(self, dbn)

    def push(self, path, args, method):
        self.execute("INSERT INTO task (path, args, method) VALUES ('%s', '%s', '%s')" % (path, args, method), True)

    def pop(self):
        data = self.execute("SELECT path, args, method, id FROM task ORDER BY id").fetchone()
        if data:
            self.execute("DELETE FROM task WHERE id=%s" % data[-1], True)
        return data

    def length(self):
        data = self.execute("SELECT path FROM task").fetchall()
        return len(data) if data else 0


def create_db(dbn):
    global cron, task
    cron = Cron(dbn)
    task = Task(dbn)
