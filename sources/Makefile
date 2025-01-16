#!/usr/bin/make -f

include ./make/prelude.mk


.DEFAULT_GOAL := all

MODULES := $(shell \
	find \
		"modules" \
		-mindepth 2 \
		-maxdepth 2 \
		-type "f" \
		-name "module.mk" \
		-exec sh -c \
			'basename $$( dirname {} )' \
		\; \
)

BUILD_OUTPUT = "../packages/jean-loup"


.PHONY: all
all: prepare build



# Prepare

.PHONY: prepare
prepare: $(patsubst %, prepare-%, $(MODULES))


.PHONY: $(filter prepare-%,$(MAKECMDGOALS))
prepare-%: 
	@ $(MAKE) \
		-C "./modules/$*" \
		-f "./module.mk" \
			prepare



# Build

.PHONY: build
build: $(patsubst %, build-%, $(MODULES))


.PHONY: $(filter build-%,$(MAKECMDGOALS))
build-%: guard-BUILD_OUTPUT
	@ $(MAKE) \
		-C "./modules/$*" \
		-f "./module.mk" \
			build \
				BUILD_OUTPUT="$(shell realpath $(BUILD_OUTPUT) --relative-to "./modules/$*")"