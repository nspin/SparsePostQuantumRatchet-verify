crate_name := spqr

dest := foo

translation := $(dest)/translation.json

.PHONY: none
none:

.PHONY: charon
charon:
	charon cargo \
		--preset=aeneas \
		--hide-marker-traits \
		-- \
		--features extraction

$(translation): $(crate_name).llbc
	aeneas \
		-backend lean \
		-split-files \
		-emit-json \
		-dest $(dest) \
		-subdir SrcTranslated \
		$<

.PHONY: aeneas
aeneas: $(translation)
