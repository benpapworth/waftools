#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com

import os

version = "0.1.5"
location = os.path.dirname(__file__)


def get_scripts(top, name):
	'''Returns a list of top level paths containing the specified file name.
	
	:param: top: root where the search should be started.
	:type top: str
	:param: name: name of the file to be found.
	:type name: str
	'''
	locations = []
	for cwd, _, files in os.walk(top):
		for f in files:
			if os.path.basename(f) != name:
				continue
			locations.append(cwd)
	scripts = []
	for loc in locations:
		if any(os.path.dirname(loc).endswith(t) for t in locations):
			continue
		scripts.append(loc)
	return scripts

