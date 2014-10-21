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
try:
	from urllib.request import urlopen
except ImportError:
	from urllib2 import urlopen


WAF_VERSION = "1.8.2"
PREFIX = "D:\\programs" if sys.platform=="win32" else "~/.local/bin"


def usage():
	print(__doc__)


def download(url, saveto):
	u = f = None
	try:
		print("downloading: %s" % url)
		u = urlopen(url)
		f = open(saveto, 'wb')
		f.write(u.read())
		print("done")
	finally:
		if u:
			u.close()
		if f:
			f.close()
	return os.path.realpath(saveto)


def untar(name, path='.'):
	print("deflating: %s" % name)
	if name.endswith('.gz') or name.endswith('.tgz'):
		compression = 'gz'
	else:
		compression = 'bz2'

	t = tarfile.open(name, 'r:%s' % compression)
	for member in t.getmembers():
		print(member.name)
		t.extract(member, path=path)
	print("done")
	

def create(release, tools):
	print("creating: %s" % release)
	top = os.getcwd()
	try:
		cmd = "python waf-light --make-waf --tools=%s" % tools
		cwd = "./%s" % release
		subprocess.check_call(cmd.split(), cwd=cwd)
	finally:
		os.chdir(top)
		print("done")


def install(release, prefix):
	print("installing: %s" % release)
	if not os.path.exists(prefix):
		os.makedirs(prefix)

	if sys.platform == "win32":
		dest = os.path.join(prefix, release)
		if os.path.exists(dest):
			shutil.rmtree(dest)
		shutil.move(release, prefix)
		win32_set_path(os.path.join(prefix, release))
	else:
		shutil.copy("./%s/waf" % release, "%s/waf" % prefix)
		os.chmod("%s/waf" % prefix, stat.S_IRWXU)
		# TODO: add environment path (~/.bashrc)
	print("done")


def win32_set_path(path):
	print("updating registry")
	path = path.replace('/','\\').rstrip('\\')
	try:
		import winreg
	except ImportError:
		print("setting path(%s) failed, please add it manually." % path)
		return

	reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
	key = winreg.OpenKey(reg, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_ALL_ACCESS)
	try:
		(paths, type) = winreg.QueryValueEx(key, "Path")
		if path in [p.replace('/','\\').rstrip('\\') for p in paths.split(';')]:
			print("path '%s' already exists." % (path))
			return
		winreg.SetValueEx(key, "Path", 0, type, paths + ';' + path)
		print("path '%s' added to registry." % path)
	finally:
		winreg.CloseKey(key)
		print("path will be available after system reboot or next login.")


def main():
	prefix = PREFIX
	version = WAF_VERSION
	tools = "batched_cc,unity"

	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hv:p:t:', ['help', 'version=', 'prefix=', 'tools='])
	except getopt.GetoptError as err:
		print(str(err))
		usage()
		sys.exit(2)

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

	release = "waf-%s" % version
	package = "%s.tar.bz2" % release
	url = "http://ftp.waf.io/pub/release/%s" % package

	top = os.getcwd()
	tmp = tempfile.mkdtemp()
	try:
		os.chdir(tmp)
		print('chdir(%s)' % os.getcwd())
		download(url, package)
		untar(package)
		create(release, tools)
		install(release, prefix)
	finally:
		os.chdir(top)
		print('chdir(%s)' % os.getcwd())
		print('rmtree(%s)' % tmp)
		shutil.rmtree(tmp)


if __name__ == "__main__":
	main()


