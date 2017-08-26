#!/usr/bin/python
# -*- coding: utf-8 -*
from __future__ import absolute_import

homepage = '''
<!DOCTYPE html>
<html>
<head>
  <title> 欢迎 - uCron </title>
  <style>
    a {
      color: #0072E3;
      text-decoration: none;
    }
    a:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <p>感谢你使用 uCron，若有疑问和建议请 Email 至 1024@setq.me。</p>
  <p><a href="https://github.com/akgnah/ucron" target="_blank">项目主页</a> | <a href="/status">查看状态</a> |
   <a href="/log">查看日志</a>
% if not conf.reload:
  | <a href="/reload">重载 Cron</a></p>
% else:
  </p>
% end
</body>
</html>
'''

reload_cron = '''
<!DOCTYPE html>
<html>
<head>
  <title> 重载配置 - uCron </title>
  <style>
    a {
      color: #0072E3;
      text-decoration: none;
    }
    a:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <p>OK</p>
  <p><a href="{{ previous }}">返回上页</a></p>
</body>
</html>
'''

status = '''
<!DOCTYPE html>
<html>
<head>
  <title> {{ title }} - uCron </title>
  <style>
    a {
      color: #0072E3;
      text-decoration: none;
    }
    a:hover {
      text-decoration: underline;
    }
    hr {
      height: 1px;
      border: none;
      border-top: 1px dashed gray;
    }
    .table-container {
      width: 100%;
      overflow-y: auto;
      _overflow: auto;
      margin: 1em 0;
    }
    table {
      border: 0;
      border-collapse: collapse;
      text-align: center;
      min-height: 25px;
      line-height: 25px;
    }
    table td, table th {
      border: 1px solid #999;
      padding: .5em 1em;
      width: 25%;
    }
    .info {
      text-align: center;
      margin-bottom: 10px;
      background: #fff8e1;
      color: #795548;
      border: 1px solid #ffecb3;
      border-radius: 4px;
    }
  </style>
</head>
<body>
% if notice:
  <p class="info">{{ notice }}</p>
% end
% if cron:
  <table class="table-container">
    <thead>
      <tr>
        <th> 执行 URL </th>
        <th> 执行周期（Schedule） </th>
        <th> 上次执行时间 </th>
        <th> 上次执行状态 </th>
      </tr>
    </thead>
    <tbody>
      % for item in cron:
      <tr>
        <td>{{ item[0] }}</td>
        <td>{{ item[1] }}</td>
        <td>{{ item[2] }}</td>
        <td>{{ item[3] }}</td>
      </tr>
      % end
    </tbody>
  </table>
% end
% if not conf.cron:
  <p>暂无用户定时任务，请指定 --cron 参数</p>
% end
  <hr />
  <table class="table-container">
    <thead>
      <tr>
        <th> 队列名称 </th>
        <th> 队列类型 </th>
        <th> 剩余长度（估值） </th>
        <th> 操作 </th>
      </tr>
    </thead>
    <tbody>
      % for item in task:
      <tr>
        <td>{{ item[0] }}</td>
        <td>{{ item[1] }}</td>
        <td>{{ item[2] }}</td>
        <td><a href="/taskq?opt=del&name={{ item[0] }}" onclick="return confirm('delete sure?');">删除</a> |
            <a href="/taskq?opt=cls&name={{ item[0] }}" onclick="return confirm('cleanup sure?');">清空</a></td>
      </tr>
      % end
    </tbody>
  </table>
  <hr />
  <form action="/taskq" method="GET">
  队列名称：<input type="text" name="name" />
  队列类型：<select name="mode">
    <option value="seq">seq</option>
    <option value="con">con</option>
  </select>
  <input type="hidden" name="opt" value="add" />
  <input type="submit" value="添加队列" />
  </form>
  <p>查看日志：<a href="/log?mode=cron">定时任务</a> | <a href="/log?mode=task">任务队列</a></p>
  <p><a href="/">返回主页</a></p>
% if not conf.reload:
  *若在运行过程中修改了 ucron.tab，需手动<a href="/reload">重载 Cron </a>才能生效。
% end
</body>
</html>
'''

log = '''
<!DOCTYPE html>
<html>
<head>
  <title> {{ title }} - uCron </title>
  <style>
    a {
      color: #0072E3;
      text-decoration: none;
    }
    a:hover {
      text-decoration: underline;
    }
    .context p {
      margin: 0;
      padding: 0;
      line-height: 32px;
    }
    .even {
      background-color:	#F8F8F8;
    }
  </style>
</head>
<body>
  <div class="context">
% if not data:
    <p>暂无日志</p>
% end
% for i, item in enumerate(data, 1):
    <p{{ !' class="even"' if i % 2 == 0 else '' }}>{{ item.strip() }}</p>
% end
  </div>
  <p>
% if count > 10 * page:
   <a href="/log?mode={{ mode }}&page={{ page + 1}}">下一页</a> |
% end
% if page > 1:
  <a href="/log?mode={{ mode }}&page={{ page - 1}}">上一页</a> |
% end
   <a href="/log?mode={{ mode }}&sort={{ sort['sort'] }}">{{ sort['title'] }}</a> |
   <a href="/log?mode={{ other['mode'] }}">{{ other['title'] }}</a> |
   <a href="/status">查看状态</a></p>
  <p><a href="/">返回主页</a></p>
</body>
</html>
'''
