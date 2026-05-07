import os
import json
import asyncio
import requests
import re
import base64
import time
from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest

# --- Configuration ---
api_id = 34330516
api_hash = '9693b684498bf93a949bf50ba0573fc3'
phone = '+919512339243'

IMGBB_API_KEY = "0abf6d61d3ba547aa94ef21ceb4b3c0a"
MAX_POSTS_TOTAL = 100 # Total kitne posts nikalne hai
POSTS_PER_FILE = 600   # Ek file me kitne posts honge

# --- Naye Channels Yahan Add Karein ---
channel_links = [
'https://t.me/DesiZip',
    'https://t.me/+480FwuEWpqZiZGY1',
'https://t.me/+k9XL7lnp2s0yYjk1',
'https://t.me/+_ClpGVd7sL1jZWY1',
    'https://t.me/+cX2FMG9v9cIzNTBl',
    # 'https://t.me/+Your_New_Link_1',
    # 'https://t.me/+Your_New_Link_2'
]

converter_bot = '@DW2DW_LinkConverterBot'
progress_file = "channel_progress.json"

client = TelegramClient('session_json_maker', api_id, api_hash)

def get_latest_json_file():
    """Check karta hai ki abhi kaunsi file me data likhna hai"""
    i = 1
    while True:
        file_name = f"posts{i}.json"
        if not os.path.exists(file_name):
            return file_name, []
        
        with open(file_name, 'r') as f:
            try:
                data = json.load(f)
                if len(data) < POSTS_PER_FILE:
                    return file_name, data
            except:
                return file_name, []
        i += 1

def upload_to_imgbb(image_path):
    try:
        with open(image_path, "rb") as file:
            img_base64 = base64.b64encode(file.read())
            res = requests.post(
                "https://api.imgbb.com/1/upload",
                data={"key": IMGBB_API_KEY, "image": img_base64},
                timeout=20
            )
            result = res.json()
            if res.status_code == 200:
                return result['data']['url']
    except:
        pass
    return None

async def main():
    await client.start(phone)

    # Progress load karein (taaki purane message skip ho sakein)
    progress = {}
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as f:
                progress = json.load(f)
        except: pass

    count = 0

    for invite_url in channel_links:
        if count >= MAX_POSTS_TOTAL: break

        try:
            hash_code = invite_url.split('/')[-1].replace('+', '')
            try: await client(ImportChatInviteRequest(hash_code))
            except: pass

            channel = await client.get_entity(invite_url)
            last_msg_id = progress.get(invite_url, 0)

            async for message in client.iter_messages(channel, min_id=last_msg_id, reverse=True):
                if count >= MAX_POSTS_TOTAL: break

                if message.photo and message.text and "diskwala.com" in message.text:
                    link_match = re.search(r'(https?://\S*diskwala\.com\S*)', message.text)
                    if not link_match: continue

                    old_link = link_match.group(1)
                    
                    # Current file and data load karein
                    current_file, current_data = get_latest_json_file()
                    
                    # Duplicate check in current file
                    if any(item['link'] == old_link for item in current_data):
                        continue

                    print(f"Processing Msg: {message.id} for {current_file}")

                    path = await message.download_media()
                    img_url = upload_to_imgbb(path)
                    if path and os.path.exists(path): os.remove(path)

                    if not img_url: continue

                    # Bot convert
                    new_link = None
                    async with client.conversation(converter_bot, timeout=120) as conv:
                        await conv.send_message(old_link)
                        try:
                            response = await conv.get_response(timeout=30)
                            m = re.search(r'(https?://\S*diskwala\.com\S*)', response.text)
                            if m: new_link = m.group(1)
                        except: pass

                    if new_link:
                        post = {
                            "img": img_url,
                            "link": new_link,
                            "time": int(time.time())
                        }

                        # Naya post sabse upar insert karein
                        current_data.insert(0, post)

                        # Save to file
                        with open(current_file, 'w') as f:
                            json.dump(current_data, f, indent=2)

                        # Update progress
                        progress[invite_url] = message.id
                        with open(progress_file, 'w') as f:
                            json.dump(progress, f)

                        count += 1
                        print(f"Saved in {current_file}. Total: {count}")
                        await asyncio.sleep(2)

        except Exception as e:
            print(f"Error in channel {invite_url}: {e}")

if __name__ == "__main__":
    client.loop.run_until_complete(main())

