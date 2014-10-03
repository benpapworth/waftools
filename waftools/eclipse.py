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
		self.language = 'cpp' if 'cxx' in tgen.features else 'c'
		self.cdt = {}
		if set(('cprogram', 'cxxprogram')) & set(tgen.features):
			self.cdt['ext'] = 'exe'
			self.cdt['kind'] = 'Executable'
			self.cdt['buildArtefactType'] = 'org.eclipse.cdt.build.core.buildArtefactType.exe'
			
		if set(('cshlib', 'cxxshlib')) & set(tgen.features):
			self.cdt['ext'] = 'so'
			self.cdt['kind'] = 'Shared Library'
			self.cdt['buildArtefactType'] = 'org.eclipse.cdt.build.core.buildArtefactType.sharedLib'
			self.cdt['artifactExtension'] = 'dll' if tgen.env.DEST_OS=='win32' else 'so'
			
		if set(('cstlib', 'cxxstlib')) & set(tgen.features):
			self.cdt['ext'] = 'lib'
			self.cdt['kind'] = 'Static Library'
			self.cdt['buildArtefactType'] = 'org.eclipse.cdt.build.core.buildArtefactType.staticLib'
			self.cdt['artifactExtension'] = 'a'
			
		self.cdt['cc'] = 'gnu%s' % ('.mingw' if sys.platform == 'win32' else '')
		self.cdt['build'] = 'debug' if '-g' in tgen.env.CFLAGS else 'release'
		self.cdt['parent'] = 'cdt.managedbuild.config.%s.%s' % (self.cdt['cc'], self.cdt['build'])
		self.cdt['instance'] = '%s.%s' % (self.cdt['parent'], self.get_uuid())
		self.cdt['name'] = '%s_%s' % (tgen.env.DEST_OS, tgen.env.DEST_CPU)
		self.cdt['parser'] = 'org.eclipse.cdt.core.PE' if tgen.env.DEST_OS=='win32' else 'org.eclipse.cdt.core.ELF' 		

		c = 'cdt.managedbuild.tool.gnu.%s.compiler.%s' % (self.language, 'mingw.' if sys.platform=='win32' else '')
		c += '%s.%s' % (self.cdt['ext'], 'debug' if '-g' in tgen.env.CFLAGS else 'release')
		self.cdt['compiler'] = '%s.%s' % (c, self.get_uuid())	
		self.cdt['input'] = 'cdt.managedbuild.tool.gnu.%s.compiler.input.%s' % (self.language, self.get_uuid())

		d = tgen.env.DEST_OS
		c = tgen.env.DEST_CPU
		# TODO: assuming host is i386 only!!!		
		if sys.platform.startswith(d) and c in ('x86_64', 'x86', 'ia'):
			self.cross = False
			self.cdt['toolchain'] = 'cdt.managedbuild.toolchain.%s.%s.%s' % (self.cdt['cc'], self.cdt['build'], self.cdt['ext'])
			self.cdt['platform'] = 'cdt.managedbuild.target.gnu.platform%s.%s.%s' % ('.mingw' if d=='win32' else '', '', '')
		else:
			self.cross = True
			self.cdt['toolchain'] = 'cdt.managedbuild.toolchain.base'
			self.cdt['platform'] = 'cdt.managedbuild.target.gnu.platforms.base'
			self.cdt['archList'] = 'all'
			self.cdt['osList'] = 'linux,hpux,aix,qnx'

		self.cdt['archiver'] = 'cdt.managedbuild.tool.gnu.archiver%s.base' % ('.mingw' if d=='win32' else '')


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
				self.update_scanner_configuration(module)
		return ElementTree.tostring(root)

	def update_cdt_core_settings(self, module):
		cconfig = self.cconfig_get(module)
		if not cconfig:
			cconfig = ElementTree.fromstring(ECLIPSE_CDT_CCONFIGURATION)
			module.append(cconfig)
		self.cconfig_update(cconfig)

	def update_buildsystem(self, module):
		project = module.find('project')
		if project == None:
			project = ElementTree.SubElement(module, 'project')
		ptype = 'cdt.managedbuild.target.%s.%s' % (self.cdt['cc'], self.cdt['ext'])
		
		project.set('id', '%s.%s.%s' % (self.tgen.get_name(), ptype, self.get_uuid()))
		project.set('name', self.cdt['kind'])
		project.set('projectType', ptype)

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
		i = self.cdt['instance']
		c = self.cdt['compiler']
		f = self.cdt['input']
		scanner = ElementTree.SubElement(module, 'scannerConfigBuildInfo')
		scanner.set('instanceId', '%s;%s.;%s;%s' % (i, i, c, f))
		ElementTree.SubElement(scanner, 'autodiscovery', {'enabled': 'true', 'problemReportingEnabled' : 'true', 'selectedProfileId' : ''})

	def	cconfig_get(self, module):
		'''Returns configuration module'''
		for cconfig in module.findall('cconfiguration'):
			if cconfig.get('id') and cconfig.get('id').startswith(self.cdt['parent']):
				for storage in cconfig.findall('storageModule'):
					if storage.get('moduleId') == 'org.eclipse.cdt.core.settings':
						if storage.get('name') == self.cdt['name']:
							return cconfig
		return None

	def	cconfig_update(self, cconfig):
		'''Update configuration module.'''
		cconfig.set('id', self.cdt['instance'])
		for storage in cconfig.findall('storageModule'):
			if storage.get('moduleId') == 'org.eclipse.cdt.core.settings':
				self.cconfig_settings_update(storage)
			if storage.get('moduleId') == 'cdtBuildSystem':
				self.cconfig_buildsystem_update(storage)

	def	cconfig_settings_update(self, storage):
		storage.set('name', self.cdt['name'])
		storage.set('id', self.cdt['instance'])
		extensions = storage.find('extensions')				
		for extension in extensions:
			if extension.get('point') == 'org.eclipse.cdt.core.BinaryParser':
				extension.set('id', self.cdt['parser'])
				return
		extension = ElementTree.SubElement(extensions, 'extension')
		extension.set('point', 'org.eclipse.cdt.core.BinaryParser')
		extension.set('id', self.cdt['parser'])

		settings = storage.find('externalSettings')
		if self.cdt['ext'] == 'exe':
			settings.clear()
		else:
			name = self.tgen.get_name()
			for entry in settings.iter('entry'):
				if entry.get('kind') == 'includePath':
					entry.set('name', '/%s' % name)
				if entry.get('kind') == 'libraryPath':
					entry.set('name', '/%s/%s' % (name, self.cdt['name']))
				if entry.get('kind') == 'libraryFile':
					entry.set('name', '%s' % name)

	def	cconfig_buildsystem_update(self, storage):
		config = storage.find('configuration')
		config.set('name', self.cdt['name'])
		config.set('buildArtefactType', self.cdt['buildArtefactType'])
		if 'artifactExtension' in self.cdt:
			config.set('artifactExtension', self.cdt['artifactExtension'])
		config.set('parent', self.cdt['parent'])
		config.set('id', self.cdt['instance'])
				
		prop = '{0}.{1}={0}.{1}.{3},{0}.{2}={0}.{2}.{3}'.format( \
			'org.eclipse.cdt.build.core', 'buildType', 'buildArtefactType', self.cdt['ext'])
		config.set('buildProperties', prop)
		folder = config.find('folderInfo')
		folder.set('id','%s.' % (self.cdt['instance']))
		self.cconfig_toolchain_update(folder)

	def	cconfig_toolchain_update(self, folder):
		d = self.tgen.env.DEST_OS
		toolchain = folder.find('toolChain')
		toolchain.set('superClass', self.cdt['toolchain'])
		toolchain.set('id', '%s.%s' % (self.cdt['toolchain'], self.get_uuid()))
		toolchain.set('name', '%s' % ('MinGW GCC' if d=='win32' else 'Linux GCC'))
		
		target = toolchain.find('targetPlatform')
		target.set('name', self.cdt['name'])
		target.set('superClass', self.cdt['platform'])
		target.set('id', '%s.%s' % (self.cdt['platform'], self.get_uuid()))
		if self.cross:
			target.set('archList', self.cdt['archList'])
			target.set('osList', self.cdt['osList'])

		builder = toolchain.find('builder')
		builder.set('buildPath', '${workspace_loc:/%s}/%s' % (self.tgen.get_name(), self.cdt['name']))
		builder.set('superClass', 'cdt.managedbuild.target.gnu.builder.base')
		builder.set('id', '%s.%s' % (builder.get('superClass'), self.get_uuid()))
		builder.set('name', 'Gnu Make Builder%s' % ('.%s' % self.cdt['name'] if self.cross else ''))

		archiver = self.toolchain_archiver_get(toolchain)
		archiver.set('name', 'GCC Archiver')
		archiver.set('superClass', self.cdt['archiver'])
		archiver.set('id', '%s.%s' % (self.cdt['archiver'], self.get_uuid()))

		''' TODO:
		add remaining:
		- compiler
		- linker
		- assembler
		- input
		'''

	def toolchain_archiver_get(self, toolchain):
		for tool in toolchain.findall('tool'):
			if tool.get('superClass').count('.gnu.archiver.'):
				return tool
		return ElementTree.SubElement(toolchain, 'tool', {'id':'', 'name':'', 'superClass':''})

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
		<project id="" name="" projectType=""/>	
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


