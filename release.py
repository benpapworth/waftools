#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com


'''
Description
-----------
Create a new release, performs following steps: 
- build package and documentation using waf (distclean, configure, build, distclean)
- tags and publishes the release using git
- creates and upoloads the package to PyPi
'''


import subprocess
import waftools

subprocess.call(['waf', 'distclean'])
subprocess.call(['waf', 'configure'])
subprocess.call(['waf', 'build'])
subprocess.call(['waf', 'distclean'])

v = str(waftools.version)
subprocess.call(['git', 'tag', '-a', 'v%s' % v, '-m', '"release %s"' % v])
subprocess.call(['git', 'push', 'origin', '--tags'])

subprocess.call(['python', 'setup.py', 'sdist', 'upload'])

