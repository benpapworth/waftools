#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

import os
import sys
from setuptools import setup
import waftools


url = "https://bitbucket.org/Moo7/waftools"
here = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(here,'README.rst')) as f:
	long_description = f.read()


setup(
	name = "waftools",
	version = waftools.version,
	author = "Michel Mooij",
	author_email = "michel.mooij7@gmail.com",
	maintainer = "Michel Mooij",
	maintainer_email = "michel.mooij7@gmail.com",
	url = url,
	download_url = "%s/downloads/waftools-%s.tar.gz" % (url, waftools.version),
	description = "Handy tools for the WAF meta build environment",
	long_description = long_description,
	packages = ["waftools"],
	install_requires = ["pygments", "chardet", "jinja2"],
	license = 'MIT',
	keywords = ["waf", "c", "c++", "cppcheck", "codeblocks", "eclipse", "make", "cmake", "msdev", "doxygen", "GNU indent"],
	platforms = 'any',
	package_data = { '': ['waftools/msdev.sln', 'waftools/doxy.config'] },
	include_package_data = True,
	entry_points = {
		'console_scripts': [
			['wafinstall = waftools.wafinstall:main'],
		],
	},
	classifiers = [
		"Development Status :: 4 - Beta",
		"Environment :: Console",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Operating System :: Microsoft :: Windows :: Windows 7",
		"Operating System :: Microsoft :: Windows :: Windows Vista",
		"Operating System :: Microsoft :: Windows :: Windows XP",
		"Operating System :: POSIX :: Linux",
		"Programming Language :: C",
		"Programming Language :: C++",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3.4",
		"Topic :: Software Development :: Build Tools",
		"Topic :: Software Development :: Embedded Systems",
		"Topic :: Utilities",
	],
)

