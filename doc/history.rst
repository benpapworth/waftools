History
-------
Following lists the changes per released version.

**v0.4.13**, 2016-10-19:

- *eclipse*; add <prefix>/lib and <prefix>/lib64 to LD_LIBRARY_PATH of launchers


**v0.4.12**, 2016-01-24:

- *eclipse*; added missing deps import
- *eclipse*; warn instead of abort when C++ compiler has not been configured
- issue16_; fixed external lib paths for msdev tool (visual studio 10.0)
- *indent*; fixed crash when using --indent-cleanup option
- *indent*; improved detection of .indent.pro configuration file


**v0.4.11**, 2016-01-24:

- *general*; updated to waf version 1.8.19
- *general*; tested with waf versions 1.8.10 ~ 1.8.19
- *general*; tested with python-2.7.10 and python python-3.4.3
- *ccenv*; add */DEBUG* link option; used for exporting debug program database
- *ccenv*; add */Fd<appname>.pdb* CL link option; specifies debug program database name
- *cppcheck*; presence is now optional, source code checking will be skipped durinig build when not available
- issue17_; removed redundant quotes around preprocessor defines


**v0.4.10**, 2015-03-15:

- *general*; updated to waf version 1.8.7
- *cmake*, *makefile*; improved detection of include paths
- issue14_; set external path and symbol references


**v0.4.9**, 2015-01-07:

- *bdist*; renamed module *package* into *bdist*, better reflects intended use of the module
- *ccenv*; use a shallow environment copy, i.e. use env.derive() for each variant build environment


**v0.4.8**, 2015-01-05:

- *ccenv*; added configuration option *host* (e.g. host = linux), only create variant build environment when  building on the specified host
- *general*; updated documentation to use theme from 'Read the Docs'


**v0.4.7**, 2014-12-31:

- *ccenv*; new module, replacement of ccross and gnucc modules
- *ccross*, gnucc; marked as deprecated, use ccenv instead
- *general*; dropped default support for batched_cc,unity, still too experimental
- issue6_; added check for presence of C and C++ compilers in eclipse module  


**v0.4.6**, 2014-12-30:

- issue13_; improved package installation
- *general*; added description for test script
- *general*; updated setup script for Fedora


**v0.4.5**, 2014-12-07:

- *cppcheck*; fixed crash when used in conf.check(); i.e. there are no bld.options


**v0.4.4**, 2014-12-07:

- *cppcheck*; fixed static title and header in top index page
- *cppcheck*; show highlighted source code for each file


**v0.4.3**, 2014-12-05:

- *makefile*, *cmake*, *msdev*; use additional system includes (bld.env.INCLUDES)
- *msdev*; treat bld.objects() as stlib.


**v0.4.2**, 2014-11-30:

- issue12_; *makefile*, treat bld.objects() as stlib.
- *makefile*; improved detection and handling of nested libraries.
- issue11_; *cmake*, treat bld.objects() as stlib.


**v0.4.1**, 2014-11-23:

- *ccross*; added support for msvc
- *ccross*; use gcc as default host compiler, use --cchost to use default platform compiler
- *ccross*; added option for specifying compiler postfix in ccross.ini file
- *cppcheck*; reimplemented using JinJa2

**v0.4.0**, 2014-11-17:

- *waftools*; moved get_deps() and get_targets() to module *deps*

**v0.3.9**, 2014-11-16:

- *waftools*; return unique list of deps in *waftools.get_deps()*
- *eclipse*; [bug fix] use general compiler flags and includes
- *eclipse*; [bug fix] export *bld.objects()* as static library
- *cmake*; [bug fix] export *bld.objects()* as static library


**v0.3.8**, 2014-11-13:

- issue9_; add *-pthread* option by default in gnucc and use it for export(*eclipse*, *makefiles*, *codeblocks*)
- *eclipse*; [bug fix] added shared system libs
- *eclipse*; added *eclipse_skipme* task generator option
- *codeblocks*; added *codeblocks_skipme* task generator option
- *cmake*; added *cmake_skipme* task generator option
- *msdev*; added *msdev_skipme* task generator option
- *codeblocks*, *cmake*; only export projects for selected targets (e.g. --targets=a,b,)


**v0.3.7**, 2014-11-12:

- *general*; added package dependency to *chardet*
- *ccross*; fix when using multiple cross compilers
- *cppcheck*; detect character encoding when parsing on source failed.


**v0.3.6**, 2014-11-10:

- *waftools*; added generic *waftools.recurse(ctx,trees=[])* function
- issue8_; check if options (e.g. *env*) exist in cross.ini file
- *ccross*; use normal compiler, linker and archvier if no prefix has been specified in ccross.ini
- *eclipse*; added generation of launchers

**v0.3.5**, 2014-11-09:

- *ccross*; specify configuration file (cross.ini) using command line argument
- *ccross*; added support for defining environment variables in 'cross.ini'
- *wafinstall*; allways create 'extras' directory (required for 'compiler_c' tool)


**v0.3.4**, 2014-11-06:

- *msdev*, *makefile*; only export projects for selected targets (e.g. --targets=a,b,)
- *wafinstall*; by default do not install files from waflib/Tools/extras (i.e. --tools=None), add missing __init__.py file to waflib/Tools/extras.


**v0.3.3**, 2014-11-04:

