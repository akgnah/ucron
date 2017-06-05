uCron
=====

缘起
----

小鲸鱼最初运行在本地，在饭否API要求应用改用OAuth认证时，重写并迁移到了新浪SAE。小鲸鱼每隔一段时间会抓取一次Timeline，同时需要按时上下班，所以使用了SAE提供的任务队列和定时任务。如此运行了几年（懒），直到SAE提高了收费标准（小鲸鱼每天消费多了10倍）。试着把数据从MySQL迁移到较便宜的Memcache后（这也是小鲸鱼现在的源码有着在Redis中模拟SQL的怪异行为的原因），消耗仍然过高。最后把小鲸鱼迁移到VPS，因为使用了定时任务和任务队列，同时本着造轮子的原则，写了个简单的task。

现在回头看，小鲸鱼的代码写得很糙，那个task反而显得有趣些，于是便把task提出来改成了现在这个小工具。

安装
----

.. code-block:: bash

   $ sudo pip install ucron

程序依赖 six 和 bottle，在Linux和Win10上，Python2.7和3.6测试通过。

使用
----

.. code-block:: python

   python -m ucron

这是最简单的使用方法，然后用浏览器打开 `http://127.0.0.1:8089` 将会看到一个简陋的欢迎页面。

运行 python -m ucron -h 可查看全部可用参数。
::

   --port  指定程序运行的端口，默认为8089。
   --cron  指定定时任务的配置文件，格式见ucron.tab或下文。
   --dbn   指定一个文件用于Sqlite，或者不提供此参数以使用默认值 :memory:，
           该值会告诉Sqlite使用内存模式。内存模式非常快，但在程序关闭时会丢失未完成的任务队列。
   --log   指定一个日志文件，默认为当前目录下的ucron.log。
   --max   指定日志文件的最大行数，默认值为10240。
   --tab   指定清理日志文件的执行周期，默认为每天早上5点。

定时任务
^^^^^^^^

定时任务的配置文件使用和Crontab类似的格式，每个任务有四个部分，各部分之间用空格分隔。第一部分是执行周期，使用和标准Crontab一致的格式；第二部分是要访问的地址；第三部分是提供给地址的参数，使用 key1=value1&key2=value2 的格式；最后一部分是访问方法，可为GET或POST，默认为GET。前面两个部分必需，后面两个部分可选。因为使用空格分隔各部分，所以URL或参数中不能含有空格。当在运行中修改了该配置文件，需要访问 `http://127.0.0.1:8089/reload` 以使配置生效。

这个在线 |crontab_edit| 很有趣。

.. |crontab_edit| raw:: html

   <a href="https://crontab.guru/" target="_blank">Crontab编辑器</a>

任务队列
^^^^^^^^

要添加任务到队列中很简单

.. code-block:: python

   from ucron add_task

   body = {'page': i, 'text': '测试'}
   resp = add_task('http://setq.me', body, method='GET')
   print(resp.read())

add_task方法可以接受的参数有 path, args, method, host, port。prot默认为8089，当你在运行时指定了该参数，那么你需要提供该值给add_task，你可以修改host参数以访问非本地运行的uCron。path为要访问的地址，args接受一个字典作为传递给path的数据，method可为GET或POST，默认为GET。add_task方法定义在 ext.py 中，它很简单且是该文件中唯一的内容。
