#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

import os
from waflib import Build, Logs, Scripting, Task, Context
import makefile
import codeblocks

VERSION='0.0.2'

def options(opt):
	opt.add_option('--export-cleanup', 
		dest='export_cleanup', 
		default=False, 
		action='store_true', 
		help='removes files generated by export')

	opt.add_option('--export-codeblocks', 
		dest='export_codeblocks', 
		default=False, 
		action='store_true', 
		help='export codeblocks projects and workspace.')
		
	opt.add_option('--export-makefile', 
		dest='export_makefile', 
		default=False, 
		action='store_true', 
		help='export makefiles.')


def configure(conf): 
	conf.env.EXPORT_FORMATS = []
	if conf.options.export_codeblocks:
		conf.env.append_unique('EXPORT_FORMATS', 'codeblocks')
	if conf.options.export_makefile:
		conf.env.append_unique('EXPORT_FORMATS', 'makefile')


class ExportContext(Build.BuildContext):
	'''exports and converts tasks to external formats (e.g. makefiles, 
	codeblocks, msdev, ...).
	'''
	fun = 'build'
	cmd = 'export'

	def execute(self, *k, **kw):
		self.components = {}

		old_exec = Task.TaskBase.exec_command
		def exec_command(self, *k, **kw):
			ret = old_exec(self, *k, **kw)
			try:
				self.cmd = k[0]
			except IndexError:
				pass
			return ret
		Task.TaskBase.exec_command = exec_command

		old_process = Task.TaskBase.process
		def process(self):
			old_process(self)
			task_process(self)
		Task.TaskBase.process = process

		def postfun(self):
			if not len(self.components):
				Logs.warn('export failed: no targets found!')
			else:
				build_postfun(self)
		super(ExportContext, self).add_post_fun(postfun)

		Scripting.run_command('clean')
		super(ExportContext, self).execute(*k, **kw)


class Export(object):
	def __init__(self, bld):
		self.version = VERSION
		self.wafversion = Context.WAFVERSION
		self.appname = getattr(Context.g_module, Context.APPNAME)
		self.appversion = getattr(Context.g_module, Context.VERSION)
		self.prefix = bld.env.PREFIX
		self.top = os.path.abspath(getattr(Context.g_module, Context.TOP))
		self.out = os.path.abspath(getattr(Context.g_module, Context.OUT))
		self.bindir = bld.env.BINDIR
		self.libdir = bld.env.LIBDIR
		self.ar = os.path.basename(bld.env.AR)
		self.cc = os.path.basename(bld.env.CC[0])
		self.cxx = os.path.basename(bld.env.CXX[0])
		self.rpath = ' '.join(bld.env.RPATH)
		self.cflags = ' '.join(bld.env.CFLAGS)
		self.cxxflags = ' '.join(bld.env.CXXFLAGS)
		self.defines = ' '.join(bld.env.DEFINES)
		self.dest_cpu = bld.env.DEST_CPU
		self.dest_os = bld.env.DEST_OS		
		self._clean_os_separators()


	def _clean_os_separators(self):
		for attr in self.__dict__:
			val = getattr(self, attr)
			if isinstance(val, str):
				val = val.replace('\\', '/')
				setattr(self, attr, val)


def task_process(self):
	if not hasattr(self, 'cmd'):
		return
	self.cmd = [arg.replace('\\', '/') for arg in self.cmd]
	gen = self.generator
	bld = self.generator.bld
	if not bld.components.has_key(gen):
		bld.components[gen] = [self]
	else:
		bld.components[gen].append(self)


def build_postfun(self):
	self.export = Export(self)

	if self.options.export_cleanup:
		makefile.cleanup(self)
		codeblocks.cleanup(self)

	else:
		formats = self.env.EXPORT_FORMATS
		if 'makefile' in formats or self.options.export_makefile:
			makefile.export(self)
	
		if 'codeblocks' in formats or self.options.export_codeblocks:
			codeblocks.export(self)

