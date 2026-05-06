import os
import shutil
import math

SOURCE_DIR = "/storage/emulated/0/vegamovies_post"
DEST_DIR = "Posts"
FILES_PER_FOLDER = 990
LIMIT = 15000   # 🔥 Yaha limit set karo

os.makedirs(DEST_DIR, exist_ok=True)

# Sirf root ke html files lo
files = [
    f for f in os.listdir(SOURCE_DIR)
    if f.endswith(".html") and os.path.isfile(os.path.join(SOURCE_DIR, f))
]

# 🔥 Latest files first (mtime ke basis par)
files.sort(
    key=lambda x: os.path.getmtime(os.path.join(SOURCE_DIR, x)),
    reverse=True
)

# 🔥 Sirf 15k lo
files = files[:LIMIT]

total_folders = math.ceil(len(files) / FILES_PER_FOLDER)

for i in range(total_folders):
    folder_path = os.path.join(DEST_DIR, f"p{i+1}")
    os.makedirs(folder_path, exist_ok=True)

    start = i * FILES_PER_FOLDER
    end = start + FILES_PER_FOLDER
    chunk = files[start:end]

    for file in chunk:
        shutil.copy(
            os.path.join(SOURCE_DIR, file),
            os.path.join(folder_path, file)
        )

print(f"✅ {len(files)} files copied & divided into {total_folders} folders successfully!")
