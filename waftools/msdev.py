#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

'''
Summary
-------
Exports and converts *waf* project data, for C/C++ programs, static- and shared
libraries, into **Microsoft Visual Studio**, also known as **msdev**, 
project files (.vcproj) and solution (*.sln) files.

**Microsoft Visual Studio** is a mature and stable integrated development 
environment for, amongst others, the C and C++ programming language. A free
version of this IDE, known as the *express* version can be obtained from Microsoft
at http://wwww.visualstudio.com.

Description
-----------
When exporting *waf* project data, a single **Visual Studio** solution will be
exported in the top level directory of your *WAF* build environment. This 
solution file will contain references to all exported **Visual Studio** 
projects and will include dependencies between those projects and will have the
same name as APPNAME variable from the top level *wscript* file.

For each single task generator (*waflib.TaskGenerator*), for instance a 
*bld.program(...)* which has been defined within a *wscript* file somewhere in
the build environment, a single **Visual Studio** project file will be generated
in the same directory as where the task generator has been defined.
The name of this task generator will be used as name for the exported **Visual
Studio** project file. If for instance the name of the task generator is 
*hello*, then a **Visual Studio** project file named *hello.vcproj* will be
exported.

Example below presents an overview of an environment in which **Visual Studio** 
files already have been exported::

        .
        ├── components
        │   └── clib
        │       ├── program
        │       │   ├── cprogram.vcproj
        │       │   └── wscript
        │       ├── shared
        │       │   ├── cshlib.vcproj
        │       │   └── wscript
        │       └── static
        │           ├── cstlib.vcproj
        │           └── wscript
        │
        ├── waf.vcproj
        ├── appname.sln
        └── wscript


Projects will be exported such that they will use the same settings and 
structure as has been defined for that build task within the *waf* build 
environment as much as possible. Note that since cross compilation is not 
really supported in this IDE, only the first environment encountered that
is targeted for **MS Windows** will be exported; i.e. an environment in 
which::
	
	bld.env.DEST_OS == 'win32'

is true.

	
Please note that in contrast to a *normal* IDE setup the exported projects 
will contain either a *debug* **or** a *release* build target but not both at
the same time. By doing so exported projects will always use the same settings
(e.g. compiler options, installation paths) as when building the same task in
the *waf* build environment from command line.

Besides these normal projects that will be exported based on the task 
generators that have been defined within the *waf* build environment, a special
**Visual Studio** project named *waf.vcproj* will also be exported. This project 
will be stored in the top level directory of the build environment and will
contain the following build targets;

* build
* clean
* install
* uninstall

If, for instance, an additional build variant named *arm5* has been defined in 
the *waf* build environment, then the following build targets will be added as
well;

* build_arm5
* clean_arm5
* install_arm5
* uninstall_arm5

Usage
-----
**Visual Studio** project and workspace files can be exported using the *export* 
command, as shown in the example below::

        $ waf export --msdev

When needed, exported **Visual Studio** project- and solution files can be 
removed using the *export-clean* command, as shown in the example below::

        $ waf export --cleanup --msdev

Once exported simply open the *appname.sln* using **Visual Studio**
this will automatically open all exported projects as well.
'''

import os
import sys
import copy
import uuid
import platform
import xml.etree.ElementTree as ElementTree
from xml.dom import minidom
from waflib import Utils, Node, Logs


def options(opt):
	'''Adds command line options to the *waf* build environment 

	:param opt: Options context from the *waf* build environment.
	:type opt: waflib.Options.OptionsContext
	'''
	opt.add_option('--msdev', dest='msdev', default=False, 
		action='store_true', help='select msdev for export/import actions')


def configure(conf):
	'''Method that will be invoked by *waf* when configuring the build 
	environment.
	
	:param conf: Configuration context from the *waf* build environment.
	:type conf: waflib.Configure.ConfigurationContext
	'''	
	if conf.options.msdev:
		conf.env.append_unique('MSDEV', 'msdev')


def _selected(bld):
	'''Returns True when this module has been selected/configured.'''
	m = bld.env.MSDEV
	return len(m) > 0 or bld.options.msdev


