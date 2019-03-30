##
#
# tw_projector handling 
#

NOSE := /usr/bin/nose2

all:
	@echo targets:
	@echo \* test -- run functional tests 

test: 
	${NOSE} --verbose --config nose2.cfg


