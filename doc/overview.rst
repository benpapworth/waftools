Overview
========
The *waftools* package contains a collection of tools for the waf_ build environment.

The waf_ framework provides a meta build system allowing users to create
concrete build systems. Out of the box it provides support for building and 
installation of programs for a myriad of programming languages (C, C++, Java, 
Python, Fortran, Lua, ...), when needed new functions (e.g. source code 
checking) can be added to a concrete build solution using *tools* which can be
imported and used in *wscript* build files. See the wafbook_ for a detailed 
description of the waf_ meta build system structure and usage.

The *waftools* package provides a collection of *tools* focused on development
projects using the C/C++ programming languages. When installed these tools can
be imported and used from any *wscript* file of a concrete waf_ build system.
Following provides a non-exhausting list of functions provided by this package:

- C/C++ source code checking using **CppCheck** (including *HTML* reports)
- Create C/C++ documentation using **DoxyGen**
- C/C++ export to IDE's (e.g. **CodeBlocks**, **Eclipse**, **VisualStudio**)
- Clean and format C/C++ source code using **GNU** indent
- Create installers using **NSIS**
- C/C++ export to makefiles (e.g. **make**, **cmake**)
- List dependencies between build tasks


.. _waf: https://waf.io/
.. _wafbook: https://waf.io/book

