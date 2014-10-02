#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

'''
Summary
-------
Exports and converts *waf* project data, for C/C++ programs, static- and shared
libraries, into **Eclipse** *CDT* project files (.cbp) and workspaces 
(codeblock.workspace).
**Eclipse** is an open source integrated development environment, which can be, 
amongst others, used for development of C/C++ programs. 

See https://www.eclipse.org and https://www.eclipse.org/cdt for a more detailed 
description on how to install and use it for your particular Desktop environment.

Usage
-----
**Eclipse** project and workspace files can be exported using the *eclipse* 
command, as shown in the example below::

        $ waf eclipse

When needed, exported **Eclipse** project- and workspaces files can be 
removed using the *clean* command, as shown in the example below::

        $ waf eclipse --clean
'''

# TODO: add detailed description for 'eclipse' module
# TODO: add support for multiple variant (e.g. cross-compile)


import sys
import os
import re
import codecs
import xml.etree.ElementTree as ElementTree
from xml.dom import minidom
import waflib
from waflib import Utils, Logs, Errors, Context
from waflib.Build import BuildContext


def options(opt):
	'''Adds command line options to the *waf* build environment 

	:param opt: Options context from the *waf* build environment.
	:type opt: waflib.Options.OptionsContext
	'''
	opt.add_option('--eclipse', dest='eclipse', default=False, action='store_true', help='select Eclipse for export/import actions')
	opt.add_option('--clean', dest='clean', default=False, action='store_true', help='delete exported files')


def configure(conf):
	'''Method that will be invoked by *waf* when configuring the build 
	environment.
	
	:param conf: Configuration context from the *waf* build environment.
	:type conf: waflib.Configure.ConfigurationContext
	'''
	pass


class EclipseContext(BuildContext):
	'''export C/C++ tasks to Eclipse CDT projects.'''
	cmd = 'eclipse'

	def execute(self):
		'''Will be invoked when issuing the *eclipse* command.'''
		self.restore()
		if not self.all_envs:
			self.load_envs()
		self.recurse([self.run_dir])
		self.pre_build()

		for group in self.groups:
			for tgen in group:
				try:
					f = tgen.post
				except AttributeError:
					pass
				else:
					f()
		try:
			self.get_tgen_by_name('')
		except Exception:
			pass
		
		self.eclipse = True
		if self.options.clean:
			cleanup(self)
		else:
			export(self)
		self.timer = Utils.Timer()


def get_targets(bld):
	'''Returns a list of user specified build targets or None if no specific
	build targets has been selected using the *--targets=* command line option.

	:param bld: a *waf* build instance from the top level *wscript*.
	:type bld: waflib.Build.BuildContext
	:returns: a list of user specified target names (using --targets=x,y,z) or None
	'''
	if bld.targets == '':
		return None
	
	targets = bld.targets.split(',')
	deps = []
	for target in targets:
		uses = Utils.to_list(getattr(bld.get_tgen_by_name(target), 'use', None))
		if uses:
			deps += uses
	targets += list(set(deps))
	return targets


def export(bld):
	'''Generates Eclipse CDT projects for each C/C++ task.

	Also generates a top level Eclipse PyDev project
	for the WAF build environment itself.
	Warns when multiple task have been defined in the same,
	or top level, directory.

	:param bld: a *waf* build instance from the top level *wscript*.
	:type bld: waflib.Build.BuildContext
	'''
	if not bld.options.eclipse and not hasattr(bld, 'eclipse'):
		return

	bld.workspace_loc = get_workspace_loc(bld)
	detect_project_duplicates(bld)
	targets = get_targets(bld)

	for tgen in bld.task_gen_cache_names.values():
		if targets and tgen.get_name() not in targets:
			continue
		if set(('c', 'cxx')) & set(getattr(tgen, 'features', [])):
			project = CDTProject(bld, tgen)
			project.export()


