#!/usr/bin/env python3
import json, math, html as htmlmod

with open("data/gallery.json") as f:
    items = json.load(f)

total = len(items)
per_page = 12
num_pages = math.ceil(total / per_page)

def thumb_url(url):
    return url.replace("w_2000", "w_400")

radio_inputs = ""
page_rules = ""
pag_rules = ""
for pi in range(num_pages):
    checked = ' checked' if pi == 0 else ''
    radio_inputs += f'    <input type="radio" name="page" id="p{pi}"{checked}>\n'
    page_rules += f"#p{pi}:checked ~ .gallery #page{pi} {{ display: grid; }}\n"
    pag_rules += f"#p{pi}:checked ~ .pagination label[for=\"p{pi}\"] {{background: #666; color: #fff; border-color: #666; }}\n"

pages_html = ""
items_in_page = 0
page_idx = 0
for i, item in enumerate(items):
    if items_in_page == 0:
        pages_html += f'        <div class="page" id="page{page_idx}">\n'
    is_first_page = page_idx == 0
    if is_first_page:
        attrs = 'alt="" decoding="async" fetchpriority="high"'
    else:
        attrs = 'alt="" loading="lazy" decoding="async"'
    pages_html += f'            <a href="#img{i}" class="gallery-item"><img src="{htmlmod.escape(thumb_url(item["url"]))}" {attrs}></a>\n'
    items_in_page += 1
    if items_in_page == per_page or i == total - 1:
        placeholders = per_page - items_in_page
        for _ in range(placeholders):
            pages_html += '            <div class="gallery-placeholder"></div>\n'
        pages_html += '        </div>\n'
        items_in_page = 0
        page_idx += 1

# Pagination: left arrow, page buttons, right arrow
pagination_labels = f'        <label for="p0" class="page-arrow">&#10094;</label>\n'
for pi in range(num_pages):
    pagination_labels += f'            <label for="p{pi}" class="page-btn">{pi + 1}</label>\n'
pagination_labels += f'        <label for="p{num_pages - 1}" class="page-arrow">&#10095;</label>'

# Lightboxes
lightboxes = ""
for i, item in enumerate(items):
    page_of_img = i // per_page
    lightboxes += f'    <div class="view-full" id="img{i}">\n'
    lightboxes += f'        <a href="#page{page_of_img}" class="view-full-close">&times;</a>\n'
    if i > 0:
        lightboxes += f'        <a href="#img{i - 1}" class="view-full-nav view-full-prev">&#10094;</a>\n'
    if i < total - 1:
        lightboxes += f'        <a href="#img{i + 1}" class="view-full-nav view-full-next">&#10095;</a>\n'
    if i == 0 or i == total - 1:
        lightboxes += '\n'
    lightboxes += f'        <span class="view-full-counter">{i + 1} / {total}</span>\n'
    lightboxes += f'        <img src="{htmlmod.escape(item["url"])}" alt="">\n'
    lightboxes += '    </div>\n'

html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=0.70">
    <link rel="icon" type="image/png" href="images/icon.png">
    <link rel="stylesheet" href="modern-normalize.css">
    <link rel="stylesheet" href="style.css">
    <link rel="preconnect" href="https://res.cloudinary.com">
    <style>
{page_rules}{pag_rules}    </style>
    <script data-goatcounter="https://jctdrs.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
    <title>Gallery / jctdrs</title>
</head>
<body>
    <h4>Gallery</h4>

{radio_inputs}
    <div class="gallery">
{pages_html}    </div>

    <div class="pagination">
{pagination_labels}
    </div>

{lightboxes}
    <br>
    <hr>
    <nav>
        <a href="index.html" class="home-btn"><b>Home</b></a>
    </nav>
    <hr>
</body>
</html>
"""

with open("gallery.html", "w") as f:
    f.write(html_out)

print(f"Generated gallery.html with {total} photos across {num_pages} pages")
