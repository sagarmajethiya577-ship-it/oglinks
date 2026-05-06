import os
import json
import math

POSTS_PER_PAGE = 200
JSON_PREFIX = "posts"

all_posts = []

# Load JSON
json_files = sorted([f for f in os.listdir() if f.startswith(JSON_PREFIX) and f.endswith(".json")])

for file in json_files:
    try:
        with open(file, "r") as f:
            data = json.load(f)
            all_posts.extend(data)
    except:
        pass

# 🔥 SORT BY TIME (LATEST FIRST)
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
            <button onclick="copyLink('{link}')">Copy Link</button>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {{ background:#111; }}

.home-container {{
display:grid;
grid-template-columns: repeat(auto-fill, minmax(150px,1fr));
gap:10px;
}}

.post-card img {{
width:100%;
height:auto;
}}
</style>
</head>
<body>

<div class="home-container">
{cards_html}
</div>

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

    with open(filename, "w") as f:
        f.write(html)

print("✅ Done! Sorted latest posts on top.")
