import os

POSTS_DIR = "Posts"

for root, dirs, files in os.walk(POSTS_DIR):
    for file in files:
        if not file.endswith(".html"):
            continue

        path = os.path.join(root, file)

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if "<html" in content.lower():
            continue

        title = file.replace(".html", "").replace("-", " ").title()

        new_html = f"""<!doctype html>
<html>
<head>
<meta charset="UTF-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="../../style.css">
</head>

<body>

<a href="../../index.html" class="back-btn">← Back</a>

<div class="post-container">

{content}

</div>

</body>
</html>
"""

        with open(path, "w", encoding="utf-8") as f:
            f.write(new_html)

        print("✅ Wrapped:", path)

print("🎉 All posts wrapped successfully")
