#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

import os

version = "0.1.4"
location = os.path.dirname(__file__)


def options(opt):
	'''Add default (C/C++) command line options.
	
	:param opt: options context 
	:type opt: waflib.Options.OptionsContext
	'''
	opt.add_option('--check_c_compiler', dest='check_c_compiler', default='gcc', action='store', help='Selects C compiler type.')
	opt.add_option('--check_cxx_compiler', dest='check_cxx_compiler', default='gxx', action='store', help='Selects C++ compiler type.')
	opt.add_option('--debug', dest='debug', default=False, action='store_true', help='build with debug information.')


def configure(conf):
	'''Configures general environment settings; e.g. set default C/C++ compiler flags and defines 
	based on the value of the command line --debug option.
	
	:param conf: configuration context 
	:type conf: waflib.Configure.ConfigurationContext
	
	'''
	if conf.options.debug:
		flags = ['-Wall', '-g', '-ggdb']
		defines = []
	else:
		flags = ['-Wall', '-O3']
		defines = ['NDEBUG']

	for cc in ('CFLAGS', 'CXXFLAGS'):
		for flag in flags:
			conf.env.append_unique(cc, flag)
	for define in defines:
		conf.env.append_unique('DEFINES', define)


def get_scripts(top, name):
	'''Returns a list of top level paths containing the specified file name.
	
	:param: top: root where the search should be started.
	:type top: str
	:param: name: name of the file to be found.
	:type name: str
	'''
	locations = []
	for cwd, _, files in os.walk(top):
		for f in files:
			if os.path.basename(f) != name:
				continue
			locations.append(cwd)
	scripts = []
	for loc in locations:
		if any(os.path.dirname(loc).endswith(t) for t in locations):
			continue
		scripts.append(loc)
	return scripts

