#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com


# TODO:
# 	copy setup.py/script tricks from Pygments
#	https://bitbucket.org/birkenfeld/pygments-main

import sys
import site
from setuptools import setup
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
	install_requires = ["pygments"],
	version = waftools.version,
	description = "Handy tools for the WAF meta build environment",
	author = "Michel Mooij",
	author_email = "michel.mooij7@gmail.com",
	license = 'MIT',
	url = url,
	download_url = "%s/downloads/waftools-%s.tar.gz" % (url, waftools.version),
	keywords = ["waf", "cppcheck", "codeblocks", "eclipse", "make", "cmake", "c", "c++", "msdev", "doxygen"],
	platforms = 'any',
	data_files = [(data_dir, ['waftools/msdev.sln', 'waftools/doxy.config'])],
	entry_points = {
		'console_scripts': [
			'wafinstall = waftools.wafinstall:main',
		],
	},
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

