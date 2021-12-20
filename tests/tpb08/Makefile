all: run check

run:
	@echo No build needed

check: pass fail

pass:
	@echo "=============================================================="
	@echo "= pybuild-autopkgtest passes when tests pass                 ="
	@echo "=============================================================="
	@echo
	pybuild-autopkgtest
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
