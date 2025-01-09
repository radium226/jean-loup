#!/usr/bin/make -f

SHELL := bash
.SHELLFLAGS := -euEo pipefail -c

.ONESHELL:

.DEFAULT_GOAL := all


.PHONY: all
all:
	shellcheck -x "./jean-loup"