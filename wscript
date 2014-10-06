#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com


import waftools
from waflib import Scripting


top = '.'
out = 'build'


VERSION = waftools.version
APPNAME = 'waftools'


def options(opt):
	opt.add_option('--upload', dest='upload', default=False, action='store_true', help='publish package on PyPi')


def configure(conf):
	conf.check_waf_version(mini='1.7.0')


def build(bld):
	cmd = 'python setup.py sdist --formats=gztar'
	bld.cmd_and_log(cmd, cwd=bld.path.abspath())
	bld.recurse('doc')
	bld.add_post_fun(post)


def post(ctx):
	# create archive containing HTML documentation
	tg = ctx.get_tgen_by_name('doc')
	ctx = Scripting.Dist()
	ctx.algo = 'zip'
	ctx.arch_name = 'waftools-doc-html.zip'
	html = tg.path.get_bld().find_node('html')
	ctx.files = html.ant_glob('**')
	ctx.base_name = ''
	ctx.base_path = html
	ctx.archive()


def dist(dst):
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


