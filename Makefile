crate_name := spqr

dest := foo
subdir := SrcTranslated

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
		-subdir $(subdir) \
		$<

.PHONY: aeneas
aeneas: $(translation)

.PHONY: patch
patch:
	patch_aeneas.py $(dest)/$(subdir)

upstream_url := https://github.com/signalapp/SparsePostQuantumRatchet.git
upstream_rev := f2589fef855c10f39d72634dab3d14654dd410bf

.PHONY: diff
diff:
	git fetch $(upstream_url) $(upstream_rev)
	git diff $(upstream_rev) -- src
