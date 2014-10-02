#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

'''Setup and configure multiple C/C++ build environments and configure
common C/C++ tools used when cross-compiling.

Following tools are (not yet) supported for cross-compile 
environments:
	- cmake
	- doxygen
	- eclipse (TODO: to be supported)
	- makefile
	- msdev
	- package (already includes build results from cross-compiles) 

TODO: create complete module documentation
''' 

import os
try:
	import ConfigParser as configparser
except:
	import configparser

from waflib import Scripting
from waflib.Build import BuildContext, CleanContext, InstallContext, UninstallContext
import waftools
from waftools.codeblocks import CodeblocksContext
from waftools.makefile import MakeFileContext
from waftools.eclipse import EclipseContext

def options(opt):
	opt.add_option('--all', dest='all', default=False, action='store_true', 
				help='execute command for cross-compile environments as well')
	opt.load('cmake', tooldir=waftools.location)
	opt.load('codeblocks', tooldir=waftools.location)
	opt.load('cppcheck', tooldir=waftools.location)
	opt.load('doxygen', tooldir=waftools.location)
	opt.load('eclipse', tooldir=waftools.location)
	opt.load('gnucc', tooldir=waftools.location)
	opt.load('makefile', tooldir=waftools.location)
	opt.load('msdev', tooldir=waftools.location)
	opt.load('package', tooldir=waftools.location)
	opt.load('tree', tooldir=waftools.location)


def configure(conf):	
	conf.check_waf_version(mini='1.7.6')
	prefix = str(conf.env.PREFIX).replace('\\', '/')
	cross = get_config(conf.env.CCROSSINI)

	for name, cc in cross.items(): # setup cross compile environment(s)
		conf.setenv(name)
		conf.env.CCROSS = cross
		conf.env.PREFIX = '%s/opt/%s' % (prefix, name)
		conf.env.BINDIR = '%s/opt/%s/bin' % (prefix, name)
		conf.env.LIBDIR = '%s/opt/%s/lib' % (prefix, name)
		conf.env.CC = '%s-gcc' % (cc['prefix'])
		conf.env.CXX = '%s-g++' % (cc['prefix'])
		conf.env.AR = '%s-ar' % (cc['prefix'])
		conf.load('compiler_c')
		conf.load('compiler_cxx')
		conf.load('cppcheck')
		conf.load('codeblocks') # TODO: contains errors for cross-compilers (WIN32 specific?)
		conf.load('eclipse')
		conf.load('gnucc')
		conf.load('makefile')
		conf.load('tree')

	conf.setenv('')
	conf.env.CCROSS = cross
	conf.load('compiler_c')
	conf.load('compiler_cxx')
	conf.load('cmake')
	conf.load('codeblocks')
	conf.load('cppcheck')
	conf.load('doxygen')
	conf.load('eclipse')
	conf.load('gnucc')
	conf.load('makefile')
	conf.load('msdev')
	conf.load('package')
	conf.load('tree')


def build(bld, trees=[]):
	if bld.variant:
		libs = bld.env.CCROSS[bld.variant]['shlib']
		for lib in libs:
			bld.read_shlib(lib, paths=bld.env.LIBPATH)

	elif bld.options.all:
		if bld.cmd in ('build', 'clean', 'install', 'uninstall', 'codeblocks', 'makefile', 'eclipse'):
			for variant in bld.env.CCROSS.keys():
				Scripting.run_command('%s_%s' % (bld.cmd, variant))

	for tree in trees:
		for script in waftools.get_scripts(tree, 'wscript'):
			bld.recurse(script)


def get_config(name):
	if not os.path.exists(name):
		return {}	
	cross = {}
	c = configparser.ConfigParser()
	c.read(name)
	for s in c.sections():
		cross[s] = {}
		cross[s]['prefix'] = c.get(s,'prefix')
		cross[s]['shlib'] = [l for l in str(c.get(s,'shlib')).split(',') if not l == ''] 
	return cross


def variants(name):
	cross = get_config(name)
	return list(cross.keys())


def contexts():
	return [ BuildContext, CleanContext, InstallContext, UninstallContext, CodeblocksContext, MakeFileContext, EclipseContext ]

