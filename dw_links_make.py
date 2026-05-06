import os
import json
import asyncio
import requests
import re
import base64
from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest

# --- Configuration ---
api_id = 34330516
api_hash = '9693b684498bf93a949bf50ba0573fc3'
phone = '+919512339243'

# YAHAN APNI SAHI API KEY DALEIN
IMGBB_API_KEY = "85fca1591e03f0ea1888aa7256b07efb"
MAX_POSTS = 10 

channel_links = [
    'https://t.me/+480FwuEWpqZiZGY1',
    'https://t.me/+cX2FMG9v9cIzNTBl',
    'https://t.me/+XSETLrGAygkxODBl',
    'https://t.me/+9rT0iM7kf19iNTk1'
]
converter_bot = '@DW2DW_LinkConverterBot'
output_file = "posts.json"
progress_file = "channel_progress.json"

client = TelegramClient('session_json_maker', api_id, api_hash)

def upload_to_imgbb(image_path):
    """Image ko base64 mein convert karke ImgBB par upload karta hai"""
    try:
        with open(image_path, "rb") as file:
            # Image ko base64 string mein convert karna
            img_base64 = base64.b64encode(file.read())
            
            url = "https://api.imgbb.com/1/upload"
            payload = {
                "key": IMGBB_API_KEY,
                "image": img_base64,
            }
            res = requests.post(url, data=payload, timeout=20)
            result = res.json()
            
            if res.status_code == 200:
                return result['data']['url']
            else:
                print(f"\nImgBB API Error: {result.get('error', {}).get('message', 'Unknown')}")
    except Exception as e:
        print(f"\nRequest Error: {e}")
    return None

async def main():
    await client.start(phone)
    
    # JSON load logic
    all_data = []
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            try: all_data = json.load(f)
            except: all_data = []

    progress = {}
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            try: progress = json.load(f)
            except: progress = {}

    current_count = 0
    fail_streak = 0

    for invite_url in channel_links:
        if current_count >= MAX_POSTS: break
        
        print(f"\nScanning Channel: {invite_url}")
        try:
            hash_code = invite_url.split('/')[-1].replace('+', '')
            try: await client(ImportChatInviteRequest(hash_code))
            except: pass
            
            channel = await client.get_entity(invite_url)
            last_msg_id = progress.get(invite_url, 0)

            async for message in client.iter_messages(channel, min_id=last_msg_id, reverse=True):
                if current_count >= MAX_POSTS: break
                
                if message.photo and message.text and "diskwala.com" in message.text:
                    link_match = re.search(r'(https?://\S*diskwala\.com\S*)', message.text)
                    if not link_match: continue
                    
                    old_link = link_match.group(1)
                    print(f"[{current_count + 1}] Processing Msg ID: {message.id}", end="\r")
                    
                    # Media download
                    path = await message.download_media()
                    
                    # Base64 Upload
                    img_url = upload_to_imgbb(path)
                    if path and os.path.exists(path): os.remove(path)
                    
                    if not img_url:
                        fail_streak += 1
                        if fail_streak >= 3:
                            print("\nCRITICAL: Lagatar fail ho raha hai. API Key ya Internet check karein.")
                            return
                        continue
                    
                    fail_streak = 0 

                    # Bot Conversion
                    new_link = None
                    async with client.conversation(converter_bot, timeout=120) as conv:
                        await conv.send_message(old_link)
                        try:
                            response = await conv.get_response(timeout=30)
                            if "diskwala.com" in response.text:
                                m = re.search(r'(https?://\S*diskwala\.com\S*)', response.text)
                                if m: new_link = m.group(1)
                        except asyncio.TimeoutError:
                            print("\nBot timed out.")
                    
                    if new_link:
                        all_data.append({"img": img_url, "link": new_link})
                        with open(output_file, 'w') as f:
                            json.dump(all_data, f, indent=2)
                        
                        progress[invite_url] = message.id
                        with open(progress_file, 'w') as f:
                            json.dump(progress, f)
                        
                        current_count += 1
                        print(f"\nSaved! Total in JSON: {len(all_data)}")
                        await asyncio.sleep(2) # Non-blocking sleep for Ctrl+C
                    else:
                        print(f"\nBot failed for Msg ID: {message.id}")

        except Exception as e:
            print(f"\nChannel Error: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n\nScript stopped by user. Progress remains saved.")
