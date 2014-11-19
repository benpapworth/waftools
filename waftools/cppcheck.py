#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com


'''
Summary
-------
Provides a *waf* wrapper (i.e. waftool) around the static C/C++ source code
checking tool **cppcheck**.

See http://cppcheck.sourceforge.net/ for more information on **cppcheck** 
itself; how you can obtain and install it for your particular desktop 
environment. Note that many linux distributions already provide a ready to 
install version of **cppcheck**. On *Fedora*, for instance, it can be installed
using *yum*::

    $ sudo yum install cppcheck


Description
-----------
Each time a C/C++ task generator within your *waf* build environment is being 
build or rebuild, its source code can be checked using cppcheck. This module 
will gather and extract all the required information from the C/C++ task
generator (e.g. *bld.program* defined somewhere in a *wscript* file) and will 
use it to perform a source code analysis using cppcheck on command line. The 
command line results from **cppcheck** (in XML format) will be used as input in 
order to create a highlighted and colorful HTML report pinpointing all
(possible) problems. 
For each single C/C++ task defined within your *waf* build environment such a 
separate HTML report will be created. Furthermore a single HTML index page will
be created containing references to all individual HTML reports of components. 
All these reports will be stored in the sub directory *reports/cppcheck* in the
top level directory of your build environment. When needed this location can
also be changed to, see command line options.

Example below present an example of the reports generated in a build environment
in which three *C* components have been defined::

    .
    ├── components
    │   ├── chello
    │   │   ├── include
    │   │   │   └── hello.h
    │   │   ├── src
    │   │   │   └── hello.c
    │   │   └── wscript
    │   ├── ciambad
    │   │   ├── cppcheck.suppress
    │   │   ├── include
    │   │   ├── src
    │   │   │   └── iambad.c
    │   │   └── wscript
    │   └── cleaking
    │       ├── include
    │       │   └── leaking.h
    │       ├── src
    │       │   └── leaking.c
    │       └── wscript
    ├── reports
    │   └── cppcheck
    │       ├── components
    │       │   ├── chello
    │       │   │   ├── chello.html
    │       │   │   ├── index.html
    │       │   │   ├── style.css
    │       │   │   └── chello.xml
    │       │   ├── ciambad
    │       │   │   ├── ciambad.html
    │       │   │   ├── index.html
    │       │   │   ├── style.css
    │       │   │   └── ciambad.xml
    │       │   └── cleaking
    │       │       ├── cleaking.html
    │       │       ├── index.html
    │       │       ├── style.css
    │       │       └── cleaking.xml
    │       ├── index.html
    │       └── style.css
    └── wscript

Note that each report for a task generator from the components directory 
contains an extra indent in the reports directory; cppchecks reports are stored
in a sub directory using the name of the unique task generator as name for that
sub directory. This allows for the creation of multiple reports at the same
location in case a single *wscript* file contains multiple task generators in
the components directory.  

Under normal conditions no additional parameters or definitions are needed in
the definition of a C/C++ task generator itself; simply defining it as 
*program*, *stlib* or *shlib* and adding this module to the top level *wscript*
of your *waf* build environment will suffice. However in some cases 
**cppcheck** might detect problems that are either not true, or you just want
to suppress them. In these cases you can either use global suppression options
(using command line options) but you can also add special rules to the 
definition of the C/C++ task generators in question (more on this the next 
section Usage).


Usage
-----
In order to use this waftool simply add it to the 'options' and 'configure' 
functions of your main *waf* script as shown in the example below::

    import waftools

    def options(opt):
        opt.load('cppcheck', tooldir=waftools.location)

    def configure(conf):
        conf.load('cppcheck')

When configured as shown in the example above, **cppcheck** will perform a 
source code analysis on all C/C++ tasks that have been defined in your *waf* 
build environment when using the '--cppcheck' build option::

    waf build --cppcheck

The example shown below for a C program will be used as input for **cppcheck** 
when building the task::

    def build(bld):
        vbld.program(name='foo', src='foobar.c')

The result of the source code analysis will be stored both as XML and HTML 
files in the build location for the task. Should any error be detected by
**cppcheck**, then the build process will be aborted and a link to the HTML 
report will be presented. When desired you also choose to resume with checking
other components after a fatal error has been detected using the following command
line option::

    $ waf build --cppcheck --cppcheck-err-resume 

When needed source code checking by **cppcheck** can be disabled per task or even 
for each specific error and/or warning within a particular task.

In order to exclude a task from source code checking add the skip option to the
task as shown below::

    def build(bld):
        bld.program(name='foo', src='foobar.c', cppcheck_skip=True)

When needed problems detected by cppcheck may be suppressed using a file 
containing a list of suppression rules. The relative or absolute path to this 
file can be added to the build task as shown in the example below::

    bld.program(name='bar', src='foobar.c', cppcheck_suppress='bar.suppress')

A **cppcheck** suppress file should contain one suppress rule per line. Each of 
these rules will be passed as an '--suppress=<rule>' argument to **cppcheck**.

'''

