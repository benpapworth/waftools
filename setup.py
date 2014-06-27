#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

from distutils.core import setup
import waftools

url = "https://bitbucket.org/Moo7/waftools"

with open('README.txt') as file:
	long_description = file.read()

setup(
	name = "waftools",
	packages = ["waftools"],
	version = waftools.version,
	description = "Handy tools for the WAF meta build environment",
	author = "Michel Mooij",
	author_email = "michel.mooij7@gmail.com",
	url = url,
	download_url = "%s/waftools-%s.zip" % (url, waftools.version),
	keywords = ["waf", "cppcheck", "codeblocks", "eclipse", "make", "cmake", "c", "c++", "msdev"],
	data_files = [('Lib/site-packages/waftools', ['waftools/msdev.sln', 'waftools/doxy.config'])],
	classifiers = [
		"Programming Language :: Python",
		"Development Status :: 4 - Beta",
		"Environment :: Other Environment",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
		"Operating System :: OS Independent",
		"Topic :: Software Development :: Libraries :: Python Modules",
		],
	long_description = long_description
)

