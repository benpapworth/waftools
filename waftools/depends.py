#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com


'''
Description
-----------
Display dependencies of task generators to other taskgenerators as well as any other
(external) node or library dependency.

Example below presents an abbreviated output from the 'depends' command::

		depends tree(cxxstlib):
		+-cxxstlib (t)
		depends tree(cxxprogram):
		+-cxxprogram (t)
			+-libcxxstlib.a (n)
			|    (D:\workspace\waftools\test\build\components\cxxlib\static\libcxxstlib.a)
			+-cxxshlib-1.dll (n)
			|    (D:\workspace\waftools\test\build\components\cxxlib\shared\cxxshlib-1.dll)
			+-libcxxshlib.dll.a (n)
			|    (D:\workspace\waftools\test\build\components\cxxlib\shared\libcxxshlib.dll.a)
			|
			+-cxxstlib (t)
			|
			+-cxxshlib (t)			
		...
		...
		+-cxxshlib (t)
		depends tree(cstlib):
		+-cstlib (t)
		depends tree(cxxhello):
		+-cxxhello (t)
		
		
		DESCRIPTION
		t   = build task
		n   = node (file/directory/build output)
		lib = external library
		
		'depends' finished successfully (0.340s)

Usage
-----
In order to use this waftool simply add it to the 'options' and 'configure' 
functions of your main *waf* script as shown in the example below::

	import os
	import waftools

	def options(opt):
		opt.load('depends', tooldir=os.path.dirname(waftools.__file__))

	def configure(conf):
		conf.load('depends')

When configured as shown in the example above, the depends can be issued on
targets, single or range of  targets::

	waf depends --targets=blib

'''

from waflib import Logs, Build, Scripting, Errors


class DependsContext(Build.BuildContext):
	'''display dependencies t=task, n=node(file/dir), lib=(external library)'''
	cmd = 'depends'
	fun = Scripting.default_cmd

	def _get_task_generators(self):
		'''Returns a list of task generators for which the command should be executed
		
		@return: Returns either the list of target as specified on command line (i.e. 
		--targets=...) or a list of all targets.
		'''
		taskgenerators = []
		if len(self.targets):
			for target in self.targets.split(','):
				taskgen = self.get_tgen_by_name(target)
				taskgenerators.append(taskgen)
		else:
			for group in self.groups:
				for taskgen in group:
					taskgenerators.append(taskgen)		
		return list(set(taskgenerators[:]))

	def execute(self):
		'''Entry point when executing the command (self.cmd).
		
		Displays a list of dependencies for each specified task
		'''
		self.restore()
		if not self.all_envs:
			self.load_envs()
		self.recurse([self.run_dir])

		for taskgen in self._get_task_generators():
			taskgen.post()
			Logs.info("depends tree(%s):" % taskgen.name)
			self.print_tree(taskgen, '    ')
		self.print_legend()

	def get_childs(self, parent):
		'''Returns a list of task generator used by the parent.
		
		@param parent: Task generator
		@return: List of task generators
		'''
		childs = []
		names = parent.to_list(getattr(parent, 'use', []))
		for name in names:
			try:
				child = self.get_tgen_by_name(name)
				childs.append(child)
			except Errors.WafError:
				Logs.warn("Skipping dependency '%s'; Task does not exist" % name)				
		return childs

	def print_tree(self, parent, padding):
		'''Display task dependencies in a tree like manner
		
		@param parent: Task generator for which the dependencies should be listed
		@param padding: Printing left side offset
		'''
		Logs.warn('%s+-%s (t)' % (padding[:-1], parent.name))
		padding = padding + ' '
		for task in parent.tasks:
			for node in task.dep_nodes:
				Logs.warn('%s+-%s (n)' % (padding, node))
				Logs.warn('%s|    (%r)' % (padding, node))

		for lib in parent.to_list(getattr(parent,'lib', [])):
			Logs.warn('%s+-%s (lib)' % (padding,lib))
 
		childs = self.get_childs(parent)
		count = 0
		for child in childs:
			count += 1
			Logs.warn('%s|' % padding)
			if count == len(childs):
				self.print_tree(child, padding + ' ')
			else:
				self.print_tree(child, padding + '|')

	def print_legend(self):
		'''Displays description for the depends result.'''
		Logs.info('')
		Logs.info('')
		Logs.info('DESCRIPTION')
		Logs.info('t   = build task')
		Logs.info('n   = node (file/directory/build output)')
		Logs.info('lib = external library')
		Logs.info('')
