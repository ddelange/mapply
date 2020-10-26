.PHONY: lint
## Run linting
lint:
	pre-commit run --all-files

.PHONY: test
## Run tests
test:
	python -m pytest

.PHONY: showcov
## Open the test coverage overview using the default HTML viewer
showcov:
	xdg-open htmlcov/index.html || open htmlcov/index.html

.PHONY: install
## Install this repo, plus dev requirements, in editable mode
install:
	pip install -r requirements/ci.txt -r requirements/docs.txt
	pip install -e .
	pre-commit install

.PHONY: builddocs
## Build documentation using Sphinx
builddocs:
	cd docs && make docs

.PHONY: showdocs
## Open the docs using the default HTML viewer
showdocs:
	xdg-open docs/_build/html/index.html || open docs/_build/html/index.html

.PHONY: help
## Print Makefile documentation
help:
	@perl -0 -nle 'printf("%-25s - %s\n", "$$2", "$$1") while m/^##\s*([^\r\n]+)\n^([\w-]+):[^=]/gm' $(MAKEFILE_LIST) | sort
.DEFAULT_GOAL := help
