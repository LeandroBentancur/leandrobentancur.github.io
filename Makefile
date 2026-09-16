# Each target is a ritual, not a build step. If you remember the ritual, you
# never have to remember the pipeline.
PY := python3

.PHONY: all site images check serve reconcile import-cvuy status clean

all: images check site             ## everything, in the right order

check:                             ## validate data/ — blocks on errors
	@$(PY) build/validate.py

site: check                        ## data/ + content/ -> docs/
	@$(PY) build/render_site.py

# The CVs are NOT built here. They read this data from ../cv-build, which is
# outside the repository because a CV is not something this site publishes:
#     cd ../cv-build && make

images:                            ## ../Pics originals -> assets/
	@$(PY) build/make_images.py

serve: site                        ## preview the built site at localhost:8000
	@echo "http://localhost:8000  (es at /es/)"; cd docs && $(PY) -m http.server 8000

import-cvuy:                       ## ANII export -> data/_cvuy_snapshot.yml
	@$(PY) build/import_cvuy.py

reconcile: import-cvuy             ## snapshot vs data -> reports/cvuy-drift.md
	@$(PY) build/reconcile.py

status:                            ## what is complete and what is still pending
	@$(PY) build/status.py

clean:
	@rm -rf docs reports && echo "removed generated output"
