#!/usr/bin/env python3
"""Export Gallery album from Ente and upload photos to Cloudinary."""

import json, os, subprocess
from pathlib import Path
from dotenv import load_dotenv

import cloudinary
import cloudinary.uploader

load_dotenv()

ROOT = Path(__file__).resolve().parent
FOLDER = "Gallery"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".gif"}
TRACKING = ROOT / "data" / ".uploads.json"
OUTPUT = ROOT / "data" / "gallery.json"
PHOTO_DIR = (Path.home() / "Pictures" / "Ente" / "Gallery").resolve()

def run_export():
    print("Exporting Gallery album from Ente…")
    subprocess.run(["ente-cli", "export", "--albums", "Gallery"], check=True)

def load_tracking():
    return json.loads(TRACKING.read_text()) if TRACKING.exists() else {}

def sorted_photos(directory):
    meta_dir = directory / ".meta"
    photos = []
    for path in sorted(directory.iterdir()):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
            continue
        meta = meta_dir / f"{path.name}.json"
        taken_at = json.loads(meta.read_text()).get("creationTime", "") if meta.exists() else ""
        photos.append((path, taken_at))
    photos.sort(key=lambda x: x[1], reverse=True)
    return photos

def upload(path):
    CLOUD_NAME = os.environ["CLOUDINARY_CLOUD_NAME"]
    cloudinary.config(
        cloud_name=CLOUD_NAME,
        api_key=os.environ["CLOUDINARY_API_KEY"],
        api_secret=os.environ["CLOUDINARY_API_SECRET"],
        secure=True,
    )
    r = cloudinary.uploader.upload(path, folder=FOLDER, use_filename=True, unique_filename=True, resource_type="image")
    return f"https://res.cloudinary.com/{CLOUD_NAME}/image/upload/w_2000,f_auto,q_auto/v{r['version']}/{r['public_id']}"

def save_tracking(t):
    TRACKING.parent.mkdir(parents=True, exist_ok=True)
    TRACKING.write_text(json.dumps(t, indent=2))

def main():
    run_export()

    tracking = load_tracking()
    entries = []

    for path, taken_at in sorted_photos(PHOTO_DIR):
        key = path.name
        if key in tracking:
            url = tracking[key]
            print(f"  {key} … SKIP")
        else:
            url = upload(str(path))
            tracking[key] = url
            print(f"  {key} … OK")
        entries.append({"url": url, "takenAt": taken_at})

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(entries, indent=2))
    save_tracking(tracking)
    print(f"Done — {len(entries)} photo(s)")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FAILED: {e}")
