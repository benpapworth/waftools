#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com


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
		dst.cmd_and_log('python setup.py sdist --formats=gztar upload', cwd=dst.path.abspath())
	dst.algo = 'tar.gz'
	dst.excl = '**/*~ **/*.pyc **/__pycache__/** \
		**/.lock-waf_* build/** **/*.tar.gz \
		MANIFEST dist/** doc/_build/** \
		.git/** **/.gitignore \
		**/.settings/** **/.project **/.pydevproject \
		test/**/.cproject test/**/*.launch test/**/Debug/** \
		test/output/** test/build/** \
		test/**/Makefile test/**/*.mk \
		test/**/CMakeLists.txt \
		test/**/*.cbp test/**/*.layout test/**/*.workspace test/**/*.workspace.layout \
		test/**/*.vcproj test/**/*.sln test/**/*.user test/**/*.ncb test/**/*.suo'

