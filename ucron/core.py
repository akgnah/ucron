#!/usr/bin/python
# -*- coding: utf-8 -*
import io
import six
import time
import datetime
import threading
from ucron import db
from six.moves.urllib import parse, request


class UTC(datetime.tzinfo):
    def __init__(self, offset=0):
        self._offset = offset

    def utcoffset(self, dt):
        return datetime.timedelta(hours=self._offset)

    def tzname(self, dt):
        return 'UTC %+d:00' % self._offset

    def dst(self, dt):
        return datetime.timedelta(hours=self._offset)


class Job(db.Box):
    def __init__(self, args):
        db.Box.__init__(self, 'Cron')
        self.path = args[0]
        if len(args) > 2:
            self.args = parse.urlencode(parse.parse_qsl(args[1]))
            self.method = args[2]
        elif len(args) == 2:
            if args[1].upper() in ['GET', 'POST']:
                self.args = ''
                self.method = args[1]
            else:
                self.args = parse.urlencode(parse.parse_qsl(args[1]))
                self.method = 'GET'
        else:
            self.args = ''
            self.method = 'GET'


def save_conf(args):
    global conf
    conf = db.Box('Conf')
    conf.update(args.__dict__)


def parse_job(node, attr, scope, job):
    if node == '*':
        job[attr] = list(range(*scope))
    elif '/' in node:
        node, step = node.split('/')
        if '-' in node:
            scope = map(int, node.split('-'))
            scope = [scope[0], scope[1] + 1]
        scope.append(int(step))
        job[attr] = list(range(*scope))
    elif '-' in node:
        scope = map(int, node.split('-'))
        scope = [scope[0], scope[1] + 1]
        job[attr] = list(range(*scope))
    elif ',' in node:
        job[attr] = map(int, node.split(','))
    else:
        job[attr] = [int(node)]


def parse_tab(line):
    args = line.split(' ')
    cron, job = args[:5], Job(args[5:])
    schedule = db.Box('Schedule')
    parse_job(cron[0], 'minute', [0, 60], schedule)
    parse_job(cron[1], 'hour', [0, 24], schedule)
    parse_job(cron[2], 'day', [1, 32], schedule)
    parse_job(cron[3], 'month', [1, 13], schedule)
    parse_job(cron[4], 'weekday', [0, 7], schedule)
    db.cron.push(job.path, job.args, job.method, schedule)


def load_cron():
    if not conf.cron:
        if db.cron.length() == 0:
            parse_tab(clean_log_tab())  # add sys task
        return 'Not Modified'
    db.cron.clean()                     # clean old cron
    parse_tab(clean_log_tab())          # add sys task
    with io.open(conf.cron, 'r', encoding='utf8') as f:
        for line in f.readlines():
            parse_tab(py2_encode(line.strip()))
    return 'OK'


def urlopen(path, args, method):
    now = datetime.datetime.now().strftime('%d/%b/%Y %H:%M:%S')
    try:
        if method.upper() == 'POST':
            data = args.encode() if args else b'None'
        else:
            data = None
            path = path + '?' + args if args else path
        resp = request.urlopen(path, data)
        return '[%s] %s %s - %s' % (now, path, method, resp.code)
    except (Exception) as common_ex:
        return '[%s] %s %s - %s' % (now, path, method, common_ex)


def now():
    now = datetime.datetime.now(UTC(8))
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
        jobs = db.cron.fetchall()
        for job in jobs:
            if sub_in(now(), job):
                resp = urlopen(job.path, job.args, job.method)
                print('* Cron ' + resp)
                update_log('Cron %s\n' % resp)
        time.sleep(61 - datetime.datetime.now().second)


def py2_encode(s, encoding='utf8'):
    return s.encode(encoding) if six.PY2 else s


def py6_encode(s, encoding='utf8'):
    return s.encode(encoding) if isinstance(s, six.text_type) else s


def dict_encode(d, encoding='utf8'):
    return dict({(py6_encode(k), py6_encode(v)) for k, v in d.items()})


def add_task(data):
    path = data.get('path')
    args = data.get('args', '')
    method = data.get('method', 'GET')
    if args:
        args = parse.urlencode(dict_encode(args))
    db.task.push(path, args, method)
    return 'OK'


def daemon_task():
    while True:
        task = db.task.pop()
        if task:
            resp = urlopen(*task[:-1])
            print('* Task ' + resp)
            update_log('Task %s\n' % resp)
        time.sleep(0.01)


def update_log(line):
    with io.open(conf.log, 'a', encoding='utf8') as f:
        f.write(line)


def clean_log():
    with io.open(conf.log, 'r', encoding='utf8') as f:
        logs = f.readlines()
    if len(logs) > conf.max * 2:
        logs = logs[-conf.max:]
        with io.open(conf.log, 'w', encoding='utf8') as f:
            f.writelines(logs)
        return 'OK'
    return 'Not Modified'


def clean_log_tab():
    return '%s http://127.0.0.1:%s/clean' % (conf.tab, conf.port)


def start():
    cron = threading.Thread(target=daemon_cron)
    task = threading.Thread(target=daemon_task)
    return cron, task
