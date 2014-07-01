#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

import os
import waftools


top = '.'
out = 'build'
prefix = 'output'

VERSION = waftools.version
APPNAME = 'waftools'


def options(opt):
	opt.add_option('--prefix', dest='prefix', default=prefix, help='installation prefix [default: %r]' % prefix)
	opt.load('export', tooldir=os.path.dirname(waftools.__file__))


def configure(conf):
	conf.check_waf_version(mini='1.7.0')
	conf.load('export')


def build(bld):
	if bld.cmd == 'install':
		bld.cmd_and_log('python setup.py install', cwd=bld.path.abspath())

		
def dist(ctx):
	ctx.algo = 'tar.gz'
	ctx.excl = ' **/*~ **/.lock-w* .git/** build/** dist/** .gitignore **/*.pyc **/__pycache__/**'


