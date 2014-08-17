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

#------------------------------------------------------------------------------
# definition of build and install locations
#------------------------------------------------------------------------------
ifeq ($(TOP),)
TOP=$(CURDIR)
OUT=$(TOP)/build
else
OUT=$(subst $(sp),/,$(call rptotop) build $(call rpofcomp))
endif

#------------------------------------------------------------------------------
# component data
#------------------------------------------------------------------------------
LIB=libcxxstlib.a
OUTPUT=$(OUT)/$(LIB)

# REMARK: use $(wildcard src/*.cpp) to include all sources.
SOURCES= \
	src/cxxstlib.cpp 

OBJECTS=$(SOURCES:.cpp=.1.o)

DEFINES+=
DEFINES:=$(addprefix -D,$(DEFINES))

INCLUDES+= \
	./include

HEADERS:=$(foreach inc,$(INCLUDES),$(wildcard $(inc)/*.h))
INCLUDES:=$(addprefix -I,$(INCLUDES))

CXXFLAGS+=

ARFLAGS=rcs

#------------------------------------------------------------------------------
# returns the relative path of this component from the top directory
#------------------------------------------------------------------------------
define rpofcomp
$(subst $(subst ~,$(HOME),$(TOP))/,,$(CURDIR))
endef

#------------------------------------------------------------------------------
# returns the relative path of this component to the top directory
#------------------------------------------------------------------------------
define rptotop
$(foreach word,$(subst /,$(sp),$(call rpofcomp)),..)
endef

#------------------------------------------------------------------------------
# define targets
#------------------------------------------------------------------------------
commands= build clean install uninstall all

.DEFAULT_GOAL=all

#------------------------------------------------------------------------------
# definitions of recipes (i.e. make targets)
#------------------------------------------------------------------------------
all: build
	
build: $(OBJECTS)
	$(AR) $(ARFLAGS) $(OUTPUT) $(addprefix $(OUT)/,$(OBJECTS))

clean:
	$(foreach obj,$(OBJECTS),rm -f $(OUT)/$(obj);)	
	rm -f $(OUTPUT)

install:
	
uninstall:

$(OBJECTS): $(HEADERS)
	mkdir -p $(OUT)/$(dir $@)
	$(CXX) $(CXXFLAGS) $(INCLUDES) $(DEFINES) $(subst .1.o,.cpp,$@) -c -o $(OUT)/$@

.PHONY: $(commands)

