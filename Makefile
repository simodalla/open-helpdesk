.PHONY: clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "testall - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "sdist - package"

clean: clean-build clean-pyc
	rm -fr htmlcov/

clean-build:
	rm -fr build/

	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

postgres-db:
	dropdb pytest_django$(UID); createdb pytest_django$(UID)

lint:
	flake8 --exclude=migrations,urls.py openhelpdesk tests

test:
	py.test tests

test-live:
	py.test -m livetest --livetest

test-all:
	tox

coverage:
	py.test --cov-report term-missing --cov openhelpdesk

coverage-live:
	py.test --livetest --cov-report term-missing --cov openhelpdesk

coverage-html:
	py.test --cov-report html --cov openhelpdesk
	open htmlcov/index.html

coverage-live-html:
	py.test --livetest --cov-report html --cov openhelpdesk
	open htmlcov/index.html

docs:
	rm -f docs/open-helpdesk.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ open-helpdesk
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

sdist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist
