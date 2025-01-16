include ../../make/prelude.mk

.DEFAULT_GOAL := all

PACKAGES := $(shell find packages -mindepth 1 -maxdepth 1 -type d -exec basename {} \;)

BUILD_FOLDER := build

PACKAGE_NAME_PREFIX := jean-loup


# Interface

.PHONY: prepare
prepare: sync-packages


.PHONY: build
build: build-packages



# Implementation

.PHONY: sync-packages
sync-packages:
	@ uv sync --all-packages

.PHONY: build-packages
build-packages: guard-BUILD_OUTPUT
	uv build \
		--all-packages \
		--sdist \
		--out-dir "$(BUILD_OUTPUT)"
	rm -rf "$(BUILD_OUTPUT)/.gitignore"


.PHONY: check-packages
check-packages: $(patsubst %, check-package-%, $(PACKAGES))

.PHONY: $(filter check-package-%,$(MAKECMDGOALS))
check-package-%: $(filter check-package-%,$(MAKECMDGOALS))
	@ uv run \
		--package "$(PACKAGE_NAME_PREFIX)-$*" \
		--directory "packages/$*" \
		ruff check --fix "./src"


.PHONY: test-packages
test-packages: $(patsubst %, test-package-%, $(PACKAGES))

.PHONY: $(filter test-package-%,$(MAKECMDGOALS))
test-package-%: $(filter test-package-%,$(MAKECMDGOALS))
	@ uv run \
		--package "$(PACKAGE_NAME_PREFIX)-$*" \
		--directory "packages/$*" \
			pytest