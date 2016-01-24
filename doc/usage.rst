
Usage
=====
Following sub-sections provide some examples on what can be achieved using the waftools
package.


Cross compilation and multiple build environments
-------------------------------------------------
The code snippet below provides an example of how a complete build environment
can be created allowing you to build, not only for the host system, but also 
for one or more target platforms using, for instance, a C/C++ cross compiler::

    #!/usr/bin/env python
    # -*- encoding: utf-8 -*-

    import os, waftools
    from waftools import ccenv

    top = '.'
    out = 'build'
    ini = os.path.abspath('ccenv.ini').replace('\\', '/')

    VERSION = '0.0.1'
    APPNAME = 'example'

    def options(opt):
        opt.load('ccenv', tooldir=waftools.location)

    def configure(conf):
        conf.load('ccenv')

    def build(bld):
        ccenv.build(bld, trees=['components'])

    for var in ccenv.variants(ini):
        for ctx in ccenv.contexts():
            name = ctx.__name__.replace('Context','').lower()
            class _t(ctx):
                __doc__ = "%ss '%s'" % (name, var)
                cmd = name + '_' + var
                variant = var


When loading and configuring the *ccenv* tool, as shown in the example above, all 
required C/C++ tools for each build environment variant (i.e. native or cross-
compile) will be loaded and configured as well; e.g. compilers, makefile-, cmake-, 
eclipse-, codeblocks- and msdev exporters, cppcheck source code checking, doxygen 
documentation creation will be available for each build variant. Additional (ccross)
compile build environments can be specified in a seperate .INI file (named ccenv.ini 
in the example above) using following syntax::

    [arm]
    prefix = arm-linux-gnueabihf

    [msvc]
    host = win32
    c = msvc
    cxx = msvc

The section names *arm* and *msvc* specify the name of the compile build environment 
variant. The prefix combined with compiler type (c,cxx) will be used in order to 
create the concrete names of the (cross) compile toolchain binaries for that build
environment. The actual compilers used for the *arm* build environment for instance
will be::

    AR  = arm-linux-gnueabihf-ar
    CC  = arm-linux-gnueabihf-gcc
    CXX = arm-linux-gnueabihf-g++

Note that for the *msvc* build environment no prefix is used, only the base 
type of the compilers to be used for the environment are specified. Futhermore the
host is defined as *win32*; as result the build environment *msvc* will be created
when building on a *MS-Windows* build host.

Concrete build scripts (i.e. wscript files) for components can be placed somewhere 
within the *components* sub-directory. Any top level wscript file of a tree (being 
*components* in this example) will be detected and incorporated within the build 
environment. Any wscript files below those top level script files will have to be 
included using the *bld.recurse('../somepath')* command from the top level script 
of that tree.


Source code analysis
--------------------
C/C++ source code can be checked using the **CppCheck** static source analysis 
tool. Results of sources checked by **CppCheck** will be presented in a HTML
based report. The report contains a single index file containing a summary of 
defects containing links to detailed reports, one for each component (i.e. C/C++
program, static- or shared library):

.. figure:: cppcheck_summary.png
    :align: center
    :scale: 75 %

    summary of defects found.

For each component a detailed report contains the defects found stating the
defect type, its severity and line number on which the defect has been detected:

.. figure:: cppcheck_detailed.png
    :align: center
    :scale: 75 %

    defects per file.

Clicking on the line number will show the source code with a colorfull marker for
each defect that has been detected:

.. figure:: cppcheck_source.png
    :align: center
    :scale: 75 %

    source code with highlighted defects.

The code snippet below presents a *wscript* example using the *cppcheck* source
code analysis tool::

    import waftools

    def options(opt):
        opt.load('compiler_c')
        opt.load('cppcheck', tooldir=waftools.location)

    def configure(conf):
        conf.load('compiler_c')
        conf.load('cppcheck')

    def build(bld):
        bld.program(target='hello', source='hello.c')

Using this code snippet, source code can be inspected and HTML reports can 
be generated using the following command::

    waf clean build --cppcheck --cppcheck-err-resume

