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

REMARKS:
Supports export of C/C++ projects using GCC / MinGW only. CygWin is NOT supported!

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
			Project(bld, tgen).export()
			CDTProject(bld, tgen).export()


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
			Project(bld, tgen).clean()
			CDTProject(bld, tgen).clean()


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


def is_subdir(child, parent, follow_symlinks=True):
	'''Returns True when child is a sub directory of parent.
	'''
	if follow_symlinks:
		parent = os.path.realpath(parent)
		child = os.path.realpath(child)
	return child.startswith(parent)


class EclipseProject(object):
	'''Abstract class for exporting *Eclipse* project files.

	:param bld: a *waf* build instance from the top level *wscript*.
	:type bld: waflib.Build.BuildContext

	:param tgen: Task generator that contains all information of the task to be
				converted and exported to the *Eclipse* project.
	:type tgen:	waflib.Task.TaskGen
	'''
	def __init__(self, bld, tgen, fname, template):
		self.bld = bld
		self.tgen = tgen
		self.fname = fname
		self.template = template
		self.appname = getattr(Context.g_module, Context.APPNAME)

	def export(self):
		content = self.xml_clean(self.get_content())
		node = self.make_node()
		node.write(content)
		Logs.pprint('YELLOW', 'exported: %s' % node.abspath())

	def cleanup(self):
		node = self.find_node()
		if node:
			node.delete()
			Logs.pprint('YELLOW', 'removed: %s' % node.abspath())

	def find_node(self):
		name = self.get_fname()   
		return self.bld.srcnode.find_node(name)

	def make_node(self):
		name = self.get_fname()   
		return self.bld.srcnode.make_node(name)

	def get_fname(self):
		'''returns file name including relative path.'''
		return '%s/%s' % (self.tgen.path.relpath().replace('\\', '/'), self.fname)

	def get_name(self):
		'''returns functional name of task generator.'''
		return self.tgen.get_name()

	def xml_clean(self, content):
		s = minidom.parseString(content).toprettyxml(indent="\t")
		lines = [l for l in s.splitlines() if not l.isspace() and len(l)]
		lines = self.comments + lines[1:] + ['']
		return '\n'.join(lines)

	def get_root(self):
		'''get XML root from template or file.'''
		fname = self.get_fname()
		if os.path.exists(fname):
			tree = ElementTree.parse(fname)
			root = tree.getroot()
		else:
			root = ElementTree.fromstring(self.template)
		return root

	def get_content(self):
		'''Abstract, to be defined in concrete classes:
		returns XML file contents as string.
		'''
		return None


class Project(EclipseProject):
	'''Class for exporting *Eclipse* '.project' files.

	:param bld: a *waf* build instance from the top level *wscript*.
	:type bld: waflib.Build.BuildContext

	:param tgen: Task generator that contains all information of the task to be
				converted and exported to the *Eclipse* project.
	:type tgen:	waflib.Task.TaskGen
	'''
	def __init__(self, bld, tgen):
		super(Project, self).__init__(bld, tgen, '.project', ECLIPSE_PROJECT)
		self.comments = ['<?xml version="1.0" encoding="UTF-8"?>']

	def get_content(self):
		root = self.get_root()
		root.find('name').text = self.get_name()
		self.add_projects(root)
		self.add_natures(root)
		return ElementTree.tostring(root)

	def add_projects(self, root):
		projects = root.find('projects')
		uses = getattr(self.tgen, 'use', [])
		for project in projects.findall('project'):
			if project.text in uses: uses.remove(project.text)
		for use in uses:
			ElementTree.SubElement(projects, 'project').text = use

	def add_natures(self, root):
		if 'cxx' not in self.tgen.features:
			return
		natures = root.find('natures')
		ccnature = 'org.eclipse.cdt.core.ccnature'
		for nature in natures.findall('nature'):
			if nature.text == ccnature:
				return
		element = ElementTree.SubElement(natures, 'nature')
		element.text = ccnature


