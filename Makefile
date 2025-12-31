.PHONY: all style ty style-check lint deps

package?=notes

all: deps

style:
	python -m black $(package)
	python -m ruff check $(package)
	python -m isort $(package)

ty:
	python -m ty check $(package)

style-check:
	python -m black --check --diff $(package)
	python -m ruff check $(package)
	python -m isort --check --diff $(package)

lint: style ty

deps:
	pip install -U ty ruff black isort
