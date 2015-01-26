#! /usr/bin/env python
# encoding: utf-8
# Thomas Nagy, 2011

"""
Obtain packages, unpack them in a location, and add associated uselib variables
(CFLAGS_pkgname, LIBPATH_pkgname, etc).

The default is use a Dependencies.txt file in the source directory.

This is a work in progress.

Usage:

def options(opt):
	opt.load('package')

def configure(conf):
	conf.load_packages()
"""

import os
import sys
if sys.version_info[0] == 2:
	import urllib2 as web
else:
	import urllib.request as web
import tarfile
import zipfile
from waflib import Logs
from waflib.Configure import conf

WAFCACHE_PACKAGE = '.wafcache_package'
CACHEVAR = 'WAFCACHE_PACKAGE'


@conf
def get_package_cache_dir(self):
	cache = None
	if CACHEVAR in self.env:
		cache = self.env[CACHEVAR]
		cache = self.root.make_node(cache)
	elif self.env[CACHEVAR]:
		cache = self.env[CACHEVAR]
		cache = self.root.make_node(cache)
	else:
		cache = self.srcnode.make_node(WAFCACHE_PACKAGE)
	cache.mkdir()
	return cache


@conf
def wget(self, cache, src, dst):
	if self.variant:
		dst = '%s/%s' % (self.variant, dst)

	archive = cache.find_node(dst)
	if archive:
		return archive

	url = None
	archive = cache.make_node(dst)
	try:
		self.start_msg("downloading '%s'" % (dst))
		url = web.urlopen(url=src, timeout=20)
		archive.write(url.read())
		self.end_msg('done')
	except Exception as err:
		self.end_msg('failed', color='RED')
		raise(err)
	finally:
		if url: url.close()
	return archive


@conf
def deflate(self, archive):
	path = archive.parent
	ext = os.path.splitext(str(archive))[1]

	if ext == '.zip':
		self.start_msg("deflating '%s'" % (archive))
		with zipfile.ZipFile(archive, 'r') as f:
			f.extractall(path=path.abspath())
		self.end_msg('done')

	elif ext in ('.gz', '.tgz'):
		self.start_msg("deflating '%s'" % (archive))
		with tarfile.open(archive.abspath(),'r:gz') as tar:
			for member in tar.getmembers():
				tar.extract(member, path=path.abspath())
		self.end_msg('done')

	elif ext in ('.bz2',):
		self.start_msg("deflating '%s'" % (archive))
		with tarfile.open(archive.abspath(),'r:bz2') as tar:
			for member in tar.getmembers():
				tar.extract(member, path=path.abspath())
		self.end_msg('done')

	else:
		self.fatal('unable to deflate %s' % archive)


@conf
def load_packages(self):
	cache = self.get_package_cache_dir()

	# repeat for all packages
	# read configuration from file
	package = {}
	package['libev'] = {
		'name'		: 'libev',
		'version'	: '4.19',
		'top'		: 'libev-4.19',
		'url'		: 'http://dist.schmorp.de/libev/libev-4.19.tar.gz'
	}



	name = 'libev'
	version = '4.19'
	release = '%s-%s' % (name, version)
	src = 'http://dist.schmorp.de/{0}/{0}-{1}.tar.gz'.format([name, version])
	dst = '%s.tar.gz' % release
	archive = self.wget(cache, src, dst)
	patches = ['a.patch', 'b.patch']

	# TODO: check if package is installed/available
	self.deflate(archive)
	self.patch(archive, release, patches)
	self.configure(archive, release)
	self.make_install(archive, release)


	# TODO: conditionals (do only if):
	#	- variant
	#   - dest_os, dest_cpu
	
	# actions:
	#   patch
	# 	configure --prefix=xx CC=yy AR=zz
	#   make install

	# use:
	#	add dependencies (CFLAGS_pkgname, LIBPATH_pkgname, etc) based on configuration file

