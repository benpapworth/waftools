#!/usr/bin/sh
set -e

dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
full=false

environment='python3-pip python3-virtualenv python3-wheel
    python3-chardet python3-pygments python3-jinja2
    wget indent sphinx python3-sphinx
    mingw64-gcc mingw64-gcc-c++' 

programs='eclipse-pydev eclipse-pydev-mylyn eclipse-cdt
    codeblocks meld cppcheck doxygen cmake'

fname=`basename "$0"`
fname="${fname%.*}"
usage="usage:
    $fname <options>

description:
    Install development tools and programs for waftools on Fedora
    alike distributions.
    By default the script will only install development environment
    and tools. Use the full option to also install development
    programs.
    
options:
    -f  full installation including development programs (e.g eclipse)
    -o  install openwrt crosscompiler (default=)
    -h  displays this help
"

while getopts ":foh" opt; do
	case $opt in
		f)
			echo "--> installing additional programs" >&2
			full=true
			;;
			
		h)
		    echo "$usage"
		    exit
		    ;;
		\?)
			echo "invalid option command line option '-$OPTARG'." >&2
			echo "  option  description"
			echo "  -a      install additional programs (e.g. cppcheck)."
			echo "  -y      autoinstall additional programs."
			exit 1
			;;
	esac
done

echo "--> installing required development packages..."
sudo dnf -y groupinstall "C Development Tools and Libraries"
sudo dnf -y install $environment

if [ "$full" = true ]
then
    echo "--> installing development programs..."
    sudo dnf -y install $programs
fi

echo "--> installing pypi tools..."
pip3 install twine --user 
pip3 install sphinx-rtd-theme --user

exit 1
##TODO: clean me up

echo "--> install openwrt mips cross-compiler..."
url="http://downloads.openwrt.org/barrier_breaker/14.07/ar71xx/mikrotik"
release="OpenWrt-Toolchain-ar71xx-for-mips_34kc-gcc-4.8-linaro_uClibc-0.9.33.2"
package=$release.tar.bz2
tmp=`mktemp -d`
dst=$HOME/.local/share/openwrt
cd $tmp
wget $url/$package
tar jxvf $package
mkdir $HOME/.local/share/openwrt
mv $release/* $dst
cd $HOME
rm -rf $tmp
echo 'export PATH=$PATH:~/.local/share/openwrt/toolchain-mips_34kc_gcc-4.8-linaro_uClibc-0.9.33.2/bin' >> $HOME/.bashrc





