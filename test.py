#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

'''
Summary
-------
Perform sanity test on waftools package in a virtual environment. Test can be performed
on either a released package from PyPi or from a local a copy of the waftools package (i.e.
obtained using git clone).


Description
-----------
Creates a new clean temporary python virtual environment (no site packages) and install the
waftools package including its dependencies and performs following test on the package:

	- basic operations (e.g. configure, build, clean, dist)
	- source code analysis using cppcheck
	- create source code documentation using doxygen
	- export projects to eclipse, msdev, codeblocks, make, cmake
	- run make on exported makefiles
	- run cmake on exported cmake files


When succesfully completed the entire temporary virtual environment used during the test will 
be deleted.


Usage
-----
Start with:
    python test.py [options]

Available options:
    -h | --help     prints this help message.

    -g | --git      [optional] specify complete path to git

    -p | --python   [optional] specify complete path to python interpreter

    -d | --devel    [optional] use current directory as package source location.
                    when not specified the latest (or a specific version) released
                    waftools packge from PyPi will be used.

    -v | --version  [optional] waftools package from PyPi to be used.
    -w | --waf      [optional] waf version to be used.

'''


import os
import sys
import stat
import getopt
import subprocess
import tempfile
import logging
import shutil


def usage():
	print(__doc__)


def cd(path):
	'''changes current working directory.'''
	logging.info("cd %s" % path)
	os.chdir(path)


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

	if python:
		version = subprocess.check_output([python, '--version'], stderr=subprocess.STDOUT)
		version = version.split()[1].split('.')
	else:
		version = sys.version_info

	if win32:
		bindir = '%s/Scripts' % (top)
		libdir = '%s/Lib' % (top)
		python = '%s/python.exe' % (bindir)
		pip = '%s/pip.exe' % (bindir)
		waf = '%s -x %s/waf' % (python, bindir)

	else:
		bindir = '%s/bin' % (top)
		libdir = '%s/lib/python%s.%s' % (top, version[0], version[1])
		python = 'python'
		pip = 'pip'
		waf = 'waf'

	wafinstall = '%s/wafinstall%s' % (bindir, '.exe' if win32 else '')
	
	os.environ['WAFDIR'] = "%s/site-packages" % libdir
	os.environ['PYTHONHOME'] = top
	os.environ['PYTHONPATH'] = libdir
	os.environ['PATH'] = '%s%s%s' % (bindir, ';' if win32 else ':', os.environ['PATH'])
	return (python, pip, waf, wafinstall)


def waftools_setup(python, pip, git, wafinstall, devel, version, wafversion):
	'''setup waftools test environment.
	'''
	exe('%s clone https://bitbucket.org/Moo7/waftools/waftools.git waftools' % git)
	wargs = ['--skip-env']
	if wafversion!=None: wargs.extend(['-v%s' % wafversion])
	
	if devel:
		top = os.getcwd()
		try:
			cd('waftools')
			exe(python, args=['setup.py', 'sdist', 'install'])
			cd('waftools')
			exe(python, args=['wafinstall.py'] + wargs)
		finally:
			cd(top)
	else:
		exe(pip, args=['install', 'waftools==%s' % (version) if version else 'waftools'])
		exe(wafinstall, args=wargs)


def waftools_cmake(waf):
	'''test generated cmake files.'''
	top = os.getcwd()
	try:
		cd('%s/waftools/playground' % top)
		exe('%s configure --debug --prefix=.' % waf)
		exe('%s cmake' % waf)
		mkdirs('%s/cbuild' % top)
		cd('%s/cbuild' % top)
		exe('cmake %s/waftools/playground' % top, args=['-G', 'Unix Makefiles'])
		exe('make all')
		exe('make clean')
		cd('%s/waftools/playground' % top)
		rm('%s/ctest' % top)
		exe('%s cmake --clean' % waf)
		exe('%s distclean' % waf)
	finally:
		cd(top)


def waftools_bdist(waf):
	'''test binary distributions.'''
	if sys.platform == 'win32':
		prefix = 'C:/waftools-test'
	else:
		prefix = '/usr'

	top = os.getcwd()
	try:
		cd('%s/waftools/playground' % top)
		exe('%s configure --prefix=%s' % (waf, prefix))
		exe('%s bdist' % waf)
		exe('%s distclean' % waf)
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
	finally:
		cd(top)


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG, format=' %(message)s')

	python=None
	git=None
	devel=False
	version=None
	wafversion=None

	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hg:p:dv:w:', ['help', 'git=', 'python=', 'devel', 'version=', 'waf='])
		for opt, arg in opts:
			if opt in ('-h', '--help'):
				usage()
				sys.exit()
			elif opt in ('-g', '--git'):
				git = arg
			elif opt in ('-p', '--python'):
				python = arg
			elif opt in ('-d', '--devel'):
				devel = True
			elif opt in ('-v', '--version'):
				version = arg
			elif opt in ('-w', '--waf'):
				wafversion = arg
				
	except getopt.GetoptError as err:
		print(str(err))
		usage()
		sys.exit(2)

	if not git:
		git = 'git'
	git = git.replace('\\', '/')
		
	top = tempfile.mkdtemp().replace('\\', '/')
	home = os.getcwd()
	try:
		(python, pip, waf, wafinstall) = create_env(top, python)
		cd(top)
		waftools_setup(python, pip, git, wafinstall, devel, version, wafversion)
		waftools_test(waf)
		waftools_cmake(waf)
		waftools_bdist(waf)
	finally:
		cd(home)
		rm(top)

