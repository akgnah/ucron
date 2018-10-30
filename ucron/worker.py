#!/usr/bin/python
# -*- coding: utf-8 -*
from __future__ import absolute_import

import time
import uuid
import threading
from datetime import tzinfo, timedelta, datetime

from ucron import conf, db, __version__
from ucron.utils import request, urlencode, parse_qsl, Queue, to_string

stdout_q = Queue()
lock = threading.Lock()


class UTC(tzinfo):
    def __init__(self, offset=0):
        self._offset = offset

    def utcoffset(self, dt):
        return timedelta(hours=self._offset)

    def tzname(self, dt):
        return 'UTC %+d:00' % self._offset

    def dst(self, dt):
        return timedelta(hours=self._offset)


class Job:
    def __init__(self, args):
        self.path = args[0]
        if len(args) > 2:
            self.args = urlencode(parse_qsl(args[1]))
            self.method = args[2]
        elif len(args) == 2:
            if args[1].upper() in ['GET', 'POST']:
                self.args = ''
                self.method = args[1]
            else:
                self.args = urlencode(parse_qsl(args[1]))
                self.method = 'GET'
        else:
            self.args = ''
            self.method = 'GET'


def parse_schedule(node, attr, scope, schedule):
    if node == '*':
        schedule[attr] = list(range(*scope))
    elif '/' in node:
        node, step = node.split('/')
        if '-' in node:
            scope = list(map(int, node.split('-')))
            scope = [scope[0], scope[1] + 1]
        scope.append(int(step))
        schedule[attr] = list(range(*scope))
    elif '-' in node:
        scope = list(map(int, node.split('-')))
        scope = [scope[0], scope[1] + 1]
        schedule[attr] = list(range(*scope))
    elif ',' in node:
        schedule[attr] = list(map(int, node.split(',')))
    else:
        schedule[attr] = [int(node)]


def parse_crontab(line):
    args = line.split(' ')
    job_id = uuid.uuid5(uuid.NAMESPACE_DNS, line).hex
    cron, job = args[:5], Job(args[5:])
    db.status.push(job_id, ' '.join(cron))
    schedule = {}
    parse_schedule(cron[0], 'minute', [0, 60], schedule)
    parse_schedule(cron[1], 'hour', [0, 24], schedule)
    parse_schedule(cron[2], 'day', [1, 32], schedule)
    parse_schedule(cron[3], 'month', [1, 13], schedule)
    parse_schedule(cron[4], 'weekday', [0, 7], schedule)
    db.cron.push(job_id, job.path, job.args, job.method, schedule)


def urlopen(path, args, method, json=False):
    now = datetime.now(UTC(conf.utc)).strftime('%d/%b/%Y %H:%M:%S')
    try:
        headers = {'User-Agent': 'uCron v%s' % __version__}
        path += '/' if path.count('/') < 3 else ''
        if method.upper() == 'POST' or json:
            method = 'POST'
            data = args.encode('utf8') if args else b''
            if json:
                headers['Content-Type'] = 'application/json'
        else:
            data = None
            path += '?' + args if args else ''
        resp = request.urlopen(request.Request(path, headers=headers), data)
        return '[%s] %s %s - %s' % (now, path, method, resp.code)
    except Exception as common_ex:
        return '[%s] %s %s - %s' % (now, path, method, common_ex)


def now():
    now = datetime.now(UTC(conf.utc))
    now = {
        'minute': now.minute,
        'hour': now.hour,
        'day': now.day,
        'month': now.month,
        'weekday': (now.weekday() + 1) % 7  # Monday == 1 ... Saturday == 6, Sunday == 0
    }
    return now


def sub_in(now, job):
    for key in now.keys():
        if now[key] not in job[key]:
            return False
    return True


def daemon_cron():
    while True:
        for job in db.cron.fetchall():
            if sub_in(now(), job):
                resp = urlopen(job['path'], job['args'], job['method'])
                db.status.update(job['id'], resp)
                stdout_q.put('Cron %s' % resp)
        time.sleep(60.1 - datetime.now().second)


def run_task(task):
    resp = urlopen(*task[:-1])
    stdout_q.put('Task %s' % resp)


def select_task(name, mode):
    if mode == 'seq':
        while True:
            task = db.task.pop(name)
            if not task:
                break
            run_task(task)
    else:
        threads = []
        for task in db.task.fetchall(name):
            threads.append(threading.Thread(target=run_task, args=(task,)))
        for t in threads:
            t.start()


def daemon_task():
    while True:
        threads = []
        for name, mode in db.taskq.fetchall():
            threads.append(threading.Thread(target=select_task, args=(name, mode)))
        for t in threads:
            t.start()
        time.sleep(0.01)


def _stdout():
    prefix = '%s' if conf.quiet else '* %s'
    while True:
        line = stdout_q.get()
        with open(conf.log, 'ab') as f:
            f.write(('%s\n' % line).encode('utf8'))
        print(prefix % line)


def clean_log():
    lock.acquire()
    with open(conf.log, 'rb') as f:
        lines = f.readlines()
    with open(conf.log, 'wb') as f:
        f.writelines(lines[-conf.max:])
    lock.release()


def load_crontab():
    db.cron.empty()  # empty old cron
    parse_crontab('%s %s/clean' % (conf.tab, conf.local))  # add clean task

    if not conf.cron:  # nothing to do
        return

    if conf.reload:
        parse_crontab('* * * * * %s/reload' % conf.local)  # add reload task

    with open(conf.cron, 'rb') as f:
        for line in f.readlines():
            line = to_string(line).strip()
            if not line:
                break
            if line.startswith('#'):
                continue
            parse_crontab(line)


def start():
    print('uCron v%s server starting up ...' % __version__)

    load_crontab()
    db.taskq.push('default_seq', 'seq')  # add default sequence queue
    db.taskq.push('default_con', 'con')  # add default concurrence queue

    threads = []
    for func in (daemon_cron, daemon_task, _stdout):
        threads.append(threading.Thread(target=func))
    for t in threads:
        t.daemon = True
        t.start()
