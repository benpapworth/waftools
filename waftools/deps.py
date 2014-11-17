#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

import waflib
from waflib import Utils


def get_deps(bld, target):
	'''Returns a list of (nested) targets on which this target depends.
	
	:param bld: a *waf* build instance from the top level *wscript*
	:type bld: waflib.Build.BuildContext
	:param target: task name for which the dependencies should be returned
	:type target: str
	:returns: a list of task names on which the given target depends
	'''
	from waflib import Utils
	uses = Utils.to_list(getattr(bld.get_tgen_by_name(target), 'use', []))
	deps = uses[:]
	for use in uses:
		deps += get_deps(bld, use)
	return list(set(deps))


def get_targets(bld):
	'''Returns a list of user specified build targets or None if no specific
	build targets has been selected using the *--targets=* command line option.

	:param bld: a *waf* build instance from the top level *wscript*.
	:type bld: waflib.Build.BuildContext
	:returns: a list of user specified target names (using --targets=x,y,z) or None
	'''
	if bld.targets == '':
		return None
	targets = bld.targets.split(',')
	for target in targets:
		targets += get_deps(bld, target)
	return targets