def export(bld):
	'''Exports all C and C++ task generators as **Visual Studio** projects
	and creates a **Visual Studio** solution containing references to 
	those project.
	
	:param bld: a *waf* build instance from the top level *wscript*.
	:type bld: waflib.Build.BuildContext
	'''
	if not _selected(bld):
		return

	solution = MsDevSolution(bld)
	for gen, targets in bld.components.items():
		if set(('c', 'cxx')) & set(getattr(gen, 'features', [])):
			project = MsDevProject(bld, gen, targets)
			project.export()
			
			(name, fname, deps, uuid) = project.get_metadata()
			solution.add_project(name, fname, deps, uuid)

	#project = WafMSDEVProject(bld)
	#project.export()
	#(name, fname, deps) = project.get_metadata()
	#solution.add_project(name, fname, deps)
	
	solution.export()


def cleanup(bld):
	'''Removes all **Visual Studio** projects and workspaces from the 
	*waf* build environment.
	
	:param bld: a *waf* build instance from the top level *wscript*.
	:type bld: waflib.Build.BuildContext
	'''
	if not _selected(bld):
		return

	for gen, targets in bld.components.items():
		project = MsDevProject(bld, gen, targets)
		project.cleanup()

	#project = WafMSDEVProject(bld)
	#project.cleanup()

	solution = MsDevSolution(bld)
	solution.cleanup()


class MsDev(object):
	'''Abstract base class used for exporting *waf* project data to 
	**Visual Studio** projects and solutions.

	:param bld: Build context as used in *wscript* files of your *waf* build
				environment.
	:type bld:	waflib.Build.BuildContext
	'''

	PROGRAM	= '1'
	'''Identifier for projects containing an executable'''

	STLIB   = '2'
	'''Identifier for projects containing a static library'''

	SHLIB   = '3'
	'''Identifier for projects containing a shared library'''
	
	OBJECT  = '4'
	'''Identifier for projects for building objects only'''

	def __init__(self, bld):
		self.bld = bld
		self.exp = bld.export

	def export(self):
		'''Exports a **Visual Studio** workspace or project.'''
		content = self._get_content()
		if not content:
			return
		if self._xml_clean:
			content = self._xml_clean(content)

		node = self._make_node()
		if not node:
			return
		node.write(content)

	def cleanup(self):
		'''Deletes a **Visual Studio** workspace or project file including 
		.layout and .depend files.
		'''
		cwd = self._get_cwd()
		for node in cwd.ant_glob('*.user'):
			node.delete()
		for node in cwd.ant_glob('*.ncb'):
			node.delete()
		node = self._find_node()
		if node:
			node.delete()

	def _get_cwd(self):
		cwd = os.path.dirname(self._get_fname())
		if cwd == "":
			cwd = "."
		return self.bld.srcnode.find_node(cwd)

	def _find_node(self):
		name = self._get_fname()
		if not name:
			return None    
		return self.bld.srcnode.find_node(name)

	def _make_node(self):
		name = self._get_fname()
		if not name:
			return None    
		return self.bld.srcnode.make_node(name.lower())

	def _get_fname(self):
		'''<abstract> Returns file name.'''
		return None

	def _get_content(self):
		'''<abstract> Returns file content.'''
		return None

	def _xml_clean(self, content):
		s = minidom.parseString(content).toprettyxml(indent="\t")
		lines = [l for l in s.splitlines() if not l.isspace() and len(l)]
		lines[0] = '<?xml version="1.0" encoding="UTF-8"?>'
		return '\n'.join(lines)


