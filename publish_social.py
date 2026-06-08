#!/usr/bin/env python3
"""Upload photos from an Ente export directory to Cloudinary.

Outputs a flat list of image URLs in data/social.json.

Usage:
  python3 publish_social.py --dir ~/EnteExport/
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
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

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

def save_tracking(t):
    os.makedirs(os.path.dirname(TRACKING_FILE), exist_ok=True)
    with open(TRACKING_FILE, "w") as f:
        json.dump(t, f, indent=2)

def configure():
    if cloudinary is None:
        print("Run: pip install cloudinary", file=sys.stderr)
        sys.exit(1)
    k = os.getenv("CLOUDINARY_API_KEY")
    s = os.getenv("CLOUDINARY_API_SECRET")
    if not k or not s:
        print("Set CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET in .env", file=sys.stderr)
        sys.exit(1)
    cloudinary.config(cloud_name=CLOUD_NAME, api_key=k, api_secret=s, secure=True)

def upload(path):
    configure()
    r = cloudinary.uploader.upload(path, folder=FOLDER, use_filename=True,
                                    unique_filename=True, resource_type="image")
    return f"https://res.cloudinary.com/{CLOUD_NAME}/image/upload/w_1200,f_auto,q_auto/v{r['version']}/{r['public_id']}"

def find_images(root):
    for dirpath, _, files in os.walk(root):
        for f in sorted(files):
            if os.path.splitext(f)[1].lower() in IMAGE_EXTS:
                yield os.path.join(dirpath, f)

def main():
    parser = argparse.ArgumentParser(description="Upload photos to Cloudinary")
    parser.add_argument("--dir", required=True, help="Directory with photos")
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        print(f"Directory not found: {args.dir}", file=sys.stderr)
        sys.exit(1)

    tracking = load_tracking()
    urls = []

    for f in find_images(args.dir):
        key = os.path.relpath(f, args.dir)
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
