#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

'''
Summary
-------
Provides conversion and export of C/C++ programs, static- and shared libraries
to foreign build system formats (e.g. make) as well as projects and workspaces
for C/C++ integrated development environments (e.g. Eclipse).

Description
-----------
This module can be used to convert and export *waf* project data of C/C++ 
programs, static- and shared libraries into one or more of the following 
formats:
- Makefiles (GNU/MinGW/CygWin),
- CMake makefiles,
- Code::Blocks projects and workspaces,
- Eclipse CDT projects
- Microsoft Visual Studio

Once exported to Make and/or CMake makefiles, all exported (C/C++) tasks can be
build without any further need for, or dependency, to the *waf* build system 
itself. Exporting to these formats can be beneficial when you need to tie your
build environment to some external system, a CI build system for instance, that
is unable to interact with *waf*, or just does a poor job at it. In this case 
you can use *waf* as a kind of templating system, make use of its versatility 
and export new makefiles whenever needed. Note that in such a case the exported
makefiles will merely act as intermediate files that shouldn't be altered
manually; any changes to the build environment needed should made to *wscripts*
within *waf* build system from they have been generated.
Of course one could also use the export as last resort in order to stop using
*waf* as build system altogether and just convert all C/C++ tasks from the *waf*
build environment into Make and/or CMake makefiles.

When exporting C/C++ tasks to integrated developments environments (e.g. 
Eclipse), data will be converted and exported such, that it will reflect the 
structure, relations (dependencies) and environment variables as defined within
the *waf* build system as much as possible. This however will be done such that
the generated project files and workspaces will have the same structure and 
content as one would expect when using these files. When exporting to Eclipse,
for instance, all project files will contain CDT project data; compilation and 
linking will be carried out by the CDT engine itself. In most cases the
exported project files and workspaces for the integrated development 
environements will also contain some special build targets that will allow you
to execute *waf* commands from within those IDE's.

Usage
-----
Tasks can be exported to codeblocks using the *export* command, as shown in the 
example below::

        $ waf export --codeblocks

Exported project files, workspaces and makefiles can be removed in one go using 
the *clean* option::

        $ waf export --clean --codeblocks

Note that only the formats that have been selected will be cleaned; i.e. 
exported files from formats not selected will not be removed.
'''

import os
from waflib import Build, Logs, Scripting, Task, Context
import waftools
from waftools import makefile
from waftools import codeblocks
from waftools import eclipse
from waftools import cmake
from waftools import msdev


def options(opt):
	'''Adds command line options to the *waf* build environment 

	:param opt: Options context from the *waf* build environment.
	:type opt: waflib.Options.OptionsContext
	'''
	opt.add_option('--clean', dest='clean', default=False, action='store_true', help='delete exported files')

	codeblocks.options(opt)
	eclipse.options(opt)
	makefile.options(opt)
	cmake.options(opt)
	msdev.options(opt)


def configure(conf):
	'''Method that will be invoked by *waf* when configuring the build 
	environment.
	
	:param conf: Configuration context from the *waf* build environment.
	:type conf: waflib.Configure.ConfigurationContext
	'''
	codeblocks.configure(conf)
	eclipse.configure(conf)
	makefile.configure(conf)
	cmake.configure(conf)
	msdev.configure(conf)


def task_process(task):
	'''Collects information of build tasks duing the build process.

	:param task: A concrete task (e.g. compilation of a C source file
				that is bing processed.
	:type task: waflib.Task.TaskBase
	'''
	if not hasattr(task, 'cmd'):
		return
	task.cmd = [arg.replace('\\', '/') for arg in task.cmd]
	gen = task.generator
	bld = task.generator.bld
	if gen not in bld.components:
		bld.components[gen] = [task]
	else:
		bld.components[gen].append(task)


