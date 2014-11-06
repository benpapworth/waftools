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


# PIP: install required packages
packages = subprocess.check_output('pip list'.split()).decode('utf-8')
if 'Sphinx' not in packages:
	subprocess.call('pip install Sphinx'.split())


# WAF: install waflib (required for Sphinx documentation)
subprocess.call('python waftools/wafinstall.py'.split())


# WAFTOOLS: install latest (required for Sphinx documentation)
cmd = 'python setup.py install%s' % '' if sys.platform=='win32' else ' --user'
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
subprocess.call('python setup.py sdist --formats=gztar --dist-dir=.'.split())

# GIT: tag the new release
version = str(waftools.version)
subprocess.call('git tag -a v{0} -m "v{0}"'.format(version).split())
subprocess.call('git push origin --tags'.split())

# PYPI: publish package
subprocess.call('python setup.py sdist upload'.split())

