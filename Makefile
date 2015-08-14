_all: doc sdist

doc: doc/source/*
	sphinx-build -b html doc/source doc/build/html

sdist: lifx/*.py
	./setup.py sdist

upload:
	./setup.py sdist upload

doc-upload: doc
	./setup.py upload_sphinx

