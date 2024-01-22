#!/usr/bin/make --file

SHELL := bash
.SHELLFLAGS := -euo pipefail -c

.ONESHELL:

.PHONY: default
default: all

.PHONY: all
all: check lint test

.PHONY: lint
lint:
	pdm run ruff "./src" "./tests"

.PHONY: check
check:
	pdm run mypy "./src" "./tests"

.PHONY: test
test:
	pdm run pytest -s "./tests"