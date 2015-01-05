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


.. note::
	the complete documentation for the package can be found at
	http://pythonhosted.org/waftools


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


Support
-------
Defects and/or feature requests can be reported at bitbucket_.
    

.. _waf: https://code.google.com/p/waf/
.. _wafbook: http://docs.waf.googlecode.com/git/book_18/single.html
.. _bitbucket: https://bitbucket.org/Moo7/waftools/issues

