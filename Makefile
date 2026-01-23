.PHONY: all style ty style-check lint deps test

package?=notes

all: deps

style:
	python -m black $(package) tests
	python -m ruff check $(package) tests
	python -m isort $(package) tests

ty:
	python -m ty check $(package)

style-check:
	python -m black --check --diff $(package) tests
	python -m ruff check $(package) tests
	python -m isort --check --diff $(package) tests

lint: style ty

test:
	python -m pytest tests/ -v

deps:
	pip install -U ty ruff black isort pytest pytest-asyncio pytest-mock