class MsDevSolution(MsDev):
	'''Class used for exporting *waf* project data to a **Visual Studio** 
	solution located in the lop level directory of the *waf* build
	environment.

	:param bld: Build context as used in *wscript* files of your *waf* build
				environment.
	:type bld:	waflib.Build.BuildContext
	'''
	
	def __init__(self, bld):
		super(MsDevSolution, self).__init__(bld)
		self.projects = {}
		self._xml_clean = None

	def _get_fname(self):
		'''Returns the workspace's file name.'''
		return '%s.sln' % self.exp.appname

	def _get_content(self):
		'''returns the content of a msdev solution file containing references to all 
		projects and project dependencies.
		'''
		g = ''
		p = ''
		for n, (f, d, i) in self.projects.items():
			i = str(i).upper()
			u = str(uuid.uuid4()).upper()
			p += 'Project("{%s}") = "%s", "%s", "{%s}"\nEndProject\n' % (u, n, f, i)
			g += '\t\t{%s}.Debug|Win32.ActiveCfg = Debug|Win32\n\t\t{%s}.Debug|Win32.Build.0 = Debug|Win32\n' % (i, i)
		content = str(MSDEV_SOLUTION).format(p, g)
		return content

	def add_project(self, name, fname, deps, id):
		'''Adds a project to the workspace.
		
		:param name:	Name of the project.
		:type name:		str
		:param fname:	Complete path to the project file
		:type fname: 	str
		:param deps:	List of names on which this project depends
		:type deps: 	list of str
		'''
		self.projects[name] = (fname, deps, id)