def cleanup(bld):
	'''Removes all generated Eclipse project- and launcher files

	:param bld: a *waf* build instance from the top level *wscript*.
	:type bld: waflib.Build.BuildContext
	'''
	if not bld.options.eclipse and not hasattr(bld, 'eclipse'):
		return

	targets = get_targets(bld)

	for tgen in bld.task_gen_cache_names.values():
		if targets and tgen.get_name() not in targets:
			continue
		if set(('c', 'cxx')) & set(getattr(tgen, 'features', [])):
			project = CDTProject(bld, tgen)
			project.cleanup()


def get_workspace_loc(bld):
	'''Detect and save the top level directory containing Eclipse workspace
	settings.
	'''
	path = bld.path.abspath()
	while not os.path.exists(os.sep.join((path, '.metadata'))):
		if os.path.dirname(path) == path:
			Logs.warn('WARNING ECLIPSE EXPORT: FAILED TO DETECT WORKSPACE_LOC.')
			return None
		path = os.path.dirname(path)
	return path.replace('\\', '/')


def detect_project_duplicates(bld):
	'''Warns when multiple TaskGen's have been defined in the same directory.

	Since Eclipse works with static project filenames, only one project	per
	directory can be created. If multiple task generators have been defined
	in the same directory (i.e. same wscript) one will overwrite the other(s).
	This problem can only e circumvented by changing the structure of the 
	build environment; i.e. place each single task generator in a seperate 
	directory.
	'''
	locations = { '.': 'waf (top level)' }
	anomalies = {}

	for tgen in bld.task_gen_cache_names.values():
		name = tgen.get_name()
		location = str(tgen.path.relpath()).replace('\\', '/')
		
		if location in locations:
			anomalies[name] = location
		else:
			locations[location] = name

	cnt = len(anomalies.keys())
	if cnt != 0:
		Logs.info('')
		Logs.warn('WARNING ECLIPSE EXPORT: TASK LOCATION CONFLICTS(%s)' % cnt)
		Logs.info('Failed to create project files for:')
		s = ' {n:<15} {l:<40}'
		Logs.info(s.format(n='(name)', l='(location)'))
		for (name, location) in anomalies.items():
			Logs.info(s.format(n=name, l=location))
		Logs.info('')
		Logs.info('TIPS:')
		Logs.info('- use one task per directory/wscript.')
		Logs.info('- don\'t place tasks in the top level directory/wscript.')
		Logs.info('')


def _is_subdir(child, parent, follow_symlinks=True):
	'''Returns True when child is a sub directory of parent.
	'''
	if follow_symlinks:
		parent = os.path.realpath(parent)
		child = os.path.realpath(child)
	return child.startswith(parent)


