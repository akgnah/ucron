# -*- coding: utf-8 -*

homepage = '''
<!DOCTYPE html>
<html>
<head>
  <title> 欢迎 - uCron </title>
</head>
<body>
  <p>感谢你使用 uCron，若有疑问和建议请Email至 1024@setq.me。</p>
  <p><a href="https://github.com/akgnah/ucron" target="_blank">项目主页</a> | <a href="/status">查看状态</a> |
   <a href="/log">查看日志</a> | <a href="/reload">重载Cron</a></p>
</body>
</html>
'''

reload_cron = '''
<!DOCTYPE html>
<html>
<head>
  <title> 重载配置 - uCron </title>
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
    table {
      background-color: transparent;
    }
    .table {
      width: 100%;
      max-width: 100%;
      margin-bottom: 20px;
    }

    .table > thead > tr > th,
    .table > tbody > tr > th,
    .table > tfoot > tr > th,
    .table > thead > tr > td,
    .table > tbody > tr > td,
    .table > tfoot > tr > td {
      padding: 8px;
      line-height: 1.42857143;
      vertical-align: top;
      border-top: 1px solid #ddd;
    }
    .table > thead > tr > th {
      vertical-align: bottom;
      border-bottom: 2px solid #ddd;
    }
    .table > caption + thead > tr:first-child > th,
    .table > colgroup + thead > tr:first-child > th,
    .table > thead:first-child > tr:first-child > th,
    .table > caption + thead > tr:first-child > td,
    .table > colgroup + thead > tr:first-child > td,
    .table > thead:first-child > tr:first-child > td {
      border-top: 0;
    }
    .table > tbody + tbody {
      border-top: 2px solid #ddd;
    }
    .table .table {
      background-color: #fff;
    }

    .table-bordered {
      border: 1px solid #ddd;
    }
    .table-bordered > thead > tr > th,
    .table-bordered > tbody > tr > th,
    .table-bordered > tfoot > tr > th,
    .table-bordered > thead > tr > td,
    .table-bordered > tbody > tr > td,
    .table-bordered > tfoot > tr > td {
      border: 1px solid #ddd;
    }
    .table-bordered > thead > tr > th,
    .table-bordered > thead > tr > td {
      border-bottom-width: 2px;
    }
    th, td {
      text-align:center;
    }
  </style>
</head>
<body>
% if data:
  <table class="table table-bordered">
    <thead>
      <tr>
        <th> 执行URL</th>
        <th> 执行周期（Schedule） </th>
        <th> 上次执行时间 </th>
        <th> 上次执行状态 </th>
      </tr>
    </thead>
    <tbody>
      % for item in data:
      <tr>
        <td>{{ item['path'] }}</td>
        <td>{{ item['plan'] }}</td>
        <td>{{ item['last'] }}</td>
        <td>{{ item['status'] }}</td>
      </tr>
      % end
    </tbody>
  </table>
% else:
  <p>暂无定时任务，请指定 --cron 参数</p>
% end
  <p>剩余任务队列长度：{{ length }}（估值）</p>
  <p>查看日志：<a href="/log?mode=cron">定时任务</a> | <a href="/log?mode=task">任务队列</a></p>
  <p><a href="/reload">重载Cron</a>* | <a href="/">返回主页</a></p>
  *若在运行过程中修改了 ucron.tab，需手动重载才能生效。
</body>
</html>
'''

log = '''
<!DOCTYPE html>
<html>
<head>
  <title> {{ title }} - uCron </title>
</head>
<body>
% if not data:
  <p>暂无日志</p>
% end
% for item in data:
  <p>{{ item }}</p>
% end
  <p><a href="/status">查看状态</a> |
% if count > 10 * page:
   <a href="/log?mode={{ mode }}&page={{ page + 1}}">下一页</a> |
% end
% if page > 1:
  <a href="/log?mode={{ mode }}&page={{ page - 1}}">上一页</a> |
% end
   <a href="/log?mode={{ mode }}&sort={{ sort['sort'] }}">{{ sort['title'] }}</a> |
   <a href="/log?mode={{ other['mode'] }}">{{ other['title'] }}</a></p>
  <p><a href="/">返回主页</a></p>
</body>
</html>
'''
