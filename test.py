#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

import os
import sys
import getopt
import subprocess
import tempfile
import logging
import shutil


def cd(path):
	'''changes current working directory.'''
	logging.debug("cd %s" % path)
	os.chdir(path)


def rm(path):
	'''delete directory, including sub-directories and files it contains.'''
	if os.path.exists(path):
		logging.debug("rm -rf %s" % (path))
		shutil.rmtree(path)

def exe(cmd):
	'''executes the given commands using subprocess.check_call.'''
	logging.debug(cmd)
	subprocess.check_call(cmd.split())


def create_env(dest, python):
	'''create a virtual test environment.'''
	cmd = 'virtualenv %s --no-site-packages' % dest
	if python:
		cmd += ' --python=%s' % python
	exe(cmd)
	

def waftools_clone(tmp, devel):
	if devel:
		cmd = 'git clone https://bitbucket.org/Moo7/waftools/waftools.git waftools'
		subprocess.check_call(cmd.split())
		top = os.getcwd()
		try:
			cd('%s/waftools' % tmp)
			exe('%s/bin/python setup.py sdist install' % tmp)
		finally:
			cd(top)
	else:
		exe('pip install waftools')


def waftools_test(tmp):
	commands = [
		'waf configure --debug --prefix=%s' % tmp,
		'waf build --all --cppcheck-err-resume',
		'waf clean --all',
		'waf codeblocks',
		'waf codeblocks --clean',
		'waf eclipse',
		'waf eclipse --clean',		
		'waf msdev',
		'waf msdev --clean',
		'waf cmake',
		'waf cmake --clean',
		'waf makefile',
		'waf makefile --clean',
		'waf doxygen',
		'waf indent',
		'waf tree',
		'waf list',
		'waf dist',
		'waf distclean',
		'waf configure --debug --prefix=%s' % tmp,
		'waf install --all',
		'waf uninstall --all',
		'waf distclean',
		
		# TODO: fix build with generated makefiles
		#       when using bld.objects()	
		#'waf configure --debug --prefix=%s' % tmp,
		#'waf makefile',
		#'make all',
		#'make install',
		#'make uninstall',
		#'make clean',
		#'waf makefile --clean',
		#'waf distclean',

		# TODO: fix build with cmake generated makefiles
		#       when using bld.objects()
		#'waf configure --debug --prefix=%s' % tmp,
		#'waf cmake',
		#'cmake -G "Unix Makefiles"',
		#'make all',
		#'make clean',
		#'waf cmake --clean',
		#'waf distclean',
	]

	top = os.getcwd()
	try:
		cd('%s/waftools/playground' % tmp)
		for cmd in commands:
			exe(cmd)
	finally:
		cd(top)


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG, format=' %(message)s')

	python='python'
	devel=False

	opts, args = getopt.getopt(sys.argv[1:], 'hp:r', ['help', 'python=', 'devel'])
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			sys.exit()
		elif opt in ('-p', '--python'):
			python = arg
		elif opt in ('-d', '--devel'):
			devel = True			

	tmp = tempfile.mkdtemp()
	create_env(tmp, python)
	home = os.getcwd()
	try:
		cd(tmp)
		waftools_clone(tmp, devel)
		waftools_test(tmp)		
	finally:
		cd(home)
	rm(tmp)


