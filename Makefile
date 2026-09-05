.PHONY: none
none:

.PHONY: charon
charon:
	charon cargo \
		--preset=aeneas \
		--hide-marker-traits \
		-- \
		--features extraction
