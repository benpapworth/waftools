#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

import os
import waftools


top = '.'
out = 'build'


VERSION = waftools.version
APPNAME = 'waftools'


def options(opt):
	opt.add_option('--pypi', dest='pypi', default=False, action='store_true', help='publish package on PyPi')


def configure(conf):
	conf.check_waf_version(mini='1.7.0')


def build(bld):
	if bld.cmd == 'install':
		bld.cmd_and_log('python setup.py install', cwd=bld.path.abspath())

		
def dist(dst):
	if dst.options.pypi:
		dst.cmd_and_log('python setup.py sdist upload', cwd=dst.path.abspath())
	dst.algo = 'tar.gz'
	dst.excl = ' **/*~ **/.lock-w* .git/** build/** dist/** .gitignore **/*.pyc **/__pycache__/**'

