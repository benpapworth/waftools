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

exe = '.exe' if sys.platform=='win32' else ''


def cd(path):
	'''changes current working directory.'''
	logging.debug("cd %s" % path)
	os.chdir(path)


def rm(path):
	'''delete directory, including sub-directories and files it contains.'''
	if os.path.exists(path):
		logging.debug("rm -rf %s" % (path))
		shutil.rmtree(path)

def exe(cmd, args=[]):
	'''executes the given commands using subprocess.check_call.'''
	logging.debug('%s %s' % (cmd, ' '.join(args)))
	subprocess.check_call(cmd.split() + args)


def rm(path):
	'''delete directory, including sub-directories and files it contains.'''
	if os.path.exists(path):
		logging.debug("rm -rf %s" % (path))
		shutil.rmtree(path)


def mkdirs(path):
	'''create directory including missing parent directories.'''
	if not os.path.exists(path):
		logging.debug("mkdirs -p %s" % (path))
		os.makedirs(path)


def create_env(dest, python):
	'''create a virtual test environment.'''
	cmd = 'virtualenv%s %s --no-site-packages' % (exe, dest)
	if python:
		cmd += ' --python=%s' % python
	exe(cmd)
	

def waftools_setup(tmp, devel, version):
	cmd = 'git clone https://bitbucket.org/Moo7/waftools/waftools.git waftools'
	subprocess.check_call(cmd.split())
	if devel:
		top = os.getcwd()
		try:
			cd('%s/waftools' % tmp)
			exe('%s/bin/python setup.py sdist install' % tmp)
		finally:
			cd(top)
	else:
		cmd = '%s/bin/pip install waftools' % tmp
		if version:
			cmd += '==%s' % version	
		exe(cmd)


def waftools_cmake(tmp):
	'''test generated cmake files.'''
	top = os.getcwd()
	try:
		cd('%s/waftools/playground' % tmp)
		exe('waf configure --debug --prefix=%s' % tmp)
		exe('waf cmake')
		mkdirs('%s/ctest' % tmp)
		cd('%s/ctest' % tmp)
		exe('cmake %s/waftools/playground' % tmp, args=['-G', 'Unix Makefiles'])
		exe('make all')
		exe('make clean')
		cd('%s/waftools/playground' % tmp)
		rm('%s/ctest' % tmp)
		exe('waf cmake --clean')
		exe('waf distclean')
	finally:
		cd(top)


def waftools_test(tmp):
	'''perform test operations on waftools package.'''
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
		'waf configure --debug --prefix=%s' % tmp,
		'waf makefile',
		'make all',
		'make install',
		'make uninstall',
		'make clean',
		'waf makefile --clean',
		'waf distclean',
	]

	top = os.getcwd()
	try:
		cd('%s/waftools/playground' % tmp)
		for cmd in commands:
			exe(cmd)
		waftools_cmake(tmp)
	finally:
		cd(top)


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG, format=' %(message)s')

	python='python'
	devel=False
	version=None

	opts, args = getopt.getopt(sys.argv[1:], 'hp:rv:', ['help', 'python=', 'devel', 'version='])
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			sys.exit()
		elif opt in ('-p', '--python'):
			python = arg
		elif opt in ('-d', '--devel'):
			devel = True		
		elif opt in ('-v', '--version'):
			version = arg

	tmp = tempfile.mkdtemp()
	create_env(tmp, python)
	home = os.getcwd()
	try:
		cd(tmp)
		waftools_setup(tmp, devel, version)
		waftools_test(tmp)		
	finally:
		cd(home)
	rm(tmp)