class MsDevProject(MsDev):
	'''Class used for exporting *waf* project data to **Visual Studio** 
	projects.

	:param bld: Build context as used in *wscript* files of your *waf* build
				environment.
	:type bld:	waflib.Build.BuildContext
	
	:param gen: Task generator that contains all information of the task to be
				converted and exported to the **Visual Studio** project.
	:type gen:	waflib.Task.TaskGen
	
	:param targets: (deprecated) List of tasks associated with this task 
					generator and **Visual Studio** project.
	:type targets: list of waflib.Task.TaskBase instances
	'''

	def __init__(self, bld, gen, targets):
		super(MsDevProject, self).__init__(bld)
		self.gen = gen
		self.targets = targets
		self.uuid = uuid.uuid4()

	def _get_fname(self):
		'''Returns the project's file name.'''
		gen = self.gen
		return '%s/%s.vcproj' % (gen.path.relpath().replace('\\', '/'), gen.get_name())

	def _get_root(self):
		'''Returns a document root, either from an existing file, or from template.
		'''
		fname = self._get_fname()
		if os.path.exists(fname):
			tree = ElementTree.parse(fname)
			root = tree.getroot()
		else:
			root = ElementTree.fromstring(MSDEV_PROJECT)
		return root

	def _get_target(self, project, toolchain):
		'''Returns a targets for the requested toolchain name.

		If the target doesn't exist in the project it will be added.
		'''
		build = project.find('Build')
		for target in build.iter('Target'):
			for option in target.iter('Option'):
				if option.get('compiler') in [toolchain, 'XXX']:
					return target

		target = copy.deepcopy(build.find('Target'))
		build.append(target)
		return target

	def _get_content(self):
		'''Returns the content of a project file.'''
		root = self._get_root()
		## TODO: add content
		return ElementTree.tostring(root)

	def get_metadata(self):
		'''Returns a tuple containing project information (name, file name and 
		dependencies).
		'''
		gen = self.gen
		name = gen.get_name()
		fname = self._get_fname()
		deps = Utils.to_list(getattr(gen, 'use', []))
		uuid = self.uuid
		return (name, fname, deps, uuid)


	def _get_target_title(self):
		bld = self.gen.bld
		env = self.gen.env

		if bld.variant:
			title = '%s ' % (bld.variant)
		elif env.DEST_OS in sys.platform \
				and env.DEST_CPU == platform.processor():
			title = ''
		else:
			title = '%s-%s' % (env.DEST_OS, env.DEST_CPU)

		if '-g' in env.CFLAGS or '-g' in env.CXXFLAGS:
			title += 'debug'
		else:
			title += 'release'

		return title.title()

	def _get_buildpath(self):
		bld = self.bld
		gen = self.gen
		pth = '%s/%s' % (bld.path.get_bld().path_from(gen.path), gen.path.relpath())
		return pth.replace('\\', '/')

	def _get_output(self):
		gen = self.gen
		return '%s/%s' % (self._get_buildpath(), gen.get_name())

	def _get_object_output(self):
		return self._get_buildpath()

	def _get_working_directory(self):
		gen = self.gen
		bld = self.bld

		sdir = gen.bld.env.BINDIR
		if sdir.startswith(bld.path.abspath()):
			sdir = os.path.relpath(sdir, gen.path.abspath())

		return sdir.replace('\\', '/')

	def _get_target_type(self):
		gen = self.gen
		if set(('cprogram', 'cxxprogram')) & set(gen.features):
			return '1'
		elif set(('cstlib', 'cxxstlib')) & set(gen.features):
			return '2'
		elif set(('cshlib', 'cxxshlib')) & set(gen.features):
			return '3'
		else:
			return '4'

	def _get_genlist(self, gen, name):
		lst = Utils.to_list(getattr(gen, name, []))
		lst = [l.path_from(gen.path) if isinstance(l, Node.Nod3) else l for l in lst]
		return [l.replace('\\', '/') for l in lst]

	def _get_compiler_options(self):
		bld = self.bld
		gen = self.gen
		if 'cxx' in gen.features:
			flags = getattr(gen, 'cxxflags', []) + bld.env.CXXFLAGS
		else:
			flags = getattr(gen, 'cflags', []) + bld.env.CFLAGS

		if 'cshlib' in gen.features:
			flags.extend(bld.env.CFLAGS_cshlib)
		elif 'cxxshlib' in gen.features:
			flags.extend(bld.env.CXXFLAGS_cxxshlib)
		return list(set(flags))

	def _get_compiler_includes(self):
		gen = self.gen
		includes = self._get_genlist(gen, 'includes')
		return includes

	def _get_compiler_defines(self):
		gen = self.gen
		defines = self._get_genlist(gen, 'defines') + gen.bld.env.DEFINES
		if 'win32' in sys.platform:
			defines = [d.replace('"', '\\"') for d in defines]
		else:
			defines = [d.replace('"', '\\\\"') for d in defines]
		return defines

	def _get_link_options(self):
		bld = self.bld
		gen = self.gen
		flags = getattr(gen, 'linkflags', []) + bld.env.LINKFLAGS

		if 'cshlib' in gen.features:
			flags.extend(bld.env.LINKFLAGS_cshlib)
		elif 'cxxshlib' in gen.features:
			flags.extend(bld.env.LINKFLAGS_cxxshlib)
		return list(set(flags))

	def _get_link_libs(self):
		bld = self.bld
		gen = self.gen
		libs = Utils.to_list(getattr(gen, 'lib', []))
		deps = Utils.to_list(getattr(gen, 'use', []))
		for dep in deps:
			tgen = bld.get_tgen_by_name(dep)
			if set(('cstlib', 'cshlib', 'cxxstlib', 'cxxshlib')) & set(tgen.features):
				libs.append(dep)
		return libs
	
	def _get_link_paths(self):
		bld = self.bld
		gen = self.gen
		dirs = []
		deps = Utils.to_list(getattr(gen, 'use', []))
		for dep in deps:
			tgen = bld.get_tgen_by_name(dep)
			if set(('cstlib', 'cshlib', 'cxxstlib', 'cxxshlib')) & set(tgen.features):
				directory = tgen.path.get_bld().path_from(gen.path)
				dirs.append(directory.replace('\\', '/'))
		return dirs

	def _get_includes_files(self):
		gen = self.gen
		includes = []
		for include in self._get_genlist(gen, 'includes'):
			node = gen.path.find_dir(include)
			if node:
				for include in node.ant_glob('*.h*'):
					includes.append(include.path_from(gen.path).replace('\\', '/'))
		return includes


