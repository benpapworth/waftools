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

def exe(cmd, args=[], env=os.environ):
	'''executes the given commands using subprocess.check_call.'''
	logging.debug('%s %s' % (cmd, ' '.join(args)))
	subprocess.check_call(cmd.split() + args, env=env)


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
	'''create a virtual test environment and return environment settings.'''
	win32 = sys.platform=='win32'
	
	cmd = 'pip install virtualenv'
	if not win32:
		cmd += ' --user'
	exe(cmd)

	cmd = 'virtualenv %s --no-site-packages' % (dest)
	if python:
		cmd += ' --python=%s' % python
	exe(cmd)
	
	bindir = '%s/%s' % (dest, 'Scripts' if win32 else 'bin')
	wafdir = '%s/Lib/site-packages' % (dest) # TODO for linux
	
	env = os.environ.copy()
	env['PYTHONHOME'] = ''
	env['WAFDIR'] = wafdir
	env['PATH'] = '%s%s%s' % (bindir, ';' if win32 else ':', env['PATH'])
	return env


def waftools_setup(env, git, devel, version):
	'''setup waftools test environment.
	'''
	exe('%s clone https://bitbucket.org/Moo7/waftools/waftools.git waftools' % git)
	
	if devel:
		top = os.getcwd()
		try:
			cd('waftools')
			exe('python setup.py sdist install', env=env)
		finally:
			cd(top)
	else:
		cmd = 'pip install waftools'
		if version:
			cmd += '==%s' % version	
		exe(cmd, env=env)


def waftools_cmake(env):
	'''test generated cmake files.'''
	top = os.getcwd()
	try:
		cd('%s/waftools/playground' % top)
		exe('waf configure --debug --prefix=.', env=env)
		exe('waf cmake', env=env)
		mkdirs('%s/cbuild' % top)
		cd('%s/cbuild' % top)
		exe('cmake %s/waftools/playground' % top, args=['-G', 'Unix Makefiles'], env=env)
		exe('make all', env=env)
		exe('make clean', env=env)
		cd('%s/waftools/playground' % top)
		rm('%s/ctest' % top)
		exe('waf cmake --clean', env=env)
		exe('waf distclean', env=env)
	finally:
		cd(top)


def waftools_test(env):
	'''perform test operations on waftools package.'''
	commands = [
		'waf configure --debug --prefix=.',
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
		'waf configure --debug --prefix=.',
		'waf install --all',
		'waf uninstall --all',
		'waf distclean',
		'waf configure --debug --prefix=.',
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
		cd('%s/waftools/playground' % top)
		for cmd in commands:
			exe(cmd, env=env)
		waftools_cmake(env)
	finally:
		cd(top)


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG, format=' %(message)s')

	python=None
	git=None
	devel=False
	version=None

	opts, args = getopt.getopt(sys.argv[1:], 'hg:p:rv:', ['help', 'git=', 'python=', 'devel', 'version='])
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			sys.exit()
		elif opt in ('-g', '--git'):
			git = arg
		elif opt in ('-p', '--python'):
			python = arg
		elif opt in ('-d', '--devel'):
			devel = True		
		elif opt in ('-v', '--version'):
			version = arg

	if not git:
		git = 'git'
	git = git.replace('\\', '/')
		
	tmp = tempfile.mkdtemp()
	env = create_env(tmp, python)
	top = os.getcwd()
	try:
		cd(tmp)
		waftools_setup(env, git, devel, version)
		waftools_test(env)		
	finally:
		cd(top)
	rm(tmp)


