#!/usr/bin/env python3
import json, math, html as htmlmod

per_page = 15

albums = [
    {"slug": "gallery", "title": "Gallery", "rpre": "p", "ppre": "page", "lpre": "img", "rname": "page"},
    {"slug": "granada", "title": "Granada", "rpre": "gp", "ppre": "gpage", "lpre": "gimg", "rname": "gpage"},
    {"slug": "astro", "title": "Astro", "rpre": "ap", "ppre": "apage", "lpre": "aimg", "rname": "apage"},
]

def load_items(slug):
    try:
        with open(f"data/{slug}.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def thumb_url(url):
    return url.replace("w_2000", "w_400")

def build_section(items, rpre, ppre, lpre, rname, high_priority=False):
    total = len(items)
    num_pages = math.ceil(total / per_page) if total else 0

    radio_inputs = ""
    page_rules = ""
    pag_rules = ""
    for pi in range(num_pages):
        checked = ' checked' if pi == 0 else ''
        radio_inputs += f'    <input type="radio" name="{rname}" id="{rpre}{pi}"{checked}>\n'
        page_rules += f"#{rpre}{pi}:checked ~ .gallery #{ppre}{pi} {{ display: grid; }}\n"
        pag_rules += f"#{rpre}{pi}:checked ~ .pagination label[for=\"{rpre}{pi}\"] {{background: #666; color: #fff; border-color: #666; }}\n"

    pages_html = ""
    items_in_page = 0
    page_idx = 0
    for i, item in enumerate(items):
        if items_in_page == 0:
            pages_html += f'        <div class="page" id="{ppre}{page_idx}">\n'
        if page_idx == 0 and high_priority:
            attrs = 'alt="" decoding="async" fetchpriority="high"'
        else:
            attrs = 'alt="" loading="lazy" decoding="async"'
        pages_html += f'            <a href="#{lpre}{i}" class="gallery-item"><img src="{htmlmod.escape(thumb_url(item["url"]))}" {attrs}></a>\n'
        items_in_page += 1
        if items_in_page == per_page or i == total - 1:
            placeholders = per_page - items_in_page
            for _ in range(placeholders):
                pages_html += '            <div class="gallery-placeholder"></div>\n'
            pages_html += '        </div>\n'
            items_in_page = 0
            page_idx += 1

    prev_arrows = ""
    next_arrows = ""
    arrow_rules = ""
    for pi in range(num_pages):
        if pi == 0:
            prev_arrows += '            <label class="page-arrow prev prev-boundary">&#10094;</label>\n'
            arrow_rules += f"#{rpre}{pi}:checked ~ .pagination .prev-boundary {{ display: inline-block; }}\n"
        else:
            prev_arrows += f'            <label for="{rpre}{pi - 1}" class="page-arrow prev prev-{pi}">&#10094;</label>\n'
            arrow_rules += f"#{rpre}{pi}:checked ~ .pagination .prev-{pi} {{ display: inline-block; }}\n"
        if pi == num_pages - 1:
            next_arrows += '            <label class="page-arrow next next-boundary">&#10095;</label>\n'
            arrow_rules += f"#{rpre}{pi}:checked ~ .pagination .next-boundary {{ display: inline-block; }}\n"
        else:
            next_arrows += f'            <label for="{rpre}{pi + 1}" class="page-arrow next next-{pi}">&#10095;</label>\n'
            arrow_rules += f"#{rpre}{pi}:checked ~ .pagination .next-{pi} {{ display: inline-block; }}\n"

    pagination = prev_arrows
    for pi in range(num_pages):
        pagination += f'            <label for="{rpre}{pi}" class="page-btn">{pi + 1}</label>\n'
    pagination += next_arrows[:-1]

    lightboxes = ""
    for i, item in enumerate(items):
        page_of_img = i // per_page
        lightboxes += f'    <div class="view-full" id="{lpre}{i}">\n'
        lightboxes += f'        <a href="#{ppre}{page_of_img}" class="view-full-close">&times;</a>\n'
        if i > 0:
            lightboxes += f'        <a href="#{lpre}{i - 1}" class="view-full-nav view-full-prev">&#10094;</a>\n'
        if i < total - 1:
            lightboxes += f'        <a href="#{lpre}{i + 1}" class="view-full-nav view-full-next">&#10095;</a>\n'
        lightboxes += f'        <span class="view-full-counter">{i + 1} / {total}</span>\n'
        lightboxes += f'        <img src="{htmlmod.escape(item["url"])}" alt="">\n'
        lightboxes += '    </div>\n'

    return {
        "radio_inputs": radio_inputs,
        "page_rules": page_rules,
        "pag_rules": pag_rules,
        "arrow_rules": arrow_rules,
        "pages_html": pages_html,
        "pagination": pagination,
        "lightboxes": lightboxes,
    }

sections = []
included = []
buttons = ""
tabs = ""
page_rules = ""
pag_rules = ""
arrow_rules = ""
first = True
for album in albums:
    items = load_items(album["slug"])
    if not items:
        continue
    sec = build_section(items, album["rpre"], album["ppre"], album["lpre"], album["rname"], high_priority=first)
    sections.append(sec)
    included.append(album)
    page_rules += sec["page_rules"]
    pag_rules += sec["pag_rules"]
    arrow_rules += sec["arrow_rules"]
    active = ' active' if first else ''
    buttons += f'        <button class="toggle-btn{active}" onclick="changeContent(\'{album["slug"]}\', event)">{album["title"]}</button>\n'
    tabs += f'    <div id="{album["slug"]}" class="content-paragraph{active}">\n'
    tabs += sec["radio_inputs"] + '    <div class="gallery">\n'
    tabs += sec["pages_html"] + '    </div>\n\n'
    tabs += '    <div class="pagination">\n' + sec["pagination"] + '    </div>\n\n'
    tabs += sec["lightboxes"] + '    </div>\n\n'
    first = False

navbar = '    <div class="navbar">\n' + buttons + '    </div>\n'

tab_css = """
.navbar { margin: 1rem 0; }
.navbar button {
    font-size: 1rem;
    border: 2px solid #999;
    cursor: pointer;
    padding: 0.3rem 0.6rem;
    background: none;
}
.navbar button:hover { background-color: rgba(0,0,0,0.05); }
.navbar button.active { background-color: #fff; box-shadow: 0 0 0 3px rgba(0,0,0,0.1); }
.content-paragraph { display: none; }
.content-paragraph.active { display: block; }
.content-paragraph input[type="radio"] { display: none; }
"""

tab_js = """
<script>
function changeContent(targetId, event) {
    const button = event.target.closest('button');
    const nav = button.closest('.navbar');
    nav.querySelectorAll('button').forEach(b => b.classList.remove('active'));
    button.classList.add('active');

    const target = document.getElementById(targetId);
    if (!target) return;

    const parent = target.parentNode;
    parent.querySelectorAll('.content-paragraph').forEach(element => {
        element.style.display = 'none';
        element.classList.remove('active');
    });
    target.style.display = 'block';
    target.classList.add('active');

    const firstRadio = target.querySelector('input[type="radio"]');
    if (firstRadio) firstRadio.checked = true;
}
</script>
"""

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
{page_rules}{pag_rules}{arrow_rules}{tab_css}    </style>
    <meta name="description" content="Photo gallery.">
    <script data-goatcounter="https://jctdrs.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
    <title>Gallery / jctdrs</title>
{tab_js}</head>
<body>
    <h1>Gallery</h1>

{navbar}
{tabs}    <br>
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

for album in included:
    print(f"Added {album['title']} tab with {len(load_items(album['slug']))} photos")
print(f"Generated gallery.html with {len(sections)} album tab(s)")
