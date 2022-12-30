all: run check

run:
	@echo No build needed

check:
	DH_VERBOSE=1 pybuild-autopkgtest
	test -e custom-test-executed

clean:
	./debian/rules clean
