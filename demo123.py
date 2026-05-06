import os
import json
import math

POSTS_PER_PAGE = 200
JSON_PREFIX = "posts"   # posts1.json, posts2.json...

all_posts = []

# 🔹 Load all JSON files
json_files = sorted([f for f in os.listdir() if f.startswith(JSON_PREFIX) and f.endswith(".json")])

for file in json_files:
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            all_posts.extend(data)
    except:
        continue

# 🔹 Reverse (latest first)
all_posts = list(reversed(all_posts))

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
            <button onclick="copyLink('{link}')">Copy Link</button>
        </div>
        """

    # 🔹 Pagination
    pagination = '<div class="pagination">'

    if current_page > 1:
        prev = "index.html" if current_page == 2 else f"page{current_page-1}.html"
        pagination += f'<a href="{prev}">←</a>'

    for i in range(1, total_pages + 1):
        link = "index.html" if i == 1 else f"page{i}.html"
        active = "active" if i == current_page else ""
        pagination += f'<a href="{link}" class="{active}">{i}</a>'

    if current_page < total_pages:
        pagination += f'<a href="page{current_page+1}.html">→</a>'

    pagination += "</div>"

    # 🔹 HTML Template (NO HEADER / NO SEARCH)
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Links Zone</title>

<style>
body {{ background:#111; margin:0; font-family:sans-serif; }}

.home-container {{
display:grid;
grid-template-columns: repeat(auto-fill, minmax(150px,1fr));
gap:10px;
padding:10px;
}}

.post-card {{
background:#1c1c1c;
border-radius:10px;
overflow:hidden;
text-align:center;
}}

.post-card img {{
  width:100%;
  aspect-ratio: 2/3;
  object-fit: contain;
  background:#000;
}}

.post-card button {{
width:90%;
margin:10px;
padding:8px;
border:none;
border-radius:6px;
background:#00ff88;
color:#000;
font-weight:bold;
}}

.pagination {{
display:flex;
justify-content:center;
gap:5px;
margin:20px;
flex-wrap:wrap;
}}

.pagination a {{
padding:6px 10px;
border:1px solid #00ff88;
color:#00ff88;
text-decoration:none;
}}

.pagination .active {{
background:#00ff88;
color:#000;
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
    alert("Copied!");
}}
</script>

</body>
</html>
"""

    filename = "index.html" if page == 0 else f"page{page+1}.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

print("✅ Done! Multi JSON system ready.")
