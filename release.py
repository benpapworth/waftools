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


def release(git):
	# PIP: install required packages
	packages = subprocess.check_output('pip list'.split()).decode('utf-8')
	if 'Sphinx' not in packages:
		subprocess.call('pip install Sphinx'.split())


	# WAF: install waflib (required for Sphinx documentation)
	subprocess.call('python waftools/wafinstall.py'.split())


	# WAFTOOLS: install latest (required for Sphinx documentation)
	cmd = 'python setup.py install'
	if sys.platform != 'win32':
		cmd += ' --user'
	subprocess.call(cmd.split())


	# DOC: create html documentation using Sphinx
	top = os.getcwd()
	try:
		os.chdir('doc')
		subprocess.call('make html'.split())
	finally:
		os.chdir(top)


	# ZIP: create zip containing html documentation
	top = os.getcwd()
	try:
		os.chdir('doc/_build/html')
		name = os.path.join(top, 'waftools-doc-html.zip')
		with zipfile.ZipFile(name, 'w') as zip:
			for (root, dirs, files) in os.walk('.'):
				for file in files:
					zip.write('%s/%s' % (root, file))
	finally:
		os.chdir(top)


	# BITBUCKET: create upload package
	subprocess.call('python setup.py sdist --formats=gztar'.split())

	# GIT: tag the new release
	version = str(waftools.version)
	subprocess.call('{0} tag -a v{1} -m "v{1}"'.format(git, version).split())
	subprocess.call('{0} push origin --tags'.format(git).split())

	# PYPI: publish package
	subprocess.call('python twine upload dist/*'.split())


if __name__ == "__main__":
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
	
	
