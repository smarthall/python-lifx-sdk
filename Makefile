_all: doc

doc: doc/source/*
	sphinx-build -b html doc/source doc/build/html
