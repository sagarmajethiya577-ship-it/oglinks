import os
from bs4 import BeautifulSoup
import math
import json

POSTS_DIR = "Posts"
POSTS_PER_PAGE = 200

all_files = []
search_index = []

# 1. Scan and Index
for root, dirs, files in os.walk(POSTS_DIR):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)
            all_files.append(path)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    soup = BeautifulSoup(f, "html.parser")
                    img = soup.find("img")
                    img_src = img["src"] if img else ""
                    h1 = soup.find("h1")
                    title = h1.get_text(strip=True) if h1 else os.path.basename(path).replace(".html", "").replace("-", " ").title()
                    search_index.append({"t": title, "u": path.replace("\\", "/"), "i": img_src})
            except: continue

all_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
with open("search_data.json", "w", encoding="utf-8") as f:
    json.dump(search_index, f)

total_pages = math.ceil(len(all_files) / POSTS_PER_PAGE)

for page in range(total_pages):
    current_page = page + 1
    start, end = page * POSTS_PER_PAGE, (page + 1) * POSTS_PER_PAGE
    current_files = all_files[start:end]

    cards_html = ""
    for path in current_files:
        movie_data = next((item for item in search_index if item["u"] == path.replace("\\", "/")), None)
        if movie_data:
            cards_html += f'<a class="post-card" href="{movie_data["u"]}"><img src="{movie_data["i"]}"><h2>{movie_data["t"]}</h2></a>'

    # --- Smart Pagination Logic ---
    pagination = '<div class="pagination">'
    
    # Previous Button
    if current_page > 1:
        prev_link = "index.html" if current_page == 2 else f"page{current_page-1}.html"
        pagination += f'<a href="{prev_link}" class="page-btn">← Previous</a>'

    # Logic to show limited numbers
    visible_pages = []
    if total_pages <= 5:
        visible_pages = range(1, total_pages + 1)
    else:
        if current_page <= 3:
            visible_pages = [1, 2, 3, 4, "...", total_pages]
        elif current_page >= total_pages - 2:
            visible_pages = [1, "...", total_pages - 3, total_pages - 2, total_pages - 1, total_pages]
        else:
            visible_pages = [1, "...", current_page - 1, current_page, current_page + 1, "...", total_pages]

    for i in visible_pages:
        if i == "...":
            pagination += '<span class="dots">...</span>'
        else:
            active_class = "active" if i == current_page else ""
            link = "index.html" if i == 1 else f"page{i}.html"
            pagination += f'<a href="{link}" class="page-num {active_class}">{i}</a>'

    # Next Button
    if current_page < total_pages:
        pagination += f'<a href="page{current_page+1}.html" class="page-btn">Next →</a>'
    
    pagination += "</div>"

    # HTML Template (Design fix included)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Movie Zone 🍿</title>
<link rel="stylesheet" href="style.css">
<style>
    .pagination {{ display: flex; justify-content: center; align-items: center; gap: 5px; margin: 30px 10px; flex-wrap: wrap; }}
    .page-btn, .page-num {{ padding: 8px 12px; border: 1px solid #00ff88; color: #00ff88; text-decoration: none; border-radius: 4px; font-size: 14px; min-width: 35px; text-align: center; }}
    .page-num.active {{ background: #00ff88; color: #000; font-weight: bold; border-color: #00ff88; }}
    .dots {{ color: #00ff88; padding: 0 5px; }}
    .page-btn:hover, .page-num:hover:not(.active) {{ background: rgba(0, 255, 136, 0.1); }}
    @media (max-width: 600px) {{ .page-btn {{ font-size: 12px; padding: 6px 10px; }} }}
</style>
</head>
<body>
<header class="site-header"><a href="/" class="site-title">Movie Zone 🍿</a><p class="tagline">Latest Movies & Web Series</p></header>
<div class="search-box" style="text-align:center; margin: 20px 0;"><input type="text" id="searchInput" placeholder="Search all movies..." style="width: 90%; max-width: 500px; padding: 12px; border-radius: 8px; border: 1px solid #444; background: #222; color: white; outline: none;"></div>
<main class="home-container" id="postList">{cards_html}</main>
{pagination}
<footer class="site-footer">© 2026 Movies Zone 🍿 | All Rights Reserved</footer>
<script>
let movieData = [];
async function loadSearchData() {{ const res = await fetch('search_data.json'); movieData = await res.json(); }}
loadSearchData();
const input = document.getElementById("searchInput"), postList = document.getElementById("postList"), originalContent = postList.innerHTML;
input.addEventListener("input", function () {{
    const val = input.value.toLowerCase().trim();
    if (val.length < 2) {{ postList.innerHTML = originalContent; return; }}
    const res = movieData.filter(m => m.t.toLowerCase().includes(val));
    if (res.length > 0) {{ postList.innerHTML = res.map(m => `<a class="post-card" href="${{m.u}}"><img src="${{m.i}}"><h2>${{m.t}}</h2></a>`).join(""); }}
    else {{ postList.innerHTML = "<p style='color:white; text-align:center; width:100%;'>No movies found!</p>"; }}
}});
</script>
</body></html>"""
    
    filename = "index.html" if page == 0 else f"page{page+1}.html"
    with open(filename, "w", encoding="utf-8") as f: f.write(html)

print("✅ Fixed! Smart pagination is now active.")
