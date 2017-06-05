#!/usr/bin/python
# -*- coding: utf-8 -*
import io
import os
import json
import argparse
from ucron import db, hook, core, stpl
from bottle import route, run, request, template


@route('/reload')
def reload_cron():
    core.load_cron()
    previous = request.headers.get('Referer', '/')
    return template(stpl.reload_cron, previous=previous)


@route('/add_task', 'POST')
def add_task():
    data = json.loads(request.body.read().decode('utf8'))
    return core.add_task(data)


@route('/')
def homepage():
    return template(stpl.homepage)


@route('/status')
def status():
    if os.path.exists(core.conf.log):
        with io.open(core.conf.log, 'r', encoding='utf8') as f:
            logs = f.readlines()
    else:
        logs = []

    cron = [line.strip() for line in logs if line.startswith('Cron')]

    data = []
    if core.conf.cron:
        with io.open(core.conf.cron, 'r', encoding='utf8') as f:
            tabs = f.readlines()
            tabs.insert(0, core.clean_log_tab())

        for tab in tabs:
            args = tab.strip().split(' ')
            plan = ' '.join(args[:5])
            path = args[5]

            match = [line for line in cron if path in line]
            last = match[-1] if match else None
            if last:
                status = last.split(' - ')[-1]
                last = ' '.join(last.split(' ')[1:3])[1:-1]
            else:
                status = None
            data.append(dict(zip(['path', 'plan', 'last', 'status'], [path, plan, last, status])))

    context = {
        'title': '查看状态',
        'data': data,
        'length': db.task.length()
    }

    return template(stpl.status, context)


@route('/log')
def status_log():
    mode = str(request.query.mode or 'cron')
    sort = str(request.query.sort or 'new')
    page = int(request.query.page or 1)

    if os.path.exists(core.conf.log):
        with io.open(core.conf.log, 'r', encoding='utf8') as f:
            logs = f.readlines()
    else:
        logs = []

    data = [line.strip() for line in logs if line.startswith(mode.title())]
    data = data[::-1] if sort == 'new' else data

    neg_sort = {
        'new': {'sort': 'old', 'title': '反序查看'},
        'old': {'sort': 'new', 'title': '顺序查看'}
    }

    neg_mode = {
        'cron': {'mode': 'task', 'title': '任务队列'},
        'task': {'mode': 'cron', 'title': '定时任务'}
    }

    context = {
        'title': '查看 %s 日志' % mode.title(),
        'data': data[(page - 1) * 10: page * 10],
        'mode': mode,
        'page': page,
        'count': len(data),
        'sort': neg_sort[sort],
        'other': neg_mode[mode]
    }

    return template(stpl.log, context)


@route('/clean')
def clean_log():
    return core.clean_log()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='https://github.com/akgnah/ucron', prog='python -m ucron')

    parser.add_argument('--port', nargs='?', default='8089',
                        help='specify a port number, default is 8089')
    parser.add_argument('--cron', nargs='?',
                        help='specify a crontab file, required by crontab')
    parser.add_argument('--dbn', nargs='?', default=':memory:',
                        help='specify a sqlite3 file or :memory:, default is :memory:')
    parser.add_argument('--log', nargs='?', default='ucron.log',
                        help='specify a log file, default is ucron.log in current dir')
    parser.add_argument('--max', nargs='?', default='10240', type=int,
                        help='specify the maximum rows for log, default is 10240')
    parser.add_argument('--tab', nargs='+', default=['0 5 * * *'],
                        help="specify crontab of cut down, default is '0 5 * * *'")

    args = parser.parse_args()
    hook.abspath(args)
    hook.checktab(args)

    # Initialize
    db.create_db(args.dbn)
    core.save_conf(args)
    core.load_cron()

    cron, task = core.start()
    cron.start()
    task.start()
    run(host='127.0.0.1', port=args.port)
    cron.join()
    task.join()
