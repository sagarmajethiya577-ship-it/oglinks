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

IMGBB_API_KEY = "85fca1591e03f0ea1888aa7256b07efb"
MAX_POSTS = 10 

channel_links = [
    'https://t.me/+480FwuEWpqZiZGY1',
    'https://t.me/+cX2FMG9v9cIzNTBl'
]

converter_bot = '@DW2DW_LinkConverterBot'
output_file = "posts1.json"
progress_file = "channel_progress.json"

client = TelegramClient('session_json_maker', api_id, api_hash)

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

    # Load old data
    all_data = []
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r') as f:
                all_data = json.load(f)
        except:
            all_data = []

    existing_links = {item["link"] for item in all_data if "link" in item}

    progress = {}
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as f:
                progress = json.load(f)
        except:
            progress = {}

    count = 0

    for invite_url in channel_links:
        if count >= MAX_POSTS: break

        try:
            hash_code = invite_url.split('/')[-1].replace('+', '')
            try: await client(ImportChatInviteRequest(hash_code))
            except: pass

            channel = await client.get_entity(invite_url)
            last_msg_id = progress.get(invite_url, 0)

            async for message in client.iter_messages(channel, min_id=last_msg_id, reverse=True):
                if count >= MAX_POSTS: break

                if message.photo and message.text and "diskwala.com" in message.text:
                    link_match = re.search(r'(https?://\S*diskwala\.com\S*)', message.text)
                    if not link_match: continue

                    old_link = link_match.group(1)

                    if old_link in existing_links:
                        continue  # duplicate skip

                    print(f"Processing: {message.id}")

                    path = await message.download_media()
                    img_url = upload_to_imgbb(path)
                    if path and os.path.exists(path): os.remove(path)

                    if not img_url:
                        continue

                    # Bot convert
                    new_link = None
                    async with client.conversation(converter_bot, timeout=120) as conv:
                        await conv.send_message(old_link)
                        try:
                            response = await conv.get_response(timeout=30)
                            m = re.search(r'(https?://\S*diskwala\.com\S*)', response.text)
                            if m: new_link = m.group(1)
                        except:
                            pass

                    if new_link:
                        post = {
                            "img": img_url,
                            "link": new_link,
                            "time": int(time.time())
                        }

                        # 🔥 NEW POST TOP PAR
                        all_data.insert(0, post)

                        with open(output_file, 'w') as f:
                            json.dump(all_data, f, indent=2)

                        progress[invite_url] = message.id
                        with open(progress_file, 'w') as f:
                            json.dump(progress, f)

                        existing_links.add(new_link)
                        count += 1
                        print(f"Saved: {count}")

                        await asyncio.sleep(2)

        except Exception as e:
            print("Channel error:", e)

if __name__ == "__main__":
    client.loop.run_until_complete(main())
