#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

'''
Summary
-------
Setup and configure multiple C/C++ build environments and configure
common C/C++ tools used when cross-compiling. When using this module
the following tools will be loaded and configured autmatically as well:

- cmake
- codeblocks
- cppcheck
- doxygen
- eclipse
- gnucc
- indent
- makefile
- msdev
- package
- tree


Usage
-----
The code snippet below provides an example of how a complete build environment
can be created allowing you to build, not only for the host system, but also 
for one or more target platforms using a C/C++ cross compiler::

	#!/usr/bin/env python
	# -*- encoding: utf-8 -*-

	import os, waftools
	from waftools import ccross

	top = '.'
	out = 'build'
	prefix = 'output'
	ccrossini = os.path.abspath('ccross.ini').replace('\\', '/')

	VERSION = '0.0.1'
	APPNAME = 'cross-test'

	def options(opt):
		opt.add_option('--prefix', dest='prefix', default=prefix, help='installation prefix [default: %r]' % prefix)
		opt.load('ccross', tooldir=waftools.location)

	def configure(conf):
		conf.load('ccross')

	def build(bld):
		ccross.build(bld, trees=['components'])

	for var in ccross.variants(ccrossini):
		for ctx in ccross.contexts():
			name = ctx.__name__.replace('Context','').lower()
			class _t(ctx):
				__doc__ = "%ss '%s'" % (name, var)
				cmd = name + '_' + var
				variant = var

When loading and configuring the *ccross* tool, as shown in the example above, all 
required C/C++ tools for each build environment variant (i.e. native or cross-
compile) will be loaded and configured as well; e.g. compilers, makefile-, cmake-, 
eclipse-, codeblocks- and msdev exporters, cppcheck source code checking, doxygen 
documentation creation will be available for each build variant. Cross compile 
build environments can be specified in a seperate .INI file (named ccross.ini 
in the example above) using following syntax::

	[arm]
	prefix = arm-linux-gnueabihf

The section name, *arm* in the example above, specifies the name of the cross-compile
build environment variant. The prefix will be in used to create the concrete names of
the cross compile toolchain binaries::

	AR	= arm-linux-gnueabihf-ar
	CC	= arm-linux-gnueabihf-gcc
	CXX	= arm-linux-gnueabihf-g++

Concrete build scripts (i.e. wscript files) for components can be placed somewhere 
within the *components* sub-directory. Any top level wscript file of a tree (being 
*components* in this example) will be detected and incorporated within the build 
environment. Any wscript files below those top level script files will have to be 
included using the *bld.recurse('../somepath')* command from the top level script 
of that tree.
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
	opt.load('indent', tooldir=waftools.location)


def configure(conf):
	conf.check_waf_version(mini='1.7.6')
	prefix = str(conf.env.PREFIX).replace('\\', '/')
	cross = get_config(conf.env.CCROSSINI)

	for name, ini in cross.items(): # setup cross compile environment(s)
		conf.setenv(name)
		conf.env.CCROSS = cross
		conf.env.PREFIX = '%s/opt/%s' % (prefix, name)
		conf.env.BINDIR = '%s/opt/%s/bin' % (prefix, name)
		conf.env.LIBDIR = '%s/opt/%s/lib' % (prefix, name)
		cc = '%s-gcc' % (ini['prefix'])
		conf.find_program(cc)
		conf.env.CC = cc
		conf.env.CXX = '%s-g++' % (ini['prefix'])
		conf.env.AR = '%s-ar' % (ini['prefix'])
		conf.load('compiler_c')
		conf.load('compiler_cxx')
		conf.load('cppcheck')
		conf.load('codeblocks')
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
	conf.load('indent')


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
	'''Returns dictionary of cross-compile build environments. Dictionary key name
	depict the environment name (i.e. variant name).
	
	:param name: Complete path to the config.ini file
	:type name: str
	'''
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
	'''Returns a list of variant names; i.e. a list of names for build environments 
	that have been defined in the 'ccross.ini' configuration file.
	
	:param name: Complete path to the config.ini file
	:type name: str
	'''
	cross = get_config(name)
	return list(cross.keys())


def contexts():
	'''Returns a list of cross-compile build contexts.
	
	:param name: Complete path to the config.ini file
	:type name: list of waflib.Build.BuildContext
	'''
	return [ BuildContext, CleanContext, InstallContext, UninstallContext, CodeblocksContext, MakeFileContext, EclipseContext ]