class WafMSDEVProject(MsDev):
	'''Class used for creating a dummy **Visual Studio** project containing
	only *waf* commands as pre build steps.

	:param bld: Build context as used in *wscript* files of your *waf* build
				environment.
	:type bld:	waflib.Build.BuildContext
	'''

	def __init__(self, bld):
		super(WafMSDEVProject, self).__init__(bld)
		self.title = 'waf'

	def _get_fname(self):
		'''Returns the file name.'''
		return 'waf.vcproj'

	def _get_root(self):
		'''Returns a document root, either from an existing file, or from template.
		'''
		fname = self._get_fname()
		if os.path.exists(fname):
			tree = ElementTree.parse(fname)
			root = tree.getroot()
		else:
			root = ElementTree.fromstring(MSDEV_PROJECT)
		return root

	def _get_cmd(self, name):
		'''Returns a string containing command and arguments to be executed.
		'''
		if 'win32' in sys.platform:
			cmd = 'python %s %s' % (str(sys.argv[0]).replace('\\', '/'), name)
		else:
			cmd = 'waf %s' % name
		return cmd
		
	def _init_target(self, target, name):
		'''Initializes a WAF build target.'''
		target.set('title', name)

		for option in target.iter('Option'):
			if option.get('output'):
				option.set('output', '')
			elif option.get('object_output'):
				option.set('object_output', '')
			elif option.get('compiler'):
				option.set('compiler', 'gcc')

		cmd = target.find('ExtraCommands/Add')
		cmd.set('before', self._get_cmd(name))
		return target

	def _add_target(self, project, name):
		'''Adds a WAF build target with given name.

		Will only be added if target does not exist yet.
		'''
		build = project.find('Build')			
		for target in build.iter('Target'):
			if target.get('title') == 'XXX':
				commands = ElementTree.SubElement(target, 'ExtraCommands')
				ElementTree.SubElement(commands, 'Add', {'before': 'XXX'})
				return self._init_target(target, name)

			if target.get('title') == name:
				return self._init_target(target, name)

		target = copy.deepcopy(build.find('Target'))
		build.append(target)
		return self._init_target(target, name)

	def _get_content(self):
		'''Returns the content of a code::blocks project file.
		'''
		root = self._get_root()
		project = root.find('Project')
		for option in project.iter('Option'):
			if option.get('title'):
				option.set('title', self.title)

		bld = self.bld
		targets = ['build', 'clean', 'install', 'uninstall']
		if bld.variant:
			targets = ['%s_%s' % (t, bld.variant) for t in targets]

		for target in project.iter('Build/Target'):
			name = target.get('title')
			if name in targets:
				targets.remove(name)

		for target in targets:
			self._add_target(project, target)

		return ElementTree.tostring(root)

	def get_metadata(self):
		'''Returns a tuple containing project information (name, file name and 
		dependencies).
		'''
		name = self.title
		fname = self._get_fname()
		deps = []
		return (name, fname, deps)


MSDEV_SOLUTION = \
'''Microsoft Visual Studio Solution File, Format Version 10.00
# Visual Studio 2008
{0}Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
	EndGlobalSection
	GlobalSection(ProjectConfigurationPlatforms) = postSolution
{1}	EndGlobalSection
	GlobalSection(SolutionProperties) = preSolution
		HideSolutionNode = FALSE
	EndGlobalSection
EndGlobal
'''

