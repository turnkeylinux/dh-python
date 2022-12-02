#!/usr/bin/make -f
include ../common.mk

check:
	# FIXME: This used to be a 2.7 + 3.x test. It may not be useful any more, without 2.x
	test -f debian/python3-foo/usr/lib/python3/dist-packages/foo.py
	grep -q 'Depends:.*python3-pkg-resources' debian/python3-foo/DEBIAN/control

clean:
	./debian/rules clean
