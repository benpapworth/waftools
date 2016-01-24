Summary
-------
This package contains a collection of tools for the waf_ build environment
intended for both native- as well cross compilation of C/C++ based projects.

Following provides a non-exhausting list of functions provided:

- Cross compile using several C/C++ cross compiler toolchains
- C/C++ export to makefiles (e.g. **make**, **cmake**)
- C/C++ export to IDE's (e.g. **Code::Blocks**, **Eclipse**, **Visual Studio**)
- C/C++ source code checking using **cppcheck** (including *html* reports)
- Clean and format C/C++ source code using **GNU** **indent**
- Create installers using **NSIS**
- Create C/C++ documentation using **DoxyGen**
- List dependencies between build tasks

A detailed description of *waftools* can be found at pythonhosted_.


Installation
------------
The *waftools* package can be installed using pip::

    pip install -I waftools [--user]
    wafinstall [--user]

Note that the last step will download and install the waf_ meta build system
as well.
As alternative you can also clone the repository and install the latest
revision::

    cd ~
    git clone https://bitbucket.org/Moo7/waftools.git waftools
    pip install -e ~/waftools [--user]
    wafinstall [--user]


Support
-------
If you have any suggestions for improvements and/or enhancements, please feel 
free to drop me a note by creating an issue_ at the waftools_ projects 
page.


.. _waf: https://waf.io
.. _wafbook: https://waf.io/book/
.. _issue: https://bitbucket.org/Moo7/waftools/issues
.. _pythonhosted: https://pythonhosted.org/waftools
.. _waftools: https://bitbucket.org/Moo7/waftools