MSDEV_PROJECT = \
'''<?xml version="1.0" encoding="UTF-8"?>
<VisualStudioProject
	ProjectType="Visual C++"
	Version="9,00"
	Name="CNF2DAT2"
	ProjectGUID="{5BCFE62E-B2DA-4844-B255-01F4C7A84D47}"
	Keyword="Win32Proj"
	TargetFrameworkVersion="0"
	>
	<Platforms>
		<Platform
			Name="Win32"
		/>
	</Platforms>
	<ToolFiles>
	</ToolFiles>
	<Configurations>
		<Configuration
			Name="Debug|Win32"
			OutputDirectory="Debug"
			IntermediateDirectory="Debug"
			ConfigurationType="1"
			>
			<Tool
				Name="VCPreBuildEventTool"
			/>
			<Tool
				Name="VCCustomBuildTool"
			/>
			<Tool
				Name="VCXMLDataGeneratorTool"
			/>
			<Tool
				Name="VCWebServiceProxyGeneratorTool"
			/>
			<Tool
				Name="VCMIDLTool"
			/>
			<Tool
				Name="VCCLCompilerTool"
				Optimization="0"
				PreprocessorDefinitions="WIN32;_DEBUG;_CONSOLE;NDEBUG;_MBCS;_FLOAT_ON;IF_NEST"
				MinimalRebuild="true"
				BasicRuntimeChecks="3"
				RuntimeLibrary="3"
				UsePrecompiledHeader="0"
				WarningLevel="3"
				Detect64BitPortabilityProblems="true"
				DebugInformationFormat="4"
			/>
			<Tool
				Name="VCManagedResourceCompilerTool"
			/>
			<Tool
				Name="VCResourceCompilerTool"
			/>
			<Tool
				Name="VCPreLinkEventTool"
			/>
			<Tool
				Name="VCLinkerTool"
				LinkIncremental="2"
				GenerateDebugInformation="true"
				SubSystem="1"
				TargetMachine="1"
			/>
			<Tool
				Name="VCALinkTool"
			/>
			<Tool
				Name="VCManifestTool"
			/>
			<Tool
				Name="VCXDCMakeTool"
			/>
			<Tool
				Name="VCBscMakeTool"
			/>
			<Tool
				Name="VCFxCopTool"
			/>
			<Tool
				Name="VCAppVerifierTool"
			/>
			<Tool
				Name="VCPostBuildEventTool"
			/>
		</Configuration>
		<Configuration
			Name="Release|Win32"
			OutputDirectory="Release"
			IntermediateDirectory="Release"
			ConfigurationType="1"
			>
			<Tool
				Name="VCPreBuildEventTool"
			/>
			<Tool
				Name="VCCustomBuildTool"
			/>
			<Tool
				Name="VCXMLDataGeneratorTool"
			/>
			<Tool
				Name="VCWebServiceProxyGeneratorTool"
			/>
			<Tool
				Name="VCMIDLTool"
			/>
			<Tool
				Name="VCCLCompilerTool"
				PreprocessorDefinitions="WIN32;NDEBUG;_CONSOLE;"
				RuntimeLibrary="2"
				UsePrecompiledHeader="0"
				WarningLevel="3"
				Detect64BitPortabilityProblems="true"
				DebugInformationFormat="3"
			/>
			<Tool
				Name="VCManagedResourceCompilerTool"
			/>
			<Tool
				Name="VCResourceCompilerTool"
			/>
			<Tool
				Name="VCPreLinkEventTool"
			/>
			<Tool
				Name="VCLinkerTool"
				LinkIncremental="2"
				GenerateDebugInformation="true"
				SubSystem="1"
				OptimizeReferences="2"
				EnableCOMDATFolding="2"
				TargetMachine="1"
			/>
			<Tool
				Name="VCALinkTool"
			/>
			<Tool
				Name="VCManifestTool"
			/>
			<Tool
				Name="VCXDCMakeTool"
			/>
			<Tool
				Name="VCBscMakeTool"
			/>
			<Tool
				Name="VCFxCopTool"
			/>
			<Tool
				Name="VCAppVerifierTool"
			/>
			<Tool
				Name="VCPostBuildEventTool"
			/>
		</Configuration>
	</Configurations>
	<References>
	</References>
	<Files>
		<Filter
			Name="Header Files"
			Filter="h;hpp;hxx;hm;inl;inc;xsd"
			UniqueIdentifier="{93995380-89BD-4b04-88EB-625FBE52EBFB}"
			>
			<File
				RelativePath=".\cnftodat.h"
				>
			</File>
			<File
				RelativePath=".\mos.h"
				>
			</File>
			<File
				RelativePath=".\parser.h"
				>
			</File>
			<File
				RelativePath=".\scanner.h"
				>
			</File>
			<File
				RelativePath=".\types.h"
				>
			</File>
		</Filter>
		<Filter
			Name="Resource Files"
			Filter="rc;ico;cur;bmp;dlg;rc2;rct;bin;rgs;gif;jpg;jpeg;jpe;resx"
			UniqueIdentifier="{67DA6AB6-F800-4c08-8B7A-83BB121AAD01}"
			>
		</Filter>
		<Filter
			Name="Source Files"
			Filter="cpp;c;cc;cxx;def;odl;idl;hpj;bat;asm;asmx"
			UniqueIdentifier="{4FC737F1-C7A5-4376-A066-2A32D752A2FF}"
			>
			<File
				RelativePath=".\CNFTODAT.C"
				>
			</File>
			<File
				RelativePath=".\parser.c"
				>
			</File>
			<File
				RelativePath=".\scanner.c"
				>
			</File>
		</Filter>
		<File
			RelativePath=".\debug\BuildLog.htm"
			>
		</File>
	</Files>
	<Globals>
	</Globals>
</VisualStudioProject>
'''
