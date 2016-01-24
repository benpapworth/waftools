#!/usr/bin/sh
set -e

cwd=`pwd`
dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

minimal=false
full=false
cross=false

oprefix=$HOME/.local/share/openwrt
ourl="http://downloads.openwrt.org/barrier_breaker/14.07/ar71xx/mikrotik"
orel="OpenWrt-Toolchain-ar71xx-for-mips_34kc-gcc-4.8-linaro_uClibc-0.9.33.2"
opkg=$orel.tar.bz2

environment='python3-pip python3-virtualenv python3-wheel
    python3-chardet python3-pygments python3-jinja2
    wget indent sphinx python3-sphinx
    mingw64-gcc mingw64-gcc-c++'

programs='eclipse-pydev eclipse-pydev-mylyn eclipse-cdt
    codeblocks meld cppcheck doxygen cmake'

fname=$(basename "${BASH_SOURCE[0]}")
name="${fname%.*}"
usage="usage:
    $name <options>

description:
    Install development tools and programs for waftools on Fedora
    a-like distributions using DNF package manager.
    
    By default the script will only install development environment
    and tools. Use the full option to also install development
    programs.
    
options:
    -c  install crosscompiler(s) used for testing
    -e  install development environment tools
    -f  full installation including development programs (e.g eclipse)
    -o  openwrt crosscompiler install prefix (default=$oprefix)
    -h  displays this help
"

pathadd()
{
	if [[ "$PATH" =~ (^|:)"${2}"(:|$) ]]
	then
		return 0
	fi
	export PATH=${2}:$PATH
	echo 'export PATH=$PATH:'${2} >> ${1}
	source ${1}
}

while getopts ":cfmo:h" opt; do
	case $opt in
		c)
			cross=true
			;;
		f)
			minimal=true
			full=true
			;;
		m)
			minimal=true
			;;
		o)
		    oprefix=$OPTARG
			;;
		h)
		    echo "$usage"
		    exit
		    ;;
		\?)
		    echo "$usage"
			exit 1
			;;
	esac
done

if [ "$minimal" = true ]
then
    echo "--> installing development environment..."
    sudo dnf -y groupinstall "C Development Tools and Libraries"
    sudo dnf -y install $environment
    echo "--> installing pypi tools..."
    pip3 install twine --user --upgrade
    pip3 install sphinx-rtd-theme --user --upgrade
fi

if [ "$full" = true ]
then
    echo "--> installing development programs..."
    sudo dnf -y install $programs
fi

if [ "$cross" = true ]
then
    if [ ! -d $oprefix ]
    then
        echo "--> install openwrt mips cross-compiler..."
        otmp=`mktemp -d`
        cd $otmp
        wget $ourl/$opkg
        tar jxvf $opkg
        mkdir -p $oprefix
        mv $orel/* $oprefix
        cd $cwd
        rm -rf $otmp
    else
        echo "--> WARNING: openwrt prefix $oprefix exists, skipping install."
    fi
    oexp="$oprefix/toolchain-mips_34kc_gcc-4.8-linaro_uClibc-0.9.33.2/bin"
    pathadd $HOME/.bash_profile "$oexp"
fi

echo "--> done."

