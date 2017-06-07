#!/usr/bin/env python
from setuptools import setup
from ucron import __version__


long_description = open('README.rst').read()

setup(name='ucron',
      version=__version__,
      description='micro crontab and taskqueen',
      author='Akgnah',
      author_email='1024@setq.me',
      url=' http://github.com/akgnah/ucron',
      packages=['ucron'],
      install_requires=['bottle', 'six'],
      long_description=long_description,
      license="MIT",
      platforms=["any"],
      keywords='cron task')
