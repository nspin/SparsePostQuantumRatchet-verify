crate_name := spqr
llbc := $(crate_name).llbc

.PHONY: none
none:

.PHONY: $(llbc)
$(llbc):
	charon cargo \
		--preset=aeneas \
		--hide-marker-traits \
		-- \
		--features extraction

.PHONY: aeneas
aeneas: $(llbc)
	aeneas \
		-backend lean \
		-split-files \
    -emit-json \
  	-dest foo \
		-subdir SrcTranslated \
  	$<
