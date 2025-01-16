include ../../make/prelude.mk



# Interface & Implementation

.PHONY: prepare
prepare:
	npm install


.PHONY: build
build: guard-BUILD_OUTPUT
	npm run build
	tar \
		--transform "s/^\./frontend/" \
		-czf "$(BUILD_OUTPUT)/jean-loup-frontend.tar.gz" \
		--directory "./dist/" \
			"."