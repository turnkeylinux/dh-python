#!/usr/bin/make -f
include ../common.mk

check:
	test -f debian/python3-foo/usr/lib/python3/dist-packages/foo.py
	test -f debian/python3-foo-ext/usr/lib/python3/dist-packages/_foo.abi3.so
	test -e test-executed

clean:
	./debian/rules clean