class Project(object):
	'''Base class for exporting *Eclipse* projects.

	Exports the *Eclipse* *.project* file that is used for all types
	of *Eclipse* projects.

	:param bld: a *waf* build instance from the top level *wscript*.
	:type bld: waflib.Build.BuildContext

	:param tgen: Task generator that contains all information of the task to be
				converted and exported to the *Eclipse* project.
	:type tgen:	waflib.Task.TaskGen
	'''
	def __init__(self, bld, tgen):
		self.bld = bld
		self.appname = getattr(Context.g_module, Context.APPNAME)
		self.tgen = tgen
		self.natures = []
		self.buildcommands = []
		self.comments = ['<?xml version="1.0" encoding="UTF-8"?>']

	def export(self):
		'''Exports an *Eclipse* project or an Eclipse (CDT) launcher.'''
		content = self.xml_clean(self.get_content())
		node = self.make_node()
		node.write(content)
		Logs.pprint('YELLOW', 'exported: %s' % node.abspath())

	def cleanup(self):
		'''Deletes an *Eclipse* project or launcher.'''
		node = self.find_node()
		if node:
			node.delete()
			Logs.pprint('YELLOW', 'removed: %s' % node.abspath())

	def get_root(self):
		'''Returns a document root, either from an existing file, or from template.
		'''
		fname = self.get_fname()
		if os.path.exists(fname):
			tree = ElementTree.parse(fname)
			root = tree.getroot()
		else:
			root = ElementTree.fromstring(ECLIPSE_PROJECT)
		return root

	def find_node(self):
		name = self.get_fname()   
		return self.bld.srcnode.find_node(name)

	def make_node(self):
		name = self.get_fname()   
		return self.bld.srcnode.make_node(name)

	def get_fname(self):
		return '%s/.project' % (self.tgen.path.relpath().replace('\\', '/'))

	def get_name(self):
		return self.tgen.get_name()

	def xml_clean(self, content):
		s = minidom.parseString(content).toprettyxml(indent="\t")
		lines = [l for l in s.splitlines() if not l.isspace() and len(l)]
		lines = self.comments + lines[1:] + ['']
		return '\n'.join(lines)

	def get_content(self):
		root = self.get_root()
		name = root.find('name')
		name.text = self.get_name()

		projects = root.find('projects')
		uses = getattr(self.tgen, 'use', [])
		for project in projects.findall('project'):
			if project.text in uses: uses.remove(project.text)
		for use in uses:
			ElementTree.SubElement(projects, 'project').text = use

		buildcommands = list(self.buildcommands)
		buildspec = root.find('buildSpec')
		for buildcommand in buildspec.findall('buildCommand'):
			if buildcommand.text in buildcommands: buildcommands.remove(buildcommand.text)
		
		for buildcommand in buildcommands:
			(name, triggers, arguments) = buildcommand
			element = ElementTree.SubElement(buildspec, 'buildCommand')
			ElementTree.SubElement(element, 'name').text = name
			if triggers is not None:
				ElementTree.SubElement(element, 'triggers').text = triggers
			if arguments is not None:
				element.append(arguments)

		natures = list(self.natures)		
		for nature in root.find('natures').findall('nature'):
			if nature.text in natures: natures.remove(nature.text)			
		for nature in natures:
			element = ElementTree.SubElement(root.find('natures'), 'nature')
			element.text = nature

		return ElementTree.tostring(root)


