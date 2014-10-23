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

OPTIONS:
	-h | --help		prints this help message.
	
	-n archive | --name=archive
					specify the name of the archive to extact.

	-p location | --path=location
					specify the extraction location.
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
try:
	from urllib.request import urlopen
except ImportError:
	from urllib2 import urlopen


WAF_VERSION = "1.8.2"
WAF_TOOLS = "unity,batched_cc"

HOME = os.path.expanduser('~')
PREFIX = "D:\\programs" if sys.platform=="win32" else "~/.local/bin"


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


def install(release, prefix):
	'''installs waf at the given location.'''
	logging.info("installing: %s" % release)
	if not os.path.exists(prefix):
		os.makedirs(prefix)

	if sys.platform == "win32":
		dest = os.path.join(prefix, release)
		if os.path.exists(dest):
			shutil.rmtree(dest)
		shutil.move(release, prefix)
	else:
		waf = str("%s/waf" % prefix).replace('~', HOME)
		shutil.copy("./%s/waf" % release, waf)
		os.chmod(waf, stat.S_IRWXU)


def set_path(release, prefix):
	'''adds the waf install location to the PATH system environment variable.'''
	if sys.platform == "win32":
		win32_env_path(os.path.join(prefix, release))
	else:
		linux_env_path(prefix)


def win32_env_path(path):
	'''adds the waf install location to the PATH system environment variable.'''
	logging.info("updating registry")
	path = path.replace('/','\\').rstrip('\\')
	try:
		import winreg
	except ImportError:
		logging.error("setting path(%s) failed, please add it manually." % path)
		return

	reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
	key = winreg.OpenKey(reg, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_ALL_ACCESS)
	try:
		(paths, type) = winreg.QueryValueEx(key, "Path")
		if path in [p.replace('/','\\').rstrip('\\') for p in paths.split(';')]:
			logging.info("path '%s' already exists." % (path))
			return
		winreg.SetValueEx(key, "Path", 0, type, paths + ';' + path)
		logging.info("path '%s' added to registry." % path)
	finally:
		winreg.CloseKey(key)
	logging.warning("path will be available after system reboot or next login.")


def linux_env_path(path):
	'''adds the waf install location to '~/.bashrc'.'''
	name = os.path.join(HOME, '.bashrc')

	with open(name, 'r') as f:
		for line in list(f):
			if line.startswith('export PATH=') and line.count(path):
				logging.warning("path '%s' already exists in '%s'" % (path, name))
				return

	logging.info("updating '%s'" % name)
	with open(name, 'r+') as f:
		f.seek(-2, 2)
		s = f.read(2) 
		if s == '\n\n': 
			f.seek(-1, 1) # remove double newline
		e = 'export PATH=$PATH:%s\n' % path
		if s[1] != '\n':
			e = '\n' + e
		f.write(e)


def get_options(argv):
	'''returns a tuple of command line options (prefix,version,tools).'''
	prefix = PREFIX
	version = WAF_VERSION
	tools = WAF_TOOLS

	try:
		opts, args = getopt.getopt(argv[1:], 'hv:p:t:', ['help', 'version=', 'prefix=', 'tools='])
	except getopt.GetoptError as err:
		print(str(err))
		usage()
		raise err

	for o, a in opts:
		if o in ('-h', '--help'):
			usage()
			sys.exit()
		elif o in ('-v', '--version'):
			version = a
		elif o in ('-p', '--prefix'):
			prefix = a.replace('\\', '/').rstrip('/')
		elif o in ('-t', '--tools'):
			tools = a

	return (prefix,version,tools)


def main(argv=sys.argv, level=logging.INFO):
	logging.basicConfig(level=level)

	try:
		(prefix, version, tools) = get_options(argv)
	except getopt.GetoptError as err:
		return 2

	release = "waf-%s" % version
	package = "%s.tar.bz2" % release
	url = "http://ftp.waf.io/pub/release/%s" % package
	logging.info("WAF version=%s, prefix=%s, tools=%s, url=%s" % (version, prefix, tools, url))

	top = os.getcwd()
	tmp = tempfile.mkdtemp()
	try:
		os.chdir(tmp)
		logging.debug('chdir(%s)' % os.getcwd())
		download(url, package)
		deflate(package)
		create(release, tools)
		install(release, prefix)
		set_path(release, prefix)
	finally:
		os.chdir(top)
		logging.debug('chdir(%s)' % os.getcwd())
		logging.debug('rmtree(%s)' % tmp)
		shutil.rmtree(tmp)
	logging.info("COMPLETE")
	return 0


if __name__ == "__main__":
	main()


