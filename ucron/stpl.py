#!/usr/bin/python
# -*- coding: utf-8 -*
from __future__ import absolute_import

github = '''<a href="https://github.com/akgnah/ucron" class="github-corner" aria-label="View source on Github">
      <svg width="80" height="80" viewBox="0 0 250 250" style="fill:#151513; color:#fff; position: absolute; top: 0; border: 0; right: 0;"
        aria-hidden="true">
        <path d="M0,0 L115,115 L130,115 L142,142 L250,250 L250,0 Z"></path>
        <path d="M128.3,109.0 C113.8,99.7 119.0,89.6 119.0,89.6 C122.0,82.7 120.5,78.6 120.5,78.6 C119.2,72.0 123.4,76.3 123.4,76.3 C127.3,80.9 125.5,87.3 125.5,87.3 C122.9,97.6 130.6,101.9 134.4,103.2"
          fill="currentColor" style="transform-origin: 130px 106px;" class="octo-arm"></path>
        <path d="M115.0,115.0 C114.9,115.1 118.7,116.5 119.8,115.4 L133.7,101.6 C136.9,99.2 139.9,98.4 142.2,98.6 C133.8,88.0 127.5,74.4 143.8,58.0 C148.5,53.4 154.0,51.2 159.7,51.0 C160.3,49.4 163.2,43.6 171.4,40.1 C171.4,40.1 176.1,42.5 178.8,56.2 C183.1,58.6 187.2,61.8 190.9,65.4 C194.5,69.0 197.7,73.2 200.1,77.6 C213.8,80.2 216.3,84.9 216.3,84.9 C212.7,93.1 206.9,96.0 205.4,96.6 C205.1,102.4 203.0,107.8 198.3,112.5 C181.9,128.9 168.3,122.5 157.7,114.1 C157.9,116.9 156.7,120.9 152.7,124.9 L141.0,136.5 C139.8,137.7 141.6,141.9 141.8,141.8 Z"
          fill="currentColor" class="octo-body"></path>
      </svg>
    </a>'''  # Svg copy from httpbin.org

style = '''*{-webkit-box-sizing: border-box;-moz-box-sizing: border-box;box-sizing: border-box;}
      a{color:#0072E3;text-decoration:none;}
      a:hover{text-decoration:underline;}
      .container{position:relative;max-width:1080px;margin:auto;}
      nav{position:absolute;left:0px;width:200px;}
      section{margin-left:210px;}
      .title{font-size:36px;margin:0;font-family:Open Sans,sans-serif;color:#3b4151;}
      .title small{font-size:10px;position:relative;top:-5px;display:inline-block;margin:0 0 0 5px;padding:2px 4px;vertical-align:super;border-radius:57px;background:#7d8492;}
      .title small pre{margin:0;font-family:Titillium Web,sans-serif;color:#fff;}'''

nav = '''<h2 class="title">uCron
          <small><pre class="version">{{ version }}</pre></small>
        </h2>
        <p class="description">A micro Crontab &amp; Task Queue for Python Web.</p>
        <form action="/taskq" method="GET">
          队列名称：
          <input type="text" name="name" /><br>
          队列类型：
          <select name="mode"><br>
            <option value="seq">seq</option>
            <option value="con">con</option>
          </select>
          <p><input type="hidden" name="opt" value="add" />
          <input type="submit" value="添加队列" /></p>
        </form>
        <p><a href="{{ nav[0] }}">{{ nav[1] }}</a> | <a href="/reload" onclick="return confirm('reload sure?');">重载 Cron</a></p>'''

status = '''<!DOCTYPE html>
<html>
  <head>
    <title> {{ title }} - uCron </title>
    <style>
      #style#
      hr{height:1px;border:none;border-top:1px dashed gray;}
      .table-container{width:100%;overflow-y:auto;_overflow:auto;margin:1em 0;}
      table{border:0;border-collapse:collapse;text-align:center;min-height:25px;line-height:25px;}
      table td, table th{border:1px solid #999;padding:.5em 1em;width:25%;}
      .info{text-align:center;margin-bottom:10px;background:#fff8e1;color:#795548;border:1px solid #ffecb3;border-radius:4px;}
    </style>
  </head>
  <body>
    #github#
    <div class="container">
      <nav>
        #nav#
      </nav>
      <section>
      % if notice:
        <p class="info">{{ notice }}</p>
      % end
      % if cron:
        <table class="table-container">
          <thead>
            <tr>
              <th> 执行 URL </th><th> 执行周期（Schedule） </th><th> 上次执行时间 </th><th> 上次执行状态 </th>
            </tr>
          </thead>
          <tbody>
          % for item in cron:
            <tr>
              <td>{{ item[0] }}</td><td>{{ item[1] }}</td><td>{{ item[2] }}</td><td>{{ item[3] }}</td>
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
              <th> 队列名称 </th><th> 队列类型 </th><th> 剩余长度（估值） </th><th> 操作 </th>
            </tr>
          </thead>
          <tbody>
          % for item in task:
            <tr>
              <td>{{ item[0] }}</td><td>{{ item[1] }}</td><td>{{ item[2] }}</td>
              <td><a href="/taskq?opt=del&name={{ item[0] }}" onclick="return confirm('delete sure?');">删除</a> |
                <a href="/taskq?opt=cls&name={{ item[0] }}" onclick="return confirm('cleanup sure?');">清空</a></td>
            </tr>
            % end
          </tbody>
        </table>
      </section>
    </div>
  </body>
</html>'''.replace('#nav#', nav).replace('#style#', style).replace('#github#', github)

log = '''<!DOCTYPE html>
<html>
  <head>
    <title> {{ title }} - uCron </title>
    <style>
      #style#
      .section p{margin:0;padding:0;line-height:32px;}
      .even{background-color:#F8F8F8;}
    </style>
  </head>
  <body>
    #github#
    <div class="container">
      <nav>
       #nav#
      </nav>
      <section>
      % if not data:
        <p>暂无日志</p>
      % end
      % for i, item in enumerate(data, 1):
        <p{{ !' class="even"' if i % 2 == 0 else '' }}>{{ item.strip() }}</p>
      % end
        <p>
      % if count > 10 * page:
        <a href="/log?mode={{ mode }}&page={{ page + 1}}">下一页</a> |
      % end
      % if page > 1:
        <a href="/log?mode={{ mode }}&page={{ page - 1}}">上一页</a> |
      % end
        <a href="/log?mode={{ mode }}&sort={{ sort['sort'] }}">{{ sort['title'] }}</a> |
        <a href="/log?mode={{ other['mode'] }}">{{ other['title'] }}</a></p>
      </section>
    </div>
  </body>
</html>'''.replace('#nav#', nav).replace('#style#', style).replace('#github#', github)