Installation
============
The preferred to install this package is by means of the Python package installer::

    pip install -I waftools [--user]

If this, for some reason does not work, you can allso clone the repository and install 
the package from it::

    cd ~
    git clone https://bitbucket.org/Moo7/waftools.git waftools
    pip install -e ~/waftools [--user]


Contained within the *waftools* package is a special install script which can be used to 
install the waf build system itself::

    wafinstall [--version=version] [--tools=compat15] [--user]

Using the *--tools* command line option, the *waf* tools to be installed from 
*waflib/Tools/extras* can be specified in a comma separated list. When omitted no 
tools from *extras* will be installed.

.. _waf: https://code.google.com/p/waf/
.. _wafbook: http://docs.waf.googlecode.com/git/book_18/single.html