import os
import sys
import xml.etree.ElementTree as ElementTree
from waflib import TaskGen, Context, Logs, Utils

CPPCHECK_WARNINGS = ['error', 'warning', 'performance', 'portability', 'unusedFunction']


def options(opt):
	'''Adds command line options to the *waf* build environment 

	:param opt: Options context from the *waf* build environment.
	:type opt: waflib.Options.OptionsContext
	'''
	opt.add_option('--cppcheck', dest='cppcheck', default=False,
		action='store_true', help='check C/C++ sources (default=False)')

	opt.add_option('--cppcheck-path', dest='cppcheck_path', default='reports/cppcheck',
		action='store', help='location to save cppcheck reports to.')
	
	opt.add_option('--cppcheck-fatals', dest='cppcheck_fatals', default='error',
		action='store', help='comma separated list of fatal severities')
	
	opt.add_option('--cppcheck-err-resume', dest='cppcheck_err_resume',
		default=False, action='store_true',
		help='continue in case of errors (default=False)')

	opt.add_option('--cppcheck-bin-enable', dest='cppcheck_bin_enable',
		default='warning,performance,portability,style,unusedFunction',
		action='store',
		help="cppcheck option '--enable=' for binaries (default=warning,performance,portability,style,unusedFunction)")

	opt.add_option('--cppcheck-lib-enable', dest='cppcheck_lib_enable',
		default='warning,performance,portability,style', action='store',
		help="cppcheck option '--enable=' for libraries (default=warning,performance,portability,style)")

	opt.add_option('--cppcheck-std-c', dest='cppcheck_std_c',
		default='c99', action='store',
		help='cppcheck standard to use when checking C (default=c99)')

	opt.add_option('--cppcheck-std-cxx', dest='cppcheck_std_cxx',
		default='c++03', action='store',
		help='cppcheck standard to use when checking C++ (default=c++03)')

	opt.add_option('--cppcheck-check-config', dest='cppcheck_check_config',
		default=False, action='store_true',
		help='forced check for missing buildin include files, e.g. stdio.h (default=False)')

	opt.add_option('--cppcheck-max-configs', dest='cppcheck_max_configs',
		default='10', action='store',
		help='maximum preprocessor (--max-configs) define iterations (default=20)')


def configure(conf):
	'''Method that will be invoked by *waf* when configuring the build 
	environment.
	
	:param conf: Configuration context from the *waf* build environment.
	:type conf: waflib.Configure.ConfigurationContext
	'''
	if conf.options.cppcheck:
		conf.env.CPPCHECK_EXECUTE = [1]
	conf.env.CPPCHECK_PATH = conf.options.cppcheck_path
	conf.env.CPPCHECK_FATALS = conf.options.cppcheck_fatals.split(',')
	conf.env.CPPCHECK_STD_C = conf.options.cppcheck_std_c
	conf.env.CPPCHECK_STD_CXX = conf.options.cppcheck_std_cxx
	conf.env.CPPCHECK_MAX_CONFIGS = conf.options.cppcheck_max_configs
	conf.env.CPPCHECK_BIN_ENABLE = conf.options.cppcheck_bin_enable
	conf.env.CPPCHECK_LIB_ENABLE = conf.options.cppcheck_lib_enable
	conf.find_program('cppcheck', var='CPPCHECK')


def postfun(bld):
	'''Method that will be invoked by the *waf* build environment once the 
	build has been completed.
	
	It will use the result of the source code checking stored within the given
	build context and use it to create a global HTML index. This global index
	page contains a reference to all reports on C/C++ components that have been
	checked.
	
	:param bld: Build context from the *waf* build environment.
	:type bld: waflib.Build.BuildContext
	'''
	for entry in bld.catalog:
		print(entry)
	

@TaskGen.feature('c')
@TaskGen.feature('cxx')
def cppcheck_execute(self):
	'''Method that will be invoked by *waf* for each task generator for the 
	C/C++ language.
	
	:param self: A task generator that contains all information of the C/C++
				 program, shared- or static library to be exported.
	:type self: waflib.Task.TaskGen
	'''
	bld = self.bld
	check = bld.env.CPPCHECK_EXECUTE
	root = str(bld.env.CPPCHECK_PATH).replace('\\', '/')
	if not bool(check):
		if not bld.options.cppcheck and not bld.options.cppcheck_err_resume:
			return
	if getattr(self, 'cppcheck_skip', False):
		return

	if not hasattr(bld, 'catalog'):
		bld.catalog = []
		bld.add_post_fun(postfun)

	fatals = bld.env.CPPCHECK_FATALS
	if bld.options.cppcheck_err_resume:
		fatals = []

	index = '%s/%s/%s/index.html' % (bld.path.abspath(), root, self.path.relpath())
	severities = CppCheck(self, root, fatals).execute()
	bld.catalog.append( (self.get_name(), index.replace('\\', '/'), severities) )


