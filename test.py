#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

import os
import sys
import stat
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
	def onerror(function, path, excinfo):
		os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
		if function == os.remove:
			os.remove(path)
		if function == os.rmdir:
			os.rmdir(path)
	
	if os.path.exists(path):
		logging.info("rm -rf %s" % (path))
		shutil.rmtree(path, onerror=onerror)


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
	waf = '%s -x %s/waf' % (python, bindir)
	wafinstall = '%s/wafinstall%s' % (bindir, '.exe' if win32 else '')
	return (python, pip, waf, wafinstall)


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
			exe(python, args=['wafinstall.py', '--local'])
		finally:
			cd(top)
	else:
		exe(pip, args=['install', 'waftools==%s' % (version) if version else 'waftools'])
		exe(wafinstall, args=['--local'])


def waftools_cmake():
	'''test generated cmake files.'''
	top = os.getcwd()
	try:
		cd('%s/waftools/playground' % top)
		exe('waf configure --debug --prefix=.')
		exe('waf cmake')
		mkdirs('%s/cbuild' % top)
		cd('%s/cbuild' % top)
		exe('cmake %s/waftools/playground' % top, args=['-G', 'Unix Makefiles'])
		exe('make all')
		exe('make clean')
		cd('%s/waftools/playground' % top)
		rm('%s/ctest' % top)
		exe('waf cmake --clean')
		exe('waf distclean')
	finally:
		cd(top)


def waftools_test(waf):
	'''perform test operations on waftools package.'''
	commands = [
		'%s configure --debug --prefix=.' % waf,
		'%s build --all --cppcheck-err-resume' % waf,
		'%s clean --all' % waf,
		'%s codeblocks' % waf,
		'%s codeblocks --clean' % waf,
		'%s eclipse' % waf,
		'%s eclipse --clean' % waf,		
		'%s msdev' % waf,
		'%s msdev --clean' % waf,
		'%s cmake' % waf,
		'%s cmake --clean' % waf,
		'%s makefile' % waf,
		'%s makefile --clean' % waf,
		'%s doxygen' % waf,
		'%s indent' % waf,
		'%s tree' % waf,
		'%s list' % waf,
		'%s dist' % waf,
		'%s distclean' % waf,
		'%s configure --debug --prefix=.' % waf,
		'%s install --all' % waf,
		'%s uninstall --all' % waf,
		'%s distclean' % waf,
		'%s configure --debug --prefix=.' % waf,
		'%s makefile' % waf,
		'make all',
		'make install',
		'make uninstall',
		'make clean',
		'%s makefile --clean' % waf,
		'%s distclean' % waf,
	]

	top = os.getcwd()
	try:
		cd('%s/waftools/playground' % top)
		for cmd in commands:
			exe(cmd)
		waftools_cmake()
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
	home = os.getcwd()
	try:
		(python, pip, waf, wafinstall) = create_env(top, python)
		cd(top)
		waftools_setup(python, pip, git, wafinstall, devel, version)
		waftools_test(waf)		
	finally:
		cd(home)
		rm(top)

