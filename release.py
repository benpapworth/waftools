#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com


'''
Description
-----------
Creates a new release::

	- install required packages using pip
	- install waflib, required for Sphinx documentation
	- install waftools, required for Sphinx documentation
	- create html documentation using Sphinx
	- create zip containing html documentation
	- create waftools package to be uploaded to BitBucket
	- tags the new release using git
	- publishes the package on PyPi

'''


import os
import sys
import subprocess
import waftools
import zipfile
import getopt
import logging
import shutil


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
		if os.path.isdir(path):
			shutil.rmtree(path, onerror=onerror)
		else:
			os.remove(path)


def mkdirs(path):
	'''create directory including missing parent directories.'''
	if not os.path.exists(path):
		logging.info("mkdirs -p %s" % (path))
		os.makedirs(path)


def cp(src, dst):
	'''copy files or directories'''
	logging.info("cp %s %s" % (src,dst))
	if os.path.isdir(src):
		shutil.copytree(src,dst)
	else:
		shutil.copy2(src,dst)


def release(git):
	win32 = sys.platform == 'win32'
	user = '--user' if not win32 else ''

	# PIP: install required packages
	packages = subprocess.check_output('pip list'.split()).decode('utf-8')
	for package in ('Sphinx', 'sphinx-rtd-theme', 'twine'):
		if package not in packages:
			exe('pip install', args=[package,user])

	# WAFTOOLS: install latest (required for Sphinx documentation)
	exe('pip install -I %s' % os.path.dirname(__file__), args=[user])

	# WAF: install waflib (required for Sphinx documentation)
	exe('wafinstall', args=[user])

	# DOC: create html documentation using Sphinx
	top = os.getcwd()
	try:
		cd('doc')
		exe('make html')
	finally:
		cd(top)

	# ZIP: create zip containing html documentation
	top = os.getcwd()
	try:
		cd('doc/_build/html')
		name = os.path.join(top, 'waftools-doc-html.zip')
		with zipfile.ZipFile(name, 'w') as zip:
			for (root, dirs, files) in os.walk('.'):
				for file in files:
					zip.write('%s/%s' % (root, file))
	finally:
		cd(top)

	# BITBUCKET: create upload package
	cp('doc/history.rst', 'CHANGES')
	exe('python setup.py sdist --formats=gztar')
	rm('CHANGES')

	# GIT: tag the new release
	version = str(waftools.version)
	exe('{0} tag -a v{1} -m "v{1}"'.format(git, version))
	exe('{0} push origin --tags'.format(git))

	# PYPI: publish package
	exe('twine upload dist/*')


if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG, format=' %(message)s')
	git=None
	opts, args = getopt.getopt(sys.argv[1:], 'hg:', ['help', 'git='])
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			sys.exit()
		elif opt in ('-g', '--git'):
			git = arg

	if not git:
		git = 'git'
	git = git.replace('\\', '/')
	release(git)

	