class Defect(object):
	def __init__(self, id, severity, msg='', verbose='', file='', line=0):
		self.id = id
		self.severity = severity
		self.msg = msg
		self.verbose = verbose
		self.file = file
		self.line = line

	
class CppCheck(object):
	'''Class used for creating colorfull HTML reports based on the source code 
	check results from **cppcheck**.
	
	Excutes source code checking on each C/C++ source file defined in the 
	task generator.

	Performs following steps per source file:
	- check source using cppcheck, use xml output
	- save the result from stderr as xml file
	- process and convert the results from stderr and save as html report
	- report defects, if any, to stout and including a link to the report
	
	:param tgen: Contains all input information for the C/C++ component
	:type tgen: waflib.Task.TaskGen
	:param root: top level directory for storing the reports
	:type root: str
	:param fatals: list of severities that should be treated as fatal when encountered
	:type fatals: list
	'''
	def __init__(self, tgen, root, fatals):
		self.tgen = tgen
		self.bld = tgen.bld
		self.root = root
		self.fatals = fatals
		self.warnings = CPPCHECK_WARNINGS

	def save(self, fname, content):
		fname = '%s/%s/%s' % (self.root, self.tgen.path.relpath(), fname)
		path = os.path.dirname(fname)
		if not os.path.exists(path):
			os.makedirs(path)
		node = self.bld.path.make_node(fname)
		node.write(content)
		return node.abspath().replace('\\', '/')

	def save_xml(self, fname, stderr, cmd):
		root = ElementTree.fromstring(stderr)
		element = ElementTree.SubElement(root.find('cppcheck'), 'cmd')
		element.text = cmd
		s = ElementTree.tostring(root)
		return self.save(fname, s.decode('utf-8'))

	def defects(self, stderr):
		defects = []
		for error in ElementTree.fromstring(stderr).iter('error'):
			defect = Defect(error.get('id'), error.get('severity'))
			defect.msg = str(error.get('msg')).replace('<','&lt;')
			defect.verbose = error.get('verbose')
			for location in error.findall('location'):
				defect.file = location.get('file')
				defect.line = str(int(location.get('line')))
			defects.append(defect)
		return defects
		
	def report(self, bld, tgen, fatals, defects):
		name = tgen.get_name()
		url = '%s/%s/%s/index.html' % (bld.path.abspath(), self.root, tgen.path.relpath())
		Logs.pprint('PINK', '%s:' % name)
		for d in defects:
			if d.severity == 'error': color = 'RED'
			else: color = 'YELLOW' if d.severity in self.warnings else 'GREEN'
			if d.file != '':
				Logs.pprint(color, '\tfile:///%s (line:%s)' % (d.file, d.line))
			Logs.pprint(color, '\t%s %s %s' % (d.id, d.severity, d.msg))
			if d.severity in fatals:
				bld.fatal('%s: fatal error(%s) detected' % (name, d.severity))

	def execute(self):
		severity = []
		for (name, cmd) in self.commands():
			stderr = self.bld.cmd_and_log(cmd.split(), quiet=Context.BOTH, output=Context.STDERR)
			xml = self.save_xml(name, stderr, cmd)
			defects = self.defects(stderr)
			self.report(self.bld, self.tgen, self.fatals, defects)
			severity.extend([defect.severity for defect in defects])
		return severity

	def commands(self):
		'''returns a list of the commands to be executed, one per source file'''
		bld = self.bld
		gen = self.tgen
		env = self.tgen.env
		features = getattr(gen, 'features', [])
		commands = []

		if 'cxx' in features:
			language = 'c++ --std=%s' % env.CPPCHECK_STD_CXX
		else:
			language = 'c --std=%s' % env.CPPCHECK_STD_C
		configs = env.CPPCHECK_MAX_CONFIGS

		cmd = Utils.to_list(env.CPPCHECK)[0].replace('\\', '/')
		cmd += ' -v --xml --xml-version=2 --inconclusive --report-progress --max-configs=%s --language=%s' % (configs, language)

		if bld.options.cppcheck_check_config:
			cmd.append('--check-config')

		if set(['cprogram','cxxprogram']) & set(features):
			cmd += ' --enable=%s' % env.CPPCHECK_BIN_ENABLE
		elif set(['cstlib','cshlib','cxxstlib','cxxshlib']) & set(features):
			cmd += ' --enable=%s' % env.CPPCHECK_LIB_ENABLE

		inc = ''
		for i in gen.to_incnodes(gen.to_list(getattr(gen, 'includes', []))):
			inc += ' -I%r' % i
		for i in gen.to_incnodes(gen.to_list(gen.env.INCLUDES)):
			inc += ' -I%r' % i

		for src in gen.to_list(gen.source):
			fname = '%s.xml' % os.path.splitext(str(src))[0]
			commands.append((fname, '%s %r %s' % (cmd, src, inc)))
		return commands

