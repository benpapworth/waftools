Summary
-------
This package contains a collection of tools for the Waf_ build environment. 
Following provides a non-exhausting list of functions provided by this package:

- C/C++ export to makefiles (e.g. **make**, **cmake**)
- C/C++ export to IDE's (e.g. **Code::Blocks**, **Eclipse**, **Visual Studio**)
- C/C++ source code checking using **cppcheck** (including *html* reports)
- Create installers using NSIS


Description
-----------
The **Waf** framework provides a meta build system allowing users to create
concrete build systems. In contrast to many existing existing build solutions 
it is very versatile and flexible; out of the box it provides support for 
building and installation of programs for a myriad of programming languages 
(C, C++, Java, Python, Fortran, Lua, ...), when needed new functions (e.g. 
source code checking) can be added to a concrete build solution using **waf**
*tools* which can be imported and used in *wscript* build files. See the 
WafBook_ for a detailed description of **Waf** itself.

The *waftools* provides a collection of such *tools* which, once installed, 
can be imported and used from any *wscript* build file on your system.


Usage
-----
Follwing provides an example on how the *export* function from the *waftools*
can be added to (top) level *wscript* file of a concrete build solution::

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
		
Based on the example above, the meta-data for the program *hello* can be 
exported to foreign (build) formats outside of the *Waf* build environment
using the *export* command::

	waf configure
	waf export --codeblocks
		
For more information on using *Waf* commands and options use::

	waf --help

		

.. _Waf: https://code.google.com/p/waf/
.. _WafBook: http://docs.waf.googlecode.com/git/book_17/single.html
