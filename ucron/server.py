#!/usr/bin/python
# -*- coding: utf-8 -*
from __future__ import absolute_import

import os
import threading

from bottle import Bottle, request, template, redirect, __version__

from ucron import db, conf, stpl, worker, __version__ as version
from ucron.utils import dict_encode, urlencode, dumps

app = Bottle()
ctx = threading.local()


def flash():
    tmp = getattr(ctx, 'notice', '')
    ctx.notice = ''
    return tmp


@app.route('/clean')
def clean_log():
    worker.clean_log()
    return 'OK'


@app.route('/reload')
def reload_cron():
    worker.load_crontab()
    ctx.notice = '重新加载成功'
    redirect('/status')


@app.route('/add_task', 'POST')
def add_task():
    path = request.json.get('path')
    args = request.json.get('args')
    method = request.json.get('method')
    name = request.json.get('name')
    json = request.json.get('json')

    if args or json:
        args = dumps(args or json) if json else urlencode(dict_encode(args))

    rowcount = db.task.push(path, args, method, name, int(bool(json)))
    return 'OK' if rowcount > 0 else 'Not Modified'


@app.route('/taskq')
def taskq():
    opt = request.query.get('opt', 'list')
    rowcount = -1

    if opt == 'list':
        task = []
        for item in db.taskq.fetchall():
            length = db.task.length(item[0])
            task.append(list(item) + [length])
        return dumps(task)
    elif opt == 'add':
        name = request.query.name.strip()
        mode = request.query.get('mode', 'seq').strip()
        if name:
            rowcount = db.taskq.push(name, mode)
            if rowcount > 0:
                ctx.notice = '增加队列成功'
            else:
                ctx.notice = '已有同名队列'
        else:
            ctx.notice = '名称不能为空'
    elif opt == 'del':
        name = request.query.name.strip()
        rowcount = db.taskq.delete(name)
        if rowcount > 0:
            db.task.delete(name)
            ctx.notice = '删除队列成功'
        else:
            ctx.notice = '删除队列失败'
    elif opt == 'cls':
        name = request.query.name.strip()
        rowcount = db.task.delete(name)
        if rowcount > 0 or db.task.length(name) == 0:
            rowcount = 1  # fix cli
            ctx.notice = '清空队列成功'
        else:
            ctx.notice = '清空队列失败'

    if request.query.get('cli'):
        flash()
        return 'OK' if rowcount > 0 else 'Not Modified'

    redirect('/status')


@app.route('/')
@app.route('/status')
def status():
    cron = []
    task = []

    for item in db.cron.fetchall():
        plan, status = db.status.fetch(item['id'])
        last = status[1:status.find(']')]
        status = status.split(' - ')[-1]
        cron.append([item['path'], plan, last, status])

    for item in db.taskq.fetchall():
        length = db.task.length(item[0])
        task.append(list(item) + [length])

    context = {
        'title': '查看状态',
        'cron': cron,
        'task': task,
        'conf': conf,
        'notice': flash(),
        'nav': ('/log', '查看日志'),
        'version': version
    }

    return template(stpl.status, context)


@app.route('/log')
def log():
    mode = request.query.get('mode', 'cron')
    sort = request.query.get('sort', 'new')
    page = int(request.query.page or 1)

    data = []
    if os.path.exists(conf.log):
        with open(conf.log, 'rb') as f:
            lines = map(lambda s: s.decode('utf8'), f.readlines())
            data = [line for line in lines
                    if line.startswith(mode.title())]
    data = data[::-1] if sort == 'new' else data

    neg_sort = {
        'new': {'sort': 'old', 'title': '反序查看'},
        'old': {'sort': 'new', 'title': '正序查看'}
    }

    neg_mode = {
        'cron': {'mode': 'task', 'title': '队列任务'},
        'task': {'mode': 'cron', 'title': '定时任务'}
    }

    context = {
        'title': '查看 %s 日志' % mode.title(),
        'data': data[(page - 1) * 10: page * 10],
        'mode': mode,
        'page': page,
        'count': len(data),
        'sort': neg_sort[sort],
        'other': neg_mode[mode],
        'nav': ('/status', '查看状态'),
        'version': version
    }

    return template(stpl.log, context)


def start():
    if conf.quiet:
        print('Bottle v%s server starting up (using WSGIRefServer())...' % __version__)
        print('Listening on http://%s:%s/' % (conf.host, conf.port))
        print('Hit Ctrl-C to quit.')

    app.run(host=conf.host, port=conf.port, quiet=conf.quiet)  # start bottle
