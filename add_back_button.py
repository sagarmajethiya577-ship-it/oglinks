import os

POSTS_DIR = "Posts"

for root, dirs, files in os.walk(POSTS_DIR):
    for file in files:
        if not file.endswith(".html"):
            continue

        path = os.path.join(root, file)

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if 'class="back-btn"' in content:
            continue

        if "<body>" in content:
            new_content = content.replace(
                "<body>",
                '<body>\n<a href="../../index.html" class="back-btn">← Back</a>\n',
                1
            )

            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)

            print("✅ Back button added:", path)

print("🎉 Back button process complete")
