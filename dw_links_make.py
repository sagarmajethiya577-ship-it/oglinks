import os
import json
import asyncio
import requests
import re
import time
import random
import cloudinary
import cloudinary.uploader
from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest

# --- Configuration ---
api_id = 34330516
api_hash = '9693b684498bf93a949bf50ba0573fc3'
phone = '+919512339243'

cloudinary.config( 
  cloud_name = "dj1csslg1",
  api_key = "447722754135688",
  api_secret = "8SCqT-Mtem5CEAfi4KJeacdCjrY"
)

MAX_POSTS_TOTAL = 100 
POSTS_PER_FILE = 600 

channel_links = [

    'https://t.me/DesiZip',
'https://t.me/+9DlT5NAUl9s3MGNl',
'https://t.me/diskwalatgchannel',
    'https://t.me/+480FwuEWpqZiZGY1',
    'https://t.me/+k9XL7lnp2s0yYjk1',
    'https://t.me/+_ClpGVd7sL1jZWY1',
    'https://t.me/+cX2FMG9v9cIzNTBl',
]

converter_bot = '@DW2DW_LinkConverterBot'
progress_file = "channel_progress.json"

client = TelegramClient('session_json_maker', api_id, api_hash)

def get_latest_json_file():
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

async def main():
    await client.start(phone)
    
    progress = {}
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as f:
                progress = json.load(f)
        except: pass

    # --- Step 1: Saare channels ke liye iterators taiyar karein ---
    active_iterators = []
    for link in channel_links:
        try:
            print(f"Connecting to: {link}")
            hash_code = link.split('/')[-1].replace('+', '')
            try: await client(ImportChatInviteRequest(hash_code))
            except: pass
            
            entity = await client.get_entity(link)
            last_id = progress.get(link, 0)
            # Hum ek list mein iterator aur link ko store kar rahe hain
            it = client.iter_messages(entity, min_id=last_id, reverse=True)
            active_iterators.append({"link": link, "iterator": it})
        except Exception as e:
            print(f"❌ Error connecting to {link}: {e}")

    count = 0
    while active_iterators and count < MAX_POSTS_TOTAL:
        # --- Step 2: Randomly ek channel chunein ---
        target = random.choice(active_iterators)
        current_link = target["link"]
        iterator = target["iterator"]

        try:
            # Agla message uthayein
            message = await iterator.__anext__()
            
            # Check karein agar message kaam ka hai
            if message.photo and message.text and "diskwala.com" in message.text:
                link_match = re.search(r'(https?://\S*diskwala\.com\S*)', message.text)
                if not link_match: continue
                
                old_link = link_match.group(1)
                current_file, current_data = get_latest_json_file()
                
                if any(item['link'] == old_link for item in current_data): continue

                print(f"🎲 Random Pick from {current_link} | Msg: {message.id}")
                
                path = await message.download_media()
                img_url = None
                try:
                    upload_result = cloudinary.uploader.upload(path)
                    img_url = upload_result.get("secure_url")
                except Exception as e: print(f"❌ Cloudinary Error: {e}")
                
                if path and os.path.exists(path): os.remove(path)
                if not img_url: continue
                
                new_link = None
                try:
                    async with client.conversation(converter_bot, timeout=120) as conv:
                        await conv.send_message(old_link)
                        response = await conv.get_response(timeout=30)
                        m = re.search(r'(https?://\S*diskwala\.com\S*)', response.text)
                        if m: new_link = m.group(1)
                except Exception as e: print(f"❌ Bot Error: {e}")

                if new_link:
                    post = {"img": img_url, "link": new_link, "time": int(time.time())}
                    current_data.append(post)
                    random.shuffle(current_data) # File ke andar bhi shuffle
                    
                    with open(current_file, 'w') as f:
                        json.dump(current_data, f, indent=2)
                    
                    progress[current_link] = message.id
                    with open(progress_file, 'w') as f:
                        json.dump(progress, f)
                    
                    count += 1
                    print(f"✅ Saved ({count}/100) from {current_link}")
                    await asyncio.sleep(5) 
            else:
                # Agar message kaam ka nahi hai, toh loop ko continue rakhein bina wait kiye
                continue

        except StopAsyncIteration:
            # Is channel ke messages khatam ho gaye
            print(f"🏁 Finished all messages in {current_link}")
            active_iterators.remove(target)
        except Exception as e:
            print(f"⚠️ Error with {current_link}: {e}")
            # Thoda wait karein agar koi error aaye
            await asyncio.sleep(2)

    print(f"✨ Task Completed. Total posts added: {count}")

if __name__ == "__main__":
    client.loop.run_until_complete(main())