.. note::
    A (re)build is required in order to perform the source code analysis.

Once completed the HTML report can be found and at: **./reports/cppcheck/index.html**


Create source code documentation
--------------------------------
For C/C++ build tasks source code documentation can be created using 
**DoxyGen**. Once generated the documentation can be found at: 
**./reports/doxygen/**.

The code snippet below presents a *wscript* example using the *doxygen*
source code documentation tool::

    import waftools

    def options(opt):
        opt.load('compiler_c')
        opt.load('doxygen', tooldir=waftools.location)

    def configure(conf):
        conf.load('compiler_c')
        conf.load('doxygen')

    def build(bld):
        bld.program(target='hello', source='hello.c')

Using this code snippet, source code documentation can be generated using
the following command::

    waf doxygen

For more information please refer to the detailed description of the 
:ref:`doxygen <mod_doxygen>` module.


Export projects to integrated development environments
------------------------------------------------------
C/C++ build tasks (i.e. programs, static and shared libraries) can
be exported to project, workspace and/or solution files for either 
**Code::Blocks**, **Eclipse** (using CDT) or **MSDev** (Microsoft
Developer Studio).

The code snippet below presents a *wscript* that provides support
for export to **Eclipse**::

    import waftools

    def options(opt):
        opt.load('compiler_c')
        opt.load('eclipse', tooldir=waftools.location)

    def configure(conf):
        conf.load('compiler_c')
        conf.load('eclipse')

    def build(bld):
        bld.program(target='hello', source='hello.c')

Using this code snippet, **Eclipse** projects can be exported using
the following command::

    waf eclipse

When no longer needed all exported project files from a tree can simply
removed using the following command::

    waf eclipse --clean


For more information please refer to the detailed description of the 
:ref:`codeblocks <mod_codeblocks>`, :ref:`eclipse <mod_eclipse>` and 
:ref:`msdev <mod_msdev>` modules.


Export to projects to other build systems
-----------------------------------------
When needed C/C++ build tasks (programs, static or shared libraries) can be
exported to other build system formats (e.g. make, cmake). When doing so the 
definitions and settings as defined within the waf_ build environment will be
exported to those foreign build formats with the intend of keeping the same 
structure and behavior as defined within the waf build system as much as 
possible. Generated makefiles, for instance, will build out of tree and will 
use the same installation installation prefix.

The code snippet below presents a *wscript* example using the *makefile* export
module::

    import waftools

    def options(opt):
        opt.load('compiler_c')
        opt.load('makefile', tooldir=waftools.location)

    def configure(conf):
        conf.load('compiler_c')
        conf.load('makefile')

    def build(bld):
        bld.program(target='hello', source='hello.c')

Using this code snippet, the meta-data for the *C* program *hello* can be 
exported to **GNU** *MakeFiles* using the following commands::

    waf configure
    waf makefile

Note that makefiles will be exported at the location as the orginating 
wscript files (i.e. useally somewhere in the source tree). All exported 
makefiles can, when needed, be simply removed using the *clean* command::

    waf makefile --clean

Once exported *make* can be used to the building without futher need for,
or dependency to the waf build system.

For more information please refer to the detailed description of the 
:ref:`cmake <mod_cmake>` and :ref:`makefile <mod_makefile>` modules.


Binary distributions
--------------------
For windows targets platforms installers can be created using the NullSoft
Installable Scripting system (**NSIS**). If no user defined .nsi script is 
provided a default one will be created in the top level directory of the 
build system.

The code snippet below presents a *wscript* that provides support for
creating installers using **NSIS**::

    import waftools

    def options(opt):
        opt.load('compiler_c')
        opt.load('bdist', tooldir=waftools.location)

    def configure(conf):
        conf.load('compiler_c')
        conf.load('bdist')

    def build(bld):
        bld.program(target='hello', source='hello.c')

Using this code snippet, a Windows installer can be created using
the following command::

    waf bdist --formats=nsis

For more information please refer to the detailed description of the 
:ref:`bdist <mod_bdist>` module.


.. _waf: https://waf.io/
.. _wafbook: https://waf.io/book

