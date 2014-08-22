#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com


'''Selects GNU as default C/C++ compiler and adds common release/debug 
settings.
'''


def options(opt):
	'''Add default (C/C++) command line options for GNU compilers
	
	:param opt: options context 
	:type opt: waflib.Options.OptionsContext
	'''
	opt.add_option('--check_c_compiler', dest='check_c_compiler', default='gcc', action='store', help='Selects C compiler type.')
	opt.add_option('--check_cxx_compiler', dest='check_cxx_compiler', default='gxx', action='store', help='Selects C++ compiler type.')
	opt.add_option('--debug', dest='debug', default=False, action='store_true', help='build with debug information.')


def configure(conf):
	'''Configures general environment settings for GNU compilers; e.g. set
	default C/C++ compiler flags and defines based on the value of the 
	command line --debug option.
	
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

