uCron
=====

缘起
----

小鲸鱼最初运行在本地，在饭否API要求应用改用OAuth认证时，重写并迁移到了新浪SAE。小鲸鱼每隔一段时间会抓取一次Timeline，同时需要按时上下班，所以使用了SAE提供的任务队列和定时任务。如此运行了几年（懒），直到SAE提高了收费标准（小鲸鱼每天消费多了10倍）。试着把数据从MySQL迁移到较便宜的Memcache后（这也是小鲸鱼现在的源码有着在Redis中模拟SQL的怪异行为的原因），消耗仍然过高。最后把小鲸鱼迁移到VPS，因为使用了定时任务和任务队列，同时本着造轮子的原则，写了个简单的task。

现在回头看，小鲸鱼的代码写得很糙，那个task反而显得有趣些，于是便把task提出来改成了现在这个小工具。

（注：小鲸鱼是饭否上一个问候机器人）

安装
----

.. code-block:: bash

   $ sudo pip install ucron

程序依赖 six 和 bottle，在Win10上，Python2.7和3.6测试通过，在Archlinux上，Python2.7和3.3+测试通过。

使用
----

.. code-block:: python

   python -m ucron

这是最简单的使用方法，然后用浏览器打开 |ucron_home| 将会看到一个简陋的欢迎页面。

.. |ucron_home| raw:: html

   <a href="http://127.0.0.1:8089/" target="_blank">http://127.0.0.1:8089/</a>

运行 python -m ucron -h 可查看全部可用参数。
::

   --port  指定程序运行的端口，默认为8089。
   --cron  指定定时任务的配置文件，格式见ucron.tab或下文。
   --dbn   指定一个文件用于SQLite，或者不提供此参数以使用默认值 :memory: ，
           该值会告诉SQLite使用内存模式。内存模式非常快，但在程序关闭时会丢失未完成的任务队列。
   --log   指定一个日志文件，默认为当前目录下的ucron.log。
   --max   指定日志文件的最大行数，默认值为10240。
   --tab   指定清理日志文件的执行周期，默认为每天早上5点。

典型的使用方法可能是这样

.. code-block:: python

   python -m ucron --cron ucron.tab

这会读取当前目录下的ucron.tab增加定时任务。指定给参数的文件可为绝对路径或相对路径。

定时任务
^^^^^^^^

::

   */2 * * * * http://setq.me/books id=home2&text=测试 GET

这是ucron.tab中的一行，它使用和Crontab类似的格式，每行为一个任务，每个任务有四个部分，使用空格分隔，最后两个部分都为可选。

第一部分是执行周期，使用和标准Crontab一致的格式；第二部分是要访问的地址；第三部分是提供给地址的参数，使用 key1=value1&key2=value2 的格式；最后一部分是访问方法，可为GET或POST，默认为GET。

因为使用空格分隔各部分，所以URL或参数中不能含有空格。如果在运行中修改了该配置文件，需要访问 |ucron_reload| 以使配置生效。还有一点很重要，请使用 UTF-8 编码保存ucron.tab。

.. |ucron_reload| raw:: html

   <a href="http://127.0.0.1:8089/reload" target="_blank">http://127.0.0.1:8089/reload</a>

这个在线 |crontab_edit| 很有趣。

.. |crontab_edit| raw:: html

   <a href="https://crontab.guru/" target="_blank">Crontab编辑器</a>

任务队列
^^^^^^^^

要添加任务到队列中很简单

.. code-block:: python

   from ucron import add_task

   body = {'page': 1, 'text': '测试'}
   resp = add_task('http://setq.me', body, method='GET')
   print(resp.read())

add_task方法接收的参数有 path, args, method, host, port，只有path是必需的，其他均为可选参数。

path为要访问的地址，args是要传递给path的数据，它是一个字典，默认为空字符串，method可为GET或POST，默认为GET。

prot默认为8089，如果你在运行时指定了该参数，那么你需要提供该值给add_task，host参数允许你修改以访问非本地运行的uCron。

add_task方法定义在 ext.py 中，它很简单且是该文件中唯一的内容。


杂项
----

目前任务队列只有简单的顺序队列，以后不一定会增加并发队列。

若有任何问题，可以Email联系我。若你是饭否居民，还可以@ |home2| 。

.. |home2| raw:: html

   <a href="http://fanfou.com/home2" target="_blank">home2</a>

谢谢。