def build_postfun(bld):
	'''Will be called by the build environment after all tasks have been
	processed.

	Converts all collected information from task, task generator and build
	context and converts most used info to an Export class. And finally 
	triggers the actual export modules to start the export process on 
	available C/C++ build tasks.
	
	:param task: A concrete task (e.g. compilation of a C source file
				that is bing processed.
	:type task: waflib.Task.TaskBase
	'''
	bld.export = Export(bld)

	if bld.options.clean:
		codeblocks.cleanup(bld)
		eclipse.cleanup(bld)
		makefile.cleanup(bld)
		cmake.cleanup(bld)
		msdev.cleanup(bld)

	else:
		codeblocks.export(bld)
		eclipse.export(bld)
		makefile.export(bld)
		cmake.export(bld)
		msdev.export(bld)


class ExportContext(Build.BuildContext):
	'''Exports and converts tasks to external formats (e.g. makefiles, 
	codeblocks, msdev, ...).
	'''
	fun = 'build'
	cmd = 'export'

	def execute(self, *k, **kw):
		'''Executes the *export* command.

		The export command installs a special task process method
		which enables the collection of tasks being executed (i.e.
		the actual command line being executed). Furthermore it 
		installs a special *post_process* methods that will be called
		when the build has been completed (see build_postfun).

		Note that before executing the *export* command, a *clean* command
		will forced by the *export* command. This is needed in order to
		(re)start the task processing sequence.
		
		TODO:
		This introduces way too much time since it requires a rebuild when 
		exporting... HOWEVER for the makefile export it is needed since it
		parses the command line result.		
		'''
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
		def process(task):
			old_process(task)
			task_process(task)
		Task.TaskBase.process = process

		def postfun(bld):
			if not len(bld.components):
				Logs.warn('export failed: no targets found!')
			else:
				build_postfun(bld)
		super(ExportContext, self).add_post_fun(postfun)

		Scripting.run_command('clean')
		super(ExportContext, self).execute(*k, **kw)


class Export(object):
	'''Class that collects and converts information from the build 
	context (e.g. convert back- into forward slashes).

	:param bld: a *waf* build instance from the top level *wscript*.
	:type bld: waflib.Build.BuildContext
	'''
	def __init__(self, bld):
		self.version = waftools.version
		self.wafversion = Context.WAFVERSION
		try:
			self.appname = getattr(Context.g_module, Context.APPNAME)
		except AttributeError:
			self.appname = os.path.basename(bld.path.abspath())
		try:
			self.appversion = getattr(Context.g_module, Context.VERSION)
		except AttributeError:
			self.appversion = ""
		self.prefix = bld.env.PREFIX		
		try:
			self.top = os.path.abspath(getattr(Context.g_module, Context.TOP))
		except AttributeError:
			self.top = str(bld.path.abspath())
		try:
			self.out = os.path.abspath(getattr(Context.g_module, Context.OUT))
		except AttributeError:
			self.out = os.sep.join([self.top, 'build'])

		self.bindir = bld.env.BINDIR
		self.libdir = bld.env.LIBDIR
		ar = bld.env.AR
		if isinstance(ar, list):
			ar = ar[0]
		self.ar = ar
		try:
			self.cc = bld.env.CC[0]
		except IndexError:
			self.cc = 'gcc'
		try:
			self.cxx = bld.env.CXX[0]
		except IndexError:
			self.cxx = 'g++'
		self.rpath = ' '.join(bld.env.RPATH)
		self.cflags = ' '.join(bld.env.CFLAGS)
		self.cxxflags = ' '.join(bld.env.CXXFLAGS)
		self.defines = ' '.join(bld.env.DEFINES)
		self.dest_cpu = bld.env.DEST_CPU
		self.dest_os = bld.env.DEST_OS
		self._clean_os_separators()

	def _clean_os_separators(self):
		'''Replace all backward stabbing slashes with forward ones.'''
		for attr in self.__dict__:
			val = getattr(self, attr)
			if isinstance(val, str):
				val = val.replace('\\', '/')
				setattr(self, attr, val)

