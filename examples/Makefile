#------------------------------------------------------------------------------
# WAFTOOLS generated makefile
# version: 0.1.4
# waf: 1.7.15
#------------------------------------------------------------------------------

SHELL=/bin/sh

# commas, spaces and tabs:
sp:= 
sp+= 
tab:=$(sp)$(sp)$(sp)$(sp)
comma:=,

# token for separating dictionary keys and values:
dsep:=;

# token for separating list elements:
lsep:=,

export APPNAME:=waftest
export APPVERSION:=0.6.2
export PREFIX:=$(CURDIR)/output
export TOP:=$(CURDIR)
export OUT:=$(TOP)/build
export AR:=/usr/bin/ar
export CC:=/usr/lib64/ccache/gcc
export CXX:=/usr/lib64/ccache/g++
export CFLAGS:=-Wall -O3
export CXXFLAGS:=-Wall -O3
export DEFINES:=NDEBUG
export RPATH:=
export BINDIR:=$(PREFIX)/bin
export LIBDIR:=$(PREFIX)/lib

SEARCHPATH=components/
SEARCHFILE=Makefile

#------------------------------------------------------------------------------
# list of unique logical module names;
modules= \
	cleaking \
	cxxshlib \
	ciambad \
	cstlib \
	chello \
	cprogram \
	cxxstlib \
	cxxhello \
	cmath \
	cxxprogram \
	cshlib

# dictionary of modules names (key) and paths to modules;
paths= \
	cleaking;components/cleaking \
	cxxshlib;components/cxxlib/shared \
	ciambad;components/ciambad \
	cstlib;components/clib/static \
	chello;components/chello \
	cprogram;components/clib/program \
	cxxstlib;components/cxxlib/static \
	cxxhello;components/cxxhello \
	cmath;components/cmath \
	cxxprogram;components/cxxlib/program \
	cshlib;components/clib/shared

# dictionary of modules names (key) and module dependencies;
deps= \
	cleaking; \
	cxxshlib; \
	ciambad;cleaking \
	cstlib; \
	chello; \
	cprogram;cstlib,cshlib \
	cxxstlib; \
	cxxhello; \
	cmath; \
	cxxprogram;cxxstlib,cxxshlib \
	cshlib;

#------------------------------------------------------------------------------
# define targets
#------------------------------------------------------------------------------
build_targets=$(addprefix build_,$(modules))
clean_targets=$(addprefix clean_,$(modules))
install_targets=$(addprefix install_,$(modules))
uninstall_targets=$(addprefix uninstall_,$(modules))

cmds=build clean install uninstall
commands=$(sort $(cmds) all help find list modules $(foreach prefix,$(cmds),$($(prefix)_targets)))

.DEFAULT_GOAL:=all

#------------------------------------------------------------------------------
# recursive wild card implementation
#------------------------------------------------------------------------------
define rwildcard
$(wildcard $1$2) $(foreach d,$(wildcard $1*),$(call rwildcard,$d/,$2))
endef

#------------------------------------------------------------------------------
# returns the value from a dictionary
# $1 = key, where key is the functional name of the component.
# $2 = dictionary
#------------------------------------------------------------------------------
define getdval
$(subst $(lastword $(subst _,$(sp),$1))$(dsep),$(sp),$(filter $(lastword $(subst _,$(sp),$1))$(dsep)%,$2))
endef

#------------------------------------------------------------------------------
# returns path to makefile
# $1 = key, where key is the functional name of the component.
#------------------------------------------------------------------------------
define getpath
$(call getdval, $1, $(paths))
endef

#------------------------------------------------------------------------------
# returns component dependencies.
# $1 = key, where key is the functional name of the component.
#------------------------------------------------------------------------------
define getdeps
$(addprefix $(firstword $(subst _,$(sp),$1))_,$(subst $(lsep),$(sp),$(call getdval, $1, $(deps))))
endef

#------------------------------------------------------------------------------
# creates a make recipe:
#      'make -r -C <path> -f <name>.mk <command>'
# where:
#      <path>     is the relative path to the component
#      <name>     is the name of the component
#      <command>  is the make action to be executed, e.g. build, install, clean
#
# $1 = key, where key is the functional recipe name (e.g. build_a).
#------------------------------------------------------------------------------
define domake
$1: $(call getdeps, $1)
	$(MAKE) -r -C $(call getpath,$1) -f $(lastword $(subst _,$(sp),$1)).mk $(firstword $(subst _,$(sp),$1))
endef

#------------------------------------------------------------------------------
# return files found in given search path
# $1 = search path
# $2 = file name so search
#------------------------------------------------------------------------------
define dofind
$(foreach path, $(dir $(call rwildcard,$1,$2)),echo "  $(path)";)
endef

#------------------------------------------------------------------------------
# definitions of recipes (i.e. make targets)
#------------------------------------------------------------------------------
all: build
	
build: $(build_targets)

clean: $(clean_targets)

install: build $(install_targets)

uninstall: $(uninstall_targets)

list:
	@echo ""
	@$(foreach cmd,$(commands),echo "  $(cmd)";)
	@echo ""

modules:
	@echo ""
	@$(foreach module,$(modules),echo "  $(module)";)
	@echo ""

find:
	@echo ""
	@echo "$@:"
	@echo "  path=$(SEARCHPATH) file=$(SEARCHFILE)"
	@echo ""
	@echo "result:"
	@$(call dofind,$(SEARCHPATH),$(SEARCHFILE))
	@echo ""

help:
	@echo ""
	@echo "$(APPNAME) version $(APPVERSION)"
	@echo ""
	@echo "usage:"
	@echo "  make [-r] [-s] [--jobs=N] [command] [VARIABLE=VALUE]"
	@echo ""
	@echo "commands:"
	@echo "  all                                 builds all modules"
	@echo "  build                               builds all modules"
	@echo "  build_a                             builds module 'a' and it's dependencies"
	@echo "  clean                               removes all build intermediates and outputs"
	@echo "  clean_a                             cleans module 'a' and it's dependencies"
	@echo "  install                             installs files in $(PREFIX)"
	@echo "  install_a                           installs module 'a' and it's dependencies"
	@echo "  uninstall                           removes all installed files from $(PREFIX)"
	@echo "  uninstall_a                         removes module 'a' and it's dependencies"
	@echo "  list                                list available make commands (i.e. recipes)"
	@echo "  modules                             list logical names of all modules"
	@echo "  find [SEARCHPATH=] [SEARCHFILE=]    searches for files default(path=$(SEARCHPATH),file=$(SEARCHFILE))"
	@echo "  help                                displays this help message."
	@echo ""
	@echo "remarks:"
	@echo "  use options '-r' and '--jobs=N' in order to improve speed"
	@echo "  use options '-s' to decrease verbosity"
	@echo ""

$(foreach t,$(build_targets),$(eval $(call domake,$t)))

$(foreach t,$(clean_targets),$(eval $(call domake,$t)))

$(foreach t,$(install_targets),$(eval $(call domake,$t)))

$(foreach t,$(uninstall_targets),$(eval $(call domake,$t)))

.PHONY: $(commands)

