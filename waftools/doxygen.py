#! /usr/bin/env python
# -*- coding: utf-8 -*-


'''
DESCRIPTION
-----------
This module contains a wrapper around doxygen; the de facto standard 
tool for generating documentation from annotated C/C++ sources. Doxygen
is part of many linux distributions (e.g. Ubuntu, Fedora, ..) but can 
also be found at:
    "http://www.doxygen.org/"

In order to start generating documentation of C/C++ source code simply 
issue the following command:
    "waf doxygen"

Note that in contrast to the standard doxygen module this module will only 
generate documentation for shared- and static C/C++ libraries; i.e. 
documentation for programs will not be generated.

When needed the generation of documentation for a specific task can be
skipped by adding the feature 'doxygen_skipme' to the task, as presented
in the example below:

   bld.shlib(   ...,
                doxygen_skipme = True,
                ...
    )

For each C/C++ static- and shared library task doxygen will store the
documentation results in:
    "reports/doxygen/<task-name>"

TODO
----
Create general index page containing links to index pages of 
generated components.
'''

import os, subprocess, time, re, datetime
from waflib.Build import BuildContext
from waflib import Utils, TaskGen, Logs, Scripting, Context


def options(opt):
	opt.add_option('--doxygen-output', dest='doxygen_output', default='reports/doxygen',
		action='store', help='defines destination path for generated DoxyGen files')

	opt.add_option('--doxygen-config', dest='doxygen_config', default='resources/doxy.config',
		action='store', help='complete path to doxygen configuration file')

 
def configure(conf):
	conf.find_program('doxygen', var='DOXYGEN')
	conf.env.DOXYGEN_OUTPUT = conf.options.doxygen_output
	conf.env.DOXYGEN_CONFIG = conf.options.doxygen_config


class DoxygenContext(BuildContext):
	'''Base class for generating source code documentation using doxygen.'''
	cmd = 'doxygen'
	fun = Scripting.default_cmd

	def execute(self):
		'''Enrty point for the doxygen source code document generator.
		
		iterate through all groups(g) and task generators (t) and generate
		doxygen report for C and C++ tasks.
		'''
		self.restore()
		if not self.all_envs:
			self.load_envs()
		self.recurse([self.run_dir])

		for group in self.groups:
			for tgen in group:
				if self.targets == '':
					skipme = getattr(tgen, 'doxygen_skipme', False)
					if skipme:
						continue

				elif tgen.name not in self.targets.split(','):
					continue

				doxygen = self._get_doxygen_conf(tgen)
				if doxygen is not None:
					self._exec_doxygen(tgen, doxygen)

	def _get_doxygen_conf(self, tgen):
		'''Returns a dictionary containing input data for the doxygen
		source code documentation tool
		
		Returns None if no documentation should be generated for the task 
		generator.
		'''
		if not isinstance(tgen, TaskGen.task_gen):
			return None

		tgen.post()
		targets = self.options.targets
		if targets != '' and tgen.name not in targets:
			return None

		features = Utils.to_list(getattr(tgen, 'features', ''))
		if not set(['c', 'cxx']) & set(features):
			return None

		# create list inputs files for the documentation (paths to files)
		input = []
		sources = Utils.to_list(getattr(tgen, 'source', ''))
		for source in sources:
			src = './%s' % os.path.dirname(source.relpath()).replace('\\','/')
			input.append(src)   

		# create list of include paths
		tgen_path = './%s' % tgen.path.relpath().replace('\\','/')
		include_path = []
		includes = tgen.to_incnodes(tgen.to_list(getattr(tgen, 'includes', [])) + tgen.env['INCLUDES'])
		for include in includes:
			# add include files from component itself to input
			inc = './%s' % include.relpath().replace('\\', '/')
			if inc.startswith(tgen_path):
				input.append(inc)
			else:
				include_path.append(inc)

		# remove duplicates and replace '\' with '/'
		input = list(set(input[:]))
		include_path = list(set(include_path[:]))

		# create a list of defines
		defines = Utils.to_list(getattr(tgen, 'defines', ''))

		# get the application name and version from the main script
		appname = getattr(Context.g_module, Context.APPNAME, os.path.basename(self.srcnode.abspath()))
		version = getattr(Context.g_module, Context.VERSION, os.path.basename(self.srcnode.abspath()))
		now = datetime.datetime.now()
		
		conf = {}
		conf['PROJECT_NAME']     = tgen.name.upper()
		conf['PROJECT_NUMBER']   = '"%s v%s / %s"' % (appname.upper(), version, now.strftime('%Y-%m-%d'))
		conf['PROJECT_BRIEF']    = '"features: %s"' % ', '.join(features)
		conf['OUTPUT_DIRECTORY'] = '%s/%s' % (self.env.DOXYGEN_OUTPUT, tgen.name)
		conf['INPUT']            = ' '.join(input)
		conf['INCLUDE_PATH']     = ' '.join(include_path)
		conf['PREDEFINED']       = ' '.join(defines)
		return conf

	def _exec_doxygen(self, tgen, conf):
		'''Generate source code documentation for the given task generator.'''
		Logs.info("Generating documentation for '%s'" % tgen.name)

		# open template configuration and read as string
		name = self.env.DOXYGEN_CONFIG
		if not os.path.exists(name):
			name = '%s/doxy.config' % os.path.dirname(__file__)
		f = open(name, 'r')
		s = f.read()
		f.close()

		# write configuration key,value pairs into template string
		for key,value in conf.items():
			s = re.sub('%s\s+=.*' % key, '%s = %s' % (key, value), s)

		# create base directory for storing reports
		doxygen_path = self.env.DOXYGEN_OUTPUT
		if not os.path.exists(doxygen_path):
			os.makedirs(doxygen_path)

		# write component configuration to file and doxygen on it
		config = '%s/doxy-%s.config' % (doxygen_path, tgen.name)
		f = open(config, 'w+')
		f.write(s)
		f.close()
		cmd = '%s %s' % (self.env.DOXYGEN, config)
		self.cmd_and_log(cmd)

