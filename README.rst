Summary
-------
This package contains a collection of tools for the waf_ build environment
intended for both native- as well cross compilation of C/C++ based projects.


Description
-----------
The waf_ framework provides a meta build system allowing users to create
concrete build systems. Out of the box it provides support for building and 
installation of programs for a myriad of programming languages (C, C++, Java, 
Python, Fortran, Lua, ...), when needed new functions (e.g. source code 
checking) can be added to a concrete build solution using waf_ *tools* 
which can be imported and used in *wscript* build files. See the 
wafbook_ for a detailed description of the waf_ meta build system structure
and usage.

The *waftools* package provides a collection of C/C++ *tools* which, once 
installed, can be imported and used from any *wscript* build file on your 
system. Following provides a non-exhausting list of functions provided by this 
package:

- Cross compile using several C/C++ cross compiler toolchains
- C/C++ export to makefiles (e.g. **make**, **cmake**)
- C/C++ export to IDE's (e.g. **Code::Blocks**, **Eclipse**, **Visual Studio**)
- C/C++ source code checking using **cppcheck** (including *html* reports)
- Clean and format C/C++ source code using **GNU** **indent**
- Create installers using **NSIS**
- Create C/C++ documentation using **DoxyGen**
- List dependencies between build tasks


Installation
------------
The package can be installed using pip::

    pip install -I waftools

or by cloning the repository and using distutils::

    cd ~
    git clone https://bitbucket.org/Moo7/waftools.git waftools
    cd waftools
    python setup.py sdist install

Contained within the *waftools* package is a special install script which can be used to 
install the waf build system itself::

    wafinstall [--version=version] [--tools=compat15]


Usage
-----
The code snippet below provides an example of how a complete build environment
can be created allowing you to build, not only for the host system, but also 
for one or more target platforms using a C/C++ cross compiler::

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
    c = msvc
    cxx = msvc

The section name, *arm* in the example above, specifies the name of the compile
build environment variant. The prefix combined with compiler type (c,cxx) will be 
used in order to create the concrete names of the cross compile toolchain 
binaries::

    AR  = arm-linux-gnueabihf-ar
    CC  = arm-linux-gnueabihf-gcc
    CXX = arm-linux-gnueabihf-g++

Concrete build scripts (i.e. wscript files) for components can be placed somewhere 
within the *components* sub-directory. Any top level wscript file of a tree (being 
*components* in this example) will be detected and incorporated within the build 
environment. Any wscript files below those top level script files will have to be 
included using the *bld.recurse('../somepath')* command from the top level script 
of that tree.


Support
-------
Defects and/or feature requests can be reported at::
    https://bitbucket.org/Moo7/waftools/issues


.. note::
    the complete package documentation can be found at: 
    http://pythonhosted.org/waftools/


.. _waf: https://code.google.com/p/waf/
.. _wafbook: http://docs.waf.googlecode.com/git/book_18/single.html

