#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Michel Mooij, michel.mooij7@gmail.com


'''
Summary
-------
Installs the WAF meta build system.

Description
-----------
Downloads the waf-x.y.z.tar.bz2 archive, extracts it, builds the
waf executable and installs it (e.g. in ~/.local/bin). Depending on 
the platform and python version the PATH environment variable will 
be updated as well.

Usage
-----
In order to install waf call:
	python wafinstall.py [options]

Available options:
	-h | --help		prints this help message.

	-v | --version	waf package version to install, e.g.
					-v1.8.2

	-t | --tools	comma seperated list of waf tools to be used
					default=unity,batched_cc
'''


import os
import sys
import stat
import subprocess
import shutil
import tarfile
import getopt
import tempfile
import logging
import site
try:
	from urllib.request import urlopen
except ImportError:
	from urllib2 import urlopen


WAF_VERSION = "1.8.2"
WAF_TOOLS = "unity,batched_cc"

HOME = os.path.expanduser('~')
BINDIR = os.path.join(sys.prefix, 'Scripts') if sys.platform=="win32" else "~/.local/bin"
LIBDIR = site.getusersitepackages()


def usage():
	print(__doc__)


def download(url, saveto):
	'''downloads the waf package.'''
	logging.info("downloading: %s" % url)
	try:
		u = urlopen(url)
		with open(saveto, 'wb') as f: f.write(u.read())
	finally:
		if u: u.close()
	return os.path.realpath(saveto)


def deflate(name, path='.'):
	'''deflates the waf archive.'''
	logging.info("deflating: %s" % name)
	c = 'gz' if os.path.splitext(name)[1] in ('gz', 'tgz') else 'bz2'
	with tarfile.open(name, 'r:%s' % c) as t:
		for member in t.getmembers():
			logging.debug(member.name)
			t.extract(member, path=path)


def create(release, tools):
	'''creates the waf binary.'''
	logging.info("creating: %s" % release)
	top = os.getcwd()
	try:
		cmd = "python waf-light --make-waf --tools=%s" % tools
		cwd = "./%s" % release
		subprocess.check_call(cmd.split(), cwd=cwd)
	finally:
		os.chdir(top)


def install(release, bindir, libdir):
	'''installs waf at the given location.'''
	logging.info("installing: %s" % release)

	if not os.path.exists(bindir):
		os.makedirs(bindir)

	waf = str(bindir + "/waf").replace('~', HOME)
	shutil.copy("./%s/waf" % release, waf)
	os.chmod(waf, stat.S_IRWXU)

	if not os.path.exists(libdir):
		os.makedirs(libdir)
	
	waflib = os.path.join(libdir, 'waflib')
	if os.path.exists(waflib):
		shutil.rmtree(waflib)
			
	shutil.move(os.path.join(release, 'waflib'), libdir)

	if sys.platform == "win32":
		shutil.copy("./%s/waf.bat" % release, waf + '.bat')
	
	env_set('PATH', bindir, extend=True)	
	env_set('WAFDIR', libdir)


def env_set(variable, value, extend=False):
	'''sets an environment variable.'''
	variable = variable.upper()
	if variable in os.environ:
		val = os.environ[variable]
		if extend:
			values = val.split(';' if sys.platform=='win32' else ':')
			if value in values:
				return
		elif val == value:
			return

	if sys.platform == "win32":
		win32_env_set(variable, value, extend)
	else:
		linux_env_set(variable, value, extend)


def win32_env_set(variable, value, extend=False):
	'''sets environment variable.'''
	try:
		import winreg
	except ImportError:
		logging.error("failed to set environment variable '%s'. please add it manually" % variable)
		return

	reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
	key = winreg.OpenKey(reg, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_ALL_ACCESS)

	(values, _) = winreg.QueryValueEx(key, variable)
	if values:
		if value in values.split(';'):
			logging.info("environment variable '%s' already set." % variable)
			return
		if extend:
			value = values + ';' + value

	try:
		winreg.SetValueEx(key, variable, 0, winreg.REG_SZ, value)
	finally:
		winreg.CloseKey(key)
	logging.info("environment variable '%s' set" % variable)


def linux_env_set(variable, value, extend=False):
	'''sets environment variable.'''
	name = os.path.join(HOME, '.bashrc')
	variable = variable.upper()

	with open(name, 'r') as f:
		for line in list(f):
			if line.startswith('export %s=' % variable) and line.count(value):
				logging.info("'%s' already set for '%s' in '%s'" % (value, variable, name))
				return

	export = 'export %s={0}%s\n' % (variable, value)
	export = export.format('$%s:' % variable if extend else '')

	with open(name, 'r+') as f:
		f.seek(-2, 2)
		s = f.read(2) 
		if s == '\n\n': f.seek(-1, 1) # remove double newline
		if s[1] != '\n': f.write('\n') # add missing newline
		f.write(export)
	logging.info("environment variable '%s' set" % variable)


def main(argv=sys.argv, level=logging.INFO):
	'''downloads, unpacks, creates and installs waf package.'''
	logging.basicConfig(level=level)

	version = WAF_VERSION
	tools = WAF_TOOLS
	bindir = BINDIR
	libdir = LIBDIR
	try:
		opts, args = getopt.getopt(argv[1:], 'hv:u:t:', ['help', 'version=', 'tools='])
	except getopt.GetoptError as err:
		print(str(err))
		usage()
		return 2

	for o, a in opts:
		if o in ('-h', '--help'):
			usage()
			sys.exit()
		elif o in ('-v', '--version'):
			version = a
		elif o in ('-t', '--tools'):
			tools = a

	release = "waf-%s" % version
	package = "%s.tar.bz2" % release
	url = "http://ftp.waf.io/pub/release/%s" % package
	logging.info("WAF version=%s, tools=%s, url=%s, bin=%s, lib=%s" % (version, tools, url, bindir, libdir))

	top = os.getcwd()
	tmp = tempfile.mkdtemp()	
	try:
		os.chdir(tmp)
		logging.debug('chdir(%s)' % os.getcwd())
		download(url, package)
		deflate(package)
		create(release, tools)
		install(release, bindir, libdir)
	finally:
		os.chdir(top)
		logging.debug('chdir(%s)' % os.getcwd())
		logging.debug('rmtree(%s)' % tmp)
		shutil.rmtree(tmp)
	logging.info("COMPLETE")
	return 0


if __name__ == "__main__":
	code = main(argv=sys.argv, level=logging.DEBUG)
	sys.exit(code)

