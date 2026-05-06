import os
import time

# --- CONFIGURATION ---
POSTS_DIR = "Posts"  # Main folder jisme p1, p2 folders hain
AD_CODE = """
<script>
const adConfig = {
    link: "https://moviezone-22y.pages.dev/", 
    expiry: 24 * 60 * 60 * 1000 
};

function openPopUnder() {
    const lastClick = localStorage.getItem('last_ad_click');
    const now = new Date().getTime();
    if (!lastClick || (now - lastClick) > adConfig.expiry) {
        const win = window.open(adConfig.link, '_blank');
        if (win) {
            win.blur();
            window.focus();
            localStorage.setItem('last_ad_click', now);
        }
    }
}

document.addEventListener('click', function() {
    openPopUnder();
}, { once: false });
</script>
"""

def inject_ads_recursive():
    processed_count = 0
    skipped_count = 0
    
    print(f"🔍 Scanning folder: {POSTS_DIR} and its sub-folders...")

    for root, dirs, files in os.walk(POSTS_DIR):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file)
                
                try:
                    # 1. Purana timestamp (mtime) save karo
                    stat = os.stat(path)
                    original_times = (stat.st_atime, stat.st_mtime)

                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    # 2. Check karo ki ad pehle se toh nahi hai
                    if "openPopUnder" in content:
                        skipped_count += 1
                        continue 

                    # 3. </body> ke pehle insert karo
                    if "</body>" in content:
                        new_content = content.replace("</body>", f"{AD_CODE}\n</body>")
                        
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        
                        # 4. Wahi purana time wapas set kar do (Sorting bachane ke liye)
                        os.utime(path, original_times)
                        processed_count += 1
                        
                except Exception as e:
                    print(f"❌ Error in {file}: {e}")

    print("-" * 30)
    print(f"✅ Mission Complete!")
    print(f"📂 Total folders scanned: {POSTS_DIR}/p1 to p20...")
    print(f"✨ New ads added to: {processed_count} files")
    print(f"⏭️ Already had ads (Skipped): {skipped_count} files")
    print("-" * 30)

if __name__ == "__main__":
    inject_ads_recursive()