class CDTProject(EclipseProject):
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
		super(CDTProject, self).__init__(bld, tgen, '.cproject', ECLIPSE_CDT_PROJECT)
		self.comments = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>','<?fileVersion 4.0.0?>']
		self.cdt = {}
		if set(('cprogram', 'cxxprogram')) & set(tgen.features):
			self.cdt['ext'] = 'exe'
			self.cdt['kind'] = 'Executable'
		if set(('cshlib', 'cxxshlib')) & set(tgen.features):
			self.cdt['ext'] = 'so'
			self.cdt['kind'] = 'Shared Library'			
		if set(('cstlib', 'cxxstlib')) & set(tgen.features):
			self.cdt['ext'] = 'lib'
			self.cdt['kind'] = 'Static Library'
		self.cdt['cc'] = 'gnu%s' % ('.mingw' if sys.platform == 'win32' else '')
		self.cdt['build'] = 'debug' if '-g' in tgen.env.CFLAGS else 'release'
		self.cdt['parent'] = 'cdt.managedbuild.config.%s.%s' % (self.cdt['cc'], self.cdt['build'])
		self.cdt['instance'] = '%s.%s' % (self.cdt['parent'], self.get_uuid())
		self.cdt['name'] = '%s_%s' % (tgen.env.DEST_OS.lower(), tgen.env.DEST_CPU.lower())

	def get_uuid(self):
		uuid = codecs.encode(os.urandom(4), 'hex_codec')
		return int(uuid, 16)

	def get_content(self):
		root = self.get_root()

		for module in root.findall('storageModule'):
			if module.get('moduleId') == 'org.eclipse.cdt.core.settings':
				self.update_cdt_core_settings(module)
			if module.get('moduleId') == 'cdtBuildSystem':
				self.update_buildsystem(module)
			if module.get('moduleId') == 'refreshScope':
				self.update_refreshscope(module)

		for module in root.findall('storageModule'):
			if module.get('moduleId') == 'scannerConfiguration':
				self.update_scannerconfiguration(module)
		return ElementTree.tostring(root)

	def update_cdt_core_settings(self, module):
		'''TODO: contains bulk of project '''
		pass

	def update_buildsystem(self, module):
		project = module.find('project')
		if not project:
			project = ElementTree.SubElement(module, 'project')

		pid = '%s.cdt.managedbuild.target.%s.%s' % (self.tgen.get_name(), self.cdt['cc'], self.cdt['ext'])		
		for element in module.findall('project'):
			if element.get('id').startswith(pid):
				return
		project.set('id', '%s.%s' % (pid, self.get_uuid()))
		project.set('name', self.cdt['kind'])
		project.set('projectType', 'cdt.managedbuild.target.%s.%s' % (self.cdt['cc'], self.cdt['ext']))


	def update_refreshscope(self, module):
		name = self.cdt['name']
		for configuration in module.findall('configuration'):
			if configuration.get('configurationName') == name:
				return
		configuration = ElementTree.SubElement(module, 'configuration')
		configuration.set('configurationName', name)
		resource = ElementTree.SubElement(configuration, 'resource')
		resource.set('resourceType', 'PROJECT')
		resource.set('workspacePath', '/%s' % self.tgen.get_name())

	def update_scanner_configuration(self, module):
		'''TODO: depends on CDT core settings '''
		pass


ECLIPSE_PROJECT = \
'''<?xml version="1.0" encoding="UTF-8"?>
<projectDescription>
	<name></name>
	<comment></comment>
	<projects/>
	<buildSpec>
		<buildCommand>
			<name>org.eclipse.cdt.managedbuilder.core.genmakebuilder</name>
			<triggers>clean,full,incremental,</triggers>
			<arguments>
			</arguments>
		</buildCommand>
		<buildCommand>
			<name>org.eclipse.cdt.managedbuilder.core.ScannerConfigBuilder</name>
			<triggers>full,incremental,</triggers>
			<arguments>
			</arguments>
		</buildCommand>
	</buildSpec>
	<natures>
		<nature>org.eclipse.cdt.core.cnature</nature>
		<nature>org.eclipse.cdt.managedbuilder.core.managedBuildNature</nature>
		<nature>org.eclipse.cdt.managedbuilder.core.ScannerConfigNature</nature>
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
	<storageModule moduleId="org.eclipse.cdt.make.core.buildtargets"/>
	<storageModule moduleId="refreshScope" versionNumber="2">
	</storageModule>
</cproject>
'''