class CDTProject(Project):
	'''Class for exporting C/C++ task generators to an *Eclipse* *CDT* 
	project.
	When exporting this class exports three files associated with C/C++
	projects::
	
		.project
		.cproject
		target_name.launch

	The first file mostly contains perspective, the second contains the actual
	C/C++ project while the latter is a launcher which can be import into
	*Eclipse* and used to run and/or debug C/C++ programs. 
	
	:param bld: a *waf* build instance from the top level *wscript*.
	:type bld: waflib.Build.BuildContext

	:param tgen: Task generator that contains all information of the task to be
				converted and exported to the *Eclipse* project.
	:type tgen:	waflib.Task.TaskGen
		
	:param project: Reference to *Eclipse* project (which will export the 
					*.project* file.
	:param project: Project
	'''
	def __init__(self, bld, tgen):
		super(CDTProject, self).__init__(bld, tgen)
		self.comments = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>','<?fileVersion 4.0.0?>']
		self.cdt_config = 'cdt.managedbuild.config.gnu'
		if bld.env.DEST_OS == 'win32':
			self.cdt_config += '.mingw'
		self.language = 'c'
		if 'cxx' in tgen.features:
			self.language = 'cpp'
		self.is_program = set(('cprogram', 'cxxprogram')) & set(tgen.features)
		self.is_shlib = set(('cshlib', 'cxxshlib')) & set(tgen.features)
		self.is_stlib = set(('cstlib', 'cxxstlib')) & set(tgen.features)
		self.project = Project(bld, tgen)
		self.project.natures.append('org.eclipse.cdt.core.cnature')
		if self.language == 'cpp':
			self.project.natures.append('org.eclipse.cdt.core.ccnature')
		self.project.natures.append('org.eclipse.cdt.managedbuilder.core.managedBuildNature')
		self.project.natures.append('org.eclipse.cdt.managedbuilder.core.ScannerConfigNature')
		self.project.buildcommands.append(('org.eclipse.cdt.managedbuilder.core.genmakebuilder', 'clean,full,incremental,', None))
		self.project.buildcommands.append(('org.eclipse.cdt.managedbuilder.core.ScannerConfigBuilder', 'full,incremental,', None))

		self.uuid = {
			'debug': self.get_uuid(),
			'release': self.get_uuid(),
			'c_debug_compiler': self.get_uuid(),
			'c_debug_input': self.get_uuid(),
			'c_release_compiler': self.get_uuid(),
			'c_release_input': self.get_uuid(),
			'cpp_debug_compiler': self.get_uuid(),
			'cpp_debug_input': self.get_uuid(),
			'cpp_release_compiler': self.get_uuid(),
			'cpp_release_input': self.get_uuid(),
		}

		if self.is_shlib:
			self.kind_name = 'Shared Library'
			self.kind = 'so'
		elif self.is_stlib:
			self.kind_name = 'Static Library'
			self.kind = 'lib'
		elif self.is_program:
			self.kind_name = 'Executable'
			self.kind = 'exe'

	def export(self):
		'''Exports all *Eclipse* *CDT* project files for an C/C++ task 
		generator at the location of the task generator.
		'''		
		super(CDTProject, self).export()
		self.project.export()

	def cleanup(self):
		'''Deletes all *Eclipse* *CDT* project files associated with an C/C++ 
		task generator at the location of the task generator.
		'''
		super(CDTProject, self).cleanup()
		self.project.cleanup()

	def get_fname(self):
		return '%s/.cproject' % (self.tgen.path.relpath().replace('\\', '/'))

	def get_root(self):
		'''Returns a document root, either from an existing file, or from template.
		'''
		fname = self.get_fname()
		if os.path.exists(fname):
			tree = ElementTree.parse(fname)
			root = tree.getroot()
		else:
			root = ElementTree.fromstring(ECLIPSE_CDT_PROJECT)
		return root

	def get_uuid(self):
		uuid = codecs.encode(os.urandom(4), 'hex_codec')
		return int(uuid, 16)

	def get_content(self):
		root = self.get_root()
		for module in root.findall('storageModule'):
			if module.get('moduleId') == 'org.eclipse.cdt.core.settings':
				pass #self._update_cdt_core_settings(module)
			if module.get('moduleId') == 'cdtBuildSystem':
				pass #self._update_buildsystem(module)
			if module.get('moduleId') == 'scannerConfiguration':
				pass #self._update_scannerconfiguration(module)
			if module.get('moduleId') == 'refreshScope':
				self.update_refreshscope(module)
		return ElementTree.tostring(root)

	def update_refreshscope(self, module):
		name = '%s_%s' % (self.bld.env.DEST_OS.lower(), self.bld.env.DEST_CPU.lower())
		for configuration in module.findall('configuration'):
			if configuration.get('configurationName') == name:
				return
		configuration = ElementTree.SubElement(module, 'configuration')
		configuration.set('configurationName', name)
		resource = ElementTree.SubElement(configuration, 'resource')
		resource.set('resourceType', 'PROJECT')
		resource.set('workspacePath', '/%s' % self.tgen.get_name())


ECLIPSE_PROJECT = \
'''<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
	<name></name>
	<comment></comment>
	<projects/>
	<buildSpec>
	</buildSpec>
	<natures>
	</natures>
</projectDescription>
'''


ECLIPSE_CDT_PROJECT = \
'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<?fileVersion 4.0.0?>
<cproject storage_type_id="org.eclipse.cdt.core.XmlProjectDescriptionStorage">
	<storageModule moduleId="org.eclipse.cdt.core.settings">
	</storageModule>
	<storageModule moduleId="cdtBuildSystem" version="4.0.0">
	</storageModule>
	<storageModule moduleId="scannerConfiguration">
		<autodiscovery enabled="true" problemReportingEnabled="true" selectedProfileId=""/>
	</storageModule>
	<storageModule moduleId="org.eclipse.cdt.core.LanguageSettingsProviders"/>
	<storageModule moduleId="refreshScope" versionNumber="2">
	</storageModule>
</cproject>
'''


