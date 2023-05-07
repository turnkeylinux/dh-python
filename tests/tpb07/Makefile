#!/usr/bin/make -f
include ../common.mk

check:
	test -f debian/python3-foo/usr/lib/python3/dist-packages/foo/__init__.py
	test -f debian/python3-bar/usr/lib/python3/dist-packages/bar/__init__.py
	test -f debian/python3-foo/usr/bin/foo
	test -f debian/python3-bar/usr/bin/bar
	test -e foo/tests-executed-foo

clean:
	./debian/rules clean
