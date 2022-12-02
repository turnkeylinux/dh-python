#!/usr/bin/make -f

FALLBACK_FLAGS = $(shell dpkg-vendor --is ubuntu && echo '--ubuntu')

all: cpython3_fallback README.PyDist.html

clean:
	rm -rf cache
	#rm -f dist_fallback
	rm -f README.PyDist.html

cpython3_fallback:
	python3 ./generate_fallback_list.py $(FALLBACK_FLAGS)

README.PyDist.html: README.PyDist
	rst2html $< $@

.PHONY: clean
