#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import subprocess
import waftools

subprocess.call('waf distclean')
subprocess.call('waf configure')
subprocess.call('waf build')

subprocess.call('git tag -a v{0} -m "release {0}"'.format(waftools.version))
subprocess.call('git push origin --tags')

subprocess.call('python setup.py sdist upload')

