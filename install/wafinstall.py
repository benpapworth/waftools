#!/usr/bin/env python
import os
import sys
import stat
import subprocess
import shutil
import tarfile
try:
	from urllib.request import urlopen
except ImportError:
	from urllib2 import urlopen


WAF_REL = "waf-1.8.2"
WAF_PKG = "%s.tar.bz2" % WAF_REL
PREFIX = "C:/programs/" if sys.platform=="win32" else "~/.local/bin"


def download(url, saveto):
	u = f = None
	try:
		print("downloading %s" % url)
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
	if name.endswith('.gz') or name.endswith('.tgz'):
		compression = 'gz'
	else:
		compression = 'bz2'
	
	t = tarfile.open(name, 'r:%s' % compression)
	for member in t.getmembers():
		print(member.name)
		t.extract(member, path=path)
	

if __name__ == "__main__":
	dst = PREFIX
	rel = WAF_REL
	pkg = WAF_PKG
	url = "http://ftp.waf.io/pub/release/%s" % pkg
	tools = "batched_cc,unity"
	# TODO: add command line options
	
	download(url, pkg)
	untar(pkg)
	
	top = os.getcwd()
	try:	
		cmd = "python waf-light --make-waf --tools=%s" % tools
		cwd = "./%s" % WAF_REL
		subprocess.check_call(cmd.split(), cwd=cwd)
	finally:
		os.chdir(top)

	os.mkdirs(dst)		
	if sys.platform == "win32":
		shutil.move("./%s" % rel, dst)
		# TODO: add environment path
		# new winreg module in python 3.x OR
		# use pywin32 OR 
		# add manually
	else:
		shutil.copy("./%s/waf" % rel, "%s/waf" % dst)
		os.chmod("%s/waf" % dst, stat.S_IRWXU)
		# TODO: add environment path (~/.bashrc)
		
	


		
