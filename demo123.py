import os
import json
import math

POSTS_PER_PAGE = 20
JSON_PREFIX = "posts"

all_posts = []

# 🔹 Load JSON files
json_files = sorted([f for f in os.listdir() if f.startswith(JSON_PREFIX) and f.endswith(".json")])

for file in json_files:
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            all_posts.extend(data)
    except:
        continue

# 🔥 Latest post top par
all_posts.sort(key=lambda x: x.get("time", 0), reverse=True)

total_pages = math.ceil(len(all_posts) / POSTS_PER_PAGE)

for page in range(total_pages):
    current_page = page + 1
    start = page * POSTS_PER_PAGE
    end = start + POSTS_PER_PAGE
    current_posts = all_posts[start:end]

    cards_html = ""

    for post in current_posts:
        img = post.get("img", "")
        link = post.get("link", "")

        cards_html += f"""
        <div class="post-card">
            <img src="{img}">
            
            <button class="open-btn" onclick="openLink('{link}')">Open Link</button>
            <button class="copy-btn" onclick="copyLink('{link}')">Copy Link</button>
        </div>
        """

    # 🔹 Pagination
    pagination = '<div class="pagination">'

    if current_page > 1:
        prev = "index.html" if current_page == 2 else f"page{current_page-1}.html"
        pagination += f'<a href="{prev}" class="page-btn">←</a>'

    for i in range(1, total_pages + 1):
        link_page = "index.html" if i == 1 else f"page{i}.html"
        active = "active" if i == current_page else ""
        pagination += f'<a href="{link_page}" class="page-num {active}">{i}</a>'

    if current_page < total_pages:
        pagination += f'<a href="page{current_page+1}.html" class="page-btn">→</a>'

    pagination += "</div>"

    # 🔥 HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Links Zone</title>

<style>
body {{
    background:#111;
    margin:0;
    font-family:sans-serif;
}}

.home-container {{
    display:grid;
    grid-template-columns: repeat(auto-fill, minmax(160px,1fr));
    gap:12px;
    padding:12px;
}}

.post-card {{
    background:#1c1c1c;
    border-radius:10px;
    overflow:hidden;
    text-align:center;
    transition:0.2s;
}}

.post-card:hover {{
    transform:scale(1.03);
}}

.post-card img {{
    width:100%;
    height:auto;
    display:block;
}}

.post-card button {{
    width:90%;
    margin:6px;
    padding:8px;
    border:none;
    border-radius:6px;
    font-weight:bold;
    cursor:pointer;
}}

.open-btn {{
    background:#007bff;
    color:white;
}}

.open-btn:hover {{
    background:#0056b3;
}}

.copy-btn {{
    background:#00ff88;
    color:#000;
}}

.copy-btn:hover {{
    background:#00cc6a;
}}

.pagination {{
    display:flex;
    justify-content:center;
    gap:5px;
    margin:25px;
    flex-wrap:wrap;
}}

.page-btn, .page-num {{
    padding:8px 12px;
    border:1px solid #00ff88;
    color:#00ff88;
    text-decoration:none;
    border-radius:4px;
}}

.page-num.active {{
    background:#00ff88;
    color:#000;
    font-weight:bold;
}}
</style>

</head>

<body>

<div class="home-container">
{cards_html}
</div>

{pagination}

<script>
function copyLink(link) {{
    navigator.clipboard.writeText(link);
    alert("Link copied!");
}}

function openLink(link) {{
    window.open(link, "_blank");
}}
</script>

</body>
</html>
"""

    filename = "index.html" if page == 0 else f"page{page+1}.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

print("✅ Done! Open + Copy buttons added.")