- *wafinstall*; corrected detection of compression of the waf archive (gz or bz2)
- *makefile*; several fixes and improvements:

	- handle cflags in task generator being specified as string
	- added support for read_shlib()
	- only build C/C++ tasks
	- use correct makefile, build directory and libpaths for variants (cross-compile)
	
- *eclipse*; several fixes and improvements:

	- added support for library task generators exporting headers only (i.e. no source)
	- added missing external libraries in project; use 'lib' from task generator, added support for read_shlib(), a.k.a. *fake_lib*


**v0.3.2**, 2014-11-03:

- issue5_; fixed detection of (cross)compilers in *ccross* module when using waf-1.8.x


**v0.3.1**, 2014-10-30:

- issue4_; added missing package files ('msdev.sln' and 'doxy.config')
- *wafinstall*; improved/revised *waf* install script (beta)


**v0.3.0**, 2014-10-23:

- *wafinstall*; added install script, can be used to install the *waf* build system


**v0.2.0**, 2014-10-15:

- *general*; added support for waf-1.8.x, several fixes for environment variables being changed to type(list)
- *ccross*; use new *unity* and *batched_cc* tools from waf-1.8.x when available


**v0.1.8**, 2014-10-11:

- *general*; updated package trove classifiers in setup.py
- *indent*; new module uses GNU indent in order to clean-up and format C/C++ source code
- *documentation*; improved detailed description of modules


**v0.1.7**, 2014-10-06:

- *makefile*, *codeblocks*, *eclipse*; added support for multiple build environments (cross-compile)
- *codeblocks*; added support for multiple build environments (cross-compile)
- *eclipse*; changed export, now only export settings defined within the environment


**v0.1.6**, 2014-09-03:

- *makefile*; corrected creation of relative source paths and fixed a problem when using underscores in directory or task names
- *cppcheck*; fixed broken hyperlinks when using firefox web browser


**v0.1.5**, 2014-08-24:

- *general*; corrected download url in setup.py
- *general*; always use *tgz* format for released packages
- *gnucc*; new module containing GNU C/C++ compiler specific configuration settings
- *examples*; updated build scripts in 'playground'


**v0.1.4**, 2014-08-18:

- *depends*, *tree*; renamed *depends* module into *tree*
- *documenation*; added *tree* to package description
- *waftools*; added 'location' variable (i.e. 'waftools.location')
- *msdev*, *eclipse*, *cmake*, *codeblocks*, *make*; improved export speed
- issue2_, issue3_; improved installation path of package data files (e.g. msdev.sln) 
- *msdev*, *cmake*, *codeblocks*; fixed export on Windows


**v0.1.3**, 2014-07-21:

- *license*; changed license to MIT
- *documentation*; updated and improved detailed description of modules
- *msdev*, *eclipse*, *cmake*, *codeblocks*, *make*; improved export function
- *eclipse*; improved export when using MinGW on Windows


**v0.1.2**, 2014-07-01:

- *eclipse*; improved export when *includes* and *use* tgen arguments are specified as string intead of list
- *codeblocks*; use LIBPATH and INCLUDES dependencies, added pthread linker option
- *depend*; new module that allows users to get an overview of dependencies between tasks
- *doxygen*; new module that allows users to create C/C++ source documentation


**v0.1.1**, 2014-05-10:

- *codeblocks*; added extra check when parsing dependencies (*use*)
- *msdev*; added extra check when parsing dependencies (*use*)
- *eclipse*; added extra check when parsing dependencies (*use*)
- *cppcheck*; added extra check on C/C++ sources containing non human readable characters


**v0.1.0**, 2014-04-08:

- *msdev*; added export function of C/C++ tasks to Visual Studio projects.


**v0.0.9**, 2014-04-01:

- initial release.


.. _issue2: https://bitbucket.org/Moo7/waftools/issue/2/exception-when-exporting-to-msdev
.. _issue3: https://bitbucket.org/Moo7/waftools/issue/3/exception-when-exporting-to-msdev
.. _issue4: https://bitbucket.org/Moo7/waftools/issue/4/msdevsln-not-included-in-the-latest
.. _issue5: https://bitbucket.org/Moo7/waftools/issue/5/detecting-cross-compiler-fails
.. _issue6: https://bitbucket.org/Moo7/waftools/issue/6/eclipse-tools-fail-when-not-using-c
.. _issue8: https://bitbucket.org/Moo7/waftools/issue/8/module-crosspy-fails-in-v035
.. _issue9: https://bitbucket.org/Moo7/waftools/issue/9/eclipse-missing-pthread
.. _issue11: https://bitbucket.org/Moo7/waftools/issue/11/cmake-export-fails-when-using-bldobjects
.. _issue12: https://bitbucket.org/Moo7/waftools/issue/12/makefile-export-fails-when-using
.. _issue13: https://bitbucket.org/Moo7/waftools/issue/13/package-version-045-install-fails-on
.. _issue14: https://bitbucket.org/Moo7/waftools/issue/14/eclipse-generation-does-not-generate
.. _issue16: https://bitbucket.org/Moo7/waftools/issues/16/msdev-for-visual-studio-100-external-lib
.. _issue17: https://bitbucket.org/Moo7/waftools/issue/17/command-line-macro-defines-are-not
 
