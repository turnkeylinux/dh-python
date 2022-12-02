#!/usr/bin/make -f

export DEBPYTHON3_DEFAULT ?= $(shell python3 ../../dhpython/_defaults.py default cpython3)
export DEBPYTHON3_SUPPORTED ?= $(shell python3 ../../dhpython/_defaults.py supported cpython3)
export DEB_HOST_MULTIARCH=my_multiarch-triplet
export DEB_HOST_ARCH ?= $(shell dpkg-architecture -qDEB_HOST_ARCH)
export DH_INTERNAL_OPTIONS=

all: run check

run: clean
	@echo ============================================================
	@echo ==== TEST: `basename $$PWD`
	dpkg-buildpackage -b -us -uc \
	  --no-check-builddeps \
	  --check-command="../test-package-show-info"

clean-common:
	./debian/rules clean
