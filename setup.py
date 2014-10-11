#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com


import sys
import site
from distutils.core import setup
import distutils.sysconfig
import waftools


url = "https://bitbucket.org/Moo7/waftools"

with open('README.txt') as f:
	long_description = f.read()

if "--user" in sys.argv:
	data_dir = '%s/waftools' % site.getusersitepackages()
else:
	data_dir = '%s/waftools' % distutils.sysconfig.get_python_lib()

setup(
	name = "waftools",
	packages = ["waftools"],
	version = waftools.version,
	description = "Handy tools for the WAF meta build environment",
	author = "Michel Mooij",
	author_email = "michel.mooij7@gmail.com",
	url = url,
	download_url = "%s/downloads/waftools-%s.tar.gz" % (url, waftools.version),
	keywords = ["waf", "cppcheck", "codeblocks", "eclipse", "make", "cmake", "c", "c++", "msdev", "doxygen"],
	data_files = [(data_dir, ['waftools/msdev.sln', 'waftools/doxy.config'])],
	classifiers = [
		"Development Status :: 4 - Beta",		
		"Environment :: Console",
		"Environment :: Win32 (MS Windows)",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Operating System :: Microsoft :: Windows :: Windows 7",
		"Operating System :: Microsoft :: Windows :: Windows Vista",
		"Operating System :: Microsoft :: Windows :: Windows XP",
		"Operating System :: POSIX :: Linux",
		"Programming Language :: C",
		"Programming Language :: C++",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
		"Topic :: Software Development :: Build Tools",
		"Topic :: Software Development :: Embedded Systems",
		"Topic :: Utilities",
		],
	long_description = long_description
)
