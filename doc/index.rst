.. waftools documentation master file, created by
   sphinx-quickstart on Mon Mar 31 23:16:45 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Waftools 0.1.3 documentation
============================
Welcome! This is the documentation for the *waftools* package, last updated Jul 2nd 2014.


Overview
========
The *waftools* package contains a collection of tools for the waf_ build environment.

The **waf** framework provides a meta build system allowing users to create
concrete build systems. Out of the box it provides support for building and 
installation of programs for a myriad of programming languages (C, C++, Java, 
Python, Fortran, Lua, ...), when needed new functions (e.g. source code 
checking) can be added to a concrete build solution using **waf** *tools* 
which can be imported and used in *wscript* build files. See the 
wafbook_ for a detailed description of the **waf** meta build system structure
and usage.

The *waftools* package provides a collection of such *tools* which, once 
installed, can be imported and used from any *wscript* build file on your 
system. Following provides a non-exhausting list of functions provided by this 
package:

- C/C++ export to makefiles (e.g. **make**, **cmake**)
- C/C++ export to IDE's (e.g. **Code::Blocks**, **Eclipse**, **Visual Studio**)
- C/C++ source code checking using **cppcheck** (including *html* reports)
- Create installers using **NSIS**
- Create C/C++ documentation using **DoxyGen**
- List dependencies between build tasks

The code snippet below provides an example on how the *export* function from 
the *waftools* package can be added to (top) level *wscript* file of a (your)
concrete build solution::

	import os
	import waftools

	def options(opt):
		opt.load('compiler_c')
		opt.load('export', tooldir=os.path.dirname(waftools.__file__))
	
	def configure(conf):
		conf.load('compiler_c')
		conf.load('export')

	def build(bld):
		bld.program(target='hello', source='hello.c')
		
Using this code snippet, the meta-data for the *C* program *hello* can be 
exported to foreign (build) formats (e.g. **Eclipse** projects or **GNU**
*MakeFiles*) using the *export* command::

	waf configure
	waf export --codeblocks

For more information on using *waf* commands and options use::

	waf --help

.. _waf: https://code.google.com/p/waf/
.. _wafbook: http://docs.waf.googlecode.com/git/book_17/single.html


Detailed description
====================
Following links provide a detailed description for each module contained within
this package:

.. toctree::
   :maxdepth: 2

   waftools


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

