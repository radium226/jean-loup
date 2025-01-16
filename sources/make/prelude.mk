SHELL := bash
.SHELLFLAGS := -euEo pipefail -c

.ONESHELL:



.PHONY: $(filter guard-%,$(MAKECMDGOALS))
guard-%:
	@ if [ "$(${*})" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi