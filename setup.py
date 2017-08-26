#!/usr/bin/env python
# -*- coding: utf-8 -*
from setuptools import setup
from ucron import __version__


long_description = open('README.rst', 'rb').read().decode('utf8')

setup(name='ucron',
      version=__version__,
      description='micro crontab and task queue',
      author='Akgnah',
      author_email='1024@setq.me',
      url='http://github.com/akgnah/ucron',
      packages=['ucron'],
      install_requires=['bottle'],
      long_description=long_description,
      license='MIT',
      platforms=['any'],
      keywords='crontab task queue')