ECLIPSE_CDT_CCONFIGURATION = '''
<cconfiguration>
	<storageModule buildSystemId="org.eclipse.cdt.managedbuilder.core.configurationDataProvider" id="" moduleId="org.eclipse.cdt.core.settings" name="">
		<externalSettings>
			<externalSetting>
				<entry flags="VALUE_WORKSPACE_PATH" kind="includePath" name=""/>
				<entry flags="VALUE_WORKSPACE_PATH" kind="libraryPath" name=""/>
				<entry flags="RESOLVED" kind="libraryFile" name="" srcPrefixMapping="" srcRootPath=""/>
			</externalSetting>
		</externalSettings>
		<extensions>
			<extension id="org.eclipse.cdt.core.GCCErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
			<extension id="org.eclipse.cdt.core.GASErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
			<extension id="org.eclipse.cdt.core.GLDErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
			<extension id="org.eclipse.cdt.core.GmakeErrorParser" point="org.eclipse.cdt.core.ErrorParser"/>
			<extension id="org.eclipse.cdt.core.CWDLocator" point="org.eclipse.cdt.core.ErrorParser"/>
		</extensions>
	</storageModule>
	<storageModule moduleId="cdtBuildSystem" version="4.0.0">
		<configuration artifactName="${ProjName}" buildArtefactType="" buildProperties="" cleanCommand="rm -rf" description="" id="" name="" parent="">
			<folderInfo id="" name="/" resourcePath="">
				<toolChain id="" name="" superClass="">
					<targetPlatform id="" name="" superClass=""/>
					<builder buildPath="" id="" name="" superClass=""/>
				</toolChain>
			</folderInfo>
		</configuration>
	</storageModule>
	<storageModule moduleId="org.eclipse.cdt.core.externalSettings"/>	
</cconfiguration>
'''

