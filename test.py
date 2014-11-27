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
	logging.info("cd %s" % path)
	os.chdir(path)


def rm(path):
	'''delete directory, including sub-directories and files it contains.'''
	if os.path.exists(path):
		logging.info("rm -rf %s" % (path))
		shutil.rmtree(path)

def exe(cmd, args=[]):
	'''executes the given commands using subprocess.check_call.'''
	args = cmd.split() + args
	logging.info('%s' % (' '.join(args)))
	subprocess.check_call(args)


def rm(path):
	'''delete directory, including sub-directories and files it contains.'''
	if os.path.exists(path):
		logging.info("rm -rf %s" % (path))
		shutil.rmtree(path)


def mkdirs(path):
	'''create directory including missing parent directories.'''
	if not os.path.exists(path):
		logging.info("mkdirs -p %s" % (path))
		os.makedirs(path)


def create_env(top, python):
	'''create a virtual test environment and return environment settings.'''
	win32 = sys.platform=='win32'
	
	cmd = 'pip install virtualenv'
	if not win32:
		cmd += ' --user'
	exe(cmd)

	cmd = 'virtualenv %s --no-site-packages' % (top)
	if python:
		cmd += ' --python=%s' % python
	exe(cmd)
	
	bindir = '%s/%s' % (top, 'Scripts' if win32 else 'bin')
	libdir = '%s/Lib' % (top) # TODO for linux
	python = '%s/python%s' % (bindir, '.exe' if win32 else '')
	pip = '%s/pip%s' % (bindir, '.exe' if win32 else '')
	wafinstall = '%s/wafinstall%s' % (bindir, '.exe' if win32 else '')
	return (python, pip, wafinstall)


def waftools_setup(python, pip, git, wafinstall, devel, version):
	'''setup waftools test environment.
	'''
	exe('%s clone https://bitbucket.org/Moo7/waftools/waftools.git waftools' % git)
		
	if devel:
		top = os.getcwd()
		try:
			cd('waftools')
			exe(python, args=['setup.py', 'sdist', 'install'])
			cd('waftools')
			exe(python, args=['wafinstall.py', '--local', '--tools=unity,batched_cc'])
		finally:
			cd(top)
	else:
		exe(pip, args=['install', 'waftools==%s' % (version) if version else 'waftools'])
		exe(wafinstall, args=['--local', '--tools=unity,batched_cc'])

	exe(python, args=['-c', 'import sys; print(sys.prefix);'])	
	exe(pip, args=['list'])
	exe(python, args=['-c', 'import waftools; print(waftools.version);'])	


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
		
	top = tempfile.mkdtemp().replace('\\', '/')
	(python, pip, wafinstall) = create_env(top, python)
	home = os.getcwd()
	try:
		cd(top)
		waftools_setup(python, pip, git, wafinstall, devel, version)
		#waftools_test(env)		
	finally:
		cd(home)
	#rm(top)


