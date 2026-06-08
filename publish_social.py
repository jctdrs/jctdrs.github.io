#!/usr/bin/env python3
"""Upload all album directories from an Ente export to Cloudinary.

Outputs a flat list of image URLs in data/social.json.

Usage:
  python3 publish_social.py --export-dir ~/Pictures/Ente/
"""

import argparse, json, os, sys

try:
    import cloudinary, cloudinary.api, cloudinary.uploader
except ImportError:
    if "--help" not in sys.argv:
        print("Install cloudinary: pip install cloudinary", file=sys.stderr)
        sys.exit(1)
    cloudinary = None

ROOT = os.path.dirname(os.path.abspath(__file__))

def load_env():
    path = os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

load_env()

CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "dcsypb1xt")
FOLDER = "Social"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".gif"}
TRACKING_FILE = os.path.join(ROOT, "data", ".uploads.json")
OUTPUT_FILE = os.path.join(ROOT, "data", "social.json")

def load_tracking():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE) as f:
            return json.load(f)
    return {}

def save_tracking(tracking):
    os.makedirs(os.path.dirname(TRACKING_FILE), exist_ok=True)
    with open(TRACKING_FILE, "w") as f:
        json.dump(tracking, f, indent=2)

def configure():
    if cloudinary is None:
        print("Run: pip install cloudinary", file=sys.stderr)
        sys.exit(1)
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    if not api_key or not api_secret:
        print("Set CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET in .env", file=sys.stderr)
        sys.exit(1)
    cloudinary.config(cloud_name=CLOUD_NAME, api_key=api_key, api_secret=api_secret, secure=True)

def upload(path):
    configure()
    resp = cloudinary.uploader.upload(path, folder=FOLDER, use_filename=True,
                                      unique_filename=True, resource_type="image")
    return f"https://res.cloudinary.com/{CLOUD_NAME}/image/upload/w_1200,f_auto,q_auto/v{resp['version']}/{resp['public_id']}"

def collect_images(dir_path):
    return sorted(
        os.path.join(dir_path, f)
        for f in os.listdir(dir_path)
        if os.path.splitext(f)[1].lower() in IMAGE_EXTS
    )

def main():
    parser = argparse.ArgumentParser(description="Upload Ente export albums to Cloudinary")
    parser.add_argument("--export-dir", required=True, help="Ente export directory")
    args = parser.parse_args()

    if not os.path.isdir(args.export_dir):
        print(f"Directory not found: {args.export_dir}", file=sys.stderr)
        sys.exit(1)

    tracking = load_tracking()
    urls = []

    for entry in sorted(os.listdir(args.export_dir)):
        album_dir = os.path.join(args.export_dir, entry)
        if not os.path.isdir(album_dir):
            continue
        for f in collect_images(album_dir):
            key = entry + "/" + os.path.basename(f)
            if key in tracking:
                urls.append(tracking[key])
                print(f"  {key} … SKIP", file=sys.stderr)
            else:
                print(f"  {key} …", file=sys.stderr, end=" ")
                try:
                    url = upload(f)
                    urls.append(url)
                    tracking[key] = url
                    print("OK", file=sys.stderr)
                except Exception as e:
                    print(f"FAILED: {e}", file=sys.stderr)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(urls, f, indent=2)
    save_tracking(tracking)

    print(f"Done — {len(urls)} photo(s)", file=sys.stderr)

if __name__ == "__main__":
    main()
