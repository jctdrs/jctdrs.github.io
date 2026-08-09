PYTHON := ./venv/bin/python
ALBUMS ?= Gallery,Granada,Astro

.PHONY: update export publish generate

## update: export albums from Ente, upload new photos, regenerate gallery.html
update:
	$(PYTHON) -m scripts.update

## export: sync the given albums from Ente (defaults to all)
export:
	ente-cli export --albums "$(ALBUMS)"

## publish: upload new photos to Cloudinary and write data JSONs (no export)
publish:
	$(PYTHON) -m scripts.publish_gallery --skip-export

## generate: rebuild gallery.html from data JSONs
generate:
	$(PYTHON) -m scripts.generate_gallery
