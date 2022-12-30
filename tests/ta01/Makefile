all: run check

run:
	@echo No build needed
ifeq ($(AUTOPKGTEST_TMP),)
	@echo NOTE this test uses the system pybuild-autopkgtest, not the working directory
endif

check: pass fail

pass:
	@echo "=============================================================="
	@echo "= pybuild-autopkgtest passes when tests pass                 ="
	@echo "=============================================================="
	@echo
	pybuild-autopkgtest
	test -f marker-before-pybuild-autopkgtest
	test -f marker-after-pybuild-autopkgtest
	grep '^1$$' marker-PYBUILD_AUTOPKGTEST
	@echo '------------------------------'
	@echo "OK: pybuild-autopkgtest passed"
	@echo '------------------------------'
	@echo

fail:
	@echo "=============================================================="
	@echo "= pybuild-autopkgtest fails when tests fail                  ="
	@echo "=============================================================="
	@echo
	! FAILS=1 pybuild-autopkgtest
	@echo '------------------------------'
	@echo "OK: pybuild-autopkgtest failed"
	@echo '------------------------------'
	@echo

clean:
ifneq ($(AUTOPKGTEST_TMP),)
	rm -r $(AUTOPKGTEST_TMP)/*
endif
