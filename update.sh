#!/usr/bin/env bash
# Pull new photos from Ente for every album, upload them to Cloudinary,
# and regenerate gallery.html. Run this after adding a photo to any album.
#
# Usage: ./update.sh
set -euo pipefail
cd "$(dirname "$0")"

PY=./venv/bin/python
ALBUMS=(Gallery Granada Astro)

for album in "${ALBUMS[@]}"; do
    echo "== Exporting $album =="
    ente-cli export --albums "$album"
    echo "== Rebuilding metadata for $album =="
    "$PY" scripts/rebuild_meta.py "$album"
    echo "== Publishing $album =="
    "$PY" publish_gallery.py "$album" --skip-export
done

echo "== Regenerating gallery.html =="
"$PY" generate_gallery.py
echo "Done."
