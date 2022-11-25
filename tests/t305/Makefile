#!/usr/bin/make -f

include ../common.mk
clean: clean-common

check:
	grep -qe "Depends: .*python3\(:any\)\?" debian/foo5a/DEBIAN/control
	grep -qe "Depends: .*python3\(:any\)\?" debian/foo5b/DEBIAN/control
	grep -qe "Depends: .*python3\(:any\)\?" debian/foo5c/DEBIAN/control
	grep -qe "Depends: .*python3\(:any\)\?" debian/foo5d/DEBIAN/control
	grep -qe "Depends: .*python3\(:any\)\?" debian/foo5e/DEBIAN/control
	grep -qe "Depends: .*python3\(:any\)\?" debian/foo5f/DEBIAN/control
	grep -Fxq dh_python3 debian/foo5a.debhelper.log.end_dh_install
	grep -Fxc dh_python3 debian/foo5a.debhelper.log.end_dh_install | grep -Fxq 1
